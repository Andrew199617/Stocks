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
 "watchlist": ["APP", "DUOL", "U", "..."],
 "failed": [],
 "notes": ["..."]}
```
`watchlist` is every ticker in `_system/watchlist.json` (upper-cased, sorted, whether or not it is in the universe);
`counts.watchlist` is how many index rows carry the flag. `failed` lists tickers whose record could not be built this
run (`counts.failed`); they keep their previous row/record, if any.

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
 "watchlist": true,
 "has": {"prices": true, "fundamentals": true, "dividends": true, "segments": true, "live": true, "analysis": true, "second_pass": false}}
```
`watchlist` is true when the row's ticker is in `_system/watchlist.json` (the app's "Watchlist" toggle next to the tier
filters filters on it). Stale (pre-v5) scores are listed under `meta.stale` as
`[{ticker, name, tier, irr, analysis_date, watchlist}]`, never in `index`.

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

## Decisions (static app — `_daily/site/index.html`, `app.css`, `app.js`, `tests/`, 2026-10-14)
Choices made where the text above was silent or ambiguous; none changes a data shape.
- **Hash parsing.** `#T.tab` splits at the LAST `.` and only when the suffix is one of the seven tab names, so a dotted ticker
  (`#BRK.B`, `#BRK.B.data`) routes correctly. The v2 form `#T/tab` is accepted and normalised to `#T.tab`. Ticker matching is
  case-insensitive against `index.json`; the canonical ticker from the index is what the hash is rewritten to. A token outside
  `[A-Za-z0-9._-]` or a ticker not in the index returns to the list with a one-time notice ("No company "X" in this ranking").
  Tab switches use `history.replaceState` (in try/catch), so the back button returns to the ranking, not through every tab.
- **`window.SITE_DATA`** is read as `{meta, index, records}` where `records` is an object keyed by ticker (an array of records is
  also accepted). With `SITE_DATA` present the app never calls `fetch`; a row without a record renders the "not embedded in this
  file — open the site" page (linking to `meta.site_url` when the data layer provides one) with the row's scored / live figures.
- **Ranking columns and sort.** The default sort is Live IRR with the scored IRR as the fallback key for rows without `live.json`
  (the same order as `index.json`), so names never fall to the bottom for lacking a repricing. The tier filter matches the
  DISPLAYED tier (`tier_live` when present, else `tier`); the Band column shows `tier_bear_live → tier_bull_live` on live rows and
  the scored band otherwise; Price / Upside / Mkt cap show the live figure when the row has one (the title attribute carries
  `price_date`). Column headers with a key sort on click; the sort select, tier and fit segments and the search box are one
  state object remembered in `localStorage` (`oe-dcf.list.v1`, every read/write in try/catch, bad values fall back to defaults).
- **Prev / next by rank** walk `index.json` order (which includes sector misfits even when the list is filtered to Modeled);
  the page footer shows the rank.
- **Live view precedence** is the v2 rule: `live.json` wins when it carries a price AND a weighted IRR; `score.json` otherwise, with
  `row.*` only as a fallback for fields an older score lacks (`irr_bear`, `tier_bear`, `iv20`, `iv25`, `irr_at_floor`). The band
  text falls back to `tierForIrr(scenario irr)` using `meta.hurdles` (default S .25 / A .20 / B .15 / C .10) only when no tier is
  stored — a classification of a stored IRR, never a valuation.
- **Hurdle prices / sensitivity** come from `forecast.hurdle_prices` / `forecast.sensitivity`; without them the page falls back to
  `score.iv_at_15` + `row.iv20/iv25` and the stored `numbers.scenarios[*].iv_at_*`. No present-value replay happens in the app;
  a record without `forecast.paths` shows a note in place of the two Forecast charts.
- **Negative money** renders as `-$1,234.50` (v2 Python printed `$-1,234.50`). `fmtPct` renders `-12.3%`; signed variants
  prefix `+`. Nothing else in the number formats differs from v2.
- **Markdown** is the v2 subset (headings shifted one level, `-`/`*` lists, pipe tables, `**bold**`, `` `code` ``, http(s) links
  only — `javascript:` and relative targets stay plain text) plus `1.` ordered lists and ``` fences (escaped). Everything is
  passed through `esc()` before inline formatting.
- **Charts.** Specs live in a per-page map keyed by `data-cid` (never in attributes); `stacked:true` stacks positives per label
  upward from zero and negatives downward, draws `spec.totals` as an unfilled outline (legend entry `totalName`), and every
  bar / point carries a `<title>` tooltip "label · series: value" plus the optional per-point `tips[i]` (YoY on the DPS chart,
  share of total on segments — v2 emitted these tips but never rendered them). Charts are drawn after mount, on tab switch and
  150 ms after the last resize; hidden panes are drawn when they become visible.
- **Owner layout decision (header → sticky tab bar → tab content)** is implemented as: compact hero (tier tile, ticker, name,
  tier chip, sector · cap · exchange · filer line; expected return with the scored figure beside it; last close with 1-day
  change, 52-week range and 1-year return; value @15% with upside) → `.tabbar` (`position: sticky`, with a `.tabsum` line
  "tier · ticker · last close · 1d change · expected return" that appears once the hero scrolls above the viewport, toggled by a
  frame-throttled scroll listener) → panes. The price-vs-value card is the first card of the Overview pane; the one-liner moved
  from the hero into the verdict card. Overview order: price chart, verdict (gauge + chips + one-liner), pass-2 box, About,
  Financial performance, Street consensus, Filings, Key numbers, Overrides, Scenarios, Moat, Fragility flags.
- **`record.profile` absent** (profile.py has not run): About falls back to `fundamentals.profile` facts (SIC, exchange, filer
  category, FYE, incorporation) with a note; Street consensus renders a one-line empty card stating the Street's view never
  enters the valuation; Filings fall back to `fundamentals.profile.latest_filings`. `about.description` is accepted either as a
  string or as `{text, accession, url}`; `about.employees` as a number or `{count, as_of, evidence}`. Only `http(s)` URLs become
  links. Street price targets are shown beside OUR hurdle prices (15% / 20%) with the Street-not-ours note.
- **Financial performance prose** (`financialPerformance(record)`, exported and node-tested) reads only `fundamentals.annual`
  (latest FY vs prior) and `fundamentals.ttm`: revenue and growth, gross / operating / net margins, operating cash flow, capex,
  SBC, owner's earnings and margin and per share, TTM figures, diluted-share change (vs prior FY and vs five FYs back), cash /
  debt / net debt, dividends / buybacks / acquisitions. Empty string without annual rows (the card is then omitted).
- **Tests** (`node _daily/site/tests/app.test.js`) load `data/<T>.json` when the data layer has written it, else assemble a record
  from the company folder via `tests/fixtures/assemble.js` (no fixture is ever written into a company folder); the dividends /
  segments / live / profile paths are covered by `tests/fixtures/synthetic.json`, since no real folder carried those blocks when
  the app was written.

## Decisions (owner, 2026-10-14 night — Forecast tab)
- **Forecast tab = three sub-tabs**, in this order: **DCF** (ours, the verdict's engine), **Street** (Nasdaq analyst data, clearly labelled third-party and never used by the valuation), **Analysts** (coverage and rating history). The Overview keeps only a compact "Street summary" card (one paragraph: analyst count, consensus, mean target and its % vs the last close; the buy/hold/sell bar; a "See forecast" link) — the full section lives here.
- **DCF sub-tab** (every existing section stays): (1) "Owner's earnings per share — history and forecast": one chart in the stockanalysis style — the filed OE/share history (fundamentals annual `oe_per_share`, else the engine CSV) as a solid line, then the forecast as dashed lines from the base year: the probability-weighted path bold, bear and bull as thinner dashed lines, super-bear→super-bull as a shaded band; below it the table High (super bull) / Avg (weighted) / Low (super bear) for projection years 1, 2, 3, 5, 10 and 15. (2) "Owner's earnings growth": historical YoY bars from the same series, then forecast bars = the weighted growth path with an error bar from the bear to the bull growth path for the same year; table High / Avg / Low for years 1–3. (3) The existing growth-fade chart, value-at-every-rate table (scored + live IRR columns), hurdle-price tiles, and "how growth was set".
- **Street sub-tab**, sections in order: (1) "Stock price forecast" — paragraph (N analysts, consensus, mean target, % vs the last close, low and high), the gauge (semicircle Sell → Hold → Buy with the needle at (buy + 0.5·hold) / (buy + hold + sell); Nasdaq gives buy / hold / sell only, no strong split — say so in the legend), the price-target chart (past year of weekly closes, then a fan from the last close to low / mean / high one year out, labelled tags at the right edge). (2) "Price target" table: Low / Average / High with % change vs the last close (Nasdaq publishes no median — omit the column). (3) "Analyst ratings" — the paragraph, "Recommendation trends" stacked bars by month (buy / hold / sell from `street.history`), the monthly table (Buy / Hold / Sell / Total / mean target). (4) "Financial forecast" with an Annual · Quarterly toggle: tiles EPS This Year / Next Year (from `street.eps_forecast.annual`; "from" = last FY diluted EPS in fundamentals; growth badge) and, on Quarterly, EPS This Quarter / Next Quarter ("from" = the same quarter a year earlier from fundamentals quarterly `eps_diluted`); the table with historical columns (last two FY or four quarters, filed: Revenue, Revenue growth, Gross profit, Gross margin, Operating income, Net income, EPS, EPS growth) and forecast columns (EPS consensus, EPS growth vs the prior filed/forecast, No. of estimates; revenue and margin rows show "—" because Nasdaq publishes EPS consensus only — say so under the table). (5) "EPS forecast": chart with filed diluted EPS as a solid line then consensus dashed with the low–high band; table High / Avg / Low per forecast fiscal year. (6) "EPS growth": historical YoY bars then forecast bars with error bars (low–high); table High / Avg / Low. (7) "Earnings track record": the last four quarters' actual vs consensus EPS (`street.eps_history`) as paired bars with the surprise %, plus the next report date line. (8) Data-sources box: "Nasdaq analyst endpoints (Zacks consensus) — pulled <as_of>; EPS consensus is on the analysts' adjusted basis, not GAAP; not an input to the DCF."
- **Analysts sub-tab**: the covering brokers (`street.brokers`, as chips), the ratings history table (monthly: consensus label, buy / hold / sell / total, mean target), estimate momentum (consensus EPS now vs 1 week / 1 month ago for the quarter and the year), the forward PEG when present, upgrades / downgrades when Nasdaq returns any (it rarely does), and an honest note: individual analyst names, track records and per-analyst targets are paid (TipRanks) data and are not included.
- **`profile.street` schema (extends the earlier decision):** {"source","as_of","consensus","analysts","buy","hold","sell","target_mean","target_low","target_high","target_1y_nasdaq_summary","history":[{"date","mean_target","buy","hold","sell","consensus"}] (oldest first),"brokers":[...],"upgrades_downgrades":[...],"eps_forecast":{"quarterly":[{"period","fiscal_end","consensus","low","high","estimates","revisions_up","revisions_down"}],"annual":[...]},"eps_history":[{"period","consensus","actual","surprise_pct"}] (quote/eps PreviousQuarter rows, oldest first),"eps_upcoming":[{"period","consensus"}],"momentum":{"quarter":{"period","current","week_ago","month_ago"},"year":{...}},"next_earnings":{"date","text"},"peg_forward"}.

## Decisions (build_site.py review round, 2026-10-15)
Fixes from the adversarial review of the data layer; each is additive to the shapes above.
- **Watchlist is in the data.** `build()` reads `_system/watchlist.json` (`tickers[]` of `{ticker, ...}` objects or bare
  strings; upper-cased, trimmed, blanks and non-strings dropped; a missing or malformed file is an empty list). It emits
  `meta.watchlist` (sorted), `meta.counts.watchlist`, and `watchlist: bool` on every `index.json` row and every `meta.stale`
  entry. The flag is **re-derived on every run for every row**, including skipped ones, and the watchlist file is deliberately
  NOT part of the per-record skip check (editing it must not rebuild 2,600 records). Consequence: `index.json` is authoritative
  for `watchlist`; a skipped record's embedded `row.watchlist` can lag until that record is next rebuilt. The attachment
  therefore copies the index row into each embedded record (`records[T].row` is the index row, not the on-disk record's row).
  The app side (the toggle itself in `app.js`) is not part of this builder.
- **Served key = `score.json`'s `ticker`.** A company is keyed by `score.ticker` (trimmed, upper-cased), falling back to the
  folder name; `data/<key>.json`, the index row's `ticker`, `state.json`, `meta.stale[].ticker` and the attachment's `records`
  all use that key, so the app's `fetch('./data/' + row.ticker + '.json')` always finds the file. The folder name stays in
  `record.folder`. `--only` accepts either the served ticker or the folder name. When two folders claim one ticker, the folder
  named exactly after the ticker is served; otherwise the first by folder name. The other is ignored and reported (stderr
  `build_site: duplicate ticker ...`, `meta.notes`, the summary line, `build()["duplicates"]`); when the served folder
  disappears the remaining claimant takes over the key on the next run.
- **One malformed folder never aborts the build.** (1) `score.json` / `dcf_numbers.json` that are not JSON objects count as
  absent (`{}`): a non-object `score.json` means "not scored" (neither current nor stale); a non-object `dcf_numbers.json` is
  classified like a pre-v5 run (`meta.stale`). (2) Every nested field read as an object or list (`scenarios`, `weighted`,
  `hurdle_prices`, `inputs`, `diagnostics`, `growth_components[_adjusted]`, `override_impact`, `second_pass`, `overrides`,
  `fragility_flags`, `paths`/`growth_paths`, `live.scenarios`, `prices.stats/weekly/daily_1y`, `fundamentals.dividends`,
  registry entries) is coerced — a wrong type renders as absent/empty, so e.g. a list under `numbers.scenarios` gives a record
  with `forecast.paths/hurdle_prices = null` (and `iv20/iv25` from `live.json` if present), a string under
  `score.fragility_flags` falls back to `numbers.fragility_flags`. Tier strings are validated against S/A/B/C/D/F (anything else
  → null, `tier` → "?"). (3) Non-finite floats: `financials_history.csv` cells that parse to ±inf (e.g. `1e400`) become null
  like NaN; every record, the index and meta pass through a deep `finite()` pass (NaN/±inf → null) before `dump()`, whose
  `allow_nan=False` stays as the guard. (4) The per-folder body of the build loop (`load_company` → `build_record` → `dump`)
  runs under `try/except Exception`: a failure is logged to stderr as `build_site: FAILED <T> (<folder>): <Exc>: <msg>`
  (even under `--quiet`), the ticker is listed in `meta.failed` / `meta.counts.failed` / `meta.notes` / the summary line
  (`/ N FAILED [T]`) and `build()["failed"]`; the previous row and record are kept when they exist (`state.json` is not
  updated for it, so the next run retries); without a previous record the ticker is simply absent this run. Exit status stays
  0 — everything else was written and WORKER_SPEC step 10 / the crons do not gate on it; the stderr line and `meta.failed`
  are the signal.
- **Deleted folder files invalidate the record.** `state.json` record entries carry `files` (the folder's sorted file list at
  build time) and a record is skipped only when the list is unchanged as well as the mtime/builder checks above. Removing
  `live.json` / `segments.json` / `fundamentals.json` therefore rebuilds the record (`has.*` false, `irr_live` null, ranking by
  the scored IRR). The fallback-from-record path compares `record.files`; a `state.json` written before this change (no
  `files`) rebuilds its records once, then settles.
- **`write_atomic` retries on Windows locks.** `os.replace` onto a file another process has open (the browser serving the
  site, another agent, antivirus) raises `PermissionError` on Windows; the writer retries ~20 times with a short back-off before
  giving up (the `.tmp` file is removed on failure).

## Decisions (static app review round, 2026-10-15 — Forecast sub-tabs, watchlist, floor markers)
Fixes from the adversarial review of `app.js` / `app.css` / `tests/app.test.js`; none changes a data shape.
- **Forecast sub-tabs and their hash form.** The Forecast pane carries a sub-tab strip DCF · Street · Analysts (`.subtabs` /
  `.subpane`, DCF default). Hash: `#T.forecast` (DCF), `#T.forecast.street`, `#T.forecast.analysts`; `parseHash` only treats a
  trailing `.street` / `.analysts` / `.dcf` as a sub-tab when the token before it ends in `.forecast`, so dotted tickers still
  route (`#BRK.B.forecast.analysts`) and `#APP.overview.street` is simply an unknown ticker. The sub-tab is remembered for the
  page (switching Overview → Forecast returns to the last sub-tab). The Overview's Street card is the compact "Street summary"
  (one paragraph: analyst count, consensus, mean target and its % vs the last close, range; our 15% / 20% hurdle prices; the
  buy / hold / sell bar; a "See forecast ›" link to `#T.forecast.street`); the EPS and history tables moved to the Street sub-tab.
