# Site contract — data layer and static app (v6 presentation, 2026-10-14)

Why this exists: the pages were rendered as Python f-strings, every company page was emitted
twice (embedded in the ranking file and as a standalone file, each repeating the CSS/JS), and the
single ranking file grows without bound as the sweep approaches 2,617 names. The presentation is
now split in two, built around Muse's loop (claim a company → scripts write files into
`<TICKER>/` → rebuild → next):

1. **Data layer** — `python3 _system/build_site.py` reads the per-company folders (the source of
   truth Muse writes) and derives JSON: `_daily/site/meta.json`, `_daily/site/index.json` and
   `_daily/site/data/<TICKER>.json`. Incremental: a company record is regenerated only when a
   file in its folder is newer than the record. Python only, stdlib only, nothing for Muse to
   install. This is WORKER_SPEC step 10 and the daily cron's build step.
2. **Static app** — `_daily/site/index.html`, `app.css`, `app.js` are hand-written, committed
   files (vanilla JS, no bundler, no framework, no network calls except fetching the JSON next
   to them). They render the ranking and every company page in the browser with hash routing.
   Muse never edits them, so the UI cannot drift between runs.
3. **Chat attachment** — `build_site.py --attachment` writes the dated self-contained file
   `_daily/ranking-YYYY-MM-DD.html` (+ `latest.html`) by inlining `index.html` + `app.css` +
   `app.js` and a `window.SITE_DATA` object carrying `meta`, the full `index`, and the records
   for the top `--top N` rows (default 150, trimmed as described under "Attachment trimming").
   The same app renders it; it just never fetches. The hosted site (GitHub Pages at
   `_daily/site/`, updated on every push of the mirror) is the complete one.

Every number on a page comes from a file Muse's scripts wrote; the only computation in the data
layer is the forecast replay through the engine's own functions (`dcf_engine.replay_paths`,
`present_value`, `solve_irr`, `tier_for_irr`) and display arithmetic (growth, ratios) when a
field is missing from an older file. The app never computes a valuation figure.

## Routing (plain hash tokens only — letters, digits, `.`, `_`, `-`)
- `#` ranking · `#APP` company page (Overview) · `#APP.financials` a tab.
- Tabs, in order: `overview`, `financials`, `dividends`, `segments`, `forecast`, `analysis`, `data`.

## `meta.json`
```json
{"built_at": "2026-10-14T19:07:00-04:00", "date": "2026-10-14", "data_version": 1,
 "engine_release_latest": "5.4.0",
 "sweep": {"done": 89, "total": 2617, "pending": 2518, "blocked_data_gap": 5, "blocked_no_data": 5, "in_progress": 0},
 "counts": {"current": 90, "stale": 0, "misfits": 23, "tiers": {"S":0,"A":0,"B":3,"C":22,"D":48,"F":17}, "with_live": 70},
 "hurdles": {"S": 0.25, "A": 0.20, "B": 0.15, "C": 0.10},
 "notes": ["..."]}
```

## `index.json` — one row per CURRENT company (engine v5+, no uncovered gap), ranked by `irr_live` when present else `irr`
```json
{"ticker": "APP", "name": "AppLovin Corporation", "sector": "Technology / Advertising software",
 "fit": "modeled" | "misfit",
 "tier": "B",                 "tier_by_numbers": "B",  "tier_override": false,
 "tier_live": "A" | null,     "tier_bear": "C" | null, "tier_bull": "A" | null,
 "irr": 0.1843,               "irr_live": 0.199 | null, "irr_bear": 0.1293 | null, "irr_bull": 0.227 | null,
 "irr_at_floor": false,       "irr_capped": false,     "f_subtype": null | "sbc_exceeds_cash" | "no_cash_generation",
 "price": 272.28,             "price_live": 262.19 | null, "price_date": "2026-10-14" | null, "ret_1y_pct": -55.6 | null,
 "iv15": 376.12, "iv12": 535.47, "iv20": 290.1 | null, "iv25": 230.4 | null,
 "upside15": 38.1,            "upside15_live": 43.5 | null,
 "market_cap_b": 93.11,       "market_cap_b_live": 88.6 | null,
 "moat": 6, "cap_years": 9.8, "confidence": "medium", "confidence_capped": false,
 "one_liner": "...", "analysis_date": "2026-10-14", "engine_release": "5.4.0" | null,
 "flags": ["STALE_FY", "BUYBACK_TAILWIND", "..."],
 "overrides": [{"field": "capex", "kind": "estimate"}], "override_unblocks_tier": true,
 "second_pass": {"date": "...", "verdict": "changed" | "no_change", "prior_tier": "C"} | null,
 "alert_eligible": false,
 "dividend_yield": 0.0 | null, "shareholder_yield": 0.024 | null,
 "has": {"prices": true, "fundamentals": true, "dividends": true, "segments": true, "live": true, "analysis": true, "second_pass": false}}
```
Stale (pre-v5) scores are listed under `meta.stale` as `[{ticker, name, tier, irr, analysis_date}]`, never in `index`.

