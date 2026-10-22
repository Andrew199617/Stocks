# Second pass — what it is, why it exists, and how it runs (v5.4 governance)

The first pass is a standardized, filing-driven DCF (see README.md, DCF_AUDIT.md). It is
deliberately uniform, which means it structurally misses company-specific context that
doesn't show up in consolidated EDGAR facts. The second pass exists to catch exactly
that, in BOTH directions (hidden strength and hidden rot).

Pass 2 was paused after audit round 1 until its governance existed. This version adds it:
a materiality rule, adversarial framing, a guidance-vs-model check, and the same
no-hand-edits mechanics as pass 1 (judgment.json → make_score.py; queue.py for the queue).

## What it hunts for
- **Segment growth masked by consolidated numbers** — a core segment compounding while a
  sunset / discontinued / legacy line drags consolidated growth (the Unity case: ads
  growing fast while a sunset legacy stack ate reported growth). Reverse case: a dying
  one-off segment flattering the consolidated total.
- **One-offs that aren't** — charges or gains pass 1 normalized away that actually recur;
  and "one-offs" that are really structural costs of the business.
- **Post-filing reality** — guidance changes, earnings-call disclosures, M&A, major
  customer wins/losses, product sunsets announced after the last filing pass 1 used.
- **SBC / dilution trajectory** vs the share-count adjustment pass 1 baked in.
- **Thin flag resolutions** — fragility flags pass 1 resolved on weak evidence get
  re-examined with targeted searches.
- **Guidance vs model (added with the governance)** — the company's own guidance for the
  current year against the scenario growth starts. A base-case start above guidance, or a
  bear case above it, needs a reason or a recalibration.

