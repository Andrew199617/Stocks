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
