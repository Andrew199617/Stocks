#!/usr/bin/env python3
"""score.json builder (v5, 2026-10-13 — zero hand transcription of numbers).

Usage: python3 make_score.py <TICKER>

Builds score.json purely from dcf_numbers.json plus judgment.json in the
company folder. Judgment fields (written by the analyzing agent):
  name, sector, moat_score, moat_justification, moat_for, moat_against
  (optional lists of short pillar strings), probs_used (5 numbers, the
  probabilities passed to the engine), one_liner, confidence,
  tier_override + tier_override_reason, in_scope_under_40b.
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
- score.json `iprd_adjustment` (only when dcf_numbers.json carries the block —
  output from an older release, or a 5.6 run with no IPR&D expense filed,
  gets no key): treatment, total, charge_per_share, shares_denominator /
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
  native → pinned base from the run's own record. [v5.6 review] Figures are
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
  apply (or listed in `deferred_payments_unused` because its period left the
  window: drop it), an applied one judgment.json dropped or now declares
  differently, are refused. score.json `iprd_adjustment` carries
  `recurrence_excluded` (when the run had declarations) and each period's
  `deferred_payment_of` / `recurrence_excluded`; key_numbers.md says on the
  period line whether it is excluded from the recurrence count or, partly
  deferred, still counts, plus one "Excluded from the recurrence count" line,
  naming each first charge by its date. The deduction is unchanged. Not a
  registry event, like iprd_cash_flow_check: it records what the filing shows.
"""
import json, sys, os, re, datetime, subprocess, hashlib, csv
# Every file is read and written as UTF-8 (most judgment.json files carry raw
# UTF-8 text; Windows Python otherwise defaults to cp1252 and mangles it).
from zoneinfo import ZoneInfo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _lock import locked  # v5.4: cross-platform exclusive file lock (fcntl / msvcrt)
import dcf_engine as _engine  # v5.5: the release stamp and the market-cap formula (no I/O at import)
from dcf_engine import ENGINE_RELEASE

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
    if score.get("tier_final") and score.get("tier_by_numbers") and score["tier_final"] != score["tier_by_numbers"]:
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
    written; None when absent or the registry is unreadable."""
    try:
        with open(REGISTRY, encoding="utf-8") as f:
            reg = json.load(f)
    except (OSError, ValueError):
        return None
    for e in (reg.get("entries") or []) if isinstance(reg, dict) else []:
        if isinstance(e, dict) and e.get("ticker") == ticker and e.get("event") == "base_override":
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
             f"presentation: one of {sorted(_engine.IPRD_CF_PRESENTATIONS)}, source: the filing and the cash-flow line}}")
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


def check_iprd_cash_flow(n, entries):
    """[fixer review round] The cash-flow checks and the engine record must
    agree, and no expense-basis period may still await one: the run's value
    is unknown until the worker declares what the 10-K's cash-flow statement
    shows (WORKER_SPEC step 3, ACQUIRED_IPRD_UNCONFIRMED)."""
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
    by = {(e["period"], e["window"]): e for e in entries or []}
    for p in periods:
        k = (p.get("period"), p.get("window"))
        applied = p.get("cash_flow_check") if isinstance(p.get("cash_flow_check"), dict) else None
        d = by.get(k)
        if applied is not None:
            if (d is None or d.get("presentation") != applied.get("presentation")
                    or not isinstance(applied.get("amount"), (int, float)) or abs(float(d["amount"]) - float(applied["amount"])) > 1.0
                    or str(d.get("source")) != str(applied.get("source"))):
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
    unused = {(e.get("period"), e.get("window"), _engine._deal_key((e.get("deferred_payment_of") or {}).get("deal")))
              for e in (blk or {}).get("deferred_payments_unused") or [] if isinstance(e, dict)}
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
    for k, d in by.items():
        if k in unused:
            fail(f"judgment.json {IPRD_DEFERRED_KEY} declares {lbl(k)} a deferred payment of "
                 f"{d['deferred_payment_of']['deal']!r}, but that period has left the engine's window "
                 f"({', '.join(((blk or {}).get('window') or {}).get('fy') or [])}): it no longer feeds the recurrence "
                 "count — drop it from judgment.json and rerun the engine")
        if k not in applied:
            fail(f"judgment.json {IPRD_DEFERRED_KEY} declares {lbl(k)} a deferred payment of "
                 f"{d['deferred_payment_of']['deal']!r} but the engine run did not apply it — judgment.json changed "
                 "after the run; rerun the engine (it refuses a declaration its window does not support: "
                 "BAD_IPRD_DEFERRED_PAYMENT)")


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
    if not (tv and nb is not None and abs(nb - tv) <= 0.001 * abs(tv) and ts is not None and sh is not None
            and abs(ts - sh) < 1.0):
        fail(f"the {IPRD_AMORTIZED_BASIS} base_override's native base is ttm.json's TTM base (record: "
             f"{nb} per share on {sh} shares) but ttm.json now holds ttm_oe_per_share {tv} on ttm_shares_diluted {ts} — "
             "ttm.json changed after the engine run; rerun ttm.py and the engine, then rebuild the declaration from the "
             "new run (WORKER_SPEC step 8)")


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


def check_iprd_share_count_unverified(n, j):
    """[Codex review r1 of PR #47] Treatment not_applied_share_count_unverified (a share-scale defect rescued by a
    pin with no power-of-ten factor): the engine found a positive acquired-IPR&D total but no verified share count to
    put it on, so it deducted nothing and the tier is the UNADJUSTED one. WORKER_SPEC step 4 / AGENTS check 8: the
    worker blocks NEEDS_MAIN_AGENT: shares, and only a main-agent tier_override whose reason quantifies the hand
    deduction publishes it. make_score refuses the score unless judgment.json sets tier_override with a reason that
    names a dollar figure and a percentage (the charge per share on the verified count and the adjusted weighted
    IRR); whether the figures are right is the review's to check."""
    blk = n.get("iprd_adjustment") if isinstance(n.get("iprd_adjustment"), dict) else None
    if not blk or blk.get("treatment") != "not_applied_share_count_unverified":
        return
    total = _num(blk.get("total"))
    if not total or total <= 0:
        return
    why = str(j.get("tier_override_reason") or "")
    if j.get("tier_override") and re.search(r"\$\s?\d", why) and re.search(r"\d\s?%", why):
        return
    fail(f"NEEDS_MAIN_AGENT: shares — ACQUIRED_IPRD_CHARGE not deducted: {_usd_exact(total)} (iprd_adjustment "
         "treatment not_applied_share_count_unverified: the share count behind the base is unverified, so the "
         "engine's tier is the UNADJUSTED one). Block the folder NEEDS_MAIN_AGENT; only the main agent publishes it, "
         "through judgment.json tier_override whose tier_override_reason quantifies the hand deduction — the charge "
         "per share on the verified share count ($) and the adjusted weighted IRR (%) (WORKER_SPEC step 4)"
         + ("; the tier_override_reason given names no dollar figure and percentage" if j.get("tier_override") else ""))


