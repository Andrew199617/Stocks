# Pass-1 worker spec (single source — both sweep crons point here)

Run ONE company through the owner's-earnings DCF sweep. Method: v5 data gate + engine
release 5.7 (normalized base, blended growth, moat-driven fade, five scenarios, IRR band).
5.5 added the share-basis checks, additive capex with intangible purchases, SBC tag
reconciliation and USD-declared overrides. 5.6 added the one-time acquired-IPR&D value
adjustment. 5.7 is Andrew's rulings release of 2026-10-19 (R1-R9):
- the mechanical sector-misfit notch, detected on the universe sector or the EDGAR SIC;
- declared facts and strict quoting (`facts.json`, `check_quotes.py`);
- the moat's sources and evidence scorecard, with the moat's direction setting the growth hold;
- the declared 6-K interim bridge, and annual facts read from a filing's own XBRL instance;
- declared share classes (Up-C / multi-class share basis);
- a STALE_FY TTM base that may be rejected only with a reason that carries a number;
- capitalized software / development in capex, and every filed PP&E component summed
  (machinery and equipment, mining assets, furniture and fixtures);
- the sweep's preflight and run-health checks.
README "Fixes & lessons" (the Engine 5.5, 5.6 and 5.7 entries) has the detail.
`README.md` has the method and "Fixes & lessons"; `DCF_AUDIT.md` explains why each rule
exists; `APP/` is the worked example of the output shape (including an override). For 5.7
facts and quoting see `_system/examples/facts/`. The other files in `_system/examples/` are
worked examples of the moat scorecard, the interim bridge and a TTM rejection.

**MECHANICS — no exceptions.** Never edit `queue.json`, `score.json`, `key_numbers.md` or
`second_pass_queue.json` by hand. The queue is touched only through `queue.py`, TTM figures
come only from `ttm.py`, `score.json` is built only by `make_score.py` from
`dcf_numbers.json` + the `judgment.json` (and `facts.json`) you write. Every number in
`analysis.md` is copied from `key_numbers.md`, `dcf_numbers.json`, `ttm.json` or a saved
method run (`dcf_numbers_<label>.json`) — never recomputed, never retyped. Some numbers the
engine cannot produce: filing text, a company release, a third-party source, or a
folder-file figure such as a quarterly print in fundamentals.json. Declare each one in
`facts.json` first (step 7b). make_score renders it under "Declared facts (not engine
output)" in key_numbers.md, and you quote it from there. judgment.json is never a source.
Since engine 5.7 `queue.py done` runs `check_quotes.py` and refuses a run whose analysis.md
quotes a number no generated file holds. All paths below are under `~/workspace/stocks/`
(the system folder is `_system/`).

## Steps
1. **Preflight, then claim.** Run `python3 _system/preflight.py` first.
   - Exit 0 → `python3 _system/queue.py claim` prints your ticker (atomic, 90-min lease; the
     reaper runs first). Nothing printed → rebuild the HTML (step 10) and finish silently
     (a successful run).
   - Any other exit → do not claim. Record the run as failed with preflight's first line
     (step 11) and finish. Exit 1 means this tree's policy files (every top-level
     `_system/*.py`, WORKER_SPEC.md, SECOND_PASS.md, PR_PROTOCOL.md, AGENTS.md) differ from
     origin/main, or the tree has no readable `_system/industry_returns.json` while main has
     one. A score made now would be on a method main has replaced (MOH and ESTC were scored
     on 5.4.0 after 5.5 merged). Exit 4 means the fetch failed: the run cannot prove it is on
     main's method.
   - Never edit or sync those files yourself. `preflight.py --sync` is the main agent's step
     (PR_PROTOCOL.md "Syncing the sweep tree").
