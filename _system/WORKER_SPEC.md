# Pass-1 worker spec (single source — both sweep crons point here)

Run ONE company through the owner's-earnings DCF sweep. Method: v5 data gate + engine
release 5.4 (normalized base, blended growth, moat-driven fade, five scenarios, IRR band).
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
     "filing" from it is in bounds.
   - **Exit 3 `DATA_GAP:price`** → block the same way and finish.
   - **Re-score after a new filing**: when the folder already holds a prior run (the queue
     entry carries `refresh_reason: NEW_FILING…`), read its analysis.md first; judgment.json
     and its overrides carry over and the tools apply them, except its `second_pass` object:
     remove it, since it reviewed the previous score (pass 2 reviews the new one, and
     make_score.py would otherwise copy the old badge onto it). Write the new analysis.md as a
     dated supersession (state what the new filing changed), keep the prior flag and
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
   `BASE_DIVERGENCE`: say which base is distorted and why. `NI_OCF_DIVERGENCE`: find the
   one-off. `BASIS_BREAK_SUSPECT`: name the divestiture / M&A / restatement and pick growth
   inputs that do not straddle it. `HIGH_NET_DEBT` / `BIG_NET_CASH` / `DEBT_TAGS_BLANK`
   (5.4: no debt tag found — net debt is unknown, not zero): state the balance sheet from
   the filing. `SHARES_FALLBACK` (5.4): history years on a non-diluted count — note it.
   `IRR_AT_FLOOR` (5.4): the price is beyond the model's range; the IRR reads "at most
   ~3%". `TIER_BAND` (5.4): bear and bull tiers differ — size to the bear end.
   `SECTOR_MODEL_MISMATCH`: confidence low; the ranking lists the name under sector misfits.
   `FX_CONVERTED` / `USD_TRANSLATIONS_USED` / `ADS_RATIO_*`: note the basis.
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
   `python3 _system/dcf_engine.py <T> --moat <m> --probs <5> [--offsets <5>] [--mults <5>] [--ttm] [--gterm <x>] [--cik <cik>]`.
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
   that field; name the anchor. (c) `base_override` — ONLY built exclusively from figures
   THIS run's dcf_numbers.json / ttm.json / financials_history.csv printed, construction
   quoted in analysis.md. (d) `ads_ratio` — ONLY when stated in the filer's own 20-F/40-F.
   Anything outside: block with a reason starting `NEEDS_MAIN_AGENT: <field> — <detail>` and
   finish. If judgment.json already carries overrides when you start (a main-agent
   decision), the tools apply them — carry the fields through unchanged and quote the
   measured impact. Then `python3 _system/make_score.py <T>`; it refuses on any
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
   repriced at the last close → `live.json`; Tier F names are skipped by design). The
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
    itself is blocked. Never invent a number.

Parallel workers: `queue.py claim` is atomic under a lock — two workers can never claim
the same company. Never coordinate by editing the queue.