def iprd_score_block(n):
    """score.json iprd_adjustment from the engine's block (None when the run
    has none: older-release output, or no acquired-IPR&D expense filed)."""
    b = n.get("iprd_adjustment")
    if not isinstance(b, dict):
        return None
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


def iprd_lines(n):
    """key_numbers.md's acquired-IPR&D section ([] when the run has no block)."""
    b = n.get("iprd_adjustment")
    if not isinstance(b, dict):
        return []
    L = ["", "## Acquired IPR&D adjustment (engine 5.6 — Andrew, 2026-10-19)"]
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
                 + dpo_txt
                 + ("; deal and consideration: not identified by the engine — name them in analysis.md" if p.get("deducted") else ""))
    mat = b.get("materiality")
    tail = "" if one_time else f" (treatment {t}: no one-time deduction)"
    L.append(f"- Total charge: {_usd_exact(b.get('total'))} ÷ {b['shares_denominator']:,.0f} shares ({b.get('shares_source')})"
             f" = {_money(b.get('charge_per_share'))}/share{tail}" if b.get("shares_denominator")
             else f"- Total charge: {_usd_exact(b.get('total'))} (no share denominator: not deducted)")
    L.append(f"- Treatment: {t}" + (f" · {mat * 100:.2f}% of the base OE total" if isinstance(mat, (int, float)) else "")
             + (" · material (ACQUIRED_IPRD_CHARGE)" if b.get("material")
                else (" · below the 5% flag threshold (deducted, no flag)" if one_time else " · below the 5% flag threshold (no flag)")
                if b.get("total") else "")
             + (" · recurrent (ACQUIRED_IPRD_RECURRENT)" if b.get("recurrent") else ""))
    rx = b.get("recurrence_excluded") if isinstance(b.get("recurrence_excluded"), list) else []
    if rx:
        L.append("- Excluded from the recurrence count (judgment.json iprd_deferred_payment — a deferred payment of a deal "
                 "first charged earlier; still deducted): " + "; ".join(
                     f"FY{str(x.get('period'))[:4]} {_usd_exact(x.get('amount'))} — {x.get('deal')}, first charged "
                     f"{x.get('first_charged_period')}" for x in rx))
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
        L.append(f"- Amortized in the base (iprd_amortized base_override): native base {_money(am.get('native_base_per_share'))} "
                 f"({am.get('native_base')}) − mean annual charge {_usd_exact(am.get('mean_annual_charge'))} ÷ "
                 f"{(am.get('shares') or 0):,.0f} shares = pinned base {_money(am.get('pinned_per_share'))}; no one-time deduction")
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
    if not (pinned and tv and b is not None and abs(b - tv) <= 0.001 * abs(tv)):
        return {}
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