## `data/<TICKER>.json` — everything the company page renders
```json
{"ticker": "APP", "name": "...", "sector": "...", "folder": "APP", "built_at": "...", "built_from_mtime": 1760480000.0,
 "row": { ...the index.json row for this ticker... },
 "score": { ...score.json verbatim... },
 "numbers": { ...dcf_numbers.json verbatim minus "paths" and "growth_paths" (they live under forecast)... },
 "forecast": {"paths": {"super_bear": [15 floats], "bear": [...], "base": [...], "bull": [...], "super_bull": [...], "weighted": [...]},
              "growth_paths": {"super_bear": [15 floats], ...},
              "sensitivity": {"super_bear": {"10": 238.3, "12": 183.0, "15": 134.0, "20": 90.1, "25": 65.2, "irr": 0.0915, "irr_live": 0.101 | null}, ..., "weighted": {...}},
              "hurdle_prices": {"15": 376.12, "20": 290.1, "25": 230.4},
              "inputs": { ...numbers.inputs... }, "g_base": 0.35, "g_blend": 0.5022, "g_terminal": 0.025, "cap_years": 9.8,
              "growth_components": {...}, "growth_components_adjusted": {...} | null, "share_cagr": -0.027, "share_count_adj": 0.027, "share_adj_basis": "..." | null,
              "replayed": true | false},
 "live": { ...live.json verbatim... } | null,
 "history": [ {financials_history.csv rows, numeric strings coerced to numbers, blanks to null} ],
 "fundamentals": { ...fundamentals.json verbatim (profile, annual, quarterly, ttm, dividends, tags_used, warnings, currency)... } | null,
 "prices": {"source": "...", "as_of": "...", "stats": {...}, "weekly": [[date, close]...], "daily_1y": [[date, close]...]} | null,
 "segments": { ...segments.json verbatim... } | null,
 "ttm": { ...ttm.json verbatim... } | null,
 "judgment": { ...judgment.json verbatim... } | null,
 "registry": [ ...overrides_registry entries for this ticker... ],
 "analysis_md": "..." | null, "second_pass_md": "..." | null,
 "files": ["analysis.md", "dcf_numbers.json", ...]}
```
`forecast.sensitivity[*].irr_live` is the live repricing's scenario IRR when `live` exists.
`forecast.replayed` is true when paths were replayed (pre-5.4 run) rather than read from the file.

## Attachment trimming (`--attachment`, top N rows only)
Records embedded in the attachment drop `judgment`, `ttm`, `prices.daily_1y` and `numbers.used_tags`;
everything else is kept. Rows beyond the top N are in `index` but have no record; the app shows
"not embedded in this file — open the site" for them.

## What the app renders (parity with the v2 Python pages)
- **Ranking**: header (date, sweep progress bar, tier counts, misfit count), how-to-read, controls
  (tier segmented buttons, Modeled / Sector misfits / All, sort select, search), table with the
  columns Company · Tier (live, "was X" when changed) · Band · Live IRR · Scored IRR · Price (last
  close) · IV@15 · Upside · Moat · Conf · Mkt cap · 1y price · Take (badges: pass 2, overrides,
  tier override, misfit, IRR at floor; one-liner; flags count; date). Card layout under 760px.
  Collapsed "Pre-v5 results" box from `meta.stale`.
- **Company page**: nav (← Ranking, pass/date), header (tier tile, ticker, name, sector · cap ·
  exchange · filer category; big live or scored expected return with the scored/live sub-line and
  the bear→bull band; price used; value @15% with upside; last close with 1-day change, 52-week
  range, 1-year return; one-liner), price-vs-value chart (ranges 1Y/3Y/5Y/10Y/MAX, toggles for
  weighted value, bear–bull range, 20%/25% hurdle prices; falls back to the number line without
  prices), tabs:
  - Overview: hurdle gauge, chips, pass-2 box, key-number tiles (price, IV@15, price for 20% and
    25%, upside, base-case IRR, OE yield, TV share, scenario spread, net debt/OE), base OE card,
    overrides card (table + measured impact + reasons), scenarios card (bars vs the hurdle),
    moat card (score, dots, CAP, strengths/pressures or justification), fragility flags list.
  - Financials: TTM tiles, quarterly chart + table (12 quarters, derived markers), annual
    income / cash-flow / balance-sheet tables with growth and margin sub-rows, charts: revenue &
    profits, cash flow & OE, margins, cash & debt, capital returned; falls back to the engine's
    history CSV when fundamentals are absent.
  - Dividends: tiles (yield, annual dividend + basis, frequency, payout vs EPS, payout vs OE,
    growth YoY + 5y CAGR, growth years + last cut, buyback yield, net buyback yield, shareholder
    yield), annual DPS bar chart, history table; "No dividend" state; "enrichment not run" state.
  - Segments: per table a card with stacked bars and the period table (growth and share-of-total
    sub-rows, eliminations last, derived markers); empty state.
  - Forecast: five OE/share paths + weighted line chart, growth-fade chart, value-at-every-rate
    table (scored IRR column plus live), hurdle-price tiles vs the live price, "how growth was
    set" table + note.
  - Analysis: analysis.md and second_pass.md rendered from Markdown in the browser (headings,
    lists, tables, bold, code, links).
  - Data: provenance key/value table (entity + EDGAR link, SIC, FYE, filer category, latest
    filings with links, engine release and run date, price source, base and pin source, run
    inputs, net-debt basis, FX, ADS, data gaps, content hash, tags used by engine and by
    fundamentals, files), TTM construction table, overrides, judgment calls on record,
    judgment.json pretty-printed.
