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
  ttm_rejection_reason / ttm_unavailable_reason (R7); and facts.json beside judgment.json declares
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
  capex_source / capex_tag, when the run recorded capex_provenance; 5.7:
  "…, of which capitalized software $X" when the run read software, and a
  5.7 capex override beside filed software needs software_included), a "Share
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
  M1b / M1c — Andrew 2026-10-19; the main agent's decisions 03c and the
  lane defaults of 2026-10-21) The moat is a COMBINATION of Dorsey's
  framework and the evidence scorecard, checked by moat_scorecard.evaluate
  (main() step 6, before registry_transaction; every refusal writes
  nothing). judgment.json moat_scorecard {version, business_type,
  business_type_reason, sources, pillars, supporting, volume_price,
  moat_divergence_reason, low_roic_reason, high_return_low_moat_reason,
  erosion_rebuttal} is REQUIRED on a 5.7 run and shape-checked whenever
  present; score.json moat_evidence is written on every rebuild (status
  report_only on pre-5.7 output: mechanical pillars, flags and lint, nothing
  refused). Sources (the closed enum of eight types and their subtypes, S1-S9
  / W1-W8) cap the moat: none -> 3, one narrow -> 6, 7+ a wide source or two
  fact-backed sources, 9+ two wide and returns_on_capital +2 sustained.
  Evidence = clamp(core + supporting adjustment, 0, 10): 11 core pillars
  (weight 16; mechanical returns_on_capital on the governing measure — ROIC,
  tangible ROIC when goodwill + intangibles exceed 30% of invested capital,
  ROE at a balance-sheet financial incl. a SIC-6798 mortgage REIT —,
  industry_structure from _system/industry_returns.json same-ladder peers,
  capital_intensity, scale_economics; seven declared pillars on facts.json
  series) and four supporting factors whose sum / 4 (capped +-1) is added.
  Gates G1-G6 (divergence beyond +-2, the weight floor 8, the caps, 7+ on a
  governing return below 10% / ROE 15%, 4 or below on 20%+ sustained,
  MOAT_EROSION with erosion_risks +1) refuse a 5.7 run unless the reason
  field carries a number; each reason goes through check_influence with the
  moat evidence's numeric leaves (step 7, authoring runs). A rebuild (same
  engine run, declaration and facts.json: moat_scorecard.run_kind, never
  persisted, so an identical rerun writes an identical moat_evidence)
  records a newly failing data-driven gate in moat_evidence.gate_drift
  instead (GATE_DRIFT_ON_REBUILD; the weight floor too when measured pillars
  could clear it, and the volume x price bounds on the rows' revenue). The
  acquired-IPR&D charge engine 5.6 deducts once from value is added back to
  EBIT in returns_on_capital and scale_economics, in the rows' money unit
  (moat_scorecard.ADDBACK_IPRD, lane default Q3 (b)). Registry events moat_divergence, moat_low_roic,
  moat_high_return_low_moat, moat_erosion_rebuttal (identity moat_score as a
  float + reason; never a deferred-payment field name) when a gate applies on
  a checked run and its reason is declared. key_numbers.md "## Moat
  scorecard" (_kn_moat) prints only generated numbers, never worker text.
  fundamentals.py's capital_returns_from_row is the one returns function the
  pillar reads (fundamentals.json, statements.json and the scorecard agree).
- (L3b, M6 moat direction, Andrew 2026-10-20: "eroding moat should fade
  faster and vice versa") the trend sync and moat_widening_declined. The
  moat's direction sets the growth hold the engine ran (--moat-trend:
  eroding 0 / stable 2 / widening 3 years, on scenarios starting above
  terminal growth). moat_scorecard.trend_test measures it on the last 5 FY
  of fundamentals.json (governing return AND gross margin — operating
  margin where gross margin is not filed, 10b COVERAGE / lane default Q4 —
  both down: MOAT_EROSION; both up by the same 3pp / 20% / 2pp: MOAT_WIDENING)
  and fade_trend turns it into the hold a 5.7 run must run: eroding -> 0
  unless moat_scorecard.erosion_rebuttal is declared; widening -> 3 only
  with a fact-backed source, returns_on_capital >= +1, plain ROIC agreeing
  when tangible ROIC governs, ROA agreeing when ROE governs, and no
  commodity SIC (or a SIC-6199 filer booking contract revenue) unless a
  cost-position fact anchors business_type_reason (10b OQ10), and
  moat_scorecard.widening_declined (no number needed) not declared;
  anything else 2. score.json moat_evidence.fade records the evidence, the
  guards, the engine's recorded trend, in_sync and the counterfactual at
  the holds that matter (replay_paths(n, hold=h), no engine spawn). On a
  5.7 authoring run of a record with scenarios make_score refuses a
  recorded trend / hold other than fade_trend's (and a record whose holds
  disagree with its own trend everywhere); a rebuild records gate drift
  `fade_sync` instead (03c decision 6 kept for this gate: lane default Q5,
  moat_scorecard.FADE_DRIFT_ON_REBUILD); a Tier F record has no
  projection and is not checked. erosion_rebuttal is an influence field
  whenever MOAT_EROSION fired and it is declared, and it must be ANCHORED
  (fade_anchor_check: a cited non-third-party fact tagged erosion_rebuttal
  or an engine figure outside the trend test — the trend's own figures,
  the counterfactual and the record's hold-moved valuation outputs trace
  but never anchor); a business_type_reason lifting the commodity guard
  takes the same check. _final_run_args replays --moat-trend from inputs,
  so every counterfactual spawn (override impact, payable pin, amortized
  IPR&D, the interim bridge) runs on the scored hold. score.json copies
  moat_trend / hold_years beside cap_years on 5.7 records; key_numbers'
  "- Moat:" line names the hold (an older record prints the old line byte
  for byte) and the Moat scorecard section prints "- Trend test" and
  "- Fade direction". Registry: moat_erosion_rebuttal (now also on the
  rebutted hold) and moat_widening_declined, each with the hold run, the
  hold without it and the weighted IRR both ways.
- (L4, R2) the declared 6-K interim bridge and the annual-instance check
  (Andrew, 2026-10-19: "do what we gotta to get good foreign companies
  working"). (a) A 20-F / 40-F filer's TTM bridged from its 6-K interim —
  latest FY − prior interim + current interim, per leg — is a scored base
  only when DECLARED in judgment.json interim_bridge and built by
  ttm.py --interim (ttm.json basis "declared_interim"), pinned through
  --ttm. interim_pin_state re-verifies the record (refusals, in order):
  judgment.json still declares a valid interim_bridge, its canonical hash
  is ttm.json's declaration_hash, the pin is base_pin_source ttm_json (a
  --base-oe-ps copy is refused), ttm.json's arithmetic reproduces from its
  own legs and rates (interim_bridge.recompute_from_record) and its legs are
  the declaration's, the FY leg is this run's (release, latest FY end, the
  CSV's last row), the ADS ratio is the engine's, and the declaration passes
  interim_bridge.py's rules again (declaration_rule_problems, the bundle
  ttm.py runs, on ttm.json's FY leg, report period and filing date; and the
  declared report is the 6-K ttm.py verified — review fix 2026-10-21: a
  rule-breaking edit with a patched declaration_hash no longer scores on
  ttm.json's word). A declared bridge the
  final run is not pinned to is refused (check_interim_obligation; R7's
  rejection is the only way to keep it declared and unpinned), so are a
  declaration beside interim_bridge_declined, an iprd_amortized or a
  basis_window "ttm" base_override beside a bridge (named refusals). The
  5.7 obligation (5.7 runs only): a STALE_FY 20-F / 40-F run declares
  interim_bridge or interim_bridge_declined {reason with a number, report};
  default Q7 (main agent, 2026-10-21; switch INTERIM_OBLIGATION_RULE):
  a plain or amortized --base-oe-ps pin (TFII / FUTU / VIV's hand-built 6-K
  pins) needs one too — only the payable base is exempt. The bridged base
  is measured against the annual median (interim_bridge_measurement: one
  --measure replay of the final configuration with no pin, field overrides
  on and no DCF_IPRD_HOLD — the median takes its own acquired-IPR&D window;
  carried or "not measured" under a release mismatch) and both bases are
  recorded in score.json base_alternatives (the declared_interim published
  entry and the annual_median alternative, R7's one record), the
  declaration's descriptors in score.json interim_bridge, the flag
  TTM_DECLARED_INTERIM in score.json fragility_flags (never in the hashed
  engine output), the registry events interim_bridge (identity: the
  declaration hash) and interim_bridge_declined, and key_numbers.md's
  "Interim bridge" section (leg table, rates, shares, verification,
  like-for-like, sources; worker text in curly quotes). The override impact
  on a bridged base holds the pin (base_used "declared_interim"; FY
  override fields zero-filled from ttm.json override_counterfactual) and
  never runs ttm.py. (b) When the engine read a fiscal year from the
  filing's own XBRL instance (dcf_numbers.json annual_from_instance
  applied), <T>/annual_instance.json must be that instance's file with the
  same accession, instance_sha256 and facts_sha256 (annual_instance_check),
  and key_numbers.md says so in "Base owner's earnings".
- (L8, R6) declared share classes (Up-C / multi-class) and UP_C_SUSPECT
  (Andrew, 2026-10-19/20; design 08 rev. 3, 08b, rebase map L8). judgment.json
  share_classes is validated (R-1: share_classes.validate, every snippet at
  most 24 words and showing its count) and checked against the engine run
  (R-2: declaration_sha256 and the applied units; "rerun the engine (and
  ttm.py)"), refused beside share_class_mismatch (R-3), beside a plain
  base_override that does not state share_basis "total_units" (R-4: VNOM's
  2026-10-16 per-unit pin is retired — --ttm on the declared ttm.json
  reproduces it; an attested pin keeps a share_period consistent with its
  basis_window) and beside the payable base (R-5); an attested pin equal to
  a filed-basis per-share figure (ttm.json's *_filed_basis TTM, an applied
  FY's OE ÷ its filed traded count) is refused (R-4b, review 2026-10-21 —
  beyond 08's attestation text, raised with Andrew; switch
  SC_REFUSE_FILED_BASIS_PIN); a score whose base reads ttm.json's TTM (--ttm,
  a via-TTM --base-oe-ps, an iprd_amortized pin on native ttm_json, a
  basis_window "ttm" pin) is refused when ttm.json is not on the declaration
  (R-6); an out-of-band period — an FY row or the TTM leg (the record's
  share_classes.ttm, ttm.json's block on this declaration) — needs
  ack_reason (R-1); nci_check / cap_check
  disagreements need nci_gap_reason / cap_gap_reason (R-7 / R-7b); on a 5.7
  run UP_C_SUSPECT needs up_c_suspect_reason with a number (R-8); the reasons
  are influence fields (R-9); shares_override.share_basis is traded_class |
  all_classes and an OVERRIDE period with units must be attested (R-10).
  A declared 6-K interim bridge at a declaring filer is re-derived on
  ttm.json's filed-basis twins plus the rescale onto total units
  (sc_interim_rescale_edited, _interim_problems step 4).
  share_classes_impact measures the declaration both ways (one engine
  --measure replay with DCF_NO_SHARE_CLASSES: a TTM base at ttm.json's
  ttm_oe_per_share_filed_basis, a declared pin at pin × total ÷ filed with
  DCF_SC_PIN_SCALE, an amortized pin likewise or by a two-step median
  replay; a replay the engine refuses (exit 3) or that gaps is "not
  measured", any other failed replay — timeout, crash, another exit, no
  JSON — refuses), recorded in score.json share_classes (plus up_c_check),
  the share_classes registry event (units_by_period, never `periods`) and
  the up_c_suspect event, and key_numbers.md's share-class lines (the
  "Shares diluted (latest)" line names total economic units); an entry
  alert is suppressed when the declaration RAISES the tier.
- (L9, R8 / R9) capex components, capitalized software and the ttm.json
  release stamp (Andrew, 2026-10-19, R8 / R9; assigned to Claude). On a
  5.7 run: (R8) every CAPEX_UNLISTED_COMPONENT:<tag> flag needs judgment.json
  capex_unlisted_ack[<tag>] (a reason carrying the figure) —
  refuse_unlisted_capex_component; a capex_override does not release it
  (09b Q4); the CAPEX_UNLISTED_COMPONENT_OVERRIDDEN variant is never
  refused. Each released tag is recorded as a capex_unlisted_ack registry
  event {tag, reason, value}. (R9) key_numbers.md's capex-basis line names
  the capitalized-software part ("…, of which capitalized software $X");
  a capex_override that fills a last-3-FY year or a TTM leg beside filed
  capitalized software needs capex_override.software_included: true and a
  value at least the filed intangible leg in USD on the engine's own
  basis (refuse_capex_override_software; an override-filled TTM leg of an
  unstamped ttm.json is refused as uncheckable); software_included rides on
  the capex field's registry entry. (R8/R9 TTM provenance) a 5.7 run whose
  basis read ttm.json (ttm_inputs recorded) needs
  ttm_inputs.ttm_engine_release >= 5.7.0 — refuse_pre57_ttm_json, right
  after check_ttm_inputs_current. validate_overrides checks both new
  judgment keys' shapes on every run.