- **OE/share history + forecast chart.** History = `fundamentals.annual.oe_per_share`; a null cell is filled by filed OE ÷ diluted
  shares from the annual row or, failing that, the engine CSV row for the same fiscal year (display arithmetic on two filed
  values; APP's FY2025 is such a cell); without fundamentals the CSV alone. Last 10 FYs, leading empty years dropped. The
  forecast series carry the engine's base OE/share (`score.base_oe_per_share`) at the last history position so the dashed lines
  start "from the base year"; projection years are labelled FY+1… when the last FY label is a year, else `+1…`. Without any
  history a single `Base` label is used. The chart gets a dashed divider ("forecast →") after the base year. The High / Avg /
  Low table is super bull / weighted / super bear for years 1, 2, 3, 5, 10, 15, straight from `forecast.paths`.
- **OE growth chart: the weighted growth is derived, not stored.** No weighted growth path exists in the data (`growth_paths`
  has the five scenarios only), so the forecast bars are the year-over-year change of the stored weighted OE path (year 1
  measured from the base — it therefore also carries the scenarios' OE level multiples, said in the note). Error bars run from
  the stored bear to bull growth path for the same year; the High / Avg / Low table for years 1–3 is bull growth path / weighted
  YoY / bear growth path (matching the error bars). Historical bars are YoY of the filed series and blank where the prior year
  was not positive (a ratio on a negative base has no sign). This is display arithmetic on stored values, never a valuation.
- **Street sub-tab.** Every section the owner listed renders from `profile.street` with graceful empties: paragraph; semicircle
  gauge (needle at (buy + ½·hold) ÷ total, legend says Nasdaq gives no strong split); price-target fan (`drawFan`: past year of
  closes from `prices.daily_1y` else `weekly`, dashed lines from the last close to low / mean / high one year out, shaded fan,
  right-edge tags; omitted with a note when there are no prices); Low / Average / High table with % vs the last close (no
  median — Nasdaq publishes none); ratings paragraph + stacked buy / hold / sell bars by month from `street.history` (sorted
  oldest first for the chart, newest first in tables) + the monthly table; Financial forecast with an Annual · Quarterly
  toggle (tiles "EPS this / next year" from `eps_forecast.annual[0..1]`, "from" = last filed FY diluted EPS then the prior
  consensus; quarterly tiles' "from" = the same quarter a year earlier matched by quarter number and year−1 against
  `fundamentals.quarterly` labels, blank when no match; the table shows the last two FYs / four quarters filed beside the
  consensus columns, with "—" for everything but EPS, growth and estimate counts); EPS forecast chart (filed solid, consensus
  dashed, low–high band) + High / Avg / Low table; EPS growth bars with low–high error bars + table; earnings track record
  (`eps_history`, last four, paired consensus / actual bars with the surprise % computed when not supplied) + next report line
  (`next_earnings`, `eps_upcoming`); the data-sources box. Consensus EPS is labelled as the analysts' adjusted basis.
- **Analysts sub-tab** renders `street.brokers` (strings or `{name}`), the ratings history (newest first), `street.momentum`
  (now vs 1 week / 1 month ago with the % change), `peg_forward`, `upgrades_downgrades` (objects or strings) and the TipRanks
  note; without `profile.street` it shows the enrichment note plus the TipRanks note.
- **Watchlist toggle and per-device stars.** The list state gains `watch: false` (persisted with the rest in `oe-dcf.list.v1`;
  only a real boolean is accepted). A "★ Watchlist N" button sits between the tier and fit segments; N counts index rows with
  `row.watchlist === true` plus the tickers starred on this device (`oe-dcf.stars.v1`, an array, normalised and upper-cased).
  Canonical watchlist rows show a fixed star (no toggle — the file is the source of truth); every other row gets a ☆/★ button
  that adds a per-device extra, which the watch filter includes. The company hero shows a "★ Watchlist" chip for canonical rows
  only (the record does not know about device stars). `filterSortIndex`, `renderListRowsHTML`, `renderRowHTML` and
  `renderListHTML` take the stars as an extra argument so they stay pure.
- **Ranking table geometry.** `renderListHTML` emits a `<colgroup>` with the width % from `COLS[i][3]` (Company 14, Tier 4.5,
  Band 5.5, Live / Scored IRR 6 each, Price 6, IV 6, Upside 5, Moat 4.5, Conf. 5, Mkt cap 6, 1y 5, Take 26.5 — sums to 100), so
  `table-layout: fixed` no longer splits 13 columns evenly. At 1265 px the rows are ~120–185 px tall (were 400–600).
- **Condensed tab bar price.** `renderTabSummary` follows the header's rule: live page → live price with the 1-day change; no
  live.json → `prices.stats.last` with its change when `last_date` exists, else the scored price with no change figure. A change
  is never shown beside a price it was not measured on (AEE: `$104.58 +0.25%`, not `$104.48 +0.25%`).
- **Floor markers.** `sensitivity()` carries `irr_at_floor` and `irr_live_at_floor` per scenario (the weighted row also reads
  `live.irr_at_floor` / `row.irr_at_floor_live`); `liveView().irr_at_floor` treats `row.irr_at_floor_live` like
  `live.irr_at_floor`. A flagged IRR cell in "Value at every discount rate" is coloured and carries an "at floor" superscript
  with a title explaining it is a bound, not a solved return (the note under the table repeats this when any cell is flagged);
  the hurdle-price band note and the hero's bear → bull band mark a floored end the same way; the hero's "at the model floor"
  text covers the weighted figure. ZS (live super bear / bear at the floor) is the test case.
- **Chart primitives added** to `drawChart`: `kind: 'band'` series (`values` = high, `lows` = low, shaded between contiguous
  runs), per-bar `colors`, per-bar `errors` (`[lo, hi]` stems with caps and a tooltip), `nodots`, `dividerAt` (index after which
  the dashed "forecast →" divider is drawn) and `legendExtra`; legend swatches distinguish dashed lines, bands and error bars.
- **Not done here (deliberately).** The attachment build (`--attachment`) writes `_daily/ranking-<date>.html` / `latest.html` next
  to files other agents own and was not run from this change; the app's `SITE_DATA` path is unchanged. Per-device stars are not
  synced anywhere (README already says GitHub Pages cannot). `meta.counts.watchlist` is not read: the button's count is derived
  from the index rows so device stars are included — the two agree for the canonical set.

## Decisions (prices.py intraday capture, 2026-10-15 — schema for build_site.py's pass-through)
`prices.py` makes a second Nasdaq request per name (after the daily history; `--no-intraday` skips it) and `prices.json`
gains three top-level keys. Every pre-existing key (`daily_1y`, `weekly`, `monthly`, `stats`, `as_of`, `fetched_at`, …) is
unchanged in meaning. Nothing here feeds the valuation; `reprice.py` still reads `stats.last` / `stats.last_date` only.
- **`prices.intraday`** (object | null) — the current session, or on a weekend / holiday the LAST session the endpoint returns:
  `{"session_date": "2026-10-14", "tz": "America/New_York", "regular_open": "09:30", "regular_close": "16:00",
  "prev_close": 272.28, "last": 257.14, "last_time": "19:59", "last_sale": 262.19, "time_as_of": "Oct 14, 2026", "points": 821,
  "bars": [[minutes_since_ET_midnight, price], ...], "source": "api.nasdaq.com chart (no dates)"}`. `bars` are 5-minute buckets
  keyed by the bucket's START minute (240 = 04:00, 570 = 09:30, 955 = 15:55, 1195 = 19:55), the LAST 1-minute price inside each
  bucket, time order, no empty buckets, pre-market + regular + after-hours exactly as Nasdaq returned them (a thin name has
  gaps). `prev_close` = `data.previousClose`; `last` / `last_time` = the FINAL point (after-hours when the session has any —
  so `last` ≠ the regular close); `last_sale` = `data.lastSalePrice` (the official last sale = the regular-session close, equal to
  `stats.last` after the close); `points` = raw 1-minute points received. Prices are rounded to 4 dp. The 1D chart's
  previous-close dashed line is `prev_close`; the pre / after-hours shading is `minutes < 570` / `minutes >= 960`.
- **`prices.sessions_5d`** (list) — rolling buffer of the most recent up to five sessions, OLDEST FIRST, today's included:
  `[{"session_date", "prev_close", "bars"}, ...]` with the same bar shape. Maintained by reading the previous `prices.json`
  before writing: a re-run on the same day replaces that day's entry (never duplicates it); a sixth day drops the oldest.
  Because the dated chart endpoint returns daily bars only, 5D intraday ACCUMULATES: a name first pulled today has one session
  and reaches five after five trading days of crons. The app's 5D range should draw whatever sessions exist, separated by date.
- **`prices.warnings`** (list of strings, always present, usually empty). A failed chart call keeps the whole daily series,
  writes `intraday: null`, carries the previous `sessions_5d` over unchanged and appends one entry; `--no-intraday` carries
  BOTH the previous `intraday` and `sessions_5d` over (the block's own `session_date` shows its age) and appends one entry.
  Exit status is unaffected — the daily series is never lost because intraday failed.
- **Nasdaq `x` is NOT a true epoch.** In the no-dates chart payload `x` is the ET wall-clock encoded as if it were UTC
  (`x=1791950400000` is labelled "4:00 AM ET"; a true-epoch reading would say midnight). `decode_point()` reads `x` both ways and
  keeps the one that agrees with the point's `z.dateTime` label (wall-clock first, true epoch second; label minute wins when
  neither agrees), so a convention change on Nasdaq's side cannot silently shift the bars by four hours. `session_date` is the
  decoded ET date carrying the most points. Tests: `_system/tests/test_prices.py` (no network).
- **For `build_site.py` (other owner):** `data/<T>.json` `record.prices` carries `intraday` and `sessions_5d` verbatim (plus
  `warnings` if convenient); `trim_record` (the attachment) drops `sessions_5d` and KEEPS `intraday`. Sizes: APP's whole
  `prices.json` is ~19 KB with one session (~2 KB per session of bars), so the record grows by at most ~12 KB at five sessions.
- **Rate limit.** `--all` keeps the 0.3 s pause between names and adds a 0.1 s pause between a name's two requests
  (≈ 5 req/s worst case, under Nasdaq's 10). The user-agent, 3× backoff and 40 s timeout are unchanged.

## Decisions (statements.py + build_site.py pass-through, 2026-10-15 — Financials tab data)
Owner of `_system/statements.py`, `_system/tests/test_statements.py` and the build_site.py changes below. Additive to every shape above.
- **`<T>/statements.json`** (written by `python _system/statements.py <T> [--cik N] [--no-write] | --all [--force] [--cache DIR]`) is the
  Financials tab's full income statement, balance sheet, cash-flow statement and derived metrics over the company's WHOLE EDGAR
  companyfacts history. Shape: `{"ticker","cik","entity","as_of","currency","fiscal_year_end_mmdd","source":"SEC EDGAR companyfacts
  (filing-direct)","schema_version":1,"latest_filed":{"form","filed","period"} (the newest 10-K / 10-Q / 20-F / 40-F in the submissions
  feed — the --all skip key),"periods":{"annual":[{"end","label":"FY2025","filed"}] (oldest first, EVERY fiscal year companyfacts
  supports; `filed` is the ORIGINAL 10-K's date, not a restating comparative's),"quarterly":[{"end","label":"Q2 FY2026","fy_start",
  "filed"}] (oldest first, every derivable fiscal quarter),"ttm":{"end","quarters":[4 ends]} | null,"current":{"end"} | null},
  "statements":{"income":[LINE],"balance":[LINE],"cashflow":[LINE],"metrics":[LINE]},"warnings":[...]}`. LINE =
  `{"key","label","level":0|1|2,"total":bool,"unit":"money"|"shares"|"per_share"|"ratio"|"pct","annual":[v|null],"quarterly":[v|null],
  "ttm":v|null,"growth_annual":[...],"growth_quarterly":[...],"derived_quarterly":[bool],"tags":[us-gaap / ifrs-full tags that
  supplied values]}` plus `cf_sign` (+1 / −1) on cash-flow lines: cash-flow amounts are AS FILED (capex, buybacks, dividends,
  repayments, acquisitions are positive amounts paid), so the app negates `cf_sign: -1` lines for display. Raw units (dollars,
  shares); the app scales to millions. A line is emitted only when it carries at least one value, in the fixed spec order; a filed
  line two statements list (net_income, da, sbc) appears in both with each statement's own indent / total flag / cf_sign.
- **Line set** = the standardized list in the brief (INCOME revenue … dps, BALANCE cash … total_liabilities_and_equity, CASHFLOW
  net_income … owner_earnings, METRICS total_debt … current_ratio) plus the bank block (interest_income_total, interest_expense_total,
  net_interest_income, provision_credit_losses, noninterest_income, noninterest_expense; deposits, loans_net, allowance_credit_losses,
  investment_securities). Bank shape = the filer files `NoninterestIncome` AND `InterestIncomeExpenseNet`; banks then show the bank
  block and NOT the non-bank `interest_expense` / `interest_income` lines, and revenue = the filer's own `Revenues` total when it is
  filed for every NII period, else net interest income + noninterest income (both legs required; marked derived when either leg is).
  Lenders / brokers: the filer's own `Revenues` / `RevenuesNetOfInterestExpense` total replaces the contract-revenue line when it
  exceeds it by >5% in the latest FY (the contract line is a component for such filers). Every choice lands in `warnings`.
- **Columns.** Annual = FY-duration facts on 10-K / 20-F / 40-F (fp FY), latest filing wins per period — a restated comparative
  carries the restating filing's value, so a basis change (APP's apps divestiture: FY2023–FY2025 are continuing-ops, FY2022 and
  earlier consolidated) shows as a step in the series rather than being smoothed; quarterly = the fundamentals.py machinery
  (`quarterly_by_tag`): direct 3-month facts where filed, else YTD − prior YTD in the same fiscal year (flagged
  `derived_quarterly`), Q4 = FY − 9M; a derived quarter of a non-negative line (revenue, costs, capex, buybacks, …) that comes out
  negative is a restatement-basis artefact (FY restated, nine-month leg not) and is blanked with a warning naming the quarters. A
  period counts when at least two of revenue / net income / OCF / operating income / total assets carry it. Balance-sheet instants are
  never derived: annual = FY end, quarterly = quarter end, `ttm` = the latest quarter-end value (the app labels that column
  "Current"; `periods.current.end` names it). Per-share and weighted-share lines are never subtracted; the two exceptions are
  filed-arithmetic: fiscal Q4 weighted shares = 4 × FY − the three filed quarters when they are mutually consistent (quarters within
  25% of each other, the result within 25% of the middle one), then Q4 EPS = Q4 net income (to common when filed, else net income)
  ÷ that count rounded to the cent — both flagged derived (APP Q4 FY2025 $3.24, KR Q4 FY2026 $1.35, HBAN Q4 FY2025 $0.30). A
  filed Q4 figure is never replaced.
- **TTM** (flow lines) = the sum of the last four quarters when they are four CONSECUTIVE fiscal quarters (60–130 days apart) and
  all four carry a value, else null (`periods.ttm` is null and a warning says so when the last four are not consecutive). Shares
  lines: the duration-weighted average over the four. Per-share lines (EPS, DPS): the sum. Instants: the latest.
- **Growth.** `growth_annual[i]` = value ÷ the prior fiscal year − 1 only when the two FY ends are 300–400 days apart; `growth_quarterly[i]`
  = vs the quarter ending 365 ± 20 days earlier; null when either side is missing or the base is not positive (fundamentals.py's
  `_g`); ratio / pct lines carry all-null growth arrays.
- **Derived lines** (ebitda = operating_income + da; fcf = ocf − capex; owner_earnings = ocf − capex − sbc; total_debt;
  net_cash = cash + short_term_investments − total_debt; working_capital; book / tangible book value (+ per share on period-end
  shares, falling back to diluted weighted); fcf / owner-earnings per share (diluted weighted); gross / operating / net / fcf margin;
  roe / roa (quarterly columns use the trailing-four-quarter numerator, null when those four are not all present); roic_proxy =
  operating income × (1 − tax rate) ÷ (equity + debt − cash), tax rate = income tax ÷ pretax within 0–50%; debt_to_equity;
  current_ratio) are computed per period only from lines present in the SAME period. A component the filer has NEVER filed in any
  period (no short-term investments, no goodwill, no intangibles, no debt) counts as zero where the definition allows it; one filed in
  other periods but not this one gives null. `total_debt` = long_term_debt + (DebtCurrent aggregate, else short_term_debt +
  current_lt_debt); without a noncurrent line, the filer's combined `LongTermDebt` / `DebtLongtermAndShorttermCombinedAmount` total
  (+ short-term borrowings unless the short-term tag was itself `DebtCurrent`); the current-only sum otherwise. Totals are never
  synthesised: a missing GrossProfit, OperatingExpenses, Liabilities or LiabilitiesAndStockholdersEquity stays absent even when the
  components exist (only the "derived" lines above are computed).
- **Shares outstanding (period end)** = `CommonStockSharesOutstanding` (ifrs `NumberOfSharesOutstanding`), falling back per period to
  the cover-page `dei:EntityCommonStockSharesOutstanding` dated within 75 days after the period end (tag recorded as
  `dei:EntityCommonStockSharesOutstanding`).
- **Currency** = USD unless the money lines' units are mostly another currency (shown as filed, no FX, warning). 20-F / 40-F filers
  with no 10-Qs get annual columns only (`periods.quarterly = []`, warning). When the submissions feed shows a filing newer than
  the newest period in companyfacts, a warning names it (`latest 10-Q (period …, filed …) is not yet in EDGAR companyfacts —
  columns stop at …`) — EDGAR's API lags: on 2026-10-15 HBAN's Q2 2026 10-Q (filed 2026-07-28) and GFI's FY2025 20-F (filed
  2026-03-30) were still absent from companyfacts (re-fetched fresh to confirm), so those columns stop at 2026-03-31 / FY2024.
  Reaching such filings means parsing the filing's own XBRL instance (what segments.py does) — not done here.
- **`--all` cost rule.** For every folder with score.json: one small submissions request; the name is SKIPPED without the
  companyfacts download when the existing statements.json records the same `latest_filed` form + date and the same
  `schema_version`, unless `--force`. The run prints `N written, N skipped (…companyfacts not downloaded), N failed [T…]`; one
  failure never stops the loop (stderr `statements.py: FAILED T: …`). EDGAR rules: the Muse User-Agent, ≤ 10 requests/second
  (0.11 s floor between requests), 3 attempts with backoff, 90 s timeout; `--cache DIR` reads / writes the raw payloads there
  (tests and offline verification only). A single-name run always rebuilds. Writes are atomic (`.tmp` then `os.replace`).
- **Verified 2026-10-15** against the filings' own R pages (EDGAR Financial Report viewer), raw units: APP 10-Q 2026-06-30 — revenue
  1,923,686K, net income 1,266,538K, total assets 8,269,131K, total liabilities 5,106,115K, Q2 OCF 869,040K (= 6M 2,160,433K −
  Q1, derived), diluted shares 337,031K, cash 3,053,306K, diluted EPS 3.76; capex null because APP's cash-flow statement has no
  property-and-equipment purchase line (companyfacts has none after FY2024 — the engine's capex override exists for the same reason).
  KR 10-Q 2026-08-15 — sales 34,621M, net earnings 641M, total assets 49,491M, total liabilities 43,645M, Q1 + Q2 OCF 1,774 + 1,311 =
  3,085M and capex 1,293 + 1,144 = 2,437M (the 10-Q's 6M YTD figures), diluted shares 608M, cash 1,676M, EPS 1.05. HBAN 10-Q
  2026-03-31 — total interest income 3,086M, NII 1,891M, net income 523M, total assets 285,372M, total liabilities 252,791M, OCF
  524M, capex 124M, diluted shares 1,900,647K, EPS 0.25; cash 19,186M is `CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents`
  (the cash-flow definition incl. interest-earning deposits with banks) — "cash and due from banks" 2,096M is the narrower caption.
  GFI 20-F FY2024 — revenue 5,201.6M, total assets 10,142.9M, total liabilities 4,776.0M, OCF 1,607.0M, capex 1,183.4M, cash 860.2M,
  diluted EPS 1.38; net income 1,245.0M is `ProfitLossAttributableToOwnersOfParent` (the 1,290.5M "profit for the year" includes
  minority interests — same convention as us-gaap NetIncomeLoss). History depth: APP FY2019–FY2025 (7 FY, 26 quarters from Q1 2020),
  KR FY2008–FY2026 (19 FY, 73 quarters), HBAN FY2008–FY2025 (18 FY, 68 quarters), GFI FY2007–FY2024 (18 FY, no quarters), ZS
  FY2016–FY2026 (11 FY, 38 quarters), AEE FY2007–FY2025 (19 FY, 73 quarters). Sizes 57–266 KB per name.
- **build_site.py pass-through.** (a) `<T>/statements.json` is copied VERBATIM (NaN/inf → null, compact) to
  `_daily/site/data/<T>.statements.json` — next to the record, never inside it, never in the attachment — whenever the record is
  (re)built (the folder file is part of the mtime / file-list skip check, so a refreshed statements.json rebuilds the record) and
  also when a skipped record's copy is missing; it is removed when the folder's file is gone or malformed (not a JSON object), with
  the record when the folder no longer qualifies, and an orphan copy with no record is removed too. `has.statements` on the index
  row; `meta.counts.statements`; the summary line and `meta.notes` carry `statements N written / N removed`; `build()` returns
  `statements_written` / `statements_removed`. The app fetches `./data/<T>.statements.json` when the Financials tab opens
  (`row.has.statements` says whether to try). (b) `record.prices` gains `intraday` (object | null), `sessions_5d` (list of objects)
  and `warnings` (list of strings) verbatim from prices.json; `trim_record` (the attachment) drops `sessions_5d` and `daily_1y` and
  keeps `intraday`. (c) **Watchlist**: `meta.watchlist` = `_system/watchlist.json` tickers in FILE ORDER (upper-cased, trimmed,
  duplicates / blanks / non-strings dropped — the previous "sorted" rule is replaced; nothing reads the order); `meta.watchlist_outside`
  = those not in the universe (over $40B, no page): an entry's own `in_universe: false`, else the universe.csv membership test when
  that file is readable; `meta.watchlist_entries` = `[{ticker, in_universe, name}]` in the same order (names for the outside
  tickers, which have no index row). Without the file (or a malformed one) the list is the universe.csv `watchlist` column in
  queue order and nothing is outside. `row.watchlist` on every index row and `meta.stale` entry, re-derived every run, unchanged.
  (d) `<T>/profile.json` (profile.py) is embedded as `record.profile` (dict | null; a malformed file renders as absent) and kept in
  the attachment; `has.profile` on the row; `meta.counts.profiles`. `COMPANY_FILES` lists profile.json and statements.json.
- **Tests**: `python _system/tests/test_statements.py` (no network: an inline companyfacts fixture with two FYs / ten quarters, the
  skip rule on cached payloads, and the build_site pass-through on a temp copy of APP with `--only APP`). `test_build_site.py`'s
  watchlist and `has` assertions were extended for the file-order list and the two new flags.

## Decisions (fundamentals.py dividends block 5.4.3, 2026-10-15 — re-verification fixes)
Additive to `fundamentals.dividends` (copied verbatim into `data/<T>.json`); nothing feeds the valuation. Every figure stays a
filed value or plain arithmetic on filed values. Tests: `_system/tests/test_fundamentals_dividends.py` (36, no network).
- **`yield_basis`** (object, always present) — one entry per yield: `buyback_yield`, `net_buyback_yield`, `shareholder_yield`
  (`{"legs": {leg: basis string}, "filed": [legs summed from filed quarters], "zero": [legs taken as zero — a tag the filer never
  filed in any period], "excluded": [legs left out — not filed inside the window], "partial": [legs filed for only some of the four
  quarters], "bound": "exact" | "lower" | "upper" | "indeterminate" | null, "complete": bool, "numerator", "denominator"
  (the market-cap basis string), "note" (present when not exact)}`) and `dividend_yield` (`{numerator, basis, bound, complete,
  denominator}`). Every flow yield is built the same way — filed legs in, never-filed legs as zero, unfiled-in-window legs out —
  and a yield is null only when its own required leg is unknown (buybacks for the buyback yields; dividends AND buybacks for the
  shareholder yield). `bound` is "lower" when a positive leg is partial or missing, "upper" when the issuance leg is, "indeterminate"
  when both. **Rule for the app:** a yield whose `yield_basis[*].bound != "exact"` is shown with the bound ("≥ 0.5%", "≤ 6.1%",
  or "≈ 3.7%, incomplete") and never as a bare figure; `shareholder_yield_complete` remains `bound == "exact"` with no excluded leg.
  HBAN: `buyback_yield` 0.49% is `bound: "lower"` (repurchases filed for Q1 2026 only, $150M in the 10-Q filed 2026-04-30);
  EXPE: `net_buyback_yield` 6.09% is `bound: "upper"` (no issuance fact in the window); APP: issuance filed for 2/4 quarters → upper.
- **DPS CAGR across a suspension is null.** `dps_cagr_3y` / `dps_cagr_5y` require an unbroken run of consecutive fiscal years
  (period ends 300–400 days apart) each with annual DPS > 0 between the base year (the annual row ±45 days from N years before
  the latest) and the latest; a missing year or a filed zero inside the window gives null and `notes` names the gap
  (`dps_cagr_5y: null — the 5-year window FY2020→FY2025 has no annual DPS between FY2020 … and FY2025 … — a dividend suspension or
  unfiled years, not a growth path`). EXPE's FY2020 0.34 → FY2025 1.60 (10-K DPS facts, filed 2021-02-12 and 2026-02-13) no
  longer reads as 36%/yr. A base year simply absent (no row N years back) is null without a note; `dps_growth_yoy` likewise
  needs consecutive years.
- **Share count for the market cap, dual-class filers (TKO).** `latest_share_count` (cover-page dei count, else the balance
  sheet's) stays the rule; when companyfacts holds no undimensioned instant count at all (TKO, CIK 1973266: zero dei / balance-sheet
  share facts — both are class-dimensioned and dropped by the API) `fallback_share_count` uses the latest filed (non-derived)
  diluted weighted-average count from the last four quarterly rows or the latest fiscal year — unless a recent count exceeds it by
  >20%, in which case the LATEST count within 20% of the largest is used (a diluted count excludes antidilutive / if-converted
  units period by period: TKO's Q2 2026 three-month count is 75,870,706 against 194,631,394 in Q1 2026, 199,061,830 in Q3 2025 and
  194,011,072 for FY2025 — all `WeightedAverageNumberOfDilutedSharesOutstanding` in the 10-Qs / 10-K). `shares_basis` is
  `"instant"` or `"weighted_average_diluted_fallback"`; `shares_source` names the count used, the candidates and why;
  `market_cap_basis` repeats it; `notes` carries `shares: market cap uses the …`. `market_cap` is never null while a weighted count
  and a price exist (TKO: 172.38 × 194,631,394 = $33.55B; before this fix $13.08B on the 75.9M count). `shares_diluted` /
  `shares_diluted_source` still report the latest quarter's own diluted count beside it.
- **Unfiled-split guard needs the EPS to agree** (`basis_breaks`). A DPS move of ~1/k against a share-count move of ~k is read as a
  share-basis change only when the diluted EPS of the two years (both filed and positive) also moved ~1/k (EPS ratio × share ratio
  within 0.6–1.6); a candidate the EPS contradicts stays a cut and is listed in `basis_breaks_rejected`
  (`[{period_end, dps_ratio, shares_ratio, eps_ratio}]`) with a note. Without EPS on both sides the guard applies as before.
- **Fiscal-year labels** (`fy_label_basis`, string). Normally "calendar year of the fiscal period end (the annual table's
  convention)". When two fiscal years end in one calendar year (a 53-week year or a fiscal-year-end change, KVUE / TDY) the annual
  / quarterly tables repeat a label and `annual_dps` does not — its labels become the year most of each fiscal year falls in,
  `fy_label_basis` says so and a note names each relabelled row (`FY2022 here (period ended 2023-01-01) is labelled FY2023 in the
  annual / quarterly tables`). **Join `annual_dps` to the annual table on `period_end`, never on the label.**
- **FY DPS unit slips** (`dps_fy_facts`). When the filings that report one fiscal year's DPS disagree by a power of ten, the value
  most filings agree on wins; an even split goes to the value closest (log) to the tag's other fiscal years; the note names every
  filing on each side and which rule decided. Amended annual reports (`10-K/A`, `20-F/A`, `40-F/A`, `DPS_FY_FORMS`) count as filings
  of their period here (the statements' `annual_series` does not count `20-F/A` / `40-F/A`; the dividends block diverges on purpose
  so GFI's FY2017 is 0.08 by 2-1 — 20-F/A filed 2018-04-23 and 20-F filed 2019-03-29 — over the 8 in the 20-F filed 2020-04-06).
  A real restatement (not a power of ten) still takes the latest filing.
- **Which was stale, test or code.** `test_build_dividends_degrades_without_quarters_or_price` expected `shares_source`
  'latest annual diluted' from the pre-5.4.3 code; the contract above makes it the fallback string, so the test was updated and the
  code kept. `test_fallback_share_count_uses_the_most_inclusive_recent_diluted_count` expected TKO's Q1 2026 count; the code picked
  the oldest-and-largest (Q3 2025), so the code was changed to "latest count within 20% of the largest" — the newest consistent
  count, not the oldest. `test_build_dividends_bank_shape` and `…_no_dividend_payer…` were green against the 5.4.3 code already.

## Decisions (profile.py, 2026-10-15 — the `<T>/profile.json` store)
Choices made where the owner's schema above was silent; every one is additive to the shapes under "layout and profile"
and "Forecast tab". `build_site.py` (other owner) copies the file verbatim into `record.profile`.
- **`about.description` is an object**, `{text, source, form, filed, period, accession, url}` (the app already accepts
  either a string or an object). `source` names the section the prose came from: `"10-K Item 1 Business"`,
  `"20-F Item 4.B Business Overview"`, `"20-F Item 4 Information on the Company"` or `"20-F Overview section (integrated
  annual report without an Item 4 heading)"` — the last is the fallback for integrated reports such as Gold Fields', whose
  20-F primary document is the annual report plus a cross-reference guide and has no Item 4 heading at all; the bare
  "Overview" heading whose first 400 characters name the registrant and contain a sentence is used. The table-of-contents
  (or cross-reference-table) occurrence of a heading is the one followed by the next item with no sentence in between; a
  short real section followed by Item 1A within 300 characters is still the real one. Page numbers, stray punctuation
  ("BUSINESS." leaves a lone ".") and short sub-heading lines ("Overview", "General Business Description") under the item
  heading are dropped, and the prose stops at the next sub-heading once 300 characters have been collected, then is cut at
  a sentence boundary at ≤ 1,500 characters. A 40-F's primary document is a wrapper: description null with a warning.
- **`about.employees` is an object**, `{count, as_of, evidence, form, filed, url[, basis]}`; `as_of` is ISO when the
  sentence carries a date, a bare year for a year-average count. Three filed forms, in order of preference: (1) "As of
  <date>, we had approximately N employees"; (2) "<Name> had N average full-time equivalent colleagues during 2025"
  (`basis: "average full-time equivalent for the period"`); (3) the integrated-report bullet "N employees (2024: N)" —
  the prior-year comparative is what marks it as the headcount — dated by the filing's fiscal period end
  (`basis` says so). A figure with a percentage or a department qualifier attached ("380 employees, or 42% of our
  headcount, involved in research") is a subset and never wins; a count without a date or comparative is not evidence;
  null otherwise (AEE's 10-K states no headcount sentence → null, by design). The evidence is the one sentence (or the
  one bullet), with a run-on heading stripped.
- **`about` extras**: `entity` (EDGAR name), `cik`, `region`, `exchanges` (all from submissions), `address`
  `{street, city, state, zip}`, `phone`, `former_names` (≤ 5). `exchange` prefers the Nasdaq summary's (e.g. `NASDAQ-GS`)
  over the submissions list. `website` = submissions `website` else the Nasdaq `CompanyUrl`.
- **`market` extras**: `previous_close`, `one_year_target`, `annualized_dividend`, `ex_dividend_date`, `dividend_pay_date`
  (ISO) — all from the quote summary; `N/A` → null.
- **`street` details**: `analysts` is the count in `ratingsSummary` ("Based on 16 analysts…"), falling back to
  buy + hold + sell; `consensus` is `meanRatingType`, falling back to the latest history row's label. Nasdaq's
  `historicalConsensus.x` is a true UNIX epoch in seconds here (unlike the chart endpoint), used only when `z.date` is
  unparseable. `eps_forecast` rows carry `period` (Nasdaq's label) and `fiscal_end` (`YYYY-MM`). `next_earnings` adds
  `timing` ("after market close" / "before market open" / null); the `date` is null when Nasdaq's text says the vendor
  has not provided one. `surprise_pct` is null when the consensus is 0 (no ratio on a zero base). **Nasdaq placeholders
  are not figures**: estimate-momentum publishes 999 for "no estimate" (GFI's quarter) → null; quote/eps rows with
  consensus 0 AND earnings 0 (every row for a name Zacks does not cover — GFI) are dropped; both add a `warnings` entry.
  A genuine zero consensus with a non-zero actual is kept. `brokers` are Nasdaq's abbreviated broker names.
- **`filings` entries** add `accession`; the description for an amendment is `"Amendment: …"`; 8-K item 9.01 (exhibits)
  is listed in `items` but not described unless it is the only item; unknown codes read `"Item X.XX"`; the non-8-K forms
  read "Annual report", "Quarterly report", "Annual report (foreign private issuer)", "Annual report (Canadian issuer)",
  "Report of a foreign private issuer", "Registration statement", "Proxy statement". Only the eight owner-listed forms
  (and their `/A` amendments) appear, newest first, at most 20.
- **Top-level extras**: `cik`, `fetched_at` (ET, seconds), `newest_filing_date` (the skip check's key), `sources`
  (every URL used; a failed Nasdaq endpoint reads `"FAILED: <url>"`) and `warnings` (always a list).
- **Refresh and failure policy**: `--all` walks every folder with a `score.json`; a name is skipped when its
  `profile.json` `as_of` is younger than `--max-age-days` (default 7, ET dates) AND `newest_filing_date` equals the
  newest `filingDate` in the submissions feed (one small request per name); `--force` rebuilds all. A single-name run
  exits 2 with no CIK (`--cik` > `dcf_numbers.json` > `sec_tickers_exchange.json` > `universe.csv`), 3 when the
  submissions feed is unreadable (nothing written); an unreadable annual document or any Nasdaq failure still writes the
  file with the affected block null and a warning. Rate limit: ≥ 0.11 s between requests to the same host (≤ 10/s),
  three attempts with 1 s / 2 s backoff, EDGAR timeout 90 s, Nasdaq 40 s, 0.5 s pause between names under `--all`.
  Writes are atomic (`.tmp` + `os.replace`, retried on Windows locks). Tests: `python _system/tests/test_profile.py`
  (no network).

## Decisions (prices.py review round, 2026-10-15 — stale prev_close, the lost 16:00 print, partial sessions)
Fixes from the adversarial review of the intraday capture. Each is additive to the shapes above; where a sentence in the
2026-10-15 intraday section above now reads differently, THIS section wins.
- **`prev_close` is the filed daily close strictly before `session_date`**, i.e. the same series `stats.prev_close` uses —
  NOT Nasdaq's `data.previousClose`. Reason: before the regular open the chart endpoint already serves today's session but
  `previousClose` still holds the close of TWO sessions ago (verified 2026-10-15 08:40–08:51 ET on APP, KR, HBAN, ZS, AEE,
  GFI: session 10-15, previousClose = the 10-13 close, while the file's own `daily_1y[-1]` is the 10-14 close). The sweep
  touches names at any hour, so pre-market captures are routine; with the old rule the 1D return read −4.95 % for APP
  instead of −1.29 %. Nasdaq's value is kept verbatim as **`prev_close_nasdaq`** and used only when the daily series has no
  row before the session (a name listed today); **`prev_close_source`** says which (`"daily close 2026-10-14"` | `"nasdaq"`).
  A disagreement beyond rounding (0.005) appends a `warnings` entry (`prev_close: Nasdaq previousClose 272.28 differs from
  the daily close 262.19 (2026-10-14) before session 2026-10-15; daily used`). These fields are in `intraday`; `sessions_5d`
  entries carry the reconciled `prev_close` only. The app's 1D dashed line and period-return base keep reading `prev_close`.
- **Bars are keyed by the bucket's END minute (right-closed)** — `bar_key: "end"` on the block and on every entry written
  from now on. Prints 15:56–16:00 → 960 (so the 16:00 closing print is the regular segment's last bar instead of being
  overwritten by the 16:01–16:04 after-hours prints), 16:01–16:05 → 965, 9:26–9:30 → 570 (the opening print), 19:56–19:59
  → 1200, 4:00 → 240. The shading rule for the app becomes: pre-market = key < 570, regular = 570 … 960 inclusive,
  after-hours = key > 960 (the app's region shading `[domain0, 570]` / `[960, domain1]` already draws exactly that, and its
  session window is 240 … 1200). Entries written by the morning-of-2026-10-15 version carry no `bar_key` and are keyed by
  bucket START (their 955 bar = prints 15:55–15:59); they are left verbatim (never re-keyed — that would be a guess) and
  age out of the five-day buffer by 2026-10-22. The app treats both the same (x = key); the difference is a ≤ 5-minute
  offset on those legacy days.
- **`close`** (official regular-session close) on `intraday` and on every `sessions_5d` entry, with **`close_source`**:
  the filed daily close ON `session_date` when the daily series already has that row (`"daily close"`), else
  `data.lastSalePrice` once the session is past 16:00 (`"nasdaq lastSalePrice"` — after the close that field is the official
  last sale: HBAN 2026-10-14 lastSalePrice 15.10 = the daily close while the 19:58 after-hours print was 15.11), else null
  (during pre-market and the regular session `lastSalePrice` is the live print). Every run backfills `close` on stored
  entries that lack it from the daily series, so a partial entry gets its official close the next morning even though its
  bars stay partial. The 5D chart should end each day's regular segment at `close` when present.
- **`captured_at`** (ET ISO, = the file's `fetched_at` clock) and **`complete`** (bool) on `intraday` and on every entry.
  `complete` is true when the last 1-minute print is at/after 19:55 ET or the capture happened at/after 20:00 ET of
  `session_date` (or on a later date) — the endpoint keeps serving the finished session until the next pre-market (observed
  at 02:07 ET). Legacy entries get `complete` derived from their own last bar (≥ 1195). The app can label a day
  "partial (to HH:MM)" from `complete` + the last bar.
- **A session's bars end at the time of the last run that day.** The endpoint serves only the CURRENT session, and the next
  morning it has moved on, so a day captured only during trading hours stays partial forever. Under today's crons
  (live-refresh 09:30–16:30 ET every 30 min; the sweep at any hour; daily ranking 19:07, i.e. with after-hours still live)
  NO run lands between 20:00 and 03:59 ET, the only window that yields a complete day. **Required (automation owner):**
  one `python3 _system/prices.py --all --quiet` between 20:00 and 03:59 ET (e.g. 20:15), or move the daily-ranking job's
  prices step past 20:00; until then every `sessions_5d` entry is `complete: false` and the 1D chart of a name the sweep
  touched at 10:00 freezes at 10:00 until the next touch. `prices.py` itself cannot schedule anything.
- **`merge_sessions` never shortens a stored session.** The same-date entry on disk is KEPT when its last bar is later
  than the new capture's, or equal with more bars (a later capture of one session is a superset), and a `warnings` entry
  says so (`sessions_5d: the stored 2026-10-15 entry (captured …, last bar 08:51) reaches further than this capture …;
  stored entry kept`). The `intraday` block itself is always the current capture (it is "what Nasdaq says now": `last`,
  `last_sale`, `time_as_of`). This guards an out-of-order or concurrent run; it is not a substitute for the post-20:00 run.
- **For `build_site.py` (other owner, still open):** `record.prices` must pass `intraday`, `sessions_5d` and `warnings`
  through (build_site.py:469 whitelists `source, as_of, currency, stats, weekly, daily_1y` only) and `trim_record` should
  drop `sessions_5d` as it drops `daily_1y`. Until that lands the site shows "Intraday (1D · 5D) not captured yet" for every
  name although the files carry the sessions. The new per-entry fields add ~120 bytes per session.
- **Tests:** `_system/tests/test_prices.py` (no network, no writes in the repo; the clock `now_et()` and both fetchers are
  monkeypatched) covers the 959 / 960 / 961 boundary, the pre-market payload (`prev_close` == `daily[-1]` close, warning
  names Nasdaq's stale value), `complete` by print and by capture time, `close` by daily row and by lastSalePrice, the
  merge guard, legacy-entry handling and the backfill.

## Decisions (static app — statements viewer, watchlist, dividends, phone containment, 2026-10-15)
Choices made in `app.js` / `app.css` / `tests/` for the Financials statements viewer, the watchlist and the Dividends review findings; none changes a data shape. What already existed from the earlier rounds (Forecast sub-tabs, the "★ Watchlist N" toggle between the tier and fit segments with per-device stars, the compact hero + sticky tab bar, the About / Financial performance / Street summary / Filings cards) is kept as is.
- **Statements viewer = the first card of the Financials tab**, above the existing TTM tiles and quarterly / annual summary cards (every one of those stays). It renders `data/<T>.statements.json` (schema in the task brief: `periods.annual/quarterly/ttm/current`, `statements.income/balance/cashflow/metrics`, each LINE with `annual[]`, `quarterly[]`, `ttm`, `growth_*`, `derived_quarterly[]`, `level`, `total`, `unit`, optional `cf_sign`). The file is **fetched on demand the first time the Financials tab opens** (`ensureStatements`, cached per ticker in `D.statements`; a loading row is shown until it arrives; HTTP 404 → "not built yet" note naming statements.py / build_site.py; any other failure → error note). In the attachment (`SITE_DATA`) no fetch happens: the card says the full statements are on the site and links to `<meta.site_url or index.html>#<T>.financials`. The view state (statement · period · growth rows) is shared across company pages in memory; the opened line resets per ticker.
- **Columns are newest first.** Header = period label + its end month ("FY2025" / "Dec '25"; "Q2 FY2026" / "Jun '26"). The TTM view puts ONE leading column first: "TTM · to Jun '26" (`line.ttm`) for income / cash-flow / metrics, "Current · Jun '26" (the latest quarter-end instant, `periods.current.end` else the last quarterly end) for the balance sheet; then the fiscal years. Without a `periods.ttm` (quarters not consecutive) the flow statements show no TTM column and the units note says so; the balance sheet keeps "Current". The metrics note states that flow-based metrics are TTM and balance-based ones are at the latest quarter end.
- **Formatting (`stmFmt`)**: money and shares in millions — no decimals from 100 M, two below; per-share two decimals; ratios two; percentages one; negatives with a leading minus; empty cells "–". Growth rows (toggle) are a `tr.sub.growth` "YoY growth" line under every line that has a growth value, signed and coloured; the TTM column carries no growth. Derived quarters carry a † with a legend line. Lines with no value in the selected periodicity are dropped from that view (a `dps` line with annual facts only does not appear in Quarterly).
- **Cash-flow sign**: lines with `cf_sign: -1` (capex, buybacks, dividends, repayments, acquisitions, investment purchases) are displayed as negatives — the file stores them as positive amounts paid, as filed; the units note says so. Growth figures are the file's (computed on the filed positive amounts).
- **Sparkline**: a line's label is a `<button class="stl" aria-expanded>`; tapping it renders a card **directly below the table** (all widths — an in-table row would scroll sideways with the table on a phone, so the card sits under the `.twrap` and is scrolled into view on screens under 760 px) charting the line over the selected periodicity (the TTM view charts the fiscal years) with the existing `drawChart` (bars for money / shares, a line for per-share / ratio / pct; `yfmt` `cnt` added for share counts so they are not printed with a `$`), with a close button; tapping the same label again closes it.
- **Phone containment (Segments tab measured at scrollWidth 684 vs 375).** The only element in that pane with an intrinsic width above the viewport is `table.fin.segt` (`min-width: 640px` + nowrap cells; 16 body + 14 card + 640 + 14 = 684 is exactly that table laid out uncontained). Fixes in `app.css`: (1) `.pane{min-width:0;max-width:100%;overflow-x:hidden;overflow-x:clip}` — a tab pane can never widen the page, `clip` so no scroll container is created and the sticky label column keeps working inside `.twrap`; (2) `.card{max-width:100%}`, `.twrap{min-width:0}`, `.chart{min-width:0}`, `svg{max-width:100%}`, legend items and notes `overflow-wrap:anywhere`; (3) the sticky rule was `table.fin th` — EVERY header cell, so the period headers piled up at the left edge on scroll — it is now `table.fin tbody th, table.fin thead th:first-child` (the row-label column only). `tests/app.test.js` reads `app.css` and asserts these rules and that every `min-width` above 320 px sits on `table.fin` / `#t` (both always inside a `.twrap`).
- **Watchlist**: the repo list = `meta.watchlist` ∪ index rows with `watchlist: true` (`repoList`); viewer stars persist under `localStorage["stocks.watchlist"]` (JSON array of tickers; every read / write in try/catch; the earlier key `oe-dcf.stars.v1` is read once, merged and removed). Repo rows show a fixed blue repo star (not a toggle — the file is the source of truth); every other row and the company hero carry the gold ☆/★ toggle (`starButtonHTML`, the hero one `.hstar`; repo names show the "★ Watchlist repo" chip in the hero instead). The "★ Watchlist N" toggle counts repo ∪ starred; "Copy tickers" next to it copies the combined list (`watchTickers`: index order first, then starred / repo tickers absent from the index A–Z, deduped, upper-cased) via `navigator.clipboard.writeText`, falling back to a read-only input with the text selected when the API is missing or refuses. `filterSortIndex`, `renderListRowsHTML`, `renderRowHTML`, `watchCount`, `watchButtonHTML` take `repo` as an extra trailing argument (`renderListHTML` derives it from `meta`), so the earlier three-argument calls still work.
- **Dividends review findings**: (i) "No dividend" is decided from `frequency` and the absence of dividends paid / DPS history — `payer = frequency === 'none' ? dividends_paid_ttm > 0 : (any DPS fact in history / annual_dps || dividends_paid_ttm > 0)`; never from `dps_ttm` being null. CCL (quarterly, `dps_ttm` null after the staleness rule) and TKO (`frequency` null, dividends paid, per-share rate untagged) render as payers with a "Pays a dividend — no trailing-twelve-month per-share figure" card naming what IS filed, "—" yield tiles that point to the notes, and "Not inferable" frequency. (ii) Filed per-share dividends print at their filed precision via `fmtDps` (at least two, at most four decimals, float noise trimmed: $0.155 stays $0.155) — in the history table, the tiles, the quarterly DPS rows and the DPS chart (`yfmt: 'dps'`). (iii) The meta line under the tiles names the share basis the block used (`shares_source`, count, `shares_as_of`) and the market cap on that basis (`market_cap_basis`), and says in one line that the header's market cap uses the engine's diluted count at the last close, so the two can differ.
- **Test suite note**: the pre-existing `drawPrice` assertion expected an integer period return; the price-chart owner's `fmtRange` prints one decimal under 100%, so the regex now accepts decimals (`drawPrice` itself untouched).
- **Data-layer dependency (resolved during the round)**: `build_site.py` now copies `<T>/statements.json` to `data/<T>.statements.json` and sets `row.has.statements`; the app skips the fetch and shows the "not built yet" note straight away when `has.statements === false`, and fetches otherwise (404 → the same note). The viewer was verified against the served `data/APP|HBAN|KR.statements.json` as well as scratch fixtures generated from `statements.py`'s `build_statements()`; nothing was written into any company folder by the app work.

## Decisions (profile.py review round, 2026-10-15 — sign, IPO proxy, cover address, headcount forms, NaN)
Fixes to the `<T>/profile.json` store after the adversarial review; every shape change is additive. The earlier
profile decisions above stand except where this section says otherwise.
- **`street.eps_history[].surprise_pct = (actual − consensus) / |consensus| × 100`** (supersedes "actual / consensus − 1"):
  on a negative consensus the old ratio flipped the sign, so a beat read as a miss (ZS Oct 2025: consensus −0.05,
  actual −0.01 → now +80.0, as Nasdaq's own earnings-surprise endpoint publishes it). Still null on a zero consensus.
  The app's own fallback (`actual / consensus − 1`, used only when `surprise_pct` is absent) has the same flaw and is
  the app owner's to align; every file profile.py writes carries the field, so the fallback never fires for them.
- **`about.first_sec_filing` is the earliest registration / listing form**, published with its form in
  `about.first_sec_filing_form`: S-1, F-1, S-11, 10-12B, 10-12G, 20FR12B, 40FR12B, 8-A12B, 8-A12G, 424B1, 424B4 (and
  their `/A`). A private-placement Form D or a confidential DRS draft never wins (APP: S-1 2021-03-02, not the 2018 Form
  D; ZS: S-1 2018-02-16, not the 2017 DRS). When a periodic report (10-K, 10-Q, 8-K, 20-F, 40-F, 6-K, DEF 14A, 10-K405,
  10-KSB, 10-QSB) precedes the earliest registration form the company was public before EDGAR and the overall earliest
  filing of any form is used instead (KR 1994-01-07 424B5, HBAN 1994-02-14 SC 13G, AEE 1995-11-13 S-4). Paginated
  submissions files are fetched OLDEST first and the walk stops once a registration form has been seen (one request for
  a post-2008 IPO, every page for a pre-EDGAR name; an unreadable page falls back to its `filingFrom` with a warning).
  The app may label the line "<form> <date>" instead of the bare "IPO-date proxy".
- **`about.headquarters` / `about.address` come from the annual filing's inline-XBRL cover** (the filed
  `dei:EntityAddressAddressLine1/2/3`, `CityOrTown`, `StateOrProvince`, `Country`, `PostalZipCode` tags of the same
  10-K / 20-F the description is read from; tags stripped, a trailing comma dropped — HBAN's city tag reads
  "Columbus,"), falling back to the EDGAR submissions business address. `address` adds `country` and `source`
  ("annual filing cover" | "EDGAR submissions"), and `form` / `filed` when it is the cover's. State is the filed
  spelling ("California" on ZS's cover, "OH" on KR's). ZS now reads San Jose, CA 95134 (the 10-K cover) where the
  submissions feed said Santa Clara; KR's zip 45202 (cover) where the feed said 45201. A document without the tags
  leaves a warning and the submissions address.
- **`market.ex_dividend_date` / `dividend_pay_date` parse Nasdaq's text dates** ("Sep 17, 2026" → 2026-09-17;
  MM/DD/YYYY still accepted). Nasdaq's quote summary carries the dividend keys only for Nasdaq-listed names; for an
  NYSE-listed name (KR, AEE, GFI) the summary has no `Yield` / `ExDividendDate` key at all and the fields stay null —
  the filed dividend record is `fundamentals.json`'s dividends block, not this one.
- **Employees extractor, four forms and a ranking.** Form 4 is the multi-year 20-F sentence "As of December 31,
  2023, 2024 and 2025, we had a total of 517,124, 570,895 and 776,682 employees, respectively" (JD): the LAST number
  dated with the LAST year and the stated month/day. `basis` reads "average full-time equivalent for the period" only
  when the sentence says *average*; a point-in-time FTE count (EQT: "As of December 31, 2025, we had 1,523 full-time
  equivalent employees") reads "full-time equivalent as of the stated date". Candidates are ranked (subject, geographic
  qualifier, form, anchor proximity, position): a first-person subject ("we", "the Company", or a proper noun sharing a
  word with the EDGAR registrant name — `extract_employees(text, period, entity)`; "Con Edison and its subsidiaries"
  counts) beats any other proper noun, so a subsidiary's "Acme GmbH had 380 employees" loses to the registrant's
  sentence wherever it sits; a figure followed by "in <Place>" without "worldwide / globally / in total / across" ranks
  below an unqualified one and a per-country breakdown ("2,100 employees in the United States and 3,400 employees in
  India") is never the total (null, never summed); a year-average sentence whose subject is a proper noun other than
  the registrant is dropped outright ("Hurricane Milton had 150 workers in 2024 displaced"). The subject never spans
  a line break, so a heading above the sentence is not part of the evidence.
- **`html_to_text` drops inline tags instead of spacing them**: `span`, `b`, `i`, `u`, `em`, `strong`, `a`, `font`,
  `sup`, `sub`, `small`, `big` and `ix:*` vanish (EDGAR documents keep their whitespace inside the spans), block tags
  still break lines. Words and numbers split across spans ("2</span><span>025", "It<span>em 1. B</span>USINESS") are
  read whole: ED's 15,407 headcount and IBKR's / TKO's Item 1 heading were lost to the old spacing.
- **Table-of-contents detection is sentence-based.** An Item 1 heading is the TOC occurrence when the next item label
  (`Item 1A`, `Item 1(a)` — Halliburton's labels — `Item 1B/1C`, `Item 2`, within 600 characters) follows with no
  sentence of ≥ 12 words closed by a period in between; page numbers, "Item 1(a). Risk Factors" labels and an index
  of the section's sub-headings ("A. Overview … E. Industry and Market Data", Carnival) are not sentences. The real
  section must show such a sentence in its first 700 characters (`_reads_as_prose`), the body is cut at "Item 1(a)
  Risk Factors" as well as "Item 1A", and an indexed sub-heading ("A. Overview") under the heading is dropped like
  any other sub-heading. Verified live on HAL and CCL (both now the filed prose) and unchanged on APP, KR, HBAN, ZS,
  GFI, AEE, IBKR, TKO, EQT, ED, JD.
- **Numbers and JSON hygiene**: `num()` accepts only a finite decimal literal — "NaN", "Infinity", "-inf", "1_000"
  → null (a NaN crashed `intnum`; an inf serialised as `Infinity`, invalid JSON for the browser); `write_atomic`
  passes `allow_nan=False` so no such value can ever reach the file. `run_one` fetches the submissions feed itself
  (exit 3 when unreadable, nothing written) and an exception inside the build is reported as "build failed
  (<type>: <msg>)" with the traceback, **exit 4** (nothing written) — no longer mislabelled as a submissions failure.
- Tests (`python _system/tests/test_profile.py`, no network) carry fixtures for each case: ZS's four negative-consensus
  rows, APP's D → DRS → S-1 → 424B4 sequence and Kroger's pre-EDGAR sequence, pagination order and early stop, the ZS
  and HBAN cover tags, HBAN's text dividend dates, the HAL and CCL tables of contents, the JD / EQT / ED / subsidiary /
  per-country / Hurricane sentences, NaN / Infinity / underscore numbers and the `allow_nan` guard.

## Decisions (static app review round 2, 2026-10-15 — statements viewer phone fixes, negative zero, focus, re-mount)
Fixes from the adversarial review of `app.js` / `app.css` / `tests/app.test.js`; none changes a data shape. Verified with `node _daily/site/tests/app.test.js` (44 tests, including a sweep over every served `data/*.statements.json`) and a real-browser pass at 375×812 over every tab of #APP (Overview, Financials, Dividends, Segments, Forecast): `document.documentElement.scrollWidth === 375`, no element outside a scroll container reaches past the viewport.
- **Opaque sticky labels on total rows.** `table.fin tr.strong th` now sets `background:var(--cardstrong)` (`#191C22` = `--card` blended with the 2% white the strong cells use) instead of the translucent `rgba(255,255,255,.02)` that is kept on `tr.strong td` only; the scrolled numbers no longer print through "Revenue" / "Net income" on a phone. The CSS test refuses any rule on a `tr.strong th` selector that sets an rgba background.
- **Controls wider than a phone wrap; the pane still clips.** `.ranges` is `display:flex;flex-wrap:wrap` (`.pcbar>*{min-width:0;max-width:100%}`), so 5Y and Max land on a second row at 375 px instead of being clipped; the period-return badge (`.rb`) renders on its own line under the active range. `.stmbar .seg{flex-wrap:wrap;max-width:100%}` with `button{flex:1 1 auto}` wraps Income · Balance sheet · Cash flow · Metrics inside a phone-width card. `.pane{overflow-x:clip}` stays — it is the guarantee that nothing widens the page — so any new strip-like control must wrap or live in a `.twrap`.
- **Negative zero never prints.** The minus sign is decided on the ROUNDED text (`minus(v, txt)`: `-` only when `v < 0` and the text has a non-zero digit) in `stmFmt`, `fmtPct`, `fmtPts`, `fmtX` and `fmtMoney`; `-4,000` in millions is `0.00`, `-0.0004` growth is `0.0%` / `+0.0%` signed. `stmFmt`'s 100 M switch (no decimals) is decided on the rounded value, so 99.995 M prints `100`, not `100.00`. The test sweeps every served statements file × 4 statements × 3 periods for `-0`, `-0.00`, `-0.0%`.
- **The sparkline survives a re-mount.** `companyCharts(record, stm)` (exported, node-tested) = `chartSpecs(record)` plus the `stm-spark` spec when the cached statements state is `ready` with a line open; `mountCompany` uses it, so back-to-the-ranking-and-return or Overview → Financials later in the session draws the open line's chart instead of "No data." The open line still resets only on a statement switch (unchanged).
- **Keyboard focus is kept across redraws.** `focusKey(el)` (pure, node-tested) names a redrawn control by selector — line button, statement / period segment button, Growth-rows checkbox, chart close button, ☆/★ star, the watch toggle; `redrawStatements(focusSel)` and `refreshRows()` remember the focused control before replacing markup and re-focus it (`focus({preventScroll:true})`) after; closing a chart with its × returns focus to the line it belonged to. The open line's `.stl` button carries `aria-controls="stmspark"` (only while the region exists — a closed line does not point at a missing id).
- **Attachment without `meta.site_url`.** `build_site.py` does not emit `site_url` (meta.json has none), so the embedded statements card no longer links to a relative `index.html` that does not exist next to the attachment: it says "open <T>'s Financials tab on the site" with no link, and links to `<site_url>#<T>.financials` only when the data layer provides the URL. **Open for the build_site.py owner:** emit `meta.site_url` (the GitHub Pages URL) so the attachment and `renderMissingHTML` can link.

## Decisions (fundamentals.py dividends block 5.4.4, 2026-10-15 — adversarial-review fixes)
Additive to `fundamentals.dividends` (copied verbatim into `data/<T>.json`); nothing feeds the valuation. Every figure stays a filed value or
plain arithmetic on filed values. Tests: `_system/tests/test_fundamentals_dividends.py` (45, no network; the 5.4.4 fixtures are shaped like
TSCO, NVDA, CTAS, AVGO, LRCX, WMT and CCL). Re-run on APP, KR, HBAN, ZS, GFI, AEE, CCL and TKO (`python _system/fundamentals.py <T>`).
- **One split, however many context dates it is tagged at** (`split_events`). `StockholdersEquityNoteStockSplitConversionRatio1` facts with the
  same ratio within 180 days of the event's first date are ONE event at that date (TSCO's 5-for-1 at 2024-12-05 / 12-20 / 12-28; NVDA's 4-for-1 at
  2021-06-03 / 07-19 and 10-for-1 at 2024-05-31 / 06-30); a `notes` line names the folded dates. A second guard in `split_direction`: two events
  that rest on the same pair of filed diluted counts (last FY filed before, first filed after) are one split when their compounded ratio overshoots
  the observed count move by more than 1.5x — the later ratio fact is left out and noted. Before this every date compounded (TSCO's FY2021 DPS
  2.08 → 0.01664 instead of 0.416, growth_years 16 and a 138 %/yr CAGR; NVDA ×16 / ×100).
- **The basis changes at the first post-split filing, not at the ratio fact's date** (`share_refilings`, `split_filing_cutoffs`). Filers tag the
  ratio at the approval / record date (CTAS 2024-05-02, split distributed in September; KR 2015-06-25 with a pre-split 10-Q filed 2015-06-30). The
  first filing that re-files a period's diluted weighted-average count ×≈ratio (within 10 %, −200..+400 days of the ratio date) is the cutoff:
  `split_adjustments[*].first_post_split_filing` (CTAS 2024-10-04, KR 2015-09-22, TSCO 2025-02-20, AVGO 2024-09-11, LRCX 2024-10-28, WMT
  2024-03-15); `split_factor` divides facts last filed before it; without evidence the ratio date stands. CTAS FY2022 is 0.95 (was 3.80 → a
  phantom 70 % cut, a `basis_breaks` entry on FY2023 and growth truncated to FY2023 on). `splits` tuples carry (date, ratio, cutoff); two-tuples
  still work.
- **A split restatement is not a unit slip** (`split_restatement`, inside `dps_fy_facts`). When one period's filings disagree by exactly a split
  ratio — a filed ratio (direction-checked) dated before the newer group's first filing, or the diluted count re-filed by the same factor between
  the two groups — the latest filing on the new basis wins and the note says `restated for the 10-for-1 split effective …`; the 5.4.3 majority
  rule applies only when no such share-basis evidence exists (GFI's FY2017 0.08 stays by 2-1, shares unchanged). AVGO FY2022 1.64 (not 16.4),
  NVDA FY2023 0.016, LRCX FY2023 0.69, WMT FY2022 0.7333. The restated value is already on today's basis, so `apply_splits` never divides it again.
- **DPS basis per period, not per filer** (`dps_basis`, `dps_basis_detail`, `kind` on every `history` and `annual_dps` row). The PRIMARY basis is
  the tag with the newest fact (declared on a tie); the other tag extends the series only OUTSIDE the primary's span — before its oldest or after its
  newest fact — never interleaved inside it (a declared Q4 and a paid Q1 can be the same dividend). `dps_basis` is `declared` / `paid` when one tag
  is used and `mixed` when both are, `dps_basis_detail` names the periods each covers and a note warns that the switch year can double-count or skip
  one payment. AVGO (declared facts end FY2020, CashPaid runs FY2016..FY2025 with quarters to 2026-08-02): primary = paid, annual_dps FY2016..FY2025,
  dps_ttm 2.54, quarterly, 9 growth years — no longer "dividend suspended" with a history stopping at FY2020. GFI reads `mixed` (paid 2007..2014,
  declared 2015..2024, both USD/shares).
- **Frequency: the fiscal year is bounded by the previous fiscal year's period end** (annual table, else `annual_dps`; the 400-day look-back only
  when neither exists), so the prior year's Q4 fact no longer joins the count; `frequency_basis` prints the window. **dps_ttm: a FY fact newer than
  the latest quarterly fact wins** over the four-quarter sum (a filer that stopped tagging the Q4 fact: prior Q4 + Q1..Q3 is older than the year
  itself) — the FY rollforward path is used and the note says `the FY DPS fact (period ended …) is newer than the latest quarterly DPS fact (…)`.
  Reviewer scenario S1 now reads quarterly / 1.40 (was irregular / 1.35).
- **Frequency: staleness applies to the latest positive fact only.** The spacing is read from the trailing run of positive facts (consecutive gaps
  ≤400 days — a suspension ends the run), the last four of them whatever their own age; `frequency_basis` names them and lists the quarters filed as
  zero inside that span (`…; quarters filed as zero: 2025-07-31, 2026-07-31`). WMT (the year's dividend declared in Q1, zeros after, 457 days between
  positive facts) reads `annual` with dps_ttm 0.99; a reinstated payer with one fact after the gap still gets the "single quarterly DPS fact so far"
  note and `frequency` null; a stale latest fact still reads suspended / irregular.
- **Partial flow legs use the filed year-to-date facts** (`ytd_cover`, `ctx.flow_facts` = `duration_facts` per flow, built in `main()`). When a
  leg is not filed for all four quarters, the longest filed YTD fact whose span is whole window quarters (its end a window quarter's end, its length
  that quarter's fiscal rank, the fiscal year's first quarter inside the window) is the leg's value plus the filed quarters outside its span; only
  quarters no filed fact covers are missing. `legs[k].basis` names the fact (`3/4 quarters covered (the nine-month year-to-date fact
  2025-12-01..2026-08-31 = 929.0M (PaymentsForRepurchaseOfCommonStock, filed 2026-09-29)) — a lower bound`), the `*_ttm` note says which quarters it
  covers, and when the YTD + filed rows cover all four the leg is exact and `buybacks_ttm` etc. is filled from it. CCL: buyback_yield ≥ 2.66 % (929M
  / 34.92B; was 1.57 % from the single derived Q3), shareholder_yield ≈ 4.43 % incomplete (was 3.34 %). TKO: ≥ 3.01 % (six-month fact + the filed
  quarter). HBAN is unchanged at ≥ 0.49 % (repurchases filed for one quarter only).
- **`yields_display`** (object, always present) — `{dividend_yield | buyback_yield | net_buyback_yield | shareholder_yield: {value, bound, prefix,
  label, note}}`: `label` is the figure with its bound already applied (`"4.11%"`, `"≥ 2.66%"`, `"≤ 2.78%"`, `"≈ 4.43% (incomplete)"`, `"—"` when
  null), `prefix` is `""` / `≥` / `≤` / `≈`, `note` is the partial / excluded legs' basis strings (the dividend yield's: `dps_ttm_basis`, or the
  note that explains the null). **Rule for the app and for `build_site.py`'s ranking row:** print `yields_display[name].label` (and `note` as the
  subtitle when `bound != "exact"`) — never the bare `buyback_yield` / `shareholder_yield` number, and never "no buyback filed" when the leg has a
  value. Until `app.js` / `build_site.py` adopt it the Dividends tab and the ranking row still print HBAN 0.49 %, CCL 2.66 % and TKO 3.01 % bare;
  the data now carries the display string so that change is a one-line swap on each side.
- **Not changed, on purpose.** NVDA's FY2016 declared fact is 0.115 (one quarter's rate tagged with the FY context, restated ×40 → 0.002875) against
  FY2015 0.0085 — a filed value shown as filed, so `last_cut_fy` 2016 stands; the 10x outlier rule does not catch a 3x drop and inventing a
  correction would be an estimate. CTAS FY2021 1.2525 (filed 5.01 ÷ 4) likewise. ZS's shareholder yield reads `≥ −0.18 %` (dividends never filed =
  zero, buybacks not filed in the window = excluded as a lower bound, issuance filed): the 5.4.3 bound semantics, now visible in the label.

## Decisions (static app — price chart, 2026-10-15: stockanalysis-style ranges, intraday 1D / 5D, crosshair)
Owner of the chart in `app.js` (`priceSpec`, `selectRange`, `priceRanges`, `defaultRange`, `drawPrice`, `drawPriceCard`, the crosshair
functions, `renderPriceChart`), its CSS and `tests/app.test.js`'s chart block. Reads `record.prices` as the prices.py sections above
describe it (`daily_1y`, `weekly`, `intraday`, `sessions_5d`); nothing here is a valuation figure. Verified with
`node _daily/site/tests/app.test.js` (51 tests; the chart block runs every available range over every served record) and in the browser on #APP.
- **Ranges** 1D · 5D · 1M · YTD · 3M · 6M · 1Y · 5Y · Max as one segmented row (`.ranges button[data-r]`), the active button carrying the
  period-return pill (`.rb.pos/.neg`). Data per range: 1D = `prices.intraday.bars` with x = minutes since ET midnight over the fixed
  4:00 AM – 8:00 PM window (a pre-market capture still spans the whole window, so the day fills in as it is recaptured); 5D =
  `prices.sessions_5d` laid out session after session (each 960 virtual minutes, a 90-minute gap and a dashed separator between
  sessions, one line segment per session, a weekday-date tick per session — "Wed Oct 14", "Wed 14" under 520 px of plot);
  1M / 3M / 6M / YTD / 1Y = `daily_1y` cut at the last close minus N months (day clamped to 28) or at January 1 of the last close's
  year; 5Y / Max = `weekly` (5Y cut at the last close minus five years). A range whose series has fewer than two points is
  disabled with `title="not captured yet"`. Without a daily series (the attachment trims `daily_1y`) the daily ranges fall back to
  the weekly closes and the default becomes 5Y; otherwise 1Y; without either, the first range that has data (an intraday-only record
  opens on 1D). The v6.0 names 3Y / 10Y map to 5Y / Max.
- **Period return** = last ÷ base − 1 in percent, printed with two decimals under 10 %, one under 100 %, none above; the base is the
  previous close on 1D (`intraday.prev_close` — the reconciled daily close, never Nasdaq's `previousClose`), the close before the
  oldest session on 5D (`sessions_5d[0].prev_close`), else the first close in range. The line and area colour follow its sign; the
  footer line reads `1D: −1.73% (4:00 AM ET → 8:56 AM ET) · vs prev close $262.19`. No ratio on a zero or negative base (null → "—").
- **Intraday specifics.** Pre-market (key < 09:30) and after-hours (key > 16:00) are shaded `rect.ext` behind the line; 1D draws the
  previous close as a dashed `line.pcl` with its value; x labels are times (6 am … 6 pm, minor ticks only when the plot is ≥ 520 px);
  the y-axis is tight to the session(s) (plus the previous close) and the valuation overlays (weighted IV@15, scenario band, 20 % / 25 %
  hurdles) are NOT drawn on 1D / 5D — the toggles dim and `.pcnote` says "Value lines hidden on intraday ranges". Every other range keeps
  them, with the right-edge tags and the "▲ IV@15% above chart" note when the value is off-scale. Bars are drawn at x = their key
  whether the entry is end-keyed (`bar_key: "end"`) or a legacy start-keyed day — the ≤ 5-minute offset on legacy days is accepted,
  never re-keyed.
- **The filed close ends the regular segment** (`sessionBars`): when a session carries a numeric `close` and its bars reach 16:00, the
  bar keyed 960 is replaced by (or, absent, a point at 960 is inserted with) that close — the 960 bucket is 15:56–16:00 end-keyed or
  16:00–16:04 start-keyed with after-hours prints, so the filed daily close is the right value at that x. A session whose bars stop
  before 16:00 is left alone (a point at 16:00 would draw a line across hours that were not captured). Bars are sorted by key and a
  duplicate key keeps the later entry.
- **Partial captures are labelled, never hidden.** `complete` is the block's own boolean, else derived from the last bar (≥ 19:55 ET,
  prices.py's rule) for legacy entries. A 1D of an incomplete session appends "· partial session (captured to 8:56 AM ET)" to the
  footer line and the source note says "captured to 08:56 ET (partial — the next prices.py run after 8 PM ET completes it)"; on 5D the
  footer counts "1 of 2 sessions partial" and the crosshair label of every point in a partial session ends "(partial capture)".
  `drawPrice` returns `partial` (count) with the text, so the card can style it later without re-deriving.
- **Crosshair** (DOM only, delegated from `document` — nothing is attached per chart, so re-renders leak no listeners): `pointermove` /
  `pointerdown` over `.pchart` map the client x to the SVG frame and snap to the nearest drawn point (`nearestIndex`, binary search,
  ties to the earlier point); the hidden `<g class="xh">` moves its dashed vertical and horizontal guides, the dot, the right-edge price
  tag and the floating label (date, plus the time on 1D / 5D, and the price; kept inside the plot). `pointerout` hides it for a mouse;
  a touch crosshair stays until the next tap elsewhere; `pointercancel` hides. `.pchart{touch-action:none}` is what lets a finger scrub
  without scrolling the page (it was missing before this round); `cursor:crosshair`, no text selection. Browsers without PointerEvent get
  touch / mouse fallbacks. The chart is `tabindex="0"`: ← → Home End move the crosshair, Esc hides it. The geometry a redraw leaves on
  the element (`el._pcGeom`) is the only state; redraws (resize, tab change, toggle) rebuild it.
- **Accessibility / motion**: focus-visible rings on the range buttons and the chart come from the global rule; the period pill and the
  crosshair text are tabular numerals; `prefers-reduced-motion` is honoured by the global rule (the chart animates nothing anyway).
- **Tests** (`tests/app.test.js`, chart block): every range from a fixture spec (288 weekly closes, 255 trading days, a complete legacy
  start-keyed session + today's end-keyed pre-market capture), the missing-intraday and weekly-only (attachment) cases, the default-range
  ladder, YTD at the January boundary (December out, Jan 2 in, a lone January close not yet a chart), `nearestIndex` (edges, ties,
  2,000-point binary search), `periodReturn`, `fmtRange`, `minuteToX` (4:00 AM at the left edge, 8:00 PM at the right, 9:30 / 12:00 /
  16:00 in proportion), `sessionBars` / `sessionComplete`, the 1D / 5D / YTD drawings (shading count, prev-close line, hidden overlays,
  time labels, tight axis, crosshair parts and ascending geometry), the card markup (nine buttons, disabled titles, default range, notes),
  and a sweep drawing every available range of every served record. The CSS test asserts `touch-action:none` and the pill rules.
- **Open for other owners.** (1) The served `intraday` blocks today are 08:5x ET pre-market captures with `complete: false` and the
  `sessions_5d` buffer holds one or two days per name — the 1D / 5D charts are correct but thin until the post-20:00 ET prices.py run the
  prices.py section asks for is scheduled (automation owner). (2) The attachment drops `sessions_5d`, so 5D is "not captured yet" there by
  design. (3) `meta.site_url` is still not emitted (build_site.py), so the attachment's links stay plain text.

## Decisions (statements.py review round, 2026-10-15 — filing generations, units, splits, bank / Kroger / IFRS lines)
Fixes from the adversarial review of `<T>/statements.json`. Additive to the statements section above; where a sentence there now
reads differently, THIS section wins. Tests: `python _system/tests/test_statements.py` (18, no network); verified offline on the
cached companyfacts of APP, HBAN, KR, GFI, ACGL, HSY, IRM, JD, KMB, AEE, ZS and then with a full `--all` regeneration.
- **The fact readers are local to statements.py** (`duration_history`, `instant_history`, `annual_values`, `instant_values`,
  `quarterly_series_gen`): the rules below need the WHOLE filing history of a fact (every filing that reported it, its unit and
  accession), which fundamentals.py's readers collapse to "latest wins". The tag lists come from `fundamentals.DUR` / `INST`
  (`SalesRevenueNet` ranks ahead of `Revenues` again — HSY's rounded $1.4B/$1.5B/$1.8B note facts on `Revenues` no longer beat
  its net sales); the period bookkeeping, `core_fy_starts` and the split machinery are still imported.
- **A derived quarter's two legs come from ONE filing generation** (`pair_generations`): the shorter leg (9M for Q4, the prior YTD
  otherwise) is its latest filing (date F); the longer leg is the first filing on or after F — the original 10-K after the original
  Q3 10-Q, the next year's 10-K after the next year's Q3 comparative — else the last one before F. If the longer leg was restated
  AFTER the shorter leg's last filing (its value moved by >0.5% against the filing before F while the shorter leg was re-filed
  unchanged) the pair before F is used. APP Q4 FY2023: operating income 648,207K (FY2024 10-K's comparative) − 378,693K (9M in the
  Q3 2024 10-Q) = 269,514K, pretax 178,896K, tax 6,663K — not the FY2025 10-K's restated 772,411K minus an un-restated leg. The
  annual column keeps "latest filing wins" (restated), so such a year now shows as a basis break (next item) instead of a wrong Q4.
- **`basis_break_quarterly`** (list of bool, present on a line only when some cell is true): for every money flow line, a fiscal
  year whose four quarters are all present and sum to more than 1% away from the fiscal-year figure has those four quarters flagged
  and the `growth_quarterly` cells that read from or into a flagged quarter blanked; one `warnings` entry per file lists every line
  and year (`basis break (...): revenue: 2024-12-31 (3,603,803,000 vs 3,224,058,000); ...`). APP FY2023/FY2024 (apps divestiture),
  AEE FY2011, CBRE FY2016, FTI FY2019, EQT FY2024 and the like are visible now. **App:** grey a flagged quarter (the file no longer
  pretends the year and its quarters agree). EPS / weighted shares / instants are never checked (they do not sum).
- **One money unit per file** (`money_unit`): the unit most of the core FY facts (revenue, net income, OCF, assets) are filed in,
  USD on ties; every money line reads that unit only (per-share lines `<unit>/shares`), so a quarter is never derived from legs in
  two currencies and a line never mixes a convenience translation with the filed currency. `currency` reports it; JD is CNY
  (its USD facts are the latest year's convenience translation and are ignored, warning), and its two bogus "Q4 FY2018/FY2019"
  columns are gone. A filer with no 10-Q at all (20-F / 40-F with 6-K interims) keeps only fiscal years whose four quarters all
  exist (warning names the dropped count).
- **Revenue basis is decided PER PERIOD**, not on the latest fiscal year: the filer's own `Revenues` / `RevenuesNetOfInterestExpense`
  replaces the contract-revenue value for every fiscal year and quarter where it exceeds it by >5% (IRM FY2018 4,225,761K and
  FY2019 4,262,584K instead of the 1,603M / 1,581M service component; the warning lists the periods). Before that, a plausibility
  guard: a fiscal year whose chosen value is >5% away from the sum of its four quarters, or BELOW its own nine months (a negative
  derived Q4 — impossible for revenue), takes another candidate tag's value when that agrees (within 2% of the quarters, or at
  least the nine months and a Q4 no bigger than twice the largest filed quarter), with a warning naming both tags and values.
- **Bank provision** = the income-statement total tags only (`ProvisionForCreditLosses` first); the loans-only allowance component
  `FinancingReceivableExcludingAccruedInterestCreditLossExpenseReversal` is never shown alone. When no total is tagged (HBAN, CFG,
  MTB, NTRS tag it with a custom element) the line is the loans component + `OffBalanceSheetCreditLossLiabilityCreditLossExpenseReversal`
  for periods where BOTH are filed (tag recorded as `A+B`, quarterly legs each derived per tag then summed, flagged derived when
  either is), blank otherwise; a warning says it can differ from the face line by other components (HBAN Q1 2026 158M = face;
  FY2025 466M vs face 463M; FY2024 418M vs 420M). General mechanism: a line spec may carry `combo=[(sign, tag), ...]` — plain
  arithmetic on legs filed in the same period, used only where the primary tags leave the period empty.
- **Other non-operating income (expense)** prefers `OtherNonoperatingIncomeExpense` (the face line: APP FY2025 8,012K, Q2 FY2026
  62,405K). `NonoperatingIncomeExpense` is the whole non-operating section for many filers (interest inside it) and the face
  "other" line for others, so per period where it supplied the value and an interest line exists it is reconciled against pretax
  income: operating income + it = pretax → it is the total and the line becomes it + interest expense − interest income (tag
  `NonoperatingIncomeExpense+InterestExpense-InterestIncome`); operating income − interest expense + interest income + it = pretax →
  it is the face line, kept; neither within 1% → blank. Periods with no interest line keep it as is.
- **Interest lines.** Non-banks: `InterestIncomeExpenseNonoperatingNet` / `InterestIncomeExpenseNet` (income − expense as filed)
  join the interest-expense tags NEGATED, and the label becomes "Interest expense, net" when they supply any value (KR FY2026 639M,
  Q2 FY2027 156M; the line used to be blank while the 199M interest income read as net income). IFRS: `FinanceCosts` (the face
  "finance expense") ranks before ifrs `InterestExpense` (the gross note figure) — GFI FY2024 50.4M, not 130.4M; interest income
  adds ifrs `FinanceIncome` and `InvestmentIncome` ahead of `InterestIncomeOnCashAndCashEquivalents` — GFI 28.7M, not 17.4M.
  Dividends paid stays the parent-holders' line (GFI 350.9M; the 379.2M face line includes dividends to minority holders —
  the same convention the dividends block uses).
- **Balance sheet.** `long_term_debt` falls back per period to `LongTermDebt`, `LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities`,
  `ConvertibleNotesPayableNoncurrent`, `ConvertibleLongTermNotesPayable`, `ConvertibleDebtNoncurrent`, `SeniorLongTermNotes`,
  `SeniorNotes`, `ConvertibleNotesPayable` (HBAN 17,221M at 2025-12-31, ZS's 1,696M convertibles); when the period's tag is one of
  the combined totals (`DEBT_TOTAL_TAGS`) the total-debt metric treats it as the filer's combined figure (adds short-term
  borrowings unless the short-term tag was `DebtCurrent`, never the current maturities again). Bank securities are two lines,
  `securities_afs` ("Securities available for sale": HBAN 26,132M) and `securities_htm` ("Securities held to maturity": 15,258M);
  `investment_securities` remains only for a filer that tags a total. `inventory` adds `InventoryGross` and the LIFO combo
  `FIFOInventoryAmount − InventoryLIFOReserve` (KR FY2026 9,445M − 2,553M = 6,892M). `short_term_investments` adds
  `DebtSecuritiesAvailableForSaleExcludingAccruedInterestCurrent`.
- **Operating-cost totals.** `total_costs` ("Total costs & expenses": `CostsAndExpenses`, `OperatingCostsAndExpenses`) is emitted only
  when the filer has no `OperatingExpenses` total at all (never mixed into it). When the operating lines shown explain less than
  90% of the latest fiscal year's revenue − operating income, a warning says the filer's other operating lines are custom-tagged
  (Kroger's OG&A 28,308M and Rent 872M cannot be reached from companyfacts).
- **Capex / SBC / intangibles purchases read as ZERO for a period whose cash-flow statement has no such line** — decided per
  filing, not per history: the filing(s) that supplied the period's OCF (the accession of the FY fact; both legs of a derived
  quarter) carry no fact of the line in any period. The line itself stays blank; the derived lines (fcf, owner_earnings, their
  margins and per-share figures, the TTM) read the zero (`_zero_annual` / `_zero_quarterly`, warning names the periods). APP FY2025
  FCF = OCF 3,971,094K, TTM 4,527,589K, owner's earnings TTM 4,245,213K. A derived quarter whose longer leg's filing carries the
  line while the shorter leg's does not is the longer leg minus zero, written into the line and flagged derived (warning). A line
  the filer has never filed anywhere is untouched (the earlier never-filed = zero rule covers it). The FCF definition is unchanged
  (ocf − capex; purchases of intangibles are NOT subtracted — open question below).
- **Per-share and share-count lines are split-adjusted** (`split_schedule`: fundamentals' `split_events` → `split_direction` →
  `share_refilings` → `split_filing_cutoffs`; `split_factor` per cell on the cell's own filing date): EPS and DPS ÷ ratio, weighted
  and period-end share counts × ratio for every cell last filed before the split's first post-split filing. The derived Q4 count
  and Q4 EPS are computed on the adjusted inputs. ACGL (3-for-1, basis change 2018-08-08): FY2016 EPS 1.78 = Q1–Q4 0.40 + 0.55 +
  0.66 + 0.17; the 2017 quarters' diluted counts are all ~417M. One warning per file names the split and the cells touched.
- **Fiscal Q4 weighted shares are day-weighted**: Q4 = (D_FY × FY − Σ dᵢ × Qᵢ) / d₄ with d₁ = days from the fiscal-year start to the
  first quarter end and dᵢ the quarter lengths, rounded to the nearest thousand shares above 1M (consistency gate unchanged). KR
  FY2026 (111/84/84/84-day quarters): 633,107,000 and Q4 EPS 1.36 (4 × FY − ΣQ gave 636,000,000 and 1.35).
- **`covered_through`** (top level: the newest period end in the columns) and the **`--all` skip rule**: a name is skipped only when the
  existing file records the same newest filing (form + date), the same `schema_version` AND `latest_filed.period <= covered_through`.
  A file written while companyfacts lagged the filing (the "not yet in EDGAR companyfacts" warning) is therefore retried on every
  run until the data arrives (HBAN's Q2 2026 10-Q, GFI's FY2025 20-F, BIIB, CTSH, ED, GEHC, VMC on 2026-10-15). A file without
  `covered_through` (pre-rule) is rebuilt once. `can_skip()` is the rule; the summary line reads "newest filing already recorded
  and covered".
- **Open questions for the owner.** (1) Whether FCF should subtract purchases of intangibles / capitalised software for filers
  with no PP&E line (APP: 28,318K in FY2025; the engine's capex override does); the file keeps the contract's ocf − capex and shows
  the intangibles line beside it. (2) HBAN's provision total differs from the face by 2–3M in FY2024/FY2025 (a securities
  component the filer does not tag); the alternative is a blank line. (3) The app should render `basis_break_quarterly` (grey or
  a marker) and may label "Interest expense, net" lines from the file's label.

## Decisions (static app — price chart review round, 2026-10-15: label fitting, return conventions, after-hours, pan-y)
Fixes to the price-chart owner's files (`app.js`, `app.css`, `tests/app.test.js` chart block) from the adversarial review. Where a sentence in the
2026-10-15 price-chart section above now reads differently, THIS section wins. Verified with `node _daily/site/tests/app.test.js` (53 tests) and in
the built-in browser at 375 × 812 on #APP (every crosshair label's `getBBox()` inside the 44…255 px plot of the 313 px SVG on 1D / 5D / 1M / YTD / 1Y / 5Y).
- **Period-return base on the daily / weekly ranges = the close AT OR BEFORE the reference date, prices.py's own rule** (`_close_at_or_before`),
  and the reference dates are prices.py's: 30 · 91 · 182 · 365 · 1,826 days before the last close for 1M · 3M · 6M · 1Y · 5Y, Dec 31 of the prior
  year for YTD (`RANGE_DAYS`). That base row is DRAWN as the window's first point, so the line starts where the return is measured from
  (stockanalysis draws the same way) and `base === pts[0].v` still holds; it carries no x tick (no "Dec" on YTD). Only when nothing sits at or
  before the reference date (MAX, a series trimmed to the window — the attachment's 1Y) is the first close the base (`priorBase: false`). Result:
  the pill now equals `prices.stats.ret_1m/3m/6m/ytd/1y_pct` to the cent on every served record (APP YTD −61.09, KR 0.98, HBAN −12.97, ZS, AEE —
  a test sweeps every served record); the old first-close rule had dropped the first day of each window (APP YTD read −57.60 against the hero's
  −61.09). 5Y still differs from `stats.ret_5y_pct` by the gap between the WEEKLY close at or before the date and prices.py's daily close (the
  record carries no daily series beyond one year) — documented, not hidden. `selectRange` returns `baseDate` and `priorBase`.
- **A finished session's 1D / 5D return ends on the OFFICIAL close, not the 19:5x after-hours print** (`sessionEnd`): when the session carries a
  numeric `close` and its bars reach the 16:00 key (the point `sessionBars` placed there), `last` = that close, the footer reads
  `1D: −3.71% (4:00 AM ET → 4:00 PM ET close) · vs prev close $272.28 · after-hours $257.14 at 7:55 PM ET (−1.93% vs close)`, the pill and the
  line colour follow the same −3.71 %, and `drawPrice` returns `after` ({t, v, label, pct}) and `last`. The chart's 1D figure therefore equals
  `stats.change_1d_pct` for every served finished session (asserted over the records' `sessions_5d`). A live session (no `close` yet, or bars short
  of 16:00) keeps the last print as before, with no after-hours clause. 5D applies the rule to its LAST session only; the base is unchanged (the
  close before the oldest session).
- **The crosshair label is fitted, never clipped** (`crosshairLines`, pure): the full text (`label · $price`) when its estimated width
  (`XL_CH` = 7.1 px per character of IBM Plex Mono 11.5 px, + 14 px padding) fits the plot, else the point's short tokens `sl` packed greedily
  into lines joined by " · " — 1D `['9:50 AM', 'Thu 15']`, 5D `['Thu 15', '9:50 AM (partial)']`, daily `['Wed Oct 14, 2026']` — with the price as
  the last token; a token wider than the plot stays whole and clamped. Lines are `<tspan>`s 13 px apart, the box grows to `6 + 13 × lines`, and the
  box x is clamped so the TEXT (not only the rect) stays inside `[L, W − R]`. In the browser the rendered width (`getComputedTextLength`) then
  replaces the estimate: the box tightens to it, or when the font runs wider than estimated the tokens are re-packed once with the measured ratio.
  On a 375 px phone (313 px SVG, 211 px plot) every 1D / 1M / YTD / 1Y / 5Y label is one line and a partial 5D point is two
  ("Thu 15 · 9:50 AM (partial)" / "$271.89"); the test asserts the estimate for every point of every available range of every served record at W = 313.
- **`.pchart{touch-action:pan-y}`** replaces `none`: a horizontal drag still delivers `pointermove` and scrubs; a vertical flick is a native page
  scroll (the browser takes the pan and fires `pointercancel`, which `wireEvents` already maps to `crosshairHide`). `none` had made the first,
  full-width, 240 px card of every company page a scroll trap on phones. The CSS test asserts `pan-y` and that `touch-action:none` is absent.
- **Deliberately not changed.** (1) 5Y keeps the weekly base (see above) rather than reading `stats.ret_5y_pct` for the pill: the pill always
  describes the drawn line. (2) The 1D pill of a LIVE session still moves with the last print (pre-market included) while the hero shows the
  previous session's `change_1d_pct` — those are two different sessions, and the footer names the capture time. (3) The 1D crosshair's short form
  drops the year and " ET" (the x-axis and the footer carry both); the full form is unchanged on wide plots and in the point `<title>`.

## Decisions (static app audit round, 2026-10-15 — layout check, About / Street / Filings completion, floor markers, hash canon)
Audit of `app.js` / `app.css` / `tests/app.test.js` against the owner's layout decision and the review findings. What ALREADY
existed and was kept as is: the compact hero + `.tabbar` sticky bar with the condensed `.tabsum` line, the tab bar directly
under the header, the price-vs-value card as the Overview's first card and the Overview order (chart → verdict → pass 2 →
About → Financial performance → Street summary → Filings → Key numbers → Overrides → Scenarios → Moat → Flags), the About /
Financial performance (`financialPerformance`) / Street summary / Filings cards, the Forecast DCF · Street · Analysts sub-tabs,
the "★ Watchlist N" toggle with per-device stars, the statements viewer and the price chart. Added or changed here; none
changes a data shape:
- **About.** `aboutFacts(record)` (pure, exported) builds the grid in the stockanalysis order — Industry (SIC), Sector,
  Headquarters (the full filed address in the title), Employees (count and date inline, the 10-K sentence ONLY in the
  `title` attribute, with the filing linked), Exchange, **Ticker** (new), Fiscal year end, Filer category, Incorporated, First SEC
  filing (labelled with `about.first_sec_filing_form` — "S-1" — when profile.py recorded one, else "IPO-date proxy"), Website,
  EDGAR. A fact with a title gets a small ⓘ. The description past ~600 characters (`ABOUT_CLAMP`, `clampText`: cut at a sentence
  end inside the second half of the window, else at a word; a tail under 80 characters is not hidden) ends in a **"Read more"**
  button that reveals the rest in place ("Show less" closes it — the text is already in the markup, no re-render). The source
  line reads `about.description.source` ("10-K Item 1 Business" / the 20-F variants), the filed date and the accession linked
  to the filing. Absent profile → "**Profile not pulled yet** — profile.py has not run …" above the fundamentals facts.
- **Street summary.** `streetCardModel(record)` (pure, exported): counts, mean / low / high targets and their % vs the price the
  page uses (the last close on a live page, else the scored price; null without a price), the monthly history oldest first
  (`{date, buy, hold, sell, total, mean_target}`), our hurdle prices. The card = the label "Street view — Nasdaq analyst data, not
  used by the valuation" → the paragraph → the mean target large with a `.badge` (+86.6% vs last close $262.19) and the low–high
  range → the buy / hold / sell bar → a small `drawChart` stacked chart of the last six months (`street-sum`, 120 px; only with two
  or more months) → our 15% / 20% / **25%** hurdle prices → "See the full forecast →" (`#T.forecast.street`) and the source note.
- **Filings.** A chips row All · 10-K / 10-Q · 8-K · Other with counts (`FILING_KINDS`, `filingKind(form)`: 10-K / 10-Q / 10-KT /
  10-QT / 20-F / 40-F / 10-K405 / 10-KSB / 10-QSB and their `/A` → periodic; 8-K, 8-K/A and 6-K → 8-K; everything else → other;
  `filterFilings(list, kind)`). Rows carry `data-kind`; a chip hides the other kinds' rows in the DOM (no re-render) and a chip
  with nothing behind it is disabled. The fundamentals `latest_filings` fallback rows carry kinds too.
- **Floor markers (review finding a).** The Overview Scenarios card reads `sensitivity()`'s `irr_at_floor` / `irr_live_at_floor`:
  a floored shown figure gets the `atfloor` colour and the "at floor" superscript with the explanation in its title (live wording
  when the page is live), the "Scored IRR" sub-figure carries its own marker when the scored solve was floored, the weighted foot
  marks a floored headline, and the section note explains "at floor" once any is marked. The ranking row badges **"live IRR at
  floor"** (`row.irr_at_floor_live`) and **"scored IRR at floor"** (`row.irr_at_floor`; "IRR at floor" on a row without a live
  figure) separately, each with a title, and marks the matching IRR cell. The Forecast sensitivity table was already marked.
- **Hash canon (review finding b).** `canonicalHash(hash, findTicker)` (pure, exported) = `hashFor(index ticker, tab, sub)` for any
  accepted spelling; `route()` rewrites the address bar to it on load with `replaceState` (`#app/Financials` → `#APP.financials`,
  `#APP.forecast.STREET` → `#APP.forecast.street`, `#APP.overview` → `#APP`), so a shared legacy link lands on the canonical URL
  without a history entry or a second `hashchange`.
- **Sticky bars.** `.tabbar` and (at ≥ 761 px) the ranking `.controls` row use `top: env(safe-area-inset-top, 0px)`; the filter
  row stays at the top of the ranking while the long table scrolls on desktop only — on a phone it wraps to three lines and would
  cover the cards, so it scrolls with the page there.
- **Statements viewer.** `basis_break_quarterly` is rendered: a flagged quarter cell is greyed (`td.bbrk`, dotted underline, the
  explanation in its title) and a legend line says the fiscal year's quarters do not add up to its restated figure (APP FY2023 /
  FY2024, the apps divestiture); `stmTable` carries `basisBreak` per cell and `anyBasisBreak`. The units note now says how far the
  table reaches — "**26 quarters, Q1 FY2020 → Q2 FY2026** — scroll the table sideways for the older periods" (`stmSpan`; the
  TTM / Current column is not counted) — because a phone shows two or three of the columns.
- **Summary tables (Financials tab, fundamentals.json).** A line with no value in any shown period is dropped from the quarterly
  and the annual summary tables (the statements viewer's existing rule; a row of dashes carries nothing — APP's quarterly "Gross
  margin", a bank's "Cost of revenue"). Lines with any value are unchanged.
- **What the chat attachment cannot show.** `_daily/latest.html` inlines this app with the top-150 records but, by the data-layer
  contract, no `statements.json` (57–266 KB per name), so its Financials tab shows the summary tables and "The full statements are
  on the site". That is the "missing" Financials page when the attachment is what is open; the served site has the viewer. Still
  open for build_site.py: emit `meta.site_url` so the attachment can link straight to `<site>#<T>.financials`.
- **Tests** (`node _daily/site/tests/app.test.js`, 61): the About grid (order, Ticker, title evidence, first-filing form, fallbacks),
  `clampText` and the Read more markup, the Street card model (percent vs the last close and vs the scored price, history order,
  no-price / no-target / one-month cases) and its small chart, the filings kinds / filter / chips / disabled chips / fallback rows,
  `canonicalHash` (legacy slashes, casing, sub-tabs, bad and unknown), the Scenarios-card and ranking-row floor markers (ZS live,
  synthetic scored / live / weighted), the basis-break cells and legend and `stmSpan` (fixture + APP's served file), the dropped
  empty summary lines, negative-growth prose, and the new CSS rules.

## Decisions (static app review round 3, 2026-10-15 — the active tab is always inside the scrolling strip)
Fix from the adversarial review of `app.js` (`mountCompany` / `showTab` toggled `.tab.on` but never scrolled `.tabs{overflow-x:auto}`,
so a phone deep link to `#T.forecast…`, `#T.analysis` or `#T.data` opened the right pane with nothing highlighted in the visible strip).
No data shape changes.
- **`tabScrollLeft(strip, tab)`** (pure, exported with `TAB_PAD = 16`): given `{scrollLeft, clientWidth[, scrollWidth]}` and the tab's
  `{left, width}` in the strip's content coordinates, the `scrollLeft` that brings the tab fully into view with 16 px of its neighbour
  showing — scrolling back when the tab is left of the window, forward when right of it, clamped to `[0, scrollWidth − clientWidth]` —
  or `null` when it is already visible, the strip is hidden (`clientWidth` 0) or the input is malformed. **`revealTab(page)`** (DOM) reads
  the rects of `.tabs` and `.tab.on`, converts to content coordinates (`tabRect.left − stripRect.left + scrollLeft`) and ASSIGNS
  `strip.scrollLeft` — never `scrollIntoView`, which can also scroll the page or an ancestor, and never animated, so the reduced-motion
  rule needs no opt-out and the viewer's vertical position is untouched. Called after the mount in `mountCompany` and in `showTab`
  right after the `.on` classes are toggled (so a hashchange to another tab on the same page, a tap on a half-visible tab and a deep
  link all reveal). On desktop the strip is wider than its tabs and the helper is a no-op.
- **Verified** with `node _daily/site/tests/app.test.js` (62) and in the built-in browser at 375 × 812 (`/site/#HBAN.forecast.street`:
  Forecast at 259.6–342.8 px inside the 16–359 px strip, `scrollLeft` 123 = the unit test's figure, Street sub-pane on; `#HBAN.data`,
  `#HBAN.analysis` by hashchange, `#APP.data` / `#KR.financials` as deep links, a tab tap while scrolled 2,000 px down: active tab
  visible every time, `document.documentElement.scrollWidth` 375, `scrollY` unchanged by the reveal).

- **Review round 4 (static app, 2026-10-15 — Forecast audit, watchlist view, partial yields, sticky bar, chart / statements minors).**
  No data shape changes; the app reads two fields build_site.py already emits (`row.shareholder_yield_label` / `_bound`) and
  `meta.watchlist_outside`. Verified with `node _daily/site/tests/app.test.js` (72) and in the built-in browser (375 × 812 and desktop).
  - *OE/share history (Forecast → DCF).* A fiscal year is drawn only when BOTH its owner's earnings and its diluted share count are
    filed: `fundamentals.annual.oe_per_share`, or OE ÷ diluted shares when that cell is empty; every other year is null and the note
    under the chart names it and why ("Not shown: FY2025: capex not filed (the engine run fills capex with an estimate — not a filed
    value)"). The engine CSV is used only for a record without `fundamentals.annual`, and never for a CSV row whose `*_tag` is
    `OVERRIDE`. This reverses the earlier decision that filled APP's FY2025 from the CSV (that OE uses the capex estimate override) and
    removes ZS's -61/share FY2018 point (CSV diluted shares 119,764). The y-axis covers history and forecast together; `oeAxisFloor`
    sets a floor (drawChart `yFloor`, rounded down to a grid step) only when a filed loss reaches further below zero than the chart
    reaches above it, at minus that positive extent — the pinned point is drawn as a ▼ with its real value in the tooltip and a legend
    line. History alone is never floored. Tier F (AEE) and runs without stored paths now show "Owner's earnings per share — history"
    (the filed line alone) above the no-projection note. Street sub-tab: the quarterly "from" is the filed quarter whose period end is
    within 45 days of the consensus quarter's end month one year earlier (`yearAgoQuarter`; Nasdaq names quarters "Sep 2026" /
    `fiscal_end` "2026-09"; Kroger's 52/53-week quarters end a week off), the "Q3 2026" form still matching by quarter number.
  - *Watchlist toggle = a view.* On, it shows every watched name (repo list ∪ device stars) whatever the Modeled / misfit segment says
    (the segment is dimmed with a title); the tier filter and the search still apply. "★ Watchlist N" = the rows shown with the tier
    on All; `#count` adds "· M more watched outside the Tier X filter". "Copy tickers" copies exactly those N (`watchTickers` now
    returns ranked names only, `watchCopy`); repo names with no page are listed in a note — outside the universe
    (`meta.watchlist_outside` minus any ticker with an index row, so APP stays copied), in the universe but not ranked yet, and device
    stars with no row. Titles name `_system/watchlist.json`.
  - *Partial yields.* Dividends tiles (dividend, buyback, net buyback, shareholder yield) print `yields_display[k].label` with the note
    as the tile tooltip (ⓘ) and the bound named on the tile ("lower bound" / the label's own "(incomplete)" on a small second line);
    the leg amount comes from `legs[k].value` (HBAN's Q1-only $150M, not "no buyback filed"). The ranking row's Take line prints
    "Shareholder yield <label>" from `row.shareholder_yield_label`, nothing when the label is absent — never the bare figure.
  - *Sticky bar.* `.tabsum` is `position:absolute; bottom:100%` inside `.tabbar` (shown with `visibility`), and `.tabbar.condensed`
    sticks `--tabsum-h` (36px) lower: the bar's height never changes (45 px both ways in the browser; the pane's document top constant).
    `condenseNow(heroBottom, barMarginTop, 36)` switches where the stuck and natural positions meet, so the tabs do not jump either.
  - *Overview.* `section('')` emits no `<h2>`. The Street summary prints the mean-target move once (the badge, one decimal); the
    Street sub-tab paragraph prints it at one decimal like its table. When Nasdaq's analyst count and its buy / hold / sell total
    differ (APP 16 vs 20) the paragraph names both and says they come from separate tables; the bar is labelled "Rating breakdown · N".
  - *Price chart.* 5D sorts `sessions_5d` by `session_date` before laying them out; a live 1D card prints one "captured to" time —
    `intraday.last_time` (`capturedTo`) — in the footer and the source note.
  - *Statements viewer.* The chart card renders only while its line has values in the selected periodicity (a period switch clears the
    open line otherwise); closing a chart whose row is gone focuses the active period button. Annual-only filers say "No TTM / Current
    column: this filer reports annual periods only". An `error` status is retried when the tab is reopened, and the error note carries a
    Retry button. Duplicate quarter labels (ADM, HSY, KVUE, ON, TDY, TTWO, YUM) get " · Mon 'YY" in the sparkline; drawChart thins x
    labels by their length. `basis_break_quarterly` cells were already greyed with a title (unchanged).
  - *Hero chip.* With a repo list in hand (meta ∪ index, as mountCompany passes) the "★ Watchlist repo" chip comes from it alone;
    `record.row.watchlist` is consulted only when no list is given.

## Decisions (fundamentals.py dividends block 5.4.5, 2026-10-15 — re-verification fixes)
Additive to `fundamentals.dividends`; nothing feeds the valuation; every figure stays a filed value or plain arithmetic on filed values. Tests:
`_system/tests/test_fundamentals_dividends.py` (52, no network; the 5.4.5 fixtures are shaped like CCI, NVDA, HSY / STAG, EXPE and the reviewers'
S-A scenario). Re-run on CCI, HSY, EXPE, HBAN, KR, APP, ZS (written) and NVDA, MAIN (`--no-write`).
- **A flow leg filed below zero is a sign error, read as its absolute amount** (`sign_fixed_flows`). Dividends paid, repurchases and issuance
  proceeds are non-negative by definition. CCI's 10-Ks tag `PaymentsOfDividendsCommonStock` negative (FY2025 −2,080,000,000, filed 2026-02-23)
  while every 10-Q year-to-date fact is positive (nine months 1,615,000,000), so the quarterly table's Q4 = FY − 9M read −3,695,000,000. A quarter
  whose row is below zero, or whose row was built from a fact filed below zero, is rebuilt from the absolute filed facts (|−2,080M| − 1,615M =
  465M); when no consistent figure can be rebuilt the quarter is left out (a missing quarter, never a guess). Annual values are read as absolute
  amounts (payout ratios, the 20-F fallback legs). New optional keys: `legs[k].sign_corrected` (list of strings) and
  `yield_basis[name].sign_corrected` ({leg: string}); `yields_display[name].note` adds "filed below zero, read as the absolute amount"; a `notes`
  line per leg lists every corrected value. `payout_ratio` is null for a negative numerator. CCI: dividends_paid_ttm 1,859M (was −2,301M),
  shareholder yield ≤ 8.52 % (was ≤ −3.13 %), payout_ratio_oe 0.74 (was −0.74). The quarterly table itself (`build_quarterly`) is unchanged.
- **Primary DPS basis by coverage, not by the newest fact** (`choose_dps_basis`). The coverage of the last 8 quarter slots ending at the newest
  fact of either tag (a quarterly fact within 20 days of a slot, or an FY fact whose fiscal year contains it); `paid` is primary only when it
  covers at least 2 more slots than `declared`, otherwise `declared`. One extra paid Q4 fact can no longer flip a whole history (reviewer S-A);
  AVGO still reads paid (declared 0/8, paid 8/8). `dps_basis_detail` ends with the counts.
- **The no-interleave rule is for quarterly facts only.** A fiscal year with no primary FY fact and no four primary quarterly facts takes the other
  tag's FY fact (kind = that tag, `dps_basis` `mixed`, `dps_basis_detail` lists the years, a note warns about the switch year). NVDA: CashPaid
  FY2016-FY2021 fill the declared tag's hole; `dps_cagr_5y` 20.1 % (FY2021 0.016 → FY2026 0.04), `last_cut_fy` null (was 2016).
- **An FY DPS fact below the sum of its own tag's quarterly facts inside that fiscal year is not used** (a total cannot be smaller than its
  quarters; 10 % tolerance) and the note names the quarters. NVDA's FY2016 declared fact (0.115, one quarter's rate, ÷40 = 0.002875 against
  quarters summing 0.007) is dropped and the paid FY fact 0.395 (÷40 = 0.009875) fills the year. This supersedes the 5.4.4 "not changed, on
  purpose" line for NVDA FY2016: nothing is estimated, an impossible filed value is set aside and another filed value used.
- **Power-of-ten disagreements: consistency before the count** (`dps_fy_facts`). Each group is checked against that year's own three-month facts
  (summed, when ≥2) and the tag's other fiscal years (log median); when exactly one group is within 3x of every reference and every other is
  ≥10x from all of them, it wins whatever the count. CCI FY2014: 1.87 (10-K 2015-02-19) over 1870 (10-Ks 2016-02-22 and 2017-02-22) — the
  year's quarters 0.35 × 3 = 1.05 and the other years' median 4.75 agree. A note is now written for every power-of-ten disagreement (GFI gains
  FY2018 / FY2019 notes). `dps_outliers` also checks the first / last dividend year against its one neighbour at 100x (one-sided; HBAN's real
  FY2008 0.6625 → FY2009 0.04 cut is not flagged).
- **A cash payer whose per-share tags lapsed is not "suspended".** Payer status and, when the per-share facts cannot give it, `frequency` come
  from the filed dividends paid in the latest four consecutive quarters: 4/4 positive → quarterly; 2/4 two quarters apart → semiannual and 1/4 →
  annual only for an established payer (cash dividends in every fiscal year of the last three); otherwise null with a note.
  `frequency_basis` then starts "cash dividends paid are filed for 4 of the last four quarters (…)" and says the per-share facts do not give the
  cadence. HSY (CashPaid only 2008-2010; 271.1M / 271.3M / 288.0M / 286.4M paid in the last four quarters): quarterly, no "suspended" note.
  TKO now reads quarterly from cash. STAG-shaped filers (Q1-Q3 per-share facts, no Q4 / FY fact for years, cash every year) get "tagged for some
  quarters only, not a suspension" instead of "suspended / reinstated"; CCL's real suspension keeps its wording.
- **A split evidenced only by re-filed values restates the quarterly facts too.** When a period's FY DPS and the filer's diluted share count were
  both re-filed by the same factor (split_restatement's re-filed-counts evidence) and no ratio fact sits within 800 days, `dividends_inputs`
  applies it like a filed ratio at the first filing on the new basis. `split_adjustments[*]` gains `source`: `ratio_fact` or `re_filed_counts`
  (`effective` is then the first post-split filing date, not the corporate-action date). EXPE: 1-for-2 at 2012-02-10, the 2010 quarterly facts
  0.07 → 0.14 beside 2011's 0.14.
- **Wording.** `yields_display[name].note` phrases each partial / excluded leg by its effect on that yield ("the deduction is understated, so this
  yield is an upper bound"; "left out, so this yield is a lower bound"). A quarterly `frequency_basis` from per-share facts ends "the per-share
  facts are filed per quarter — a payment cadence inside the quarter (a monthly payer) is not tagged" (MAIN, STAG pay monthly).
- **Not changed.** ZS's `≥ −0.18 %` shareholder-yield label (correct bound semantics; the note now says the buyback leg was left out). Two genuine
  same-ratio splits within 180 days still fold into one event (`split_events`; no name in the universe hits it). The app / ranking-row adoption of
  `yields_display` belongs to `app.js` / `build_site.py`.

### profile.py reverify round (2026-10-15) — description is a prose run, headcount totals only
Fixes from the second review of `_system/profile.py` (`about.description`, `about.employees`, headquarters, first filing). One
additive field; every other shape unchanged.
- **`about.description`** is the first genuine prose run under the heading: everything between the heading and the first line that
  is itself prose (>= 8 words, a sentence end, mostly lower-case words, few digits / page ranges; a sentence the document broke
  across two lines is judged whole) is skipped — sub-headings, a sub-section index with its page numbers (Prudential, MetLife, The
  Hartford), and a leading forward-looking-statements / "should be read in conjunction" / "incorporated by reference" paragraph
  (Waste Connections, Cboe, Con Edison). If the next item label, two page ranges or 2,500 skipped characters come first, that
  occurrence is a cross-reference sheet (M&T Bank's subpart 1400 sheet, Gold Fields' 20-F guide) and the next heading is tried.
  The body must still read as prose (two sentences, mostly lower case, few digits). Page furniture is dropped anywhere in the
  text: page numbers, "Table of Contents", "PART I", repeats of the Item 1 heading, and lines that recur >= 5 times in the document
  with a page token (Constellation's "#WORTHREACHINGFOR I 7" footer). Headings now include "Items 1 and 2. Business and Properties"
  (Devon, Diamondback, Permian Resources; `description.source` = "10-K Items 1 and 2 Business and Properties") and "Part I. Item 1.
  Business" / "Part I - Item 1. Business" on one line (Expedia, The Hartford). The 1,500-char cut never ends on "Inc." / "U.S.".
- **`about.employees` is a company total or null.** Forms added: the dates-last multi-year sentence ("We had approximately 39,800,
  35,900 and 33,500 full time employees as of December 31, 2023, 2024 and 2025, respectively" — Baidu); multi-year sentences pair
  years and counts by position and take the LATEST year (Estée Lauder's descending "June 30, 2026 and 2025 ... 55,000 and 57,000"
  -> 55,000 as of 2026-06-30; lists of unequal length are rejected); "<Name> ... N employees as of / at <date>" (Northern Trust, The
  Hartford, EchoStar — the whole sentence is the evidence; only a heading glued BEFORE the match is trimmed); "the Company and its
  subsidiaries had / employed" (United Airlines, Yum! Brands); "we directly employ", "our total workforce consisted of", "we have a
  team of", "<Name> team consisted of ... team members", "employed N individuals" ("individuals" only with a form of "employ"), and
  "We ended the year 2025 with N" (Diamondback; as_of = the fiscal period end in that year, `basis` "year-end headcount ..."). A
  count followed directly by one function or place ("18,600 employees in research and development", "11,172 people in the United
  States") is a subset, and a sentence giving the registrant's count and another entity's ("PG&E Corporation had 10 employees, and
  the Utility had approximately 29,000") has no filed total: both are rejected — a lone location count is no longer accepted as a
  fallback (Vulcan's 10-K lists 11,172 in the U.S. and then 280 in Mexico, 32 in Honduras, 63 in Canada, 1 in the Bahamas). A
  total listed with its parts ("898 employees, comprised of ...", "24,214 ... including ... with 20,471 employees in the U.S. and
  3,743 in Canada", "in our consolidated operations", "in the following locations:", "compared with 45,000 ... at December 31,
  2024") stays the total. Ranking adds the as-of date (latest first) after the form rank. A point-in-time FTE count reads `basis`
  "full-time equivalent as of the stated date"; a year-only date without "average" reads "headcount stated for the year (no day
  given)".
- **New `about.employees_unresolved`** = `{count: null, reason, evidence, form, filed, url}` | null — present only when
  `about.employees` is null because the filing states only a part of the workforce; `evidence` is the filed sentence and the same
  text is in `warnings` ("employees: null - <reason> ..."). The app ignores it today (its employees row needs a count).
- **Headquarters (cover path)**: an all-caps cover city is put in readable case ("GOODLETTSVILLE" -> "Goodlettsville",
  "MCLEAN" -> "McLean"); a cover city tag the filer cut short ("St. John'" — Fortis) is replaced by the submissions city with
  `address.city_source` saying so; a foreign cover city that is a district or part of the submissions city ("Haidian District",
  "Daxing District", "Chuo-ku") also names the city proper in `address.metro` (`metro_source` "EDGAR submissions") and in the text:
  "Haidian District, Beijing, The People's Republic of China". A domestic cover (with a state) never borrows the submissions city.
- **First filing**: form spellings are compared without hyphens / spaces, so EDGAR's 1990s "10QSB", "10KSB", "10-KT", "10-QT" and
  "10-KSB405" count as periodic reports for the "periodic report precedes the registration" rule.
- **`write_atomic`** serialises before touching the disk and removes its `.tmp` on any failure (no `profile.json.tmp` left in a
  company folder).
- **Verified**: `python _system/tests/test_profile.py` (no network); live writes for BIDU, UAL, YUM, EL, PRU, HIG, STZ, PCG, APP,
  KR, HBAN, ZS; `--no-write` for DVN and PR (Permian Resources, sector Energy, "ITEMS 1 AND 2. BUSINESS AND PROPERTIES"); offline
  re-extraction over 102 cached annual documents (descriptions: none starts with a TOC, index, cross-reference or boilerplate; the
  only nulls are SYF — a cross-reference 10-K with no Item 1 prose — and FTS's 40-F wrapper).


### statements.py review round 3 (2026-10-15) — consensus values, one split per event, capex never zero, labels, dates
Additive to the two statements sections above; where a sentence there reads differently, THIS one wins. No key added or removed;
`schema_version` is now 2 so the `--all` skip rule rebuilds every file written under the old rules once; `basis_break_quarterly` may now be true on a BLANK cell; quarterly labels can carry
` (YYYY-MM-DD)` when a fiscal-calendar change gives two genuine quarters the same name. Tests: `python _system/tests/test_statements.py`
(29, no network).
- **A period's value is the CONSENSUS of its filings**, not the latest filing: the value most DISTINCT filings agree on (within 0.5%),
  ties to the value filed latest (a restatement wins once it is re-filed as often as the original). Applies to FY facts (annual
  reports), balance-sheet instants (every 10-K / 10-Q that reported the date votes; the annual column's tag is the first in priority
  an annual report used for that date) and direct quarters. HBAN cash FY2010 847,888K (10-K + 9 later filings; the 2015 10-K's shifted
  1,115,968K loses), FY2011 1,115,968K; HIG Q1 2013 EPS −0.58 (three filings; the 2015 10-K's −490,000 loses). Before voting, a
  filing whose value is a **power-of-ten slip** (10^k, k ≥ 3) of another filing's is dropped, keeping the value closest (log scale)
  to the tag's other periods: HAL FY2022–FY2024 continuing EPS 1.73 / 2.92 / 2.83 although later 10-Ks re-filed them ×1,000,000 (FY2022 and FY2023 twice); HAL Q2
  2020 −1.91. Warnings: `power-of-ten disagreement …` and `consensus over latest filing …` (every fiscal-year cell where the newest
  filing's different figure was overruled, with that filing). **Consequence:** a year restated only once (discontinued operations,
  a reclassification) shows the value as originally reported — HPQ FY2014 revenue 111,454M (HP Co. before the HPE separation), APP
  FY2023 3,283,087K (consolidated, matching its 2023 quarters), KMB FY2023 20,431M, JBL FY2017 OCF 1,256.6M — named in that warning.
  A last-resort cell check blanks an EPS / DPS above 1,000 and 100× the line's median, or a share count 100× off its median (ECHO's
  2023 quarters re-filed as 307,410 "shares").
- **One period, one date** (`canonical_dates`): context dates ≤ 3 days apart are one period, dated as the earliest filing dated it
  (HSY Q1 2012: the 10-Q's 2012-04-01 and the next 10-K's 2012-03-31 are one column, both voting). Warning `period dates merged …`.
- **Quarter labels** use the annual columns' rule (`period_labels`: `fy_labels` over the fiscal-year ends plus estimated ends of years
  with quarters only): TDY's 52/53-week years ending 2012-01-01 / 2012-12-30 are FY2011 / FY2012 and their quarters Q1–Q4 FY2011 /
  FY2012 (were FY2012 twice); KVUE likewise.
- **Stock splits: one event per split** (`split_events_dedup`). A ratio fact on a duration context is a restated comparative and does
  not date a split; instant contexts are the events; duration facts attach to the same-ratio event filed ≤ 3.5 years before (≤ 200 days
  after) them, else chain by filing date into one event. DXCM: one 4-for-1 (2022-06-10, first filed on the new basis 2022-07-28) —
  FY2017 diluted 345.2M = 86.3M × 4 and EPS −0.145 = −0.58 / 4 (were ×256 / ÷256). A tagged split with no share count re-filed on a
  new basis is applied only when the fiscal-year diluted counts move by its ratio (or nothing was filed before it): CFG's ratio 6
  tagged against FY2021 (counts flat) is not applied (its 2012–2018 EPS were ÷6), warning `split ratio not applied …`. ODFL's and
  WCN's 3-for-2 splits tagged twice are one event each.
- **Capex is never read as zero.** A period with operating cash flow and no filed capex has NO free cash flow and NO owner's earnings
  (warning `capex: no capital-expenditure figure is filed …`, naming unlisted capex-like tags in those filings). This replaces the
  earlier "read as 0 when the filing has no such line" rule for capex: APP FY2025 and its 2025–2026 quarters now show FCF blank
  (the cash-flow statement has no PP&E line; the engine's capex override is separate). Capex candidates add, after the PP&E tags,
  `PaymentsForCapitalImprovements`, `PaymentsToDevelopRealEstateAssets`, `PaymentsToAcquireAndDevelopRealEstate`,
  `PaymentsToAcquireRealEstate` and `PaymentsForProceedsFromProductiveAssets` (one tag per period, never a sum; EXR FY2018 capex =
  development 60,677K). SBC keeps the per-filing zero rule only when the filing carries no SBC-like caption at all.
- **No quarter from unpaired legs.** A quarter is derived only when every leg exists in the same tag; the former "longer leg minus 0"
  fill is gone. Such a blank cell is flagged `basis_break_quarterly` (APP Q4 FY2025 purchases of intangibles: 28,318K in the 10-K,
  folded into "other investing" in the 10-Qs). The catch-all lines (other non-cash / investing / financing) blank a derived quarter
  whose longer leg's filing carries a line of that section the shorter leg's filing lacks while the catch-all's year-to-date figure
  shrank (APP Q4 FY2025 other investing 373K − 27,863K), flagged too.
- **Same filed fact once**: two debt lines carrying the same value for the same date from the same filing are one figure — the later
  line's cell is blank (GFI FY2024 "Current portion of borrowings" 719.1M tagged `ShorttermBorrowings` and
  `CurrentBorrowingsAndCurrentPortionOfNoncurrentBorrowings`): total debt 1,776.5 + 719.1 = 2,495.6M, net cash −1,635.4M (20-F
  0001172724-25-000010 R5); IFRS `CurrentBorrowingsAndCurrentPortionOfNoncurrentBorrowings` is an aggregate like `DebtCurrent`.
- **Interest**: `InterestAndDebtExpense` ranks before `InterestExpenseDebt` (APP FY2025 207,016K = the 10-K face line). Per period,
  interest income is blank where the interest-expense figure is the filer's NET tag (KR FY2026 "Net interest expense" 639M); the
  "Interest expense, net" label follows the newest fiscal year's tag.
- **Revenue fallbacks** (`REVENUE_FALLBACK_TAGS`) fill only periods the standard tags leave empty, and only when the element agrees
  (1%) with the chosen revenue in at least as many overlapping years as it disagrees and never by >10%: ATO FY2009–FY2015
  (FY2015 4,142,136K), CMG FY2008–FY2015 (FY2015 4,501,223K), EXR FY2008–FY2015 (FY2015 782,270K), WEC FY2007–FY2010, CCL
  FY2010–FY2013 (FY2013 15,456M), ALNY FY2011–FY2015, GFI's US-GAAP years. EQT's `OilAndGasRevenue` disagrees with its revenue and
  stays unused (FY2007–FY2015 blank, warned). EPS falls back to `IncomeLossFromContinuingOperationsPer{Diluted,Basic}Share` for
  periods with no EPS tag and no discontinued operations (HAL FY2022–FY2025).
- **Payments filed negative** (capex, intangibles, buybacks, dividends, investment purchases, debt repaid; not net tags) are read as
  the absolute amount in every filing and leg, warning naming the filings (CCI FY2024 dividends 2,729M, 10-K R6 "(2,729)").
- **Derived lines** carry `derived_quarterly[i]` = any input line's flag (EBITDA, FCF, margins, per-share figures).
  **`periods.annual[].filed`** = the annual report whose report date is that fiscal-year end in the submissions feed, else the first
  annual-form filing within 400 days that reported any fact for that end, else the first annual report that carried it.

- **Static app, OE/share history (app review round 5, 2026-10-15)** — display rules only; no schema change.
  `oeHistory` keeps every fiscal year of the last ten (leading blank years are no longer trimmed), so the chart keeps
  fiscal-year labels even when nothing is plottable (TDY / HSY / TKO / ARES / EME / HAL / STZ) and the note says
  "No solid line" plus the reason, grouped over runs of years ("FY2016–FY2025: stock-based compensation not tagged …").
  An override is worded by `numbers.overrides_applied[].kind`: `estimate` = "not a filed value"; `filing` = "not tagged in
  companyfacts (the engine run uses $X read from the Form 10-K for fiscal year ended … for all N untagged years — a filing
  value, but not in fundamentals.json, so not plotted)". A filing override is still not plotted: the engine applies one
  year's figure to every gap year and fundamentals.json does not carry it. A year whose filed diluted count is more than 5×
  from the median of the last three filed counts is not plotted (WRB FY2017–22 counts in thousands; CMG FY2016–21
  pre-split; SMCI, RKT, CPNG, CMPS, AFRM share-class / IPO years); fiscal years missing from `fundamentals.annual` get a
  blank placeholder from the period ends (MTD FY2014–16, HIG FY2016); a YoY bar is drawn only between plotted years one
  fiscal year apart (period ends 330–400 days apart) whose diluted counts moved less than 3× (DXCM's 4:1 split year gets
  none, with a "No year-over-year bar" note). The app never restates for splits — that is fundamentals.py's job.
- **Shareholder-yield tile caption** names its own dividend leg: "dividends paid $930M (3.04%) + net buyback, ÷ market cap
  $30.61B" (legs.dividends_paid.value ÷ dividends.market_cap), with a tooltip sentence that the leg is cash paid, not TTM
  DPS × shares, so it need not equal the Dividend yield tile (HBAN 3.04% paid vs 4.11% DPS yield).

### fundamentals.py dividends block 5.4.6 (2026-10-15) — second re-verification: stable basis, FY facts kept, signs by kind
Additive to the 5.4.5 dividends section above; where a sentence there reads differently, THIS one wins (it supersedes the 5.4.5 lines
"primary DPS basis by coverage … One extra paid Q4 fact can no longer flip a whole history" and "an FY DPS fact below the sum of its own
tag's quarterly facts … is not used"). New optional keys only: `legs[k].kept_as_filed`, `legs[k].left_out` (lists of strings),
`yield_basis[name].kept_as_filed` / `.left_out` ({leg: string}). Tests: `_system/tests/test_fundamentals_dividends.py` (64, no network).
Offline replay over 94 cached companyfacts and live writes for ZTS, ATO, WRB, IRM, GEHC, HPQ, FTI, FIG, DHI, CCI, CFG, WCN.
- **Primary DPS basis — the same answer at every filing date** (`choose_dps_basis`). The 5.4.5 slot coverage was seasonal for a tag that
  files only full-year facts (each 10-K gave it four slots, each 10-Q took them away: ZTS, ATO flipped run to run), and one newer fact could
  move the slot difference by two. Now: (1) a tag whose newest fact is ≥ 330 days older than the other tag's newest has stopped — the other
  tag is primary (AVGO); (2) otherwise a tag with quarterly facts in the latest eight quarters beats a tag with only full-year facts there
  (ZTS → declared; a CashPaid Q1-Q3 + FY filer with a declared FY-only tag → paid); (3) otherwise declared. `dps_basis_detail` ends with the
  rule that decided. Replayed at eight run dates (2025-03 … 2026-12) over the cache, a name changes basis at most once (when a tag starts
  or stops).
- **An FY DPS fact below the sum of its own quarters is kept as filed unless a filed value replaces it.** The quarters come from the latest
  filing and can be the faulty side (FTI re-tags Q1 2019 at the year's 0.52; HPQ's 10-K tags YTD values as quarters). The FY fact is set
  aside only when (i) the other tag's FY fact for that year is ≥ 90 % of the quarters (NVDA FY2016: CashPaid 0.395 replaces declared
  0.115), or (ii) the quarters are borne out by the tag's year-to-date facts, or each equals the FY value with at least two of them filed
  in their own quarter's report (IBKR tags the quarterly rate in every context). Otherwise it stays, with a note naming the quarters. Two
  fiscal calendars inside one year (YUM 2016) skip the comparison. FTI FY2019 0.52 / FY2020 0.13 are back (`last_cut_fy` 2020, was 2017);
  HPQ FY2019 0.64 is back (`growth_years` 9, was 5).
- **Quarterly DPS facts re-filed at another value** (`original_quarterly_dps`, in `dividends_inputs`): when one quarter's filings disagree
  on today's share basis, the value equal to the same tag's year-to-date arithmetic (YTD − the YTD a quarter shorter; for Q1, 6M − Q2) wins;
  when that decides nothing, the filing that first reported the quarter. One split-notes line lists the changes. FTI Q1 2019 0.13 (not
  0.52); WRB Q2 2020 0.12 (not the six-month 0.23); WRB Q2 2021 keeps the later 0.63 its 6M − Q1 supports; ARES 2018 0.40 / 0.37.
- **Frequency.** The FY-count rule needs the FY total and the quarters inside it from the same tag (ZTS: CashPaid 2.03 vs Declared 0.5, 0.5, 0
  read "irregular"); a remainder counts as an extra payment only when it is ≥ half the year's smallest positive quarterly fact
  (`fy_remainder_is_a_payment`; IRM 3.22 − 3.219 is rounding); an FY count of "irregular" yields to a regular spacing. When the per-share
  facts read irregular / semiannual / annual while cash dividends are paid in each of the last four quarters, `frequency` is "quarterly" and
  `frequency_basis` starts with the cash quarters and keeps the per-share reading ("… read semiannual (…) because they are filed on a
  declaration cadence"): only on the common-stock dividends tag, or on the total `PaymentsOfDividends` line when its four quarters are within
  0.85–1.15× of `dps_ttm` × the latest diluted count (GEHC 64.0M vs 0.14 × 457M). GEHC, HPQ, IRM, ZTS read quarterly; WMT-shaped annual
  declarers that pay quarterly read quarterly from cash.
- **Cash payer status** (the HSY rule) comes only from the COMMON dividends line (`PaymentsOfDividendsCommonStock`,
  `PaymentsOfOrdinaryDividends`, IFRS dividends to owners of the parent) and never overrides per-share facts filed as zero after a stale last
  payment (or a latest FY DPS of 0): that is a suspension ("filed as zero since …", `frequency` "irregular"). Per-share facts that simply stop
  while only the total line is paid read neither "suspended" nor "not a suspension": `frequency` null, "whether the common dividend continues
  is not filed".
- **dps_ttm roll-forward across tags**: FY total + quarters since − the same quarters a year earlier is used when those quarters are one tag;
  when that tag is not the FY total's, `dps_ttm_basis` says "mixed basis: … the year-over-year change in the declared quarterly rate is
  applied to the paid total" (ZTS 2.09, ATO 3.87, ED 3.38).
- **Signs by kind** (`sign_fixed_flows` entries are `(key, text, kind)`): dividends paid and repurchases below zero are still sign errors read
  as absolute amounts (`sign_corrected`). Issuance below zero is a sign error only when the same fiscal year's other facts (same start) are
  positive (CCI pattern); otherwise it is a net line kept as filed (`kept_as_filed`; IRM FY2022 −4.8M, LRCX −43,000) and lowers the deduction.
  A quarter whose facts are all positive but whose year-to-date total decreases is left out as such (`left_out`: "the year-to-date facts
  decrease (A = x > B = y) — no quarter can be derived"), never called a sign error; `yields_display` notes say "filed below zero, read as the
  absolute amount" only for real sign corrections (DHI, CMPS, STZ, WCN no longer do).
- **Issuance "totals" must be totals** (`combined_duration_facts`): `ProceedsFromIssuanceOfCommonStock` / `ProceedsFromSaleOfTreasuryStock` /
  the plan-including-options tag / `ProceedsFromIssuanceOrSaleOfEquity` replace their components only when ≥ the components' sum (0.5 %
  rounding); a smaller one is a separate statement line and every line is summed. FIG issuance TTM 591.0M (was 432.9M), DHI FY2025 18.5M
  (was 0), ROP adds treasury sales to stock-plan proceeds. KR (182M on both lines) is unchanged.
- **Splits.** A split read from re-filed values takes the simplest whole-number ratio p/q (p, q ≤ 10) within 1 % of the DPS ratio, else of
  the share-count factor (`snap_ratio`; WRB June 2024: 1.5, not 0.89 / 0.59 = 1.50847). A ratio filed rounded and inverted (WRB 2019 0.6667,
  counts filed in thousands vs units) reads 1.5. The same ratio tagged again within 400 days is a second split only if a filing re-files a
  value already on the first split's basis (WCN's 1.5 at 2018-03-31 dropped: its older DPS were ÷2.25). A ratio fact the annual diluted
  counts do not bear out across the first post-split filing is not applied (CFG's 6 at 2021-12-31, counts ×0.94: CFG FY2015-FY2020 DPS
  0.40 … 1.56, were ÷6). `basis_breaks` reads the annual diluted counts restated to today's share basis (`dividends_inputs` meta
  `shares_by_end`, passed in `ctx`), for the fiscal years the annual table carries — WRB's false FY2022 "unfiled split" is gone and its real
  FY2021 0.893 → FY2022 0.59 decline is `last_cut_fy` 2022.
- **Not changed.** `build_quarterly`'s own rows (the dividends block corrects its copies). A quarterly DPS fact filed only once, in a later
  comparative (FTI Q2 / Q3 2020 at 0.13), is shown as filed — DPS is never derived by subtraction. DXCM's 4 tagged at 2019-12-31 (no share
  count filed before it) stays in `split_adjustments`; it touches no DPS fact.

### profile.py review round 3 (2026-10-15) — lead-in preamble, per-type splits, Human Capital first, readable dates
No shape change; these change which filed text / count is published.
- **`about.description` skips a leading definitional / navigational preamble.** Before the first prose line, leading sentences that
  only say who "we" are ("referred to herein as", "As used in this report, references to ... refer to", "Unless the context
  requires otherwise", "the terms ... are used interchangeably"), give the principal executive office / telephone number / website,
  state the units ("All amounts are in millions") or point elsewhere ("We refer you to Item 1A ...", "For more information ... see
  Note 22") are dropped, as the forward-looking-statements lead-in already was. Yum! Brands now opens "YUM has over 63,000
  restaurants in 155 countries ..." (was 846 characters of incorporation / address / phone / website / defined terms); Arch Capital
  "Arch Capital is a publicly listed Bermuda exempted company ..." (was three lead-in sentences). EMCOR, MetLife, Old Dominion,
  Paychex, PSEG, Sysco and WEC lose their opening definitions sentence. Such sentences never count toward the 300-character minimum
  before the walk may stop at a sub-heading, and a sub-heading met before that minimum is dropped rather than published inside the
  text (Con Edison now continues past its trailing "As used in this report, the term ... refers to" sentence and the "Con Edison /
  CECONY" labels into "Con Edison's principal business operations are ..."). A section that is only preamble yields null.
- **`about.employees`: a per-type / per-location split with no filed total is never published.** "17,550 full-time employees and
  2,045 part-time employees", "4,000 salaried employees and 6,000 hourly employees", "2,000 employees domestically and 500 employees
  internationally", onsemi's "22,600 regular full-time employees and about 70 part-time or temporary employees" (U+2010 / U+2011
  hyphens are now plain hyphens in the text) and Axon's "5,100 full-time employees and more than 1,200 temporary employees" -> null
  with the sentence in `employees_unresolved` (reason "a per-type / per-location breakdown with no filed total"). Not summed: summing
  the parts would be one explicit owner-approved rule with its own `basis`, not done here. Still the total: a second count of
  non-employee labour ("1,234 employees and 5,678 independent contractors", "130,301 people worldwide and 1,233 contract workers" —
  Chipotle), a first count said to be the whole ("worldwide", "around the globe" before the second count), "including" / "excluding
  the 8,000 employees of our joint ventures", and prior-year comparisons. "internationally" / "across" after the second count no
  longer make the first count a whole-workforce statement.
- **Ranking**: (registrant subject, form, proximity to the Human Capital / Employees passage, latest date, position) — proximity now
  ranks BEFORE the date, so a later-dated "we had N ..." elsewhere in the 10-K cannot beat the count under the heading. "people",
  "persons", "individuals", "associates", "colleagues", "workers" and "staff" count as a workforce only inside that passage or with a
  form of "employ"; a count followed by "enrolled", "using", "serving", "holders", "as customers / members / executive officers"
  etc. is never a headcount.
- **`about.employees.as_of` is ISO or a bare year, never raw text.** "Sept." / "Sept" read as September (Super Micro writes "Sept.
  30, 2025"); a stated date that is not a calendar date ("February 30, 2026", Feb 29 in a non-leap latest year of a multi-year
  sentence) rejects the sentence (`employees_unresolved` reason "a headcount sentence whose date cannot be read as a calendar date").
- **Verified**: `python _system/tests/test_profile.py`; offline re-extraction over the 102 cached annual documents (descriptions
  changed only for ACGL, ED, EME, IR, MET, ODFL, PAYX, PEG, SYY, WEC, YUM, plus RKT's U+2011 hyphen; employees changed only for AXON
  -> null and ON's note); live single-name runs listed in the round's report.


### statements.py review round 4 (2026-10-15) — newest filing wins, one basis per period, Q4 per-share rules, splits
Additive to the statements sections above; where a sentence there reads differently (notably round 3's "a period's value is the
CONSENSUS of its filings"), THIS one wins. No key added or removed; `schema_version` is now 3, so the `--all` skip rule rebuilds every
file once. Tests: `python _system/tests/test_statements.py` (37, no network).
- **The newest filing of a period wins** (`pick`), as before round 3, once three anomalies are dropped (`drop_anomalies`, each
  warned): a power-of-ten slip of another filing's value (HAL, HIG, unchanged); a filed **0** that is the period's newest figure while
  an earlier filing reported a non-zero one (`filed zero …` — DXCM's FY2014 10-K tagged EPS 0 for every 2013 quarter: Q2–Q4 2013 now
  −0.035 / −0.02 / −0.01 split-adjusted, Q4 = FY − three quarters); a **shifted column** — a value only the newest filing(s) carry
  that equals, exactly and with ≥ 3 significant digits, the value an EARLIER filing gave the comparative period one year away, when
  the late filing does not itself report that neighbour at the same value (`shifted column …` — HBAN's 2015 10-K: 2010 cash 847,888K
  kept, not 2011's 1,115,968K; MTD's 2012 10-K quarterly data shifted a year; a restated goodwill that simply did not move is not a
  shift). The round-3 consensus vote is gone: it kept a year restated only once on its original basis next to restated neighbours,
  and mixed bases inside one period (ECHO FY2022: DISH-recast income statement with the EchoStar-only balance sheet, ROE 72%).
  Now ECHO FY2022 cash 2,497.5M, equity 21,487.6M, ROE 11.8%; HPQ FY2014 56,651M (post-HPE, FY2015 −9.2%); APP FY2023 1,841,762K
  (continuing, FY2024 +75.1%); TKO FY2024 +51.5%; NVT FY2022 2,295.1M and goodwill 1,466.4M; DXCM FY2020 net income 549.7M, EPS
  1.33, diluted shares 420.4M (ASU 2020-06 restated). The `consensus over latest filing …` warning no longer exists.
- **Provenance.** A cell's provenance is every accession that filed its value (within 0.5%). `growth_annual` is null where the two
  years' values share no filing although some filing reported both years — two filing generations (the earlier year as originally
  reported, the later one restated); warning `growth across filing generations …` lists the line-years (CCI FY2023 revenue: 4,734M
  continuing vs FY2022 6,986M total → null). Over the 94 cached names this blanks ~4% of annual growth cells (76,363 → 73,087).
  Derived lines carry the intersection of their inputs' provenance; EBITDA, FCF, owner's earnings, gross / operating / net / FCF
  margins are **null** in a fiscal year whose inputs share no filing although one filing carries them all (warning `same filing: …`;
  APP FY2023–FY2024 FCF margin: total-company FCF over continuing revenue). A combo line (inventory = FIFO − LIFO reserve, continuing
  OCF) is built only from legs of one generation.
- **FCF on one basis when discontinued operations are split out of the cash-flow statement.** In a period whose statement files
  `CashProvidedByUsedInInvestingActivitiesDiscontinuedOperations` ≠ 0, capex is continuing-only, so FCF and owner's earnings use
  continuing OCF: `NetCashProvidedByUsedInOperatingActivitiesContinuingOperations`, else OCF − `CashProvidedByUsedInOperating-
  ActivitiesDiscontinuedOperations` (same filing generation); blank when neither exists. The OCF line itself stays the filed total.
  CCI FY2023 / FY2024 / FY2025 FCF = 1,691M / 1,644M / 1,690M (3,126 − 1,192 − 243; 2,943 − 1,123 − 176; 3,057 − 1,185 − 182; 10-K
  0001051470-26-000016), was 2,883M / 2,767M / 2,875M. Net margin uses continuing net income in a period with discontinued
  operations (revenue is continuing-only there). Warnings `free cash flow: …`, `net margin: …`.
- **Q4 per-share figures.** The fiscal Q4 BASIC weighted count is still day-weighted from the year and three filed quarters. A Q4
  DILUTED count is no longer derived that way (antidilution; treasury-stock / if-converted results differ by period): in a LOSS Q4
  (net income to common, else net income, < 0) it is the derived basic count, otherwise null — never below basic (DXCM Q4 FY2018
  355,083,000 = basic; Q4 FY2022 null). Q4 EPS (basic and diluted) = FY EPS − the three FILED quarters, rounded to 6 decimals, marked
  derived (DXCM Q4 FY2022 0.82 − 0.23 − 0.12 − 0.24 = 0.23); not derived when the year's four net-income quarters miss its net income
  by > 1% (different bases — DXCM FY2020 after the ASU 2020-06 restatement) or when the result's sign contradicts the Q4 net income
  by more than a cent (warning `Q4 EPS not derived …`). An EPS cell whose filings disagree and whose shown value is 0 or of the
  opposite sign to net income (to common) while that income ÷ shares is ≥ 1 cent is blanked (`EPS blanked …`).
- **Interest.** A period's interest-expense figure is NET (interest income blanked for it) when it came from a net tag OR when the
  gross tag's value equals minus a net tag's value for the same period in any filing (0.5%): KR FY2023 / FY2024 (535M / 441M under
  `InterestExpense`, −441M under `InterestIncomeExpenseNonoperatingNet`) — interest income 33M / 118M no longer shown beside it. The
  label is "Interest expense, net" only when EVERY figure on the row is net; a row mixing gross and net periods keeps "Interest
  expense" and the warning `interest expense: the row mixes gross and NET figures …` names the net span (KR, JBL, CBRE, RMD).
- **Splits.** `split_borne_out` compares the last diluted count (fiscal year OR quarter) filed before a ratio's date with the first
  count for a later period filed after it; a flat count is no split, and a ratio tagged only on duration contexts with nothing filed
  since is not applied. Q (Qnity): 0.5 on 2026 duration contexts is the spin-off distribution ratio — not applied; FY2023–FY2025 EPS
  2.42 / 3.31 / 3.30 and FY2023 diluted shares 209.4M as filed (were 4.84 / 6.62 / 6.60, 104.7M). Splits inferred from re-filed
  counts accept ANY whole ratio (n or 1/n, n ≤ 100) from even one period when a `StockIssuedDuringPeriodSharesReverseStockSplits` /
  `…StockSplits` instant dated between the last old-basis filing − 120 days and the re-filing corroborates it; the split is dated
  and cut off at that instant. DFTX 1-for-15 (2022-08-26): FY2020 diluted 17,748,039 and EPS −1.95 (filed 266,220,592 / −0.13).
  `split_events_dedup` attaches a duration-context ratio fact only to a same-ratio event whose own chain of filings (gaps ≤ 400
  days) reaches it and whose date is not a year before the context starts, so a second split of the same ratio a few years on is a
  second event (WRB 2019 / 2022 / 2024 3-for-2; ODFL; CNC unchanged).
- **One capex caption per series** (`sticky_tags`): walking the periods in order, a period whose priority tag differs from the
  previous period's keeps the previous tag while the filer still files it for that period (EXR: `PaymentsToDevelopRealEstateAssets`
  for FY2022–FY2025 — 62.0M / 100.2M / 128.6M / 143.0M — not `PaymentsToAcquireProductiveAssets` 1,193.3M / …; FY2022 FCF 1,176.1M,
  was 44.9M). A caption change that remains is warned and blanks the growth across it.
- Split-adjusted values are trimmed to 12 significant digits (−1.95, not −1.9500000000000002).
- **Verified**: tests above; offline rebuild of all 94 cached companyfacts (no crash, JSON finite); live single-name writes for
  CCI, APP, DXCM, KR, JBL, CBRE, RMD, ECHO, HPQ, TKO, NVT, Q, DFTX, EXR, HBAN, HIG, HAL, CCL, ALNY, AXON, CNC, WRB (never `--all`).