- **Charts** (drawn in the browser, responsive): category chart with bar / line / area series and
  `stacked` support, the price chart with overlays; tooltips via `<title>`; axis labels from the
  design tokens; redraw on resize and on tab change.
- **Design**: the IBM Plex dark system already in use (tokens on `:root`, `color-scheme: dark`),
  16px gutters, card layout at phone width, no horizontal page scroll (tables scroll inside their
  own container), visible focus states, `prefers-reduced-motion` respected.

## Decisions (build_site.py, 2026-10-14)
Choices made where the text above was silent or ambiguous; each is additive to the shapes above.
- **Incremental bookkeeping lives in `_daily/site/state.json`** (`{records: {T: {built_from_mtime, builder_mtime, built_at}}}`),
  not in the served files: deciding "skip" for 2,600 folders must not parse 2,600 records. A record is skipped when
  `built_from_mtime >= newest mtime among the folder's files` AND the builder's own mtime has not moved since the record was
  written; `--force` rebuilds all. Without `state.json` the builder falls back to the record file (its `built_from_mtime` and
  file mtime). Skipped records' index rows come from the previous `index.json` (fallback: the record's `row`). The registry
  (`_system/overrides_registry.json`) is not part of the mtime check: it is only ever rewritten by `make_score.py`, which also
  rewrites the folder's `score.json`.
- **`--only T,T` scopes the rebuild, not the index.** Only the listed tickers are (re)built (still incremental unless `--force`);
  every other current company keeps its previous row and record. In a fresh site dir that means the index holds only the
  listed names — the test harness relies on it. The removal of disqualified records and `meta.stale` always run over all folders.
- **Qualifying folder** = `score.json` present and non-empty, `dcf_numbers.json` with `engine_version >= 5` and a `data_gap` key,
  and an empty `data_gap_uncovered`. Pre-v5 numbers go to `meta.stale`; an uncovered gap is neither stale nor current (same as v2).
  Folders starting with `_` or `.` are ignored.
- **Pre-5.4 runs (every folder today).** `forecast.paths` / `growth_paths` come from `dcf_engine.replay_paths` (stored paths when the
  run has them); `sensitivity` cells missing from the file are `present_value` on those paths at the run's `g_terminal`
  (`numbers.weighted.iv_at_15` reproduces bit-for-bit); `hurdle_prices` prefer `numbers.hurdle_prices`, then `score.iv_at_15/20/25`,
  else `present_value` of the weighted path at 15/20/25%. `irr` per scenario is the stored scored figure (never re-solved — the
  5.4 floor fix would change it); `irr_live` (and `irr_live_at_floor`) are copied from `live.json` when it carries a price and a
  weighted IRR, else null. `row.irr_at_floor` is `score.irr_at_floor` (5.4) → `diagnostics.irr_at_floor` → for an older run the
  at-floor flag of `solve_irr` on the replayed weighted path at the scored price (flag only; the IRR itself stays the stored one).
  `row.irr_bear/irr_bull` fall back to `scenarios.bear/bull.irr`, `tier_bear/tier_bull` to `tier_for_irr` of those.
- **Band fields are the scored band**, as in the v2 ranking row; the live band is carried additively as `irr_bear_live`,
  `irr_bull_live`, `tier_bear_live`, `tier_bull_live`, plus `irr_at_floor_live`, only on rows with `has.live`.
- **`price_date`** is the live price's date (`live.price_date` else `live.as_of`) and null without `live.json`; the scored price's
  date is `analysis_date`. `upside15_live` = `live.iv_at_15 / live.price − 1` in percent (falls back to `live.upside_at_15`).
  `iv20` / `iv25` = `forecast.hurdle_prices` (fallback `live.iv_at_20/25`).