2. **Preliminary engine run.** `python3 _system/dcf_engine.py <T>` (allow 300s: it fetches
   EDGAR, Nasdaq and ECB rates, and replays itself twice when an override is present).
   - **Exit 4 `DATA_GAP`** — required filing data is missing (sbc / capex / shares / ocf /
     currency / price; the DATA_GAP flag names the field and years). Never score gapped
     data. Resolve ONLY within the bounded authority in step 8, then continue; otherwise
     block via stdin — `printf '%s' "DATA_GAP: <fields> — <detail>" | python3 _system/queue.py block <T> --stdin`
     — and finish. `DATA_GAP:shares` (5.4) names the basic / outstanding count the filer
     did file: the diluted count sits in the 10-K EPS note — a `shares_override` kind
     "filing" from it is in bounds. A filed count of 0 (or below) is not a count (5.5): the
     gap text names it ("a filed count <= 0 is not a share count and was treated as not
     filed (FY<y> <tag> 0)" — TLN FY2022) and the same EPS-note override fills it. Two 5.5 `DATA_GAP:shares` texts are a different case
     that no override covers — `SHARE_SCALE` and `SHARE_CLASS_MISMATCH` (gap keys
     `share_scale` / `share_class`); step 4 says how to block them.
   - **Exit 3 `DATA_GAP:price`** → block the same way and finish.
   - **Exit 3 `BAD_SHARE_CLASSES` / `BAD_TTM_SHARE_BASIS` (engine 5.7)** → the engine refused
     the run and wrote nothing. These two refusals, and the `UP_C_SUSPECT` flag (step 4), are
     not blocked. Fix them in judgment.json (`share_classes`, `up_c_suspect_reason`,
     `shares_override.share_basis`), then rerun `ttm.py` and the engine.
   - **Re-score after a new filing**: when the folder already holds a prior run (the queue
     entry carries `refresh_reason: NEW_FILING…`), read its analysis.md first; judgment.json
     and its overrides carry over and the tools apply them, except its `second_pass` object:
     remove it, since it reviewed the previous score (pass 2 reviews the new one, and
     make_score.py would otherwise copy the old badge onto it). An `iprd_amortized`
     `base_override` is not carried either: rebuild it from this re-score's preliminary run
     (step 8 — the new filing moves its native base, window and share count, so the carried
     value no longer reproduces and the engine refuses it), or drop it when that run no longer
     raises `ACQUIRED_IPRD_RECURRENT`. `ttm_rejection_reason` and `ttm_unavailable_reason`
     (engine 5.7, step 4) carry over only as drafts. Each answers one ttm.json (or one ttm.py
     message). Rewrite the reason's figures from this re-score's ttm.json (make_score traces
     them), re-quote ttm.py, or drop the field when you pin the TTM. `iprd_cash_flow_check` entries carry over (they record
     what a filed cash-flow statement shows); add one for each new period the run names, then rerun the
     engine (step 3: make_score refuses a judgment.json whose IPR&D declarations changed after the run).
     `iprd_deferred_payment` entries carry over too (they record which deal a filed charge
     belongs to; they name FY periods only, so a change of basis never strands one); KEEP one whose period
     has left the engine's window — never delete it: the engine lists it in `deferred_payments_rolled_out`,
     never applies it (no deduction, no recurrence effect), and still counts its amount toward the deal's
     lifetime `contingent_total` cap; make_score refuses a run whose rolled-out entry judgment.json no longer
     declares (Codex review round 4 of PR #47) — also when the window holds no acquired-IPR&D charge at all
     (a minimal `deferred_payments_only` block; Codex review round 5) — and, since Codex review round 8, whatever
     the engine run: the registry's `iprd_deferred_payment` event keeps each deal's paid_to_date and every period
     ever declared, so declarations summing below it are refused, (round 9) its recorded name,
     `contingent_total` and `first_charged_period` stay as recorded (step 8), and (round 10) every recorded
     period keeps its recorded amount — declare it unchanged, never moved to another period. Write the new
     analysis.md as a dated supersession (state what the new filing changed), keep the prior flag and
     override decisions unless the filing changes them, and re-run every enrichment step.
   - **Exit 3 `NO_DATA` / exit 2 `NO_CIK`** → thin or no history, often a holding-company
     CIK change: web-search "<company> CIK 10-K", rerun with `--cik <CIK>`; only if no filing
     parent exists, block with a reason starting `NO_DATA:` and finish.
   - **Exit 5 `BAD_MOAT_TREND` (engine 5.7)** → the `--moat-trend` value is not eroding /
     stable / widening. It is never a CIK or data problem. Rerun with the value
     `python3 _system/moat_scorecard.py <T>` printed (step 5). The engine checks the flag
     before any fetch, so nothing was downloaded.
   - **Save the preliminary run at once (engine 5.7):**
     `python3 _system/check_quotes.py --save-run <T> prelim`. Save any exploratory run you
     will quote the same way (`--save-run <T> <label>`): a method range is quoted from saved
     runs only. The copy is refused unless the run's content_hash verifies.
   - **Run the SEC enrichment now** (non-blocking): `python3 _system/fundamentals.py <T>`,
     `python3 _system/segments.py <T>`, `python3 _system/statements.py <T>`,
     `python3 _system/profile.py <T>` (step 9 says what each file holds). make_score verifies
     folder facts against these files. The moat scorecard's measured pillars read
     fundamentals.json (at least 3 annual rows; else financials_history.csv, which has no
     goodwill, pretax or gross-margin line: no tangible ROIC and no trend test). So they run
     before the moat is scored.
3. **Research** (1–3 web searches): the business, latest quarter and TTM, competitive
   position, red flags (dilution/SBC, concentration, litigation, going concern, one-offs,
   divestiture/restated basis breaks). Record every figure you will quote as a fact as you
   go: its kind, source (accession + section / exhibit, or URL + publisher + date), period,
   date, and a verbatim snippet of at most 24 words that contains the number (a figure a
   folder file holds is a kind `folder` fact with a path instead — step 7b).
4. **Address EVERY fragility flag** in `dcf_numbers.json` with a specific resolution in
   `analysis.md`. Recurring ones — `STALE_FY` (engine 5.7; Andrew's ruling R7, 2026-10-19):
   a 10-K filer runs `python3 _system/ttm.py <T>` (saves `ttm.json`) and passes `--ttm` in the
   final run; quote ttm.json's legs. Run ttm.py with the CURRENT engine every time, then rerun
   the engine (a ttm.json regenerated after the run is refused: TTM_CHANGED). Never reuse a
   ttm.json from an earlier run. Since engine 5.7 ttm.json records the `engine_release` that
   built it. The engine copies it to dcf_numbers.json `ttm_inputs.ttm_engine_release` whenever
   the run's basis reads ttm.json (the `--ttm` pin, an undeclared `--base-oe-ps` pin, a
   `basis_window` "ttm" pin). make_score refuses a 5.7 run whose basis read a ttm.json from an
   older engine ("ttm.json predates engine 5.7 … rerun ttm.py with the current engine").
   **Rejecting the TTM (R7).** You MAY reject the TTM base, but only with judgment.json
   `ttm_rejection_reason`. It is one sentence that names the distorting cash-flow line WITH A
   NUMBER. The line is operating cash flow or one of its lines (working capital, receivables,
   inventories, payables, deferred revenue, taxes paid, pension …), capex (PP&E, capitalized
   software, intangibles) or SBC. A cyclical peak or trough names operating cash flow (or the
   line that moved) with its figure. HII qualifies ("median +$16.14/sh Tier C vs TTM
   −$3.48/sh on a half-year working-capital trough"; `_system/examples/ttm_rejection_hii.json`).
   "Working-capital timing" does not. Every figure in the reason traces to ttm.json,
   key_numbers.md, dcf_numbers.json or the CSV, or cites a fact `[F#]` that lists
   `used_for: ttm_rejection` and is not third-party only.
   - make_score refuses a 5.7 STALE_FY run whose base is the median or a declared
     `base_override` pin while ttm.json holds a TTM for its latest FY, when the reason is
     missing or does not qualify. The payable pin (`--base-judgment`) is exempt.
   - It refuses the field beside a TTM pin, or with nothing to reject.
   - It refuses a rejected TTM it cannot price: a ttm.json from before engine 5.7, or one
     built with an override judgment.json no longer declares. Rerun ttm.py.
   - It replays the final configuration with `--ttm` and records both bases (base OE/share,
     weighted IRR, tier) in score.json `base_alternatives`, the registry and key_numbers.md
     "Base alternatives". Quote the rejected TTM from there, never retyped.
   - The field is make_score's alone: editing it needs no engine rerun.
   - A declared 6-K bridge may be rejected the same way: keep `interim_bridge` declared and
     add `ttm_rejection_reason`.
   **No TTM: ttm.py exits 3 (default Q14, main agent 2026-10-21, pending Andrew).** ttm.py
   exits 3 when it cannot build the TTM (a leg with no fact to build it from, such as no 10-Q
   since the fiscal year end). It prints one line: "ttm.py: cannot compute TTM for
   <T> (CIK …): …". Copy that line into judgment.json `ttm_unavailable_reason`, verbatim: the
   whole line and nothing else, no words of your own around it.
   - make_score refuses a STALE_FY 10-K median or pin run with no TTM for its FY without it.
   - It checks the quote against ttm.py's own messages for this ticker, CIK and fiscal year.
     It also checks it against the run's own financials_history.csv: a "no annual (FY) fact"
     the latest FY contradicts is refused.
   - ttm.py writes nothing when it exits 3, so a ttm.json from an earlier run can stay beside
     the run. When make_score cannot price that file (it predates engine 5.7, or used an
     override judgment.json no longer declares) and the rerun exits 3, the same quote stands
     for it. make_score then records the old file as not computed, and no rejection reason is
     needed.
   - At a 20-F / 40-F filer the field is refused: `interim_bridge_declined` (below) records
     why no TTM exists there.
   **20-F / 40-F filers: the declared 6-K interim bridge (engine 5.7, Andrew's ruling R2).**
   - Open the latest 6-K interim report with a condensed cash-flow statement. Run
     `python3 _system/ttm.py <T> --interim-draft <6-K accession>`: it prints a draft from the
     6-K's XBRL and writes nothing.
   - Complete `interim_bridge` in judgment.json (schema:
     `_system/examples/interim_bridge.example.json`). Every interim leg is `{value, kind,
     source {accession, document, page | null, section}, snippet, reason}`. The snippet is the
     report's own words, at most 24, and shows the figure.
   - A leg the report does not print is kind `estimate` with a `method`: fy_prorated,
     comparative_carried, combined_in_ppe, fy_diluted_count, or other + method_detail.
   - Declare `like_for_like`: is the comparative restated? List every acquisition, disposal,
     demerger and discontinued operation in the window with its resolution. A change declared
     `material: false` carries a revenue_share below 5% and its source, whatever its
     resolution. `same_business_perimeter` resolves a demerger only.
     `comparatives_re_presented` needs `comparative_restated` and
     `restatement.fy_leg_consistent` true.
   - Declare the per-period ECB rates `ttm.py` prints. The bridge also needs judgment.json
     `ads_ratio` (step 8 (d); 1 when the ordinary shares trade directly). It must be the ratio
     the engine applied, or the bridge refuses ([IB-ADS]).
   - Then run `python3 _system/ttm.py <T> --interim` and pass `--ttm` in the final run. Quote
     key_numbers.md's "Interim bridge" section. Do not re-declare its leg values as facts.
   - A 6-K without XBRL (EDGAR isXBRL 0 — TFII's, FUTU's) bridges too. Every filing leg is
     then verified by its snippet only. ttm.py does not read that report's period from EDGAR
     (a non-XBRL 6-K's reportDate is its cover date): the current interim must have ended
     before the report's filing date.
   - When no bridge is possible, declare `interim_bridge_declined {reason (with a number),
     report {form, accession, document} | null}`. make_score refuses a 5.7 STALE_FY 20-F /
     40-F run with neither (default Q7, main agent 2026-10-21, pending Andrew). That includes
     a hand-built 6-K pin (`base_override`, plain or `iprd_amortized`): re-declare it as
     `interim_bridge`. Only the payable pin is exempt.
   - `ttm.py --interim` exits 3 on any rule (the message lists every `[IB-*]` code) and 4 on
     a fetch failure (retry). make_score re-runs the same rules on the declaration. It
     refuses one changed after `ttm.py --interim` ran: after any edit to `interim_bridge`,
     rerun `ttm.py <T> --interim` and the final engine pass.
   - Resolve `TTM_DECLARED_INTERIM` and `ANNUAL_FROM_INSTANCE` by name.
     `ANNUAL_FROM_INSTANCE` (any annual form: 10-K, 20-F or 40-F) means the engine read the
     latest FY from the filing's own XBRL instance (EDGAR companyfacts lacked it). The engine
     writes `<T>/annual_instance.json`,
     a committed SEC file; make_score refuses the run when that file is missing or no longer
     matches the run. It also refuses a run whose EDGAR reads did not complete ("the engine run
     could not complete its EDGAR reads": the submissions document or the instance fetch
     failed) — rerun the engine when EDGAR answers; never score around it.
   **ttm.json is bound to the run.** (Codex review round 23 of PR #47) Regenerating ttm.json — rerunning ttm.py after a new 10-Q,
   a shares override or a split — means rerunning the engine before make_score. Every run whose
   base reads ttm.json (`--ttm`, or a `--base-oe-ps` pin that is not declared built on FY figures —
   round 25 of PR #47) records what it read from ttm.json (`ttm_inputs` in
   dcf_numbers.json: `ttm_oe_per_share`, `ttm_shares_diluted`, `ytd_current_period` and
   `ttm_input_hash` over its input legs), and make_score refuses a ttm.json that no longer gives
   it ("ttm.json changed after the engine run — rerun dcf_engine.py"), even when the base still
   matches within 0.1%: the acquired-IPR&D share denominator and current-YTD window come from
   ttm.json too. Warnings and an override's source text do not count. (Codex review round 26 of
   PR #47) A pin is ttm.json's figure only within 0.1%, and a $0.00 TTM base only at exactly 0:
   pass `--ttm` (or the exact figure), never a number near it. (Codex review round 30 of PR #47) A
   TTM base's acquired-IPR&D figures are per share on ttm.json's `ttm_shares_diluted`, never the
   latest-FY count: when ttm.json carries no positive count (missing, null, 0, negative, not a
   number) the engine refuses a TTM run whose window holds an acquired-IPR&D charge, a charge
   awaiting its cash-flow check or charges in 2 or more of the last 3 FY (`BAD_TTM_SHARES`, exit 3)
   — rerun ttm.py (it always writes the count beside `ttm_oe_per_share`), then the engine.
   `BASE_DIVERGENCE`: say which base is distorted and why. `NI_OCF_DIVERGENCE`: find the
   one-off (an acquired-IPR&D expense added back in OCF is not "OCF unaffected": it is
   `ACQUIRED_IPRD_CHARGE`'s, below). `BASIS_BREAK_SUSPECT`: name the divestiture / M&A / restatement and pick growth
   inputs that do not straddle it. `HIGH_NET_DEBT` / `BIG_NET_CASH` / `DEBT_TAGS_BLANK`
   (5.4: no debt tag found — net debt is unknown, not zero): state the balance sheet from
   the filing. `SHARES_FALLBACK` (5.4): history years on a non-diluted count — note it.
   `IRR_AT_FLOOR` (5.4): the price is beyond the model's range; the IRR reads "at most
   ~3%". `TIER_BAND` (5.4): bear and bull tiers differ — size to the bear end.
   `SECTOR_MODEL_MISMATCH`: confidence low; the ranking lists the name under sector misfits.
   It fires on the universe sector OR the EDGAR SIC (engine 5.7; dcf_numbers.json
   `sector_model` says which). A present SIC outside 6000-6799 and outside every misfit range
   sets a Finance / Real Estate / Utilities universe sector aside, so no flag fires (default
   Q1 (b), main agent 2026-10-21, pending Andrew). make_score publishes the tier one notch
   below the numbers tier (the mechanical misfit notch, Andrew 2026-10-19). There is no notch
   on a numbers tier of D or F, or on a `--base-judgment` payable base. On a notched misfit,
   write `misfit_notch_reason` in judgment.json: the payable-earnings measure or the IRR it
   implies, with a number. Leave `tier_override` null unless you downgrade further. On a 5.7
   run make_score refuses a notched misfit without the reason, and an override at or above
   the notched tier (the one exception: the main agent's acquired-IPR&D share-count
   override below, which may sit at it).
   `MOAT_TREND_HOLD` (5.7): the run held growth 0 years (moat eroding) or 3 (widening)
   instead of 2. For eroding, name the measured decline (key_numbers.md "Trend test"). For
   widening, say why it is not a cyclical upswing or a recovery from a trough.
   **Insurer payable-earnings base (Andrew, 2026-10-19):** at a P&C insurer or reinsurer
   whose filings print **operating income (loss) available to common shareholders** (the
   non-GAAP line in every quarterly earnings release and the 10-K MD&A), the OCF base is
   not the owner's earnings: consolidated OCF capitalizes the reserve build (policyholder
   float) and the cash earned by consolidated third-party-capital vehicles, so it can run
   2× or more above what common shareholders earn (RNR: OCF base $77.78/sh vs $27.21/sh
   through-cycle operating income to common; Tier S by numbers, where the payable base
   prints C). The mechanical misfit notch (one tier, engine 5.7) cannot bridge that gap. For these filers
   the worker declares in judgment.json:
   `base_override: {basis: "payable_earnings_5y", kind: "filing", figures: [5 annual
   amounts in USD dollars, oldest first], shares: <this run's latest shares_diluted from
   financials_history.csv>, value: <average of figures ÷ shares, per ORDINARY share>,
   source: <each year's release or 10-K, with the five figures>, reason}` and runs the
   final pass with **`--base-judgment`** (in place of `--ttm`). The engine recomputes the
   base from `figures` / `shares` (the recomputed figure is what gets recorded and
   pinned), scales it by `ads_ratio` for a 20-F/40-F filer (the pin must be per ADS,
   like the price; `ttm.py --interim` applies the ADS ratio itself: its `ttm_oe_per_share`
   is per ADS, its `ttm_shares_diluted` the ordinary count), records the construction in dcf_numbers.json (`payable_base`, with
   the filer's EDGAR SIC) and refuses the run (BAD_BASE_OVERRIDE, exit 3) when the
   declared `value` does not reproduce to the cent, `shares` is not exactly this run's
   latest diluted count, the filer's series were FX-converted (the rule is for USD
   filers; a non-USD P&C filer escalates `NEEDS_MAIN_AGENT`), or EDGAR's SIC for the
   filer is not a P&C code (6331 fire, marine & casualty; 6351 surety) — the scope is
   the industry code, not the worker's say-so. A declared `base_override` with `basis`
   that the final run was not pinned through is refused by make_score, never silently
   unused. The registry's `base_override` event carries the override's own measured
   impact (engine-native median base and IRR with field overrides on → pinned payable
   base and IRR, tiers both ways), since the payable pin is the material judgment call
   on these names. make_score checks the declaration figure for figure against the
   engine's record and key_numbers.md prints the five exact figures, the average, the
   share count and the pinned base — quote the construction in analysis.md from there,
   never retyped from the filing. Five-year average, not 3-year median, because a
   catastrophe cycle is longer than three years and a benign window would otherwise set
   the base. This filing-sourced base is the one standing exception to clause (c) in
   step 8, authorized by the main agent. With it in force the mechanical misfit notch is
   **not** applied (score.json `misfit_notch.not_applied: payable_base`; no
   `misfit_notch_reason` needed). A `tier_override` below the numbers tier on top of it is
   refused as double-counting. The alert-gate misfit suppression and the low-confidence
   grade stay. Life insurers, banks and REITs, and any filer without that printed line, get
   the mechanical notch.
   `FX_CONVERTED` / `USD_TRANSLATIONS_USED` / `ADS_RATIO_*`: note the basis.
   **Acquired IPR&D (engine 5.6 — Andrew's 2026-10-19 decision: the one-time deduction, cash preferred, the
   5% flag, recurrence and the impairment non-goal; the no-cliff deduction, the cash-flow check and the
   amortized declaration are main-agent / review additions awaiting his ratification).**
   `ACQUIRED_IPRD_UNCONFIRMED` (fixer review round): the period's charge was expensed with no us-gaap
   investing cash tag, and companyfacts cannot show where the payment went — NOTHING is deducted for it and
   make_score refuses to score until you resolve it. Open that 10-K's (or 10-Q's) cash-flow statement
   (EDGAR filing index → FilingSummary.xml → the cash-flow R page) and declare in judgment.json one
   `iprd_cash_flow_check` entry per period the flag names: `{period: <the period end>, window: "fy" |
   "ttm_current_ytd", amount: <the expense as the flag prints it>, presentation, source: <accession, R page
   and the exact line(s)>}`, presentation `added_back_paid_in_investing` when operating activities add the
   charge back as non-cash and investing activities show the payment (HALO: "Acquired in-process research and
   development expense" added back, "Acquisition of in-process research and development" in investing —
   deducted), `inside_operating_cash_flow` when there is no add-back (NBIX FY2023–25 — the cash went out
   through OCF, which OE already carries; not deducted), `paid_in_shares` when it was added back as a non-cash
   stock payment with no investing outflow (the dilution is in the share count; not deducted),
   `paid_in_intangible_capex` when the payment sits inside an intangible-purchase line the engine sums into capex
   (`PaymentsToAcquireIntangibleAssets` and the like — cite that line; OE already charged it: excluded
   `already_in_capex`, and not applied, the period still gated, when the run's capex intangible leg for the period
   is under 98% of the charge — Codex review round 8 of PR #47: the engine no longer infers this from the leg's
   size, which only adds a `capex_overlap_note` asking you to look). Rerun the
   engine; quote the line in analysis.md. Never guess: a filing you cannot read is `NEEDS_MAIN_AGENT:
   iprd — cash-flow presentation unknown: <period> <amount>`. (Codex review round 12 of PR #47) A cash-basis
   period (the cash tag is filed) needs no check for its own deduction — its cash outflow is deducted — but when
   its expense exceeds its cash and the filing shows the rest paid in shares, declare `paid_in_shares` for it too
   (amount: the filed expense): the residual is then recorded `residual_paid_in_shares` and never accrued as an
   unpaid cash balance, so no later cash-only payment is deducted against it. A `deferred_payment` period that
   carries `deferred_payment_assumption` was matched against a residual nothing declared: say in analysis.md how
   that residual was settled (cash later: the deduction stands; shares: declare `paid_in_shares` and rerun).
   A check's amount is the filed expense, within $1 (Codex review round 14 of PR #47): one that is not is never
   applied (`cash_flow_check_mismatch` on the period) and make_score refuses the run whatever the period's basis —
   correct the amount, or remove the entry if the period needs no check. (Codex review round 21 of PR #47) An
   expense filed only in a currency with no FX rate, beside a usable cash outflow (the period's `expense_fx_note`
   and make_score's refusal show the native figure, e.g. `100,000,000 EUR`), is declared in its own unit: `amount` the native figure and `unit` its
   unit (`"EUR"`); a matching `paid_in_shares` check then records the residual settled in shares
   (`residual_paid_in_shares_unknown_usd`). A `unit` is optional elsewhere and, when named, is `"USD"`.
   A check whose period has left the
   window has no record and still carries over (step 2). On a cash-basis period (Codex review round 15 of PR
   #47) a matching check declaring `inside_operating_cash_flow` or `paid_in_intangible_capex` contradicts the
   investing cash tag the engine deducts: it is recorded `cash_flow_check_inapplicable` and make_score refuses
   the run, naming the presentation — remove the entry (the period needs no check for its own deduction) or
   reconcile it with the cash-flow statement and rerun; `paid_in_shares` is read there as above.
   (Codex review round 22 of PR #47) Changing an IPR&D declaration means rerunning the engine before
   make_score: adding, removing or editing any `iprd_cash_flow_check` or `iprd_deferred_payment` entry, or
   `base_override`'s `basis`, `basis_window` or (basis `iprd_amortized`) `value` / `native_base` / `figures` /
   `shares`. The engine records a hash of those inputs as it read them (`iprd_judgment_hash` in
   dcf_numbers.json) and make_score refuses a judgment.json whose inputs no longer hash to it ("judgment.json
   changed after the engine run — rerun dcf_engine.py"): a check added after the run can change the deduction
   while leaving no trace on the period (a `paid_in_shares` check on a cash-basis period stops a later cash-only
   payment being deducted against the residual). Entry order, `20000000` vs `20e6` and the text of fields the
   engine never reads (a plain pin's `source` / `reason`) do not count.
   `ACQUIRED_IPRD_UNCONVERTED` (Codex review round 3 of PR #47): the charge was expensed only in a currency the
   engine holds no FX rate for, with no usable us-gaap cash fact — NOTHING is deducted, the tier is the
   UNADJUSTED one, and make_score refuses the score whatever judgment.json says. Block the folder
   `NEEDS_MAIN_AGENT: currency — ACQUIRED_IPRD_UNCONVERTED: <period> <native amount and currency>`; it is
   scored once the engine can convert the charge. The same flag (Codex review round 4 of PR #47) names a
   payment on the cash tag, with no acquired-IPR&D expense in its period, filed in a currency the engine has
   no rate for even after fetching one for its date, that could settle the window's unpaid remainder or a
   charge expensed before the window (`cash_native` on the period): block the folder the same way,
   `NEEDS_MAIN_AGENT: currency — ACQUIRED_IPRD_UNCONVERTED: <period> <native amount and currency>`. So does
   (Codex review round 6 of PR #47) a period's cash outflow beside a positive expense when that cash fact cannot
   be converted: the cash is the preferred amount, so the expense never stands in for it and nothing is
   deducted for the period — block the folder the same way. So does (Codex review round 8 of PR #47) a later cash
   payment, with no expense in its period, after a charge expensed in a currency with no rate (the engine first
   fetches the expense period's rate; with none it deducts that period's USD cash but cannot know what is still
   unpaid): the period carries `unconverted_remainder_of` — block it the same way, whether the later payment is
   filed in USD or (Codex review round 24 of PR #47) in a currency with no rate either. So does (round 24) a
   period where both acquired-IPR&D expense tags are filed positive and one has no FX rate: the two cannot be
   compared, so the engine records `expense_tags_conflict` with each tag's native figure, unit and USD value and
   `expense_tag_unconverted`, applies no `iprd_cash_flow_check` there (`cash_flow_check_not_applied`) and deducts
   nothing for the period — block it `NEEDS_MAIN_AGENT: currency — ACQUIRED_IPRD_UNCONVERTED: <period> <tags,
   native amounts and currencies>`. While the folder is blocked, reprice.py and the site
   never show live figures for the refused run (`live_withheld` reason `iprd_unresolved`; since Codex review
   round 11, any run make_score refused or has not yet scored: reason `score_not_from_this_run`). A non-USD
   fact of exactly 0 needs no rate (Codex review round 13 of PR #47): it reads as $0, never `non_usd_no_rate`.
   A negative one needs none either (Codex review round 20 of PR #47): it is a reversal, excluded `negative` with
   its `expense_native` kept, and its period's cash is matched, listed or gated as beside a USD negative fact (a
   `deferred_payment` with `expense_reversal_note` follows the round-14 rule in AGENTS.md); only a positive fact
   with no rate is `non_usd_no_rate`.
   When one tag is filed for one period in more than one unit (Codex review round 15 of PR #47), a positive fact
   in any unit outranks a zero one — converted at the FX pass's rate or one fetched for its date, else the period
   is excluded `non_usd_no_rate` and the flag above applies — and two positive facts that disagree after
   conversion (by more than the engine's unit-agreement tolerance, `IPRD_UNIT_TOLERANCE`: max($1, 1% of the
   larger)) are both recorded on the period (`unit_conflict`, `unit_conflict_note`)
   with the USD one used: reconcile the units against the filing in analysis.md. Since Codex review round 16 of
   PR #47 a unit filed only in quarters is tiled beside another unit's exact FY fact (so it is compared, or
   recorded as `partial_coverage`), and a cash-only period (a deferred payment, an unconverted payment, an
   `ignored_cash_only` entry) carries its cash tag's `unit_conflict` too: reconcile those the same way (since
   Codex review round 17 of PR #47 also on the record a declaration builds from an `ignored_cash_only` payment).
   A unit that tiles a period to $0 no longer hides another unit's positive partial facts: they are
   `partial_coverage` (round 17).
   `ACQUIRED_IPRD_PARTIAL_PERIOD` (Codex review round 11 of PR #47): an acquired-IPR&D tag is filed for only
   part of a window period — a 10-Q's nine-month figure with no FY fact in the 10-K (SMMT FY2023), or a quarter
   alone — and no set of three-month / year-to-date facts tiles the period, so NOTHING is counted for that tag
   there (`iprd_adjustment.partial_coverage` lists the facts found). (Facts that DO tile it are summed and the
   period carries `context_basis` `aggregated_quarters` with the contexts used; quote them in analysis.md.)
   Read the filing for the period's full figure and state it in analysis.md with its effect on the IVs and
   IRR; if a material charge owner's earnings never saw is missing from the deduction, block the folder
   `NEEDS_MAIN_AGENT: iprd_partial_period — <period> <figure>`.
   `ACQUIRED_IPRD_CHARGE`: in-process R&D bought in
   an asset acquisition was expensed in the base window (ASC 805) — the expense is added back in OCF and
   the payment is not capex (the cash tag, or your cash-flow check), so owner's earnings never saw it. The engine deducts the charge ONCE: window
   total ÷ the base's share count (× `ads_ratio`) comes off every scenario's IV and is added to the price
   every IRR is solved at; the base is never cut. The flag fires at ≥ 5% of the base OE total, but the
   deduction applies to any qualifying charge (no cliff). key_numbers.md's "Acquired IPR&D adjustment"
   section prints each period (amount, cash or expense basis, tag), the total and per-share charge, the
   weighted IVs before → after at 15/20/25% and the weighted IRR before → after — quote them from there.
   Resolve it in analysis.md with: the amount, the deal (the acquired company or asset and the 10-K note),
   the consideration mix (cash vs stock — stock is already in the diluted count; the engine prefers the
   `PaymentsToAcquireInProcessResearchAndDevelopment` cash figure when filed), and the recurrence assessment
   (a one-off deal, or the way this company buys its pipeline). On a 5.7 run the consideration figures (cash
   paid, transaction costs, contingent milestones, the investing line) are `filing` facts in facts.json. The
   IPR&D declaration's own values (the `iprd_deferred_payment` amounts, `contingent_total`,
   `iprd_cash_flow_check` amounts) are already in dcf_numbers.json: quote them from the Acquired IPR&D section,
   never re-declare them. key_numbers.md says so on the period line ("declare the consideration in facts.json,
   kind filing"). `ACQUIRED_IPRD_RECURRENT`: charges in 2 or
   more of the last 3 FY (material). A year counts by its own acquired-IPR&D expense, paid that year or
   accrued and paid later, never by its cash timing (Codex review round 27 of PR #47); cash that settles an
   earlier year's charge, with no expense of its own, is not a new charge year, so one deal expensed once
   and paid in installments is one year. A year counts whatever its cash presentation too (Codex review round
   28 of PR #47): paid in shares, inside operating cash flow, inside intangible capex, awaiting its cash-flow
   check or with no FX rate, it is still a charge year (those presentations still deduct nothing). "Material"
   is the recurrence gate's own figure: the counted periods' acquired-IPR&D expense (the current-YTD leg's too
   on a TTM base, less any part declared an installment) against the base OE total, never the cash deducted —
   key_numbers.md prints it on its "Recurrence" line; a counted period whose acquired-IPR&D expense has no
   USD figure reads as material (a known USD expense beside cash with no FX rate is read).
   So the flag can fire with little or nothing deducted (deals paid in stock, inside OCF, or not yet paid):
   resolve it the same way. The engine does not amortize: either justify the one-time treatment in
   analysis.md (why the next three years will not repeat it), or declare the amortized base of step 8 and
   run the final pass with `--base-oe-ps <its value>`. The amortized base carries only the FY charges the
   window deducted (the cash), not the expense the gate measured — the flag names both; when nothing was
   deducted in the last 3 FY there is nothing to amortize (the engine refuses the declaration,
   `BAD_BASE_OVERRIDE`) and the flag asks only for the recurrence assessment in analysis.md (round 28
   re-verification). **Deferred payments (Andrew's 2026-10-20 ruling, delegated to the main agent, who decided).** A charge that
   is a contingent milestone or other deferred payment on a deal already charged in an earlier period (inside
   the window or before it) is the same purchase, not a second one: it stays deducted (real cash spent on that
   pipeline), but it is not evidence of buying R&D as a habit. Declare it in judgment.json
   `iprd_deferred_payment`, one entry per FY period and deal: `{period: <the FY end>, window: "fy", amount:
   <this deal's part of that period's charge>, deferred_payment_of: {deal: <the deal's name>,
   first_charged_period: <the period end the deal was first charged>, source: <the original acquisition
   filing's accession + section / page showing the contingent milestone or deferred consideration>,
   contingent_total: {value: <the deal's unrecognized milestones / deferred consideration, USD>, source:
   <accession + section / page disclosing that total>}}}` (the per-deal cap — the main agent's decision on the
   review's open item, delegated by Andrew 2026-10-20: required, declared once and identically on every entry of
   the deal). Only FY
   periods count toward recurrence, so a current-YTD charge is not declared (window `ttm_current_ytd` is
   refused): declare it once it lands in an FY. A period paying milestones of two earlier deals takes one entry
   per deal. When the period's entries sum to its whole charge it leaves the recurrence count
   (`recurrence_excluded: "deferred_payment_of"`); a partly deferred period still counts. A period that
   expensed the charge with $0 cash (paid in a later year) counts by that expense, so its whole charge is the
   expense (Codex review round 27 of PR #47; the later cash is still deducted once, as the settlement of the
   window's unpaid remainder; round 28: the same when its residual is declared paid in shares). Whatever its
   cash, a charge year's whole charge is the larger of its cash and its own expense (round 28 re-verification):
   $1 or $20M paid in the year on a $100M acquisition is a part, so declaring that cash leaves the year
   counted; and a declared part comes first from the cash beyond the period's expense (an earlier deal's
   settlement), so a new deal expensed beside it still counts in full. A year whose whole charge has no USD
   figure — its own expense, or its cash, filed in a currency with no FX rate (even fetched), or an expense tag
   (the parallel one too) or the cash tag also filed in such a currency beside the USD figure the engine used
   (`unit_conflict` with no USD value: EUR 100M filed beside the USD 40M expensed and paid) — cannot be declared
   at all (Codex review round 29 of PR #47): its cash had stood in for the whole charge, so declaring the $40M
   paid on a EUR 100M expense took the year out of the count; the engine refuses any amount there ("names no
   acquired-IPR&D charge … that a declaration can be measured against", the message it already gave a year with
   no usable cash, naming the figure with no USD value — the expense or the cash tag — and its unit) and the
   year stays in the recurrence count — block it `NEEDS_MAIN_AGENT: currency` if the
   year should leave. When every figure converts (Codex review round 29 of PR #47, polish reviews), the year's
   own expense is the largest positive figure on any of its acquired-IPR&D expense tags (the detector tag and the
   parallel one) in every unit filed, and its whole charge is the largest of that expense, every positive
   cash-tag figure in every unit and the cash deducted: EUR 100M at 1.08 ($108M) filed on either tag, or the
   parallel expense tag filed at $108M on its own, beside the USD 40M expensed and paid makes $40M a part (the
   year still counts), $108M the whole, and more than $108M is refused. "Every unit filed" (Codex review round
   30 of PR #47) is every unit that disagrees with the figure used beyond the engine's unit-agreement tolerance
   (`IPRD_UNIT_TOLERANCE`, 0.01: units disagree only when, after conversion, they differ by more than
   max($1, 1% of the larger) — the units `unit_conflict` records); a unit within it is the figure used, the
   same charge translated at another rate (the run's period-end rate is not the filer's): USD 100M beside EUR
   converting to $100.7M is a $100M charge, so declare the $100M the filing states ($100.7M is refused as more
   than the charge), while EUR converting to $102M makes $102M the whole. With three or more units filed, the tolerance applies to their spread: once the largest and smallest converted figures differ by more than it, every unit is recorded and the largest counts. The recurrence figure reads the expense
   side only — the own expense, less only the part of a declaration beyond the whole charge less that expense —
   and the whole charge adds the cash side: with EUR 100M at 1.08 on the cash tag the recurrence figure is $40M
   and the whole charge $108M. The recurrence figure is unknown (read as material) only when the own expense has
   no USD figure: a USD expense beside cash with no FX rate reads that expense (its declarations are still
   refused, its whole charge being unknown). The engine refuses
   (`BAD_IPRD_DEFERRED_PAYMENT`, exit 3): a `first_charged_period` that does not precede the period; one deal
   with two first charges; a first charge inside the window whose record shows no acquired-IPR&D expense of
   its own there (Codex review round 29 of PR #47: cash that settles an earlier charge, a reversal or a $0
   expense is no deal's first charge — name the period that expensed it; an expense accrued with $0 cash, paid
   in shares or filed with no FX rate is one), or whose
   whole charge is itself declared a deferred payment (a deal's first charge is a purchase, not an
   installment); a first charge before the window that companyfacts covers but shows no acquired-IPR&D
   expense fact ending on that date (name the period end of the filing that first expensed it); a source whose
   accession is not from the first charged fiscal year's start year through the year after its end (a two-digit
   accession year 93–99 is 1993–1999, else 20YY; the
   original filing: an 8-K or 10-Q of that fiscal year, or the 10-K that closes it), inside or before the
   window, so the entry survives the first charge rolling out; entries summing past the period's whole charge
   (the largest of its own expense and its cash, in every unit filed that disagrees beyond the unit-agreement
   tolerance: round 29's polish reviews, round 30); a
   missing or malformed `contingent_total`; one deal's entries carrying different `contingent_total` values (or
   sources); one deal's declared amounts, summed across every entry in judgment.json (a rolled-out one
   included), exceeding its `contingent_total`; and (Codex review round 8 of PR #47) a `period` or
   `first_charged_period` that is not a real date; and (Codex review round 9) a `period` older than the window
   that is not one of the filer's fiscal-year ends (a quarter end, any other date: name the FY end of the 10-K
   that recorded the payment). make_score also records each deal's lifetime in the registry
   (`iprd_deferred_payment` event: paid_to_date and every period ever declared) and refuses a run whose
   declarations for the deal sum below that paid_to_date (an entry deleted or shrunk) or whose lifetime —
   max(the declarations on recorded periods, paid_to_date) + newly declared periods — passes the contingent_total.
   Since Codex review round 10 every period the event recorded is immutable: make_score refuses a declaration that
   omits a recorded period or declares it more than $1 apart from the recorded amount (shrunk OR grown), naming the
   period, and the event keeps the recorded amounts (only a new period is added). Declare a recorded period exactly
   as recorded; never move an amount from one period to another (that could make another period wholly deferred
   and drop it from the recurrence count). A filing that restates a paid milestone is NEEDS_MAIN_AGENT.
   Never edit the registry's `iprd_deferred_payment` events by hand: since Codex review round 28 of PR #47
   make_score refuses the whole registry ("restore it from git"), naming the entry, its ticker and the field,
   when any such event — for any ticker — has a ticker or deal that is not a non-empty string (a ticker
   with surrounding whitespace included), or a missing or
   invalid first_charged_period, contingent_total, paid_to_date (a number > 0), periods (a list of {period:
   a real date, amount > 0}, no period twice) or date. Since the round 28 re-verification the same refusal
   covers an entry carrying such an event's fields (deal, first_charged_period, contingent_total,
   paid_to_date, periods) under a misspelt, missing or other `event` name, a lower-case ticker on such an
   event, and any entry that is neither a field override nor an event make_score writes.
   Since Codex review round 9 the recorded deal is fixed by its evidence: a recorded deal's `contingent_total`
   (value, source) and `first_charged_period` cannot change (declare the recorded ones; a filing that revises
   the deal's milestones is NEEDS_MAIN_AGENT), and a later milestone is declared under the deal's recorded name —
   a new name with the same `first_charged_period` and a `contingent_total` cited to the same filing as a recorded
   (or co-declared) deal is refused as a renamed copy (two distinct deals first charged in one period whose caps
   one filing discloses: NEEDS_MAIN_AGENT).
   If both expense tags are filed for a period with different positive values the engine uses the current tag and
   records both (`expense_tags_conflict`): reconcile them in analysis.md against the filing. Never declare a new deal (another counterparty or asset) as an
   installment, and never overstate `contingent_total`: it is the contingent consideration the filing
   discloses for that deal, and a payment past it is a second purchase, a second charge.
   `ACQUIRED_IPRD_UNMATCHED_PAYMENT` (Codex review round 3 of PR #47): a payment on the cash tag with no
   acquired-IPR&D expense in its period, beyond the window's unpaid remainder, at a filer that expensed
   acquired IPR&D BEFORE the window (the flag names those period ends) — possibly the deferred payment of that
   earlier charge, which OE never saw; nothing is deducted for it. Read the filing: if the payment settles that
   charge (deferred consideration, a milestone accrued then and paid now), declare `iprd_deferred_payment` for
   the FY period with `first_charged_period` = that pre-window expense's period end (it must be one the flag
   names: companyfacts must show the expense) and rerun — the engine then deducts the declared amount once (at
   most the payment, within `contingent_total`), cash basis, outside the recurrence count. This is the one
   declaration that changes the deduction. When part of the same payment already settled the window's unpaid
   remainder automatically (Codex review round 17 of PR #47), declare only the rest the flag names: a
   declaration first charged before the window claims that rest (at most it) on top of the automatic part,
   which keeps its own note (`automatic_settlement`, `declared_residual`); one first charged inside the window
   still names the automatic part. Otherwise say in analysis.md what the payment is. A cash-tag-only
   payment at a filer that never expensed acquired IPR&D (MAA) raises no flag and can never be declared.
   key_numbers.md prints the excluded periods;
   quote them in analysis.md beside the recurrence assessment. HALO: the FY2025 10-K discloses $100.0M of
   unrecognized Surf Bio milestones — when one is expensed, declare it (once it lands in an FY) against
   `first_charged_period` 2025-12-31, citing that 10-K (0001159036-26-000024), with `contingent_total`
   {value 100000000, source: that 10-K's accession + the note disclosing the $100.0M of milestones}. Treatment `not_applied_share_count_unverified` (the
   flag says "not deducted — the share count behind the base is unverified": a share-scale defect rescued by
   a pin with no power-of-ten factor): the tier is UNADJUSTED — block `NEEDS_MAIN_AGENT: shares —
   ACQUIRED_IPRD_CHARGE not deducted: <total>` with the charge total; only the main agent may publish it,
   through a `tier_override` whose reason quantifies the hand deduction — the charge per share on the verified
   share count ($) and the adjusted weighted IRR (%); make_score refuses the score without one (Codex review
   round 1 of PR #47). On a sector misfit (engine 5.7) that override sits at or below the notched tier — the
   notch of the recorded numbers tier; make_score refuses it above — and `misfit_notch_reason` is still
   required on a 5.7 run. On a 5.7 run its reason follows the quoting rule of step 8 (the verified share count a
   cited filing fact, the charge per share a calc fact, the adjusted IRR from a saved run). reprice.py never reprices it (no live figures: the hand deduction cannot be replayed —
   round 2). Impairments of previously capitalized intangibles are
   not this flag and are never deducted (that spend went through capex / intangible purchases when made); a
   cash-tag-only year (MAA's development-spend mistag) is never a charge.
   **Engine 5.5 flags (2026-10-19)** — each names its figures; quote them from
   dcf_numbers.json / key_numbers.md. `SHARE_SCALE_SUSPECT`: the filed diluted counts look
   mis-scaled (base OE/share above 20× the price, the latest diluted count outside
   1/100–100× the cover-page dei count — thousands filed as units: NTNX, TEM, VIV — or price ×
   that count outside 1/100–100× of universe.csv's market cap in either direction) but a
   declared pin carries the base. Only one pin qualifies: a `--base-oe-ps <x>` value that
   judgment.json declares as a `base_override` with no `basis` whose `value` equals `x`
   within 0.1%, and that is itself within 20× the price. Name the defect and show the pin's
   construction (step 8 (c)) with the filing check behind it (the 10-K's printed diluted
   EPS); `share_scale` records the evidence and the power-of-ten factor the market cap used
   (none found → the cap is price × the filed count ÷ any ADS ratio: say it is unreliable;
   the pin's power of ten is used only when the median year's count and the latest count
   are on one scale (those two counts are compared; a year between them on another scale
   does not matter) — `share_scale.pin_factor_withheld` names a ratio withheld for a break
   between them, and the cap then uses the latest count as filed; with no cover-page count,
   one the latest count fails by more than 100×, or one that agrees with a latest count on
   the same scale as the median year the 20×-price test found mis-scaled (the cover page is
   then filed in thousands too), `share_scale.leverage_unverifiable` is true and the flag
   says net debt / normalized OE was not computed and HIGH_NET_DEBT / BIG_NET_CASH were not
   tested — state the balance sheet from the filing instead). When the share series breaks scale inside the growth
   window (two adjacent counts among the last four more than 100× apart — VIV), the
   share-count CAGR is an artefact of the units, and so is the OE/share CAGR when its two
   endpoint counts are more than 100× apart: the engine drops them from the growth blend
   and sets the share adjustment to 0 (`share_scale.scale_breaks` /
   `growth_inputs_dropped`; an OE/share CAGR whose endpoints share one scale stays —
   `growth_inputs_kept`; the flag names them)
   — set the scenario growth starts from revenue and the latest prints, and say so.
   `DATA_GAP:shares — SHARE_SCALE`: the same defect with no qualifying pin — no per-share
   figure is reliable and no override covers the gap. It also fires when the pin itself (a
   `--ttm`, `--base-oe-ps` or `--base-judgment` value) is above 20× the price
   (`share_scale.pin_over_price`), however clean the annual counts: check ttm.json's
   `inputs.shares_diluted` and its `warnings` (ttm.py warns when the TTM denominator is
   outside 1/100–100× of the FY diluted count or the cover-page count — a 10-Q count filed
   in thousands). When a `--base-oe-ps` pin was passed
   and rejected, `share_scale.pin_rejected` and the gap text say why (no declared
   `base_override`, a payable-shape `basis`, a value more than 0.1% off the pin, or a pin
   itself above 20× the price). Block `NEEDS_MAIN_AGENT: shares — SHARE_SCALE: <the flag's
   reasons>`. A `base_override` already in judgment.json (a main-agent decision or an
   earlier run's) is honoured when it qualifies: run the final pass with its value as
   `--base-oe-ps <value>` and the gap becomes `SHARE_SCALE_SUSPECT` (the tier then rests on
   that override: make_score closes both alert gates and records the pin's impact in the
   registry `base_override` event — give the declaration a `kind`). Never type a TTM or any
   other per-share figure as `--base-oe-ps` without that declaration — it does not rescue —
   and a `--ttm` or `--base-judgment` pin does not rescue either (both divide by the same
   counts).
   `DATA_GAP:shares — SHARE_CLASS_MISMATCH`: judgment.json declares `share_class_mismatch`
   (step 8) — the filed count is a different class from the traded security. Nothing
   rescues it: block `NEEDS_MAIN_AGENT: shares — SHARE_CLASS_MISMATCH: <the EPS-note
   citation>` and finish (make_score refuses the declaration too).
   **Share classes (engine 5.7, Andrew 2026-10-19/20, R6).** `UP_C_SUSPECT` says the per-share
   figures may cover only the traded class. It fires at a domestic filer (not a 20-F / 40-F
   filer) when noncontrolling interests hold at least
   20% of equity or of consolidated net income (3 FY), the count looks short (the cover page
   counts shares by class, or carries more shares than the diluted count, or the screener's cap
   — universe.csv's own price × the filed count — is at least 1.05× it), and the diluted count
   does not include an exchange of their units. VNOM printed a fake Tier S at 25.05% ($7.9338
   TTM OE per Class A share). Read the equity note's ownership table (units held outside the
   filer) and the EPS note. On a 5.7 run make_score refuses the flag left unresolved: declare
   the classes, or write the reason (below).
   - The noncontrolling holders own units of the same operating business that exchange into
     the traded class (Up-C), or the filed count leaves out another class of the filer's own
     common → declare `share_classes` (step 8 (e)) and rerun `ttm.py` and the engine.
   - The minority is an ordinary interest in subsidiaries (JV partners, a listed subsidiary,
     project equity), or the filed count already includes every class → write
     `up_c_suspect_reason` with the figure that shows it. That figure is the EPS note's diluted
     count including the exchange, or a `shares_override` that already counts every class
     (FPS's 304,699,000 incl. 60,897,000 Class B). Never declare the classes again on top of it.
   - A year whose EPS-note diluted count already includes the units (if-converted) keeps its
     units with `in_filed_count: true`. The engine checks diluted − basic.
   - If the structure collapsed or ended inside the base window, the year it happened in
     declares the class's weighted-average units for that year. Never 0: the class existed for
     part of it. With no printed weighted count, use a `kind: "calc"` day-weighted average of
     two dated, cited counts. Only a year wholly after the event is 0, with `zero_event` and
     the `event_date` written in its source.
   - `SHARE_CLASSES_CAP_GAP` asks whether the screener counts one class only (say so in
     `share_classes.cap_gap_reason`, with the figure), or whether the filed count already
     includes the declared classes (remove them).
   - `SHARE_CLASSES_NCI_GAP` says the declared share of total units is more than 15pp from both
     NCI shares. Check the units, or write `nci_gap_reason`.
   - `SHARE_CLASSES_DECLARED` then names the units per year. Resolve it by name in
     analysis.md, quoting key_numbers.md's share-class lines. Say whether the counts are
     period-end or weighted-average (a period-end count in a year of heavy unit issuance
     understates that year's per-unit OE).
   `SHARE_BASIS_ADJUSTED`: a split ratio filed after the latest FY end, confirmed by a
   post-split cover-page count; the engine multiplied every share count filed before the
   split (CSV `shares_split_factor`), so history, base and price share one basis. Name the
   split (ratio, effective date, the 10-Q that reports it); with a TTM pin, check
   ttm.json's `split_adjustment`. The flag lists every adjusted fiscal year and names any
   year whose count is an `OVERRIDE` ("except FY<y> (OVERRIDE count, not rescaled)"): the
   engine never rescales an override, so a `shares_override` at a split-adjusted filer must
   already be on the post-split basis (step 8) — check it against the ratio and restate it
   if it is not (the engine confirms the split against the latest FILED count, named in
   `share_basis.split.confirmed_against_period`, so a post-split override in the latest
   year does not hide the split). key_numbers.md also prints "Share basis: unconfirmed split fact <date>
   ratio <r> (no post-event cover-page count confirms it) — check the latest 10-Q" for a
   split ratio filed after the FY end that no later cover-page count confirms (no flag, no
   adjustment: history and price may sit on different bases). Check the latest 10-Q and
   resolve it in analysis.md; a split that took effect leaves the per-share base on the
   wrong basis — block `NEEDS_MAIN_AGENT: shares` with its ratio and date. Its "in-history
   split facts" line is informational (splits the annual filing already reflects), but a
   history year sourced from a filing older than the split can still be on the pre-split
   basis (TPL): if the CSV's `shares_diluted` jumps by about the ratio inside the last four
   years, `DILUTION` / `BUYBACK` and the share adjustment are artefacts — say so and set
   the growth starts without them.
   `SHARE_BASIS_DIVERGENCE`: the cover-page count dated after the FY end differs from the
   latest diluted count so that one is more than 25% below the other (dei ÷ diluted outside
   0.75×–1.333×) and no split ratio is filed; the market cap uses
   the cover-page count, the per-share history stays on the filed basis. Find the cause in
   the latest 10-Q: issuance or a merger — say whether the base still fits the business the
   price buys (as for `BASIS_BREAK_SUSPECT`); an unfiled split — the per-share base is on
   the wrong basis and no override replaces a filed count: block `NEEDS_MAIN_AGENT: shares`
   with the split's ratio and date. A split after the latest cover date raises nothing
   (IESC: both counts pre-split) — the research in step 3 must catch it; block the same way.
   `CAPEX_COVERAGE_LOW`: capex below 50% of D&A in each of the last 3 FY at a filer with
   positive PP&E. Reconcile the CSV's `capex` (`capex_tag`, `capex_ppe`,
   `capex_intangibles`) against the cash-flow statement's investing section line by line
   (construction in progress, land-use rights, spectrum, intangible purchases; capitalised
   software is read since 5.7 unless it is filed only as `CapitalizedComputerSoftwareAdditions`
   or an extension tag). Either the engine read the whole capex (an asset-light or acquisition-led
   model — say which, with the line) or a filed capex line is unread: then the base
   overstates owner's earnings and no override adds to a filed value — block
   `NEEDS_MAIN_AGENT: capex — <the unread line(s) and amounts>`.
   `SBC_TAG_RECONCILED`: `AllocatedShareBasedCompensationExpense` exceeded
   `ShareBasedCompensation` for the years listed and was used (JLL: the Share tag carried a
   $2.7M note-level slice of $112.0M). Confirm against the cash-flow statement's stock
   compensation addback; a difference under 1% is tag rounding and needs one line.
   ttm.json's `sbc_reconciled_legs` lists any TTM leg it changed; `used_tags.sbc` names the
   tag the latest year used. TTM SBC never falls below the unreconciled figure: a reconciled
   prior-YTD leg (the one TTM subtracts) that would lower it keeps its
   `ShareBasedCompensation` figure (`sbc_reconciliation_withdrawn_legs`, with a warning), and
   a warning names each leg's tag when only some legs reconcile (a 10-Q often files only one
   tag — JLL) — check each leg against its own filing's stock-compensation line.
   `OVERRIDE_SUPERSEDED_BY_FILED_TAG:capex`: the engine now reads a filed PP&E capex leg in
   years a `capex_override` used to fill, outside 0.5×–2× of the override (WY: capital
   improvements $57M / $52M / $51M beneath a $447M total-capex override); the filed value
   is used there (an override never replaces a filed value), and make_score refuses while
   the `capex_override` is still declared. Reconcile against the cash-flow statement: the
   filed leg is the whole capex line (RBC, CR, IT) → remove the override and re-run the
   engine; the filed leg is only part of capex → the run's capex is incomplete
   (`CAPEX_COVERAGE_LOW` usually fires too) — block `NEEDS_MAIN_AGENT: capex` with both
   figures. ttm.py warns per TTM leg the same way (ttm.json `warnings` and
   `capex_override_superseded_legs`). A newly read filed leg inside 0.5×–2× of the
   override raises nothing: the override simply fills nothing and drops out of
   `overrides_applied` (AMH, UDR) — remove it from judgment.json on that run (an override
   that fills nothing has no effect to carry).
5. **Moat 0–10: sources first, then the evidence (Andrew, 2026-10-19 — a combination of
   Dorsey's framework and the evidence scorecard; engine 5.7).** Name the specific pillars FOR
   and the erosion forces AGAINST — no generic claims.
   **One lever per question.** Risk lives in the scenario probabilities, the bear weight and
   confidence. Growth lives in the growth start. Return on capital lives in the capex inside
   owner's earnings. The moat sets ONLY the fade. Each of these is double counting: a moat
   argued from growth ("users are growing fast, so the moat is wide"); a growth start raised
   because the moat is high; a risk (a lawsuit, a customer loss) carried as a lower moat
   instead of in the probabilities. reach_and_growth scores the size, growth and retention of
   the user / customer base. A growth rate alone lifts it to +1 at most; +2 needs a scale or
   retention fact besides the rate.
   **The scorecard (required on a 5.7 run).** judgment.json `moat_scorecard` is
   `{version: 1, business_type, business_type_reason, sources, pillars, supporting,
   volume_price, moat_divergence_reason, low_roic_reason, high_return_low_moat_reason,
   erosion_rebuttal}` (plus `widening_declined`, below); worked examples are
   `_system/examples/moat_scorecard_*.json`. `business_type` is one of consumer_users,
   enterprise_recurring, consumer_brands_retail, industrial, healthcare, commodity_producer,
   financial_balance_sheet, financial_fee, real_assets. `business_type_reason` says why (a
   revenue share or segment). The filer's SIC can lock the type: make_score refuses a type the
   SIC range contradicts (a mortgage-REIT balance sheet is financial_balance_sheet).
   **Sources first.** Name the source(s) in judgment.json `moat_scorecard.sources`: type and
   subtype from the enum, narrow or wide, and facts (used_for `moat:sources`) or a measured
   metric at +1. The types are Dorsey's intangible assets, switching costs, network effects,
   cost and size advantage; Morningstar's efficient scale; Helmer's counter-positioning;
   Greenwald's customer captivity (the table is in `_system/README.md` §Moat).
   - First-mover advantage, a technology lead, high growth, a large addressable market,
     partnerships and culture are not sources. Score them, with great products, share,
     execution and management, under the four supporting factors.
   - Bad moats (products, share, execution, management) are allowed as supporting factors.
     Presenting them as the moat's source, with no source type named, is P2.
   - The caps: none ≤ 3; one narrow ≤ 6; 7+ a wide or two fact-backed sources; 9+ two wide
     and returns_on_capital +2 sustained. No reason field relaxes a cap.
   - The source rules of README §Moat apply: brand, patent expiry, switching / pillar
     agreement, aftermarket series, efficient-scale competitor count and returns,
     counter-positioning incumbents, captivity series, process lead.
   - A process edge is acceptable as the way a company breaks in (Dorsey). Call it narrow
     and name, in the rationale, the bigger moat it is building toward.
   **The evidence.** `moat_scorecard.pillars` holds the seven declared core pillars:
   pricing_power, retention, reach_and_growth, switching_costs, concentration, erosion_risks
   (−2..+1, with typed `threats`: technology_substitution, reinvestment_away_from_moat,
   subsidized_competitor, patent_licence_expiry, regulation) and customer_regard.
   - Each is `{score, rationale, facts}`, or `{applicable: false, not_applicable_reason}`
     where the business type allows it (README table).
   - Every cited metric is a SERIES of at least 3 periods over at least 12 months in
     facts.json. Third-party-only support caps a pillar at ±1.
   - The four mechanical pillars are measured; they carry only an optional `comment`.
     returns_on_capital prints ROIC, tangible ROIC, ROE and ROA side by side, and make_score
     picks the governing one. industry_structure compares the governing return with
     same-ladder SIC peers. capital_intensity and scale_economics are measured too.
   - `supporting`: product_quality, market_share, execution (−1..+1) and management
     (−2..+1; −2 only for value-destroying reinvestment outside the moat), each with facts or
     N/A with a reason. Their sum ÷ 4 (N/A counts 0), capped at ±1, is added to the core
     evidence. They may be positive with no source, and they never lift the moat past a cap.
   - Where the filer discloses a volume series, declare `volume_price` (required for
     consumer_users).
   **The dry run.** Run `python3 _system/moat_scorecard.py <T>` before the final engine run.
   It checks the scorecard's gates the way that run will (always an authoring check: every gate
   that would refuse the run refuses here). It prints the evidence score, every gate and the
   `--moat-trend` value for the final run. It does not trace the reasons — make_score does when
   it scores the final run — so a reason whose number does not trace passes here and is refused there. For a
   rebutted MOAT_EROSION the printed `stable` assumes the `erosion_rebuttal` passes that trace (a
   number, anchored as below, not a restatement of the trend test); when make_score refuses it,
   fix the rebuttal or drop it and pass `--moat-trend eroding`.
   - Your moat must land within 2 points of the evidence score, or carry
     `moat_divergence_reason` with a number.
   - A moat of 7+ on a governing return below 10% (ROE 15%) or unmeasured carries
     `low_roic_reason`.
   - A moat of 4 or below on 20%+ sustained carries `high_return_low_moat_reason`.
   - An erosion score of +1 under MOAT_EROSION carries `erosion_rebuttal`.
   - Each reason has a number that traces: an engine figure, a key_numbers.md Moat-scorecard
     figure, or a cited `[F#]` fact that lists the reason's tag.
   **Rubric (Andrew, 2026-10-19 — use the whole range).** 0–2 no moat: no source, and returns at or below the cost of
   capital. 3 no source, with decent returns (the supporting factors can reach 3, never more). 4 one narrow source with
   thin evidence. 5–6 narrow: one source; governing return above ~10–15%. 7–8 wide: a wide source or two fact-backed
   sources; governing return ≥ 15–20% through a cycle. 9–10 exceptional: two wide sources; governing return ≥ 25–30%
   through a cycle (returns_on_capital +2 sustained). Today's scores are compressed: 82% of folders sit at 4–6. The
   median governing return at moat 6 is 19.5% and at moat 7 is 29.1% — on returns alone those are 7–8 and 9–10
   companies (moat 4 / 5: 10.6% / 16.0%; plain ROIC proxy at 4 / 5 / 6 / 7: 8.0% / 8.5% / 12.9% / 21.6%); score the
   sources and let the number land there.
   **The fade (Andrew, 2026-10-20, M6).** The moat's LEVEL sets CAP = clamp(2 + 1.3 × moat,
   2, 15) years. Its DIRECTION sets the growth hold before the fade; growth then converges to
   2.5% over CAP years. `moat_scorecard.py <T>` runs the trend test. It looks at the
   governing return AND the margin (gross, else the filed operating margin) over the last
   5 FY. Both down is MOAT_EROSION; both up is MOAT_WIDENING. Each needs a move of 3pp and 20%
   of the starting return, and 2pp of margin. The dry run prints the `--moat-trend` value
   for the final run:
   - eroding → hold 0 (the fade starts in year 1), unless `moat_scorecard.erosion_rebuttal`
     carries a traced number (why this is a cycle, not erosion). The rebuttal must be anchored
     on a cited filing / release / folder fact tagged erosion_rebuttal, or on an engine figure
     outside the trend test (such as the filed history). The trend test's own figures, the
     record's IRRs and values that the hold moves, and the counterfactual IRR trace but never
     anchor: a rebuttal that only restates them is refused.
   - widening → hold 3, only with a fact-backed source and returns_on_capital +1 or better.
     When tangible ROIC governs, plain ROIC must also rise by the same thresholds (an
     acquisition's goodwill shrinks the tangible base, so tangible returns alone can "widen"
     while the return on the price paid falls). When ROE governs, ROA must also rise by them
     (buybacks shrink equity, so ROE alone can "widen").
   - widening never applies to a commodity producer, checked on the filer's SIC (mining,
     oil and gas, primary metals, commodity chemicals, pulp and paper, lumber, refining, bulk
     shipping; a SIC-6199 filer booking contract revenue, i.e. crypto mining and treasury
     companies; an unknown SIC fails). The one exception: `business_type_reason` quotes a
     cited cost-position fact (cost-curve position, cash cost per unit vs peers; metric one of
     `moat_scorecard.COST_POSITION_METRICS`, used_for business_type_reason). A declared
     `commodity_producer` business type is never exempted. A commodity price move never
     counts.
   - Decline a widening in `moat_scorecard.widening_declined` when the rise is a cyclical
     upswing or a recovery from a trough (`WIDENING_FROM_TROUGH`: the first-two-year return
     sat below the cost-of-capital line). It is a sentence and needs no number, because it
     only lowers the value.
   - anything else → hold 2. Scenarios that start at or below the terminal rate always hold 2.
   The hold carries the direction. Do not also cut the moat score or the growth start because
   the moat is eroding (one lever per question). `--gterm` only with a written reason.
6. **Five scenarios** summing to 100%. Defaults 10/25/30/25/10; growth-start offsets
   −12/−5/0/+5/+12pp vs the engine's blended start; OE multipliers 0.75/0.90/1.00/1.10/1.25.
   Adjust to THIS company's evidence with written reasons. **Sanity check:** compare every
   scenario's growth start with the actual recent prints (latest FY, TTM, latest quarter
   YoY, guidance). A start below what the company just printed — especially bull — needs a
   written reason; equally, if the blend hit the 35% cap on inflection artifacts, recalibrate
   downward with the reason written. User growth informs the growth start through the
   decomposition. The moat sees the user base only through reach_and_growth, which scores its
   size, growth and retention. Never raise reach_and_growth above +1 on the same growth rate
   that sets the growth start, and never raise a growth start because the moat is high.
   Final run:
   `python3 _system/dcf_engine.py <T> --moat <m> --moat-trend <eroding|stable|widening> --probs <5> [--offsets <5>] [--mults <5>] [--ttm | --base-oe-ps <x> | --base-judgment] [--gterm <x>] [--cik <cik>]`
   (`--base-judgment` is the insurer payable-earnings pin from step 4; a declared
   `base_override` with `basis` that the final run does not pass is unused and make_score
   refuses the score; `--base-oe-ps <x>` pins a declared `base_override` value from
   step 8 (c), the only pin that carries a `SHARE_SCALE_SUSPECT` base, and the
   `iprd_amortized` base of step 8). Pass the `--moat-trend` value the moat_scorecard dry run
   printed (step 5). make_score refuses a different one, and the engine exits 5 on a value
   that is not a trend.
   Exit 4 here → block as in step 2 and finish.
7. **Write `analysis.md`** in APP's shape:
   - what it is;
   - owner's earnings (both definitions, which base and why, ttm.json legs quoted if TTM;
     under STALE_FY both bases from key_numbers.md "Base alternatives" when the TTM is
     rejected, or ttm.py's exit-3 message when no TTM exists);
   - MOAT: score, FOR/AGAINST, CAP, and from key_numbers.md's Moat scorecard the sources and
     caps, the governing return beside ROIC / tangible ROIC / ROE / ROA, the industry rank,
     the evidence score with the supporting adjustment and the gap, the flags, and any
     divergence / low-return / reverse / erosion reason. For moat_for / moat_justification
     name the source type behind each point. A bad-moat point is support: mark it
     `(supporting: <factor>)`;
   - five-scenario table + weighted result + diagnostics;
   - FLAGS resolving every flag;
   - thoughts / method range / hurdle-clearing price;
   - verdict sized to the conservative end.
   Quote declared facts as key_numbers.md renders them. A figure you derive from two others
   (a premium to IV, a midpoint, a CAGR, a share of OCF) is a `calc` fact in facts.json, not
   prose arithmetic.
7b. **Write `facts.json`** (engine 5.7; schema and worked examples: `_system/examples/facts/`).
   - Ids are F1, F2, ….
   - Kind `folder`, with a path `<file>:<selector>`, whenever a folder file holds the number
     (statements.json, fundamentals.json, segments.json, profile.json, ttm.json,
     financials_history.csv). Never another kind for it: make_score refuses a filing /
     release / third-party fact that repeats a folder figure for the same period (its
     `metric` and period match, or a same-period folder leaf matches at 4+ significant
     digits); a shorter match with no `metric` is printed as a "possible folder duplicate"
     in key_numbers.md, not refused — declare it kind `folder` anyway.
   - Kind `filing` (accession + section), `release` (8-K / 6-K accession + exhibit) and
     `third_party` (https URL, publisher, date) each carry the snippet.
   - `type`: guidance / estimate for forward figures; `metric` for a KPI tracked over several
     periods (a series — the moat scorecard reads series); `event` for a dated term carrying
     a number; actual otherwise.
   - A derived figure is a `calc` fact (it carries `calc`; make_score reproduces it, and its
     kind is its weakest operand's).
   - Third-party facts are for scenarios and context only.
   - Names that look like numbers ("Paragon 28") go in `not_quantities`.
   - A count's `unit_label` is a noun with no digits (stores, MW).
   - Each fact a reason cites lists that reason's tag in `used_for` (step 8).
8. **Write `judgment.json`** with exactly: name, sector, moat_score, moat_justification,
   moat_for (short pillar strings), moat_against, probs_used (5, engine order), one_liner
   (quality + moat + why it does/doesn't clear 15% + hurdle price if below), confidence
   (low/medium/high — never high with WIDE_SCENARIO_SPREAD or unresolved flags),
   tier_override (null unless the final tier must differ from the published tier, reason in
   analysis.md; on a sector misfit the published tier is already the notch, and an override
   may only go below it), tier_override_reason, in_scope_under_40b. Engine 5.7 adds, each
   where its step says:
   - `misfit_notch_reason` — required on a 5.7 run of a notched sector misfit (numbers tier
     S-C, off the payable base); it carries a number (step 4).
   - `moat_scorecard` — required on a 5.7 run (step 5).
   - `ttm_rejection_reason` — only when you reject a STALE_FY TTM (step 4).
   - `ttm_unavailable_reason` — only when ttm.py exits 3 at a STALE_FY 10-K filer (step 4).
   - `interim_bridge` (a 20-F / 40-F STALE_FY filer's declared 6-K bridge; schema
     `_system/examples/interim_bridge.example.json`) or `interim_bridge_declined {reason with
     a number, report}` — never both (step 4).
   - `share_classes` (clause (e) below; with its optional `ack_reason`, `nci_gap_reason`,
     `cap_gap_reason`, `diluted_gap_reason`, each carrying a number) and
     `up_c_suspect_reason` (step 4).
   - `capex_unlisted_ack` `{"<tag>": "<reason with the figure>"}` (step 8, capex overrides).
   **Reasons cite facts (engine 5.7, R3).** On a 5.7 run `tier_override_reason` and every
   other reason field (a plain `base_override`'s reason / source included) cites the facts it
   rests on as `[F#]`.
   - Every number in it is an engine figure or a cited fact's value.
   - A reason carries at least one number (a plain `base_override`'s text is exempt, and so
     is `moat_scorecard.widening_declined`, step 5).
   - It never rests on third-party facts alone.
   - Each cited fact lists the field's `used_for` tag (`tier_override`, `base_override`,
     `misfit_notch`, `ttm_rejection`, `share_classes`, `capex_unlisted_ack`, …).
   - A hand base pin (`--base-oe-ps`) may quote its own figure, but that figure never
     supports the pin alone. The reason needs an engine figure other than the pin (the TTM or
     CSV lines it was built from) or a cited filing / release / folder fact tagged
     `base_override`.
   - Numbers inside your own `ads_ratio.source`, an override's source or a share-class
     source are your text, not engine figures, even though the engine repeats them in its
     flags.
   - The main agent's unverified-share-count IPR&D override (step 4,
     `not_applied_share_count_unverified`) follows the same rule. The verified share count
     is a cited filing fact. The per-share charge is a cited calc fact (the run's
     `iprd_adjustment.total` ÷ that count). The adjusted weighted IRR comes from a saved
     method run of an engine run pinned at the hand-adjusted base
     (`check_quotes.py --save-run <T> <label>`).
   Optional overrides `capex_override` /
   `sbc_override` / `shares_override` `{value, source, reason, kind}`. Engine 5.7 adds the
   optional keys `shares_override.share_basis` (`traded_class` | `all_classes`),
   `capex_override.software_included` (below),
   `interim_bridge.legs.shares_diluted.current_interim.share_basis`, and
   `base_override.share_basis` (`total_units`) / `share_period`.
   **Bounded override authority (Andrew, 2026-10-14):** (a) kind "filing" — a figure from
   the company's own filings for the missing period(s); source cites form, period and
   location. (b) kind "estimate" — ONLY within 0.1×–10× of the last engine-filed value for
   that field; name the anchor. **Depreciation-anchor exception (Andrew, 2026-10-18):** for
   capex only, when no capex value was ever filed for the company — so no last-filed capex
   exists to anchor the band — a capex estimate may anchor on the filer's filed
   depreciation instead (the estimate still sits within 0.1×–10× of that depreciation
   anchor), and analysis.md must state the anchor explicitly: that the estimate anchors
   on filed depreciation because no capex was ever filed. With no filed capex the engine
   marks the estimate out-of-band by construction, so the override must also carry an
   `ack_reason` saying exactly that (the existing out-of-band acknowledgment — ALLY's
   scored capex override is the worked example); without it make_score refuses. Any
   other field, or any capex case where a capex value was filed at some point, follows
   the plain rule above or escalates. (c) `base_override` — ONLY built exclusively from figures
   THIS run's dcf_numbers.json / ttm.json / financials_history.csv printed, construction
   quoted in analysis.md. A plain one (no `basis`) pinned through `--base-oe-ps` at a value
   that is not ttm.json's `ttm_oe_per_share` also carries `basis_window` (Codex review round
   15 of PR #47; make_score refuses a 5.6 run without it): `{"window": "ttm",
   "ytd_current_period": <ttm.json inputs.ocf.ytd_current_period, copied>}` when the pin was
   built from ttm.json's TTM figures on another denominator (at a declaring filer the per-unit
   TTM base is `--ttm` itself — share_classes — and a total-unit pin also states
   `share_basis: "total_units"`) — the acquired-IPR&D
   window then reads the current-YTD leg whose cash flows are in the base —, `{"window":
   "fy"}` when it was built from FY figures (NTNX, VIV). The engine refuses a `ttm` window
   whose period is not this ttm.json's (BAD_BASE_OVERRIDE, exit 3): after ttm.py reruns,
   copy the new period. The declared window holds even when the pin happens to equal ttm.json's
   `ttm_oe_per_share` (Codex review round 24 of PR #47): `{"window": "fy"}` keeps the FY window
   and the latest FY share count. (d) `ads_ratio` — ONLY when stated in the filer's own 20-F/40-F.
   (e) `share_classes` (engine 5.7, R6) — ONLY counts from the filer's own 10-K / 10-Q
   (balance-sheet parenthetical, equity-note ownership table, EPS note): kind `filing`, or the
   kind `calc` straddle-year average below.
   - The shape: `{basis: up_c_exchangeable_units | multi_class_common, traded_class, reason
     (with a number), classes: [{name, holder, exchange_ratio, ratio_source, periods:
     [{period_end, value, count_basis: period_end | weighted_average, kind, accession,
     source, snippet, …}]}]}`.
   - One entry per class per period. Every class lists the same periods. The declaration
     covers the last 3 FY and, with a TTM base, the current-YTD period end.
   - An explicit 0 only for a class that did not exist at all during the period:
     `zero_event` `not_yet_issued` / `ended`, with the `event_date` written in its source. A
     class that existed for part of the period declares its weighted-average units, or a
     `kind: "calc"` day-weighted average of two dated, cited counts. At least one period is
     above 0.
   - Units already in the filed diluted count carry `in_filed_count: true`.
   - `exchange_ratio` comes from the filing, as filed-count (ordinary) shares per unit —
     never per ADS (`ratio_source` when it is not 1).
   - The units are the economic units the noncontrolling holders own (OpCo units), not the
     voting shares paired with them (VNOM: 164,789,844 Class B but 171,536,228 OpCo units at
     2026-06-30; the Class B count alone is 8 cents off the base).
   - `split_basis` on a period cited from a filing outside the filer's companyfacts when a
     split is confirmed.
   - It replaces a share-basis `base_override` pin: clause (c) never covers a unit count.
     VNOM's 2026-10-16 pin is retired on its re-score (`--ttm` on the declared ttm.json
     reproduces it).
   - A clause-(c) pin built from total-unit engine outputs states
     `share_basis: "total_units"` (and `share_period`, or its `basis_window` sets it). Never a
     filed-basis figure such as ttm.json's `ttm_oe_per_share_filed_basis` or an FY's OE ÷ its
     filed traded count: make_score refuses it (R-4b).
   - An `iprd_amortized` pin on `native_base: "ttm_json"`, or a pin with `basis_window`
     "ttm", needs ttm.json rebuilt on the declaration first (rerun ttm.py).
   - A `shares_override` at a declaring filer — and a declared interim share leg — is the
     traded-class count only and says so (`share_basis: "traded_class"`).
   - A mis-scaled traded count (`SHARE_SCALE`) is fixed with that override before units are
     declared (the engine refuses both together).
   - A period left over after roll-forward may stay (the engine lists it as unused).
   - At a 20-F / 40-F filer with a declared 6-K bridge, declare the current-interim period
     from the 6-K's equity note before the preliminary run. The engine accepts it (listed
     unused) although companyfacts has no 6-K share fact, and `ttm.py --interim` then
     applies it.
   - Units more than 20× the traded count in any declared period, the current-YTD / interim
     one included, need `ack_reason`.
   Anything outside: block with a reason starting `NEEDS_MAIN_AGENT: <field> — <detail>` and
   finish. If judgment.json already carries overrides when you start (a main-agent
   decision), the tools apply them — carry the fields through unchanged and quote the
   measured impact.
   **Amortized acquired IPR&D (engine 5.6 — main-agent addition awaiting Andrew's ratification; his decision
   is that the engine does not amortize and the worker decides).** Beside `ACQUIRED_IPRD_RECURRENT` only, a
   `base_override` under clause (c) may carry the charge in the base instead of the one-time deduction:
   `{basis: "iprd_amortized", kind: "filing", native_base: "ttm_json" | "median_of_last_3_fy_oe_per_share",
   figures: [the FY charges dcf_numbers.json iprd_adjustment.periods deducted, one per FY of
   iprd_adjustment.window.fy — three, or two at a filer with only two FY —, oldest first, $0 years included
   (a charge year that deducted nothing — paid in shares, inside OCF or not yet paid — enters at its deducted
   $0: Codex review round 28 of PR #47; figures that are all $0 have nothing to amortize and the engine refuses
   them, round 28 re-verification), copied as printed (both tools accept each within $1)], shares: <the native base's count — ttm.json
   ttm_shares_diluted, or the CSV's latest shares_diluted>, value: <native base − mean(figures) ÷ shares
   (× ads_ratio)>, source, reason}`, final run `--base-oe-ps <value>`. The native base is the base the
   one-time run scored, not a free choice: `ttm_json` when that run was `--ttm` (always under `STALE_FY` with a
   ttm.json TTM base — step 4; the engine refuses the median there, also when the TTM is rejected: a rejected
   TTM leaves the median with the one-time deduction), else the median. The amortized run reads
   the native base's own window and share count (a `ttm_json` native base keeps the current-YTD leg; Codex
   review round 24 of PR #47: a median native base the FY window and the latest FY count, even when the pin
   happens to equal ttm.json's figure) and judges recurrence against the native base, so a filer the one-time run flagged RECURRENT stays recurrent.
   (Codex review round 26 of PR #47) Pin `--base-oe-ps` at that value: the cent tolerance is the declaration's
   arithmetic, and a pin on the other side of zero from the reproduced value (0.004 on a $0.00 base) is refused.
   The engine recomputes it to the cent and refuses the run (BAD_BASE_OVERRIDE, exit 3)
   otherwise, or when the charges are not recurrent, or when nothing was deducted in the last 3 FY; with it in force no one-time deduction is applied
   (`iprd_adjustment.treatment` `amortized_in_base`). make_score checks the declaration against the engine's
   record and refuses a malformed one, one the run did not carry, and an amortized record whose declaration
   is gone, and (native base `ttm_json`) a ttm.json that changed after the run; the registry `base_override`
   event records it. It is the one override NOT carried through unchanged on a re-score: rebuild it from
   every re-score's preliminary run (the new filing moves the native base, the window and the share count),
   pass the new value to the final `--base-oe-ps` run, and drop it when the new run no longer raises
   `ACQUIRED_IPRD_RECURRENT` or no longer deducts an FY charge.
   **Engine 5.5 (2026-10-19).** `share_class_mismatch: {value: true, source, reason}` —
   declare it, filing-sourced, when the filer's EPS note presents EPS for a class other
   than the traded security, or the traded security is an exchangeable / paired share
   whose price tracks a parent (BNT); `source` cites the form, period and note. It forces
   `DATA_GAP:shares — SHARE_CLASS_MISMATCH`: no tier, no alert (block as in step 4). Only
   `true` or an object whose `value` is `true` declares (an object without `value` is
   malformed, even with a `source`); `false`, null, `{value: false}` and an empty
   object declare nothing. Any other value — a string such as "false", "no" or "true", a
   number, a list, a `value` that is not a bool — is malformed: the engine records
   `share_class_mismatch: {"malformed": …}` without a gap and make_score refuses it
   ("share_class_mismatch must be true or {value: true, source, reason}"). make_score
   refuses every declaration too, and says so when source or reason is missing, so always
   give both. It is exclusive with `share_classes` (engine 5.7: the engine and make_score
   refuse both together). A kind "filing" override
   may carry `currency: "USD"` when the filing states the figure in US dollars: the
   engine then uses it verbatim instead of FX-converting it from the reporting currency
   (`override_checks.<field>.currency_basis` `declared_usd`). make_score accepts only
   "USD", only on kind "filing", and refuses a USD declaration the engine run converted
   anyway (output from an older engine — rerun it). Without the key, an override at a
   converted filer is read in the reporting currency and converted at the period-end
   rate — except where the field's last filed unit is USD, the issuer's own USD
   statements or translations (JD, BEKE, LI, HTHT, CX, PUK; usually with
   `USD_TRANSLATIONS_USED`): there it is used verbatim as dollars (`last_filed_unit_usd`).
   That fallback cannot tell a dollar figure from a local-currency one (an RMB note sits
   inside the 0.1×–10× band, CNY ≈ 7.2×), so make_score refuses any applied kind "filing"
   override the engine used this way unless it declares `currency: "USD"`. The engine
   records that basis only at a filer whose figures it FX-converted, so under 5.5 the
   fallback alone never yields a score for a filing override (an addition awaiting
   Andrew's ratification — README, Engine 5.5): declare `currency: "USD"` when the source
   states the figure in US dollars (PUK, CX); a local-currency figure (HTHT's RMB capex)
   must be restated as the filing's own US-dollar figure, declared `currency: "USD"`, or
   the name blocked `NEEDS_MAIN_AGENT: <field>`. A kind "estimate" override used under
   that basis is refused too — it cannot carry `currency` (ruling 7 reserves that for kind
   "filing") and the 0.1×–10× band admits a CNY figure at ≈ 7.2×: at such a filer use the
   filing's own US-dollar figure as a kind "filing" override with `currency: "USD"`, or block
   `NEEDS_MAIN_AGENT: <field>`.
   ttm.py reads US-dollar facts only and holds no FX rates: at a filer whose core facts are also
   filed in another currency it refuses (exit 3) a capex / SBC override without `currency: "USD"`
   wherever the override would fill a TTM leg, and make_score refuses a TTM-leg override at an
   FX-converted filer without the declaration. Declare the filing's US-dollar figure (kind
   "filing", `currency: "USD"`) or leave the TTM unbuilt and use the median base (under
   STALE_FY at a 10-K filer, `ttm_unavailable_reason` then quotes ttm.py's exit-3 line —
   step 4).
   A `shares_override` at a filer the engine split-adjusts (`SHARE_BASIS_ADJUSTED`) must be
   on the post-split basis: the engine multiplies filed counts only, never an override, and
   confirms the split against the latest filed count, so a latest-year override on the
   post-split basis sits on the same basis as the rescaled history.
   Capex overrides: the engine now reads the filer's tagged capex lines itself — the
   `PaymentsForCapitalImprovements` line (CR, IT, MAA, RBC, SNA, ELS) and, for a year with
   no PP&E roll-up filed, the SUM of the filed components (E&P drilling and leasehold
   acquisition, other PP&E, construction in process, productive assets: AR, APA, PR) — so
   the single-value capex overrides such filers carried (CR, IT, MAA, RBC, SNA, APA) are no
   longer needed (an override fills only years with no filed value, and make_score refuses
   one left beside `OVERRIDE_SUPERSEDED_BY_FILED_TAG:capex` — step 4).
   **Engine 5.7 capex (Andrew, 2026-10-19, R8 / R9).**
   - The components also include machinery and equipment, mining assets and furniture and
     fixtures (`PaymentsToAcquireMachineryAndEquipment`: KNX's whole capex line;
     `PaymentsToAcquireMiningAssets`: HUT's miner purchases;
     `PaymentsToAcquireFurnitureAndFixtures`: EXR, UDR).
   - Mining assets and furniture and fixtures are sub-classes. They are summed only beside a
     non-zero component of another class filed in the same unit. Filed alone (or beside
     another class only in a different currency) they are not the year's PP&E leg
     (`capex_provenance.<FY>.dropped` reason `subclass_alone`). With no other component the
     year has no PP&E leg: a `DATA_GAP:capex` in the last 3 FY.
   - RL, HUT and HTHT carried overrides citing or covering these lines — remove them. The
     filed value wins, and make_score refuses an override left beside
     `OVERRIDE_SUPERSEDED_BY_FILED_TAG:capex`.
   - `CAPEX_UNLISTED_COMPONENT:<tag>` means a capex-like cash-flow tag the engine does not
     read is larger than the whole component capex it did read for that year in the same
     filing (the KNX pattern). If the tag is the filer's capex line, block the company
     `NEEDS_MAIN_AGENT: capex`. An override cannot fix it, because an override never
     replaces a filed figure. If it is not capex (an acquisition, a deposit, a lessor fleet),
     say why with the figure in judgment.json `capex_unlisted_ack`
     `{"<tag>": "<reason with the figure>"}`. make_score refuses a 5.7 run without it and
     records the ack in the registry. On a 5.7 run every figure in that reason traces like
     any 5.7 reason: an engine figure such as the flag's own, or a cited fact listing
     `used_for: capex_unlisted_ack` — never a third-party fact alone.
   - `CAPEX_UNLISTED_COMPONENT_OVERRIDDEN:<tag>` is the same kind of tag in a year with no
     PP&E leg (override-filled or `DATA_GAP:capex`). It is not refused: your override citing
     that tag is valid. Say in analysis.md that the engine's list lacks the tag (RRC:
     `PaymentsToAcquireOilAndGasPropertyAndEquipment`).
   Intangible purchases
   (`PaymentsToAcquireIntangibleAssets`, `PaymentsToAcquireOtherIntangibleAssets`, IFRS
   `PurchaseOfIntangibleAssetsClassifiedAsInvestingActivities`) are counted as capex on top
   of the PP&E leg (CSV `capex_intangibles`) — a fact repeating a value the same tag files
   on a multi-year context is a cumulative total and is dropped (`capex_provenance` reason
   `cumulative_duplicate`). Since engine 5.7 capitalized software and development count as
   capex the same way (Andrew, 2026-10-19, R9): `PaymentsToDevelopSoftware`,
   `PaymentsToAcquireSoftware`, `PaymentsForSoftware` and IFRS
   `PaymentsForDevelopmentProjectExpenditure` sit inside `capex_intangibles`, named per tag in
   `capex_provenance.<FY>.software`. A filer that expenses development already carries it in
   OCF; excluding the capitalized kind would reward the accounting choice.
   `CapitalizedComputerSoftwareAdditions` is a note element and is not read. Dropped: a
   software figure equal to a PP&E line the leg uses (`ppe_duplicate`), one a PP&E total
   already contains with its other parts (`in_ppe_total`), and the parts of a software /
   intangible total (`parts_of_total`). Intangibles and software are NOT added on a year a
   `capex_override` fills: an override is read as the filer's total capex line. So declare
   the total (PP&E plus capitalised software / development and intangible purchases) when
   the cash-flow statement shows them — `OVERRIDE_APPLIED:capex` names any filed intangible
   purchases left off it. On a 5.7 run say so with `capex_override.software_included: true`
   whenever the engine reports capitalized software filed in a year (or a ttm.json leg) the
   override fills. make_score refuses the override without it. With it, make_score refuses a
   figure smaller than the filed intangible leg it claims to include, compared in USD on the
   engine's currency basis: a total is never smaller than its part (JKHY's PP&E-only 67.1M
   beside 188.4M of software is refused even when declared). An override-filled TTM leg in a
   ttm.json from an older engine cannot be checked: rerun ttm.py. The TTM legs bind only a
   ttm.json the run prices — its base reads it (`--ttm`), or it is the TTM `ttm_rejection_reason`
   rejects; a ttm.json the score never reads (another fiscal year, off the share-class
   declaration, one ttm.py can no longer rebuild) is not checked (whole-PR review fix,
   2026-10-21). Intangibles are not added on a
   year with no PP&E leg filed either (`capex_assumed_zero`): capex stays 0 and `capex_tag` blank (a
   `DATA_GAP:capex` in the last 3 FY, as before), `capex_intangibles` records the amount and
   `capex_provenance` notes `intangibles_not_added: no_ppe_leg`. A negative intangible fact
   is dropped (`negative`); a $0 one joins nothing. In ttm.json the FY and prior-YTD legs
   add their intangible purchases only when the FY leg files at least the prior-YTD amount
   (or the prior YTD files none); otherwise neither does
   (`capex_components.<leg>.intangibles_not_added: remainder_unknown`, with a warning — BAX:
   the 10-Qs file the line, the 10-K does not) and the current-YTD leg still adds its own.
   Within one year's components a line
   equal within 0.5% to the sum of two or more of the others is the filer's total: it is
   kept and the parts dropped (`parts_of_total`; GLPI FY2024). No other near-equal pair is
   merged — when two summed lines look like the same spending (GLPI FY2023 / FY2025, GSAT
   FY2024–25), check the 10-K investing section before trusting the base and say what you
   found.
   Then `python3 _system/make_score.py <T>`; it refuses on any
   disagreement with the engine run — fix the cause (usually rerun the final pass with the
   exact judgment inputs) and run it again. `DATA_GAP:ads_ratio` has the bounded fix (d).
   Then run `python3 _system/check_quotes.py <T>`. It lists every number in analysis.md that
   traces to no generated file (line, column and token). Quote the generated figure, or
   declare it in facts.json and re-run make_score.py (no engine re-run is needed for a
   facts.json or `[F#]` edit). STALE guidance facts are warnings: refresh or drop them. Never
   edit key_numbers.md: score.json `key_numbers_sha256` proves it, and the gate refuses an
   edited one.
9. **Enrich (non-blocking).** The SEC files already ran in step 2:
   `python3 _system/fundamentals.py <T>` (filing-direct annual + quarterly statements, TTM,
   dividends → `fundamentals.json`), `python3 _system/segments.py <T>` (segment / product /
   geography breakdowns from the filing's XBRL instance → `segments.json`),
   `python3 _system/statements.py <T>` (the full standardized income statement, balance
   sheet, cash flow and metrics, whole filing history → `statements.json`) and
   `python3 _system/profile.py <T>` (About and filing feed → `profile.json`; Street consensus
   and market data → `street.json`). Re-run them here only if a filing landed since. Now run
   `python3 _system/prices.py <T>` (ten years of closes → `prices.json`) and
   `python3 _system/reprice.py <T>` (the scored cash-flow paths
   repriced at the last close → `live.json`; Tier F names are skipped by design; since Codex review round 11
   of PR #47 it writes nothing until make_score has scored the CURRENT dcf_numbers.json — live figures pause
   between an engine run and its make_score, and a run make_score refused gets none; since round 29 a folder
   with no score.json gets none either, any old live.json is removed, and the site withholds a live.json not
   computed against the score.json on file, so run it after make_score, never before). A full
   refresh (`refresh.py`) runs all six in this order: fundamentals, prices, segments,
   statements, profile, reprice. The company page reads all of them. The SEC files (fundamentals, statements, segments,
   profile) are committed and rewritten only when their content changes; `prices.json`,
   `street.json` and `live.json` are gitignored caches rewritten every run. A failure here
   never blocks the score — note it in analysis.md's data section and move on.
10. `python3 _system/queue.py done <T>` then `python3 _system/build_site.py` (the data layer:
    `_daily/site/{meta,index}.json` + `data/<T>.json`; incremental, so it only regenerates the
    names whose files changed). The static app in `_daily/site/` renders everything — never
    edit HTML by hand. `--attachment` (the daily cron's job) also writes the dated
    self-contained ranking file.
    - `queue.py done` refuses an engine 5.7 run whose analysis.md fails check_quotes.py
      ("analysis.md fails the quote check"), or whose key_numbers.md / facts.json / saved
      runs changed after make_score (exit 1, nothing recorded). A saved run replaced with
      `--save-run … --replace` counts as changed. Fix the cause and re-run make_score; never
      edit key_numbers.md. judgment.json is never a source: a figure typed into it after
      make_score does not make a quote pass.
    - The company PR is cut per `_system/PR_PROTOCOL.md` (`pr_worktree.py`: per-ticker lock,
      a worktree at main's code, make_score re-run there, check_quotes, only `<T>/` + the
      ticker's registry entries + appended backlog lines). `pr_audit.py` lists every done name
      still without a PR for its scoring generation.
11. **Report** to chat ONLY when `score.json` has `alert_eligible: true` (Tier S/A at
    medium+ confidence, not a sector misfit, tier not resting on an override, IRR not at
    the floor): one line — ticker, tier, weighted IRR, bear→bull band, moat, price, IV@15%,
    one-liner. Since 5.7 an entry alert is also withheld when a share-class declaration or a
    TTM rejection lifts the tier into S/A (`alert_suppressed_reason` says which). Otherwise
    silent (Andrew gets the daily HTML). Report plainly if the sweep
    itself is blocked. Never invent a number. A score rebuilt by make_score.py on engine
    output from another release (engine 5.5: `engine_release` ≠ the current release)
    never alerts — `alert_eligible` and `exit_alert_eligible` are false with "engine output
    predates release <the current release> — re-run the engine before an entry / exit alert"
    (5.7.0 since Andrew's 2026-10-19 rulings release; 5.6.0, the acquired-IPR&D release, before it — every
    folder scored on 5.6.0 or earlier is stale until its next engine run); re-run the engine first.
    **Run health (engine 5.7, R5).** The cron body opens the run with
    `run_health.py start <job>`. End it with `run_health.py record <job> ok` when the run
    ended at a state this spec names: no pending entry; done + build_site; a block. Else end
    it with `record <job> fail --stdin` and the reason (preflight's first line, the refusal
    or crash line). A `reprice.py` exit 3 in step 9 (Skip: Tier F, a score not from the run,
    no prices) is not a failed run. Post to chat any line run_health prints — that line is
    the only health message.

Parallel workers: `queue.py claim` is atomic under a lock — two workers can never claim
the same company. Never coordinate by editing the queue. Parallel PR agents:
`pr_worktree.py acquire <T> --holder <id> --kind <kind>` is the per-ticker lock. Never
enter, edit or delete another agent's worktree (exit 4 names the holder; finish without
touching it).
