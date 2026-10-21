# Pass-1 worker spec (single source — both sweep crons point here)

Run ONE company through the owner's-earnings DCF sweep. Method: v5 data gate + engine
release 5.6 (normalized base, blended growth, moat-driven fade, five scenarios, IRR band;
5.5 adds the share-basis checks, additive capex with intangible purchases, SBC tag
reconciliation and USD-declared overrides; 5.6 the one-time acquired-IPR&D value
adjustment — README "Fixes & lessons", Engine 5.5 / Engine 5.6).
`README.md` has the method and "Fixes & lessons"; `DCF_AUDIT.md` explains why each rule
exists; `APP/` is the worked example of the output shape (including an override).

**MECHANICS — no exceptions.** Never edit `queue.json`, `score.json` or
`second_pass_queue.json` by hand. The queue is touched only through `queue.py`, TTM figures
come only from `ttm.py`, `score.json` is built only by `make_score.py` from
`dcf_numbers.json` + the `judgment.json` you write. Every number in `analysis.md` is copied
from `key_numbers.md`, `dcf_numbers.json` or `ttm.json` — never recomputed, never retyped.
If a figure you need is not in the computed outputs, say so in words. All paths below are
under `~/workspace/stocks/` (the system folder is `_system/`).

## Steps
1. **Claim.** `python3 _system/queue.py claim` prints your ticker (atomic, 90-min lease; the
   reaper runs first). Nothing printed → rebuild the HTML (step 10) and finish silently.
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
   - **Re-score after a new filing**: when the folder already holds a prior run (the queue
     entry carries `refresh_reason: NEW_FILING…`), read its analysis.md first; judgment.json
     and its overrides carry over and the tools apply them, except its `second_pass` object:
     remove it, since it reviewed the previous score (pass 2 reviews the new one, and
     make_score.py would otherwise copy the old badge onto it). An `iprd_amortized`
     `base_override` is not carried either: rebuild it from this re-score's preliminary run
     (step 8 — the new filing moves its native base, window and share count, so the carried
     value no longer reproduces and the engine refuses it), or drop it when that run no longer
     raises `ACQUIRED_IPRD_RECURRENT`. `iprd_cash_flow_check` entries carry over (they record
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
3. **Research** (1–3 web searches): the business, latest quarter and TTM, competitive
   position, red flags (dilution/SBC, concentration, litigation, going concern, one-offs,
   divestiture/restated basis breaks).
4. **Address EVERY fragility flag** in `dcf_numbers.json` with a specific resolution in
   `analysis.md`. Recurring ones — `STALE_FY`: run `python3 _system/ttm.py <T>` (saves
   `ttm.json`) and pass `--ttm` in the final run; quote ttm.json's legs. IFRS filers: ttm.py
   reads us-gaap only and exits non-zero — use the median base and say so.
   (Codex review round 23 of PR #47) Regenerating ttm.json — rerunning ttm.py after a new 10-Q,
   a shares override or a split — means rerunning the engine before make_score. Every run whose
   base reads ttm.json (`--ttm`, or a `--base-oe-ps` pin that is not declared built on FY figures —
   round 25 of PR #47) records what it read from ttm.json (`ttm_inputs` in
   dcf_numbers.json: `ttm_oe_per_share`, `ttm_shares_diluted`, `ytd_current_period` and
   `ttm_input_hash` over its input legs), and make_score refuses a ttm.json that no longer gives
   it ("ttm.json changed after the engine run — rerun dcf_engine.py"), even when the base still
   matches within 0.1%: the acquired-IPR&D share denominator and current-YTD window come from
   ttm.json too. Warnings and an override's source text do not count.
   `BASE_DIVERGENCE`: say which base is distorted and why. `NI_OCF_DIVERGENCE`: find the
   one-off (an acquired-IPR&D expense added back in OCF is not "OCF unaffected": it is
   `ACQUIRED_IPRD_CHARGE`'s, below). `BASIS_BREAK_SUSPECT`: name the divestiture / M&A / restatement and pick growth
   inputs that do not straddle it. `HIGH_NET_DEBT` / `BIG_NET_CASH` / `DEBT_TAGS_BLANK`
   (5.4: no debt tag found — net debt is unknown, not zero): state the balance sheet from
   the filing. `SHARES_FALLBACK` (5.4): history years on a non-diluted count — note it.
   `IRR_AT_FLOOR` (5.4): the price is beyond the model's range; the IRR reads "at most
   ~3%". `TIER_BAND` (5.4): bear and bull tiers differ — size to the bear end.
   `SECTOR_MODEL_MISMATCH`: confidence low; the ranking lists the name under sector misfits.
   **Insurer payable-earnings base (Andrew, 2026-10-19):** at a P&C insurer or reinsurer
   whose filings print **operating income (loss) available to common shareholders** (the
   non-GAAP line in every quarterly earnings release and the 10-K MD&A), the OCF base is
   not the owner's earnings: consolidated OCF capitalizes the reserve build (policyholder
   float) and the cash earned by consolidated third-party-capital vehicles, so it can run
   2× or more above what common shareholders earn (RNR: OCF base $77.78/sh vs $27.21/sh
   through-cycle operating income to common; Tier S by numbers, where the payable base
   prints C). The one-notch softening (2026-10-15) cannot bridge that gap. For these filers
   the worker declares in judgment.json:
   `base_override: {basis: "payable_earnings_5y", kind: "filing", figures: [5 annual
   amounts in USD dollars, oldest first], shares: <this run's latest shares_diluted from
   financials_history.csv>, value: <average of figures ÷ shares, per ORDINARY share>,
   source: <each year's release or 10-K, with the five figures>, reason}` and runs the
   final pass with **`--base-judgment`** (in place of `--ttm`). The engine recomputes the
   base from `figures` / `shares` (the recomputed figure is what gets recorded and
   pinned), scales it by `ads_ratio` for a 20-F/40-F filer (the pin must be per ADS,
   like the price), records the construction in dcf_numbers.json (`payable_base`, with
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
   step 8, authorized by the main agent. With it in force the one-notch `tier_override`
   is **not** applied — make_score refuses the pair as double-counting; the alert-gate
   misfit suppression and the low-confidence grade stay. Life insurers, banks and REITs,
   and any filer without that printed line, keep the 2026-10-15 rule.
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
   conversion (by more than $1 and 1%) are both recorded on the period (`unit_conflict`, `unit_conflict_note`)
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
   (a one-off deal, or the way this company buys its pipeline). `ACQUIRED_IPRD_RECURRENT`: charges in 2 or
   more of the last 3 FY (material). The engine does not amortize: either justify the one-time treatment in
   analysis.md (why the next three years will not repeat it), or declare the amortized base of step 8 and
   run the final pass with `--base-oe-ps <its value>`. **Deferred payments (Andrew's 2026-10-20 ruling, delegated to the main agent, who decided).** A charge that
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
   (`recurrence_excluded: "deferred_payment_of"`); a partly deferred period still counts. The engine refuses
   (`BAD_IPRD_DEFERRED_PAYMENT`, exit 3): a `first_charged_period` that does not precede the period; one deal
   with two first charges; a first charge inside the window whose record shows no charge there, or whose
   whole charge is itself declared a deferred payment (a deal's first charge is a purchase, not an
   installment); a first charge before the window that companyfacts covers but shows no acquired-IPR&D
   expense fact ending on that date (name the period end of the filing that first expensed it); a source whose
   accession is not from the first charged fiscal year's start year through the year after its end (a two-digit
   accession year 93–99 is 1993–1999, else 20YY; the
   original filing: an 8-K or 10-Q of that fiscal year, or the 10-K that closes it), inside or before the
   window, so the entry survives the first charge rolling out; entries summing past the period's charge; a
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
   round 1 of PR #47); reprice.py never reprices it (no live figures: the hand deduction cannot be replayed —
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
   (construction in progress, capitalised software, land-use rights, spectrum, intangible
   purchases). Either the engine read the whole capex (an asset-light or acquisition-led
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
5. **Moat 0–10, justified.** Rubric: 9–10 wide and durable (network effects, switching
   costs, structural cost advantage, proven pricing power, high returns on capital through
   a cycle); 7–8 strong; 5–6 moderate/narrow; 3–4 weak; 0–2 none. Name the specific pillars
   FOR and the erosion forces AGAINST — no generic claims. Evidence first: quote the
   company's **return on invested capital** history (the `roic_proxy` series in
   `fundamentals.json`: after-tax operating income over equity + debt − cash) and its gross
   margin level and trend for the last five fiscal years. Andrew thinks in ROIC terms: a
   moat of 7 or above should sit on ROIC that has stayed well above the cost of capital
   through a cycle, or carry a written reason why the measured history understates the
   franchise (early scale, heavy growth spend, a divestiture break). A high moat on low or
   falling ROIC is the first thing pass 2 will attack. The moat sets the fade: growth holds 2 years, then converges to 2.5% over
   CAP = clamp(2 + 1.3 × moat, 2, 15) years. `--gterm` only with a written reason.
6. **Five scenarios** summing to 100%. Defaults 10/25/30/25/10; growth-start offsets
   −12/−5/0/+5/+12pp vs the engine's blended start; OE multipliers 0.75/0.90/1.00/1.10/1.25.
   Adjust to THIS company's evidence with written reasons. **Sanity check:** compare every
   scenario's growth start with the actual recent prints (latest FY, TTM, latest quarter
   YoY, guidance). A start below what the company just printed — especially bull — needs a
   written reason; equally, if the blend hit the 35% cap on inflection artifacts, recalibrate
   downward with the reason written. Final run:
   `python3 _system/dcf_engine.py <T> --moat <m> --probs <5> [--offsets <5>] [--mults <5>] [--ttm | --base-oe-ps <x> | --base-judgment] [--gterm <x>] [--cik <cik>]`
   (`--base-judgment` is the insurer payable-earnings pin from step 4; a declared
   `base_override` with `basis` that the final run does not pass is unused and make_score
   refuses the score; `--base-oe-ps <x>` pins a declared `base_override` value from
   step 8 (c), the only pin that carries a `SHARE_SCALE_SUSPECT` base, and the
   `iprd_amortized` base of step 8).
   Exit 4 here → block as in step 2 and finish.
7. **Write `analysis.md`** in APP's shape: what it is; owner's earnings (both definitions,
   which base and why, ttm.json legs quoted if TTM); MOAT (score, FOR/AGAINST, CAP);
   five-scenario table + weighted result + diagnostics; FLAGS resolving every flag;
   thoughts / method range / hurdle-clearing price; verdict sized to the conservative end.
8. **Write `judgment.json`** with exactly: name, sector, moat_score, moat_justification,
   moat_for (short pillar strings), moat_against, probs_used (5, engine order), one_liner
   (quality + moat + why it does/doesn't clear 15% + hurdle price if below), confidence
   (low/medium/high — never high with WIDE_SCENARIO_SPREAD or unresolved flags),
   tier_override (null unless the final tier must differ, reason in analysis.md),
   tier_override_reason, in_scope_under_40b. Optional overrides `capex_override` /
   `sbc_override` / `shares_override` `{value, source, reason, kind}`.
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
   built from ttm.json's TTM figures (VNOM: TTM OE total ÷ total units) — the acquired-IPR&D
   window then reads the current-YTD leg whose cash flows are in the base —, `{"window":
   "fy"}` when it was built from FY figures (NTNX, VIV). The engine refuses a `ttm` window
   whose period is not this ttm.json's (BAD_BASE_OVERRIDE, exit 3): after ttm.py reruns,
   copy the new period. The declared window holds even when the pin happens to equal ttm.json's
   `ttm_oe_per_share` (Codex review round 24 of PR #47): `{"window": "fy"}` keeps the FY window
   and the latest FY share count. (d) `ads_ratio` — ONLY when stated in the filer's own 20-F/40-F.
   Anything outside: block with a reason starting `NEEDS_MAIN_AGENT: <field> — <detail>` and
   finish. If judgment.json already carries overrides when you start (a main-agent
   decision), the tools apply them — carry the fields through unchanged and quote the
   measured impact.
   **Amortized acquired IPR&D (engine 5.6 — main-agent addition awaiting Andrew's ratification; his decision
   is that the engine does not amortize and the worker decides).** Beside `ACQUIRED_IPRD_RECURRENT` only, a
   `base_override` under clause (c) may carry the charge in the base instead of the one-time deduction:
   `{basis: "iprd_amortized", kind: "filing", native_base: "ttm_json" | "median_of_last_3_fy_oe_per_share",
   figures: [the FY charges dcf_numbers.json iprd_adjustment.periods deducted, one per FY of
   iprd_adjustment.window.fy — three, or two at a filer with only two FY —, oldest first, $0 years included,
   copied as printed (both tools accept each within $1)], shares: <the native base's count — ttm.json
   ttm_shares_diluted, or the CSV's latest shares_diluted>, value: <native base − mean(figures) ÷ shares
   (× ads_ratio)>, source, reason}`, final run `--base-oe-ps <value>`. The native base is the base the
   one-time run scored, not a free choice: `ttm_json` when that run was `--ttm` (always under `STALE_FY` with a
   ttm.json TTM base — step 4; the engine refuses the median there), else the median. The amortized run reads
   the native base's own window and share count (a `ttm_json` native base keeps the current-YTD leg; Codex
   review round 24 of PR #47: a median native base the FY window and the latest FY count, even when the pin
   happens to equal ttm.json's figure) and judges recurrence against the native base, so a filer the one-time run flagged RECURRENT stays recurrent.
   The engine recomputes it to the cent and refuses the run (BAD_BASE_OVERRIDE, exit 3)
   otherwise, or when the charges are not recurrent; with it in force no one-time deduction is applied
   (`iprd_adjustment.treatment` `amortized_in_base`). make_score checks the declaration against the engine's
   record and refuses a malformed one, one the run did not carry, and an amortized record whose declaration
   is gone, and (native base `ttm_json`) a ttm.json that changed after the run; the registry `base_override`
   event records it. It is the one override NOT carried through unchanged on a re-score: rebuild it from
   every re-score's preliminary run (the new filing moves the native base, the window and the share count),
   pass the new value to the final `--base-oe-ps` run, and drop it when the new run no longer raises
   `ACQUIRED_IPRD_RECURRENT`.
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
   give both. A kind "filing" override
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
   "filing", `currency: "USD"`) or leave the TTM unbuilt and use the median base.
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
   one left beside `OVERRIDE_SUPERSEDED_BY_FILED_TAG:capex` — step 4). Intangible purchases
   (`PaymentsToAcquireIntangibleAssets`, `PaymentsToAcquireOtherIntangibleAssets`, IFRS
   `PurchaseOfIntangibleAssetsClassifiedAsInvestingActivities`) are counted as capex on top
   of the PP&E leg (CSV `capex_intangibles`) — a fact repeating a value the same tag files
   on a multi-year context is a cumulative total and is dropped (`capex_provenance` reason
   `cumulative_duplicate`) — but NOT on a year a `capex_override` fills:
   an override is read as the filer's total capex line, so declare the total (PP&E plus
   capitalised development / intangibles) when the cash-flow statement shows both —
   `OVERRIDE_APPLIED:capex` names any filed intangible purchases left off it. Nor on a year
   with no PP&E leg filed (`capex_assumed_zero`): capex stays 0 and `capex_tag` blank (a
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
   After it runs, check analysis.md against `key_numbers.md` and fix any figure that
   disagrees.
9. **Enrich (5.4, non-blocking).** Run, in this order: `python3 _system/fundamentals.py <T>`
   (filing-direct annual + quarterly statements, TTM, dividends → `fundamentals.json`),
   `python3 _system/prices.py <T>` (ten years of closes → `prices.json`),
   `python3 _system/segments.py <T>` (segment / product / geography breakdowns from the
   filing's XBRL instance → `segments.json`), `python3 _system/statements.py <T>` (the full
   standardized income statement, balance sheet, cash flow and metrics, whole filing history
   → `statements.json`), `python3 _system/profile.py <T>` (About and filing feed →
   `profile.json`; Street consensus and market data → `street.json`),
   `python3 _system/reprice.py <T>` (the scored cash-flow paths
   repriced at the last close → `live.json`; Tier F names are skipped by design; since Codex review round 11
   of PR #47 it writes nothing until make_score has scored the CURRENT dcf_numbers.json — live figures pause
   between an engine run and its make_score, and a run make_score refused gets none). The
   company page reads all of them. The SEC files (fundamentals, statements, segments,
   profile) are committed and rewritten only when their content changes; `prices.json`,
   `street.json` and `live.json` are gitignored caches rewritten every run. A failure here
   never blocks the score — note it in analysis.md's data section and move on.
10. `python3 _system/queue.py done <T>` then `python3 _system/build_site.py` (the data layer:
    `_daily/site/{meta,index}.json` + `data/<T>.json`; incremental, so it only regenerates the
    names whose files changed). The static app in `_daily/site/` renders everything — never
    edit HTML by hand. `--attachment` (the daily cron's job) also writes the dated
    self-contained ranking file.
11. **Report** to chat ONLY when `score.json` has `alert_eligible: true` (Tier S/A at
    medium+ confidence, not a sector misfit, tier not resting on an override, IRR not at
    the floor): one line — ticker, tier, weighted IRR, bear→bull band, moat, price, IV@15%,
    one-liner. Otherwise silent (Andrew gets the daily HTML). Report plainly if the sweep
    itself is blocked. Never invent a number. A score rebuilt by make_score.py on engine
    output from another release (engine 5.5: `engine_release` ≠ the current release)
    never alerts — `alert_eligible` and `exit_alert_eligible` are false with "engine output
    predates release <the current release> — re-run the engine before an entry / exit alert"
    (5.6.0 since the acquired-IPR&D release); re-run the engine first.

Parallel workers: `queue.py claim` is atomic under a lock — two workers can never claim
the same company. Never coordinate by editing the queue.
