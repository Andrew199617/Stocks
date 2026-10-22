# Company PR protocol (engine 5.7; Andrew's ruling R5, 2026-10-19)

Binding for whoever Muse assigns to cut a company PR (pass 1, a re-score, a second-pass change, a review round, a
bulk rebuild). Every step goes through `python3 _system/pr_worktree.py`; nothing here is done by hand.

Why: after PR #31 the sweep tree kept running engine 5.4.0 and MOH (#37) / ESTC (#35) were published as 5.4
scores; BMRN was done with no PR; two PR agents worked in one worktree; registry deltas were hand-"constructed"
(#33, #38); review fixes were made only in the PR worktree (HUT #33). The guards: `preflight.py` (the sweep tree
runs origin/main's method), a per-ticker lease lock, make_score re-run at origin/main's code inside the PR worktree,
staging limited to what a company PR may carry, and `pr_audit.py` daily.

Where this file is used: pass 1 reaches it from WORKER_SPEC.md step 10, pass 2 from SECOND_PASS.md steps 6–7, and
the 19:07 job through pr_audit's findings (section 8). The backlog appends of section 1 go to `_system/ENGINE_BACKLOG.md`.
`_system/README.md` "Fixes & lessons" (2026-10-21, sweep reliability) records why each guard exists.

## 1. What a company PR carries

- The ticker's committed files under `<T>/` (everything there `.gitignore` does not exclude).
- `_system/overrides_registry.json` with only `<T>`'s entries changed. make_score derives them in the PR worktree
  against main's registry — never hand-constructed. Another ticker's entry changed is P2.
- Appended lines in `_system/ENGINE_BACKLOG.md` (the backlog exception, AGENTS.md "What is in a PR"): a new
  `### EB-<NNN>` entry, or an `### EB-<NNN> seen again` entry, after the file's last line. `pr_worktree.py
  backlog-next` names the next free id. A "didnt fix" reply that names a code defect appends one in the same PR.
  The entry is appended in the PR worktree's `_system/ENGINE_BACKLOG.md` — the one file edited there (preflight
  never guards the sweep tree's copy; main's file is the record) — in the format the file's header gives; `open` / `push`
  refuse an edited or removed line, an id main already uses, an entry that does not parse, and the `#<this>`
  placeholder.
- Never `_system/queue.json`, never a cache (`prices.json`, `live.json`, `street.json`, site files), never code or
  a spec. `pr_worktree.py open` refuses anything else.
- Never `_system/industry_returns.json` (the moat evidence's industry input; the daily cron and `rebuild_scores.py`
  write the sweep tree's build). prepare scores against the sweep tree's copy, puts main's back, and the Mechanics
  block names both builds. A bulk rebuild PR is the one PR that carries it.
- An owner-directed acceptance re-score (AGENTS.md "What is in a PR"; PR #31, PR #47's HALO) rides with its code PR
  and never goes through pr_worktree.

## 2. Branch and title

- Branch `dcf/<T>` when origin has no branch of that name; otherwise `dcf/<T>-<YYYYMMDD>` (the ET date of the
  scoring generation's claim), then `-2`, `-3`. (`dcf/<T>/…` is impossible: it collides with the ref `dcf/<T>`.)
  Bulk make_score rebuilds: `rebuild/<release>-<YYYYMMDD>`.
- Title, written by pr_worktree from score.json:
  `DCF pass 1: <T> — <name> — Tier <final>[ (<by numbers> by numbers, <irr>%)], weighted IRR <irr>%`
  (`Tier F (no cash generation)` for a Tier F run with no IRR); `Re-score: <T> — …` for a refreshed generation;
  `Second pass: <T> — …` for a pass-2 change; `Rebuild: make_score at release <rel> over <N> folders` for a bulk
  rebuild.

## 3. Steps, in order

Every command after `acquire` names the same `--holder "<your agent id>"` (exit 2 without it). When your lease
expired and another agent took the name, prepare / open / push / restack refuse with exit 4 naming the new holder:
stop, never touch that worktree, and finish.

a. `python3 _system/pr_worktree.py acquire <T> --holder "<your agent id>" --kind pass1|rescore|pass2` — the
   per-ticker lock (a 3-hour lease) and a fresh sparse worktree at `<PR_ROOT>/<T>` on a new branch from
   origin/main. Refused (exit 4) while another agent holds it: never enter, edit or delete another agent's
   worktree; finish and leave the name to it. Long work: `renew <T> --holder <id>`.
b. `python3 _system/pr_worktree.py prepare <T> --holder <id>` — checks the sweep tree with preflight (refuses on
   drift); copies the committed folder files (refuses when a record file main has is gone from the sweep folder);
   re-runs make_score.py at origin/main's code in the worktree (score.json, key_numbers.md and `<T>`'s registry
   entries against main's registry), against the sweep tree's `_system/industry_returns.json` (the build the sweep
   scored with; main's copy is put back afterwards); runs `check_quotes.py <T>` on a 5.7 run; refuses when the
   rebuilt score differs from the sweep tree's on any decision field (make_score's `SCORE_DECISION_KEYS` plus
   `override_impact.unblocks_tier`; the refusal names the differing sub-field, e.g. `moat_evidence.industry_file`
   when the daily cron rewrote the industry file after the folder was scored — re-run make_score.py on the sweep
   tree, then prepare again); refuses when the registry would change another ticker's entries, would be refused by
   make_score, or loses part of `<T>`'s acquired-IPR&D deferred-payment record; prints the summary.
   **Engine output from an older release** (lane default Q12 (b), 2026-10-21, pending Andrew's ratification): the
   folder is rebuilt by make_score at main's release (the misfit notch applies mechanically) and published with the
   alert gates the stale-release rule closes; no engine re-run is required (Andrew's Q3 ruling: no directed re-run
   wave). The Mechanics block says the engine output predates the release, and so must the body. The one switch is
   `STALE_RELEASE_POLICY` in pr_worktree.py ("refuse" = re-run the engine first, design 05's option (a)).
c. Write the PR body (template in section 7). Every number is copied from key_numbers.md, score.json,
   dcf_numbers.json or ttm.json (R3) — the "rubric checks" are recomputations of those files, stated as such.
d. `python3 _system/pr_worktree.py open <T> --holder <id> --body-file <path>` — stages exactly the allowed paths
   (refuses anything else, a deletion, or a worktree file changed since prepare), commits, pushes, opens the PR with
   `gh pr create`, records the number in the lock, prints the URL. Pass `--trailer "<line>"` for the attribution
   trailer the session uses.
e. `python3 _system/pr_worktree.py release <T> --holder <id>`. The worktree stays until the PR is merged or closed;
   `reap` removes it.

Fix in the **sweep tree**, never only in the worktree: the sweep tree must equal main after the merge (pr_audit
reports it otherwise). open and push refuse a worktree file changed since prepare (ENGINE_BACKLOG.md appends
excepted).

## 4. Review rounds

`acquire <T> --holder <id> --kind review-fix` (reuses the open PR's branch and the same path). Fix the sweep tree
first, re-run make_score there, then `prepare <T> --holder <id>` again and
`push <T> --holder <id> -m "<what the round fixed>"`. A "didnt fix" reply that names a code defect appends an
ENGINE_BACKLOG entry in the same PR (section 1).

## 5. Main moved before the merge

A registry or backlog conflict, or prepare saying the worktree runs older code than origin/main:
`python3 _system/pr_worktree.py restack <T> --holder <id>` — resets the branch onto origin/main, re-copies the folder, re-runs
make_score (the registry re-derived against the new main), re-appends the PR's backlog block after main's new last
line (renumbering any new EB id main now uses), commits and pushes with `--force-with-lease`.

## 6. Syncing the sweep tree after a code PR merges (main agent, not a worker)

Workers stop on preflight exit 1 (their run is recorded as failed; run_health raises the ALERT on the second one —
the expected signal until the sync). In this order:
1. `python3 _system/preflight.py --sync` — refuses (exit 5) while a claim is live; checks out origin/main's policy
   and advisory files, and `_system/industry_returns.json` when the sweep tree has none (a sweep tree's own build of
   it is never overwritten; preflight exits 1 while it is missing). On the VM run it **before any engine-5.7
   registry event exists there**: a pre-5.7 make_score refuses a registry that holds one (misfit_notch,
   declared_facts, …), so every tree on the VM runs 5.7 code first.
2. `python3 _system/rebuild_scores.py` — the dry run: which folders change tier, which refuse, which need network.
   It builds `industry_returns.json` from the scored folders into its work copy first, so it scores against the file
   the apply step writes. Bring the list to Andrew when it shows tier changes.
3. `python3 _system/rebuild_scores.py --apply --from-report <report.json>` — `industry_returns.py --write` on the
   sweep tree, make_score on each changed folder, then one `reprice.py --all`, then one `build_site.py` (live figures
   pause on every rebuilt name until the reprice; a changed industry build since the dry run is named, and the
   applied table is the actual result).
4. `python3 _system/pr_worktree.py acquire --bulk <report.json>.applied.json --holder <id>` (every rebuilt in-sync
   ticker, all-or-nothing), `prepare --bulk <branch>`, `open --bulk <branch> --body-file <path>` (`--holder` defaults
   to the bulk set's). The bulk PR carries the sweep tree's `_system/industry_returns.json` with the folders. A
   folder `prepare --bulk` refuses is named first in the refusal (`pr_worktree: <T>: …`); before `open`,
   `prepare --bulk <branch> --exclude <T>[,<T>]` drops it from the set (its lock released, the worktree reset) and
   prepares the rest — re-score the dropped folder on its own afterwards. The Mechanics block names each folder's
   `score.dcf_content_hash`, whether its score is built from its run, and "the engine output predates release <rel>"
   for every folder whose run does (whole-PR review fix, 2026-10-21).

## 7. PR body template

```
## Verdict
| | |
|---|---|
| Tier | <tier_final> (<tier_by_numbers> by numbers) |
| Weighted IRR | <implied_irr> |
| Price / IV@15 | <price> / <iv_at_15> |
| Base OE | <base_oe_per_share> (<base_source>) |
| Moat | <moat_score> (evidence <moat_evidence.evidence_score>) |
| Confidence / model_fit / misfit notch | <confidence> / <model_fit> / <misfit_notch: applied B → C, or not applied (why), or —> |
| Acquired IPR&D | <iprd_adjustment: charge/share and treatment — only when present> |
| Market cap | <market_cap_b> |
| Engine release | <engine_release> (say so when it predates main's: rebuilt by make_score, alert gates closed) |
## Base
## Overrides
## Flags resolved
## Rubric checks
## Didn't-fix and backlog
(each didnt-fix with its EB id)
## Files
```
pr_worktree appends a generated `## Mechanics` block: the origin/main sha the score was rebuilt at, the release,
the run's release (and that it predates main's, when it does), `score.dcf_content_hash` (12 characters) and "score
built from this run: yes" (build_site's score_from_run), the check_quotes result, the registry delta count, the
fields make_score re-derived that are not decisions, and the file list. Never edit it.

## 8. pr_audit findings (the 19:07 job prints them)

- `missing_pr` — a done name differs from main with no PR for its scoring generation: cut the PR now (section 3).
  A finished second pass (done_changed or done_no_change in second_pass_queue.json) of the current scoring
  generation is a generation of its own: its PR is the `Second pass: <T> —` PR (`acquire <T> --kind pass2`); the
  finding says "second pass" and is never reported before the review's day is over plus the grace hours.
- `merged_then_changed` — the folder changed after its PR merged (for a second pass: after its Second pass PR
  merged): if the change is a newer generation, cut its PR; if it is a review fix left behind, copy main's files
  back into the sweep folder (`git -C ~/workspace/stocks checkout origin/main -- <T>/<f>`) — main is the reviewed
  record. A second pass after the pass-1 PR merged is never this finding (copying main back would erase the review).
- `stale_open_pr` — the only open PR predates this generation: push the new generation to it (`review-fix`) or
  close it and cut a new one.
- `score_not_from_run` — score.json is not make_score's score of the folder's dcf_numbers.json (make_score refused
  the latest engine run, or has not run on it): no PR until it scores; fix the refusal in the sweep tree.
- `missing_folder` — done in queue.json with no score.json: block or requeue the name.

## 9. Housekeeping

- `python3 _system/pr_worktree.py status` — every lock (live / expired) and worktree.
- `python3 _system/pr_worktree.py reap` — removes stale locks, and the clean worktrees whose newest PR merged or
  closed (a branch name like `dcf/<T>` is reused: a worktree with any OPEN PR on its branch name stays, and so does
  one holding commits that are neither that PR's head nor pushed).
- `python3 _system/pr_worktree.py discard <T> --force` — removes a dirty orphan worktree (only with no live lock).
- `python3 _system/pr_worktree.py backlog-next` — the next free ENGINE_BACKLOG id on origin/main.
Exit codes: 0 ok · 1 refused · 2 usage · 3 environment · 4 held by another holder.
