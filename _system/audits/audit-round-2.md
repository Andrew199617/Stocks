# Re-audit, round 2: Muse's v5 fixes

Oct 13, 2026 · @Andrew

## Verdict

P0 is real progress. The gate blocks exactly what it names, APP reconciles to the cent, and the queue lock and make\_score's cross-checks work. But the gate's perimeter is narrower than "incomplete data," and I got a tier past it eight ways.

- **Live risk today:** make\_score will build a fresh score.json from a v4, gate-less dcf\_numbers.json. 40 of 45 folders still hold v4 output mid-re-run. A run that calls make\_score before the engine republishes HIG's Tier B with SBC missing in all five years.
- **The gate doesn't cover operating cash flow.** If OCF is tagged under the continuing-operations tag, the engine emits a fake Tier F. If only the latest year is missing, it emits a tier from older years with no flag.
- **Overrides have no sanity bounds.** A capex override typed as 19 instead of 19,000,000 lifted a test company from B to A, and a negative one produced Tier S.
- **The TTM pin is a free number.** Any `--base-oe-ps` is accepted, and ttm.py's output isn't saved, so the score's base can drift from its recorded override.
- **Today's ranking mixes engines.** 40 of 43 rows are v4 output, unmarked, and HIG, PCG and PRU still sit in Tier B.

Method: I ran Muse's unmodified dcf\_engine.py and make\_score.py against synthetic filings, with only the paths and network calls stubbed. I also recomputed APP from its folder and read every changed file.

Muse's newer bundle, sent mid-review, fixes the override-impact basis. I re-ran both test harnesses on it, and every other finding below still reproduces.

## Ask 1: making the gate emit a tier

The gate held on every field it names. It failed on fields it doesn't name, on unvalidated inputs, and on the path around the engine.

| Attempt | Result | Verdict |
| --- | --- | --- |
| SBC missing in the latest FY | Exit 4, no tier | Holds |
| TTM pin plus an SBC gap | Exit 4, no tier | Holds |
| No price from any source | Exit 3, no tier | Holds |
| OCF filed under the continuing-operations tag | Tier F, exit 0 | Fake tier |
| OCF missing in the latest FY only | Tier B from older years (base $1.77 vs $1.95), no flag | Silent |
| Capex override entered as 19, not 19,000,000 | Tier A (true answer B) | Fake tier |
| Negative capex override | Tier S | Fake tier |
| Arbitrary `--base-oe-ps 9.99` on complete data | Tier S | Unvalidated pin |
| Manual `--price 1.00` with no real price | Tier D with a blank IRR | Fake tier and a bug |
| USD-reporting 20-F filer (an ADR) | Tier emitted, ADS ratio never checked | Still open |
| Diluted shares missing, basic shares present | Tier emitted on basic shares, no flag | Silent swap |
| make\_score on HIG's v4 folder | Writes a fresh Tier B score.json | Bypass, live now |
| make\_score on a hand-edited dcf\_numbers.json | Accepts Tier S, 31% IRR | No provenance |
| One stray EUR fact from 2016 | Whole company blocked | False positive |

The manual-price row exposes an old bug. When the value at a 200% discount rate still exceeds the price, the IRR returns blank and the tier falls to D. The cheapest stocks would be ranked as the worst.

## Ask 2: override integrity and the registry

Yes, a score can disagree with its recorded override, through the TTM base. The annual history is locked down; the base the score actually uses is not.

- **Annual history: holds.** make\_score refuses when judgment.json and dcf\_numbers.json disagree on an override's value or kind, and when an applied override has no declaration.
- **TTM base: doesn't hold.** Change APP's capex override to $50M, re-run the engine with the old `--base-oe-ps 12.508` pin, and make\_score accepts it. The score then records $50M while its base reflects $19M. Nothing links the pin to ttm.py, and ttm.py's output isn't saved in the folder.
- **Registry coverage today: complete.** APP is the only folder with an override, and it's the only entry.
- **Registry over time: goes stale.** When I removed APP's override and re-scored, the $19M entry stayed. The upsert only replaces fields that are still applied.
- **Judgment calls the registry never sees:** tier overrides, manual prices, base pins, `--gterm` and `--cik`. A D-to-S tier override with the reason "x" was accepted and left no trace, and the ranking doesn't badge it.
- **Impact basis: fixed in Muse's latest bundle.** The registry now records APP on the TTM base it actually uses: $12.56 → $12.51 (−0.45%), weighted IRR −0.05pp, unblocks tier yes. make\_score now runs ttm.py itself, so checking the pin against ttm.py's output is a few lines away.

## Ask 3: APP from its folder alone

APP reconciles exactly, filing figures through headline. One gap: the TTM inputs live only in analysis.md prose, not in a machine-readable file, so a script can't re-derive the base.

| Figure | Folder says | I recomputed | Match |
| --- | --- | --- | --- |
| TTM OCF (FY − prior YTD + current YTD) | $4,527,589,000 | $4,527,589,000 | Yes |
| TTM SBC | $282,376,000 | $282,376,000 | Yes |
| TTM capex (override, prorated) | $18,947,945 | $18,947,945 | Yes |
| TTM OE per share (÷ 337,875,000) | $12.5084 | $12.5084 | Yes |
| Weighted IV @15% / @12% | $376.13 / $535.47 | $376.13 / $535.47 | Yes |
| Weighted IRR | 18.43% | 18.43% | Yes |
| Scenario IRRs | 9.15 / 12.93 / 17.47 / 22.70 / 28.58% | Same | Yes |
| Upside @15% | 38.1% | 38.1% | Yes |

