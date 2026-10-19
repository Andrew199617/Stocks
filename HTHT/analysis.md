# HTHT — H World Group Limited
v5 run (engine 5.4.0), 2026-10-17. All figures below are copied from key_numbers.md, dcf_numbers.json, financials_history.csv, fundamentals.json, or the company's own FY2025 Form 20-F / Q2 2026 results — none are recomputed.

## What it is
China's dominant economy/midscale hotel group (formerly Huazhu): H World China (HWC — Hanting, JI Hotel, Orange, Ni Hao and other brands) plus H World International (HWI — the ex-Deutsche Hospitality / Steigenberger leased estate in Europe and beyond). It reports in RMB under US GAAP on Form 20-F; the Nasdaq instrument is an ADS, each representing ten ordinary shares (FY2025 20-F cover); ordinary shares also list in Hong Kong (1179). The model is shifting asset-light: at June 30, 2026 the network was 13,539 hotels / 1,335,445 rooms with 93% of rooms under manachised & franchised (M&F) agreements, and a pipeline of 3,089 hotels (Q2 2026 results).

## Owner's earnings
**FY2025 (20-F via EDGAR, from financials_history.csv, with the capex override applied):** operating cash flow $1,198,000,000; capex $118,271,520 (override — see OVERRIDE); SBC $60,000,000 (always a real cost).
- **Conservative owner's earnings FY2025: $1,019,728,480 = $3.14/share per ADS** (key_numbers.md: latest FY OE/share $3.14, latest FY OE total $1.020B).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $833,951,400 for FY2025 — same ballpark, below the conservative figure; the conservative (OCF-based) series is the one the engine and this verdict use.
- OE positive 5 of the last 5 fiscal years (dcf_numbers.json), but the level swung violently through COVID: conservative OE/share per ordinary share was $0.0201 (FY2021) and $0.0302 (FY2022) against $0.2815 (FY2023), $0.2662 (FY2024) and $0.3140 (FY2025) in financials_history.csv — see OE_VOLATILE.
- Balance sheet (dcf_numbers.json): net debt -$654,662,920 (net cash on the engine's debt/cash lines; net debt / normalized OE -0.07x) — but lease liabilities are $3,879,000,000, the real fixed obligation of the leased estate, and they sit outside that net-debt line.

**Base used = the engine's normalized base, median of the last 3 FY OE/share: $2.82 per ADS** (base_oe_normalized_per_share $2.8151, base_source median_of_last_3_fy_oe_per_share; the median year is FY2023). No TTM pin was used: ttm.py exited 3 with the message "ttm.py: cannot compute TTM for HTHT (CIK 1483994): ocf: no annual (FY) fact; sbc: no annual (FY) fact; shares_diluted: no annual (FY) fact; capex: no capex facts in companyfacts under any candidate tag and no capex_override in judgment.json — refusing to zero-fill (same DATA_GAP standard as the engine)" when run before judgment.json existed, the standard 20-F fact-shape failure seen on other foreign filers in this sweep, so there is no ttm.json for this name and the median base stands, per the sweep spec. Post-FY evidence is consistent with the base rather than above it: Q2 2026 revenue was RMB7.1 billion, +10.8% YoY, and management raised FY2026 group revenue guidance only to 4%-8% growth (from 2%-6%), with M&F revenue guided +16%-20% (Q2 2026 results, filed 2026-08-17).

## OVERRIDE — capex (filing) and ADS ratio
- **The gap:** the preliminary engine run exited 4 with `DATA_GAP:capex` — capex missing for fiscal years 2023, 2024, 2025 of the last 3 (dcf_numbers.json data_gap: ["capex"]) — no tier, correctly. In fact no capex value is filed under any candidate tag in any year: financials_history.csv showed capex blank / assumed-zero for 2016-2025 before the override.
- **The decision (bounded worker authority, kind "filing"):** judgment.json carries `capex_override = {value: 828000000, kind: "filing", source: "Form 20-F for fiscal year ended December 31, 2025 (filed 2026-04-24), Consolidated Statements of Cash Flows, investing activities line 'Purchases of property and equipment': RMB828M for FY2025 (US$119M in the filing's own convenience-translation column), with RMB883M for FY2024 and RMB894M for FY2023 in the same statement"}`. The engine applies this single FY2025 value to every missing period (periods_filled: all of 2016-2025 in overrides_applied / key_numbers.md); against the true per-year figures in the same statement it understates FY2023 capex by RMB66M and FY2024 by RMB55M — slightly aggressive in direction, ~0.8% of those years' operating cash flow, noted not hidden. Declared in RMB, the reporting currency; the engine FX-converts at period-end ECB rates (the filled USD values in financials_history.csv are $116,541,000 for FY2023, $113,436,000 for FY2024 and $118,271,520 for FY2025).
- **Out-of-band, acknowledged:** the engine flags the override out of band because its band anchors on the last filed value under an engine-read tag, and no such value exists (last_filed_value null); judgment.json carries an ack_reason stating exactly that. The value itself is a filing figure, not an estimate.
- **Measured impact (key_numbers.md / dcf_numbers.json override_impact):** base OE/share $3.16 zero-fill → $2.82 with the override (-10.99%); weighted IRR 14.07% → 12.94% (-1.13pp). Unblocks tier: YES — without it there is no tier at all. Because the tier exists only because of an override, score.json sets alert_eligible: false with exit_alert_suppressed_reason "tier exists only because of a judgment override" (moot here — the tier is C, not S/A).
- **ADS ratio:** judgment.json carries ads_ratio = 10, sourced from the same 20-F cover (each ADS represents ten ordinary shares). Per-share figures were scaled x10 so they are comparable to the $46.50 ADS price (flag ADS_RATIO_APPLIED).

## Moat: 6/10 — moderate, real but not wide
Justification: China's dominant economy/midscale hotel platform: 13,539 hotels and 1.34M rooms (Q2 2026), the Hanting/JI brand pair, a direct-membership distribution base and an asset-light model that is now 93% manachised/franchised rooms, with M&F revenue +25.2% YoY in Q2 2026. That is real scale, brand and cost advantage in its segment. Capped at 6 because the measured return history does not clear a wide-moat bar through a cycle: roic_proxy (fundamentals.json) was near zero/negative in FY2021-22 (0.27%, -0.68%) and recovered to 10.37% / 21.72% / 11.94% in FY2023-25 — good, not consistently well above the cost of capital, and the series is COVID-broken. Gross margin is not presented in the filing-direct data (fundamentals.json gross_profit/cogs are null — the 20-F presents hotel operating costs, not COGS), so no gross-margin claim is made.
- FOR: Scale network in China lodging: 13,539 hotels / 1,335,445 rooms in operation at June 30, 2026 (Q2 2026 results), with Hanting and JI Hotel the dominant economy/midscale brands — density rivals cannot quickly replicate
- FOR: Asset-light manachise/franchise engine: 93% of rooms are M&F (Q2 2026), and M&F revenue grew +25.2% YoY in Q2 2026 to RMB3.6B — franchisees fund the capex, H World collects fees
- FOR: Direct distribution: H Rewards membership and member bookings reduce OTA dependence and give pricing/revenue-management leverage (HWC ADR +2.6% YoY and RevPAR +1.1% YoY in Q2 2026)
- FOR: Proven low-cost operating system for economy/midscale hotels (standardized design, central reservation and procurement) — a structural cost advantage in its segment
- AGAINST: Returns are not through-cycle proven: roic_proxy in fundamentals.json was 0.27% (FY2021) and -0.68% (FY2022) in the COVID trough before recovering to 10.37% / 21.72% / 11.94% (FY2023-25) — earnings power is hostage to the China travel cycle and RevPAR
- AGAINST: H World International (ex-Deutsche Hospitality / Steigenberger) is a leased-hotel drag: HWI revenue -5.8% YoY in Q2 2026 as leased hotels are exited, and lease liabilities are large ($3,879M in dcf_numbers.json) against a thin equity base
- AGAINST: Competition is dense and brands are replicable at the economy/midscale end: Jin Jiang, BTG Homeinns and Atour contest the same tier-1-4 cities; franchisees multi-home and own the real estate
- AGAINST: Growth is shifting to lower-tier cities (pipeline 3,089 hotels at June 30, 2026) where fee density per room is lower, and group FY2026 revenue guidance is only 4%-8% including HWI
- AGAINST: China/VIE/regulatory overhang: VIE structure, PRC regulation, US ADS tail risk, and founder/concentrated governance
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-17)
Growth inputs: the engine's blended growth is 12.94% (components from key_numbers.md: revenue CAGR 5y 18.31%, revenue CAGR 3y 21.62%, latest revenue YoY 10.44%, OE/share CAGR 2y 5.61%; share count CAGR +1.44%/yr, adj -1.44pp). Default offsets (-12/-5/0/+5/+12pp) and default OE multipliers (0.75/0.90/1.00/1.10/1.25) were kept. Probabilities were skewed bearish to 15/25/30/20/10 (defaults 10/25/30/25/10) per the OE_VOLATILE flag's instruction to widen bear weight and because group guidance (below) sits well under the blend.
SANITY CHECK against actual prints: the base start (12.9%) sits above FY2025's filed revenue YoY (+10.44% in the USD translations) and above the raised FY2026 group revenue guidance of 4%-8% — the written reason it is still defensible as an OE/share (not revenue) start is the mix shift: M&F revenue grew +25.2% YoY in Q2 2026 and is guided +16%-20% for FY2026, Q2 2026 adjusted EBITDA grew +20.0% YoY, and the L&O exit shrinks low-margin revenue while fee revenue compounds — OE/share can grow faster than group revenue on that mix. The bear start (7.9%) brackets the guidance range, the super-bear start (0.9%) prices a RevPAR relapse, and the bull (17.9%) / super-bull (24.9%) starts sit at and just above the current M&F growth print (+25.2%), i.e. they require the asset-light mix shift to run at today's pace for years — possible, not the base case, and weighted at only 20% / 10%. Price $46.50.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | 0.9% | 0.75 | China RevPAR relapses; HWI lease drag persists; network growth stalls | $16.15 | 6.77% |
| Bear | 25% | 7.9% | 0.90 | Growth at guidance; mix shift offsets L&O shrinkage only slowly | $26.46 | 9.84% |
| Base | 30% | 12.9% | 1.00 | Blended filed growth; M&F mix keeps OE/share ahead of revenue | $36.71 | 12.62% |
| Bull | 20% | 17.9% | 1.10 | M&F compounding at near-current pace; HWI turns profitable | $50.36 | 15.88% |
| Super bull | 10% | 24.9% | 1.25 | Full asset-light flywheel: fee growth at today's +25% M&F pace for years | $77.75 | 21.25% |

