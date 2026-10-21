# facts.json — declared facts (engine 5.7, Andrew's ruling R3, 2026-10-19)

Every number in a 5.7 run's `analysis.md` must trace to a generated file: `key_numbers.md`, `dcf_numbers.json`,
`ttm.json` or a saved method run (`dcf_numbers_<label>.json`, made only by `check_quotes.py --save-run`). A number
the engine cannot produce — filing text, a company release, a third-party source, or a folder-file figure such as a
quarterly print in `fundamentals.json` — is declared in `<T>/facts.json` first. `make_score.py` validates and verifies
the declaration and renders it last in `key_numbers.md` under **"Declared facts (not engine output)"**; quote the
figure as it is rendered there. `queue.py done` (and `pass2-done`) runs `check_quotes.py` and refuses a 5.7 run whose
analysis.md quotes an untraced number.

Files here:
- `TST/facts.json` — a synthetic company, one fact of every kind (folder, filing, release, third_party), a
  guidance range, a metric series entry, an `event`, two `calc` facts and a `not_quantities` entry. Its schema
  validates; its folder facts are illustrative (there is no TST folder).
- `APP_folder_facts.json` — folder facts with real paths into APP's files (the CSV, statements.json, fundamentals.json,
  segments.json, profile.json, ttm.json); every value verifies against APP's committed files.

## The schema (`facts.py` validates it; every rule is a make_score refusal)

```json
{"schema": 1, "ticker": "TST",
 "facts": [{"id": "F1", "label": "Q2 2026 revenue", "value": 1923686000, "unit": "USD", "scale": "B",
            "precision": 2, "period": "Q2 FY2026", "kind": "release", "type": "actual", "metric": "revenue",
            "source": {"form": "8-K", "accession": "0000000000-26-000057", "exhibit": "99.1", "filed": "2026-08-05"},
            "snippet": "Revenue of $1.92 billion, up 53% year over year", "used_for": ["context"]}],
 "not_quantities": [{"text": "Phillips 66", "reason": "company name"}]}
```

- `id` `F1`, `F2`, … (stable across re-scores). `label` 3–80 characters.
- `value` in base units (dollars, not millions; a share count, not millions of shares); `pct` / `pp` / `bps` are
  fractions (`0.126` = 12.6%, `0.0042` = 42 bps); a range is `[low, high]` (never a folder fact).
- `unit`: an ISO currency (`USD`, `EUR`, …), `<CCY>/share` or `<CCY>/ADS`, `pct`, `pp`, `bps`, `x`, `count`
  (`unit_label` names a count: `stores`, `employees` — a noun with no digits). `scale` (`""`, `K`, `M`, `B`, `T`) and `precision` (0–6
  decimals at that scale) are how the figure is quoted — they set the verification tolerance.
- `period`: `FY2025`, `Q2 FY2026`, `H1 FY2026`, `9M FY2026`, `TTM 2026-06-30`, `CY2026` or a `YYYY-MM-DD`
  instant. FY labels are the calendar year of the fiscal year's END (the folder files' convention). Guidance and
  estimates carry the TARGET period.
- `kind`:
  - `folder` — `source.path` `<file>:<selector>`; make_score VERIFIES the value against the file. A number a folder
    file holds MUST be declared this way: a filing / release / third-party fact that repeats a folder figure for the
    same period is refused. Selectors: `financials_history.csv:ocf[FY2025]`,
    `statements.json:income.revenue.quarterly[Q2 FY2026]`, `statements.json:income.revenue.ttm@2026-06-30`,
    `fundamentals.json:annual[FY2025].buybacks`, `fundamentals.json:quarterly[Q2 FY2026].revenue_yoy`,
    `fundamentals.json:ttm.sbc@2026-06-30`,
    `segments.json:tables[geography/Revenues/annual].rows[country:US].values[FY2025]`,
    `profile.json:about.employees.count`, `ttm.json:ttm_ocf`. Never an integer index; a ttm selector names its end.
  - `filing` — SEC filing text: `{form, accession, section, filed}`.
  - `release` — an 8-K / 6-K exhibit: `{form, accession, exhibit, filed}`.
  - `third_party` — `{url (https://), publisher, published}`. Third-party facts calibrate scenarios and give context
    only: never `used_for` tier_override, misfit_notch, base_override or ttm_rejection, and never the only support of
    a reason.
  Filing, release and third-party facts carry `snippet`: the source's own words, under 25 words, containing the
  number (a filing table snippet may print in thousands or millions).
- `type`: `actual`, `guidance`, `estimate`, `metric` (an operating KPI — part of a series sharing `metric`) or
  `event` (a dated occurrence or term carrying a number). Guidance / estimates older than the latest filing the
  engine used are marked STALE in key_numbers.md (a warning, never a refusal).
- `calc`: `{op: growth | ratio | diff | sum | mid | cagr, of: [fact ids or paths], years?}` — a figure you derive
  from others ("22.3% above IV@15", a guidance midpoint, a CAGR). make_score reproduces it; its `kind` is its weakest
  operand's (`third_party` < `filing` = `release` < `folder`; paths, including `dcf_numbers.json:<key>`, count as
  folder). No snippet.
- `used_for`: `context`, `scenarios`, `guidance_check`, `flag_resolution`, a reason tag (`tier_override`,
  `misfit_notch`, `base_override`, `moat_divergence`, `low_roic`, `share_classes`, `ttm_rejection`, …) or
  `moat:<pillar>`.
- `not_quantities`: up to 20 literal strings that are names, not quantities (`Paragon 28`); one that reads as money,
  a percent or a multiple is refused.

## Reasons cite facts

On a 5.7 run `tier_override_reason`, a plain `base_override`'s reason / source, `misfit_notch_reason` and the other
reason fields cite facts as `[F1]` or `[F1, F3]`. Every number in them must be an engine figure or a cited fact's
value, a reason (not a pin) must carry a number, it may never rest on third-party facts alone, and each cited fact
must list the field's `used_for` tag.

## Editing after make_score

Never edit `key_numbers.md` (score.json `key_numbers_sha256` proves it). After changing `facts.json` or a reason,
re-run `make_score.py` (no engine re-run is needed); `check_quotes.py <T>` then reports what still does not trace.