- **The zero-fill TTM base is $12.56, not $12.57.** The $12.57 is v4's hand figure, a cent high. The −0.45% effect is correct against $12.56.
- **The two tools disagree slightly on the same override.** ttm.py counts the FY leg as 364 days (end minus start), so its TTM capex is $18.95M, while the engine fills FY2025 with $19.00M. That's immaterial, but it should be inclusive and match.
- **One quoted number carries the wrong meaning.** analysis.md says the price is "38.1% below" the weighted IV. 38.1% is the upside; the price is 27.6% below IV. The quote-verbatim rule stops arithmetic slips, not misreadings.

## Ask 4: new failure modes

Most new issues sit at the seams between the scripts, not inside them.

| Failure | Evidence | Fix |
| --- | --- | --- |
| Ranking mixes engines | 40 of 43 rows are v4 output with no label; HIG, PCG and PRU still show Tier B | Label rows "pre-v5, re-run pending" or hide them until re-scored |
| Pass-2 badges describe v4 | CMPS, SNAP, DUOL, TTWO and STZ show "Pass 2 checked, no change" from reviews of v4 numbers, and the badge will carry onto their v5 rows | Reset pass-2 status for every re-run name |
| Reaper never runs | No job calls `queue.py reap`, so a crashed claim stays in progress forever | Reap inside `claim`, under the same lock |
| Shell mangles block reasons | TKO's note lost the digits after each dollar sign (93.753M became .753M); the worker appended a correction | Pass reasons through stdin or a file, never a quoted shell argument |
| One status for two problems | DATA\_GAP names (TKO, CMPS) are stored as blocked\_no\_data, so there's no clean list awaiting override decisions | A separate blocked\_data\_gap status that names the fields |
| TKO plan may not work | As far as I know, companyfacts carries only standard taxonomies; custom tags like `tko:` live in each filing's own XBRL | Test on TKO before building namespace scanning |
| Hand math in notes | TKO's queue note computes corrected OE and per-share figures by hand | The no-hand-math rule covers notes too |
| ttm.py zero-fills where the engine blocks | No capex facts at all returns capex 0 with a warning and exit 0; override legs match exact period dates, so a filed fact with a shifted start date gets replaced | Block unless an override exists; match legs within a few days |
| make\_score trusts judgment for rule fields | `in_scope_under_40b: true` at a 93B market cap and `confidence: high` with WIDE\_SCENARIO\_SPREAD were both accepted | Compute scope from market cap; cap confidence at medium when the rule says so |
| key\_numbers.md drops lines | A misplaced conditional drops OE yield and TV share whenever scenario spread is blank, and the shares reason prints twice | Fix the two lines |

## Next steps

Do the first two today: the re-run is live, and both affect what it publishes. The rest close the gaps the harness found.

| Priority | Change |
| --- | --- |
| Now | make\_score refuses any dcf\_numbers.json below engine v5 or without a data\_gap field |
| Now | Label or hide pre-v5 rows in the ranking; reset pass-2 status for every re-run name |
| P0 | Gate operating cash flow, with the continuing-operations tag as a fallback |
| P0 | Override checks: refuse only impossible values (negative). Anything far from the company's own filed history (under 0.1× or over 10× the last filed figure, or no filed figure at all) needs an explicit acknowledgment field and gets flagged |
| P0 | Save ttm.py output as ttm.json in the folder; the engine reads it via `--ttm`; make\_score refuses a base that differs from it; any other pin needs a `base_override` judgment field |
| P1 | 20-F and 40-F filers need an `ads_ratio` judgment field or block; check currency on the last 3 FY only |
| P1 | Registry replaces a ticker's entries on every score, and also records tier overrides, manual prices, base pins, `--gterm` and `--cik`; the ranking badges tier overrides |
| P1 | make\_score computes scope from market cap and enforces the confidence cap |
| P1 | queue.py reaps inside claim, takes reasons on stdin, uses a blocked\_data\_gap status, and adds `requeue` |
| P1 | ttm.py blocks on missing capex unless overridden; inclusive day counts; legs match within a few days |
| P1 | Fix the IRR-above-200% bug; flag basic-share fallback; make\_score verifies a content hash the engine writes |
| P2 | Prove TKO's extension tags are reachable before building namespace scanning |
| P2 | Fix the two key\_numbers.md lines and APP's margin-of-safety sentence |

Brief to hand Muse:

```
Re-audit round 2 results. Do items 1-2 now, before the v5 re-run continues.
1. make_score.py: refuse when dcf_numbers.json has engine_version < 5 or no
   data_gap field. (Today it rebuilds HIG's v4 Tier B, SBC missing all 5 FY.)
2. build_daily_html.py: label or hide rows whose dcf_numbers.json is pre-v5.
   Reset second_pass_queue entries for every v5_rerun name.
3. Engine gate: treat missing operating cash flow (any of the last 3 FY) as
   DATA_GAP:ocf; add NetCashProvidedByUsedInOperatingActivitiesContinuingOperations
   as a fallback tag. (Today it emits a fake Tier F.)
4. Override checks in engine and make_score: refuse only impossible values
   (negative). Outside 0.1x-10x of the last filed value needs an ack reason.
   (Today an override typed as 19 lifts a company B to A; a negative one gives S.)
5. TTM pin: ttm.py writes ttm.json into the company folder; the engine takes
   --ttm and reads it; make_score refuses if base_oe_per_share differs from
   ttm.json by > 0.1%. Any other --base-oe-ps needs a base_override field in
   judgment.json with value/source/reason, and goes in the registry.
Then P1 from the round-2 tab of the audit doc, and a fresh bundle for re-test.
```