- **`has.dividends`** is true only when `fundamentals.json` carries a `dividends` object; `has.second_pass` means `second_pass.md`
  exists (the pass-2 verdict itself is `row.second_pass`, from `score.second_pass`). `row.overrides` is `[{field, kind}]` only;
  the full override objects are in `score.overrides` / `numbers.overrides_applied`. `override_unblocks_tier` is true when
  `score.override_impact.unblocks_tier` or any registry entry for the ticker says so.
- **Record extras**: `data_version`, `builder_mtime`; `prices` also keeps `currency`; `forecast.inputs` is null for a run without
  inputs; a Tier F record has `forecast.paths/growth_paths/sensitivity/hurdle_prices = null` and `replayed = false`.
  `history` cells: integers → int, other numerics → float, `True`/`False` → bool, blank → null, anything else a string.
  A malformed optional JSON file (not an object) renders as absent.
- **`meta` extras**: `tabs` (the routing order above) and `notes` (ranking rule, this run's written/skipped/removed, replay count,
  `--only` scope). `engine_release_latest` is `dcf_engine.ENGINE_RELEASE` (fallback: the newest release seen on a row).
  `sweep.total` is `queue.json`'s `universe_size`; `in_progress` counts the `in_progress` status.
- **Attachment inlining**: the `<link … href="app.css">` tag becomes an inline `<style>`; the `<script src="app.js">` tag becomes
  `<script>window.SITE_DATA=…</script>` immediately followed by the inline app script, so the app reads `SITE_DATA` at load. When
  a tag is missing the style goes before `</head>` and the scripts before `</body>`; when `index.html` is missing a placeholder
  shell (ticker table from `SITE_DATA`) is used. `SITE_DATA` = `{meta, index, records, embedded_top, embedded}`; the JSON is
  emitted with `ensure_ascii=False` and `</` → `<\/`, `<!--` → `<\u0021--`, U+2028/9 escaped (still valid JSON). A literal
  `</style` / `</script` inside app.css / app.js is escaped the same way. The attachment date is the America/New_York date.
- **Output hygiene**: every file is written atomically (`.tmp` then `os.replace`); records are compact JSON, `meta.json` indented;
  the one-line summary is ASCII only (Windows consoles).

## Decisions (owner, 2026-10-14 evening — layout and profile)
- **Layout change (Andrew):** the company page is header → tab bar → tab content. The header is compact (tier tile, ticker, name, sector line; last close with 1-day change; live expected return with the scored figure beside it). The tab bar sits directly under the header and becomes a sticky condensed bar on scroll (ticker · last close · change · expected return · the tabs). The price-vs-value chart moves INSIDE the Overview tab as its first card, followed by: the verdict gauge + chips + one-liner, "About" (profile), "Financial performance" (generated prose from the filed numbers), "Street consensus" (Nasdaq analyst data, clearly labelled as the Street's view next to our hurdle prices), "Filings" (the 8-K / 10-Q / 10-K feed from EDGAR with links), then the existing key numbers, overrides, scenarios, moat and flags cards. Nothing that exists today is removed.
- **`<T>/profile.json`** (new, `_system/profile.py`), copied into the record as `record.profile` (kept in the attachment; it is small): {"ticker","as_of","sources":{...},"about":{"description" (10-K Item 1 Business first paragraphs, cleaned, ≤1,500 chars, with the filing accession and a link), "description_short" (Nasdaq company-profile description), "industry","sector" (Nasdaq), "sic","sic_description","state_of_incorporation","fiscal_year_end_mmdd","filer_category","exchange","website","headquarters" (EDGAR submissions business address, city/state), "employees" (from the 10-K human-capital text, with the sentence quoted as evidence) | null, "first_sec_filing" (earliest filing date in submissions, the IPO-date proxy), "edgar_url"}, "street":{"source":"Nasdaq analyst endpoints","as_of","consensus":"Buy"|...,"analysts":16,"buy":16,"hold":4,"sell":0,"target_mean","target_low","target_high","target_1y_nasdaq_summary","history":[{"date","mean_target","buy","hold","sell"}...],"eps_forecast":{"quarterly":[{"period","consensus","low","high","estimates","revisions_up","revisions_down"}],"annual":[...]}} | null, "filings":[{"form","filed","period","items" (8-K items),"description" (e.g. "Results of operations" for 2.02),"url"}...] (latest 20), "market":{"exchange","average_volume","volume","market_cap_nasdaq","high_52w","low_52w","dividend_yield_nasdaq"} }. Refresh policy: profile.py --all skips files younger than --max-age-days (default 7) unless the company has a newer filing; the Street block is third-party data and is never used by the valuation.
- **Financial performance prose** is generated in the app from record.fundamentals / live (pure function, node-tested): latest FY revenue and growth, net income, operating cash flow, owner's earnings and margin, TTM where available, shares trend, with the fiscal year named — no adjectives, numbers only.
