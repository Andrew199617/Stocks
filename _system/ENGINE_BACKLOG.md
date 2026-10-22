# Engine backlog — deferred code defects

Every code defect a review found that a PR did not fix gets one entry here, with the thread that found it
(Andrew, 2026-10-19, ruling R5). A company data PR whose didnt-fix reply names a code defect appends an entry in the
same PR — besides its own ticker's entries in `_system/overrides_registry.json`, the one `_system/` file a data PR
may touch, and only by adding lines at the end (AGENTS.md "What is in a
PR"; `_system/PR_PROTOCOL.md` section 1; `pr_worktree.py open` refuses any other change to this file in a data PR).
`_system/README.md` "Fixes & lessons" (2026-10-21, sweep reliability) says why the file exists. A code/spec PR that
fixes an entry edits that entry's Status line in place. The next free id is
`python3 _system/pr_worktree.py backlog-next`.

Entry format (one `###` heading per entry; ids are never reused):

    ### EB-<NNN> — <file>:<function or area> — <one-line defect>
    - Opened: <YYYY-MM-DD>, <ticker> PR #<n>
    - Status: open | needs-decision (Andrew) | deferred (<ruling, date>) | fixed in PR #<n> (<YYYY-MM-DD>)
    - Threads: <comment URL> (<ticker>, P<1-3>)[; <comment URL> (<ticker>, P<1-3>) …]
    - Effect: <one line with the numbers from the thread>
    - Fix sketch: <one line>

A defect already listed that a later review hits again gets a short entry, not an edit:

    ### EB-<NNN> seen again — <ticker> PR #<n>, <YYYY-MM-DD>
    - Threads: <comment URL> (<ticker>, P<1-3>)
    - Effect: <one line>

A thread URL is `https://github.com/Andrew199617/Stocks/pull/<n>#discussion_r<id>` (or `#issuecomment-<id>`). An entry
a design found, with no PR thread, says `- Opened: <date>, design (<where>)` and `- Threads: (design <date>, no PR
thread)`. `fixed in PR #<this>` marks a fix in the code PR that seeded this file; its number replaces the
placeholder once that PR is open, and a data PR never writes the placeholder.

### EB-001 — dcf_engine.py:delta_nwc — current debt read from a series key that does not exist (`g("debt_current")`), so a falling current maturity is booked as a working-capital outflow
- Opened: 2026-10-19, AVTR PR #19
- Status: fixed in PR #<this> (2026-10-19)
- Threads: https://github.com/Andrew199617/Stocks/pull/19#discussion_r4310689017 (AVTR, P3); https://github.com/Andrew199617/Stocks/pull/29#discussion_r4313985957 (HII, P3)
- Effect: AVTR FY2025 ΔNWC +$829.7M vs +$39.4M (maintenance OE −$1,078.5M vs ≈ −$288.2M); HII FY2025 maintenance OE $379M vs $882M. Conservative OE (the scored base) unaffected.
- Fix sketch: use the assembled current-debt value (engine 5.7, lane L1, D9).

### EB-002 — dcf_engine.py:load_overrides — overrides are single-value fill-only; no per-period override exists
- Opened: 2026-10-19, EGP PR #25
- Status: open
- Threads: https://github.com/Andrew199617/Stocks/pull/25#discussion_r4312573422 (EGP, P1); https://github.com/Andrew199617/Stocks/pull/33#discussion_r4315740956 (HUT, P1); https://github.com/Andrew199617/Stocks/pull/43#discussion_r4319976161 (GGB, P1)
- Effect: EGP filed capital-improvement series gives median OE/sh $7.0909 and TTM $8.060 vs $8.089; HUT FY2025 on filed capex −$3.94/sh; GGB per-year filed diluted counts give median base $0.406841 vs $0.424355 and weighted IRR 9.887% (Tier D) vs 10.206% (C) — corrected only through a tier_override.
- Fix sketch: `{field}_override.periods: {FY: value}` with per-period source, fill-only, replayed by make_score.

### EB-003 — statements.py — FY2019 balance-sheet column internally impossible (total assets below cash)
- Opened: 2026-10-19, TXG PR #24
- Status: open
- Threads: https://github.com/Andrew199617/Stocks/pull/24#discussion_r4312148500 (TXG, P3)
- Effect: statements.json FY2019 total assets $45,604,000 vs cash $424,166,000; CSV and fundamentals.json agree on $605,923,000. Site only; scored chain unaffected.
- Fix sketch: reject a period whose assets < cash + receivables, take the fact from the filing that reports the period as current.

### EB-004 — statements.py — split effective date stamped with the filing date of the 20-F that re-filed the counts
- Opened: 2026-10-19, RDY PR #30
- Status: open
- Threads: https://github.com/Andrew199617/Stocks/pull/30#discussion_r4314554858 (RDY, P3)
- Effect: warning reads "5-for-1 split effective 2025-06-06" (filing date) vs corporate action 2024-10-28.
- Fix sketch: use the split fact's own period / the dei event date; fall back to "on or before <filing date>".

### EB-005 — fundamentals.py — growth and dividend yield mix reporting-currency and USD-translation facts
- Opened: 2026-10-19, RDY PR #30
- Status: fixed in PR #53 (2026-10-20)
- Threads: https://github.com/Andrew199617/Stocks/pull/30#discussion_r4314554871 (RDY, P3)
- Effect: FY2017 revenue Rs140.809B vs FY2018 $2.181B prints −98.45% growth; dividend_yield 3.108 (Rs DPS over a $12.87 price). Not in the scored chain.
- Fix sketch: one currency per series (the engine's FX rule), yield on DPS converted at the price date — done by the enrichment PR #53 ("one currency per fundamentals.json", test_fundamentals_currency.py).

### EB-006 — dcf_engine.py:share tags — diluted-share tag `WeightedAverageNumberOfShareOutstandingBasicAndDiluted` not read
- Opened: 2026-10-19, ESTC PR #35
- Status: open
- Threads: https://github.com/Andrew199617/Stocks/pull/35#discussion_r4316653913 (ESTC, P3)
- Effect: ESTC FY19 falls back to a non-diluted count; on the filed 54,893,365 FY19 OE/share is −$1.2265.
- Fix sketch: add the tag to the diluted candidates after the specific tags.

### EB-007 — dcf_engine.py:sbc — annual ShareBasedCompensation fact disagrees with the sum of the year's quarters; no reconciliation for that case
- Opened: 2026-10-19, ESTC PR #35
- Status: open
- Threads: https://github.com/Andrew199617/Stocks/pull/35#discussion_r4316345695 (ESTC, P3)
- Effect: quarterly sums $40,078,000 / $141,194,000 make FY22 OE −$138,007,000 and the 5-yr positive count 2/5.
- Fix sketch: flag annual-vs-quarterly SBC divergence > 10% and prefer the tagged quarterly sum when the annual fact is a partial-period restatement.

### EB-008 — dcf_engine.py:SECTOR_MODEL_MISMATCH / make_score model_fit — misfit keyed to the universe sector only; managed-care insurers (SIC 6324) missed
- Opened: 2026-10-19, OSCR PR #36
- Status: fixed in PR #<this> (2026-10-19)
- Threads: https://github.com/Andrew199617/Stocks/pull/36#discussion_r4317210649 (OSCR, P2); https://github.com/Andrew199617/Stocks/pull/37#discussion_r4317545724 (MOH, P1)
- Effect: OSCR and MOH scored `model_fit: modeled` with `exit_alert_eligible: true`.
- Fix sketch: EDGAR SIC codes plus the sector rule (engine 5.7, R1 SIC detection, lane L1).

### EB-009 — dcf_engine.py:debt tags — `LongTermDebt` / `ConvertibleDebtNoncurrent` not read, so DEBT_TAGS_BLANK fires with debt on file
- Opened: 2026-10-19, BMRN PR #42
- Status: open
- Threads: https://github.com/Andrew199617/Stocks/pull/42#discussion_r4319789907 (BMRN, P3)
- Effect: net_debt_latest null vs −$714,503,000 on the filed $597,176,000 debt and $1,311,679,000 cash; leverage diagnostics suppressed.
- Fix sketch: add the tags to the debt candidates (current/non-current split preserved).

### EB-010 — dcf_engine.py:capex — capitalized software development not in total capex (policy question)
- Opened: 2026-10-19, JKHY PR #26
- Status: fixed in PR #<this> (2026-10-19)
- Threads: https://github.com/Andrew199617/Stocks/pull/26#discussion_r4312939271 (JKHY, P1)
- Effect: FY25 total capex $225.803M ($53.358M + $172.445M) vs $53.358M; software-inclusive median base ≈ $5.30/sh, ≈ Tier D.
- Fix sketch: Andrew ruled it (R9, 2026-10-19: capitalized software counts as capex); engine 5.7 lane L9 adds PaymentsToDevelopSoftware / PaymentsToAcquireSoftware / PaymentsForSoftware and the IFRS development tags to the additive intangible capex.

### EB-011 — make_score.py:compute_override_impact — the zero-fill baseline is on the normalized base while the final figures are TTM-pinned, so the base switch is attributed to the override
- Opened: 2026-10-19, AGNC PR #39
- Status: open
- Threads: https://github.com/Andrew199617/Stocks/pull/39#discussion_r4318618238 (AGNC, P3)
- Effect: override_impact pairs $0.0865 / 3.58% (normalized, zero-fill) with $0.7530 / 11.83% (TTM, override).
- Fix sketch: when the final base is a TTM pin whose legs no override fills, measure the override on the same pin (the payable/declared-pin path already does this).

### EB-012 — _daily/site (segments renderer) — product shares above 100% shown when `ties_to_total` is false
- Opened: 2026-10-19, RTO PR #41
- Status: open
- Threads: https://github.com/Andrew199617/Stocks/pull/41#discussion_r4319224570 (RTO, P3)
- Effect: pre-central-cost segment operating profit over a post-amortisation consolidated total renders shares > 100%.
- Fix sketch: hide the share column (or label "of segment total") when `ties_to_total` is false.

### EB-013 — dcf_engine.py / ttm.py — no ESEF (EU/UK machine-readable annual report) second source for foreign filers
- Opened: 2026-10-19, RDY PR #30
- Status: deferred (R2, Andrew 2026-10-19)
- Threads: https://github.com/Andrew199617/Stocks/pull/30#discussion_r4314360756 (RDY, P2); https://github.com/Andrew199617/Stocks/pull/41#discussion_r4319224561 (RTO, P2)
- Effect: RDY scored on FY2025 (latest_period_end 2025-03-31) while the FY26 20-F existed — engine 5.7 adds the filing-instance fallback and the declared 6-K bridge; ESEF stays deferred.
- Fix sketch: filings.xbrl.org ESEF package as a third source behind companyfacts and the filing instance.

### EB-014 — make_score.py:write_key_numbers — key_numbers.md could not carry filing / release / third-party figures, so guidance quoted in analysis.md had no generated home
- Opened: 2026-10-19, TXG PR #24
- Status: fixed in PR #<this> (2026-10-19)
- Threads: https://github.com/Andrew199617/Stocks/pull/24#discussion_r4312274368 (TXG, P2); https://github.com/Andrew199617/Stocks/pull/25#discussion_r4312674348 (EGP, P2); https://github.com/Andrew199617/Stocks/pull/30#discussion_r4314360791 (RDY, P2); https://github.com/Andrew199617/Stocks/pull/35#discussion_r4316345704 (ESTC, P3)
- Effect: guidance and filing figures quoted in analysis.md traced to no generated file.
- Fix sketch: R3 facts.json — declared facts rendered under their own key_numbers.md heading and the check_quotes.py gate (engine 5.7, lane L2).

### EB-015 — make_score.py — sector-misfit notch not mechanical; reviewers re-graded it per PR
- Opened: 2026-10-19, SF PR #7
- Status: fixed in PR #<this> (2026-10-19)
- Threads: https://github.com/Andrew199617/Stocks/pull/7#discussion_r4310310489 (SF, P1); https://github.com/Andrew199617/Stocks/pull/25#discussion_r4312674334 (EGP, P1); https://github.com/Andrew199617/Stocks/pull/32#discussion_r4314856877 (FNF, P1); https://github.com/Andrew199617/Stocks/pull/39#discussion_r4318618222 (AGNC, P1)
- Effect: each misfit's one-notch softening was a judgment call the reviewer graded again on every PR.
- Fix sketch: R1 — make_score applies the notch mechanically (misfit_notch, misfit_notch_reason; engine 5.7, lane L1).

### EB-016 — dcf_engine.py:delta_nwc — NWC subtracts the raw `cash` tag (which may include restricted cash) while `cash_avail` subtracts restricted cash
- Opened: 2026-10-19, design (01 notch engine, open question 5)
- Status: open
- Threads: (design 2026-10-19, no PR thread)
- Effect: a filer whose cash tag includes restricted cash shows that restricted cash as non-operating in ΔNWC while the net-debt figure treats it as unavailable; conservative OE (the scored base) unaffected.
- Fix sketch: subtract the same available-cash figure in both places, or record why the two differ.

### EB-017 — make_score.py — a `base_override` whose source cites a CSV column is not re-verified against the CSV after the column moves
- Opened: 2026-10-19, design (01 notch engine, open question 4)
- Status: open
- Threads: (design 2026-10-19, no PR thread)
- Effect: TTMI's pin cites the `oe_maintenance` median 0.3654; the 5.7 delta_nwc fix (EB-001) moves that column, so the declared value no longer equals what the CSV now prints until TTMI's next engine run re-derives the pin.
- Fix sketch: when a base_override source names a financials_history.csv column, recompute the cited statistic from the CSV and refuse on a mismatch.

### EB-018 — statements.py / fundamentals.py — read companyfacts only, so the fiscal years the engine reads from a filing's own XBRL instance are missing from the site pages
- Opened: 2026-10-19, design (04 foreign, R2b follow-up)
- Status: open
- Threads: (design 2026-10-19, no PR thread)
- Effect: the 17 lagging ifrs-full annuals the engine reads through annual_from_instance (engine 5.7) do not appear in statements.json / fundamentals.json until companyfacts ingests them.
- Fix sketch: reuse xbrl_instance in statements.py / fundamentals.py when submissions show an annual report newer than companyfacts' latest annual period.

### EB-019 — forensic_pull.py — freshness lists 10-K / 10-Q only; 6-K interims are not flagged
- Opened: 2026-10-19, design (04 foreign, R2a follow-up)
- Status: open
- Threads: (design 2026-10-19, no PR thread)
- Effect: a pass-2 review of a 20-F / 40-F filer is not told that a newer 6-K interim exists.
- Fix sketch: list 6-K filings (interim reports only, by document type) beside 10-Q in the freshness block.

### EB-020 — statements.py / fundamentals.py — the site's cash-flow fcf / owner_earnings lines omit intangible capex, and their capex tag lists lag the engine's
- Opened: 2026-10-20, design (enrichment PR #53 review; 09 capex A3d)
- Status: open
- Threads: (design 2026-10-20, no PR thread)
- Effect: statements.json cashflow fcf / owner_earnings omit intangible capex (GGB FY2025, GMED TTM); fundamentals' display `capex_intangibles` list and statements.py's `CAPEX_TAGS` / cash-flow lines carry no PaymentsToAcquireSoftware / PaymentsForSoftware / IFRS development and no machinery & equipment / mining assets / furniture & fixtures, so at KNX / JKHY-type filers the site's statements and its unlisted-tag notice differ from the engine (separate generator path from the scored chain).
- Fix sketch: build the site's capex lines from the engine's capex assembly (dcf_engine capex lists and capex_for_period) instead of a second tag list.

### EB-021 — fundamentals.py — the fundamentals.json ttm row has no `capex_intangibles` key
- Opened: 2026-10-20, design (enrichment PR #53 review)
- Status: open
- Threads: (design 2026-10-20, no PR thread)
- Effect: GMED's TTM fcf does not reconcile on its own row (the annual rows carry the intangible leg, the ttm row cannot).
- Fix sketch: add the key to the ttm row from the same YTD legs as capex.

### EB-022 — dcf_engine.py:shares — SF `shares_diluted_latest` 110.05M looks pre-split beside a post-split price ($67.56)
- Opened: 2026-10-20, design (enrichment PR #53 review)
- Status: open
- Threads: (design 2026-10-20, no PR thread)
- Effect: market cap and per-share figures could be on the pre-split count; verify on SF's next engine run before treating it as a defect.
- Fix sketch: on SF's next run, compare the latest diluted count with the dei cover count after the split; if pre-split, apply the split adjustment to shares_diluted_latest.

### EB-023 — dcf_engine.py:shares — IPO-year weighted-average share counts understate the year's share base (CRCL, CHYM, FIG)
- Opened: 2026-10-20, design (enrichment PR #53 review)
- Status: open
- Threads: (design 2026-10-20, no PR thread)
- Effect: the IPO year's weighted average spans pre-IPO months, so that year's OE/share is overstated beside the post-IPO count.
- Fix sketch: for the IPO fiscal year, use the period-end diluted count (or drop the year from per-share growth inputs) and flag it.

### EB-024 — dcf_engine.py:capex — `PaymentsForFlightEquipment` is a lessor's fleet at AER but would be the capex line at an airline
- Opened: 2026-10-20, design (09 capex, revision 3; 09b decisions)
- Status: needs-decision (Andrew)
- Threads: (design 2026-10-20, no PR thread)
- Effect: AER is DATA_GAP:capex today; its flight-equipment line is 5.7's only `CAPEX_UNLISTED_COMPONENT_OVERRIDDEN` hit. For a lessor the fleet is the business asset (arguably capex), so it needs a ruling together with the 5.8 sector-models question before AER can score.
- Fix sketch: rule the tag not capex, or read it as capex for non-lessors only (by SIC), then re-run AER.

### EB-025 — dcf_engine.py:iprd_detect — the acquired-IPR&D detector misses 10-Q-only acquired-IPR&D facts (SMMT)
- Opened: 2026-10-20, design (engine 5.6 IPR&D follow-up)
- Status: open
- Threads: (design 2026-10-20, no PR thread)
- Effect: SMMT's acquired IPR&D appears only in 10-Q facts, so its TTM base carries the charge with no ACQUIRED_IPRD_CHARGE flag or one-time adjustment.
- Fix sketch: scan the TTM window's 10-Q YTD facts for the IPR&D tags as the annual scan does.

### EB-026 — build_site.py — a refused re-score publishes a mixed record: the new run's numbers, forecast and hurdle prices beside the older score's tier and IRR
- Opened: 2026-10-20, HALO PR #47
- Status: fixed in PR #<this> (2026-10-21)
- Threads: https://github.com/Andrew199617/Stocks/pull/47#discussion_r4322859281 (HALO, P1)
- Effect: when make_score refuses any re-score, record.numbers, forecast and hurdle_prices come from the new dcf_numbers.json while tier / IRR come from the older score.json; only live figures were withheld (`score_not_from_this_run`). The older run's numbers cannot be shown instead: the engine overwrote its file.
- Fix sketch: lane default Q11 (a), 2026-10-21, pending Andrew's ratification: keep the page and label every panel "as scored <date>" or "latest run, not scored yet" (engine 5.7, lane L6); options (b) drop the name until it scores and (c) show only the scored figures stay open.

### EB-027 — dcf_engine.py:iprd_deferred_payment — two distinct deals first charged in the same period are refused as renamed copies, with no escape hatch
- Opened: 2026-10-20, HALO PR #47
- Status: open
- Threads: https://github.com/Andrew199617/Stocks/pull/47#discussion_r4323764895 (HALO, P1)
- Effect: two genuinely distinct acquired-IPR&D deals whose contingent caps are disclosed in the same filing stop the run (NEEDS_MAIN_AGENT); no folder hits it today.
- Fix sketch: a cited `distinct_from` declaration on the second deal, used only when a multi-deal filer (JAZZ, BMRN) hits it.

### EB-028 — queue.py:_pass2_load — a malformed second_pass_queue.json was silently repaired: `setdefault("entries", {})` then saved
- Opened: 2026-10-21, HALO PR #47
- Status: fixed in PR #<this> (2026-10-21)
- Threads: https://github.com/Andrew199617/Stocks/pull/47#discussion_r4333889298 (HALO, P1)
- Effect: a parseable file of another shape (`{}`, a list, `{"entries": null}`) crashed the command or was saved back with `entries` emptied, so other tickers' second-pass records could be erased (the registry analogue of PR #47 round 26).
- Fix sketch: refuse a malformed file and restore it from git (engine 5.7, lane L5: `_pass2_load` refuses unless `entries` is an object of objects; every pass-2 command and refresh's reset go through it).

### EB-029 — ttm.py --interim / dcf_engine.py:iprd_detect — the IPR&D detector reads no 6-K interim facts
- Opened: 2026-10-21, design (lane default Q8; 04 foreign, rebase amendment 11)
- Status: deferred (lane default Q8, 2026-10-21)
- Threads: (design 2026-10-21, no PR thread)
- Effect: a US-GAAP 20-F filer's acquired-IPR&D charge in the current interim is refused by `ttm.py --interim` ([IB-IPRD], NEEDS_MAIN_AGENT) instead of deducted, so that bridge cannot score.
- Fix sketch: extend iprd_detect to the 6-K instance's current-interim leg (read the 6-K's XBRL instance through xbrl_instance).

### EB-030 — make_score.py / dcf_engine.py — no amortized acquired-IPR&D base on the annual median after a TTM rejection
- Opened: 2026-10-21, design (lane default Q17; 11 R7 base alternatives, question 5)
- Status: deferred (lane default Q17, 2026-10-21)
- Threads: (design 2026-10-21, no PR thread)
- Effect: a recurrent IPR&D filer under STALE_FY can amortize only on the TTM; once its TTM is rejected (R7) the median carries the one-time deduction. No folder declares `iprd_amortized` today.
- Fix sketch: let the engine read an amortized declaration on the median (≈ 6 lines in the IPR&D block; presence added to iprd_judgment_inputs only when declared, so every existing hash holds).

### EB-031 — dcf_engine.py:CAPEX_COMPONENT_TAGS — RRC files its E&P capex as `PaymentsToAcquireOilAndGasPropertyAndEquipment`, on no list
- Opened: 2026-10-21, design (09 capex, R8 scope question 1)
- Status: deferred (lane default Q9, 2026-10-21)
- Threads: (design 2026-10-21, no PR thread)
- Effect: RRC's whole E&P capex line (FY2023-25 $571.8M / $570.4M / $581.5M) is unread; a capex_override of $628.58M fills FY2023-25 and every TTM leg (5.7 flags it `CAPEX_UNLISTED_COMPONENT_OVERRIDDEN`). Adding the tag: TTM capex $628.6M → $632.7M, base $2.9133 → $2.8958, weighted IRR 9.03% → 8.37%, Tier D either way.
- Fix sketch: append the tag to the components; the filed line then supersedes the override, which RRC's next run must remove.

### EB-032 — dcf_engine.py:capex sub-class rule — FCFS tags its 10-Q capex line as furniture and fixtures alone, so its YTD legs are set aside
- Opened: 2026-10-21, design (09 capex, R8 scope question 2)
- Status: deferred (lane default Q9, 2026-10-21)
- Threads: (design 2026-10-21, no PR thread)
- Effect: FCFS's 10-K files `PaymentsToAcquireProductiveAssets` ($54.9M FY2025) but every 10-Q files only `PaymentsToAcquireFurnitureAndFixtures` (H1-2025 $25.9M, H1-2026 $37.9M); the sub-class rule leaves the YTD legs to a prorated override, so TTM capex is $54.9M where the filings give $66.9M (base $13.5018 vs $13.2300, weighted IRR 13.01% vs 12.82%, Tier C either way).
- Fix sketch: "a sub-class alone is the leg in a 10-Q period whose fiscal year's 10-K files a roll-up" — not dropping furniture and fixtures from the sub-classes (EXR FY2013-21 would then read a $3.7-7.8M fixtures line as its whole capex).

### EB-033 — fundamentals.py:returns — debt tags it does not read understate invested capital (VRSN, AES)
- Opened: 2026-10-20, design (03b moat combined §17 (g))
- Status: open
- Threads: (design 2026-10-20, no PR thread)
- Effect: `DEBT_NOT_TAGGED` on 785 rows understates invested capital, so the ROIC proxy is overstated; AES's moat reverse-gate hit is an artefact of it; statements.py does read VRSN's debt (its proxy line is blank where fundamentals.json's reads −37.6%).
- Fix sketch: read the engine's debt candidates (dcf_engine debt_current / debt_lt / debt_total groups) in the returns function.

### EB-034 — filing_watch.py — a declared 6-K interim bridge is not re-queued when a newer 6-K interim arrives
- Opened: 2026-10-21, design (04 foreign, L4 review)
- Status: open
- Threads: (design 2026-10-21, no PR thread)
- Effect: QUARTERLY lists 10-Q / 10-Q/A only, so a name scored on a declared 6-K bridge (ttm.json `basis: declared_interim`) stays on the old interim until its next 20-F / 40-F.
- Fix sketch: compare a newer 6-K against the bridge's report filing date (ttm.json `report.filed`; a non-XBRL 6-K's reportDate is its cover date) or, for an XBRL 6-K, `report.period_end`; queue for a worker check, never re-bridge automatically (not every 6-K is an interim report).

### EB-035 — xbrl_instance.py:parse_undimensioned — keeps only undimensioned dei share counts
- Opened: 2026-10-21, design (04 foreign, L4 notes)
- Status: open
- Threads: (design 2026-10-21, no PR thread)
- Effect: a multi-class foreign filer whose FY comes from the filing instance gets the undimensioned cover count only (companyfacts keeps the per-class ones).
- Fix sketch: keep the class-dimensioned dei share counts and sum them the way companyfacts reads them.

### EB-036 — dcf_engine.py:capex — capex-like tags ruled not capex are never read: Buildings, EquipmentOnLease, Timberlands, Land and the real-estate tags
- Opened: 2026-10-21, design (09 capex §9)
- Status: needs-decision (Andrew)
- Threads: (design 2026-10-21, no PR thread)
- Effect: WTRG's whole capex line is mis-tagged as buildings (override in place); EquipmentOnLease carries lessor fleets / buy-outs at DOW, FTAI, DOCN; Timberlands at WY. Each would need a policy call to read.
- Fix sketch: one ruling per tag family, then a component list entry with a regression on the named filers.

### EB-037 — make_score.py / dcf_engine.py:superseded capex band — the override's declared value is compared with the filed leg in its filed unit
- Opened: 2026-10-21, design (09 capex §9)
- Status: open
- Threads: (design 2026-10-21, no PR thread)
- Effect: HTHT's capex override (USD) is compared with the RMB-filed PP&E leg, so the 0.5x-2x superseded band tests two currencies.
- Fix sketch: convert the filed leg to the override's currency at the period's rate before the band test.

### EB-038 — dcf_engine.py:capex — 21 scored filers report capitalized software only through `CapitalizedComputerSoftwareAdditions` (a note element)
- Opened: 2026-10-21, design (09 capex §9)
- Status: open
- Threads: (design 2026-10-21, no PR thread)
- Effect: the engine believes the amount is inside their PP&E line and does not add it (R9 adds only the cash-flow software tags); unverified per filer.
- Fix sketch: per filer, check the cash-flow statement for a separate software line; add it only where the PP&E line excludes it.

### EB-039 — dcf_engine.py:unlisted_capex_components — the unlisted-component check reads us-gaap annual legs only
- Opened: 2026-10-21, design (09 capex §9)
- Status: open
- Threads: (design 2026-10-21, no PR thread)
- Effect: IFRS partial roll-ups, extension-tagged lines and 10-Q legs are outside it (`CAPEX_COVERAGE_LOW` is the net there), and its CAPEX_LIKE vocabulary cannot see a class without one of its words (MiningAssets, FurnitureAndFixtures — both listed since 5.7).
- Fix sketch: run the same check over ifrs-full and 10-Q legs and match on the element's balance / cash-flow role rather than words.

### EB-040 — make_score.py:TTM_PY_EXIT3_RES — ttm.py's share-class refusal (`BAD_SHARE_CLASSES`, exit 3) has no exit-3 pattern, so a ttm_unavailable_reason quoting it is not checked
- Opened: 2026-10-21, design (11 R7 base alternatives, lane default Q14; R7 lane review)
- Status: open
- Threads: (design 2026-10-21, no PR thread)
- Effect: ttm.py's exit-3 problem texts are mirrored, each whole, in make_score.TTM_PY_EXIT3_RES (a ttm_unavailable_reason must quote ttm.py's line verbatim, [TTM-UNAV1]); L8's refusal in ttm.py (`BAD_SHARE_CLASSES for <T>: …`, e.g. an undeclared new YTD period) matches none, so such a folder's ttm_unavailable_reason is allowed beside an off-basis ttm.json but not quote-checked. No scored folder declares share classes today.
- Fix sketch: add a pattern for ttm.py's BAD_SHARE_CLASSES line to TTM_PY_EXIT3_RES and run that real exit-3 path in test_make_score_57_r7 beside the five it already runs.