def _declared_pin_not_ttm(ticker, n):
    """[v5.5] True when the final run's --base-oe-ps pin equals a declared
    base_override without `basis`, or (v5.6) of basis iprd_amortized on the
    median native base (within 0.1%), and does NOT equal ttm.json's
    ttm_oe_per_share (within 0.1%): a pin built from engine outputs (NTNX /
    TEM / VIV), whose override impact is measured with the pin held constant,
    not by re-running ttm.py. An iprd_amortized pin on native_base ttm_json is
    measured on the TTM branch instead (False)."""
    inp = n.get("inputs") or {}
    pin = inp.get("base_oe_ps_arg")
    if inp.get("base_pin_source") != "base_oe_ps_arg" or not isinstance(pin, (int, float)) or isinstance(pin, bool) or pin == 0:
        return False
    try:
        with open(f"{BASE}/{ticker}/judgment.json", encoding="utf-8") as f:
            bo = (json.load(f) or {}).get("base_override")
    except Exception:
        return False
    if (not isinstance(bo, dict) or bo.get("basis") not in (None, IPRD_AMORTIZED_BASIS) or not isinstance(bo.get("value"), (int, float))
            or isinstance(bo.get("value"), bool) or abs(float(bo["value"]) - pin) > 0.001 * abs(pin)):
        return False
    if bo.get("basis") == IPRD_AMORTIZED_BASIS and _iprd_amortized_ttm(n) is not None:
        return False    # [v5.6 review] ttm.json's TTM base less the amortization: measured on the TTM branch
    try:
        with open(f"{BASE}/{ticker}/ttm.json", encoding="utf-8") as f:
            tv = json.load(f).get("ttm_oe_per_share")
        if isinstance(tv, (int, float)) and not isinstance(tv, bool) and tv != 0 and abs(tv - pin) <= 0.001 * abs(tv):
            return False
    except Exception:
        pass
    return True


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
_FIELD_DECLARATION = ("value", "kind", "source", "reason", "currency", "scope")
_EVENT_DECLARATION = {"tier_override": ("tier_by_numbers", "tier_final", "reason"),
                      "manual_price": ("value",),
                      "base_override": ("value", "kind", "source", "reason", "basis", "figures", "shares", "native_base"),
                      "gterm": ("value",), "cik": ("value",), "ads_ratio": ("ratio", "source", "reason"),
                      "scope_correction": ("old_cap", "new_cap", "in_scope")}