## Filing freshness — step 0, before the hunts (added 2026-10-13, Andrew)
Pass 1's numbers are only as fresh as its analysis date. Run
`python3 _system/forensic_pull.py <TICKER>` first — its Filing freshness section lists any
10-K/10-Q filed after pass 1's analysis date with a newer period than pass 1 used, plus
material 8-Ks (routine items 2.02 results and 7.01 Reg FD are excluded since 5.4).
- **Newer periodic filing exists** → pass 1's base is stale by definition. Recompute the
  TTM base in code — `DCF_TTM_NO_WRITE=1 python3 _system/ttm.py <TICKER>` (never by hand;
  `--interim` at a 20-F / 40-F filer with a declared bridge; the variable stops it saving
  ttm.json, since nothing is written before `pass2-check`, worker step 5) — and treat a
  material base change as a finding; a base that barely moves still gets both values noted
  in second_pass.md. A newer 6-K interim than the bridge's report is a newer periodic filing,
  but `--interim` rebuilds the DECLARED bridge (its older report), so it never measures the
  newer one: draft it with `python3 _system/ttm.py <TICKER> --interim-draft <new 6-K
  accession>` (it writes nothing; it drafts the legs from that 6-K's XBRL, to compare with the
  declared bridge's), and only after `pass2-check` re-declare `interim_bridge` on that report,
  run `--interim`, then the engine with `--ttm` — the bridged base from that run is the one
  compared with pass 1's (whole-PR review fix, 2026-10-21).
  - When pass 1 rejected the TTM (score.json `base_alternatives`, judgment.json
    `ttm_rejection_reason`, engine 5.7), test the reason against the new TTM's legs. A named
    line that no longer distorts it is a material finding: rerun with `--ttm`, or keep the
    rejection with a refreshed reason and figure (make_score refuses the rerun otherwise).
  - When pass 1 quoted ttm.py's exit-3 message (`ttm_unavailable_reason`), rerun ttm.py: a
    10-Q filed since then builds the TTM.
- **Material 8-K only** → fold its content into the post-filing hunt; quantify or say
  why it doesn't move the numbers.
- `fundamentals.json` (fundamentals.py) carries the last twelve quarters and the TTM; the
  company page's Financials tab shows them. Use it to see the trend the annual history
  hides.

## Forensic battery — every run (added 2026-10-13, Andrew)
Andrew's fundamental-analysis checklist, baked in. `forensic_pull.py` computes the
filing-direct half automatically (paste its output into second_pass.md); the worker
resolves every tripped flag in writing and runs the judgment checks. The battery feeds
three things only: moat evidence, base-OE reconstruction, and confidence.
- **Return on capital (engine 5.7; replaces the 2026-10-14 ROIC-proxy bullet)** —
  make_score's governing return and the same-ladder industry rank in `moat_evidence` /
  key_numbers.md are the measured half of the moat. The governing return is ROIC; tangible
  ROIC for acquirers, with the plain ROIC beside it; ROE at banks, insurers and mortgage
  REITs; ROA as a cross-check. Gross margin stays in fundamentals.json.
  - Challenge the sources first: is each a real source of the enum, and is "wide" earned?
    Then the pillars against their facts. Then the supporting factors (a supporting factor
    presented as the source is P2).
  - make_score already refuses an unreasoned 7+ on low returns and an unreasoned 4 on
    sustained 20%+ returns on a 5.7 run. On older output those remain findings: a 7+ on
    ROIC below ~10% without a written reason (moat evidence AGAINST), and a 4 on sustained
    20%+ ROIC (the reverse case).
  - Challenge an `erosion_rebuttal` or a confirmed widening against the cycle. What is each
    number in the rebuttal? A commodity price cycle is the typical case. A widening from a
    trough (`WIDENING_FROM_TROUGH`) needs an explanation.
  - An erosion_risks threat resting only on the MOAT_EROSION measurement, on top of hold 0,
    is double counting (P2 if it moves the tier, else P3).
- **Margin structure** — gross margin level + trend (≥40% is the durable-advantage rule
  of thumb, judged sector-relative: a grocer and a software firm are not the same test);
  COGS % of revenue stability (swings in non-compounders = weak cost control = moat
  evidence AGAINST).
- **SG&A-vs-COGS split test (IBM pattern)** — if costs migrate between COGS and SG&A
  while combined (COGS+SG&A)/revenue is flat, it's presentation, not improvement; the
  combined series is the honest one.
- **NI vs operating income gap** — a persistent gap means noncore items (interest,
  investment gains/losses, one-offs) are carrying or dragging reported earnings.
  Interpret with care when operating income is near zero (the % explodes).
- **Prepaid battery** — prepaids % of assets, prepaids/SG&A, YoY and QoQ jumps. The
  deferral pattern is: prepaids spiking while earnings improve and OCF weakens, then
  reversing into expense later. Any leg of that pattern gets resolved in writing.
- **Divestiture / discontinued-ops optics (judgment)** — when a divestiture, held-for-
  sale line, or discontinued ops appears, compare pre / during / post on operating
  income, SG&A, CFO, and FCF, including stranded costs the parent still carries. State
  plainly: real improvement or accounting optics.
- **Noncore income reconstruction (judgment)** — build core revenue and core operating
  profit excluding interest, investment, financing, and one-time gains; track the
  noncore share over time. If noncore is material to the base, rebuild base OE on core
  numbers and log the change like any other.
- **Capitalized-cost shifting (judgment, WorldCom pattern)** — capex or capitalized
  balances (e.g. capitalized software) growing faster than revenue while SG&A/R&D fall
  and earnings outrun OCF. Any two legs together = hard look, in writing. Since engine 5.7
  capitalized software is charged in owner's earnings, so shifting cost into capitalized
  software no longer lifts the base. The pattern still matters for earnings quality and for
  a capitalization rate that jumps.
- **Standing cautions** — adding back S&M/R&D "growth spend" to owner's earnings is a
  sensitivity only; the headline base stays conservative unless evidence is unusually
  concrete. State which of pass 1's two OE definitions (total-capex vs maintenance) is
  the honest one for this business, and why. A hard forensic hit (deferral pattern,
  capitalized-cost shifting, noncore carrying the base) can force a downgrade on its
  own, logged like any other change.

## Governance (v5.4 — the rules that let pass 2 restart)
- **Materiality.** A score changes ONLY when the recomputed weighted IRR moves by ≥2
  percentage points or the tier changes, AND the driver is a filing-sourced number
  (a newer 10-Q/10-K, a segment disclosure, a restated line) or a company-stated guidance
  figure with a citation. Everything else is "no material finding" — a valid, common
  outcome — recorded with the checks listed.
- **Adversarial framing.** Every run argues the NEIGHBORING tier (one up and one down)
  with one numeric test each — e.g. "what growth start would it take to clear 15%, and
  does any print support it?" — and records the result. A same-model re-read that merely
  confirms itself is not a second pass.
- **Sector misfits (engine 5.7).** A misfit's published tier is the mechanical notch of its
  numbers tier (score.json `misfit_notch`). Pass 2 argues the neighboring NUMBERS tier. On a
  5.7 rerun it writes `misfit_notch_reason` (with a number) — never a `tier_override`
  restating the notch (make_score refuses it).
- **Reproducible inputs.** A rerun uses the same engine and sanity checks as pass 1 and
  records its exact inputs (moat, probs, offsets, mults, base pin, gterm, price) in
  second_pass.md; the engine stamps them in dcf_numbers.json.
- **No hand edits.** Pass 2 never writes score.json. A material finding becomes a new
  judgment.json (same fields as pass 1, refreshed moat_for / moat_against and
  moat_scorecard (sources and supporting factors included), updated one_liner, plus a
  `second_pass` object — see below) and a final engine run; then `make_score.py` rebuilds
  score.json and refuses any disagreement, exactly as in pass 1. The rerun is engine 5.7
  output, so every 5.7 obligation of WORKER_SPEC steps 4-8 applies to it.
- **A malformed queue file stops the command (engine 5.7, R5).** A
  `second_pass_queue.json` that parses but is not `{"entries": {<ticker>: {...}}}` (a list,
  `{}`, `entries` null or a list, a non-object entry) makes every pass-2 command and
  `queue.py refresh` exit 1 with "is malformed … restore it from git". The file is left
  untouched, and so is queue.json: refresh checks the pass-2 file before it touches queue.json,
  so its message says "nothing was changed". Only when the file turns malformed between that
  check and the pass-2 reset does the message say queue.json already has the name back at
  pending. Restore the file from git and run the command again. (PR #47's round-26 registry rule;
  before, the command repaired it with an empty `entries`, and the save erased every other
  ticker's review record.)
- **Alerts.** Report to chat ONLY when a change moves the company INTO or OUT of Tier S/A
  AND the new score.json clears that direction's gate: an entry needs `alert_eligible: true`
  (medium+ confidence, not a sector misfit, tier not resting on an override, IRR not at
  the floor; since 5.7 also not lifted into S/A by a share-class declaration or a TTM
  rejection); an exit needs `exit_alert_eligible: true` (medium+ confidence, not a sector
  misfit, tier not existing only because of a data override; a floor IRR reads "at most
  terminal growth", which confirms the drop, and a judgment tier override that takes the
  name below A is still a warning, so neither suppresses an exit; `alert_eligible` is
  false below A by construction, so it can never gate an exit). Everything else is
  silent; the daily ranking shows the ↺ badge.

## The `second_pass` object (judgment.json → score.json, via make_score.py)
```json
"second_pass": {"date": "YYYY-MM-DD", "verdict": "changed" | "no_change",
                "prior_tier": "C", "prior_weighted_irr": 0.123, "prior_iv_at_15": 45.67,
                "summary": "evidence + sources in 2-4 sentences"}
```
`verdict: "no_change"` is recorded too (the ranking shows "✓ pass 2 checked"): rerun
`make_score.py` with the object added to judgment.json — nothing else changes, the engine
run is untouched. `verdict: "changed"` requires prior_tier (and the priors) and goes with
the new engine run.

## Worker steps (both second-pass crons point here)
1. **Preflight, then claim.** `python3 _system/preflight.py` first. Any exit but 0 → do not
   claim: record the run as failed (step 8) and finish. Then
   `python3 _system/queue.py pass2-claim` prints the ticker (first done name in
   queue order with a score.json whose second-pass entry is absent, pending, an expired
   claim, or a review of an older scoring generation; APP is the last candidate; the claim
   is marked under the lock). A generation is one pass-1 scoring run: when the filing
   watcher refreshes a name and pass 1 re-scores it, the new score is reviewed again.
   Nothing printed → finish silently.
2. **Read the folder fully**: analysis.md, score.json, dcf_numbers.json, key_numbers.md,
   financials_history.csv, fundamentals.json, facts.json (engine 5.7) and the saved runs
   `dcf_numbers_<label>.json`. Identify pass 1's load-bearing assumptions: base choice
   (under STALE_FY: `base_alternatives`, any `ttm_rejection_reason` /
   `ttm_unavailable_reason`), blended growth and scenario starts, moat (`moat_evidence`),
   probabilities, and how each flag was resolved. Attack the assumptions most likely to be wrong — do not redo the pass.
3. **Freshness + battery**: `python3 _system/forensic_pull.py <T>`; keep the output for
   second_pass.md, where every tripped flag gets a written resolution; run the judgment
   checks above.
4. **Targeted research** (2–4 searches) in BOTH directions, plus the guidance-vs-model
   check and the two adversarial tier tests.
5. **Check the claim before you write anything.** Steps 2–4 only read. Before the first
   write for this review — second_pass.md, the analysis.md addendum, judgment.json,
   ttm.json, the engine, make_score.py — run `python3 _system/queue.py pass2-check <T>`.
   It refuses (exit 1) when the name was refreshed for a newer filing or re-scored after
   your claim, so your review read a superseded score: write nothing, report nothing and
   finish — the new score gets its own second pass. Exit 0 → step 6 or 7.
6. **No material finding**: write second_pass.md (checks, sources, why the score stands,
   the adversarial tests), add `second_pass {verdict: "no_change", ...}` to judgment.json
   and run `python3 _system/make_score.py <T>`. Then
   `python3 _system/queue.py pass2-done <T> done_no_change` and
   `python3 _system/build_site.py`. Finish silently.
7. **Material finding**: quantify it; rerun the engine with the pass-1 sanity checks
   (run `python3 _system/moat_scorecard.py <T>` first and pass the `--moat-trend` value it
   prints — make_score refuses another; the dry run does not trace reasons, so a rebutted
   erosion's `stable` holds only if make_score's trace accepts the `erosion_rebuttal`
   (WORKER_SPEC step 5);
   `python3 _system/dcf_engine.py <T> --moat ... --moat-trend <value> --probs ... [--offsets] [--mults] [--ttm] [--gterm] [--cik]`,
   `--ttm` after a fresh, saving `ttm.py` run when the base moved (a rerun that keeps a
   non-TTM base under STALE_FY needs `ttm_rejection_reason`, WORKER_SPEC step 4); a judgment.json carrying an
   `iprd_amortized` `base_override` (engine 5.6) is rebuilt from that rerun's dcf_numbers.json
   `iprd_adjustment` and ttm.json exactly as WORKER_SPEC step 8 builds it — the changed inputs move its
   native base, so the old value no longer reproduces — and the final rerun passes
   `--base-oe-ps <the new value>` instead of `--ttm`; drop the declaration when the rerun no longer
   raises `ACQUIRED_IPRD_RECURRENT`); write the new judgment.json
   with the `second_pass {verdict: "changed", prior_*}` object; `make_score.py <T>`; write
   second_pass.md with what pass 1 missed, the evidence with sources, old vs new inputs,
   old vs new scenario table and weighted result; append a dated
   "## Second pass (YYYY-MM-DD)" addendum to analysis.md pointing to second_pass.md —
   never rewrite pass-1 content. Then `python3 _system/reprice.py <T>` (the live overlay
   follows the new paths), `queue.py pass2-done <T> done_changed` and
   `python3 _system/build_site.py`.
   **`pass2-done` refused by the quote check** (engine 5.7: "analysis.md fails the quote
   check"). This is not a superseded review. Nothing was recorded and nothing needs
   deleting. Fix the analysis.md addendum as step 8 says (quote the generated figure, or
   declare it in facts.json and re-run make_score.py), run `check_quotes.py <T>` until it
   passes, then run `pass2-done` again.
   **`pass2-done` refused** (exit 1, in step 6 or 7: the refresh or re-score landed while
   you were writing). Nothing was recorded in the second-pass queue. Delete the
   second_pass.md you wrote in this run and the dated "## Second pass" addendum you
   appended to analysis.md in step 7 (it points to that file), and leave the rest; the
   refusal names the case:
   - **pending, being re-scored or blocked** in queue.json → the re-score the name awaits
     rewrites judgment.json, dcf_numbers.json and score.json, and your `second_pass`
     object goes with them;
   - **re-scored after this claim** → the newer generation is already scored, so nothing
     will rewrite what you wrote: leave judgment.json and score.json as the new
     generation left them.
   Either way report nothing and finish — once your claim's lease expires, the new score
   gets its own second pass.
   A pass-2 change is a folder change: its PR is cut per `_system/PR_PROTOCOL.md` (kind
   `pass2`, title `Second pass: <T> — …`). A no-change review that wrote second_pass.md is
   one too.
8. **Reporting**: per the alert rule above; also report plainly if the second-pass system
   itself is blocked. Never invent numbers. In the analysis.md addendum every figure traces
   like pass 1's: key_numbers.md, dcf_numbers.json, ttm.json, a saved run, or a fact you add
   to facts.json and render with make_score.py. Run `check_quotes.py <T>` before
   `pass2-done`. On 5.7 runs `queue.py pass2-done` (done_no_change / done_changed) refuses a
   failing analysis and records nothing; `pass2-reset` is never gated. second_pass.md cites
   the forensic battery and sources as before (dcf_numbers.json, key_numbers.md, ttm.json,
   the forensic battery, fundamentals.json or a cited source).
   **Run health (engine 5.7, R5):** `run_health.py record <job> ok` when the run ended as
   steps 1-7 say (no candidates; a pass2-check or pass2-done refusal handled as steps 5 / 7
   say; pass2-done recorded). Else `record <job> fail --stdin` with the reason (preflight's
   first line; a script that crashed; make_score refused and the run could not finish). Post
   any line it prints.