- **Probability-weighted: IV@15% $37.90 (-18.5% vs price), IV@12% $51.72 (+11.2%), IV@10% $67.32, weighted IRR 12.94%, base-case IRR 12.62%**
- **Tier by numbers: C.** Diagnostics (key_numbers.md): OE yield 6.05%, terminal value 21.5% of IV@15%, scenario spread 4.81x, net debt -0.07x normalized OE, 9.5 months since FY end. Bear tier D (9.84%), bull tier B (15.88%) — TIER_BAND applies, verdict sized to the bear end.

## Flags — every fragility flag resolved
- **DATA_GAP:capex (preliminary run)** — resolved by the filing-sourced capex_override above; final run has data_gap_uncovered empty and overrides_applied covering the gap (all periods 2016-2025, since the tag was missing in every year).
- **STALE_FY** (FY ended 9.5 months ago): ttm.py could not compute a TTM base (its exact failure message is quoted under Owner's earnings — it found no annual facts under its matching and refused to zero-fill), so the median base was used and the reason is stated there. The post-FY evidence (Q2 2026 revenue +10.8% YoY, FY2026 group guidance raised only to 4%-8%) does not suggest a materially higher run-rate base than the FY2023-25 median.
- **OE_VOLATILE** (OE/share spans >3x over 5 years): real — it is the COVID cycle, not noise: conservative OE/share (per ordinary share, financials_history.csv) went $0.0201 (FY2021) → $0.0302 (FY2022) → $0.2815 (FY2023) → $0.2662 (FY2024) → $0.3140 (FY2025). Handled by the normalized median base, a 40% combined weight on bear/super-bear, and confidence low.
- **NI_OCF_DIVERGENCE** (2023, 2024): structural to the leased-hotel model, not a one-off tax item. In the FY2025 20-F cash-flow statement, net income of RMB4,131M (FY2023) and RMB3,102M (FY2024) reconciles to operating cash flow of RMB7,674M and RMB7,518M mainly through non-cash lease expense (RMB2,163M / RMB2,300M), depreciation & amortization (RMB1,414M / RMB1,332M) and impairment losses (RMB516M / RMB537M), partly offset by operating lease liability payments (RMB2,548M / RMB2,453M). The OCF-based conservative OE is the series used throughout, so the divergence does not contaminate the base — but it is a reminder that a large share of reported profit is absorbed by lease economics.
- **FX_CONVERTED**: reporting currency is CNY; the engine converted CNY-only periods to USD at period-end ECB reference rates (rates recorded in dcf_numbers.json fx_conversion) — flow facts use the period-end rate, not a period average, a documented simplification.
- **USD_TRANSLATIONS_USED**: where the issuer files its own USD convenience translations alongside CNY, the engine used the filed USD figures — the FY2025 lines (and the capex override's US$119M cross-check) rest partly on those translations.
- **ADS_RATIO_APPLIED / OVERRIDE_APPLIED:capex**: see OVERRIDE above — gap, decision, band acknowledgement, and measured impact (-10.99% on the base, -1.13pp on weighted IRR, unblocks the tier) are all recorded in judgment.json, dcf_numbers.json and the override registry.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.81x super-bear): real — the outcome range for a cyclical, mix-shifting hotel platform IS wide. Confidence is low, not high, and the verdict is sized to the conservative end.
- **TIER_BAND** (bear D at 9.84% vs bull B at 15.88%): the weighted C sits between two very different worlds; any position should be sized to the bear end (bear IV@15% $26.46).
- **Market-cap note (not an engine flag):** the final engine run's market_cap_est ($151,008,475,510 in dcf_numbers.json; $151.01B in score.json) multiplies the ADS price by the ordinary-share count, overstating the economic cap by the 10x ADS ratio — the same convention seen on other ADS names in this sweep. On the ADS basis (3,071,525,690 ordinary shares outstanding at 2025-12-31 per dcf_numbers.json = one-tenth as many ADSs at $46.50) the economic cap is roughly a tenth of the engine figure, i.e. under $40B; judgment.json's in_scope_under_40b is set to false to match the engine figure, as make_score.py requires, and this note is the record of the discrepancy. Scope does not affect the tier.
- **Data note:** fundamentals.json mixes filed units on this name (revenue in RMB, several other lines in the filed USD translations), so its operating-margin line is not meaningful and is not quoted here; its roic_proxy series is quoted in the moat section with that caveat in mind. Gross profit / COGS are null in fundamentals.json (the 20-F presents hotel operating costs, not COGS).

## My thoughts / overlay
- The method range is narrower than the scenario range: on the zero-filled (no-capex) base the weighted IRR was 14.07% — still a C, just under the B line — and the filing-capex override moves it to 12.94%. On the latest-FY base ($3.14/ADS vs the $2.82 median) the verdict would be a stronger C, still not a B at $46.50. No defensible input set on this engine clears 15% at this price except the bull/super-bull paths themselves.
- Quality is genuinely improving: the earnings mix is rotating from leased hotels (capital- and lease-heavy, HWI still shrinking at -5.8% YoY) toward M&F fees (+25.2% YoY), Q2 2026 adjusted EBITDA grew +20.0% YoY, and the board approved a three-year shareholder-return plan of US$2.5 billion with an ordinary dividend of US$0.87 per ADS declared alongside Q2 2026 results. That supports the growth blend — it does not close the valuation gap at $46.50.
- The bear case is not exotic: it is the company's own guidance. Group revenue growth guided at 4%-8% for FY2026 with a shrinking leased estate and lower-tier-city mix means the 12.9% base OE/share start already credits substantial operating leverage and mix shift.
- Price that clears 15%: the weighted IV@15% is $37.90 — HTHT clears Andrew's 15% hurdle only below about that price on these inputs, and a margin of safety against the bear case would require a price nearer the bear IV@15% of $26.46.

## Final verdict
- **Final tier: C** (weighted IRR 12.94% on the v5 final inputs; bear-to-bull band D to B; no tier override)
- Confidence: **Low** (OE volatility through the COVID cycle, wide scenario spread, TTM base not computable, FX-translation and ADS conventions, and a tier that exists only because of the filing capex override — though the override is filing-sourced and its measured impact is -1.13pp, not verdict-flipping)
- One-liner: China's dominant economy/midscale hotel platform going asset-light, moat 6/10 — does not clear 15% at $46.50: weighted IRR 12.94% (Tier C), weighted IV@15% $37.90 vs $46.50 price on the normalized median base OE of $2.82/ADS, with a bear-to-bull tier band of D to B — it clears 15% only at or below ~$37.90, and sized to the bear end (IV@15% $26.46).

**Correction, 2026-10-19 (ADS market-cap fix):** the market-cap note above describes the pre-fix engine. The engine now divides the share count by the ADS ratio (Andrew's ruling, 2026-10-18; Stocks PR #5): `market_cap_est` is $15.10B, and judgment.json / score.json now record `in_scope_under_40b: true`. Everything else stands — Tier C, weighted IRR 12.94%, unchanged, because the per-share figures were already ADS-scaled; only the recorded cap and scope flag were wrong.

## Engine 5.5 re-score (2026-10-19)
This is a dated addendum. The text above, including Muse's 2026-10-19 correction note, stays as written. Where this section disagrees with it, this section supersedes it.

This was a make_score-only re-score under ruling 1 ("Re-run make_score (not the engine) ... so market_cap / in_scope_under_40b are corrected without changing tiers"). `dcf_engine.py` and `ttm.py` were not run. dcf_numbers.json and financials_history.csv are still the 2026-10-19 main re-run, `engine_release` 5.4.0, which already carries Muse's ADS market-cap fix. On 2026-10-19, `make_score.py HTHT` rebuilt score.json and key_numbers.md from that record (exit 0), and then `prices.py HTHT` and `reprice.py HTHT` ran. judgment.json was not changed.

**Where the figures come from.**
- Score figures are quoted from the 2026-10-19 key_numbers.md. The "Before" column is from the key_numbers.md that make_score replaced.
- Other figures name their file in this PR: score.json, dcf_numbers.json, financials_history.csv, statements.json, fundamentals.json or `_system/README.md`.
- The open items below also quote review figures that no file in this PR prints. These are offline replays of the recorded scenario math and values from cached EDGAR companyfacts. Each is marked "cannot verify from the diff", and none is part of the score.

| | Before (5.4.0 record, make_score 5.4) | After (make_score 5.5 on the same record) |
|---|---|---|
| Base OE/share (3-yr median, per ADS) | $2.82 | $2.82 (unchanged) |
| Latest FY OE/share / OE total | $3.14 / $1.020B | $3.14 / $1.020B (unchanged) |
| Weighted IRR / base-case IRR | 12.94% / 12.62% | 12.94% / 12.62% (unchanged) |
| IV@15 (weighted) | $37.90 | $37.90 (unchanged) |
| Bear → bull band | 9.84% (D) → 15.88% (B) | 9.84% (D) → 15.88% (B) (unchanged) |
| Tier by numbers / final | C / C | C / C (unchanged) |
| Market cap (est) | $15.101B | $15.101B, basis `diluted_latest` (unchanged) |
| Scope (under $40B) | in scope | in scope (unchanged; judgment.json not rewritten) |
| Net debt / normalized OE | −0.07x | −0.72x on the ADS basis (the engine's −0.07x printed beside it) |
| Alert gates | `alert_eligible` false, `exit_alert_eligible` false (override reason) | both false; stale-release reason added (below) |

**What make_score 5.5 changed for this filer: the net-debt ratio only. The cap and scope were already right.**
- **Market cap and scope: unchanged.** Muse's 2026-10-19 main re-run already priced the cap as price × shares ÷ ads_ratio: $46.50 × 3,247,494,097 ÷ 10. key_numbers.md now prints "$15.101B (basis: diluted_latest)" and a new line, "Scope: in scope (market cap under $40B)". score.json's `market_cap_basis` reads `diluted_latest`.
  - make_score did not correct the cap again, because a 5.4.0 cap that already divides by the ratio is never divided twice.
  - judgment.json's `in_scope_under_40b` (true) already agreed, so there is no rewrite and no `scope_correction` registry event.
  - $15.101B is far from the $40B line, so a live-price move does not put the scope call at risk.
- **Net debt / normalized OE (ruling 1, "anything downstream").** Muse's fix divided the cap but not the normalized-OE total. The 5.4.0 engine still divided net debt by per-ADS OE × ORDINARY shares, which made the ratio 10× too small: −0.07x.
  - key_numbers.md now prints "-0.72x on the ADS basis (make_score: the pre-5.5 engine's ratio × ads_ratio 10 — it divided net debt by per-ADS OE × ORDINARY shares; the engine printed -0.07x)".
  - score.json records `net_debt_to_normalized_oe_ads_basis` −0.7161.
  - This supersedes the "net debt / normalized OE -0.07x" in the Owner's earnings section and the DCF diagnostics line above.

**HIGH_NET_DEBT / BIG_NET_CASH on the ADS basis: neither would fire, so no flag changes.**
- The engine's thresholds are > 3x for HIGH_NET_DEBT and < −2x for BIG_NET_CASH. −0.72x is inside both, and key_numbers.md names no crossing. The engine's flag list is hashed 5.4.0 output and stays as recorded.
- **What the balance sheet says.** Net debt (latest) is $-654.7M, i.e. net cash. It reproduces from financials_history.csv's FY2025 row: cash 1,485,000,000 against debt_current 762,337,080 and debt_lt 68,000,000 (`net_debt_basis` LongTermDebtNoncurrent+DebtCurrent).
  - On the corrected basis, net cash is about three-quarters of a year of normalized owner's earnings. That is material, but it is not a cash pile carrying the $15.101B price (BIG_NET_CASH's concern), and cash covers borrowings (HIGH_NET_DEBT's concern).
  - The real fixed obligation is the lease book. `lease_liabilities_latest` is $3,879,000,000 in dcf_numbers.json, far larger than the net cash, and by design it sits outside the net-debt test. So the corrected ratio should not be read as balance-sheet strength. The lease burden is named in the moat AGAINST list above.
- The earlier conclusion stands: the balance sheet does not move the verdict.

**Alert gates: both closed until an engine re-run, as expected.**
- make_score 5.5 treats output from any earlier engine release as stale. score.json has `alert_eligible` false and `exit_alert_eligible` false, with `exit_alert_suppressed_reason` "engine output predates release 5.5.0 — re-run the engine before an exit alert; tier exists only because of a judgment override".
- At Tier C no entry alert would fire in any case.
- The capex override impact is carried, not re-measured. key_numbers.md prints: base OE/share $3.16 (no override) → $2.82 (with override), -10.99% · weighted IRR 14.07% → 12.94% (-1.13pp), "carried from the prior score.json, not re-measured (engine output release 5.4.0 vs current 5.5.0)". score.json marks `impact_carried_from_prior_score` true with `counterfactual_engine_release` 5.4.0. The registry entry's impact fields are identical to the prior ones.

**Flags on the record: none new, but STALE_FY is reopened.** make_score does not recompute flags. The nine on the record are the 5.4.0 engine's: STALE_FY, OE_VOLATILE, NI_OCF_DIVERGENCE, FX_CONVERTED, USD_TRANSLATIONS_USED, ADS_RATIO_APPLIED, OVERRIDE_APPLIED:capex, WIDE_SCENARIO_SPREAD and TIER_BAND.
- Eight keep the resolutions in the Flags section above, and the corrected ratio changes none of them. TIER_BAND is still sized to the bear end: bear IV@15 $26.46.
- **STALE_FY: not resolved; open for the next engine re-run (escalated).**
  - The Flags section rests on ttm.py's exit-3 message. That run happened before judgment.json existed: its capex leg says "no capex_override in judgment.json", which no longer holds.
  - WORKER_SPEC step 4 allows the median-base fallback only at IFRS filers. HTHT files US GAAP.
  - key_numbers.md gives 9.6 months since FY end. That supersedes the "9.5 months" in the DCF and Flags sections above.
  - statements.json shows why ttm.py has nothing to read: "the filer reports interim periods on 6-K only (no 10-Q)", and "no quarterly facts could be assembled".
  - A TTM base would therefore have to come from the H1 2026 interim report (6-K or HKEX). It needs six-month operating cash flow, purchases of property and equipment, purchases of intangible assets and share-based compensation. The base would be FY2025 + H1 2026 − H1 2025, declared as a `base_override` with the construction shown.
  - Whether that report prints a cash-flow statement: cannot verify from the diff.
  - This needs a new judgment input and an engine run, both excluded from this pass by ruling 1, so it is escalated to Andrew.
- **The base-case growth start is above the company's own guidance: open for the next engine re-run.**
  - The base growth start is 12.9% (key_numbers.md). The FY2026 group revenue guidance of 4%–8%, quoted in the DCF section above, is below it.
  - The mix-shift reason in that section is written down. But the blend is lifted by revenue CAGRs that start in COVID trough years: rev CAGR 3y 21.62% and 5y 18.31%, against OE/share CAGR 2y 5.61% and latest revenue YoY 10.44% (key_numbers.md).
  - A review replay of the recorded scenario math (offline, printed by no file in this PR, cannot verify from the diff): a base start of 8% gives a weighted IRR of 10.95%, and a start of 10.44% gives 11.91%. Tier C holds in both, but at 8% it sits less than 1pp above the D line.
  - Offsets are a judgment input that ruling 1 holds fixed here. Before the next run, either the offsets put the base start at the top of guidance plus a mix-shift uplift shown as OE/share arithmetic, or Andrew signs off on the current start.
- **Corrections to the OVERRIDE section above.**
  - It says "no capex value is filed under any candidate tag in any year" and that the band has no anchor ("last_filed_value null"). Both are wrong.
  - statements.json carries PaymentsToAcquirePropertyPlantAndEquipment for FY2009–FY2012 only (FY2012: RMB 998,050,000). dcf_numbers.json `override_checks.capex` records `last_filed_value` 160,198,000, `last_filed_unit` "USD" and `out_of_band` false. The anchor is the issuer's USD translation of that FY2012 line.
  - No PP&E-tag fact exists in the last 3 FY (financials_history.csv `capex_tag` reads OVERRIDE in each year), so the gap and the override stand.
  - judgment.json's `capex_override.ack_reason` repeats the old description ("last_filed_value is null"; capex "blank/assumed-zero in every year"). It is stale but harmless, because the override is in band. It was not edited in this make_score-only pass. The worker who restates the override (open item 1) should refresh or drop it at the same time.
- **Confidence stays low.** WIDE_SCENARIO_SPREAD (4.81x) is on the record, STALE_FY is open, the tier exists only because of an override, and the open items below are unresolved.

**Open items for the next engine re-run. None is applied, because ruling 1 limits this pass to make_score.**
1. **USD-override branch (ruling 7): restate the RMB capex override before the next engine run.** This is the item that matters most.
   - judgment.json declares `capex_override` 828,000,000 in RMB, the reporting currency, so the 5.4.0 engine FX-converted it.
   - Under 5.5, `_override_usd` uses an override verbatim as US dollars when the field's last filed unit is USD. For HTHT it is, because of the FY2012 USD anchor above (`currency_basis` `last_filed_unit_usd`).
   - The engine would then read $828M of capex a year, about 7× the filing's own US$119M quoted in the override source.
   - `_system/README.md` (Engine 5.5 entry, USD-override paragraph) records the result in the offline differential: base $2.8151 → $0.6922, moving the name C → D. That comes from reading RMB as dollars and says nothing about the business.
   - make_score 5.5 refuses that output: an applied kind "filing" override used under `last_filed_unit_usd` scores only with an explicit `currency: "USD"`. The misread therefore cannot be published. That gate is an engine 5.5 [ADDITION] awaiting Andrew's ratification.
   - The fix: restate `capex_override` as the filing's own US-dollar total, declared `currency: "USD"` (see item 2 for which total), or block the name NEEDS_MAIN_AGENT: capex (WORKER_SPEC). Adding `currency: "USD"` to the RMB 828,000,000 would be wrong.
   - Restating now, without an engine run, would leave judgment.json disagreeing with dcf_numbers.json's `overrides_applied` (828,000,000). That is why it was not done in this pass.
2. **Capex completeness: the restated figure should be the filed total, intangible purchases included.**
   - financials_history.csv has FY2023–25 capex of $116,541,000 / $113,436,000 / $118,271,520. That is RMB 828M in every year (`capex_tag` OVERRIDE).
   - The filed totals are higher. Take the override source's own PP&E figures (RMB 894M / 883M / 828M) and add statements.json's PaymentsToAcquireIntangibleAssets (RMB 7,000,000 / 15,000,000 / 10,000,000). At the engine's period-end rates in dcf_numbers.json `fx_conversion`, that is $126,815,750 / $123,026,000 / $119,699,920, so the CSV is 8.8% / 8.5% / 1.2% short.
   - A review replay (offline, cannot verify from the diff) puts the effect at: base $2.8151 → $2.7844 (−1.09%), weighted IRR 12.94% → 12.84%. Tier C holds.
   - Under 5.5 an override is read as the total line, and intangibles are not added in override years. So the restated override must already include them.
   - The RMB 894M / 883M appear only in the override text and in cached EDGAR companyfacts outside this PR: cannot verify from the diff. In that cache, PaymentsToAcquireMachineryAndEquipment carries them, along with the issuer's USD translations of $126M / $121M / $119M.
   - statements.json names that tag as unlisted ("those filings carry unlisted tags PaymentsToAcquireMachineryAndEquipment"). Adding it to the capex component list in a separate code PR would let the engine read each year's filed value and retire the override. That is a decision for Andrew.
3. **"OE-positive years (last 5): 5/5" in key_numbers.md is not supported by filed capex.**
   - The Owner's earnings section quotes FY2021 / FY2022 OE/share of $0.0201 / $0.0302. Both rows use the RMB 828M override fill (`periods_filled` 2016–2025), but the override source cites only FY2023–25.
   - statements.json (CNY): FY2021 operating cash flow 1,342,000,000 and SBC 109,000,000; FY2022 operating cash flow 1,564,000,000 and SBC 87,000,000.
   - The cached EDGAR companyfacts outside this PR show PaymentsToAcquireMachineryAndEquipment of RMB 1,658,000,000 for FY2021 (20-F filed 2024-04-23) and RMB 1,049,000,000 for FY2022: cannot verify from the diff.
   - On those figures FY2021 OE is negative (1,342M − 109M − 1,658M), FY2022 stays positive, and the count would be 4 of 5.
   - The base and growth use FY2023–25, so the tier is not affected. OE_VOLATILE fires either way.
4. **Moat evidence: fundamentals.json's FY2023–25 roic_proxy is a unit artifact.**
   - The moat section and judgment.json (`moat_justification`, `moat_against`) quote roic_proxy of 10.37% / 21.72% / 11.94% for FY2023–25 from fundamentals.json.
   - Those rows mix units. FY2025 in fundamentals.json has debt_current of 5,337,000,000 filed in CNY, next to equity of 1,831,000,000, cash of 1,485,000,000 and operating income of 975,000,000 in the issuer's USD translations.
   - statements.json, which is all in CNY, gives 34.78% / 33.58% / 58.31%.
   - The cap at 6 ("measured return history does not clear a wide-moat bar") therefore rests partly on the artifact. The FY2021–22 trough holds in direction: operating income was 26,000,000 and −43,000,000 in fundamentals.json, and statements.json prints no ROIC for those years.
   - The moat stays at 6 here, because ruling 1 holds it fixed. A review replay at moat 7 (offline, cannot verify from the diff) gives a weighted IRR of 13.35%, still C.
   - The next worker should re-justify the moat on statements.json. The fundamentals.py unit mixing is a separate enrichment fix.

**What engine 5.5 reads differently for HTHT, apart from the items above.**
- **SBC (ruling 6): no change.**
  - HTHT files ShareBasedCompensation in CNY: 143,000,000 / 322,000,000 / 420,000,000 for FY2023–25 in statements.json. It also files it as USD translations: 20,000,000 / 44,000,000 / 60,000,000, the sbc column of financials_history.csv, which the engine uses under USD_TRANSLATIONS_USED.
  - AllocatedShareBasedCompensationExpense is filed in CNY only, with the same amounts as the CNY ShareBasedCompensation (cached companyfacts outside this PR; cannot verify from the diff).
  - The 5.5 engine compares the USD Share figure with the CNY Allocated one, and a cross-unit pair is never reconciled. Compared in one unit, Allocated does not exceed Share either.
  - `sbc_tag` stays ShareBasedCompensation, and SBC_TAG_RECONCILED does not fire.
- **Capex coverage: no CAPEX_COVERAGE_LOW.** Capex / D&A in financials_history.csv is 116,541,000 / 199,000,000, 113,436,000 / 183,000,000 and 118,271,520 / 180,000,000 for FY2023–25. All three are above one half.
- **Share basis and scale (ruling 2): no change.**
  - The 10-for-1 split effective 2021-06-30 (statements.json) falls before the FY2025 end, so 5.5 only records it (`share_basis.in_history_split_facts`).
  - The jump it leaves in financials_history.csv is FY2018 → FY2019 (303,605,809 → 3,043,098,899). That is outside the last four years, so the share-count CAGR (1.44%) and the base are unaffected.
  - The latest diluted count (3,247,494,097) is within 25% of the cover-page count in dcf_numbers.json (3,071,525,690), and the base is far below 20× the price. So no SHARE_SCALE or SHARE_BASIS flag fires.
- **Market cap: no change.** The 5.5 formula gives the same $15.101B.

**Why the tier is C.** This re-score leaves the numbers unchanged.
- The weighted IRR is 12.94% at $46.50 per ADS, inside the 10–15% C band. The bear-to-bull band runs from 9.84% (D) to 15.88% (B).
- The weighted IV@15 is $37.90, -18.5% versus the price, on a normalized median base of $2.82 per ADS and an OE yield of 6.05%.
- The corrected net-debt ratio (−0.72x) fires no flag and does not enter the IRR.
- reprice.py's live check at the 2026-10-16 close of $46.50 shows C at 12.94% (+0.00pp).
- `tier_override` stays null. The moat (6/10, CAP 9.8 yrs), probabilities and one-liner are unchanged. Confidence: low.
- Every open item measured so far keeps C in the review replays (cannot verify from the diff): filed capex totals give 12.84%, an 8% base start gives 10.95%, and moat 7 gives 13.35%. The TTM base (STALE_FY) is not measured.
- The C → D in the README's differential comes from the RMB override misread, so it is not a pending verdict. The real 5.5 verdict waits for the override to be restated as the filing's US-dollar total, or for a NEEDS_MAIN_AGENT block.

**Data (2026-10-19).**
- make_score.py: ran (exit 0). It wrote score.json and key_numbers.md. judgment.json was not rewritten, and the registry's capex impact is unchanged.
- prices.py: ran. It warned that the intraday chart request returned no usable points, and kept the daily series. prices.json is a gitignored cache.
- reprice.py: ran. The live tier is C, unchanged. live.json is a gitignored cache.