- (R7) STALE_FY discretion made checkable: ttm_rejection_reason and the
  one base_alternatives record (Andrew, 2026-10-19, ruling-sheet Q5 option A:
  "a worker MAY reject the TTM base, but only when the rejection reason names
  the distorting cash-flow line WITH A NUMBER"; design 11; the main agent's
  defaults Q13-Q18 of 2026-10-21, pending Andrew, each one R7_* switch). On a
  5.7 run (ttm_rejection_state, main() step 3, every refusal before the first
  write): when STALE_FY fires (Q13, R7_OBLIGATION_SCOPE), the published base
  is the annual median or a declared base_override pin (Q18,
  R7_DECLARED_PIN_RULE; the payable pin is exempt) and ttm.json holds a TTM
  for the run's latest FY (ttm_for_run: eligible, or fixable — a pre-5.7
  stamp, an edited bridge, an override ttm.json used that judgment.json no
  longer declares), judgment.json ttm_rejection_reason is required and must
  name a cash-flow line (CASH_FLOW_LINE_RE, a closed vocabulary of owner's
  earnings' own lines) and carry a figure (L2's carries_number) —
  [TTM-REJ0..2]; a fixable TTM refuses (it cannot be priced); the field
  anywhere else is refused (beside a TTM pin; with nothing to reject). A
  declared 6-K bridge kept declared and unpinned is rejected the same way
  (L4's binding reads plan["bridge_rejected"]). Q14 (R7_TTM_UNAVAILABLE_RULE;
  keyed on STALE_FY itself, never on Q13's scope): a STALE_FY 10-K run of
  that kind with no TTM for its FY quotes ttm.py's exit-3 line in
  ttm_unavailable_reason — verbatim, nothing else (parse_ttm_py_exit3: the
  head, whole problems in ttm.py's words joined by "; "), for this ticker /
  CIK / FY (ttm_unavailable_problem: dated problems name this FY; an undated
  one the CSV's latest-FY row or judgment.json contradicts is refused); the
  same quote stands for a fixable ttm.json for the FY that ttm.py can no
  longer rebuild (it exits 3 and writes nothing — ttm_unbuildable: recorded,
  never priced or refused). Step 4
  (build_base_alternatives, at most ONE engine --measure replay a run, field
  overrides on, no DCF_IPRD_HOLD, DCF_REPLAY_PURPOSE=base_alternatives): the
  rejected TTM replayed with --ttm (its own acquired-IPR&D window and share
  count; a replay exit 3 refuses, a gap is recorded, a failed run or a base
  other than ttm.json's refuses), the annual median replayed beside a
  TTM-published STALE_FY run (Q15, R7_MEDIAN_BESIDE_TTM), L4's bridge
  measurement folded in (one replay routine, _replay_alternative), every other
  base from the record "not replayed"; a release mismatch carries the prior
  record or records "not measured", never spawning. score.json
  base_alternatives {schema, published, stale_fy, ttm_rejection_reason,
  ttm_unavailable_reason, bases [published first: kind, role, computed,
  measured, base OE/share, weighted IRR, tier by numbers, IPR&D charge,
  source, replay, change against the published base, why], replays, measured,
  note, carried flags}; key_numbers.md "Base alternatives" after the IPR&D
  section (L4's "Interim bridge" points to it); one base_alternatives
  registry event for a rejection or a published bridge (identity chosen,
  reason, TTM kind and window; L4's interim_bridge event keeps the
  declaration's descriptors only). Step 7: ttm_rejection_reason traces
  through check_influence (used_for ttm_rejection; the record's leaves are
  engine sources), and — the main agent's decision for this lane — so do L9's
  capex_unlisted_ack reasons (used_for capex_unlisted_ack). Q16
  (R7_ALERT_RULE): no entry alert when the rejection lifts the published tier
  above the rejected TTM's into S / A (ttm_rejection_alert_reasons). Q17: an
  amortized IPR&D median after a rejection is not built (the engine's
  refusal names R7; ENGINE_BACKLOG). Older output rebuilds unchanged: no
  plan, no record, no event, no replay, the fields never read.
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
import moat_scorecard as _moat  # v5.7 (L3, R4 revised): the moat scorecard make_score checks (pure, no I/O at import)
import dcf_engine as _engine  # v5.5: the release stamp and the market-cap formula (no I/O at import)
from dcf_engine import ENGINE_RELEASE
import check_quotes as _quotes  # v5.7 (L2, R3): the quote gate's sources, saved runs and filed-history rows
import quote_tokens as _qt  # v5.7 (L2, R3): the one tokenizer (reasons carry / trace numbers through it)
import facts as _facts  # v5.7: the rulings-release predicate and the facts.json schema (stdlib, no I/O at import)
import interim_bridge as _ib  # v5.7 (L4, R2a): the declared 6-K interim bridge's rules (pure, no I/O at import)
import share_classes as _sc  # v5.7 (L8, R6): the declared share classes' rules (pure, no I/O at import)

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
# v5.7 — R7 STALE_FY discretion made checkable (Andrew, 2026-10-19; ruling-sheet Q5 option A; design 11)
TTM_REJECTION_KEY = "ttm_rejection_reason"            # judgment.json: the reason a STALE_FY TTM base is rejected
TTM_UNAVAILABLE_KEY = "ttm_unavailable_reason"        # judgment.json: ttm.py's exit-3 message, quoted (default Q14)
BASE_KINDS = ("annual_median", "ttm", "declared_interim", "payable_5y", "declared_pin")
BASE_ROLES = ("published", "rejected", "alternative")
REPLAY_PURPOSE_ENV = "DCF_REPLAY_PURPOSE"             # "base_alternatives" on R7 replays (the engine ignores it)
STALE_FY_PREFIX = "STALE_FY"                          # the engine's own flag (latest FY ended > 7 months before the run)
# The main agent's defaults for the open R7 questions (12_lane_defaults.md Q13-Q18, 2026-10-21, pending Andrew's
# ratification) — each one switch:
R7_OBLIGATION_SCOPE = "stale_fy"       # Q13: "stale_fy" — the reason binds STALE_FY runs only; "ttm_present" — every
                                       # 5.7 run beside a TTM for its latest FY (the ruling's literal reading)
R7_TTM_UNAVAILABLE_RULE = "require"    # Q14: "require" — a STALE_FY 10-K run with no TTM for its FY quotes ttm.py's
                                       # exit-3 message in ttm_unavailable_reason; "off" — recorded, never required
R7_MEDIAN_BESIDE_TTM = True            # Q15: replay the annual median beside a TTM-published STALE_FY run (1 replay)
R7_ALERT_RULE = "suppress_raise"       # Q16: "suppress_raise" — no entry alert when the rejection lifts the published
                                       # tier above the rejected TTM's into S / A (as R6's share-class raise); "off"
R7_DECLARED_PIN_RULE = "require"       # Q18: "require" — a declared base_override pin under STALE_FY needs the reason
                                       # too (both bases shown); "exempt" — declared pins are exempt like the payable pin
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
        # v5.7 R9 (Andrew, 2026-10-19): capex_override.software_included declares that the override figure is the
        # cash-flow total including capitalized software (refuse_capex_override_software checks it on 5.7 runs)
        if "software_included" in o:
            if field != "capex":
                fail(f"judgment.json: {key}.software_included is not allowed — only capex_override carries it")
            if not isinstance(o["software_included"], bool):
                fail("judgment.json: capex_override.software_included must be true or false — true when the override "
                     "figure is the cash-flow total including capitalized software")
        # v5.7 R6 (L8, rule 10 / R-10): shares_override.share_basis states which classes the override counts — the
        # traded class only (units are added on top at a declaring filer) or every class (never beside a declaration)
        if "share_basis" in o:
            if field != "shares":
                fail(f"judgment.json: {key}.share_basis is not allowed — only shares_override carries it")
            if o["share_basis"] not in SHARE_BASIS_VALUES:
                fail(f"judgment.json: shares_override.share_basis {o['share_basis']!r} is not one of "
                     f"{', '.join(SHARE_BASIS_VALUES)} (R-10)")
        out[field] = o
    # v5.7 R8 (Andrew, 2026-10-19): capex_unlisted_ack {tag: reason} releases a CAPEX_UNLISTED_COMPONENT flag the
    # worker shows is not capex; every reason carries the figure (R7's checkable-reason standard: a digit)
    ack = j.get("capex_unlisted_ack")
    if ack is not None:
        if not isinstance(ack, dict) or not ack:
            fail("judgment.json: capex_unlisted_ack must be a non-empty object {\"<tag>\": \"<reason with the figure>\"}")
        for tag, why in ack.items():
            if not (isinstance(tag, str) and tag.strip()) or not (isinstance(why, str) and why.strip()
                                                                   and re.search(r"\d", why)):
                fail(f"judgment.json: capex_unlisted_ack.{tag} must say why the tag is not capex (or is already inside "
                     "the listed lines) and carry the figure")
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
# v5.7 lane L8 (R6 declared share classes, Andrew 2026-10-19/20; designs 08 + 08b, rebase map L8.md)
# ---------------------------------------------------------------------------
UP_C_FLAG = "UP_C_SUSPECT"
UP_C_REASON_KEY = "up_c_suspect_reason"
SHARE_BASIS_VALUES = ("traded_class", "all_classes")   # shares_override / the interim share leg (rule 10, R-10)
SC_TOTAL_UNITS = "total_units"                         # base_override.share_basis on a total-unit pin (R-4)
SC_NOT_ON_DECLARATION = "ttm.json is not on this share_classes declaration"   # R-6 / 08 §8.9 (R7's gate text)
SC_SCOPE_CAP = 40e9                                     # in_scope_under_40b


def _read_judgment(folder):
    try:
        with open(f"{folder}/judgment.json", encoding="utf-8") as f:
            j = json.load(f)
        return j if isinstance(j, dict) else {}
    except (OSError, ValueError):
        return {}


def _sc_record(n):
    rec = n.get("share_classes") if isinstance(n, dict) else None
    return rec if isinstance(rec, dict) and rec.get("declared") else None


def validate_share_classes(j):
    """R-1 (08 §8.2): judgment.json share_classes — every share_classes.validate rule, then every snippet at most
    SNIPPET_MAX_WORDS words and showing its count (quote_tokens.snippet_shows_value at presentation scale: "164,811" in
    a table in thousands proves 164,810,547); a kind calc entry's two counts likewise. Returns the raw declaration
    (what declaration_sha256 hashes) or None when absent."""
    v = j.get("share_classes")
    if v is None:
        return None
    norm, errs = _sc.validate(v)
    if errs:
        fail("judgment.json: share_classes " + "; ".join(errs))
    probs = []
    for c in norm["classes"]:
        for p in c["periods"]:
            w = f"{c['name']} {p['period_end']}"
            snips = ([(p["snippet"], None)] if p["kind"] == "calc" or p["value"] == 0
                     else [(p["snippet"], p["value"])])
            if p["kind"] == "calc":
                snips += [(x.get("snippet"), x.get("value")) for x in (p.get("calc") or {}).get("counts") or []]
            for s, val in snips:
                if len(str(s).split()) > _qt.SNIPPET_MAX_WORDS:
                    probs.append(f"{w}: a snippet is over {_qt.SNIPPET_MAX_WORDS} words")
                elif val is not None and not _qt.snippet_shows_value(str(s), val, presentation_scale=True):
                    probs.append(f"{w}: the snippet does not show the count {float(val):,.0f}")
    if probs:
        fail("judgment.json: share_classes " + "; ".join(probs) + " (R-1: a verbatim snippet of at most "
             f"{_qt.SNIPPET_MAX_WORDS} words that shows the count)")
    return v


def _sc_period_totals(n, tt, period):
    """(filed traded, total units) of a declared period: the record's applied row, its zero / in_filed_count period
    (total = filed), or ttm.json's share_classes block for the current-YTD period. None when the run has neither."""
    rec = _sc_record(n) or {}
    for a in rec.get("applied") or []:
        if a.get("period_end") == period:
            return float(a["filed_traded"]), float(a["total_units"])
    blk = (tt or {}).get("share_classes") if isinstance(tt, dict) else None
    if isinstance(blk, dict) and blk.get("period_end") == period and _num(blk.get("filed_traded")):
        return float(blk["filed_traded"]), float(blk["total_units"])
    return None


def sc_share_period(n, bo, tt):
    """A-8: the declared period whose total a share_basis "total_units" pin divides by — explicit share_period, else
    from #47's basis_window (ttm: ttm.json's ytd_end; fy: the run's latest FY), else the run's latest FY. Returns
    (period, refusal | None)."""
    bw = bo.get("basis_window") if isinstance(bo.get("basis_window"), dict) else None
    win = bw.get("window") if bw else None
    ytd = (tt or {}).get("ytd_end") if isinstance(tt, dict) else None
    sp = bo.get("share_period")
    latest = n.get("latest_period_end")
    if sp is None:
        return (ytd if win == "ttm" else latest), None
    if win == "ttm" and sp != ytd:
        return sp, (f"base_override.share_period {sp} contradicts its basis_window \"ttm\" (ttm.json's current YTD ends "
                    f"{ytd}) — a TTM-window pin divides by the TTM's units")
    if win == "fy" and sp != latest:
        return sp, (f"base_override.share_period {sp} contradicts its basis_window \"fy\" (the run's latest FY ends "
                    f"{latest})")
    return sp, None


def check_share_classes_sync(n, j_sc, folder):
    """R-2 … R-5, R-7, R-7b, R-10 and A-26 (08 §8.2): the declaration against the engine run's record. R-2: the
    record absent while declared (a run before declaring, or pre-5.7 output) or present while nothing is declared,
    another declaration_sha256, or applied units that are not the declaration's -> "rerun the engine (and ttm.py)".
    R-3: share_classes beside share_class_mismatch. R-4: a plain base_override beside a declaration must state
    share_basis "total_units" (its share_period consistent with its basis_window, A-8) and (R-4b, review 2026-10-21)
    may not be a filed-basis per-share figure (sc_filed_basis_pin); an iprd_amortized one stays allowed. R-5: the
    payable base beside a declaration is not supported yet (08b decision 4). R-7 / R-7b: nci_check.agrees false /
    cap_check.gap true need nci_gap_reason / cap_gap_reason. R-10 / A-26: share_basis values (shares_override, the
    interim share leg), an applied OVERRIDE period not attested traded_class in the record or in judgment.json now, a
    ttm.json block on an OVERRIDE YTD leg whose override is not traded_class. R-1's record half: an out-of-band period
    without ack_reason — an applied FY row or the TTM leg (sc_ttm_out_of_band); a calc entry the record's
    re-derivation does not reproduce."""
    j = _read_judgment(folder)
    rec = _sc_record(n)
    ib = j.get("interim_bridge") if isinstance(j.get("interim_bridge"), dict) else {}
    leg = (((ib.get("legs") or {}).get("shares_diluted") or {}).get("current_interim")
           if isinstance(ib.get("legs"), dict) else None)
    if isinstance(leg, dict) and leg.get("share_basis") is not None and leg["share_basis"] not in SHARE_BASIS_VALUES:
        fail(f"interim_bridge.legs.shares_diluted.current_interim.share_basis {leg['share_basis']!r} is not one of "
             f"{', '.join(SHARE_BASIS_VALUES)} (R-10)")
    bo = j.get("base_override") if isinstance(j.get("base_override"), dict) else None
    if bo is not None and (bo.get("share_basis") is not None or bo.get("share_period") is not None):
        if bo.get("basis") is not None:
            fail("judgment.json: base_override.share_basis / share_period apply to a plain base_override only (R-4)")
        if bo.get("share_basis") != SC_TOTAL_UNITS:
            fail(f"judgment.json: base_override.share_basis must be \"{SC_TOTAL_UNITS}\" when present (R-4: the pin is "
                 "per economic unit of a share_classes declaration)")
        if bo.get("share_period") is not None and not _engine.iprd_date_ok(bo["share_period"]):
            fail("judgment.json: base_override.share_period must be a YYYY-MM-DD period end (R-4)")
    if j_sc is None:
        if rec is not None:
            fail("judgment.json share_classes and dcf_numbers.json share_classes are out of sync — the engine run applied "
                 f"a declaration (declaration_sha256 {str(rec.get('declaration_sha256'))[:12]}…) but judgment.json declares "
                 "none; rerun the engine (and ttm.py)")
        if bo is not None and bo.get("share_basis") is not None:
            fail(f"judgment.json: base_override.share_basis \"{SC_TOTAL_UNITS}\" needs a share_classes declaration (R-4)")
        return None
    if share_class_declared(j)[0]:
        fail("share_classes and share_class_mismatch are exclusive — declare the units, or the mismatch, not both (R-3)")
    if rec is None:
        fail("judgment.json share_classes and dcf_numbers.json share_classes are out of sync — judgment.json declares "
             "share_classes but the engine run recorded none (a run before the declaration, or engine output from "
             "before 5.7); rerun the engine (and ttm.py)")
    norm, _ = _sc.validate(j_sc)
    sha = _sc.declaration_sha256(j_sc)
    if rec.get("declaration_sha256") != sha:
        fail("judgment.json share_classes and dcf_numbers.json share_classes are out of sync — the declaration's "
             f"declaration_sha256 is {sha[:12]}…, the run's {str(rec.get('declaration_sha256'))[:12]}… (the declaration "
             "changed after the run); rerun the engine (and ttm.py)")
    units = _sc.units_by_period(norm)
    for a in rec.get("applied") or []:
        if a.get("period_end") not in units or abs(units[a["period_end"]] - float(a.get("declared_units") or 0)) > 0.5:
            fail("judgment.json share_classes and dcf_numbers.json share_classes are out of sync — the run applied "
                 f"{a.get('declared_units')} units for {a.get('period_end')}, the declaration gives "
                 f"{units.get(a.get('period_end'))}; rerun the engine (and ttm.py)")
    so = j.get("shares_override") if isinstance(j.get("shares_override"), dict) else {}
    for a in rec.get("applied") or []:
        if a.get("filed_traded_tag") == "OVERRIDE":
            if a.get("share_basis_attested") != "traded_class":
                fail(f"shares_override.share_basis: the run added units to the OVERRIDE row {a['period_end']} without a "
                     "traded_class attestation (output of an engine without check (a)) — rerun the engine (and ttm.py) "
                     "(R-10)")
            if so.get("share_basis") != "traded_class":
                fail(f"shares_override.share_basis is now {so.get('share_basis')!r}, but the run added units to the "
                     f"OVERRIDE row {a['period_end']} as the traded-class count — rerun the engine (A-26)")
    tt = _ttm_record(folder)
    oob = [a["period_end"] for a in rec.get("applied") or [] if a.get("out_of_band")] + sc_ttm_out_of_band(rec, tt, sha)
    if oob and not norm.get("ack_reason"):
        fail(f"judgment.json: share_classes units are more than {_sc.UNITS_MAX_MULT}x the traded count for "
             f"{', '.join(oob)} (out of band) and share_classes carries no ack_reason (R-1)")
    for c in rec.get("calc_entries") or []:
        r = _num(c.get("rederived"))
        if r is None or abs(r - float(c.get("value") or 0)) > _sc.CALC_TOLERANCE:
            fail(f"judgment.json: share_classes {c.get('name')} {c.get('period_end')}: the kind calc value "
                 f"{c.get('value')} does not reproduce from its counts ({r}) (A-21)")
    nc = rec.get("nci_check") or {}
    if nc.get("agrees") is False and not norm.get("nci_gap_reason"):
        fail(f"SHARE_CLASSES_NCI_GAP: the declared units are {_pct(nc.get('declared_share_of_total'))} of total units, "
             f"noncontrolling interests hold {_pct(nc.get('nci_share_of_equity'))} of equity and "
             f"{_pct(nc.get('nci_share_of_net_income_3fy'))} of consolidated net income (3 FY) — more than "
             f"{nc.get('tolerance_pp')}pp apart; check the units, or explain the gap in share_classes.nci_gap_reason "
             "(with the figure) (R-7)")
    cc = rec.get("cap_check") or {}
    if cc.get("gap") is True and not norm.get("cap_gap_reason"):
        fail(f"SHARE_CLASSES_CAP_GAP: the screener's market cap is {cc.get('cap_ratio')}x its price × the filed traded "
             f"count while the declared units add {_pct(cc.get('declared_uplift'), 1)} — say whether the screener counts "
             "one class only in share_classes.cap_gap_reason (with the figure), or remove classes the filed count "
             "already includes (R-7b)")
    blk = (tt or {}).get("share_classes") if isinstance(tt, dict) else None
    if (isinstance(blk, dict) and (((tt.get("inputs") or {}).get("shares_diluted") or {}).get("ytd_current_tag")
                                   == "OVERRIDE") and blk.get("units_equivalent") and so.get("share_basis") != "traded_class"):
        fail("shares_override.share_basis: ttm.json added declared units to an OVERRIDE YTD share leg whose "
             "shares_override is not attested traded_class — rerun ttm.py (and the engine) (R-10)")
    if bo is not None:
        if bo.get("basis") == PAYABLE_BASIS:
            fail("share_classes beside a payable_earnings_5y base is not supported yet (R-5; 08b decision 4)")
        if bo.get("basis") is None:
            if bo.get("share_basis") != SC_TOTAL_UNITS:
                fail("share_classes replaces a share-basis base pin: judgment.json declares a base_override that does not "
                     f"state share_basis \"{SC_TOTAL_UNITS}\" — retire the pin (--ttm on the declared ttm.json reproduces "
                     "a per-unit TTM base) or attest a pin built from total-unit engine outputs (R-4)")
            sp, why = sc_share_period(n, bo, tt)
            if why:
                fail(f"judgment.json: {why} (R-4)")
            if sp not in units:
                fail(f"judgment.json: base_override.share_period {sp} is not a declared share_classes period (R-4)")
            hit = sc_filed_basis_pin(n, bo, tt, folder) if SC_REFUSE_FILED_BASIS_PIN else None
            if hit:
                fail(f"judgment.json: base_override.share_basis \"{SC_TOTAL_UNITS}\" attests a per-unit pin, but its "
                     f"value {hit[2]:.6f} is a filed-basis per-share figure — {hit[0]} {hit[1]:.6f}, on the filed "
                     "traded-class count the declaration corrects; pin the per-unit figure (--ttm on the declared "
                     "ttm.json, or a pin built from total-unit engine outputs) (R-4b)")
    return None


def sc_ttm_out_of_band(rec, tt, sha):
    """R-1 / rule 6 on the TTM leg (review 2026-10-21 finding 5): ["the TTM to <period end>"] when the current-YTD
    (interim) period's units are more than UNITS_MAX_MULT x its traded count — in the --ttm run's share_classes.ttm, or
    in ttm.json's share_classes block when it is on this declaration (a median score's ttm.json is still the
    declaration's applied period: R7's alternatives price it) — else []. Banded from the counts (share_classes
    .out_of_band), not from a recorded flag."""
    out = []
    legs = [(rec or {}).get("ttm")]
    tblk = (tt or {}).get("share_classes") if isinstance(tt, dict) else None
    if isinstance(tblk, dict) and tblk.get("declaration_sha256") == sha:
        legs.append(tblk)
    for blk in legs:
        if isinstance(blk, dict) and _sc.out_of_band(blk.get("units_equivalent"), blk.get("filed_traded")):
            p = f"the TTM to {blk.get('period_end')}"
            if p not in out:
                out.append(p)
    return out


# R-4b (review 2026-10-21 finding 3; a rule beyond 08 §8.2 R-4's attestation-only text, raised with Andrew): a
# base_override attested share_basis "total_units" may not equal a filed-basis per-share figure the run or ttm.json
# carries (VNOM's $7.9338 TTM per Class A share had scored Tier S beside the declaration). False restores the
# attestation-only rule.
SC_REFUSE_FILED_BASIS_PIN = True


def sc_filed_basis_pin(n, bo, tt, folder):
    """R-4b: (figure name, filed-basis value, pin) when the attested total-unit pin — judgment.json's
    base_override.value or the run's --base-oe-ps — equals (figure_matches, 0.1%) a filed-basis per-share figure:
    ttm.json's ttm_oe_per_share_filed_basis / ttm_oe_per_ordinary_share_filed_basis (a block whose YTD carries units),
    or an applied FY's owner's earnings ÷ its filed traded count (financials_history.csv; × the ADS ratio), and no
    total-unit figure of the run (ttm.json's per-unit TTM, a CSV row's OE ÷ its total count, the record's median and
    latest) — a pin that is both is ambiguous and kept. None otherwise."""
    pins = [v for v in (_num(bo.get("value")), _num((n.get("inputs") or {}).get("base_oe_ps_arg"))) if v is not None]
    if not pins:
        return None
    rec = _sc_record(n) or {}
    ads = _applied_ads_ratio(n) or 1.0
    filed_figs, total_figs = [], [n.get("base_oe_normalized_per_share"), n.get("base_oe_latest_per_share")]
    blk = (tt or {}).get("share_classes") if isinstance(tt, dict) else None
    if isinstance(blk, dict):
        if _num(blk.get("units_equivalent")):
            for k in ("ttm_oe_per_share_filed_basis", "ttm_oe_per_ordinary_share_filed_basis"):
                if _num(tt.get(k)) is not None:
                    filed_figs.append((f"ttm.json {k}", float(tt[k])))
        total_figs += [tt.get("ttm_oe_per_share"), tt.get("ttm_oe_per_ordinary_share")]
    rows = {r["period_end"]: r for r in _csv_rows(folder)} if folder else {}
    for a in rec.get("applied") or []:
        r = rows.get(a.get("period_end"))
        oe, fil = (_f(r.get("oe_conservative")) if r else None), _num(a.get("filed_traded"))
        if oe is not None and fil:
            filed_figs.append((f"FY{str(a['period_end'])[:4]} owner's earnings ÷ its filed traded count",
                               oe / fil * ads))
    for r in rows.values():
        oe, sh = _f(r.get("oe_conservative")), _f(r.get("shares_diluted"))
        if oe is not None and sh:
            total_figs.append(oe / sh * ads)
    for pin in pins:
        if any(_engine.figure_matches(pin, t) for t in total_figs if _num(t) is not None):
            continue
        for name, v in filed_figs:
            if _engine.figure_matches(pin, v):
                return name, v, float(pin)
    return None


def check_up_c_obligation(n, j):
    """R-8 (5.7 runs): an UP_C_SUSPECT flag in fragility_flags needs judgment.json share_classes (impossible beside
    the flag: the engine suppresses it — "rerun the engine with the declaration") or up_c_suspect_reason, a non-empty
    string carrying a number. The reason's shape is checked whenever it is present."""
    r = j.get(UP_C_REASON_KEY)
    if r is not None and not (isinstance(r, str) and r.strip() and re.search(r"\d", r)):
        fail(f"judgment.json: {UP_C_REASON_KEY} must be a non-empty string carrying the number that shows the minority "
             "is an ordinary subsidiary interest or that the count already covers every class (R-8)")
    if not is_57_run(n):
        return None
    if any(str(f).startswith(UP_C_FLAG) for f in n.get("fragility_flags") or []):
        if j.get("share_classes") is not None:
            fail(f"{UP_C_FLAG} is unresolved — the engine run did not apply judgment.json share_classes (the flag would "
                 "be suppressed); rerun ttm.py and the engine with the declaration (R-8)")
        if r is None:
            fail(f"{UP_C_FLAG} is unresolved — noncontrolling interests are large and the filed diluted count may cover "
                 "only the traded class: declare share_classes (the equity note's ownership table; rerun ttm.py and the "
                 f"engine) or write judgment.json {UP_C_REASON_KEY} with the number that shows the minority is ordinary "
                 "or the count already covers every class (R-8)")
    return None


def _ttm_pinned(n, tt, folder=None):
    """True when the score's base is ttm.json's TTM: a --ttm pin, or a --base-oe-ps pin equal to ttm.json's figure
    (figure_matches) that no declaration says was built on FY figures."""
    inp = n.get("inputs") or {}
    if inp.get("base_pin_source") == "ttm_json" or n.get("base_source") == "ttm_json":
        return True
    pin = inp.get("base_oe_ps_arg")
    if inp.get("base_pin_source") != "base_oe_ps_arg" or _num(pin) is None or not isinstance(tt, dict):
        return False
    if not _engine.figure_matches(n.get("base_oe_per_share"), tt.get("ttm_oe_per_share")):
        return False
    return not (folder and declared_fy_built_pin(_judgment_base_override(folder), pin))


def _ttm_basis_pin(n):
    """v5.7 (L8, R-6; 08 §5.3 "the same table runs for an IPR&D ttm_json basis" — review 2026-10-21 finding 2): True
    when the run's --base-oe-ps pin read ttm.json as its TTM basis without being ttm.json's figure — an iprd_amortized
    pin on native base ttm_json (the engine's amortized record: its native base, window and share count are
    ttm.json's) or a plain pin the engine read on basis_window "ttm" (inputs.base_basis_window: the current-YTD leg)."""
    inp = n.get("inputs") or {}
    if inp.get("base_pin_source") != "base_oe_ps_arg":
        return False
    bw = inp.get("base_basis_window")
    return _iprd_amortized_ttm(n) is not None or (isinstance(bw, dict) and bw.get("window") == "ttm")


def check_ttm_on_declaration(n, j_sc, tt, folder=None):
    """R-6 (08 §8.2, after check_ttm_inputs_current): a score whose base reads ttm.json's TTM — TTM-pinned (--ttm, or a
    via-TTM --base-oe-ps), or an iprd_amortized / basis_window "ttm" pin on it (_ttm_basis_pin) — whose ttm.json is
    not on this share_classes declaration — share_classes.ttm_on_declaration: the block missing while declared,
    another declaration_sha256, or a block while nothing is declared — is refused. A median-base score is never
    refused by a stale ttm.json (its TTM alternatives are R7's, recorded computed: false)."""
    if not (_ttm_pinned(n, tt, folder or f"{BASE}/{n.get('ticker')}") or _ttm_basis_pin(n)):
        return None
    ok, why = _sc.ttm_on_declaration(tt, j_sc)
    if not ok:
        fail(f"{SC_NOT_ON_DECLARATION} — {why} (R-6); the score's base reads ttm.json's TTM")
    return None


def sc_interim_filed_view(tt):
    """v5.7 (L8, 08 §5.4; review 2026-10-21 finding 1): the figures a declared-interim ttm.json's own legs re-derive
    to (interim_bridge.recompute_from_record divides by the filed share leg). On a ttm.json without a share_classes
    block that is ttm.json itself; with one, ttm.py rescaled ttm_shares_diluted / ttm_oe_per_share onto total units
    after the bridge's arithmetic, so the recomputation is compared with their filed-basis twins
    (ttm_shares_diluted_filed, ttm_oe_per_share_filed_basis) — the comparison had read every declared bridge at a
    declaring filer as edited and refused it."""
    if not isinstance(tt.get("share_classes"), dict):
        return tt
    return dict(tt, ttm_shares_diluted=tt.get("ttm_shares_diluted_filed"),
                ttm_oe_per_share=tt.get("ttm_oe_per_share_filed_basis"))


def sc_interim_rescale_edited(rc, tt, j):
    """v5.7 (L8, 08 §5.4; review 2026-10-21 finding 1): True when a declared-interim ttm.json's share-class rescale
    (ttm.py apply_share_classes, leg interim) does not re-derive — ttm_shares_diluted = filed + the block's
    units_equivalent (block filed_traded / total_units the same counts), rescale_factor k = filed ÷ total, every
    rescaled per-share field = its *_filed_basis twin × k (the per-ADS pin, the per-ordinary figure, the override
    zero-fill), the recomputed per-ordinary figure = its filed-basis twin, and the units = judgment.json's declaration
    for the block's period (× its split factor) at ttm.json's ytd_end. False on a ttm.json without the block (nothing
    rescaled) and when judgment.json carries no valid declaration (R-1 / R-6 refuse that first)."""
    blk = tt.get("share_classes") if isinstance(tt.get("share_classes"), dict) else None
    if blk is None:
        return False
    filed, u = _num(tt.get("ttm_shares_diluted_filed")), _num(blk.get("units_equivalent"))
    k = _num(blk.get("rescale_factor"))
    if not filed or filed <= 0 or u is None or u < 0 or k is None:
        return True
    total = float(filed) + float(u)
    if not (_rel_eq(blk.get("filed_traded"), filed) and _rel_eq(blk.get("total_units"), total)
            and _rel_eq(tt.get("ttm_shares_diluted"), total) and _rel_eq(k, filed / total)
            and _rel_eq(rc.get("ttm_oe_per_ordinary_share"), tt.get("ttm_oe_per_ordinary_share_filed_basis"))):
        return True
    cf = tt.get("override_counterfactual") if isinstance(tt.get("override_counterfactual"), dict) else {}
    for parent, f in ((tt, "ttm_oe_per_share"), (tt, "ttm_oe_per_ordinary_share"), (cf, "base_oe_per_share_zero_fill")):
        if parent is cf and f + "_filed_basis" not in cf:
            continue
        fb = _num(parent.get(f + "_filed_basis"))
        if fb is None or not _rel_eq(parent.get(f), fb * k):
            return True
    sc = (j or {}).get("share_classes")
    norm, errs = _sc.validate(sc) if sc is not None else (None, ["absent"])
    if norm is not None and not errs:
        want, fac = _sc.units_by_period(norm).get(blk.get("period_end")), _num(blk.get("units_split_factor"))
        if blk.get("period_end") != tt.get("ytd_end") or want is None or fac is None or abs(want * fac - u) > 0.5:
            return True
    return False


def _sc_replay(cmd, env_extra):
    """(exit code | None, parsed JSON | None, first stdout line — else the last stderr line, a crash's exception): one
    engine --measure replay; the exit code is None when the run could not complete (timeout, OS error)."""
    env = dict(os.environ)
    env.update(env_extra or {})
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=600, env=env)
    except Exception:
        return None, None, ""
    txt = out.stdout or ""
    first = next((ln.strip() for ln in txt.splitlines() if ln.strip()), "")
    if not first:
        first = next((ln.strip() for ln in reversed((out.stderr or "").splitlines()) if ln.strip()), "")
    data = None
    i = txt.find("{")
    if out.returncode == 0 and i >= 0:
        try:
            data = json.loads(txt[i:])
        except Exception:
            data = None
    return out.returncode, data, first


SC_REPLAY_REFUSED = 3   # the engine's exit code for its own refusal (BAD_* / NO_TTM, nothing written): "does not score"


def _sc_replay_outcome(rc, data, first, step):
    """08 §8.4 "a replay failure refuses (nothing written)" / rebase A-17 (review 2026-10-21 finding 4): None when the
    replay printed its record (exit 0 and a JSON object); the "does not score" note when the engine itself refused the
    filed-basis run (exit SC_REPLAY_REFUSED); fail() for every other outcome — no exit code (timeout, OS error), a
    crash or any other exit (a traceback, NO_CIK), exit 0 without a JSON object. Recording a crash as "does not score"
    had shipped the score with raises_tier false, so the R6 entry-alert suppression was skipped."""
    if rc == 0 and isinstance(data, dict):
        return None
    if rc == SC_REPLAY_REFUSED:
        return f"the filed-class run does not score ({first or f'exit {rc}'})"
    how = ("no exit code: a timeout or OS error" if rc is None
           else f"exit {rc}" if rc else "exit 0 without a JSON record")
    fail(f"the share-class replay ({step}) did not complete ({how}{': ' + first[:300] if first else ''}) — cannot "
         "measure the share_classes declaration; retry make_score")
    return None


def _r4(v):
    return round(v, 4) if _num(v) is not None else None


def _sc_not_measured(blk, note):
    blk.update(measured=False, note=note)
    return blk


def share_classes_impact(ticker, n, j_sc, prior_score=None):
    """08 §8.4 (rebase A-4 / A-16 / A-17): the declaration measured both ways — one engine --measure replay of the
    final configuration (_final_run_args) with DCF_NO_SHARE_CLASSES=1 (no DCF_NO_OVERRIDES, no DCF_IPRD_HOLD: the
    acquired-IPR&D charge per share is recomputed on the filed basis). The pin is re-derived on the filed basis,
    never copied: a TTM base (--ttm or a via-TTM --base-oe-ps) replays at ttm.json's ttm_oe_per_share_filed_basis;
    the median at no pin; a declared total-unit pin at pin × total(p) ÷ filed(p), p its share_period; an
    iprd_amortized pin at pin × TTM total ÷ TTM filed (native ttm_json) or, native median, by a two-step replay
    (iprd_amortized_value on the filed median and count) — both pinned replays pass DCF_SC_PIN_SCALE = replay pin ÷
    declared value so the engine still recognises the declaration. Only the engine's own refusal (exit 3) or a data
    gap is recorded measured: false with the reason; any other failed replay — a timeout, a crash, another exit, no
    JSON — refuses (_sc_replay_outcome; review 2026-10-21 finding 4). Release mismatch: the
    prior registry share_classes event is carried when its declaration_sha256, total-unit base and weighted IRR (4 dp)
    equal this run's, else "not measured". None when nothing is declared."""
    rec = _sc_record(n)
    if j_sc is None or rec is None:
        return None
    folder = f"{BASE}/{ticker}"
    j = _read_judgment(folder)
    tt = _ttm_record(folder)
    lt = rec.get("latest") or {}
    blk = {"basis": rec.get("basis"), "declaration_sha256": rec.get("declaration_sha256"), "base_used": None,
           "replay_pin": None, "replay_pin_source": None, "replay_pin_scale": None,
           "base_oe_filed_basis": None, "base_oe_total_units": _r4(n.get("base_oe_per_share")), "base_oe_impact_pct": None,
           "weighted_irr_filed_basis": None, "weighted_irr_total_units": _r4(n.get("implied_irr_weighted")),
           "weighted_irr_impact_pp": None, "tier_filed_basis": None, "tier_total_units": n.get("tier_by_numbers"),
           "market_cap_filed_basis": None, "market_cap_total_units": _num(n.get("market_cap_est")),
           "in_scope_filed_basis": None,
           "in_scope_total_units": (n["market_cap_est"] < SC_SCOPE_CAP) if _num(n.get("market_cap_est")) else None,
           "raises_tier": False, "measured": True, "note": None,
           "units_latest": lt.get("units_equivalent"), "filed_latest": lt.get("filed_traded")}
    if n.get("engine_release") != ENGINE_RELEASE:
        prior = [e for e in registry_prior_entries(ticker) if e.get("event") == "share_classes"]
        for e in prior:
            if (e.get("declaration_sha256") == blk["declaration_sha256"]
                    and e.get("base_oe_total_units") == blk["base_oe_total_units"]
                    and e.get("weighted_irr_total_units") == blk["weighted_irr_total_units"]):
                carried = {k: e.get(k) for k in blk if k in e}
                blk.update(carried, note="carried from the prior registry share_classes event (engine output from another "
                                         "release is never replayed)")
                return blk
        return _sc_not_measured(blk, _not_measured_note(n.get("engine_release")))
    bo = j.get("base_override") if isinstance(j.get("base_override"), dict) else None
    inp = n.get("inputs") or {}
    pin = _num(inp.get("base_oe_ps_arg"))
    am = _iprd_amortized_record(n)
    args = _final_run_args(n)
    env = {_sc.ENV_OFF: "1"}
    scale = None
    if bo is not None and bo.get("basis") == IPRD_AMORTIZED_BASIS and am is not None and pin is not None:
        blk["base_used"] = "iprd_amortized_pin"
        if am.get("native_base") == "ttm_json":
            tot, fil = _num((tt or {}).get("ttm_shares_diluted")), _num((tt or {}).get("ttm_shares_diluted_filed"))
            if not (tot and fil):
                return _sc_not_measured(blk, "ttm.json carries no filed-basis TTM share count (ttm_shares_diluted_filed)")
            rp = pin * tot / fil
            blk["replay_pin_source"] = f"pin × TTM total ÷ TTM filed ({(tt or {}).get('ytd_end')})"
        else:
            rc, m1, first = _sc_replay([sys.executable, ENGINE, ticker, "--measure"] + args, env)
            why = _sc_replay_outcome(rc, m1, first, "filed-basis median, step 1 of the amortized pin")
            if why:
                return _sc_not_measured(blk, why)
            if m1.get("data_gap_uncovered"):
                return _sc_not_measured(blk, "the filed-class run does not score (data gap: "
                                             f"{', '.join(str(x) for x in m1['data_gap_uncovered'])})")
            if _num(m1.get("base_oe_normalized_per_share")) is None or not _num(m1.get("shares_diluted_latest")):
                return _sc_not_measured(blk, "the filed-class run does not score (no filed-basis median or latest "
                                             "count)")
            rp = _engine.iprd_amortized_value(m1["base_oe_normalized_per_share"], am.get("figures") or [],
                                              m1["shares_diluted_latest"], n.get("ads_ratio"))
            blk["replay_pin_source"] = "iprd_amortized_value(filed median, figures, filed latest)"
        scale = rp / float(bo["value"]) if _num(bo.get("value")) else None
    elif (bo is not None and bo.get("basis") is None and bo.get("share_basis") == SC_TOTAL_UNITS and pin is not None
          and _engine.declared_value_matches(bo, pin)):
        blk["base_used"] = "declared_pin"
        sp, _ = sc_share_period(n, bo, tt)
        tf = _sc_period_totals(n, tt, sp)
        if tf is None:
            return _sc_not_measured(blk, f"the pin's share_period {sp} has no recorded filed / total count")
        rp = pin * tf[1] / tf[0]
        blk["replay_pin_source"] = f"pin × total/filed ({sp})"
        scale = rp / float(bo["value"])
    elif _ttm_pinned(n, tt, folder):
        blk["base_used"] = "ttm"
        rp = _num((tt or {}).get("ttm_oe_per_share_filed_basis"))
        if rp is None:
            return _sc_not_measured(blk, "ttm.json carries no filed-basis TTM (ttm_oe_per_share_filed_basis)")
        blk["replay_pin_source"] = "ttm.json ttm_oe_per_share_filed_basis"
    elif pin is None and inp.get("base_pin_source") is None:
        blk["base_used"] = "median_3y"
        rp = None
    else:
        return _sc_not_measured(blk, "the run's pin is neither ttm.json's TTM nor a declared total-unit or amortized pin")
    if rp is not None:
        args = args + ["--base-oe-ps", repr(float(rp))]
        blk["replay_pin"] = rp
    if scale is not None:
        env[_sc.PIN_SCALE_ENV] = repr(float(scale))
        blk["replay_pin_scale"] = round(scale, 6)
    rc, m, first = _sc_replay([sys.executable, ENGINE, ticker, "--measure"] + args, env)
    why = _sc_replay_outcome(rc, m, first, "filed traded class, DCF_NO_SHARE_CLASSES")
    if why:
        return _sc_not_measured(blk, why)
    if m.get("data_gap_uncovered"):
        return _sc_not_measured(blk, "the filed-class run does not score (data gap: "
                                     f"{', '.join(str(x) for x in m['data_gap_uncovered'])})")
    if blk["base_used"] == "iprd_amortized_pin" and ((m.get("iprd_adjustment") or {}).get("treatment")
                                                     != "amortized_in_base"):
        return _sc_not_measured(blk, "the filed-class replay did not recognise the amortized declaration (treatment "
                                     f"{(m.get('iprd_adjustment') or {}).get('treatment')!r})")
    am_note = ((m.get("iprd_adjustment") or {}).get("amortized") or {}).get("counterfactual_replay") \
        if isinstance((m.get("iprd_adjustment") or {}).get("amortized"), dict) else None
    bf, bt = _num(m.get("base_oe_per_share")), _num(n.get("base_oe_per_share"))
    irf, irt = _num(m.get("implied_irr_weighted")), _num(n.get("implied_irr_weighted"))
    capf = _num(m.get("market_cap_est"))
    tf_, tt_ = m.get("tier_by_numbers"), n.get("tier_by_numbers")
    blk.update(base_oe_filed_basis=_r4(bf),
               base_oe_impact_pct=round((bt / bf - 1) * 100, 2) if (bf and bt is not None) else None,
               weighted_irr_filed_basis=_r4(irf),
               weighted_irr_impact_pp=round((irt - irf) * 100, 2) if (irf is not None and irt is not None) else None,
               tier_filed_basis=tf_, market_cap_filed_basis=capf,
               in_scope_filed_basis=(capf < SC_SCOPE_CAP) if capf else None,
               raises_tier=bool(tf_ in TIER_ORDER and tt_ in TIER_ORDER and TIER_ORDER[tt_] > TIER_ORDER[tf_]),
               note=am_note)
    return blk


def share_classes_raise_reason(sc_impact):
    """08 §8.8: the alert_reasons share_classes_raise text when a measured declaration RAISES the numbers tier (an
    entry alert is then suppressed; exits are never suppressed — 08b decision 3). None otherwise."""
    if not isinstance(sc_impact, dict) or not sc_impact.get("measured") or not sc_impact.get("raises_tier"):
        return None
    return (f"share-class declaration raises the tier ({sc_impact.get('tier_filed_basis')} on the filed class → "
            f"{sc_impact.get('tier_total_units')} on total units)")


def score_share_classes_fields(score, n, j_sc, sc_impact):
    """08 §8.5: score.json share_classes (the measured block plus the record's traded_class, latest, ttm, nci_check,
    cap_check, zero_periods, unused_periods) when the engine record carries a declaration; up_c_check {suspect, s,
    suppressed_by, waived_reason} when the record carries the detector (5.7 output). No key on older output."""
    rec = _sc_record(n)
    if rec is not None:
        out = dict(sc_impact or {})
        lt = rec.get("latest") or {}
        out.update(traded_class=rec.get("traded_class"),
                   latest={"period_end": lt.get("period_end"),
                           "filed_traded": int(round(lt["filed_traded"])) if _num(lt.get("filed_traded")) else None,
                           "units_equivalent": int(round(lt["units_equivalent"])) if _num(lt.get("units_equivalent")) is not None else None,
                           "total_units": int(round(lt["total_units"])) if _num(lt.get("total_units")) else None,
                           "declared_share_of_total": _r4(lt.get("declared_share_of_total"))},
                   ttm=({k: (int(round(v)) if k in ("filed_traded", "units_equivalent", "total_units") and _num(v) is not None
                             else v) for k, v in rec["ttm"].items()
                         if k in ("period_end", "filed_traded", "units_equivalent", "total_units")}
                        if isinstance(rec.get("ttm"), dict) else None),
                   nci_check=rec.get("nci_check"), cap_check=rec.get("cap_check"),
                   zero_periods=rec.get("zero_periods") or [], unused_periods=rec.get("unused_periods") or [])
        score["share_classes"] = out
    uc = n.get("up_c_check")
    if isinstance(uc, dict):
        flagged = any(str(f).startswith(UP_C_FLAG) for f in n.get("fragility_flags") or [])
        j = _read_judgment(f"{BASE}/{n.get('ticker')}") if flagged else {}
        score["up_c_check"] = {"suspect": bool(uc.get("suspect")), "s": _r4(uc.get("s")),
                               "suppressed_by": uc.get("suppressed_by"),
                               "waived_reason": j.get(UP_C_REASON_KEY) if flagged else None}
    return None


def share_classes_reason_checks(j, fc, folder, n, extra=None):
    """R-9 (08 §8.1 step 7; 5.7 runs): the share-class reasons are influence fields (facts.INFLUENCE_TAGS) —
    share_classes.reason / ack_reason / nci_gap_reason / cap_gap_reason / diluted_gap_reason and
    up_c_suspect_reason — each traced through check_influence (numbers to engine figures or cited facts, never only
    third-party). Returns the fields checked."""
    done = []
    sc = j.get("share_classes") if isinstance(j.get("share_classes"), dict) else {}
    for k in ("reason",) + _sc.OPTIONAL_REASONS:
        t = sc.get(k)
        if isinstance(t, str) and t.strip():
            check_influence(f"share_classes.{k}", t, _facts.parse_refs(t), fc, folder, n, extra=extra)
            done.append(f"share_classes.{k}")
    r = j.get(UP_C_REASON_KEY)
    if isinstance(r, str) and r.strip():
        check_influence(UP_C_REASON_KEY, r, _facts.parse_refs(r), fc, folder, n, extra=extra)
        done.append(UP_C_REASON_KEY)
    return done


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


def _impact_from_run(n, ticker=None):
    """The with-override side and the basis label, read from the run itself —
    the same label compute_override_impact gives: "payable_5y" for a run pinned
    to the insurer payable-earnings base (payable_base recorded, or
    base_pin_source judgment_base_override — M3: it read "ttm"),
    "declared_interim" (v5.7, L4) for a --ttm pin on a declared 6-K interim
    bridge (ttm.json basis declared_interim; the ticker defaults to the
    record's), "ttm" for any other pin, else "median_3y"."""
    base_with = n.get("base_oe_per_share")
    irr_with = n.get("implied_irr_weighted")
    base_src = (n.get("base_source") or "").lower()
    inp = n.get("inputs") or {}
    pinned = inp.get("base_oe_ps_arg") is not None or "ttm" in base_src
    gaps = list(n.get("data_gap") or [])
    unblocks = bool(gaps) and not (n.get("data_gap_uncovered") or [])
    base_used = "payable_5y" if (n.get("payable_base") or inp.get("base_pin_source") == "judgment_base_override") \
        else "declared_interim" if _interim_pinned(ticker or n.get("ticker"), n) \
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
# v5.7 lane L9 (R8 / R9 capex, Andrew 2026-10-19; assigned to Claude)
# ---------------------------------------------------------------------------
CAPEX_SOFTWARE_NAMES = _engine.CAPEX_SOFTWARE_NAMES          # the engine's R9 tag names (one list, never a copy)
UNLISTED_CAPEX_FLAG = _engine.UNLISTED_CAPEX_FLAG            # "CAPEX_UNLISTED_COMPONENT" (the refusing variant)
_TTM_CAPEX_LEGS = ("fy", "ytd_prior", "ytd_current")


def _record_rate(n, unit, pe, leg_fx=None):
    """USD per `unit` at period end pe from the run's own record — 1.0 for USD; the intangible leg's own fetched rate
    (capex_provenance.<FY>.intangibles_fx {currency, rate}, PR #31) when it names `unit`, else
    fx_conversion.rates_by_currency (the tables the engine converted with); None when the record carries none."""
    if not unit or unit == "USD":
        return 1.0
    if isinstance(leg_fx, dict) and leg_fx.get("currency") == unit and _num(leg_fx.get("rate")) is not None:
        return float(leg_fx["rate"])
    fx = n.get("fx_conversion") if isinstance(n.get("fx_conversion"), dict) else {}
    by = fx.get("rates_by_currency") or ({fx["from_currency"]: fx["rates"]}
                                         if fx.get("from_currency") and isinstance(fx.get("rates"), dict) else {})
    r = ((by.get(unit) if isinstance(by, dict) else None) or {}).get(pe)
    return float(r) if _num(r) is not None else None


def _capex_override_usd(n, value, pe):
    """The capex override in USD for FY period pe on the engine's recorded basis (override_checks.capex.currency_basis,
    dcf_engine.override_currency_basis): verbatim for no_fx / declared_usd / last_filed_unit_usd, else x the reporting
    currency's rate for pe (what the engine's _override_usd does); None when that rate is not in the record."""
    basis = ((n.get("override_checks") or {}).get("capex") or {}).get("currency_basis")
    if basis in (None, "no_fx", "declared_usd", "last_filed_unit_usd", "shares"):
        return float(value)
    fx = n.get("fx_conversion") if isinstance(n.get("fx_conversion"), dict) else {}
    r = _record_rate(n, fx.get("from_currency"), pe)
    return None if r is None else float(value) * r


def _software_override_hits(n, tt, value):
    """[(where, software, software_unit, software_tags, override_usd, filed_intangibles_usd)] for every last-3-FY
    year and TTM leg a capex override fills beside filed capitalized software (see refuse_capex_override_software).
    The second list: TTM legs an override fills in a ttm.json with no 5.7 stamp (no software record to check)."""
    hits, unstamped = [], []
    prov = n.get("capex_provenance") if isinstance(n.get("capex_provenance"), dict) else {}
    for pe in sorted(prov)[-3:]:
        rec = prov[pe] if isinstance(prov[pe], dict) else {}
        if rec.get("intangibles_not_added") != "override_present":
            continue
        filed = {t: float(v) for t, v in (rec.get("intangibles_filed") or {}).items() if _num(v) is not None}
        sw = {t: v for t, v in filed.items() if t in CAPEX_SOFTWARE_NAMES and v > 0}
        if not sw:
            continue
        unit = rec.get("intangibles_filed_unit") or rec.get("intangibles_unit")
        if not unit and not n.get("fx_conversion"):
            unit = "USD"   # no FX record: every figure the run read is USD
        r = _record_rate(n, unit, pe, rec.get("intangibles_fx")) if unit else None
        hits.append((f"FY{pe[:4]} ({pe})", sum(sw.values()), unit, sorted(sw), _capex_override_usd(n, value, pe),
                     None if r is None else sum(v for v in filed.values() if v > 0) * r))
    tt = tt if isinstance(tt, dict) else {}
    comps = tt.get("capex_components") if isinstance(tt.get("capex_components"), dict) else {}
    legs = ((tt.get("inputs") or {}).get("capex") or {}) if isinstance(tt.get("inputs"), dict) else {}
    used = next((e for e in (tt.get("overrides_used") or []) if isinstance(e, dict) and e.get("field") == "capex"), {})
    filled = used.get("legs_filled") if isinstance(used.get("legs_filled"), dict) else {}
    stamped = (release_tuple(tt.get("engine_release")) or (0, 0, 0)) >= RELEASE_57
    for leg in _TTM_CAPEX_LEGS:
        c = comps.get(leg)
        per = legs.get(f"{leg}_period") if isinstance(legs.get(f"{leg}_period"), list) else None
        if not stamped:
            if legs.get(f"{leg}_tag") == "OVERRIDE":
                unstamped.append(f"TTM {leg} leg ({per[0]}..{per[1]})" if per and len(per) == 2 else f"TTM {leg} leg")
            continue
        if not (isinstance(c, dict) and c.get("intangibles_not_added") == "override_present" and c.get("software_tags")
                and _num(c.get("software"))):
            continue
        amt = _num((filled.get(leg) or {}).get("amount")) if isinstance(filled.get(leg), dict) else None
        if amt is None and per and len(per) == 2:
            amt = float(value) * _engine_days(per[0], per[1]) / 365.0   # ttm.py's proration (inclusive days / 365)
        where = f"TTM {leg} leg ({per[0]}..{per[1]})" if per and len(per) == 2 else f"TTM {leg} leg"
        hits.append((where, float(c["software"]), "USD", sorted(c["software_tags"]), amt,
                     float(_num(c.get("intangibles")) or c["software"])))
    return hits, unstamped


def _engine_days(a, b):
    """ttm.py's inclusive day count (end - start + 1)."""
    return (datetime.date.fromisoformat(b) - datetime.date.fromisoformat(a)).days + 1


def refuse_capex_override_software(n, j_over, tt=None):
    """v5.7 R9 (Andrew, 2026-10-19: capitalized software is capex). A capex_override is read as the filer's TOTAL
    capex line and never takes the filed intangible leg on top. When it fills a last-3-FY year
    (capex_provenance[<FY>].intangibles_not_added == 'override_present' with a CAPEX_SOFTWARE_NAMES tag in
    intangibles_filed) or a TTM leg of the current ttm.json `tt` (capex_components.<leg>.intangibles_not_added ==
    'override_present' with non-empty software_tags) whose filed capitalized software was therefore not added, the
    override must declare software_included: true — whatever its value: raising a PP&E-only figure to the total does
    not change what the record shows, so the declaration is required. With the declaration the override must be at
    least the filed intangible leg it claims to include — a total can never be smaller than one of its parts —
    compared in USD on the engine's own basis:
      FY year: the override on override_checks.capex.currency_basis (verbatim for no_fx / declared_usd /
        last_filed_unit_usd, else x fx_conversion's reporting-currency rate for that period end — what the engine's
        _override_usd does) vs the sum of capex_provenance[<FY>].intangibles_filed x the rate of its filed unit
        (intangibles_filed_unit; the leg's own intangibles_fx rate first, else rates_by_currency);
      TTM leg: the override as ttm.py filled the leg (overrides_used capex legs_filled.<leg>.amount, else value x
        inclusive days / 365 — ttm.py's proration; ttm.py legs are USD) vs capex_components.<leg>.intangibles.
    A rate the record does not carry is refused as unverifiable. A ttm.json without a 5.7 engine_release stamp
    records no software at all, so an override-filled TTM leg in it cannot be checked: refused, naming the legs
    (rerun ttm.py) — never passed silently. Runs only on a 5.7 run; older output rebuilds unchanged."""
    if not is_57_run(n) or "capex" not in j_over:
        return None
    o = j_over["capex"]
    hits, unstamped = _software_override_hits(n, tt, o["value"])
    if unstamped:
        fail(f"judgment.json capex_override {o['value']:,.0f} fills {', '.join(unstamped)} of a ttm.json stamped "
             f"engine_release {(tt or {}).get('engine_release') or 'none (pre-5.7)'}: a ttm.json built before engine "
             "5.7 records no capitalized software, so whether the filing reports software beside the override on "
             "those legs cannot be checked — rerun ttm.py with the current engine, then the engine and make_score.")
    if not hits:
        return None
    where = "; ".join(f"{w}: {v:,.0f}{' ' + u if u and u != 'USD' else ''} ({', '.join(t)})" for w, v, u, t, _, _ in hits)
    if o.get("software_included") is not True:
        fail(f"judgment.json capex_override {o['value']:,.0f} fills {where} — capitalized software the filing reports "
             "and the engine did not add on top of the override (an override is the filer's TOTAL capex line; the "
             "intangible leg is never stacked on it). The declaration is required either way: if the override figure "
             "is the cash-flow total including that software, set capex_override.software_included: true; if it is "
             "the PP&E line only, raise capex_override.value to the total (PP&E + capitalized software + intangible "
             "purchases), re-run the engine, and set software_included: true.")
    short = [(w, ov, fi) for w, _, _, _, ov, fi in hits if ov is None or fi is None or ov < fi]
    if short:
        fail(f"judgment.json capex_override {o['value']:,.0f} declares software_included: true, but "
             + "; ".join(f"{w}: the override is "
                         + ("unverifiable (the record carries no FX rate for it)" if ov is None or fi is None
                            else f"{ov:,.0f} USD against {fi:,.0f} USD of filed intangible purchases and capitalized "
                                 "software")
                         for w, ov, fi in short)
             + " — a total that includes them can never be smaller than they are. The figure is the PP&E line only: "
             "raise capex_override.value to the cash-flow total (PP&E + capitalized software + intangible purchases) "
             "and re-run the engine (and ttm.py for a TTM leg).")
    return None


def _unlisted_capex_tags(n):
    """{tag: [(fy, value), ...]} for every CAPEX_UNLISTED_COMPONENT:<tag> flag on the record (the refusing variant only:
    CAPEX_UNLISTED_COMPONENT_OVERRIDDEN:<tag> never matches the 'CAPEX_UNLISTED_COMPONENT:' prefix)."""
    out = {}
    for f in n.get("fragility_flags") or []:
        if not (isinstance(f, str) and f.startswith(UNLISTED_CAPEX_FLAG + ":")):
            continue
        tag = f[len(UNLISTED_CAPEX_FLAG) + 1:].split(" ")[0].strip()
        if tag:
            out.setdefault(tag, []).extend((int(fy), float(v.replace(",", "")))
                                           for fy, v in re.findall(r"FY(\d{4}) ([\d,]+(?:\.\d+)?)", f))
    return out


def refuse_unlisted_capex_component(n, j):
    """v5.7 R8 (Andrew, 2026-10-19: "a small other component never stands in for the whole"). On a 5.7 run every
    CAPEX_UNLISTED_COMPONENT:<tag> flag — a capex-like cash-flow tag on no engine capex list, larger than the whole
    component capex leg the engine read for the same year in the same filing (the KNX pattern) — needs judgment.json
    capex_unlisted_ack[<tag>] (a reason with the figure, validated by validate_overrides). There is deliberately no
    override release (09b Q4, main agent 2026-10-20): an override never replaces a filed leg, so the small listed line
    would still set owner's earnings. The CAPEX_UNLISTED_COMPONENT_OVERRIDDEN variant (a year with no PP&E leg) is
    never refused. Older runs rebuild unchanged."""
    if not is_57_run(n):
        return None
    tags = sorted(_unlisted_capex_tags(n))
    ack = j.get("capex_unlisted_ack") if isinstance(j.get("capex_unlisted_ack"), dict) else {}
    missing = [t for t in tags if t not in ack]
    if missing:
        fail(f"{UNLISTED_CAPEX_FLAG} — engine release {n.get('engine_release')} found {', '.join(missing)} on no engine "
             "capex list, larger than the whole component capex leg it read for the same year (the flag names the "
             "figures). If that tag is the filer's capex line, block the company NEEDS_MAIN_AGENT: capex via queue.py: "
             "the engine's lists need it, and a capex_override cannot help (an override never replaces a filed leg, so "
             "the small listed line would still set owner's earnings). If it is not capex, declare why with the figure "
             "in judgment.json capex_unlisted_ack {\"<tag>\": \"<reason>\"} and re-run make_score.")
    return None


def capex_unlisted_acks(n, j):
    """v5.7 R8: [{tag, reason, value}] — one per CAPEX_UNLISTED_COMPONENT:<tag> flag on the record that judgment.json
    capex_unlisted_ack releases (value: the flag's figure for its latest fiscal year, None when unparseable), for the
    registry's capex_unlisted_ack events (update_registry -> _capex_events). [] when none."""
    ack = j.get("capex_unlisted_ack") if isinstance(j, dict) and isinstance(j.get("capex_unlisted_ack"), dict) else {}
    out = []
    for tag, figs in sorted(_unlisted_capex_tags(n if isinstance(n, dict) else {}).items()):
        if tag in ack:
            out.append({"tag": tag, "reason": ack[tag], "value": max(figs)[1] if figs else None})
    return out


def refuse_pre57_ttm_json(n, tt):
    """v5.7 (R8 / R9 TTM provenance; 09 rebase A6). A 5.7 run whose selected basis read an existing ttm.json — the
    engine records ttm_inputs exactly then (the --ttm pin, an undeclared --base-oe-ps pin, a TTM basis, basis_window
    "ttm", a median-native amortized pin under STALE_FY) with its ttm_input_hash — needs that ttm.json built by a 5.7
    ttm.py: ttm_inputs.ttm_engine_release (the engine's copy of the file's stamp; absent = an unstamped, pre-5.7 file)
    >= 5.7.0. A pre-5.7 ttm.json leaves capitalized software and the new PP&E components out of every TTM leg while
    still matching the score's base within 0.1%, so the pin check alone cannot see it. Called right after
    check_ttm_inputs_current (a ttm.json regenerated after the run is TTM_CHANGED first: rerun the engine), so the
    recorded stamp is the current file's. A record with ttm_inputs null (a median run, an FY-declared pin) is never
    refused; older output rebuilds unchanged."""
    if not is_57_run(n):
        return None
    ti = n.get("ttm_inputs")
    if not (isinstance(ti, dict) and ti.get("ttm_input_hash")):
        return None
    rel = ti.get("ttm_engine_release")
    if (release_tuple(rel) or (0, 0, 0)) < RELEASE_57:
        fail(f"ttm.json predates engine 5.7 — the run's basis read a ttm.json stamped engine_release "
             f"{rel or 'none (pre-5.7)'}: its TTM legs were built without the 5.7 capex rules (capitalized software, "
             f"every filed PP&E component) although this record is engine release {n.get('engine_release')} — rerun "
             "ttm.py with the current engine, then the engine (--ttm) and make_score.")
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
    # v5.7 (09 rebase A5): the ttm.py stamp is part of the record, so the refusal prints it — a re-stamped ttm.json
    # with identical legs differs only here, and the worker must see which release built which file
    return (f"ttm_oe_per_share {r.get('ttm_oe_per_share')}, ttm_shares_diluted {r.get('ttm_shares_diluted')}, "
            f"ytd_current_period {r.get('ytd_current_period')}, ttm_input_hash {str(h)[:12] + '…' if h else h}, "
            f"ttm_engine_release {r.get('ttm_engine_release') or 'none (unstamped)'}")


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
    it. Any other older record keeps the 0.1% base check alone.
    v5.7 (09 rebase A5): ttm_inputs_record carries ttm_engine_release when ttm.json is stamped (ttm.py stamps it
    since 5.7; outside ttm_input_hash). A record that is not a 5.7 run and recorded no stamp (every pre-5.7 engine)
    is compared without it, so rerunning ttm.py under 5.7 with identical legs leaves older output rebuilding as
    before; on a 5.7 run the stamp is bound like every other field (a stamp-only change names both releases)."""
    if "ttm_inputs" in n:
        rec = n.get("ttm_inputs")
        if rec is None:
            return
        now = _engine.ttm_inputs_record(tt)
        if isinstance(rec, dict) and "ttm_engine_release" not in rec and not is_57_run(n):
            now.pop("ttm_engine_release", None)
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
    the base's own: a pin built from ttm.json's TTM figures on another denominator has the current YTD's cash flows
    in it, and without the declaration a charge there counted as $0 (v5.7, L8: at a declaring filer the per-unit TTM
    base is --ttm itself, share_classes; a total-unit pin also states share_basis "total_units"). On a 5.6 run the
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
    (`trace_only` values are accepted but never an engine match, even where an engine leaf has the same value; the
    values at its dcf_numbers.json paths leave the engine set — from a saved run too where it repeats them — and are
    accepted without blocking another leaf's match, L3b review 2026-10-21); (4) every number rests
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
    tag = _facts.influence_tag(field)   # v5.7 (R7 lane): capex_unlisted_ack.<tag> -> its map's tag
    ids = list(dict.fromkeys(fact_ids or []))
    nq = fc.not_quantities() if fc is not None else ()
    hint = ""
    if field == "tier_override_reason" and iprd_override_required(n):
        hint = (" (an unverified-share-count IPR&D override: cite the verified share count as a filing fact, the "
                "per-share charge as a calc fact, and quote the adjusted IRR from a saved run — check_quotes.py "
                f"--save-run {n.get('ticker')} <label>)")
    vals, paths = _trace_only_split(trace_only)
    acc = None
    if paths:
        # [L3b review, 2026-10-21] the figures at the excluded paths trace (`accepted`) but only trace_only's VALUES are
        # never an engine match: a per-year series there (paths, growth_paths) may coincide with an independent figure
        acc = _qt.ValueSet()
        for p in paths:
            acc.merge(_numeric_values(_quotes.path_value(n, p)))
    engine = _quotes.influence_sources(folder, n, facts_doc=fc.doc if fc is not None else None, exclude_paths=paths)
    res = _facts.influence_support(s, ids, fc, engine, tag, extra=_numeric_values(extra) if extra is not None else None,
                                   trace_only=vals, not_quantities=nq, accepted=acc)
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
    if inp.get("moat_trend") is not None:   # v5.7 M6 (L3b): every counterfactual replays the scored growth hold
        args += ["--moat-trend", str(inp["moat_trend"])]
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
# v5.7 lane L4 (R2 foreign filers, Andrew 2026-10-19): the annual-instance check (R2b) and the declared 6-K interim
# bridge (R2a) — interim_bridge.py holds the rules, ttm.py --interim builds the record, this re-verifies, measures
# and reports it
# ---------------------------------------------------------------------------
INTERIM_KEY, INTERIM_DECLINED_KEY = "interim_bridge", "interim_bridge_declined"
INTERIM_FLAG = "TTM_DECLARED_INTERIM"
# Default Q7 (main agent, 2026-10-21, pending Andrew): "re_declare" — on a 5.7 STALE_FY 20-F / 40-F run, any base but
# the payable pin and a declared bridge (a median, a plain or an iprd_amortized --base-oe-ps pin, a 10-Q ttm.json)
# needs interim_bridge or interim_bridge_declined, so TFII / FUTU / VIV's hand-built 6-K pins are re-declared on their
# next engine run. "median_only" restores design 04's predicate (a median base only). The one switch.
INTERIM_OBLIGATION_RULE = "re_declare"
INTERIM_REL_TOL = 1e-9
SCORE_DECISION_KEYS = SCORE_DECISION_KEYS + (INTERIM_KEY, INTERIM_DECLINED_KEY)   # L4's decision fields (L5's P2)


def annual_instance_check(folder, n):
    """v5.7 (L4, R2b; 07 §1.12 step 1, after the content-hash check): when the run read annual facts from the
    filing's own XBRL instance (dcf_numbers.json annual_from_instance applied), <T>/annual_instance.json must be that
    instance's — the same accession and instance_sha256 — and its facts must still hash to the run's facts_sha256 (it
    is the run's input, bound like ttm.json: rebase amendment 6). Returns the record (for key_numbers.md), else None."""
    rec = n.get("annual_from_instance")
    if not isinstance(rec, dict) or not rec.get("applied"):
        return None
    import xbrl_instance as _xi
    try:
        with open(f"{folder}/annual_instance.json", encoding="utf-8") as f:
            doc = json.load(f)
    except (OSError, ValueError):
        doc = None
    if (not isinstance(doc, dict) or doc.get("accession") != rec.get("accession")
            or doc.get("instance_sha256") != rec.get("instance_sha256")):
        fail(f"dcf_numbers.json says annual facts were read from the XBRL instance of {rec.get('accession')} but "
             f"{n.get('ticker')}/annual_instance.json is missing or differs — commit the file the engine wrote, or rerun "
             "the engine")
    if _xi.facts_sha256(doc.get("facts"), doc.get("conflicts")) != rec.get("facts_sha256"):
        fail("annual_instance.json changed after the engine run (its facts no longer hash to dcf_numbers.json "
             "annual_from_instance.facts_sha256) — rerun dcf_engine.py; it is the run's input")
    return rec


def _ttm_record(folder):
    """ttm.json as an object, or None."""
    try:
        with open(f"{folder}/ttm.json", encoding="utf-8") as f:
            tt = json.load(f)
    except (OSError, ValueError):
        return None
    return tt if isinstance(tt, dict) else None


def _is_declared_interim(tt):
    return isinstance(tt, dict) and tt.get("basis") == _ib.RECORD_BASIS


def _interim_pinned(ticker, n):
    """True when the run is pinned through --ttm to a declared-interim ttm.json (its figure)."""
    if not ticker:
        return False
    tt = _ttm_record(f"{BASE}/{ticker}")
    return (_is_declared_interim(tt) and (n.get("inputs") or {}).get("base_pin_source") == "ttm_json"
            and _engine.figure_matches(n.get("base_oe_per_share"), tt.get("ttm_oe_per_share")))


def _rel_eq(a, b, tol=INTERIM_REL_TOL):
    return (_num(a) is not None and _num(b) is not None
            and abs(float(a) - float(b)) <= tol * max(1.0, abs(float(a)), abs(float(b))))


def _interim_rule_problems(n, decl, tt):
    """Step 7 of _interim_problems (review fix 2026-10-21): interim_bridge.py's pure rules re-run on the declaration —
    the one bundle ttm.py --interim runs (declaration_rule_problems: periods, sources, snippets, estimates, definitions,
    like-for-like, the share band) on the FY leg, report period and filing date ttm.json recorded, as of the run's
    as_of — and the declared report is the 6-K ttm.py verified. Without it a judgment edit that breaks a rule, with
    ttm.json's declaration_hash patched to it (declaration_hash is outside TTM_INPUT_TOP_FIELDS, so
    check_ttm_inputs_current passes), scored on the generated file's word."""
    legs = tt.get("legs") if isinstance(tt.get("legs"), dict) else {}

    def fy_val(f, k):
        lg = legs.get(f) if isinstance(legs.get(f), dict) else {}
        return _num((lg.get("fy") if isinstance(lg.get("fy"), dict) else {}).get(k))
    per = tt.get("periods") if isinstance(tt.get("periods"), dict) else {}
    fy = per.get("fy")
    fy = list(fy) if isinstance(fy, list) and len(fy) == 2 and all(_ib._is_date(x) for x in fy) else None
    rep = tt.get("report") if isinstance(tt.get("report"), dict) else {}
    shares = tt.get("shares") if isinstance(tt.get("shares"), dict) else {}
    probs = _ib.declaration_rule_problems(
        decl, fy, {f: fy_val(f, "local") for f in _ib.FLOW_FIELDS}, {f: fy_val(f, "usd") for f in _ib.FLOW_FIELDS},
        _num(shares.get("fy_diluted")), today=str(n.get("as_of") or _engine.ET_TODAY.isoformat()),
        report_date=rep.get("period_end"), filed=rep.get("filed"), report_source=rep.get("period_end_source"))
    acc = (decl.get("report") or {}).get("accession")
    if acc != rep.get("accession"):
        probs.append(f"[IB-SRC1] judgment.json interim_bridge.report.accession {acc} is not the 6-K ttm.py --interim "
                     f"verified ({rep.get('accession')})")
    return probs


def _interim_problems(n, j, tt, folder=None):
    """[(step, message)]: design 04 A.5 interim_pin_state checks 1, 2, 4, 5, 6 on a declared-interim ttm.json —
    (1) judgment.json declares a valid interim_bridge, (2) its hash is ttm.json's, (4) ttm.json's arithmetic
    reproduces from its own legs and those legs are the declaration's, (5) the FY leg is this run's, (6) the ADS ratio
    is the engine's — and (7, review fix 2026-10-21) the declaration passes interim_bridge.py's pure rules again
    (_interim_rule_problems), so make_score re-verifies what ttm.py enforced instead of trusting ttm.json. Steps 1-2
    stop the list (nothing else can be compared)."""
    t = n.get("ticker")
    decl = (j or {}).get(INTERIM_KEY)
    if decl is None or _ib.validate_shape(decl):
        return [(1, f"ttm.json is a declared interim bridge but judgment.json declares no (valid) interim_bridge — rerun "
                    f"ttm.py {t} --interim")]
    h = _ib.declaration_hash(decl)
    if h != tt.get("declaration_hash"):
        return [(2, f"judgment.json interim_bridge changed after ttm.py --interim ran (declaration hash {h[:12]}… vs "
                    f"ttm.json {str(tt.get('declaration_hash'))[:12]}…) — rerun ttm.py {t} --interim and the engine "
                    "with --ttm")]
    out = []
    rc = _ib.recompute_from_record(tt)
    edited = rc is None
    if not edited:
        # v5.7 (L8, 08 §5.4): at a declaring filer the bridge's own arithmetic is ttm.json's filed-basis twins, and the
        # share-class rescale onto total units is re-derived on its own (sc_interim_rescale_edited)
        _want = sc_interim_filed_view(tt)
        for k in ("ttm_ocf", "ttm_capex", "ttm_sbc", "ttm_shares_diluted", "ttm_oe_total", "ttm_oe_per_share"):
            edited = edited or not _rel_eq(rc[k], _want.get(k))
        edited = edited or sc_interim_rescale_edited(rc, tt, j)
        ins = tt.get("inputs") if isinstance(tt.get("inputs"), dict) else {}
        for k, v in (("ocf", tt.get("ttm_ocf")), ("capex", tt.get("ttm_capex")), ("sbc", tt.get("ttm_sbc"))):
            edited = edited or not _rel_eq((ins.get(k) or {}).get("ttm") if isinstance(ins.get(k), dict) else None, v)
        for f in _ib.FLOW_FIELDS:
            for name in _ib.LEG_NAMES:
                x = _ib.leg(decl, f, name) or {}
                edited = edited or not _rel_eq(((tt.get("legs") or {}).get(f) or {}).get(name, {}).get("local"),
                                               x.get("value"))
        sx = _ib.leg(decl, _ib.SHARES_FIELD, "current_interim") or {}
        edited = edited or not _rel_eq(((tt.get("shares") or {}).get("current_interim") or {}).get("value"), sx.get("value"))
        ru = ((tt.get("fx") or {}).get("rates_used") or {}) if isinstance(tt.get("fx"), dict) else {}
        dfx = decl.get("fx") or {}
        for name in _ib.LEG_NAMES:
            want = (dfx.get(name) or {}).get("rate") if dfx.get("basis") == "ecb_period_end" else 1.0
            got = ru.get(name)
            edited = edited or _num(got) is None or _num(want) is None or abs(float(got) - float(want)) > \
                _ib.FX_TOLERANCE * float(want) + 1e-12
        if not edited and dfx.get("basis") == "ecb_period_end":
            r_fy = (((n.get("fx_conversion") or {}).get("rates_by_currency") or {}).get(decl.get("currency")) or {}).get(
                n.get("latest_period_end"))
            edited = not _rel_eq(ru.get("fy"), r_fy)
    if edited:
        out.append((4, f"ttm.json's interim arithmetic does not reproduce from its own legs (or its legs and rates are "
                       f"not the declaration's) — it was edited; rerun ttm.py {t} --interim"))
    er = tt.get("engine_record") if isinstance(tt.get("engine_record"), dict) else {}
    rows = _csv_rows(folder) if folder else []
    last = rows[-1] if rows else {}
    fy_bad = None
    if er.get("engine_release") != n.get("engine_release"):
        fy_bad = f"engine_release: ttm.json {er.get('engine_release')}, the run {n.get('engine_release')}"
    elif ((tt.get("periods") or {}).get("fy") or [None, None])[1] != n.get("latest_period_end"):
        fy_bad = (f"latest FY end: ttm.json {((tt.get('periods') or {}).get('fy') or [None, None])[1]}, the run "
                  f"{n.get('latest_period_end')}")
    elif last:
        assumed_zero = str(last.get("capex_assumed_zero")) == "True"
        csv_fy = {"ocf": _f(last.get("ocf")), "capex_ppe": _f(last.get("capex_ppe")),
                  "capex_intangibles": 0.0 if assumed_zero else (_f(last.get("capex_intangibles")) or 0.0),
                  "sbc": _f(last.get("sbc"))}
        for f in _ib.FLOW_FIELDS:
            got = (((tt.get("legs") or {}).get(f) or {}).get("fy") or {}).get("usd")
            if not _rel_eq(got, csv_fy[f], 1e-6):
                fy_bad = f"{f}: ttm.json {got}, financials_history.csv {csv_fy[f]}"
                break
        else:
            # v5.7 (L8, 08 §5.4): on a declared run the CSV's count is total units, ttm.json's fy_diluted the filed traded
            # count with fy_total_units beside it
            got = (tt.get("shares") or {}).get("fy_total_units", (tt.get("shares") or {}).get("fy_diluted"))
            if not _rel_eq(got, _f(last.get("shares_diluted")), 1e-6):
                fy_bad = f"shares_diluted: ttm.json {got}, financials_history.csv {last.get('shares_diluted')}"
    else:
        fy_bad = "financials_history.csv is missing"
    if fy_bad:
        out.append((5, f"the bridge's FY leg is not this run's latest FY ({fy_bad}) — rerun ttm.py {t} --interim after the "
                       "engine"))
    n_ads = (n.get("ads_ratio") or {}).get("ratio") if isinstance(n.get("ads_ratio"), dict) else None
    if not _rel_eq(tt.get("ads_ratio"), n_ads, 1e-12):
        out.append((6, f"ttm.json applied ADS ratio {tt.get('ads_ratio')}, the engine {n_ads} — rerun ttm.py {t} --interim"))
    rules = _interim_rule_problems(n, decl, tt)
    if rules:
        out.append((7, "judgment.json interim_bridge breaks the rules ttm.py --interim enforces (" + "; ".join(rules)
                    + f") — ttm.py would refuse this declaration, so ttm.json was not built from it; fix the declaration "
                    f"and rerun ttm.py {t} --interim and the engine with --ttm"))
    return out


def _interim_record_problems(n, j, tt, folder=None):
    """The messages of _interim_problems (R7's ttm_for_run reads a non-empty list as status "fixable")."""
    return [m for _, m in _interim_problems(n, j, tt, folder)]


def interim_pin_state(folder, n, j, tt):
    """v5.7 (L4, R2a; 07 §1.12 step 3, after check_ttm_inputs_current, which already refused a ttm.json regenerated
    after the run): None unless ttm.json is a declared interim bridge (basis "declared_interim") and the run's base is
    its figure; then design 04 A.5's checks in order, each a refusal — (1) a valid interim_bridge declaration, (2) its
    hash is ttm.json's, (3) the pin is base_pin_source ttm_json (a --base-oe-ps copy of the figure is not accepted),
    (4) the arithmetic reproduces and the legs are the declaration's, (5) the FY leg is this run's, (6) the ADS ratio
    is the engine's. Returns {"ttm", "decl", "hash", "estimate_legs", "unverified_legs", "xbrl_verified_legs"}; the
    measurement attaches itself as "measurement" (interim_bridge_measurement)."""
    if not _is_declared_interim(tt):
        return None
    inp = n.get("inputs") or {}
    pinned = inp.get("base_oe_ps_arg") is not None or "ttm" in (n.get("base_source") or "").lower()
    if not pinned or not _engine.figure_matches(n.get("base_oe_per_share"), tt.get("ttm_oe_per_share")):
        return None
    probs = _interim_problems(n, j, tt, folder)
    if probs and probs[0][0] in (1, 2):
        fail(probs[0][1])
    if inp.get("base_pin_source") != "ttm_json":
        fail(f"a declared interim bridge pins the base only through --ttm (base_pin_source {inp.get('base_pin_source')!r}) "
             "— a --base-oe-ps copy of the figure is not accepted; rerun the final pass with --ttm")
    if probs:
        fail("; ".join(m for _, m in probs))
    return {"ttm": tt, "decl": j[INTERIM_KEY], "hash": tt["declaration_hash"],
            "estimate_legs": list(tt.get("estimate_legs") or []), "unverified_legs": list(tt.get("unverified_legs") or []),
            "xbrl_verified_legs": list(tt.get("xbrl_verified_legs") or [])}


def validate_interim_declined(j):
    """judgment.json interim_bridge_declined {reason, report} — "no bridge could be built": the 6-K checked and why it
    cannot bridge (no cash-flow statement, a comparative that is not like-for-like, ...). A malformed one (not an
    object, an empty reason, a report that is neither null nor {form, accession, document}) is refused on any release;
    the reason's number is required by the 5.7 obligation (check_interim_obligation). None when absent."""
    d = (j or {}).get(INTERIM_DECLINED_KEY)
    if d is None:
        return None
    if not isinstance(d, dict) or not str(d.get("reason") or "").strip():
        fail("judgment.json interim_bridge_declined must be {reason, report}: reason a non-empty string naming the 6-K "
             "checked and why it cannot bridge, with a number; report {form, accession, document} or null")
    rep = d.get("report")
    if rep is not None and not (isinstance(rep, dict) and str(rep.get("accession") or "").strip()):
        fail("judgment.json interim_bridge_declined.report must be null or {form, accession, document} (the interim "
             "report that was checked)")
    return {"reason": str(d["reason"]).strip(), "report": rep}


def _interim_obligation_applies(n):
    """Whether a 5.7 STALE_FY 20-F / 40-F run without a pinned bridge owes interim_bridge or interim_bridge_declined
    (INTERIM_OBLIGATION_RULE, default Q7)."""
    src = (n.get("inputs") or {}).get("base_pin_source")
    if INTERIM_OBLIGATION_RULE == "median_only":
        return src is None
    return src != "judgment_base_override"


def check_interim_obligation(n, j, interim, plan=None):
    """v5.7 (L4, R2a; 07 §1.12 step 3, after R7's plan). Refusals, in order:
    - interim_bridge and interim_bridge_declined together (a bridge that was built is not declined);
    - the binding: judgment.json declares interim_bridge but the final run is not pinned through --ttm to its
      ttm.json — unless R7's plan rejects the bridge with a qualifying ttm_rejection_reason (plan["bridge_rejected"],
      rebase amendment 16); an iprd_amortized pin or a basis_window "ttm" base_override beside the bridge gets its own
      message (amendment 12);
    - the 5.7 obligation (5.7 runs only, D1): a 20-F / 40-F run with a STALE_FY flag and no pinned or rejected bridge
      declares interim_bridge_declined with a reason that carries a number (which bases owe it: INTERIM_OBLIGATION_RULE).
    Returns the validated interim_bridge_declined (or None)."""
    declined = validate_interim_declined(j)
    has_bridge = isinstance(j, dict) and j.get(INTERIM_KEY) is not None
    t = n.get("ticker")
    if has_bridge and declined is not None:
        fail("judgment.json declares both interim_bridge and interim_bridge_declined — a bridge that was built is not "
             "declined: keep one")
    bridge_rejected = bool(plan and plan.get("bridge_rejected"))
    if has_bridge and interim is None and not bridge_rejected:
        bo = j.get("base_override") if isinstance(j.get("base_override"), dict) else {}
        if bo.get("basis") == IPRD_AMORTIZED_BASIS:
            fail("an acquired-IPR&D amortized pin cannot sit on a declared interim bridge — pin through --ttm (the "
                 "one-time deduction applies) or remove interim_bridge")
        if isinstance(bo.get("basis_window"), dict) and bo["basis_window"].get("window") == "ttm":
            fail("a declared interim bridge pins only through --ttm; a per-unit pin on its figures needs share_classes "
                 "(R6) — remove the base_override and pin with --ttm")
        fail(f"judgment.json declares interim_bridge but the final run is not pinned through --ttm to a declared-interim "
             f"ttm.json (base_source {n.get('base_source')}) — run ttm.py {t} --interim and the final engine pass with "
             "--ttm, or remove interim_bridge and record why in interim_bridge_declined — or keep it declared and "
             "reject it with ttm_rejection_reason (the bridge is then measured beside the published base)")
    if not is_57_run(n) or n.get("filer_annual_form") not in ("20-F", "40-F"):
        return declined
    if not any(str(f).startswith("STALE_FY") for f in n.get("fragility_flags") or []):
        return declined
    if interim is not None or (has_bridge and bridge_rejected) or not _interim_obligation_applies(n):
        return declined
    pin_note = ("" if (n.get("inputs") or {}).get("base_pin_source") is None else
                " — the run is pinned (base_pin_source "
                f"{(n.get('inputs') or {}).get('base_pin_source')!r}): a hand-built 6-K pin is re-declared as "
                "interim_bridge (default Q7)")
    if declined is None:
        fail(f"STALE_FY at a 20-F / 40-F filer on a 5.7 run: declare interim_bridge (python3 _system/ttm.py {t} "
             "--interim-draft <6-K accession>, then --interim and --ttm) or interim_bridge_declined {reason, report} "
             "naming the interim report checked and why it cannot bridge, with a number (no cash-flow statement, "
             f"comparative not like-for-like, ...){pin_note}")
    if not re.search(r"\d", declined["reason"]):
        fail("judgment.json interim_bridge_declined.reason carries no number — say what the interim report checked "
             "shows (or lacks) with a figure (R2: the 6-K's period, the missing line, the size of the perimeter change)")
    return declined


def _r4(v):
    return round(float(v), 4) if _num(v) is not None else None


def _measured_entry(m):
    """The annual-median figures of a --measure replay (base, weighted IRR, tier, the replay's own IPR&D charge)."""
    blk = m.get("iprd_adjustment") if isinstance(m.get("iprd_adjustment"), dict) else {}
    return {"base_oe_per_share": _r4(m.get("base_oe_per_share")), "weighted_irr": _r4(m.get("implied_irr_weighted")),
            "tier_by_numbers": m.get("tier_by_numbers"), "f_subtype": m.get("f_subtype"),
            "iprd_charge_per_share": round(_engine.iprd_charge_per_share(m), 4), "iprd_treatment": blk.get("treatment"),
            "data_gap": list(m.get("data_gap") or [])}


def interim_bridge_measurement(ticker, n, interim, release_mismatch, prior_score=None):
    """v5.7 (L4, R2a; 07 §1.12 step 4, after the override impact, before the first write): the bridged base beside
    the annual-median base (R2: "report BOTH"). Current release: one --measure replay of the final configuration
    with no pin (_final_run_args), field overrides on and NO DCF_IPRD_HOLD — the median takes its own acquired-IPR&D
    window and share count (rebase amendment 14, I5); labelled DCF_REPLAY_PURPOSE=base_alternatives (R7 folds this
    replay into build_base_alternatives). A failed replay refuses. Release mismatch: no replay — R7's one carry rule
    (carried_base_alternatives, design 11 §3.7 / §7.2; review fix 4): the prior score's annual-median entry is carried,
    its note too, when the prior record declared this bridge (its interim_bridge declaration_hash) and published it as
    declared_interim at this bridged base and weighted IRR (4 dp), else the fields are null with the not-measured note.
    Attaches itself to `interim` as "measurement"; None without a bridge."""
    if interim is None:
        return None
    bridged = {"base_oe_per_share": _r4(n.get("base_oe_per_share")), "weighted_irr": _r4(n.get("implied_irr_weighted")),
               "tier_by_numbers": n.get("tier_by_numbers"), "f_subtype": n.get("f_subtype"),
               "iprd_charge_per_share": round(_engine.iprd_charge_per_share(n), 4),
               "iprd_treatment": (n.get("iprd_adjustment") or {}).get("treatment")
               if isinstance(n.get("iprd_adjustment"), dict) else None}
    meas = {"bridged": bridged, "annual_median": None, "measured": False, "note": None, "replays": 0,
            "impact_carried_from_prior_score": False, "counterfactual_engine_release": None}
    if release_mismatch:
        pib = (prior_score or {}).get(INTERIM_KEY) if isinstance(prior_score, dict) else None
        same_decl = isinstance(pib, dict) and pib.get("declaration_hash") == interim["hash"]
        e = _alt_entry("annual_median", "alternative", bridged, True, False,
                       vals=_unmeasured(n.get("base_oe_normalized_per_share")))
        carried, cer, note = carried_base_alternatives(n, prior_score if same_decl else None,
                                                       {"kind": "declared_interim"}, bridged, [e],
                                                       [(0, "annual_median", False)])
        meas.update(annual_median={k: e.get(k) for k in _VAL_KEYS}, measured=bool(e["measured"]),
                    note=e.get("note") if carried else note, impact_carried_from_prior_score=carried,
                    counterfactual_engine_release=cer)
    else:
        # v5.7 (R7, 11 §7.2): R7's one replay routine (_replay_alternative: the same command and label, field overrides
        # on, no DCF_IPRD_HOLD) with its outcome rules — a gap or an engine refusal of the median is recorded
        # (computed: false with the note), a failed run refuses (R7-9), a base other than the record's median refuses
        # (R7-10)
        res = _replay_alternative(ticker, n, "annual_median")
        med = ({k: res.get(k) for k in _VAL_KEYS} if res["computed"]
               else dict({k: None for k in _VAL_KEYS}))
        meas.update(annual_median=med, measured=True, replays=1, note=None if res["computed"] else res["note"])
    interim["measurement"] = meas
    return meas


def _chg(alt, pub):
    """(base_change_pct, weighted_irr_change_pp, tier_changed) of an alternative against the published entry."""
    b, pb = alt.get("base_oe_per_share"), pub.get("base_oe_per_share")
    i, pi = alt.get("weighted_irr"), pub.get("weighted_irr")
    pct = round((b - pb) / abs(pb) * 100, 2) if (_num(b) is not None and _num(pb) is not None and pb) else None
    pp = round((i - pi) * 100, 2) if (_num(i) is not None and _num(pi) is not None) else None
    tiers = alt.get("tier_by_numbers"), pub.get("tier_by_numbers")
    return pct, pp, (tiers[0] != tiers[1]) if all(tiers) else None


def interim_base_alternatives(n, interim, meas):
    """The base_alternatives record of a published declared 6-K bridge (R7's schema, 11 §3.9; rebase amendment 15):
    the declared_interim entry (published, the run's own figures) and the annual_median alternative (the measurement).
    Built inside R7's one builder (build_base_alternatives), never a second shape."""
    tt = interim["ttm"]
    pub = dict(meas["bridged"], kind="declared_interim", role="published", computed=True, measured=True,
               fy_end=tt.get("fy_end"), ytd_end=tt.get("ytd_end"),
               ttm_input_hash=_engine.ttm_inputs_record(tt)["ttm_input_hash"],
               ttm_engine_release=tt.get("engine_release"), share_basis=None,
               source="ttm.json (ttm.py --interim: FY − prior interim + current interim, declared 6-K)",
               why="declared_interim",
               why_text="published — the declared 6-K interim bridge (judgment.json interim_bridge; R2)", note=None)
    pub = {k: pub[k] for k in ("kind", "role", "computed", "measured", "base_oe_per_share", "weighted_irr",
                               "tier_by_numbers", "f_subtype", "iprd_charge_per_share", "iprd_treatment", "fy_end",
                               "ytd_end", "ttm_input_hash", "ttm_engine_release", "share_basis", "source", "why",
                               "why_text", "note")}
    med = meas["annual_median"] or {}
    computed = med.get("base_oe_per_share") is not None
    # v5.7 (R7): the one entry shape (_alt_entry, 11 §3.9)
    alt = _alt_entry("annual_median", "alternative", pub, computed, bool(meas["measured"]), vals=med,
                     source=MEDIAN_SOURCE, replay=REPLAY_MEDIAN,
                     why_text="not chosen: the declared 6-K interim bridge is the published base (R2)",
                     note=meas.get("note"))
    return {"schema": 1, "published": "declared_interim",
            "stale_fy": any(str(f).startswith("STALE_FY") for f in n.get("fragility_flags") or []),
            "ttm_rejection_reason": None, "ttm_unavailable_reason": None, "bases": [pub, alt],
            "replays": meas.get("replays", 0),
            "measured": bool(meas["measured"]), "note": meas["note"] if not meas["measured"] else None,
            "impact_carried_from_prior_score": bool(meas["impact_carried_from_prior_score"]),
            "counterfactual_engine_release": meas["counterfactual_engine_release"]}


def _interim_fx_text(tt):
    fx = tt.get("fx") or {}
    ru = fx.get("rates_used") or {}
    if fx.get("basis") == "ecb_period_end":
        return (f"each converted at its own period-end ECB rate: FY {float(ru.get('fy')):.4f} (engine) · prior "
                f"{float(ru.get('prior_interim')):.4f} · current {float(ru.get('current_interim')):.4f}")
    if fx.get("basis") == "issuer_convenience_translation":
        return ("the report's own US-dollar convenience translation (rates "
                f"{(fx.get('prior_interim') or {}).get('rate')} / {(fx.get('current_interim') or {}).get('rate')})")
    return "in US dollars as filed (no conversion)"


def interim_flag(interim, meas):
    """score.json's TTM_DECLARED_INTERIM flag text (R2: "flagged in fragility_flags"; make_score's own flag, never in
    the hashed engine output)."""
    tt = interim["ttm"]
    per = tt.get("periods") or {}
    k = len(interim.get("estimate_legs") or [])
    b, med = (meas or {}).get("bridged") or {}, (meas or {}).get("annual_median") or {}
    fx = (tt.get("fx") or {}).get("basis")
    how = {"ecb_period_end": "at per-period ECB rates", "issuer_convenience_translation": "as the issuer's USD translation"
           }.get(fx, "in USD")
    return (f"{INTERIM_FLAG}: base is the declared 6-K interim bridge (FY {tt.get('fy_end')} − prior interim to "
            f"{(per.get('prior_interim') or [None, None])[1]} + current interim to {tt.get('ytd_end')}, "
            f"{tt.get('currency')} {how}; {k} estimate leg{'s' if k != 1 else ''}) — bridged "
            f"{_money(b.get('base_oe_per_share'))}/share, weighted IRR {_pct(b.get('weighted_irr'))}, tier "
            f"{b.get('tier_by_numbers')} vs annual median {_money(med.get('base_oe_per_share'))}/share, "
            f"{_pct(med.get('weighted_irr'))}, tier {med.get('tier_by_numbers') or '—'}"
            + (f" ({meas['note']})" if (meas or {}).get("note") else "")
            + '; see key_numbers.md "Interim bridge"')


def score_interim_fields(score, n, j, interim, interim_meas):
    """v5.7 (L4, R2a; 07 §1.12 step 8): score.json interim_bridge (the declaration's descriptors — its figures are
    base_alternatives', R7's one record), interim_bridge_declined (copied) and the TTM_DECLARED_INTERIM flag
    appended to a NEW fragility_flags list (flags_all and the confidence cap keep reading the engine's list)."""
    declined = validate_interim_declined(j)
    if declined is not None:
        score[INTERIM_DECLINED_KEY] = declined
    if interim is None:
        return None
    tt, decl = interim["ttm"], interim["decl"]
    per = tt.get("periods") or {}
    ru = (tt.get("fx") or {}).get("rates_used") or {}
    score[INTERIM_KEY] = {
        "basis": _ib.RECORD_BASIS, "currency": tt.get("currency"), "declaration_hash": interim["hash"],
        "fy_period": per.get("fy"), "prior_interim_period": per.get("prior_interim"),
        "current_interim_period": per.get("current_interim"),
        "report_form": (tt.get("report") or {}).get("form"), "report_accession": (tt.get("report") or {}).get("accession"),
        "fx": {"basis": (tt.get("fx") or {}).get("basis"), "fy": ru.get("fy"), "prior_interim": ru.get("prior_interim"),
               "current_interim": ru.get("current_interim")},
        "estimate_legs": interim["estimate_legs"], "unverified_legs": interim["unverified_legs"],
        "xbrl_verified_legs": interim["xbrl_verified_legs"],
        "comparative_restated": (decl.get("like_for_like") or {}).get("comparative_restated"),
        "perimeter_changes": [{k: pc.get(k) for k in ("kind", "effective_date", "material", "resolution")}
                              for pc in (decl.get("like_for_like") or {}).get("perimeter_changes") or []],
        "iprd_interim_scan": tt.get("iprd_interim_scan"),
        "measured_in": "base_alternatives"}
    score["fragility_flags"] = list(n.get("fragility_flags") or []) + [interim_flag(interim, interim_meas)]
    return None


# ---------------------------------------------------------------------------
# v5.7 lane R7 — STALE_FY discretion made checkable (Andrew, 2026-10-19, ruling-sheet Q5 option A; design 11):
# a worker MAY reject the TTM base, but only with judgment.json ttm_rejection_reason naming the distorting cash-flow
# line WITH A NUMBER; make_score replays the final configuration on the rejected TTM and records every base computed
# for the run in ONE base_alternatives record (score.json, the registry, key_numbers.md "Base alternatives"), which
# also carries the declared 6-K bridge's both-bases measurement (L4, R2a). Defaults Q13-Q18 are the R7_* switches at
# the top of the module.
# ---------------------------------------------------------------------------
SCORE_DECISION_KEYS = SCORE_DECISION_KEYS + ("base_alternatives",)   # R7's decision field (L5's P2)

# §2: the closed vocabulary of owner's earnings' own lines — operating cash flow and its statement sub-lines, capex
# (PP&E, capitalized software — R9 —, intangibles) and SBC. Case-insensitive; '-' and whitespace interchangeable;
# plurals included. P&L words (revenue, gross margin, EPS, net income, guidance, crack spread, bookings, margin,
# taxes, settlement, restructuring charges) never match: a cyclical peak or trough names operating cash flow (or the
# line that moved) with its figure.
CASH_FLOW_LINE_RE = re.compile(r"""(?ix)(?<![A-Za-z])(?:
    operating[\s-]+cash[\s-]+flows? | cash[\s-]+flows?[\s-]+from[\s-]+operat\w* | cash[\s-]+from[\s-]+operations |
    operating[\s-]+activities | OCF |
    (?:trade[\s-]+|net[\s-]+)?working[\s-]+capital | NWC |
    (?:accounts[\s-]+|trade[\s-]+)?receivables? | contract[\s-]+(?:assets?|liabilit(?:y|ies)) | unbilled |
    inventor(?:y|ies) | (?:accounts[\s-]+|trade[\s-]+)?payables? | accru(?:ed|als?) |
    deferred[\s-]+(?:revenue|income[\s-]+tax(?:es)?|tax(?:es)?) | customer[\s-]+(?:advances?|deposits?|prepayments?) |
    unearned[\s-]+revenue | prepayments? | billings |
    (?:income[\s-]+)?tax(?:es)?[\s-]+paid | cash[\s-]+tax(?:es)? | tax[\s-]+(?:payments?|refunds?) |
    pensions? | retiree[\s-]+benefits? | post-?retirement |
    interest[\s-]+paid | restructuring[\s-]+(?:payments?|cash) | (?:litigation|legal)[\s-]+settlements? |
    settlement[\s-]+payments? | insurance[\s-]+(?:proceeds|recover(?:y|ies)) | collateral | margin[\s-]+deposits? |
    factoring | securiti[sz]ations? |
    capex | capital[\s-]+(?:expenditures?|spending) | PP&E | property,?[\s-]+plant,?[\s-]+(?:and|&)[\s-]+equipment |
    property[\s-]+and[\s-]+equipment | capitali[sz]ed[\s-]+software | intangible[\s-]+(?:asset[\s-]+)?purchases |
    purchases?[\s-]+of[\s-]+intangibles? |
    SBC | (?:stock|share|equity)[\s-]+based[\s-]+compensation | stock[\s-]+compensation
)(?![A-Za-z])""")

# Default Q14: ttm.py's exit-3 message (ttm.py main(): "ttm.py: cannot compute TTM for <T> (CIK <n>): " + the
# problems joined by "; "), one pattern per problem ttm.py prints, each the WHOLE problem in ttm.py's words
# (parse_ttm_py_exit3 matches the line end to end — review fix 3); test_make_score_57_r7 runs ttm.py's real exit-3
# paths offline and holds every message it prints to these patterns.
TTM_PY_EXIT3_HEAD_RE = re.compile(r"ttm\.py: cannot compute TTM for (\S+) \(CIK (\d+)\): ")
_X3_DATE = r"(\d{4}-\d{2}-\d{2})"
_X3_LEG = r"(ocf|capex|sbc|shares_diluted)"
_X3_UNITS = r"([^\s,;]+(?:, [^\s,;]+)*)"
_X3_Q, _X3_APOS = "[\"“”]", "['’]"
TTM_PY_EXIT3_RES = (
    ("no_fy", re.compile(_X3_LEG + r": no annual \(FY\) fact")),
    ("no_current_ytd", re.compile(_X3_LEG + r": no post-FY YTD fact \(no 10-Q since the " + _X3_DATE
                                  + r" fiscal year end\)")),
    ("no_prior_ytd", re.compile(_X3_LEG + r": no prior-year YTD fact matching " + _X3_DATE + r" \(FY start " + _X3_DATE
                                + r"\)")),
    ("no_capex", re.compile(r"capex: no capex facts in companyfacts under any candidate tag and no capex_override in "
                            r"judgment\.json — refusing to zero-fill \(same DATA_GAP standard as the engine\)")),
    ("override_currency", re.compile(r"(capex|sbc): the \1_override is not declared currency " + _X3_Q + "USD" + _X3_Q
                                     + r" at a filer whose core facts are filed in " + _X3_UNITS + r" — ttm\.py"
                                     + _X3_APOS + r"s legs are USD only and it cannot convert the override to fill a "
                                     r"missing leg; declare the filing" + _X3_APOS + r"s US-dollar figure with currency "
                                     + _X3_Q + "USD" + _X3_Q + r", or leave the TTM unbuilt")),
    ("intangibles_currency", re.compile(r"capex (fy|ytd_prior|ytd_current): intangible purchases for " + _X3_DATE
                                        + r"\.\." + _X3_DATE + r" are filed only in " + _X3_UNITS + r"; ttm\.py reads "
                                        r"USD facts only and holds no FX rates, so it cannot include them \(the annual "
                                        r"engine converts and adds them\) — no TTM base; use the median base")),
)
# The us-gaap tags ttm.py reads per leg (its OCF_TAGS / CAPEX_TAGS / SBC_TAGS / SHARE_TAGS — the engine's own lists'
# us-gaap entries; test_make_score_57_r7 holds them equal): a latest-FY CSV row read from one of them in USD is
# evidence ttm.py found that leg's annual fact.
TTM_PY_LEG_TAGS = {
    "ocf": tuple(t for t in _engine.ENGINE_OCF_TAGS if isinstance(t, str)),
    "capex": tuple(t for t in _engine.CAPEX_ROLLUP_TAGS + _engine.CAPEX_COMPONENT_TAGS if isinstance(t, str)),
    "sbc": (_engine.SBC_SHARE_TAG, _engine.SBC_ALLOCATED_TAG),
    "shares_diluted": tuple(t for t in _engine.ENGINE_SHARES_DILUTED_TAGS if isinstance(t, str)),
}
TTM_TTM_SOURCE = "ttm.json (ttm.py: FY − prior YTD + current YTD, 10-Q)"
TTM_INTERIM_SOURCE = "ttm.json (ttm.py --interim: FY − prior interim + current interim, declared 6-K)"
MEDIAN_SOURCE = "median_of_last_3_fy_oe_per_share"
REPLAY_TTM = "--measure --ttm (final configuration, field overrides on)"
REPLAY_MEDIAN = "--measure (final configuration, field overrides on, no pin)"
_TTM_KINDS = ("ttm", "declared_interim")


def _stale_fy(n):
    return any(str(f).startswith(STALE_FY_PREFIX) for f in (n or {}).get("fragility_flags") or [])


def _r7_scope(stale):
    """Default Q13 (R7_OBLIGATION_SCOPE): the reason binds a STALE_FY run only ("stale_fy"), or every 5.7 run beside a
    TTM for its latest FY ("ttm_present", the ruling's literal reading)."""
    return bool(stale) if R7_OBLIGATION_SCOPE == "stale_fy" else True


def ttm_rejection_problem(text):
    """judgment.json ttm_rejection_reason's own rule (§2; pure): the refusal sentence, or None. [TTM-REJ0] not a
    non-empty string; [TTM-REJ1] it names no cash-flow line (CASH_FLOW_LINE_RE); [TTM-REJ2] it carries no figure —
    L2's one definition of "a number" (quote_tokens.carries_number: dates, years, period labels, form names, small
    counts and method constants do not count). Line and figure are checked over the whole text; REJ1 and REJ2 are
    reported together. Every surviving figure must then trace (check_influence, main() step 7)."""
    if not isinstance(text, str) or not text.strip():
        return f"[TTM-REJ0] judgment.json ttm_rejection_reason must be a non-empty string (got {repr(text)[:60]})"
    probs = []
    if not CASH_FLOW_LINE_RE.search(text):
        probs.append("[TTM-REJ1] it names no cash-flow line (operating cash flow or one of its lines — working capital, "
                     "receivables, inventories, payables, deferred revenue, taxes paid, pension …; capex; SBC)")
    if not _qt.carries_number(text):
        probs.append("[TTM-REJ2] it carries no figure (dates, years, period labels and small counts do not count)")
    if probs:
        return ("judgment.json ttm_rejection_reason does not qualify: " + "; ".join(probs)
                + " — 'working-capital timing' with no figure does not qualify (R7)")
    return None


def _fy_start_matches(start, latest):
    """True when ISO date `start` opens the fiscal year ending `latest` (start + 1 year - 1 day within 10 days)."""
    try:
        s, e = datetime.date.fromisoformat(start), datetime.date.fromisoformat(latest)
        try:
            end = s.replace(year=s.year + 1) - datetime.timedelta(days=1)
        except ValueError:   # 29 February
            end = s.replace(year=s.year + 1, day=28) - datetime.timedelta(days=1)
        return abs((end - e).days) <= 10
    except (TypeError, ValueError):
        return False


def parse_ttm_py_exit3(text):
    """ttm.py's exit-3 line, verbatim (default Q14; review fix 3): (head match, [(problem name, match), ...]) when
    `text`, stripped, is the head "ttm.py: cannot compute TTM for <T> (CIK <n>): " followed by one or more problems in
    ttm.py's own words — each matched whole (TTM_PY_EXIT3_RES) — joined by "; " and NOTHING else (no prose around
    the line, no fragment of a problem); None otherwise. Pure."""
    if not isinstance(text, str):
        return None
    s = text.strip()
    head = TTM_PY_EXIT3_HEAD_RE.match(s)
    if head is None:
        return None
    pos, hits = head.end(), []
    while True:
        hit = None
        for name, rx in TTM_PY_EXIT3_RES:
            m = rx.match(s, pos)
            if m is not None and (m.end() == len(s) or s.startswith("; ", m.end())):
                hit = (name, m)
                break
        if hit is None:
            return None
        hits.append(hit)
        if hit[1].end() == len(s):
            return head, hits
        pos = hit[1].end() + 2


def _csv_float(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if math.isfinite(f) else None


def _ttm_py_filed_leg(n, rows, leg):
    """The us-gaap tag this run's latest-FY `leg` was read from, when ttm.py reads that fact too — financials_history.csv's
    row for n["latest_period_end"] holds the leg from a filed fact (not an override, an assumed-zero capex or a share
    fallback outside ttm.py's tags) under one of TTM_PY_LEG_TAGS, in USD (no fx_conversion) and from EDGAR companyfacts
    (not the filing's own instance, annual_from_instance) — else None. Evidence that ttm.py's "<leg>: no annual (FY)
    fact" / "capex: no capex facts in companyfacts …" is not this run's message (ttm.py reads the same companyfacts,
    us-gaap, USD, 330-380-day periods). Pure."""
    if (n or {}).get("fx_conversion"):
        return None
    latest = (n or {}).get("latest_period_end")
    afi = n.get("annual_from_instance") if isinstance(n.get("annual_from_instance"), dict) else {}
    if afi.get("applied") and latest in (afi.get("periods_added") or []):
        return None
    row = next((r for r in reversed(rows or []) if isinstance(r, dict) and r.get("period_end") == latest), None)
    if row is None:
        return None
    tags = TTM_PY_LEG_TAGS[leg]
    if leg == "capex":
        tag = str(row.get("capex_tag") or "").split("+")[0]
        ok = (str(row.get("capex_source") or "").startswith(("rollup", "components"))
              and _csv_float(row.get("capex_ppe") if row.get("capex_ppe") not in (None, "") else row.get("capex"))
              is not None)
    elif leg == "shares_diluted":
        tag = str(row.get("shares_tag") or "")
        tag = tag[len("FALLBACK:"):] if tag.startswith("FALLBACK:") else tag
        ok = _csv_float(row.get("shares_diluted")) is not None
    else:
        tag = str(row.get(f"{leg}_tag") or "")
        ok = _csv_float(row.get(leg)) is not None
    return tag if (ok and tag in tags) else None


def _ttm_py_override_declared(j, field):
    """Whether ttm.py would read judgment.json's <field>_override as an override NOT declared in USD (ttm.py
    load_overrides: a numeric value, kind filing / estimate, a source and a reason; currency upper-cased) — the only
    case ttm.py prints its override-currency problem. Pure."""
    o = (j or {}).get(f"{field}_override") if isinstance(j, dict) else None
    return bool(isinstance(o, dict) and isinstance(o.get("value"), (int, float)) and not isinstance(o.get("value"), bool)
                and o.get("kind") in ("filing", "estimate") and str(o.get("source") or "").strip()
                and str(o.get("reason") or "").strip()
                and str(o.get("currency") or "").strip().upper() != "USD")


def ttm_unavailable_problem(text, n, ticker, rows=None, j=None):
    """Default Q14: judgment.json ttm_unavailable_reason must BE ttm.py's exit-3 line for this run, verbatim
    (parse_ttm_py_exit3: the head, then whole problems in ttm.py's words joined by "; ", nothing else) — for this
    ticker and CIK; every dated problem about this run's latest FY (no post-FY YTD fact: that FY's end; no prior-year
    YTD fact: that FY's start; an intangible-currency leg: its period inside that FY or the YTD after it); and no
    undated problem the record contradicts (review fix 3): "<leg>: no annual (FY) fact" / "capex: no capex facts …"
    while financials_history.csv's latest-FY row (`rows`) holds the leg from a fact ttm.py reads (_ttm_py_filed_leg),
    an override-currency problem while judgment.json (`j`) declares no such override or declares it in USD. Without
    rows / j those two checks have no evidence and pass. The refusal sentence, or None (pure)."""
    if not isinstance(text, str) or not text.strip():
        return ("[TTM-UNAV0] judgment.json ttm_unavailable_reason must be a non-empty string — ttm.py's exit-3 message, "
                f"quoted (got {repr(text)[:60]})")
    parsed = parse_ttm_py_exit3(text)
    if parsed is None:
        return ("[TTM-UNAV1] judgment.json ttm_unavailable_reason does not quote ttm.py's exit-3 message — run python3 "
                f"_system/ttm.py {ticker} and copy the line it prints, verbatim and nothing else (\"ttm.py: cannot compute "
                f"TTM for {ticker} (CIK …): <leg>: …\", every problem whole, joined by \"; \"); without it skipping ttm.py "
                "is not checkable (default Q14)")
    head, hits = parsed
    bad = []
    if head.group(1).upper() != str(ticker).upper():
        bad.append(f"it names {head.group(1)}, not {ticker}")
    try:
        cik = int(n.get("cik")) if n.get("cik") is not None else None
    except (TypeError, ValueError):
        cik = None
    if cik is not None and int(head.group(2)) != cik:
        bad.append(f"CIK {head.group(2)}, not the run's {cik}")
    latest = n.get("latest_period_end")
    for name, m in hits:
        if name == "no_current_ytd" and m.group(2) != latest:
            bad.append(f"'{m.group(1)}: no post-FY YTD fact' is about the fiscal year ending {m.group(2)}, not this run's "
                       f"latest FY ({latest})")
        if name == "no_prior_ytd" and not _fy_start_matches(m.group(3), latest):
            bad.append(f"'{m.group(1)}: no prior-year YTD fact' is about the fiscal year starting {m.group(3)}, not this "
                       f"run's latest FY (ending {latest})")
        if name == "intangibles_currency":
            leg, start = m.group(1), m.group(2)
            if leg == "ytd_current":
                try:
                    after = (datetime.date.fromisoformat(start) - datetime.date.fromisoformat(latest)).days
                except (TypeError, ValueError):
                    after = None
                inside = after is not None and 0 <= after <= 10
            else:
                inside = _fy_start_matches(start, latest)
            if not inside:
                bad.append(f"'capex {leg}: intangible purchases for {start}..{m.group(3)}' is not a {leg} leg of this "
                           f"run's latest FY (ending {latest})")
        if name in ("no_fy", "no_capex"):
            leg = m.group(1) if name == "no_fy" else "capex"
            tag = _ttm_py_filed_leg(n, rows, leg)
            if tag:
                bad.append(f"'{m.group(0)}' cannot be this run's: financials_history.csv's FY {latest} row reads {leg} "
                           f"from {tag}, a USD us-gaap fact ttm.py reads")
        if name == "override_currency" and j is not None and not _ttm_py_override_declared(j, m.group(1)):
            bad.append(f"'{m.group(1)}: the {m.group(1)}_override is not declared currency \"USD\"' but judgment.json "
                       f"declares no {m.group(1)}_override ttm.py reads outside USD")
    if bad:
        return ("[TTM-UNAV2] judgment.json ttm_unavailable_reason quotes another run's ttm.py message (" + "; ".join(bad)
                + ") — rerun ttm.py and quote what it prints now")
    return None


def base_used_label(ticker, n):
    """The base the final run actually used, as compute_override_impact labels it (extracted unchanged, v5.7 R7):
    payable_5y, declared_interim (L4), declared_pin, ttm or median_3y."""
    base_src = (n.get("base_source") or "").lower()
    pin_src = (n.get("inputs") or {}).get("base_pin_source")
    pinned = (n.get("inputs") or {}).get("base_oe_ps_arg") is not None or "ttm" in base_src
    return "payable_5y" if (pin_src == "judgment_base_override" or n.get("payable_base")) \
        else "declared_interim" if _interim_pinned(ticker, n) \
        else "declared_pin" if _declared_pin_not_ttm(ticker, n) \
        else "ttm" if pinned else "median_3y"


def published_base_kind(ticker, n):
    """(kind, ttm_published, detail): kind in BASE_KINDS — base_used_label with median_3y read as annual_median;
    ttm_published for ttm / declared_interim and for a declared_pin whose run recorded basis_window "ttm" (a pin built
    from ttm.json's TTM figures on another denominator); detail {"variant": "iprd_amortized" | None, "native_base",
    "basis_window"} for the key_numbers / why text. An iprd_amortized pin is ttm (native ttm_json) or declared_pin
    (native median), exactly as compute_override_impact labels it."""
    lbl = base_used_label(ticker, n)
    kind = "annual_median" if lbl == "median_3y" else lbl
    bw = (n.get("inputs") or {}).get("base_basis_window")
    window = bw.get("window") if isinstance(bw, dict) else None
    am = _iprd_amortized_record(n)
    ttm_pub = kind in _TTM_KINDS or (kind == "declared_pin" and window == "ttm")
    return kind, ttm_pub, {"variant": IPRD_AMORTIZED_BASIS if am is not None else None,
                           "native_base": am.get("native_base") if am is not None else None, "basis_window": window}


def ttm_doc_override_problems(doc, j_over):
    """Row 6 of ttm_for_run (pure): every override ttm.json used to fill a TTM leg (overrides_used) must be the one
    judgment.json declares now — the comparison ttm_leg_overrides makes for a pinned TTM, here as messages (a
    rejected TTM is priced on ttm.json's legs, so a withdrawn or edited override leaves it stale)."""
    out = []
    for u in (doc.get("overrides_used") or []) if isinstance(doc, dict) else []:
        f = u.get("field") if isinstance(u, dict) else None
        if f not in ("capex", "sbc", "shares"):
            continue
        o = (j_over or {}).get(f)
        if o is None:
            out.append(f"ttm.json used a {f}_override that judgment.json no longer declares")
            continue
        uv = _num(u.get("value"))
        if (u.get("kind") != o.get("kind") or uv is None
                or abs(float(o["value"]) - float(uv)) > max(1.0, abs(float(o["value"])) * 0.001)):
            out.append(f"ttm.json used a {f}_override (value {u.get('value')}, kind {u.get('kind')}) that judgment.json "
                       f"declares as value {o['value']}, kind {o['kind']}")
    return out


def ttm_for_run(folder, n, j, j_sc=None, j_over=None):
    """§3.3: <T>/ttm.json as an alternative base for this run — None when ttm.json is absent, unreadable, not an
    object or has no finite numeric ttm_oe_per_share; else {kind (ttm | declared_interim), status, note, fy_end,
    ytd_end, base_oe_per_share, ttm_input_hash, ttm_engine_release, share_basis, doc}, the first matching row deciding
    status: other_fy (not this run's latest FY), off_basis (L8: not on the share_classes declaration), orphan_bridge
    (a declared 6-K bridge judgment.json no longer declares), fixable (L4's record checks fail; a pre-5.7 stamp, L9;
    an override ttm.json used that judgment.json no longer declares the same way) or eligible (priced by a replay).
    other_fy / off_basis / orphan_bridge are not a TTM computed for this run: recorded, never an obligation."""
    doc = _ttm_record(folder)
    if doc is None:
        return None
    v = _num(doc.get("ttm_oe_per_share"))
    if v is None or not math.isfinite(float(v)):
        return None
    t = os.path.basename(os.path.normpath(folder))
    kind = "declared_interim" if _is_declared_interim(doc) else "ttm"
    rel = doc.get("engine_release") if isinstance(doc.get("engine_release"), str) else None
    rerun = f"ttm.py {t} --interim" if kind == "declared_interim" else f"ttm.py {t}"
    latest = n.get("latest_period_end")
    probs = None
    if doc.get("fy_end") != latest:
        status, note = "other_fy", (f"ttm.json is built on FY {doc.get('fy_end')}; this run's latest FY ends {latest} — "
                                    "not this run's TTM (rerun ttm.py)")
    elif not _alt_ttm_ok(doc, j_sc):
        status, note = "off_basis", "ttm.json is not on this share_classes declaration — rerun ttm.py"
    elif kind == "declared_interim" and (j or {}).get(INTERIM_KEY) is None:
        status, note = "orphan_bridge", ("ttm.json is a declared 6-K interim bridge but judgment.json declares no "
                                         "interim_bridge (withdrawn) — not a TTM for this run")
    elif kind == "declared_interim" and (probs := _interim_record_problems(n, j, doc, folder)):
        status, note = "fixable", "; ".join(probs)
    elif (release_tuple(rel) or (0, 0, 0)) < RELEASE_57:
        status, note = "fixable", (f"ttm.json predates engine 5.7 (engine_release {rel or 'none'}): its legs were built "
                                   f"without the 5.7 capex rules — rerun {rerun}")
    elif (probs := ttm_doc_override_problems(doc, j_over)):
        status, note = "fixable", "; ".join(probs) + f" — rerun {rerun} with the current judgment.json"
    else:
        status, note = "eligible", None
    return {"kind": kind, "status": status, "note": note, "fy_end": doc.get("fy_end"), "ytd_end": doc.get("ytd_end"),
            "base_oe_per_share": float(v), "ttm_input_hash": _engine.ttm_inputs_record(doc)["ttm_input_hash"],
            "ttm_engine_release": rel, "share_basis": "total_units" if j_sc else None, "doc": doc}


_KIND_TEXT = {"annual_median": "annual median", "ttm": "TTM", "declared_interim": "declared 6-K interim bridge",
              "payable_5y": "payable-earnings base", "declared_pin": "declared base_override pin"}


def ttm_rejection_state(folder, n, j, j_sc=None, interim=None, j_over=None):
    """v5.7 (R7; main() step 3, after interim_pin_state, before L4's check_interim_obligation, every refusal before the
    first write). None on output from before 5.7 (nothing read, nothing checked — D1: older output rebuilds
    unchanged). Else the plan {kind, ttm_published, detail, stale_fy, scope, ttm (ttm_for_run), required, reason,
    bridge_rejected, unavailable_required, unavailable_reason, ttm_unbuildable} after these refusals, in order:
    - ttm_unbuildable (review fix 1; design 11 §3.3 / §14 item 6 — a TTM the worker can rebuild refuses, one the
      worker cannot is recorded): the run sits beside a 'fixable' 10-Q ttm.json for its FY (a withdrawn override, a
      pre-5.7 stamp) that ttm.py can no longer rebuild — ttm.py exits 3 and writes nothing, so the stale file stays —
      and ttm_unavailable_reason quotes the exit-3 line (checked first: ttm_unavailable_problem); the run then has no
      priceable TTM, so nothing is required;
    - required = STALE_FY (R7_OBLIGATION_SCOPE, Q13) ∧ the published base is the annual median or a declared pin (Q18,
      R7_DECLARED_PIN_RULE; the payable pin is exempt) ∧ not TTM-published ∧ a TTM for this run (eligible / fixable)
      ∧ not ttm_unbuildable;
    - ttm_rejection_reason present but not required: R7-5 (the published base is the TTM) or R7-6 (nothing to reject);
    - ttm_unavailable_reason (default Q14) where it may not stand — beside an eligible TTM for this run, a TTM pin, a
      payable or exempt pin, without STALE_FY, at a 20-F / 40-F filer (interim_bridge_declined is R2's record) — or a
      quote that is not ttm.py's exit-3 line for this run (ttm_unavailable_problem, over the record's CSV and judgment);
    - required, absent: R7-1 — except a declared 6-K bridge, which L4's binding refuses (R7-11); beside a fixable
      ttm.json it names the exit-3 way out;
    - required, present: ttm_rejection_problem (R7-2 .. R7-4), then a fixable TTM (R7-7: it cannot be priced — rerun
      ttm.py, or quote its exit-3 line instead);
    - default Q14 (R7_TTM_UNAVAILABLE_RULE "require"): a STALE_FY 10-K run of that kind with no TTM for its latest FY
      (no ttm.json, or one on another FY) without ttm_unavailable_reason [TTM-UNAV0] — skipping ttm.py is checkable.
      Q14 is keyed on STALE_FY itself, never on Q13's scope (review fix 2: each default flips alone).
    bridge_rejected (a declared 6-K bridge kept declared and rejected) is what L4's binding and obligation read."""
    if not is_57_run(n):
        return None
    j = j if isinstance(j, dict) else {}
    t = os.path.basename(os.path.normpath(folder))
    kind, ttm_pub, detail = published_base_kind(t, n)
    stale = _stale_fy(n)
    scope = _r7_scope(stale)
    ttm = ttm_for_run(folder, n, j, j_sc=j_sc, j_over=j_over)
    in_kind = kind == "annual_median" or (kind == "declared_pin" and R7_DECLARED_PIN_RULE == "require")
    for_run = bool(ttm and ttm["status"] in ("eligible", "fixable"))
    reason = j.get(TTM_REJECTION_KEY)
    present = reason is not None
    unavail = j.get(TTM_UNAVAILABLE_KEY)
    foreign = n.get("filer_annual_form") in ("20-F", "40-F")
    no_ttm = ttm is None or ttm["status"] == "other_fy"
    rows = _csv_rows(folder) if unavail is not None else []
    # review fix 1: a fixable 10-Q TTM the rejection obligation would bind (Q13's scope), which ttm.py cannot rebuild
    # — its exit-3 line, quoted and checked, stands for the stale file
    unbuildable = bool(unavail is not None and scope and in_kind and not ttm_pub and not foreign and ttm is not None
                       and ttm["status"] == "fixable" and ttm["kind"] == "ttm")
    if unbuildable:
        prob = ttm_unavailable_problem(unavail, n, t, rows=rows, j=j)
        if prob:
            fail(prob)
    required = bool(scope and in_kind and not ttm_pub and for_run and not unbuildable)
    if present and not required:
        if ttm_pub:
            fail(f"judgment.json ttm_rejection_reason rejects the TTM but the final run's base is ttm.json's (base_source "
                 f"{n.get('base_source')}) — drop the field, or rerun the final pass without --ttm")          # R7-5
        cause = ("the payable-earnings base replaces the OCF base" if kind == "payable_5y"
                 else "declared base_override pins are exempt (default Q18, R7_DECLARED_PIN_RULE)"
                 if kind == "declared_pin" and not in_kind
                 else "STALE_FY does not fire (the median is the default base)" if not scope
                 else "ttm.py cannot rebuild ttm.json's TTM (judgment.json ttm_unavailable_reason quotes its exit-3 "
                      "message) — nothing priceable to reject" if unbuildable
                 else "ttm.json holds no TTM for this run (no ttm.json)" if ttm is None
                 else f"ttm.json holds no TTM for this run ({ttm['note']})")
        fail(f"judgment.json ttm_rejection_reason is declared but {cause} — remove it")                       # R7-6
    # default Q14: a STALE_FY 10-K run of that kind with no TTM for its latest FY (no ttm.json, or one on another FY)
    # quotes ttm.py's exit-3 message — keyed on STALE_FY, Q14's own population, never on Q13's scope (review fix 2);
    # the field is allowed only there, beside a ttm.json off the share-class declaration (L8: ttm.py cannot rebuild
    # it) and beside an unbuildable fixable one (above), and a quote is always checked; a misplaced field is refused
    # before the rejection rules (it says no TTM exists where one does)
    q14 = bool(stale and in_kind and not ttm_pub and not foreign)
    unavail_required = bool(R7_TTM_UNAVAILABLE_RULE == "require" and q14 and no_ttm)
    if unavail is not None and not unbuildable:
        if not (q14 and (no_ttm or ttm["status"] == "off_basis")):
            cause = ("the final run's base is the TTM" if ttm_pub
                     else "the payable-earnings base replaces the OCF base" if kind == "payable_5y"
                     else "declared base_override pins are exempt (default Q18, R7_DECLARED_PIN_RULE)" if not in_kind
                     else f"ttm.json holds a TTM for this run (to {ttm['ytd_end']}) — pin it with --ttm or reject it with "
                          "ttm_rejection_reason" if (scope and ttm is not None and ttm["status"] == "eligible")
                     else "STALE_FY does not fire (the median is the default base)" if not stale
                     else f"{n.get('filer_annual_form')} filers record why no TTM exists in interim_bridge_declined (R2)"
                     if foreign
                     else f"ttm.json holds a TTM for this run (to {ttm['ytd_end']}) — pin it with --ttm or reject it with "
                          "ttm_rejection_reason")
            fail(f"[TTM-UNAV] judgment.json ttm_unavailable_reason is declared but {cause} — remove it")
        prob = (ttm_unavailable_problem(unavail, n, t, rows=rows, j=j)
                if no_ttm or not isinstance(unavail, str) or not unavail.strip() else None)
        if prob:
            fail(prob)
    exit3_way = ("when ttm.py exits 3 instead (it cannot rebuild this TTM), " if ttm is not None
                 and ttm["status"] == "fixable" and ttm["kind"] == "ttm" and not foreign else None)
    if required and not present and ttm["kind"] == "ttm":
        fail(f"[TTM-REJ0] {'STALE_FY fires and ' if stale else ''}ttm.json holds a TTM for this run (to "
             f"{ttm['ytd_end']}: {_money(ttm['base_oe_per_share'])}/share) but the published base is the "
             f"{_KIND_TEXT[kind]} ({_money(n.get('base_oe_per_share'))}/share) — pass --ttm in the final run, or reject "
             "the TTM in judgment.json ttm_rejection_reason: name the distorting cash-flow line with a number "
             "(WORKER_SPEC step 4; Andrew's ruling R7)"
             + (f" — ttm.json cannot be priced as it stands: {ttm['note']}; {exit3_way}quote the line it prints in "
                "judgment.json ttm_unavailable_reason" if exit3_way else ""))                              # R7-1
    if required and present:
        prob = ttm_rejection_problem(reason)
        if prob:
            fail(prob)                                                                                      # R7-2..4
        if ttm["status"] == "fixable":
            fail(f"the TTM this run rejects cannot be priced: {ttm['note']} — R7 records the rejected TTM's base, "
                 "weighted IRR and tier beside the published base"
                 + (f" — {exit3_way}drop ttm_rejection_reason and quote the line it prints in judgment.json "
                    "ttm_unavailable_reason" if exit3_way else ""))                                        # R7-7
    if unavail is None and unavail_required:
        fail(f"[TTM-UNAV0] STALE_FY fires at a 10-K filer and ttm.json holds no TTM for this run's latest FY "
             f"({'no ttm.json' if ttm is None else ttm['note']}) — run python3 _system/ttm.py {t} and pass --ttm in "
             "the final run (or reject the TTM with ttm_rejection_reason); when ttm.py exits 3, quote the message it "
             "prints in judgment.json ttm_unavailable_reason (default Q14)")
    return {"kind": kind, "ttm_published": ttm_pub, "detail": detail, "stale_fy": stale, "scope": scope, "ttm": ttm,
            "required": required, "reason": reason.strip() if (required and present) else None,
            "bridge_rejected": bool(required and present and ttm["kind"] == "declared_interim"),
            "unavailable_required": unavail_required,
            "unavailable_reason": unavail.strip() if isinstance(unavail, str) and unavail.strip() else None,
            "ttm_unbuildable": unbuildable}


def _alt_ttm_ok(ttm, j_sc):
    """v5.7 gate (L8 / R7, 08 §8.9 and M-12; filled when R7 merged onto L8): a ttm.json alternative is priced only
    when it is on the share_classes declaration — share_classes.ttm_on_declaration, the one rule the engine's
    check_ttm_share_basis and make_score's R-6 (check_ttm_on_declaration) apply too: beside a declaration, a block
    whose declaration_sha256 is judgment.json's; with nothing declared, no block. `ttm` is the ttm.json object, `j_sc`
    judgment.json's raw share_classes object (validate_share_classes) or None. A ttm.json off the declaration is
    recorded computed: false (ttm_for_run's off_basis), never priced, and binds no obligation."""
    return bool(_sc.ttm_on_declaration(ttm, j_sc)[0])


def _run_replay(cmd, env_extra=None, timeout=600):
    """(rc, data, first_line) of one R7 engine replay: rc None when the run could not complete (timeout, OS error);
    data the parsed JSON object on rc 0 (None when unparseable); first_line the first non-empty stdout line, else
    stderr's (the engine prints its refusal there: BAD_TTM_SHARES, …). The replay never inherits a counterfactual
    switch from the environment (DCF_NO_OVERRIDES, DCF_IPRD_HOLD, L8's DCF_NO_SHARE_CLASSES / DCF_SC_PIN_SCALE): it
    scores the alternative base exactly as a final run would."""
    env = dict(os.environ)
    for k in ("DCF_NO_OVERRIDES", "DCF_IPRD_HOLD", "DCF_NO_SHARE_CLASSES", "DCF_SC_PIN_SCALE"):
        env.pop(k, None)
    env.update(env_extra or {})
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout,
                             env=env)
    except Exception:
        return None, None, None
    txt = out.stdout or ""
    first = (next((ln.strip() for ln in txt.splitlines() if ln.strip()), None)
             or next((ln.strip() for ln in (out.stderr or "").splitlines() if ln.strip()), None))
    data = None
    if out.returncode == 0:
        i = txt.find("{")
        if i >= 0:
            try:
                data = json.loads(txt[i:])
            except ValueError:
                data = None
    return out.returncode, (data if isinstance(data, dict) else None), first


def _replay_alternative(ticker, n, kind, ttm=None, required=False):
    """One R7 replay of the final configuration on base `kind` (annual_median: no pin; ttm / declared_interim: --ttm),
    field overrides ON, no DCF_IPRD_HOLD — each base takes its own acquired-IPR&D window and share count —, labelled
    DCF_REPLAY_PURPOSE=base_alternatives. Returns the entry's measured fields ({computed: True, measured: True,
    base_oe_per_share, weighted_irr, tier_by_numbers, f_subtype, iprd_charge_per_share, iprd_treatment (+
    ttm_engine_release)}) or {computed: False, measured: True, note} when the engine answered without a base (a data
    gap; an exit 3 / 4 on a base nobody rejected). Refusals: R7-8 the rejected TTM (`required`) exits 3 / 4; R7-9 the
    run failed or answered neither a base nor a gap; R7-10 the base is not the reference (ttm.json's figure / the
    record's median) or ttm.json changed while make_score measured it."""
    ttm_kind = kind in _TTM_KINDS
    cmd = [sys.executable, ENGINE, ticker, "--measure"] + _final_run_args(n) + (["--ttm"] if ttm_kind else [])
    rc, m, first = _run_replay(cmd, {REPLAY_PURPOSE_ENV: "base_alternatives"})
    label = {"annual_median": "annual-median", "ttm": "TTM", "declared_interim": "declared-interim"}[kind]
    if rc in (3, 4):
        if required:
            fail(f"the rejected TTM does not score through the engine: {first or f'exit {rc}'} — fix ttm.json (rerun "
                 f"ttm.py {ticker}{' --interim' if kind == 'declared_interim' else ''}), then make_score")        # R7-8
        return {"computed": False, "measured": True, "note": f"the {label} replay refused: {first or f'exit {rc}'}"}
    if rc != 0 or m is None:
        fail(f"{label} replay failed (exit {rc}) — cannot measure the base alternatives; retry make_score")       # R7-9
    b = _num(m.get("base_oe_per_share"))
    if b is None:
        gaps = [str(g) for g in m.get("data_gap") or []]
        if gaps:
            return {"computed": False, "measured": True, "note": f"the {label} replay gaps: {', '.join(gaps)}"}
        fail(f"{label} replay produced no base and no data gap (exit 0) — cannot measure the base alternatives; retry "
             "make_score")                                                                                         # R7-9
    ref = ttm["base_oe_per_share"] if ttm_kind else _num(n.get("base_oe_normalized_per_share"))
    h = (m.get("ttm_inputs") or {}).get("ttm_input_hash") if isinstance(m.get("ttm_inputs"), dict) else None
    if ref is not None and not _engine.figure_matches(b, ref):
        fail(f"the {kind} replay scored base {b!r}, not {ref!r} — re-run the engine")                             # R7-10
    if ttm_kind and h != ttm["ttm_input_hash"]:
        fail(f"the {kind} replay scored base {b!r} (ttm_input_hash {str(h)[:12]}…), not ttm.json's "
             f"{ttm['ttm_input_hash'][:12]}… — ttm.json changed while make_score measured it")                    # R7-10
    out = _measured_entry(m)
    out.pop("data_gap", None)
    out.update(computed=True, measured=True)
    if ttm_kind:
        out["ttm_engine_release"] = (m.get("ttm_inputs") or {}).get("ttm_engine_release")
    return out


_VAL_KEYS = ("base_oe_per_share", "weighted_irr", "tier_by_numbers", "f_subtype", "iprd_charge_per_share",
             "iprd_treatment")


def _alt_entry(kind, role, pub, computed, measured, vals=None, ttm=None, source=None, replay=None, why="not_chosen",
               why_text=None, note=None):
    """One non-published base_alternatives entry in the one shape (§3.9): the figures (vals), the TTM's identity for
    a TTM kind, its source and replay, the change against the published entry, why and note."""
    vals = vals or {}
    e = {"kind": kind, "role": role, "computed": bool(computed), "measured": bool(measured)}
    for k in _VAL_KEYS:
        e[k] = vals.get(k)
    if kind in _TTM_KINDS:
        t = ttm or {}
        e.update(fy_end=t.get("fy_end"), ytd_end=t.get("ytd_end"), ttm_input_hash=t.get("ttm_input_hash"),
                 ttm_engine_release=vals.get("ttm_engine_release", t.get("ttm_engine_release")),
                 share_basis=t.get("share_basis"))
    e["source"] = source or (TTM_INTERIM_SOURCE if kind == "declared_interim" else TTM_TTM_SOURCE if kind == "ttm"
                             else MEDIAN_SOURCE)
    e["replay"] = replay
    e["base_change_pct"], e["weighted_irr_change_pp"], e["tier_changed"] = _chg(e, pub)
    e.update(why=why, why_text=why_text, note=note)
    return e


def _published_entry(n, plan, why, why_text, tt=None):
    """The published entry: the score's own figures copied from the record (the engine's adjusted ones; tier by
    numbers — L1's notch acts on the published tier only), and the TTM's identity when the published base is a TTM."""
    blk = n.get("iprd_adjustment") if isinstance(n.get("iprd_adjustment"), dict) else {}
    e = {"kind": plan["kind"], "role": "published", "computed": True, "measured": True,
         "base_oe_per_share": _r4(n.get("base_oe_per_share")), "weighted_irr": _r4(n.get("implied_irr_weighted")),
         "tier_by_numbers": n.get("tier_by_numbers"), "f_subtype": n.get("f_subtype"),
         "iprd_charge_per_share": round(_engine.iprd_charge_per_share(n), 4), "iprd_treatment": blk.get("treatment")}
    if plan["kind"] in _TTM_KINDS:
        ti = n.get("ttm_inputs") if isinstance(n.get("ttm_inputs"), dict) else {}
        t = tt or {}
        e.update(fy_end=t.get("fy_end"), ytd_end=t.get("ytd_end"), ttm_input_hash=ti.get("ttm_input_hash"),
                 ttm_engine_release=ti.get("ttm_engine_release"), share_basis=t.get("share_basis"))
    e.update(source=n.get("base_source"), why=why, why_text=why_text, note=None)
    return e


def _unmeasured(base):
    """Entry figures before (or without) a replay: the base from the record, IRR / tier null."""
    return dict({k: None for k in _VAL_KEYS}, base_oe_per_share=_r4(base))


def build_base_alternatives(ticker, folder, n, j, plan, impact=None, payable_impact=None, amortized_impact=None,
                            release_mismatch=False, prior_score=None, j_sc=None, interim_meas=None):
    """v5.7 (R7; main() step 4, after the amortized impact, every replay before the first write): score.json
    base_alternatives — the published base beside every other base computed for the run (annual median, TTM,
    declared-interim TTM: base OE/share, weighted IRR, tier, role, why), ONE record shared with L4's bridge
    measurement. None on output from before 5.7 (plan None) and when no alternative exists (no STALE_FY, no
    ttm.json). The table (§3.6):
    - a published declared 6-K bridge (L4): interim_base_alternatives over interim_meas (its one median replay);
    - annual_median / a declared FY-built pin (Q18) under STALE_FY beside an eligible TTM: the TTM `rejected`, replayed
      with --ttm (1 replay); a declared pin's annual median from the record ("not replayed": its own impact is in the
      base_override event) or, for an iprd_amortized median pin, from amortized_impact;
    - STALE_FY with no TTM for the run (no ttm.json; another FY; off the share-class declaration; an orphan bridge; a
      fixable ttm.json ttm.py cannot rebuild — plan["ttm_unbuildable"]): the TTM entry `computed: false` with why
      (ttm_unavailable_reason recorded on the block, Q14; at a 20-F / 40-F filer the note quotes judgment.json
      interim_bridge_declined, §3.6 row 2);
    - no STALE_FY beside a TTM: the TTM an `alternative` from ttm.json, not replayed;
    - a TTM-published run (--ttm, a basis_window "ttm" pin): under STALE_FY the annual median replayed with no pin (Q15,
      R7_MEDIAN_BESIDE_TTM; 1 replay), else its base from the record, not replayed;
    - the payable pin: the annual median from payable_impact (measured or carried as that block is), no TTM entry.
    Every ttm.json alternative passes _alt_ttm_ok(ttm, j_sc) (L8's ttm_on_declaration, 08 §8.9) or is recorded
    computed: false and never priced. Release mismatch: no replay — carried_base_alternatives."""
    if interim_meas is not None:   # L4: the published bridge's own measurement (never a second replay here)
        _tt = _ttm_record(folder)
        return interim_base_alternatives(n, {"ttm": _tt}, interim_meas) if _alt_ttm_ok(_tt, j_sc) else None
    if plan is None:
        return None
    kind, tt, stale, scope = plan["kind"], plan["ttm"], plan["stale_fy"], plan["scope"]
    foreign = n.get("filer_annual_form") in ("20-F", "40-F")
    entries, jobs = [], []   # jobs: (entry index, base kind, required) — at most one replay per run (§6)

    def queue(entry, base_kind, required=False):
        jobs.append((len(entries), base_kind, required))
        entries.append(entry)
    if kind == "payable_5y":
        pi = payable_impact if isinstance(payable_impact, dict) else {}
        vals = {"base_oe_per_share": _r4(pi.get("base_oe_without_override")),
                "weighted_irr": _r4(pi.get("weighted_irr_without_override")),
                "tier_by_numbers": pi.get("tier_by_numbers_without_override")}
        if vals["base_oe_per_share"] is None:
            vals["base_oe_per_share"] = _r4(n.get("base_oe_normalized_per_share"))
        got = vals["weighted_irr"] is not None or vals["tier_by_numbers"] is not None
        pub = _published_entry(n, plan, "payable_rule", "published — the insurer payable-earnings rule replaces the OCF "
                               "base (base_override payable_earnings_5y)")
        entries.append(_alt_entry("annual_median", "alternative", pub, vals["base_oe_per_share"] is not None, got,
                                  vals=vals, replay="the payable pin's own native-base measurement (payable_pin_impact)",
                                  why_text="not chosen: the payable-earnings rule replaces the OCF base — its own impact "
                                           "is in the base_override event",
                                  note=None if got else (pi.get("note") or pi.get("counterfactual_note")
                                                         or "not measured")))
        return _alt_block(n, plan, pub, entries, 0, carried=bool(pi.get("impact_carried_from_prior_score")),
                          cer=pi.get("counterfactual_engine_release"), note=None)
    if plan["ttm_published"]:
        if kind == "declared_pin":
            pub = _published_entry(n, plan, "declared_pin", "published — a declared base_override pin built on "
                                   "ttm.json's TTM figures (basis_window ttm)")
        elif stale:
            pub = _published_entry(n, plan, "stale_fy_ttm", "published — STALE_FY fires: WORKER_SPEC step 4 scores the "
                                   "TTM base", tt=tt)
        else:
            pub = _published_entry(n, plan, "ttm_pinned", "published — the TTM base pinned with --ttm (STALE_FY does "
                                   "not fire)", tt=tt)
        med = _unmeasured(n.get("base_oe_normalized_per_share"))
        why_text = ("not chosen: STALE_FY fires and the TTM was not rejected (WORKER_SPEC step 4)" if stale
                    else "not chosen: the TTM base is published")
        e = _alt_entry("annual_median", "alternative", pub, med["base_oe_per_share"] is not None, False, vals=med,
                       why_text=why_text)
        if scope and R7_MEDIAN_BESIDE_TTM:
            e["replay"] = REPLAY_MEDIAN
            queue(e, "annual_median")
        else:
            e["note"] = ("not replayed: STALE_FY does not fire" if not scope
                         else "not replayed: R7_MEDIAN_BESIDE_TTM is off (default Q15 switch)")
            entries.append(e)
    else:
        # annual_median, or a declared FY-built pin (an iprd_amortized median pin never sits beside an eligible TTM
        # under STALE_FY: the engine refuses it there, §7.1)
        rejected = bool(plan["required"] and plan["reason"])
        ttm_kind = (tt or {}).get("kind") or ("declared_interim" if foreign else "ttm")
        if rejected:
            why = "bridge_rejected" if ttm_kind == "declared_interim" else "ttm_rejected"
            pub = _published_entry(n, plan, why, "published — the TTM was rejected (judgment.json ttm_rejection_reason; "
                                   "WORKER_SPEC step 4)" if why == "ttm_rejected" else
                                   "published — the declared 6-K interim bridge was rejected (judgment.json "
                                   "ttm_rejection_reason; it stays declared)")
        elif kind == "declared_pin":
            pub = _published_entry(n, plan, "declared_pin", "published — a declared base_override pin (judgment.json "
                                   "base_override)")
        elif stale:
            pub = _published_entry(n, plan, "no_ttm_for_run", "published — STALE_FY fires but no TTM exists for this "
                                   "run's latest FY" + (" that ttm.py can build (judgment.json ttm_unavailable_reason)"
                                                        if plan.get("ttm_unbuildable") else ""))
        else:
            pub = _published_entry(n, plan, "default_median", "published — the median of the last 3 FY is the default "
                                   "base (STALE_FY does not fire)")
        # design 11 §3.6 row 2 (review fix 5): at a 20-F / 40-F filer the not-computed entry quotes judgment.json
        # interim_bridge_declined — worker text, so in curly quotes (07 §1.10; check_quotes never reads inside them)
        declined = validate_interim_declined(j) if foreign else None
        declined_q = quoted(declined["reason"]) if declined else None
        if tt is None:
            if stale:   # (no STALE_FY and no ttm.json: no alternative exists)
                note = "no ttm.json for this run"
                if plan.get("unavailable_reason"):
                    note += " — ttm.py cannot build one (judgment.json ttm_unavailable_reason quotes its exit-3 message)"
                elif declined_q:
                    note += (" — no declared 6-K interim bridge (judgment.json interim_bridge_declined, R2): "
                             + declined_q)
                entries.append(_alt_entry(ttm_kind, "alternative", pub, False, False, why="no_ttm_for_run",
                                          note=note))
        elif tt["status"] in ("other_fy", "off_basis", "orphan_bridge"):
            note = tt["note"] + (" — ttm.py cannot build this run's (judgment.json ttm_unavailable_reason quotes its "
                                 "exit-3 message)" if plan.get("unavailable_reason") else "")
            if declined_q:
                note += "; judgment.json interim_bridge_declined (R2): " + declined_q
            entries.append(_alt_entry(tt["kind"], "alternative", pub, False, False, ttm=tt, why="no_ttm_for_run",
                                      note=note))
        elif plan.get("ttm_unbuildable"):
            # review fix 1: a fixable ttm.json ttm.py can no longer rebuild — recorded, never priced, never refused
            entries.append(_alt_entry(tt["kind"], "alternative", pub, False, False, ttm=tt, why="no_ttm_for_run",
                                      note=tt["note"] + " — ttm.py cannot rebuild it (judgment.json ttm_unavailable_reason "
                                                        "quotes its exit-3 message)"))
        elif rejected:
            queue(_alt_entry(tt["kind"], "rejected", pub, True, False, vals=_unmeasured(tt["base_oe_per_share"]),
                             ttm=tt, replay=REPLAY_TTM, why="rejection_reason"), tt["kind"], required=True)
        else:
            note = ("not replayed: " + tt["note"] if tt["status"] == "fixable"
                    else "not replayed: declared base_override pins are exempt (default Q18 switch)"
                    if kind == "declared_pin" and R7_DECLARED_PIN_RULE != "require"
                    else "not replayed: STALE_FY does not fire — the median is the default base")
            entries.append(_alt_entry(tt["kind"], "alternative", pub, True, False,
                                      vals=_unmeasured(tt["base_oe_per_share"]), ttm=tt, why="not_chosen",
                                      why_text="not chosen: the median of the last 3 FY is the default base", note=note))
        if kind == "declared_pin":
            am = _iprd_amortized_record(n)
            ai = amortized_impact if isinstance(amortized_impact, dict) else None
            if am is not None and ai is not None:
                vals = {"base_oe_per_share": _r4(am.get("native_base_per_share")),
                        "weighted_irr": _r4(ai.get("weighted_irr_without_override")),
                        "tier_by_numbers": ai.get("tier_by_numbers_without_override"),
                        "iprd_charge_per_share": ai.get("iprd_charge_per_share_without_override"),
                        "iprd_treatment": ai.get("iprd_treatment_without_override")}
                got = vals["weighted_irr"] is not None or vals["tier_by_numbers"] is not None
                entries.append(_alt_entry("annual_median", "alternative", pub, vals["base_oe_per_share"] is not None, got,
                                          vals=vals, replay="the iprd_amortized pin's one-time-deduction replay "
                                                            "(iprd_amortized_impact)",
                                          why_text="not chosen: the declared iprd_amortized pin carries the acquired "
                                                   "IPR&D in the base (this is its one-time-deduction path)",
                                          note=None if got else ai.get("counterfactual_note")))
            else:
                med = _unmeasured(n.get("base_oe_normalized_per_share"))
                entries.append(_alt_entry("annual_median", "alternative", pub, med["base_oe_per_share"] is not None,
                                          False, vals=med, why_text="not chosen: the declared base_override pin is "
                                                                    "published",
                                          note="not replayed: the published base is a declared base_override pin — its "
                                               "own impact is in the base_override event"))
    if not entries:
        return None
    assert len(jobs) <= 1, jobs   # at most one engine replay per make_score run (§6)
    replays, carried, cer, note = 0, False, None, None
    if jobs and release_mismatch:
        carried, cer, note = carried_base_alternatives(n, prior_score, plan, pub, entries, jobs)
    elif jobs:
        i, base_kind, required = jobs[0]
        res = _replay_alternative(ticker, n, base_kind, ttm=tt if base_kind in _TTM_KINDS else None, required=required)
        e = entries[i]
        e["computed"], e["measured"] = res["computed"], True
        for k in _VAL_KEYS:
            e[k] = res.get(k) if res["computed"] else None
        if base_kind in _TTM_KINDS:
            e["ttm_engine_release"] = res.get("ttm_engine_release", e.get("ttm_engine_release"))
        e["note"] = res.get("note")
        e["base_change_pct"], e["weighted_irr_change_pp"], e["tier_changed"] = _chg(e, pub)
        replays = 1
    return _alt_block(n, plan, pub, entries, replays, carried=carried, cer=cer, note=note)


def _alt_block(n, plan, pub, entries, replays, carried=False, cer=None, note=None):
    bases = [pub] + entries
    return {"schema": 1, "published": plan["kind"], "stale_fy": bool(plan["stale_fy"]),
            "ttm_rejection_reason": plan["reason"], "ttm_unavailable_reason": plan.get("unavailable_reason"),
            "bases": bases, "replays": replays,
            "measured": all(e["measured"] for e in bases if e["computed"]), "note": note,
            "impact_carried_from_prior_score": bool(carried), "counterfactual_engine_release": cer}


def carried_base_alternatives(n, prior_score, plan, pub, entries, jobs):
    """§3.7 — release mismatch: no replay (another release's capex / SBC basis, the M3 rule). The prior score.json
    base_alternatives entry is carried into the job's entry when the prior record's published kind, base and weighted
    IRR equal this run's (4 dp), it carries no note, and its entry of the same kind and role is the same base — for a
    TTM the same ttm_input_hash as the current ttm.json, for the median the same base at 4 dp, or a median replay
    that scored no base (computed false) — and was measured; the carried entry keeps its note. Otherwise the entry
    keeps its base from the record, IRR / tier null, measured false, and the block carries the not-measured note.
    Returns (carried, counterfactual_engine_release, note); edits the entry in place. The one carry rule: L4's bridge
    measurement (interim_bridge_measurement) carries through it too. The obligation and the validator still applied
    (ttm_rejection_state runs on every 5.7 record)."""
    rel = n.get("engine_release")
    i, base_kind, _req = jobs[0]
    e = entries[i]
    prior = (prior_score or {}).get("base_alternatives") if isinstance(prior_score, dict) else None
    pbases = [b for b in (prior or {}).get("bases") or [] if isinstance(b, dict)] if isinstance(prior, dict) else []
    ppub = next((b for b in pbases if b.get("role") == "published"), None)
    pe = next((b for b in pbases if b.get("kind") == base_kind and b.get("role") == e["role"]), None)
    same = (isinstance(prior, dict) and not prior.get("note") and prior.get("published") == plan["kind"]
            and isinstance(ppub, dict) and ppub.get("base_oe_per_share") == pub["base_oe_per_share"]
            and ppub.get("weighted_irr") == pub["weighted_irr"] and isinstance(pe, dict) and pe.get("measured"))
    if same and base_kind in _TTM_KINDS:
        same = pe.get("ttm_input_hash") == e.get("ttm_input_hash")
    elif same:
        # the median's identity is its base at 4 dp — or, for a prior replay of this same published configuration that
        # scored no base (computed false: the engine refused or gapped the median), the published identity alone: its
        # answer ("not computed — <the engine's line>") is carried with its note (review fix 4)
        same = (pe.get("base_oe_per_share") == e.get("base_oe_per_share")
                or (pe.get("computed") is False and pe.get("base_oe_per_share") is None))
    if same:
        e["computed"], e["measured"] = bool(pe.get("computed")), True
        for k in _VAL_KEYS:
            e[k] = pe.get(k)
        if base_kind in _TTM_KINDS:
            e["ttm_engine_release"] = pe.get("ttm_engine_release")
        e["note"] = pe.get("note")
        e["base_change_pct"], e["weighted_irr_change_pp"], e["tier_changed"] = _chg(e, pub)
        return True, rel, None
    e["measured"] = False
    return False, rel, _not_measured_note(rel)


def ttm_rejection_alert_reasons(base_alts, tier_final):
    """Default Q16 (R7_ALERT_RULE, main agent 2026-10-21): the entry-alert reason when a TTM rejection lifts the
    published tier above the rejected TTM's tier into S / A — the same rule R6 applies to a share-class raise: an S / A
    tier that exists only because the worker set the TTM aside rests on that judgment. Only a replayed rejection counts
    (a rejected TTM the replay could not score has no tier: below any); an unmeasured one does not (a release mismatch
    closes both gates already). [] otherwise."""
    if R7_ALERT_RULE != "suppress_raise" or tier_final not in ("S", "A") or not isinstance(base_alts, dict):
        return []
    out = []
    for e in base_alts.get("bases") or []:
        if not (isinstance(e, dict) and e.get("role") == "rejected" and e.get("measured")):
            continue
        rt = e.get("tier_by_numbers")
        if rt is None or TIER_ORDER.get(tier_final, -1) > TIER_ORDER.get(rt, -1):
            out.append(f"tier rests on a TTM rejection (ttm_rejection_reason): the rejected {_KIND_TEXT[e['kind']]} "
                       f"scores {('Tier ' + rt) if rt else 'no tier'}, the published {_KIND_TEXT[base_alts['published']]} "
                       f"Tier {tier_final}")
    return out


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
    m = None   # v5.7 (L8): the replay record, read for its share_classes.checks_relaxed below
    pin_src = (n.get("inputs") or {}).get("base_pin_source")
    pinned = (n.get("inputs") or {}).get("base_oe_ps_arg") is not None or "ttm" in base_src
    base_used = base_used_label(ticker, n)   # v5.7 (R7): this expression, extracted unchanged (published_base_kind)
    args = _final_run_args(n)
    if base_used == "declared_interim":
        # v5.7 (L4, R2a; rebase amendment 13): a --ttm pin on the declared 6-K interim bridge. ttm.py is never
        # spawned — its 10-Q path would refuse an IFRS filer, and the bridge's legs are declared, not overrides. The
        # pin is held in both worlds: the FY override fields ttm.py --interim zero-filled (ttm.json
        # override_counterfactual: without the override the engine has no FY figure for that field) give the
        # no-override pin; with none, the pin is held constant and field overrides only move the growth blend.
        # The replay holds the final run's IPR&D treatment and charge (DCF_IPRD_HOLD), as every override replay does.
        cf = (_ttm_record(f"{BASE}/{ticker}") or {}).get("override_counterfactual")
        zf = _num(cf.get("base_oe_per_share_zero_fill")) if isinstance(cf, dict) else None
        base_without = zf if zf is not None else base_with
        m = _run_json([sys.executable, ENGINE, ticker, "--measure"] + args
                      + ["--base-oe-ps", repr(float(base_without))],
                      {"DCF_NO_OVERRIDES": "1", "DCF_IPRD_HOLD": _iprd_hold(n)})
        if m is None:
            fail("counterfactual engine --measure run failed — cannot measure override impact on the declared interim "
                 "bridge base")
        if m.get("implied_irr_weighted") is None:
            if unblocks and (m.get("data_gap") or []):
                base_without, irr_without = None, None   # gate fired: honestly no counterfactual
            elif irr_with is None and not (m.get("data_gap") or []):
                irr_without = None                       # Tier F on the pin in both worlds
            else:
                fail("counterfactual run produced no IRR and no data gap — cannot measure override impact on the "
                     "declared interim bridge base")
        else:
            irr_without = m.get("implied_irr_weighted")
    elif base_used in ("payable_5y", "declared_pin"):
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
    out = {"base_used": base_used,
           "base_oe_without_override": round(base_without, 4) if isinstance(base_without, (int, float)) else None,
           "base_oe_with_override": round(base_with, 4) if isinstance(base_with, (int, float)) else None,
           "base_oe_impact_pct": base_pct,
           "weighted_irr_without_override": round(irr_without, 4) if isinstance(irr_without, (int, float)) else None,
           "weighted_irr_with_override": round(irr_with, 4) if isinstance(irr_with, (int, float)) else None,
           "weighted_irr_impact_pp": irr_pp,
           "unblocks_tier": unblocks}
    # v5.7 (L8, 08 §8.3): at a declaring filer the no-override replay leaves a fallback row without units — named
    # beside the no-override base (key absent otherwise, so every undeclared block is unchanged)
    _rel = (((m.get("share_classes") or {}).get("checks_relaxed")) if isinstance(m, dict)
            and isinstance(m.get("share_classes"), dict) else None)
    if isinstance(_rel, dict) and _rel.get("periods_left_on_fallback"):
        out["share_classes_checks_relaxed"] = _rel
    return out


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


def _moat_events(ticker, today, moat_ev, n=None, j=None):
    """v5.7 (L3, R4 revised; 03b §9.4): one registry event per moat gate that applies on a CHECKED (5.7) run, did not
    drift on this rebuild and whose reason is declared — moat_divergence, moat_low_roic, moat_high_return_low_moat,
    moat_erosion_rebuttal. The identity (_EVENT_DECLARATION) is (moat_score, reason); moat_score is a float in every
    event so keep_first_dates never re-dates 6 vs 6.0. No event uses an iprd_deferred_payment field name. Pure (runs
    under the registry lock): [] for legacy output or no moat evidence.
    L3b (M6, 10 §5.6): moat_erosion_rebuttal is also written whenever MOAT_EROSION fired and the rebuttal restored
    the 2-year hold (fade rule eroding_rebutted), and moat_widening_declined when the worker declined a widening whose
    guards pass (rule widening_declined); both carry the measured change, the hold run and the hold without the
    declaration, and the weighted IRR both ways (n: the engine record; the IRR without from fade.counterfactual; j:
    the judgment, whose moat_scorecard.widening_declined is the decline's reason) — never on a rebuild whose fade sync
    drifted, and never for a rebuttal no run has checked (moat_scorecard.rebuttal_unchecked: declared while no erosion
    was measured, met by a rebuild; L3b review, 2026-10-21)."""
    me = moat_ev if isinstance(moat_ev, dict) else None
    if not me or me.get("status") != "checked":
        return []
    g = me.get("gates") or {}
    base = {"ticker": ticker, "date": today, "moat_score": float(me.get("moat_score"))}
    out = []
    fade = me.get("fade") if isinstance(me.get("fade"), dict) else {}
    fade_ok = not any(d.get("gate") == "fade_sync" for d in me.get("gate_drift") or [])
    irr = _num((n or {}).get("implied_irr_weighted"))

    def hold_fields(without):
        cf = next((c for c in fade.get("counterfactual") or [] if c.get("hold_years") == without), {})
        return {"hold_years": fade.get("hold_years"), "hold_without": without,
                "irr_weighted": round(irr, 4) if irr is not None else None, "irr_weighted_without": cf.get("irr_weighted")}

    def due(name):
        rec = g.get(name) or {}
        return bool(rec.get("applies")) and not rec.get("drifted") and isinstance(rec.get("reason"), str) and rec["reason"].strip()
    if due("divergence"):
        out.append(dict(base, event="moat_divergence", evidence_score=me.get("evidence_score"),
                        core_evidence_score=me.get("core_evidence_score"),
                        supporting_adjustment=me.get("supporting_adjustment"), divergence=me.get("divergence"),
                        reason=g["divergence"]["reason"]))
    if due("low_return"):
        lr = g["low_return"]
        out.append(dict(base, event="moat_low_roic", measure=lr.get("measure"), median=lr.get("median"),
                        median_note=lr.get("median_note"), reason=lr["reason"]))
    if due("reverse"):
        rv = g["reverse"]
        out.append(dict(base, event="moat_high_return_low_moat", measure=(me.get("governing") or {}).get("measure"),
                        median=rv.get("median"), median_note=rv.get("median_note"), min=rv.get("min"), reason=rv["reason"]))
    rebutted = fade_ok and fade.get("rule") == "eroding_rebutted"
    # [L3b review, 2026-10-21] a rebuttal no run has checked (declared while unused, met by a rebuild) records nothing,
    # under G6 either: the registry keeps checked declarations only
    if (due("erosion") or rebutted) and not _moat.rebuttal_unchecked(fade):
        er = me.get("erosion_test") or {}
        reason = (g.get("erosion") or {}).get("reason")
        out.append(dict(base, event="moat_erosion_rebuttal", governing_change_pp=er.get("governing_change_pp"),
                        margin_change_pp=er.get("margin_change_pp"), margin_basis=er.get("margin_basis"),
                        **(hold_fields(_engine.HOLD_BY_TREND["eroding"]) if rebutted else {}), reason=reason))
    if fade_ok and fade.get("rule") == "widening_declined":
        sc = (j or {}).get("moat_scorecard") if isinstance(j, dict) else None
        out.append(dict(base, event="moat_widening_declined", governing_change_pp=fade.get("governing_change_pp"),
                        margin_change_pp=fade.get("margin_change_pp"), margin_basis=fade.get("margin_basis"),
                        **hold_fields(_engine.HOLD_BY_TREND["widening"]),
                        reason=(sc or {}).get("widening_declined") if isinstance(sc, dict) else None))
    return out


def moat_facts_by_id(fc, folder):
    """{id: fact} the moat scorecard reads: the facts check's by_id when the facts lane (L2) provides one, else
    facts.json read directly (facts.by_id) — {} when absent or unreadable (a cited id then refuses in the scorecard)."""
    bi = getattr(fc, "by_id", None) if fc is not None else None
    if callable(bi):
        bi = bi()
    if isinstance(bi, dict):
        return bi
    try:
        with open(f"{folder}/facts.json", encoding="utf-8") as f:
            return _facts.by_id(json.load(f))
    except (OSError, ValueError):
        return {}


def influence_extra(moat_ev=None, interim_meas=None, base_alts=None):
    """[Integrate L4] 07 §1.12 step 7: the engine sources every 5.7 influence check traces to beyond check_quotes'
    set — the numeric leaves of the moat evidence (L3: a reason quoting the tangible ROIC traces) and of the declared
    6-K bridge's measurement (L4: the bridged and the annual-median base OE/share, weighted IRR and acquired-IPR&D
    charge per share — a reason quoting the median IRR the bridge was measured against traces), and (R7) of the
    base_alternatives record's bases (base OE/share, weighted IRR, IPR&D charge and the changes against the published
    base: a ttm_rejection_reason quoting the rejected TTM's replayed IRR traces). All are computed before the checks
    and before the first write (steps 4 and 6). [] when none exists."""
    leaves = []
    if isinstance(moat_ev, dict):
        leaves += _moat.numeric_leaves(moat_ev)
    if isinstance(interim_meas, dict):
        leaves += _moat.numeric_leaves({k: interim_meas.get(k) for k in ("bridged", "annual_median")})
    if isinstance(base_alts, dict):
        leaves += _moat.numeric_leaves({"bases": base_alts.get("bases")})
    return leaves


def moat_reason_checks(moat_ev, j, fc, folder, n, run_kind="authoring", interim_meas=None):
    """v5.7 step 7 (L3): the moat reasons that are influence fields (03b §5, §17 (b)) — each of moat_divergence_reason /
    low_roic_reason / high_return_low_moat_reason / erosion_rebuttal whose gate applies, and business_type_reason when a
    REIT declares real_assets — goes through check_influence on an authoring 5.7 run, with the moat evidence's numeric
    leaves as engine sources (a low-ROIC reason quoting the tangible ROIC traces) and, [Integrate L4] 07 §1.12 step 7,
    the declared 6-K bridge measurement's (influence_extra). run_kind: moat_scorecard.run_kind (make_score's
    bookkeeping; moat_evidence never carries it — L3 review R1). Returns the (field, text) pairs checked."""
    me = moat_ev if isinstance(moat_ev, dict) else None
    if not me or me.get("status") != "checked" or run_kind != "authoring":
        return []
    sc = j.get("moat_scorecard") if isinstance(j.get("moat_scorecard"), dict) else {}
    leaves = influence_extra(me, interim_meas)
    fade = me.get("fade") if isinstance(me.get("fade"), dict) else {}
    done = []
    for field in _moat.REASON_FIELDS:
        text = sc.get(field)
        gate = (me.get("gates") or {}).get(_moat.REASON_GATE[field]) or {}
        if field == "erosion_rebuttal" and fade.get("rule") == "eroding_rebutted":
            # L3b (M6, 10 §1.4): with MOAT_EROSION fired the rebuttal restores the 2-year hold, so it is an influence
            # field whenever declared (not only under G6), and anchored: the trend test's own figures, its
            # counterfactual and the record's hold-moved valuation outputs trace but never anchor it
            fade_anchor_check(f"moat_scorecard.{field}", text, me, fc, folder, n)
            done.append((field, text))
            continue
        if gate.get("applies") and isinstance(text, str) and text.strip():
            check_influence(f"moat_scorecard.{field}", text, _facts.parse_refs(text), fc, folder, n, extra=leaves)
            done.append((field, text))
    cg = ((fade.get("guards") or {}).get("commodity_sic") or {})
    if cg.get("exempted_by_reason"):
        # L3b (M6, 10 §1.3 guard 4; 10b OQ10): a business_type_reason that lifts the commodity guard adds value (hold 3),
        # so it takes the same anchored check (its cost-position fact is the anchor)
        fade_anchor_check("moat_scorecard.business_type_reason", sc.get("business_type_reason"), me, fc, folder, n)
        done.append(("business_type_reason", sc.get("business_type_reason")))
    elif (me.get("type_lock") or {}).get("reason_required"):
        text = sc.get("business_type_reason")
        check_influence("moat_scorecard.business_type_reason", text, _facts.parse_refs(text), fc, folder, n, extra=leaves)
        done.append(("business_type_reason", text))
    return done


def fade_anchor_check(field, text, me, fc, folder, n):
    """v5.7 (L3b, M6; 10 §1.4, §(l)): check_influence for a reason that moves the growth hold — an erosion_rebuttal
    (restores hold 2) or a business_type_reason lifting the commodity guard (allows hold 3). Engine sources: moat
    evidence outside the trend block (moat_scorecard.fade_extra_leaves, with the plain-ROIC / ROA anchors of the
    tangible-only / ROE-only erosion case); trace-only: the trend block's figures, the counterfactual and the record's
    hold keys and valuation outputs (moat_scorecard.fade_trace_leaves); require_anchor: at least one number must rest
    on a cited non-third-party fact tagged for the field or an engine figure outside the measurement.
    [L3b review, 2026-10-21] Every figure the hold moves is trace-only, wherever the engine set meets it: the scored
    record's, and those of every saved run the engine set reads (check_quotes.influence_sources counts each verified
    dcf_numbers_<label>.json) — a preliminary run saved at another hold carries the hold-0 IRR."""
    ticker = (n or {}).get("ticker") or os.path.basename(os.path.normpath(folder))
    saved = [rec for label, _, rec in _quotes.saved_runs(folder) if _quotes.bound_saved_run(label, rec, ticker)]
    trace = _moat.fade_trace_leaves(me, n=n, saved=saved)
    check_influence(field, text, _facts.parse_refs(text), fc, folder, n,
                    extra=_moat.fade_extra_leaves(me, trace["values"]), trace_only=trace, require_anchor=True)


SCORE_DECISION_KEYS += ("moat_evidence",)   # L3 (R4 revised): moat_evidence carries a decision (L5's prepare compares it)
SCORE_DECISION_KEYS += ("share_classes", "up_c_check")   # L8 (R6): the declaration's measured block and the waiver


def _interim_events(ticker, interim, declined, today):
    """v5.7 (L4, R2a): the interim_bridge event (identity: the declaration hash, so an unchanged declaration keeps
    its first date) and the interim_bridge_declined event (identity: the reason). v5.7 (R7, 11 §7.2): the bridge
    event carries the declaration's descriptors only — both bases, their weighted IRRs and tiers are the
    base_alternatives event's (_base_alternatives_events: one record, not two shapes). No field carries an
    iprd_deferred_payment name (IPRD_DEFERRED_EVENT_KEYS)."""
    out = []
    if interim is not None:
        decl, tt = interim["decl"], interim["ttm"]
        per = tt.get("periods") or {}
        out.append({"ticker": ticker, "event": INTERIM_KEY, "date": today, "declaration_hash": interim["hash"],
                    "currency": decl.get("currency"), "fy_period": per.get("fy"),
                    "prior_interim_period": per.get("prior_interim"), "current_interim_period": per.get("current_interim"),
                    "report_accession": (decl.get("report") or {}).get("accession"),
                    "estimate_legs": interim.get("estimate_legs") or [],
                    "perimeter_changes": [{k: pc.get(k) for k in ("kind", "effective_date", "resolution")}
                                          for pc in (decl.get("like_for_like") or {}).get("perimeter_changes") or []]})
    if declined is not None:
        out.append({"ticker": ticker, "event": INTERIM_DECLINED_KEY, "date": today, "reason": declined["reason"],
                    "report_accession": (declined.get("report") or {}).get("accession")})
    return out


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
    """v5.7 (L8, R6; 08 §8.6, rebase A-14): the share_classes event — {ticker, event, date, basis, declaration_sha256,
    traded_class, classes [{name, holder, exchange_ratio}], units_by_period {period_end: units} (NEVER `periods`, an
    iprd_deferred_payment field name: registry_entry_problem would read it as one and refuse the whole registry),
    reason, and the measured block of share_classes_impact (both bases: base, weighted IRR, tier, cap, scope)} — and
    the up_c_suspect event {ticker, event, date, reason, s} when the engine flagged UP_C_SUSPECT and judgment.json
    waives it (up_c: that waiver, else derived from n / j). Identities (_EVENT_DECLARATION): (basis,
    declaration_sha256) and (reason): an unchanged declaration keeps its first date, any edit re-dates. Pure."""
    today = datetime.datetime.now(ZoneInfo("America/New_York")).date().isoformat()
    out = []
    rec = _sc_record(n)
    jsc = j.get("share_classes") if isinstance(j, dict) and isinstance(j.get("share_classes"), dict) else None
    if isinstance(share_classes, dict) and rec is not None and jsc is not None:
        norm, _ = _sc.validate(jsc)
        units = _sc.units_by_period(norm) if norm else {}
        ev = {"ticker": ticker, "event": "share_classes", "date": today, "basis": rec.get("basis"),
              "declaration_sha256": rec.get("declaration_sha256"), "traded_class": rec.get("traded_class"),
              "classes": [{k: c.get(k) for k in ("name", "holder", "exchange_ratio")} for c in rec.get("classes") or []],
              "units_by_period": {p: units[p] for p in sorted(units)}, "reason": jsc.get("reason")}
        ev.update({k: v for k, v in share_classes.items()
                   if k not in ev and k not in IPRD_DEFERRED_EVENT_KEYS and k not in ("basis", "declaration_sha256")})
        out.append(ev)
    if up_c is None and isinstance(j, dict) and isinstance(j.get(UP_C_REASON_KEY), str) and j[UP_C_REASON_KEY].strip() \
            and any(str(f).startswith(UP_C_FLAG) for f in (n or {}).get("fragility_flags") or []):
        up_c = {"reason": j[UP_C_REASON_KEY], "s": _r4(((n or {}).get("up_c_check") or {}).get("s"))}
    if isinstance(up_c, dict) and up_c.get("reason"):
        out.append({"ticker": ticker, "event": "up_c_suspect", "date": today, "reason": up_c["reason"], "s": up_c.get("s")})
    return out


def _base_alternatives_events(ticker, base_alts, today):
    """v5.7 (R7, 11 §3.10): one base_alternatives event when the base choice is a judgment call R7 or R2 records — a
    `rejected` entry (the TTM rejection) or a published declared 6-K bridge (04: "recorded in the overrides
    registry"); a mandated TTM base, a fresh-FY median, a no-TTM median and a payable base (its own base_override
    event) write none. {ticker, event, date, chosen, stale_fy, reason, ttm_kind, ttm_fy_end, ttm_ytd_end, bases [{kind,
    role, computed, base_oe_per_share, weighted_irr, tier_by_numbers, note}], measured, note,
    impact_carried_from_prior_score, counterfactual_engine_release}. Identity (_EVENT_DECLARATION): chosen, reason,
    ttm_kind, ttm_fy_end, ttm_ytd_end — an unchanged reason against the same TTM window keeps its first date; a new
    10-Q, a new FY or a rewritten reason re-dates. No field carries an iprd_deferred_payment name. Pure."""
    if not isinstance(base_alts, dict):
        return []
    bases = [b for b in base_alts.get("bases") or [] if isinstance(b, dict)]
    rej = next((b for b in bases if b.get("role") == "rejected"), None)
    if rej is None and base_alts.get("published") != "declared_interim":
        return []
    tb = rej or next((b for b in bases if b.get("role") == "published"), {})
    return [{"ticker": ticker, "event": "base_alternatives", "date": today, "chosen": base_alts.get("published"),
             "stale_fy": bool(base_alts.get("stale_fy")), "reason": base_alts.get("ttm_rejection_reason"),
             "ttm_kind": tb.get("kind"), "ttm_fy_end": tb.get("fy_end"), "ttm_ytd_end": tb.get("ytd_end"),
             "bases": [{k: b.get(k) for k in ("kind", "role", "computed", "base_oe_per_share", "weighted_irr",
                                              "tier_by_numbers", "note")} for b in bases],
             "measured": bool(base_alts.get("measured")), "note": base_alts.get("note"),
             "impact_carried_from_prior_score": bool(base_alts.get("impact_carried_from_prior_score")),
             "counterfactual_engine_release": base_alts.get("counterfactual_engine_release")}]


def _capex_events(ticker, today, unlisted_acks, n):
    """v5.7 (L9, R8): one capex_unlisted_ack event {ticker, event, date, tag, reason, value} per acknowledged
    CAPEX_UNLISTED_COMPONENT tag (unlisted_acks: capex_unlisted_acks(n, j) — the tag, the worker's reason and the
    flag's figure). The ack releases a refusal, so it is a judgment call the registry records; its identity is
    (tag, reason) — an unchanged ack keeps its first date (keep_first_dates). [] when none."""
    return [{"ticker": ticker, "event": "capex_unlisted_ack", "date": today, "tag": a["tag"], "reason": a["reason"],
             "value": a.get("value")} for a in (unlisted_acks or []) if isinstance(a, dict) and a.get("tag")]


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
                if field == "capex" and j_over[field].get("software_included") is not None:
                    ent["software_included"] = j_over[field]["software_included"]   # v5.7 R9 (L9)
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
            for _k in ("share_basis", "share_period"):     # v5.7 (L8, R6; A-8): a total-unit pin's attestation
                if bo.get(_k) is not None:
                    ev[_k] = bo[_k]
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
        entries += _moat_events(ticker, today, moat_ev, n=n, j=j)               # L3 / L3b (R4, M6)
        entries += _interim_events(ticker, interim, declined, today)            # L4 (R2)
        entries += _facts_events(ticker, today, facts_check)                    # L2 (R3)
        entries += _share_classes_events(ticker, share_classes, up_c, n, j)     # L8 (R6)
        entries += _base_alternatives_events(ticker, base_alts, today)          # R7
        entries += _capex_events(ticker, today, unlisted_acks if unlisted_acks is not None   # L9 (R8): derived
                                 else capex_unlisted_acks(n, j), n)             # from the run + judgment by default
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
    share_classes_raise (v5.7, lane L8, R6 — Andrew 2026-10-19/20: "an entry
    alert is suppressed if the declaration RAISES the tier"): the
    share_classes_raise_reason text when the measured filed-class tier is
    below the total-unit tier; appended to the ENTRY reasons of a final S/A
    tier (exits are never suppressed for it — 08b decision 3). None, the
    default, leaves every gate exactly as before."""
    sa = ("S", "A")
    entry, exit_ = [], []
    if share_classes_raise and tier_final in sa:
        entry.append(share_classes_raise)
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
        sw = _software_usd(prov.get(r["period_end"]), intang)   # v5.7 R9: None unless the run read software
        sw_s = f", of which capitalized software {_usd(sw)}" if sw is not None else ""
        split = (f" (PP&E {_usd(ppe)} + intangibles {_usd(intang or 0.0)}{sw_s})" if ppe is not None
                 else (f" ({sw_s[2:]})" if sw_s else ""))
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
        soft = p.get("software") if isinstance(p.get("software"), dict) else {}
        if soft:   # v5.7 R9: the capitalized-software part, per tag, as filed
            note += "; of which capitalized software: " + " + ".join(
                f"{t} {_amount(v, p.get('intangibles_unit'))}" for t, v in soft.items())
        out.append(f"- Capex basis FY{pe[:4]} ({pe}): {p.get('ppe_source') or '—'}: {' + '.join(legs) or '—'}{note}")
    return out


def _software_usd(p, intang_usd):
    """v5.7 R9: the capitalized-software part of a CSV row's capex_intangibles (USD), from capex_provenance[<FY>]
    `p`: capex_intangibles x (software / intangibles) — both provenance maps are in the leg's one filed unit, so the
    ratio is unit-free. None when the provenance names no software (every pre-5.7 record) or a figure is missing."""
    if not isinstance(p, dict) or not isinstance(p.get("software"), dict) or not p["software"]:
        return None
    sw = sum(float(v) for v in p["software"].values() if _num(v) is not None)
    tot = sum(float(v) for v in (p.get("intangibles") or {}).values() if _num(v) is not None) \
        if isinstance(p.get("intangibles"), dict) else 0.0
    if intang_usd is None or not tot:
        return None
    return intang_usd * sw / tot


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
    """v5.7 (L8, R6; A-25): appended to the "Shares diluted (latest)" line on a declared run whose latest FY carries
    units — the count is total economic units (filed traded-class diluted + declared). "" otherwise (undeclared
    records print the line byte for byte as before)."""
    lt = (_sc_record(n) or {}).get("latest") or {}
    if not _num(lt.get("units_equivalent")):
        return ""
    return (f" total economic units (filed traded-class diluted {lt['filed_traded']:,.0f} + declared "
            f"{lt['units_equivalent']:,.0f})")


def _sc_count_word(bases):
    return {"period_end": "period-end counts", "weighted_average": "weighted-average counts"}.get(
        bases[0], "counts") if len(bases) == 1 else "period-end and weighted-average counts"


def _kn_share_classes(n, score):
    """v5.7 (L8, R6; 08 §8.7, A-25): the share-class block in "Base owner's earnings", right after the capex / share /
    SBC basis lines — the declaration (worker text in curly quotes), one line per declared period (filed + declared =
    total, the classes' counts), the TTM's units, the measured impact both ways, the NCI / cap cross-checks, and when
    present the excluded history, zero periods, in_filed_count periods, the field-override replay's fallback rows,
    unused periods, the split rescale and the Up-C check (fired or waived). [] for an undeclared run with no Up-C
    flag. These lines are the sanctioned quote source for the unit counts (never re-declared as facts)."""
    rec = _sc_record(n)
    uc = n.get("up_c_check") if isinstance(n.get("up_c_check"), dict) else None
    flagged = any(str(f).startswith(UP_C_FLAG) for f in n.get("fragility_flags") or [])
    L = []
    if rec is not None:
        L.append(f"- Share classes (declared, {rec.get('basis')}; traded class {quoted(rec.get('traded_class'))}): per-share "
                 "figures divide by the filed traded-class diluted count plus the declared class-equivalent units")
        for a in rec.get("applied") or []:
            cls = " · ".join(f"{quoted(c.get('name'))} {float(c.get('value') or 0):,.0f}"
                             + (f" × {c['exchange_ratio']:g}" if c.get("exchange_ratio") not in (1, 1.0) else "")
                             for c in a.get("classes") or [])
            L.append(f"  - FY{a['period_end'][:4]}: {a['filed_traded']:,.0f} + {a['units_equivalent']:,.0f} = "
                     f"{a['total_units']:,.0f} ({_sc_count_word(a.get('count_bases') or [])}: {cls})")
        t = rec.get("ttm") if isinstance(rec.get("ttm"), dict) else None
        if t and _num(t.get("total_units")):
            L.append(f"  - TTM to {t.get('period_end')}: {t['filed_traded']:,.0f} + {float(t.get('units_equivalent') or 0):,.0f}"
                     f" = {t['total_units']:,.0f} → TTM OE/unit {_money4(t.get('ttm_oe_per_share'))} (filed-class basis "
                     f"{_money4(t.get('ttm_oe_per_share_filed_basis'))})")
        sc = score.get("share_classes") if isinstance(score.get("share_classes"), dict) else {}
        if sc.get("measured") and sc.get("base_oe_filed_basis") is not None:
            def _cap(v):
                return f"${v / 1e9:,.3f}B" if _num(v) else "—"
            sin = {True: "in", False: "out", None: "—"}

            def _sg(v, unit):
                return f" ({v:+.2f}{unit})" if _num(v) is not None else ""
            L.append(f"- Share classes measured impact (filed traded class → total units, same final configuration): base "
                     f"OE/share {_money4(sc.get('base_oe_filed_basis'))} → {_money4(sc.get('base_oe_total_units'))}"
                     f"{_sg(sc.get('base_oe_impact_pct'), '%')} · weighted IRR {_pct(sc.get('weighted_irr_filed_basis'))} → "
                     f"{_pct(sc.get('weighted_irr_total_units'))}{_sg(sc.get('weighted_irr_impact_pp'), 'pp')} · tier "
                     f"{sc.get('tier_filed_basis')} → {sc.get('tier_total_units')} · market cap "
                     f"{_cap(sc.get('market_cap_filed_basis'))} → {_cap(sc.get('market_cap_total_units'))} (scope "
                     f"{sin.get(sc.get('in_scope_filed_basis'))} → {sin.get(sc.get('in_scope_total_units'))})")
        elif sc:
            L.append(f"- Share classes measured impact: not measured — {quoted(sc.get('note'))}")
        nc = rec.get("nci_check") or {}
        lt = rec.get("latest") or {}
        if nc.get("agrees") is not None:
            bits = [x for x in (f"{_pct(nc.get('nci_share_of_equity'))} of equity" if nc.get("nci_share_of_equity") is not None else None,
                                f"{_pct(nc.get('nci_share_of_net_income_3fy'))} of consolidated net income (3 FY)"
                                if nc.get("nci_share_of_net_income_3fy") is not None else None) if x]
            L.append(f"- Share classes cross-check: declared units are {_pct(lt.get('declared_share_of_total'))} of total "
                     f"units at FY{str(lt.get('period_end'))[:4]}; noncontrolling interests hold {' and '.join(bits)} — "
                     + (f"within {nc.get('tolerance_pp')}pp" if nc["agrees"] else
                        f"more than {nc.get('tolerance_pp')}pp apart, explained: "
                        f"{quoted((n.get('share_classes') or {}).get('nci_gap_reason') or _sc_judgment_reason(n, 'nci_gap_reason'))}"))
        if rec.get("series_excluded_periods"):
            shc = (rec.get("growth_inputs_shortened") or {}).get("share_cagr")
            L.append("- History without a declaration (excluded from per-share inputs): "
                     + ", ".join("FY" + p[:4] for p in rec["series_excluded_periods"])
                     + (f" — share CAGR over FY{shc['declared_from'][:4]}–FY{str(lt.get('period_end'))[:4]}" if shc else ""))
        for z in rec.get("zero_periods") or []:
            L.append(f"- Declared 0 (on the filed count): FY{z['period_end'][:4]} — {quoted(z.get('source'))}")
        for i in rec.get("included_periods") or []:
            g = (i.get("exchange_test") or {}).get("gap")
            L.append(f"- Units already in the filed diluted count (in_filed_count, nothing added): FY{i['period_end'][:4]}"
                     + (f" — diluted − basic {g:,.0f} ≥ half of the {i['included_units']:,.0f} units marked"
                        if _num(g) is not None else ""))
        for x in ((rec.get("checks_relaxed") or {}).get("periods_left_on_fallback") or []):
            L.append(f"- Field-override replay: FY{x['period_end'][:4]} left on its fallback count ({x.get('tag')}), no units")
        if rec.get("unused_periods"):
            L.append(f"- Declared but unused this run: {', '.join(rec['unused_periods'])}")
        cc = rec.get("cap_check") or {}
        if cc.get("gap") is True:
            L.append(f"- Share classes cap check: screener cap {cc.get('cap_ratio'):.2f}× the filed-count cap, declared units "
                     f"+{cc.get('declared_uplift') * 100:.0f}% → SHARE_CLASSES_CAP_GAP, explained: "
                     f"{quoted(_sc_judgment_reason(n, 'cap_gap_reason'))}")
        resc = [a for a in rec.get("applied") or [] if a.get("units_split_basis") in ("pre_split_rescaled", "mixed")]
        if resc:
            split = ((n.get("share_basis") or {}).get("split") or {}) if isinstance(n.get("share_basis"), dict) else {}
            L.append(f"- Units rescaled for the split (ratio {split.get('ratio_used')}, event {split.get('event_date')}): "
                     + ", ".join("FY" + a["period_end"][:4] for a in resc))
    oi = score.get("override_impact") if isinstance(score.get("override_impact"), dict) else {}
    for x in ((oi.get("share_classes_checks_relaxed") or {}).get("periods_left_on_fallback") or []):
        L.append(f"- Field-override replay: FY{x['period_end'][:4]} left on its fallback count ({x.get('tag')}), no units")
    if uc and flagged:
        bits = [x for x in (f"NCI share of equity {_pct(uc.get('nci_share_of_equity'))}" if uc.get("nci_share_of_equity") is not None else None,
                            f"of net income (3 FY) {_pct(uc.get('nci_share_of_net_income_3fy'))}"
                            if uc.get("nci_share_of_net_income_3fy") is not None else None) if x]
        ev = ["cover page by class"] if uc.get("cover_by_class") else []
        d2b = uc.get("diluted_to_basic")
        L.append(f"- Up-C check: {' · '.join(bits + ev)} · diluted ÷ basic "
                 f"{f'{d2b:.3f}' if _num(d2b) is not None else '—'} → {UP_C_FLAG} (threshold "
                 f"{_pct(uc.get('threshold'), 0)})"
                 + (f" · waived: {quoted(_sc_judgment_reason(n, UP_C_REASON_KEY, top=True))}"
                    if _sc_judgment_reason(n, UP_C_REASON_KEY, top=True) else ""))
    return L


def _money4(v):
    return "—" if _num(v) is None else f"${v:,.4f}"


def _sc_judgment_reason(n, key, top=False):
    """judgment.json's share_classes.<key> (top: judgment.json's own <key>) for the key_numbers echo."""
    j = _read_judgment(f"{BASE}/{n.get('ticker')}")
    src = j if top else (j.get("share_classes") if isinstance(j.get("share_classes"), dict) else {})
    v = src.get(key)
    return v if isinstance(v, str) and v.strip() else None


def _kn_base_interim(n, score, interim, instance):
    """v5.7 (L4, R2): in "Base owner's earnings", before the payable block — the annual-facts-from-instance line
    (R2b), a bridge's base-source line and the "Interim bridge declined" line (the worker's reason in curly quotes)."""
    out = []
    if isinstance(instance, dict) and instance.get("applied"):
        out.append(f"- Annual facts for FY {', '.join(instance.get('periods_added') or [])}: read from the "
                   f"{instance.get('form')}'s own XBRL instance (accession {instance.get('accession')}, filed "
                   f"{instance.get('filed')}) — EDGAR companyfacts had not ingested them (its latest annual period ended "
                   f"{instance.get('companyfacts_latest_annual_end')}); {instance.get('facts_merged')} facts merged "
                   f"({n.get('ticker')}/annual_instance.json)")
    if interim is not None:
        out.append('- Base source: ttm_json — the declared 6-K interim bridge (see "Interim bridge")')
    d = score.get(INTERIM_DECLINED_KEY)
    if isinstance(d, dict):
        out.append(f"- Interim bridge declined: {quoted(d.get('reason'))} (report "
                   f"{(d.get('report') or {}).get('accession') or 'none'})")
    return out


_KN_ROLE = {"published": "Published", "rejected": "Rejected", "alternative": "Alternative"}


def _kn_alt_label(e):
    """What a base_alternatives entry is, for key_numbers.md."""
    k = e.get("kind")
    fy, ytd = e.get("fy_end"), e.get("ytd_end")
    if k == "annual_median":
        return "annual median of the last 3 FY OE/share"
    if k == "ttm":
        return f"TTM to {ytd} (ttm.py, 10-Q YTD; FY {fy})" if ytd else "TTM"
    if k == "declared_interim":
        return f"declared 6-K interim bridge TTM to {ytd} (ttm.py --interim; FY {fy})" if ytd else "declared 6-K interim bridge TTM"
    if k == "payable_5y":
        return "payable-earnings base (5-yr average operating income available to common)"
    return "declared base_override pin"


def _kn_alt_base(e):
    b = _money(e.get("base_oe_per_share"))
    if e.get("kind") == "annual_median":
        return b
    return f"{b} per economic unit" if e.get("share_basis") == "total_units" else f"{b}/share"


def _kn_base_alternatives(score):
    """v5.7 (R7, 11 §3.11): "Base alternatives" — right after the IPR&D section (each alternative's IRR carries its own
    acquired-IPR&D charge): the published base, then every other base computed for the run (rejected / alternative /
    not computed, with its change against the published base), the rejection reason and ttm.py's exit-3 message in
    curly quotes (worker text, 07 §1.10), how the alternatives were measured and the STALE_FY rule. Tiers are by
    numbers (L1's notch acts on the published tier only). [] when score.json carries no base_alternatives."""
    ba = (score or {}).get("base_alternatives")
    if not isinstance(ba, dict):
        return []
    bases = [b for b in ba.get("bases") or [] if isinstance(b, dict)]
    pub = next((b for b in bases if b.get("role") == "published"), None)
    if pub is None:
        return []
    mn = score.get("misfit_notch") if isinstance(score.get("misfit_notch"), dict) else {}
    L = ["", "## Base alternatives (R7 — the published base beside every other base computed for this run)"]
    fs = f", {pub['f_subtype']}" if pub.get("f_subtype") else ""
    L.append(f"- Published: {_kn_alt_label(pub)} {_kn_alt_base(pub)} — weighted IRR {_pct(pub.get('weighted_irr'))} · "
             f"Tier {pub.get('tier_by_numbers')} (by numbers{fs})"
             + (" (tiers by numbers; the published tier is notched — see Headline)" if mn.get("applies") else ""))
    for e in bases:
        if e is pub:
            continue
        role = _KN_ROLE.get(e.get("role"), "Alternative")
        if not e.get("computed"):
            L.append(f"- {role}: {_kn_alt_label(e)} not computed — {e.get('note') or 'no base'}")
            continue
        if not e.get("measured"):
            L.append(f"- {role}: {_kn_alt_label(e)} {_kn_alt_base(e)} — weighted IRR / tier: "
                     f"{e.get('note') or ba.get('note') or 'not measured'}")
            continue
        pp, pct, tc = e.get("weighted_irr_change_pp"), e.get("base_change_pct"), e.get("tier_changed")
        line = (f"- {role}: {_kn_alt_label(e)} {_kn_alt_base(e)} — weighted IRR {_pct(e.get('weighted_irr'))}"
                + (f" ({pp:+.2f}pp)" if isinstance(pp, (int, float)) else "")
                + f" (Tier {e.get('tier_by_numbers') or '—'}{', ' + e['f_subtype'] if e.get('f_subtype') else ''})"
                + (f" · base {pct:+.2f}% vs published" if isinstance(pct, (int, float)) else "")
                + (f" · tier {pub.get('tier_by_numbers')} → {e.get('tier_by_numbers')}" if tc is True
                   else " · tier unchanged" if tc is False else ""))
        if _num(e.get("iprd_charge_per_share")):
            line += f" · acquired IPR&D {_money(e['iprd_charge_per_share'])}/share off every IV (its own window)"
        if e.get("why_text"):
            line += f" ({e['why_text']})"
        L.append(line)
    if ba.get("ttm_rejection_reason"):
        L.append(f"- Rejection reason: {quoted(ba['ttm_rejection_reason'])}")
    if ba.get("ttm_unavailable_reason"):
        L.append(f"- TTM unavailable (ttm.py's exit-3 message, judgment.json ttm_unavailable_reason): "
                 f"{quoted(ba['ttm_unavailable_reason'])}")
    replayed = next((e for e in bases if e is not pub and e.get("replay") in (REPLAY_TTM, REPLAY_MEDIAN)
                     and e.get("measured")), None)
    if ba.get("impact_carried_from_prior_score"):
        L.append(f"- Measured: carried from the prior score.json, not re-measured (engine output release "
                 f"{ba.get('counterfactual_engine_release')} vs current {ENGINE_RELEASE})")
    elif ba.get("note"):
        L.append(f"- Measured: {ba['note']}")
    elif ba.get("replays") and replayed is not None:
        n_r = ba["replays"]
        L.append(("- Measured: the final configuration replayed with --ttm (field overrides on; the TTM's own "
                  "acquired-IPR&D window and share count; " if replayed.get("kind") in _TTM_KINDS else
                  "- Measured: the final configuration replayed without a base pin (field overrides on; the median's own "
                  "acquired-IPR&D window and share count; ") + f"{n_r} replay{'s' if n_r != 1 else ''})")
    else:
        L.append("- Measured: no replay — the alternatives are recorded from the run's own record"
                 + (" and the payable pin's measurement" if ba.get("published") == "payable_5y" else ""))
    if ba.get("stale_fy"):
        L.append("- STALE_FY fires: the TTM is the scored base unless rejected with a reason that names the distorting "
                 "cash-flow line and a number (WORKER_SPEC step 4)")
    return L


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


HOLD_LINE_TEXT = {"eroding": "moat eroding, not rebutted; default {d}", "stable": "moat stable",
                  "widening": "moat widening, confirmed; default {d}"}


def _kn_moat_line(n, j):
    """v5.7 (L3b, M6): the "Growth & moat" block's `- Moat:` line. A record carrying hold_years (engine 5.7) names the
    growth hold the engine ran — `- Moat: 4/10 · CAP 7.2 yrs · growth hold 0 yrs (moat eroding, not rebutted; default
    2) · terminal growth 2.50%`; every older record prints the pre-5.7 line byte for byte."""
    head = f"- Moat: {j['moat_score']}/10 · CAP {n.get('cap_years')} yrs · "
    h = n.get("hold_years")
    if h is None or isinstance(h, bool):
        return head + f"terminal growth {_pct(n.get('g_terminal'))}"
    t = (n.get("inputs") or {}).get("moat_trend", n.get("moat_trend")) or "stable"
    why = HOLD_LINE_TEXT.get(t, f"moat {t}").format(d=_engine.HOLD_YEARS)
    return head + f"growth hold {h} yrs ({why}) · terminal growth {_pct(n.get('g_terminal'))}"


def _kn_moat(score):
    """v5.7 (L3, R4 revised): the "## Moat scorecard" section from score.json moat_evidence (moat_scorecard.
    key_numbers_lines: every number generated, no worker free text); [] when the score carries none."""
    return _moat.key_numbers_lines((score or {}).get("moat_evidence"))


def _kn_interim(score, interim):
    """v5.7 (L4, R2a): the "Interim bridge" section (07 §1.9: after the Moat scorecard, before Declared facts) — the
    basis and rates, the leg table (local currency and the TTM in USD), the shares line, the bases compared (from
    score.json base_alternatives: since R7 a pointer to its "Base alternatives" section, one shape), what was
    verified and estimated, the like-for-like declaration and one source line per filing leg. Worker text is echoed
    in curly quotes (07 §1.10)."""
    if interim is None:
        return []
    tt, decl = interim["ttm"], interim["decl"]
    per = tt.get("periods") or {}
    rep = tt.get("report") or {}
    ccy = tt.get("currency")
    legs = tt.get("legs") or {}

    def amt(v):
        return f"{v:,.0f}" if _num(v) is not None else "—"
    out = ["", "## Interim bridge (declared 6-K TTM — the scored base)",
           f"- Basis: FY {per.get('fy', ['?', '?'])[0]}..{per.get('fy', ['?', '?'])[1]} − prior interim "
           f"{per.get('prior_interim', ['?', '?'])[0]}..{per.get('prior_interim', ['?', '?'])[1]} + current interim "
           f"{per.get('current_interim', ['?', '?'])[0]}..{per.get('current_interim', ['?', '?'])[1]} "
           f"({rep.get('form')} {rep.get('accession')}, filed {rep.get('filed')}); legs in {ccy}, {_interim_fx_text(tt)}",
           f"| Leg | FY ({ccy}) | − prior interim | + current interim | = TTM ({ccy}) | TTM (USD) |",
           "|---|---|---|---|---|---|"]
    for f in _ib.FLOW_FIELDS:
        lg = legs.get(f) or {}
        est = lambda name: " (est.)" if (lg.get(name) or {}).get("kind") == "estimate" else ""  # noqa: E731
        out.append(f"| {_ib.FIELD_LABELS[f]} | {amt((lg.get('fy') or {}).get('local'))} | "
                   f"{amt((lg.get('prior_interim') or {}).get('local'))}{est('prior_interim')} | "
                   f"{amt((lg.get('current_interim') or {}).get('local'))}{est('current_interim')} | "
                   f"{amt(lg.get('ttm_local'))} | {_usd_exact(lg.get('ttm_usd'))} |")
    out.append(f"| Owner's earnings | | | | {amt(tt.get('ttm_oe_total_local'))} | {_usd_exact(tt.get('ttm_oe_total'))} |")
    sh = (tt.get("shares") or {}).get("current_interim") or {}
    out.append(f"- Shares (current-interim weighted average diluted): {amt(sh.get('value'))} × ADS ratio "
               f"{tt.get('ads_ratio')} → bridged base OE/share "
               + (f"${tt['ttm_oe_per_share']:,.4f}" if _num(tt.get("ttm_oe_per_share")) is not None else "—")
               + " (scored)")
    # v5.7 (R7, 11 §3.11 / §7.2): the both-bases comparison lives in one key_numbers section, "Base alternatives"
    if isinstance(score.get("base_alternatives"), dict):
        out.append('- Bases compared: see "Base alternatives"')
    ver = [f"{a} {b.split('_')[0]}" for a, b in (x.split(".", 1) for x in interim.get("xbrl_verified_legs") or [])]
    est_txt = []
    for x in interim.get("estimate_legs") or []:
        f, name = x.split(".")
        lx = _ib.leg(decl, f, name) or {}
        m = lx.get("method")
        detail = ""
        if m == "fy_prorated":
            fyl = ((legs.get(f) or {}).get("fy") or {}).get("local")
            p = per.get(name) or ["?", "?"]
            try:
                detail = f": FY {amt(fyl)} × {_ib.days(*p)}/{_ib.days(*per['fy'])}"
            except (TypeError, ValueError, KeyError):
                detail = ""
        est_txt.append(f"{f} {name.split('_')[0]} ({m}{detail})")
    out.append("- Verified against the 6-K's XBRL instance: " + (", ".join(ver) or "none")
               + " · estimates: " + ("; ".join(est_txt) or "none")
               + (f" · unverified (method other): {', '.join(interim.get('unverified_legs'))}"
                  if interim.get("unverified_legs") else ""))
    lfl = decl.get("like_for_like") or {}
    parts = [f"comparative restated: {'yes' if lfl.get('comparative_restated') else 'no'}"
             + (f" ({quoted(lfl.get('comparative_note'))})" if lfl.get("comparative_note") else "")]
    for pc in lfl.get("perimeter_changes") or []:
        how = (f"immaterial; {pc.get('revenue_share') * 100:.1f}% of revenue" if pc.get("resolution") == "immaterial"
               and _num(pc.get("revenue_share")) is not None
               else f"{'material' if pc.get('material') else 'not material'}; {pc.get('resolution')}: "
                    f"{quoted(pc.get('reason'))}")
        parts.append(f"{pc.get('kind')} {pc.get('effective_date')} ({how})")
    out.append("- Like-for-like: " + " · ".join(parts))
    out.append(f"- Acquired IPR&D in the current interim: {tt.get('iprd_interim_scan')}")
    for p in tt.get("provenance") or []:
        out.append(f"- Source — {p.get('field')} {str(p.get('leg')).split('_')[0]}: {rep.get('form')} {p.get('accession')} "
                   f"{p.get('document')}, {p.get('section') or ('page ' + str(p.get('page')))} — {quoted(p.get('snippet'))} "
                   f"(verified: {p.get('verified')})")
    return out


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
          _kn_moat_line(n, j)]                                      # L3b (M6): the growth hold on 5.7 records
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
    flags = score.get("fragility_flags") or []   # v5.7 (L4): score.json's list (the engine's + TTM_DECLARED_INTERIM)
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
                         "declared_pin": "declared base_override pin (held constant in both worlds)",
                         "declared_interim": "declared 6-K interim bridge (field overrides toggled off; FY override "
                                             "fields zero-filled)"}.get(
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
    declined = validate_interim_declined(j)                    # L4: judgment.json interim_bridge_declined
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
             "cap_years": n.get("cap_years"),
             # v5.7 (L3b, M6): the growth hold the engine ran, copied when the record carries it (5.7); never on older
             **({"moat_trend": n.get("moat_trend"), "hold_years": n["hold_years"]} if n.get("hold_years") is not None else {}),
             "fragility_flags": n.get("fragility_flags", []),
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
    # (L3, R4 revised: the moat scorecard; a refusal here writes nothing — the registry is the first write)
    moat_sic = (n.get("sector_model") or {}).get("sic") if isinstance(n.get("sector_model"), dict) else None
    moat_sic = moat_sic or _engine.folder_sic(BASE, ticker)[0]
    moat_prior = prior_score if isinstance(prior_score, dict) else None
    try:
        moat_ev = _moat.evaluate(folder, n, j, facts=moat_facts_by_id(fc, folder), is_57=is_57_run(n), sic=moat_sic,
                                 industry=_moat.load_industry(SYS_DIR), prior=moat_prior)
    except _moat.MoatRefusal as e:
        fail(str(e))
    print(f"make_score.py: {_moat.industry_file_line(moat_ev)}")   # non-blocking: a stale file is information
    # (L3, step 7's moat half, run here before the first write: the four moat reasons + a REIT's type reason go through
    # check_influence on an authoring 5.7 run; a rebuild of the same run, declaration and facts skips them)
    moat_reason_checks(moat_ev, j, fc, folder, n, run_kind=_moat.run_kind(folder, n, j, is_57_run(n), moat_prior),
                       interim_meas=interim_meas)
    # v5.7 step 7: every influence check together, on 5.7 runs only and before the first write — each lane calls
    # check_influence (L2) for its own reason fields here (tier_override_reason, base_override, misfit_notch_reason,
    # the moat reasons, the share-class reasons, ttm_rejection_reason). [Integrate L4] 07 §1.12 step 7: the engine
    # sources are L2's set plus the numeric leaves of moat_ev (L3) and of the interim measurement (L4).
    if is_57_run(n):
        trace_extra = influence_extra(moat_ev, interim_meas)
        if notch and notch.get("reason_source") == "judgment":   # L1 (R1): misfit_notch_reason (R-3 / R-4 ran above)
            check_influence("misfit_notch_reason", notch["reason"], _facts.parse_refs(notch["reason"]), fc, folder, n,
                            extra=trace_extra)
        if plan and plan.get("reason"):
            # R7 (11 §3.8): every figure of the rejection traces — to an engine source (dcf_numbers.json, ttm.json, the
            # CSV, saved runs) or the base_alternatives record's leaves (the replayed IRR of the rejected TTM; for this
            # field only: the record's published entry repeats a pin, which must never anchor a base_override reason) or
            # a cited fact listing used_for ttm_rejection; never third-party facts alone
            check_influence(TTM_REJECTION_KEY, plan["reason"], _facts.parse_refs(plan["reason"]), fc, folder, n,
                            extra=trace_extra + influence_extra(base_alts=base_alts))
        # R7 lane (the main agent's decision, 2026-10-21): L9's capex_unlisted_ack reasons (R8) are 5.7 reasons like
        # every other one — each traces through L2's check (used_for capex_unlisted_ack; never third-party alone)
        for _ack in capex_unlisted_acks(n, j):
            check_influence(f"capex_unlisted_ack.{_ack['tag']}", _ack["reason"], _facts.parse_refs(_ack["reason"]), fc,
                            folder, n, extra=trace_extra)
        # L2 (R3, Andrew 2026-10-19; 02 §5): the tier override's reason and a plain base_override pin's reason +
        # source (the payable and iprd_amortized shapes are checked figure for figure elsewhere; rebase I13) — a hand
        # pin never traces to itself alone (base_pin_trace_only, review r05). misfit_notch_reason is L1's call (its
        # field, INFLUENCE_TAGS), made above.
        if override and (IPRD_HAND_OVERRIDE_TRACED or not iprd_override_required(n)):   # Q2 switch
            check_influence("tier_override_reason", j.get("tier_override_reason"),
                            _facts.parse_refs(j.get("tier_override_reason")), fc, folder, n, extra=trace_extra)
        if (base_override_event_applies(j, n) and j_base_override
                and j_base_override.get("basis") not in (PAYABLE_BASIS, IPRD_AMORTIZED_BASIS)):
            _bo_text = " ".join(str(j_base_override.get(k) or "") for k in ("reason", "source"))
            check_influence("base_override", _bo_text, _facts.parse_refs(_bo_text), fc, folder, n, extra=trace_extra,
                            trace_only=base_pin_trace_only(n, j_base_override), require_anchor=True)
        share_classes_reason_checks(j, fc, folder, n, extra=trace_extra)   # L8 (R6, R-9): the share-class reasons
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
    reasons += ttm_rejection_alert_reasons(base_alts, tier_final)   # v5.7 (R7, default Q16)
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
