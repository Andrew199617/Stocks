# DRAFT SPEC — SBC tag-priority defect in the DCF engine (v5.4.0)

Status: DRAFT, prepared 2026-10-17 (proactive research run). Not implemented.
Engine untouched. Decision needed from Andrew: implement a fix, or keep
JLL blocked and accept the same silent understatement wherever else it
already fired.

One verified blocked name: JLL (blocked 2026-10-17, escalated
NEEDS_MAIN_AGENT: sbc by the sweep worker). The defect is in the tag
merge itself, so any filer that reports both SBC tags in the same period
— with the first-priority tag carrying only a slice — is exposed.

## The verified case

**JLL (Jones Lang LaSalle) — `ShareBasedCompensation` is a $2.7M slice,
not the $114.7M total.**

- The engine's SBC series tries `ShareBasedCompensation` first. For JLL
  that tag is NOT total stock compensation: in the FY2025 10-K it is the
  $2.7M "stock-based compensation expense for post-acquisition retention
  awards" line inside the Restructuring and acquisition charges note
  (FY2024: $2.3M; FY2023: $3.4M — the exact values in
  `~/workspace/stocks/JLL/financials_history.csv`'s sbc column).
- The filer's total is ~40x larger: cash-flow statement "Amortization of
  stock-based compensation" $114.7M (FY2025), $97.4M (FY2024), $78.3M
  (FY2023), and `AllocatedShareBasedCompensationExpense` $112.0M /
  $95.1M / $74.9M for the same years (EDGAR companyfacts). The engine
  only falls back to the Allocated tag when ShareBasedCompensation is
  absent for a period, so the slice wins every period.
- Materiality (from the worker's filing rebuild in
  `~/workspace/stocks/JLL/analysis.md`): the ~$109M/yr gap is ~13% of a
  corrected median base — filing-corrected median ≈ $10.43/sh vs the
  engine's $11.73/sh even after JLL's capex override. `ttm.py` has the
  same defect (its TTM SBC leg is $1.5M).
- Why the worker cannot cure it in bounds: an override only fills a
  period where no value is filed ("an override never replaces a filed
  value"), and a base_override may only be built from figures the run's
  own outputs printed — the correct SBC total appears in no run output.
  This is the DD pattern (filed-but-wrong basis), not a DATA_GAP.
- Direction is not in doubt: even on the flattered base JLL is Tier D
  territory (diagnostic weighted IRR 8.44%, IV@15% $136.84 vs $305.51
  price). The correction lowers base, IV and IRR further. What ships
  without the fix is a materially overstated base — exactly what the
  data gate exists to prevent. No score.json was emitted; the finished
  analysis, moat (5/10) and filing capex override are saved in
  `~/workspace/stocks/JLL/` so a re-score after the fix is fast.

## Root cause, in one line

`period_series()` in `dcf_engine.py` merges candidate tags per period
in priority order and the first tag reporting a period wins it outright
(`if k not in merged`), and the SBC tag list (dcf_engine.py ~line 580)
puts `ShareBasedCompensation` ahead of
`AllocatedShareBasedCompensationExpense` — so a same-period slice from
the first tag silently suppresses the total from the second. `ttm.py`
repeats the pattern: `SBC_TAGS` in the same order, and its
`merged_facts()` gives the highest-priority tag each exact period.

## Why "take the larger when both report" is sound

`AllocatedShareBasedCompensationExpense` is by definition the portion
of total share-based compensation allocated to expense lines — it
cannot legitimately exceed the total. When Allocated > Share for the
same period, the Share tag therefore cannot be the total, whatever its
name says. The spot check below confirms the benign cases are exactly
the ones where the two are equal or Allocated is a strict subset, so a
max/reconcile rule changes nothing for them.

## Spot retro-check already done (2026-10-17, this draft's run)

Scored names whose last-3-FY SBC all came from `ShareBasedCompensation`
at under $15M/yr against >$2B revenue — the JLL-shaped risk set — were
checked directly against EDGAR companyfacts for a competing Allocated
fact in FY2023–25:

- **AMRZ, FDXF, ODFL, UI — clean.** Allocated is absent, zero, equal to
  Share (FDXF, UI: identical every year), or a one-year subset (ODFL).
- **FCNCA — clean.** No Allocated fact at all.
- **ATO (Atmos Energy) — possible second instance, immaterial.**
  Allocated $23.7M / $25.4M / $33.2M vs Share $10.2M / $10.7M / $12.7M
  (FY23/24/25), ~2.5x. Not corroborated against ATO's cash-flow
  statement in this check, so this is a flag, not a verdict. Either way
  it cannot move the score: ATO is Tier F on a −$7.95/sh base, and the
  ~$20M/yr difference is ~$0.13/sh. Re-check on the post-fix re-run.

Not done: the broader set — 112 scored names have FY SBC under 1% of
revenue on the Share tag, most of them legitimately low-SBC businesses
(retail, industrials, transport). A full dual-tag EDGAR comparison for
that set is a post-fix retro-scan job (the `sbc_tag` provenance column
in each `financials_history.csv` plus companyfacts gives it mechanically);
it is not a reason to delay the JLL decision.

## Proposed fix (for Andrew's call — options, not a unilateral change)

1. **Reconcile in `period_series` consumers, not the merge itself:**
   for the SBC field only, when both `ShareBasedCompensation` and
   `AllocatedShareBasedCompensationExpense` report the same period and
   Allocated exceeds Share, use Allocated and record provenance
   (`sbc_tag` shows the tag actually used, plus a fragility flag
   `SBC_TAG_RECONCILED` so the ranking/analysis can see it happened).
   Apply the identical rule to `ttm.py`'s SBC legs.
2. **Fallback if (1) is judged too trusting:** emit
   `DATA_GAP:sbc_tag_conflict` and block scoring when Allocated exceeds
   Share by more than a small tolerance (say 10%) in any of the last
   3 FY — gate-don't-guess, consistent with the v5 data gate. This
   keeps JLL (and ATO) blocked until a human rules per name, so it
   needs a per-name cure path the current override rules don't have.
3. Either way, after the fix lands: re-run JLL (work is saved; expected
   result Tier D on a ~$10.43/sh corrected median base), re-check ATO,
   and run the dual-tag retro-scan over already-scored names before
   trusting any score whose SBC came in under the old priority.

## What does NOT change

- No other tag families: this pattern is specific to SBC, where a
  same-named tag demonstrably carries a note-level slice for at least
  one filer. Capex/shares merges are untouched by this spec.
- Worker override authority is unchanged; the fix is an engine
  decision, which is why JLL escalated instead of self-curing.
