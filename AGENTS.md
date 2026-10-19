# Review guide — owner's-earnings DCF sweep

This repo holds the output of an automated DCF sweep over ~2,600 US-listed
companies. Most PRs add ONE company folder `<TICKER>/`, produced by a worker
agent from SEC EDGAR filings. Review a company PR like an auditor checking
internal consistency. You cannot fetch EDGAR from a review: verify
cross-file consistency and arithmetic from what is in the diff, and when a
claim can only be checked against the filing itself, say "cannot verify from
the diff" instead of guessing.

## Files in each company folder

- `financials_history.csv` — annual filing history (the input). Per-period
  `capex_tag` / `sbc_tag` / `ocf_tag` columns record which XBRL tag each
  figure came from.
- `dcf_numbers.json` — engine output: base owner's-earnings (OE) per share,
  five-scenario IVs/IRRs, fragility flags, DATA_GAP markers.
- `judgment.json` — the worker's decisions: moat (0–10), scenario
  probabilities, and any overrides.
- `score.json` — final tier / weighted IRR / IV. Generated ONLY by
  `make_score.py` from `dcf_numbers.json` + `judgment.json`.
- `key_numbers.md` — generated quotable figures. `analysis.md` may only
  quote numbers from here.
- `analysis.md` — narrative; must resolve every flag in `dcf_numbers.json`.
- `ttm.json` — TTM legs, present when a TTM base OE was used.
- `fundamentals.json`, `statements.json`, `segments.json`, `profile.json` —
  SEC-derived enrichment.

Method in one line: OE = operating cash flow − total capex − stock-based
compensation (SBC is always a real cost). Base OE/share is the median of the
last 3 fiscal years (or a TTM figure when the last FY is stale). Five
scenarios (super bear / bear / base / bull / super bull) are
probability-weighted into the headline IV/IRR. Tiers from weighted IRR:
S ≥ 25%, A 20–25%, B 15–20%, C 10–15%, D < 10%, F = no positive normalized
conservative OE.

## Checks that matter, in priority order

1. **Cross-file consistency.** Figures in `analysis.md` must match
   `key_numbers.md`. `score.json`'s tier must match its weighted-IRR band,
   and its IRR/IV must agree with `dcf_numbers.json`. Name the file and both
   disagreeing values.
2. **Overrides.** Every override in `judgment.json` needs
   `{value, source, reason, kind}`. Rules by kind:
   - `filing`: the value comes from the company's own filing; the source
     must cite the form and period.
   - `estimate`: only within 0.1×–10× of the last filed value for that field
     (check `financials_history.csv` / `dcf_numbers.json` for the anchor).
   - `base_override`: must be built only from figures printed in that PR's
     `dcf_numbers.json` / `ttm.json` / `financials_history.csv`, with the
     construction shown in `analysis.md`.
   - `ads_ratio`: only when stated in the filer's own 20-F/40-F.
   Each override should also appear in `_system/overrides_registry.json`
   with measured base/IRR impact. Flag overrides missing source/reason/kind,
   outside the estimate band, or missing from the registry.
3. **Share-basis sanity.** Base OE/share wildly out of line with the price
   (e.g. OE/share above ~20× price), or a share count ~1,000× off from the
   CSV's own history, usually means a share-scale or split-basis defect.
   Flag it — this class has produced fake Tier S results before.
4. **Scenario sanity.** Growth starts should be plausible against recent
   revenue/OE prints in `financials_history.csv`; a scenario start below the
   latest actual print needs a written reason. Probabilities must sum
   to 100.
5. **Flags resolved.** Every fragility flag in `dcf_numbers.json`
   (STALE_FY, BASE_DIVERGENCE, NI_OCF_DIVERGENCE, WIDE_SCENARIO_SPREAD,
   IRR_AT_FLOOR, …) must be addressed in `analysis.md`. Confidence must
   never be "high" with WIDE_SCENARIO_SPREAD or unresolved flags.
6. **DATA_GAP discipline.** If SBC, capex, diluted shares, or OCF is
   missing for ANY of the last 3 fiscal years, the company must be blocked
   with no tier — a `score.json` tier alongside a DATA_GAP in
   `dcf_numbers.json` is a defect.
7. **Moat.** `judgment.json`'s moat score needs FOR and AGAINST pillars in
   `analysis.md`.

## Deliberate methodology — do NOT flag these

- A `tier_override` moving the final tier off `tier_by_numbers` when a
  written reason is present — e.g. insurer-float softening: for insurers
  and financials, the OCF-based base capitalizes float, so the final tier
  is deliberately sized down from the numbers.
- `$0` overrides with kind `filing` where the filer genuinely does not
  report the item (proven against the filing's cash-flow statement).
- Missing `prices.json` / `live.json` / `street.json` and missing
  `_daily/site/` data files: gitignored by design (re-fetchable or
  derived). The committed record is the per-company files plus
  `_daily/history/*.csv`.
- `queue.json` absent from company PRs: it is committed to main separately.
- Foreign/ADS filers: per-ADS figures use `ads_ratio` from `judgment.json`;
  ordinary-share counts in the CSV are expected, not an error.

## Comment style

One comment per concrete finding: file, the two values that disagree, and
why it matters. Consistency and rule violations are findings; disagreement
with a documented judgment call is not.