def _declaration(e, ignore=()):
    if e.get("field"):
        keys, head = _FIELD_DECLARATION, ("field", e.get("field"))
    else:
        keys, head = _EVENT_DECLARATION.get(e.get("event"), ()), ("event", e.get("event"))
    return head + tuple(json.dumps(e.get(k), sort_keys=True, default=str) for k in keys if k not in ignore)


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
            if e.get("event") == "base_override" and "kind" not in e:
                lk = _declaration(e, ignore=("kind",))
                legacy[lk] = min(legacy.get(lk, d), d)
    for e in new_entries:
        d = first.get(_declaration(e))
        if d is None and e.get("event") == "base_override":
            d = legacy.get(_declaration(e, ignore=("kind",)))
        if d and (not isinstance(e.get("date"), str) or d < e["date"]):
            e["date"] = d


def update_registry(ticker, applied, j_over, impact, j, n, scope_event=None, payable_impact=None):
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
    the date it was first recorded (keep_first_dates). make_score.py is the
    single writer; the write is atomic under an fcntl lock."""
    today = datetime.datetime.now(ZoneInfo("America/New_York")).date().isoformat()
    with locked(REGISTRY + ".lock"):
        try:
            reg = json.load(open(REGISTRY, encoding="utf-8"))
        except Exception:
            reg = {"entries": []}
        prior = [e for e in reg.get("entries", []) if e.get("ticker") == ticker]
        entries = [e for e in reg.get("entries", []) if e.get("ticker") != ticker]
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
        if j.get("tier_override"):
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
            if pin_rescued(n) and not n.get("payable_base"):
                ev.update(pin_rescue_impact(n))
            _am = (n.get("iprd_adjustment") or {}).get("amortized") if isinstance(n.get("iprd_adjustment"), dict) else None
            if bo.get("basis") == IPRD_AMORTIZED_BASIS and isinstance(_am, dict):
                # v5.6: the amortized acquired-IPR&D base — the declaration and the native -> pinned base from the
                # run's own record (the IRR without it is the one-time path's, not replayed here)
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
        keep_first_dates(entries[n_kept:], prior)
        reg["entries"] = entries
        tmp = REGISTRY + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(reg, f, indent=1)
        os.replace(tmp, REGISTRY)


def alert_reasons(tier_final, tier_by_numbers, override, conf, model_fit, unblocks, irr_at_floor, stale_release=None):
    """(entry_reasons, exit_reasons): why an alert for this score is
    suppressed. Entry reasons apply only to a final S/A tier (alert_eligible),
    exit reasons only to a final tier below A (exit_alert_eligible); both are
    empty when the score clears its gate. stale_release (v5.5): the
    release_mismatch_reason() text when the engine output is not from the
    current ENGINE_RELEASE — it closes BOTH gates ("... — re-run the engine
    before an entry / exit alert"); None leaves every gate as in 5.4."""
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


def write_key_numbers(folder, n, j, score, applied, impact=None, ads_corr=None):
    """key_numbers.md — every headline figure from the final dcf_numbers.json.
    The single source workers quote in analysis.md. ads_corr (v5.5): the
    pre-5.5 ADS market-cap correction, printed with its label instead of the
    engine's uncorrected cap (the net-debt line follows its own rule, M1)."""
    L = [f"# {n['ticker']} — key numbers",
         f"Generated by make_score.py from dcf_numbers.json (engine v{n.get('engine_version')}, as of {n.get('as_of')}).",
         "Quote these figures verbatim in analysis.md — never recompute or retype a derived figure.",
         "",
         "## Headline"]
    if n.get("price") is not None:
        L.append(f"- Price: ${n['price']:,.2f} (source: {n.get('price_source')})")
    tier_note = score["tier_final"]
    if score.get("tier_override_reason"):
        tier_note += f" (agent override of {n['tier_by_numbers']}: {score['tier_override_reason']})"
    conf_note = score["confidence"]
    if score.get("confidence_capped"):
        conf_note += " (capped from high by make_score: WIDE_SCENARIO_SPREAD present)"
    L.append(f"- Tier: {tier_note} · confidence {conf_note}")
    if n.get("implied_irr_weighted") is not None:
        w = n.get("weighted") or {}
        L.append(f"- Weighted IRR: {_pct(n['implied_irr_weighted'])} · base-case IRR: {_pct(n.get('implied_irr_base'))}")
        L.append(f"- Weighted IV: @15% {_money(w.get('iv_at_15'))} · @12% {_money(w.get('iv_at_12'))} · @10% {_money(w.get('iv_at_10'))}")
        L.append(f"- Upside vs price: @15% {_pct(n.get('upside_at_15'), 1)} · @12% {_pct(n.get('upside_at_12'), 1)}")
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
          f"- Base OE/share: {_money(n.get('base_oe_per_share'))} (source: {n.get('base_source')})",
          f"- Latest FY OE/share: {_money(n.get('base_oe_latest_per_share'))} · normalized (3-yr median) OE/share: {_money(n.get('base_oe_normalized_per_share'))}",
          f"- Latest FY OE total: {_usd(n.get('base_oe_total_latest_fy'))}",
          f"- Shares diluted (latest): {n.get('shares_diluted_latest'):,.0f}" if n.get("shares_diluted_latest") else "- Shares diluted (latest): —",
          f"{cap_line} · net debt (latest): {_usd(n.get('net_debt_latest'))}"]
    if scope_line:
        L.append(scope_line)
    L.append(f"- OE-positive years (last 5): {n.get('oe_positive_years_of_last_5')}")
    L += capex_basis_lines(folder, n) + share_basis_lines(n) + sbc_reconciled_lines(n)
    pb = n.get("payable_base")
    if pb:
        figs = pb.get("figures") or []
        L += ["", "## Payable-earnings base (insurer rule, 2026-10-19)",
              "- Operating income available to common, last 5 FY (oldest first, exact): " + " / ".join(f"${x:,.0f}" for x in figs),
              f"- Average: ${pb.get('average'):,.1f} · shares diluted (latest): {pb.get('shares'):,.0f}" if pb.get("shares") else f"- Average: {_usd(pb.get('average'))}",
              f"- Per ordinary share: {_money(pb.get('per_ordinary_share'))} × ADS ratio {pb.get('ads_ratio')} = pinned base {_money(pb.get('pinned_per_share'))}",
              f"- Source: {(j.get('base_override') or {}).get('source')}"]
    L += iprd_lines(n)   # v5.6: acquired IPR&D (nothing for a record without the block)
    gc = n.get("growth_components") or {}
    L += ["", "## Growth & moat",
          f"- Growth blend: {_pct(n.get('g_blend'))}" + (f" → g_base {_pct(n.get('g_base'))}" if n.get("g_base") is not None else ""),
          f"- Components: rev CAGR 5y {_pct(gc.get('rev_cagr_5y'))} · rev CAGR 3y {_pct(gc.get('rev_cagr_3y'))} · latest rev YoY {_pct(gc.get('rev_yoy_latest'))} · OE/share CAGR 2y {_pct(gc.get('oe_ps_cagr_2y'))}",
          f"- Share count CAGR: {_pct(n.get('share_cagr'))} (growth adj {_pct(n.get('share_count_adj'))})",
          f"- Moat: {j['moat_score']}/10 · CAP {n.get('cap_years')} yrs · terminal growth {_pct(n.get('g_terminal'))}"]
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
                L.append(f"| {field} | {val} | {a['kind']} | {a['source']} | {filled} |")
        for field in ("capex", "sbc", "shares"):
            if field in applied:
                L.append(f"- {field} reason: {applied[field]['reason']}")
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
    with open(f"{folder}/key_numbers.md", "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


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
    refuse_superseded_capex_override(n, j_over)               # [ADDITION — WY]

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
    check_iprd_deferred_payment(n, validate_iprd_deferred_payment(j))   # Andrew's 2026-10-20 ruling (delegated)
    check_iprd_share_count_unverified(n, j)   # [Codex review r1 of PR #47]
    j_ads = validate_ads_ratio(j)
    j_second_pass = validate_second_pass(j)

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
        via_ttm = (isinstance(ttm_val, (int, float)) and isinstance(score_base, (int, float))
                   and ttm_val != 0 and abs(score_base - ttm_val) <= 0.001 * abs(ttm_val))
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
                declared = (j_base_override and isinstance(score_base, (int, float)) and score_base != 0
                            and abs(float(j_base_override["value"]) - score_base) <= 0.001 * abs(score_base))
            if not declared:
                fail(f"base pin provenance: the score's base OE/share {score_base} differs from ttm.json's "
                     f"ttm_oe_per_share {ttm_val} by >0.1% (or ttm.json is missing) and judgment.json declares no "
                     "matching base_override {value, source, reason} — a pinned base must come from ttm.py "
                     "(ttm.json, via --ttm) or be declared as a base_override; an arbitrary pin is not scoreable")

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
    # [ADDITION — M3] The payable-earnings pin's own impact (registry
    # base_override event): measured through the current engine only on
    # current-release output, carried / not measured otherwise — and, like
    # every measurement, before the first write.
    payable_impact = None
    if base_override_event_applies(j, n) and n.get("payable_base"):
        payable_impact = (carried_payable_impact(n, prior_payable_event(ticker)) if release_mismatch
                          else payable_pin_impact(ticker, n))

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
             "tier_final": override or n["tier_by_numbers"],
             "confidence": conf, "one_liner": j["one_liner"],
             "analysis_date": n.get("as_of"), "in_scope_under_40b": scope_val}
    # v5.4 additions — every one copied from the engine or derived by rule here.
    flags_all = n.get("fragility_flags") or []
    diag = n.get("diagnostics") or {}
    model_fit = "misfit" if any(str(f).startswith("SECTOR_MODEL_MISMATCH") for f in flags_all) else "modeled"
    _dbl = check_no_double_softening(n, j, model_fit)
    if _dbl:
        fail(_dbl)
    score.update({
        "engine_release": n.get("engine_release"),
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
    tier_final = override or n["tier_by_numbers"]
    reasons, exit_reasons = alert_reasons(
        tier_final, n.get("tier_by_numbers"), override, conf, model_fit,
        bool(reported and impact and impact.get("unblocks_tier")) or pin_rescued(n), bool(diag.get("irr_at_floor")),
        stale_release=release_mismatch_reason(n.get("engine_release")) if release_mismatch else None)
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
    if override:
        score["tier_override_reason"] = j["tier_override_reason"]
    if j.get("moat_for"):
        score["moat_for"] = j["moat_for"]
    if j.get("moat_against"):
        score["moat_against"] = j["moat_against"]
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
    nd_ads = ads_net_debt_basis(n)  # [ADDITION — M1] pre-5.5 ADS record: the ratio on the ADS basis
    if nd_ads is not None:
        score["net_debt_to_normalized_oe_ads_basis"] = round(nd_ads["ads_basis"], 4)
    # Every refusal and every measurement (override and payable impact) is
    # behind us: the scope rewrite is the first write.
    if scope_rewrite is not None:
        rewrite_judgment_scope(jpath, scope_rewrite)
        print(f"make_score.py: {ticker} judgment.json in_scope_under_40b {j['in_scope_under_40b']} -> {scope_rewrite} "
              f"(ADS-corrected market cap {_usd(mktcap)} = price × shares ÷ {ads_corr['ratio']:g}; "
              f"the pre-5.5 engine printed {_usd(ads_corr['old_cap'])})")
        j["in_scope_under_40b"] = scope_rewrite
    with open(spath, "w", encoding="utf-8") as f:
        json.dump(score, f, indent=1)
    # Every run: the ticker's registry entries are replaced wholesale and
    # re-derived from THIS run (applied overrides + judgment-call events).
    scope_event = ({"old_cap": ads_corr["old_cap"], "new_cap": ads_corr["cap"], "in_scope": bool(scope_val)}
                   if scope_corrected else None)
    update_registry(ticker, reported, j_over, impact, j, n, scope_event=scope_event, payable_impact=payable_impact)
    write_key_numbers(folder, n, j, score, reported, impact, ads_corr=ads_corr)
    print(f"make_score.py: wrote {spath} — tier {score['tier_final']}, weighted IRR {score['implied_irr']}, IV@15 {score['iv_at_15']}")


if __name__ == "__main__":
    main()
