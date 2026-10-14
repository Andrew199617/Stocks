# Audit: Muse's DCF sweep automations

Oct 13, 2026 · @Andrew

## Summary

Muse's sweep runs on schedule, but its outputs aren't reliable enough to act on yet. The top of today's ranking is model artifacts, and most fixes move mechanical steps out of the agent and into code.

- **Where it stands:** 47 companies attempted in about 28 hours. 38 scored, 9 blocked (7 IFRS filers, 2 recent IPOs), 1 in progress. Nothing reached Tier S or A.
- **The hurdle-clearers are misfits.** All four in-scope Tier B names are two insurers (HIG, PRU), a wildfire utility valued on non-GAAP core EPS (PCG) and a Chinese ADR scaled by hand (JD). All four are low confidence.
- **Missing data silently becomes zero.** SBC is absent for 9 of 40 companies and capex is assumed $0 in recent years for 8. The engine raises no flag for either.
- **Hand arithmetic slips.** DFTX's TTM net income has a sign error (−$486M instead of −$354M). ED's June net debt is overstated by $2.0B.

| # | Fix | What it stops | Effort |
| --- | --- | --- | --- |
| 1 | Engine refuses to emit a tier when SBC, capex, shares, currency or price is missing | Fake tiers from data gaps (ED, HIG, IBKR, ROP) | \~1 day |
| 2 | Compute TTM owner's earnings in code from 10-Q facts | Arithmetic errors like DFTX and ED | \~1 day |
| 3 | Generate score.json by script from engine output plus a small judgment file | Drift between files (JD at 2×, YUM's missing debt flag) | \~½ day |
| 4 | Pull banks, insurers, REITs and utilities out of the main ranking | Misfits topping the list | \~2 hours |
| 5 | Replace the hand-edited queue.json with a locked, leased claim script | Double-picks and stuck "in\_progress" entries | \~½ day |
| 6 | Watch for new 10-Q/10-K filings daily and re-queue | Stale scores after earnings season | \~½ day |

## Automation and process reliability

The job shape is right: claim, compute, research, write, rebuild. The failures come from routing every mechanical step through the agent, including the lock, the arithmetic and the JSON.

| Issue | Evidence | Fix |
| --- | --- | --- |
| Queue lock is an agent rewriting a 204 KB JSON | Two workers read-modify-write queue.json 7 minutes apart. No file lock, atomic write or lease. A crashed run stays "in\_progress" forever (CBOE has no score.json at export). | `queue.py claim / done / block / reap` with an fcntl lock, atomic rename and a 90-minute lease the reaper resets |
| Runs can overlap themselves | Timeout is 60 minutes on a 15-minute interval, so a slow pass can stack up to four live copies. | Skip a firing while the previous run is live, or cap the timeout at 14 minutes |
| Throughput is a quarter of plan | 47 attempts in \~28 hours (\~1.7/hour) vs the 8/hour two 15-minute jobs imply. README says 30 minutes, GOAL.md says hourly. | Log start/end on each queue entry and set cadence from measured run time |
| Wasted runs on unscorable filers | 9 of 47 attempts ended blocked\_no\_data, each after a web CIK hunt (7 IFRS-only, 2 IPOs with no 10-K). | One script checks companyfacts for us-gaap history across all 2,617 and pre-blocks them (\~5 minutes at SEC's rate limit) |
| Heavy context every run | Each run re-reads README, DCF\_AUDIT and the APP example; that repeats across \~5,200 planned runs. | A ≤3 KB WORKER\_SPEC.md for agents; keep the long docs for humans |
| Clock skew | The VM runs on UTC. 12 companies have engine dates one day ahead of score dates, and ranking-2026-10-14.html was written on Oct 13 ET. | Set TZ=America/New\_York for every job |
| Fragile network calls | SEC User-Agent is a placeholder (andrew@example.com). No retry or backoff on EDGAR or Nasdaq calls. | Real contact email; retry on 429/5xx with backoff |
| Daily HTML won't scale | 294 KB for 39 companies (\~7.5 KB each) projects to \~19 MB at 2,617, too big to attach or open on a phone. | Ranked list plus top-N detail pages, or JSON rendered on demand |
| Alerts will fire on artifacts | S/A alerts are most likely from misfits (insurer float, missing SBC), which is how HIG and IBKR first showed up. | Alert only at medium+ confidence with no data-gap flags |

On the two-workers question: throughput isn't the constraint, correctness is. At today's 1.7/hour the sweep still finishes in about 9 weeks. Hold at one worker per pass until the code fixes land, because every name scored now will need a re-run.

## Engine correctness

The engine's worst failures are silent: a missing tag becomes zero and the flag system never hears about it. Should the engine refuse to emit a tier when diagnostics trip? Yes for data-integrity gaps, no for judgment flags like scenario spread, which should cap confidence instead.

| Silent failure | In the code | Seen in | Fix |
| --- | --- | --- | --- |
| Missing capex becomes $0 | `capex_assumed_zero` is written to the CSV but never added to `fragility_flags`, despite the docstring | All last 5 FY: ARES, DFTX, IBKR, PRU, ROP. FY23–25: ED. FY25: APP, CMPS | Add construction-in-process and capitalized-software tags; emit CAPEX\_MISSING and withhold the tier |
| Missing SBC is dropped from OE | `oe_cons = fcf − sbc` only when SBC exists; one tag tried (`ShareBasedCompensation`) | ARES, DFTX, ED, EME, HIG, PCG, PEG, PRU, UAL | Add `AllocatedShareBasedCompensationExpense`; emit SBC\_MISSING and withhold the tier |
| Tier F skips every diagnostic | Flags are computed only inside the positive-OE branch | All 7 F names (AXON, CMPS, DFTX, FIG, IRM, SNAP, TTWO) show `[]` | Compute flags before branching |
| A price failure becomes Tier F | The F branch also catches `price is None`; a manual `--price` is labelled `nasdaq_quote_api` | JD's hand-set price is mislabelled | Exit like NO\_DATA; record the real price source |
| Currency and ADR ratios ignored | Takes the USD unit if present, else the first unit; no ADS ratio | JD needed hand-scaling (score.json is exactly 2× the engine) | ADR ratio table plus a currency check; no tier for non-USD without conversion |
| Share counts mix definitions | Diluted, basic and outstanding merge per year. The dei fallback is keyed by cover-page date, so it rarely matches a period end | STZ has no share count in any year | Record share source per year; match dei within 90 days; flag mixed sources |
| Tag provenance is hidden | `used_tags` names only the first tag that contributed, not the one used per year | ROP shows a capex tag while its last 5 years are assumed zero | Record the tag per period in the CSV |
| Debt is undercounted or double-counted | Misses notes payable, term loans and leases; `LongTermDebt` (which includes the current portion) can stack on `DebtCurrent` | YUM reads as net cash (agent found \~$11.6B net debt); SYY and EL debt blank, so no HIGH\_NET\_DEBT | Broaden debt tags; no leverage verdict when debt tags are blank |
| Sector check covers Finance only | Matches the screener sector "Finance" | REIT (IRM) and utilities (ED, PCG, PEG) unflagged | Flag Real Estate and Utilities too |

Smaller issues:

- IRRs near terminal growth are unstable because the terminal denominator floors at 0.5%. Report anything under 3.5% as "<3.5%" instead of ranking on it.
- `oe_ps_cagr_3y` is a 2-year CAGR, and the reviewers found agents repeating the mislabel.
- If value at a 200% discount rate still exceeds price, the IRR returns None and the tier falls to D. Rare, but wrong.

## Output integrity

Of 39 scored write-ups, reviewers rated 18 solid (4/5), 19 adequate (3/5) and 2 weak (APP, PCG). The recurring faults are hand arithmetic, gaps treated as zero, and fixes that never reach score.json. Method: a script cross-checked every score.json against dcf\_numbers.json, and five reviewers read every analysis.md. I re-checked the DFTX and ED errors myself.

| Tier | Count | Names |
| --- | --- | --- |
| S / A | 0 | — |
| B | 4 | HIG, JD, PCG, PRU (all low confidence) |
| C | 7 | ARES, CCL, DHI, RDDT, ROP, STZ, UAL |
| D | 20 | ADM, CBRE, CMG, DUOL, ED, EL, EME, IBKR, KR, ODFL, PAYX, PEG, RBLX, STLD, SYY, U, UI, WCN, YUM, ZS |
| F | 7 | AXON, CMPS, DFTX, FIG, IRM, SNAP, TTWO |
| Blocked | 9 | LFTO, CBRS, CCJ, VIK, FER, VOD, SHG, CHT, EC |

- **Every hurdle-clearer is a misfit.** HIG's final engine run used the default moat and probabilities. PCG's base is non-GAAP core EPS, which excludes recurring wildfire charges, while its conservative OE is negative every year.
- **Hand arithmetic is wrong in places.** DFTX added the prior-year YTD loss instead of subtracting it (TTM net income −$486.0M, should be −$353.8M). ED's June net debt is $28,344M; the inputs sum to $26,344M. AXON's "SBC 2.4× FCF" is 4.8×.
- **Agents repeat the engine's zero-fill.** PCG and PEG call SBC "nil — utility comp is cash" with no source. IBKR uses D&A as a stand-in for capex. ROP spots \~$60–90M a year of missing capex but leaves the base uncorrected.
- **The base definition drifts.** ADM and CBRE computed TTM, then used the 3-year median. ED, HIG, PCG and PEG swapped owner's earnings for adjusted EPS, which breaks comparability.
- **The APP-incident rule is skipped where it applies.** Bull starts sit below the latest print with no written reason: PCG 11% vs H1 core EPS +29.7%, IBKR 24% vs Q2 +35%, plus PAYX, PEG and ODFL. Checks compare against guidance instead.
- **Manual fixes don't reach score.json.** JD's price, IV and base are 2× the engine's. YUM's analysis finds \~$11.6B net debt, but score.json has no HIGH\_NET\_DEBT. CMG ($40.8B), KR ($41.0B) and YUM ($41.2B) are marked in scope over $40B.
- **Sourcing is thin.** Guidance, consensus and peer figures are mostly uncited, and pass 2 leans on aggregators.
- **What works:** most TTM builds re-add cleanly (DHI, DUOL, CMG, CCL, KR, STLD), moat sections are specific everywhere, and ED, YUM, EL and SYY caught engine debt errors on their own.

The −1% Unity upside in your earlier screenshot is already fixed: this bundle's pass-2 mock shows −65%.

## Model design

The five-scenario, probability-weighted structure is sound. The weakness is reporting one point estimate when defensible method choices move a name a full tier, as APP did (C to A in one day).

- **Rank on a band, not a point.** Report the weighted IRR with a low–high range from the scenario IRRs and the method range, and tier on the low end. Ten of 31 in-scope names with an IRR sit within 1pp of the 10% line (ADM, DHI, DUOL, EME, IBKR, PAYX, PEG, STZ, UAL, UI); UAL flips C to D depending on how "weighted IRR" is averaged.
- **Define "weighted IRR" on the page.** It is the IRR of the expected cash-flow path, which runs above the average of scenario IRRs (APP 18.6% vs 17.8%). That's defensible, but reviewers couldn't reproduce it, and neither will you.
- **Model margins, not just revenue.** Growth is a revenue blend applied to owner's earnings, so guided margin changes vanish (EL: sales +4% but operating income \~+20%). Give each scenario a margin path from today's OE margin to a target, replacing the flat OE multipliers.
- **Stop double-counting dilution.** The share-count adjustment is applied on top of a blend that already includes OE-per-share growth, and on top of subtracting SBC. Apply it to the revenue components only.
- **Make the moat discriminate.** All 39 moat scores fall between 3 and 7, so the CAP only spans \~6–11 years. Anchor the score to measured inputs (ROIC history, gross-margin stability from the forensic battery) and let judgment adjust by ±2.
- **Keep the flat 15% discount.** Ranking on IRR makes the discount rate irrelevant to order; IV@15% is presentation. Risk belongs in the scenarios, as you have it.
- **Treat sector misfits as unmodeled, not soft.** Pull Finance, Real Estate and Utilities into a separate "not modeled" list now (\~2 hours). Build insurer, utility or REIT models later only if those sectors matter to you (\~1 day each).
- **Split Tier F.** "SBC exceeds cash generation" (AXON) and "no cash generation" (CMPS) are different stories; label them separately.

## Pass 2 design and governance

Pass 2 checks the right things, but it runs minutes behind pass 1 with the same model and sources. Its freshness check can't fire there, and its independence is thin.

- **Only two runs so far, both "no change" (U, RDDT).** U's pass 2 misdescribed the growth starts (they are the engine blend plus hand offsets), ran no sensitivity, and never tested the moat or probabilities. RDDT's conceded the −5pp dilution penalty is too harsh but didn't quantify it.
- **Freshness is in the wrong place.** forensic\_pull.py only looks for filings after pass 1's analysis date, which is usually the same day. Staleness bites weeks later, once Q3 reports land from late October. Move it to a daily watcher over all done names that re-queues pass 1 with a code-computed TTM.
- **Battery bugs.** The STALE\_PASS1 flag is appended after the flag list prints, so it never appears there. `pick()` takes the first tag only, the truncation bug v4 fixed in the engine. Routine 8-K items 2.02 and 7.01 are counted as material.
- **Define "material" before allowing rewrites.** Allow a score change only when the weighted IRR moves ≥2pp or the tier changes, and the driver is a filing-sourced number. The rerun must be reproducible from a saved inputs file.
- **Make it adversarial.** Ask pass 2 to argue the tier next door with one numeric test, or run it on a different model than pass 1. A same-model re-read mostly confirms itself.
- **On the proposed additions:** a guidance-vs-model check (scenario year-1 growth vs company guidance) is cheap and high value, so add it. Debt maturities vs free cash flow is medium value. Insider and buyback signals add little to a valuation screen; skip them.

## Validation

Nothing has been validated yet. A point-in-time backtest of the mechanical engine is feasible from the same EDGAR data in about two days, as long as the agent stays out of it.

1. **Replay the engine at past dates.** EDGAR companyfacts records a `filed` date on every fact, so the engine can be run using only facts filed before a cutoff. Use mid-year cutoffs from 2019 to 2023 and a sample of \~300 universe names.
2. **Use mechanical inputs only.** Default moat and probabilities, no agent. An LLM knows what happened after 2019, so any judgment step leaks the future.
3. **Score it.** Measure the rank correlation between weighted IRR and 3-year forward total return, the top-vs-bottom quintile spread, and whether Tier B+ beat an equal-weight index.
4. **Name the biases.** Today's top-3,000 list is survivor-biased, and historical prices need a source other than Stooq. Accept and document both, or use dated constituent lists.
5. **Measure judgment noise now.** Re-run 10 finished names with three fresh agents each and count tier disagreements. If agents disagree on a tier more often than the engine's flags say they should, the judgment layer is adding noise, not signal.
6. **Track forward from today.** A daily job appends each scored name's price to a CSV. After 6–12 months, compare realized returns against predicted IRR by tier.

If the mechanical engine shows no rank signal in the replay, fix the model before spending more agent hours on the sweep.

## Action plan

Do the P0 items before scoring more names. Everything already scored gets one re-run once v5 lands, and each company's judgment inputs carry over.

| Priority | Change | Effort |
| --- | --- | --- |
| P0 | Pause both pass-2 jobs and run pass 1 on one worker | Minutes |
| P0 | Engine v5 data gate: SBC, capex, shares, currency, ADR ratio and price checks; DATA\_GAP flags; no tier when one fires; flags computed before the F branch | \~1 day |
| P0 | `ttm.py`: TTM OCF, capex, SBC and shares from 10-Q YTD facts, fed straight to the engine | \~1 day |
| P0 | `make_score.py`: score.json built from dcf\_numbers.json plus a judgment.json (moat, probabilities, offsets, one-liner, tier override and reason, confidence) | \~½ day |
| P0 | `queue.py` with lock, lease and reaper | \~½ day |
| P1 | Pre-block IFRS and no-10-K filers across the universe | \~1 hour |
| P1 | Separate "not modeled" list for Finance, Real Estate and Utilities | \~2 hours |
| P1 | Timezone, SEC contact email, retries | \~1 hour |
| P1 | Re-run the 38 done names under v5, reusing each judgment.json | \~1 day of runs |
| P1 | Daily filing watcher that re-queues on a new 10-Q or 10-K | \~½ day |
| P2 | IRR band in the engine and HTML; tier on the low end | \~½ day |
| P2 | Point-in-time backtest of the mechanical engine | \~2 days |
| P2 | Pass-2 materiality rule and adversarial framing | \~2 hours |
| P2 | Slim the daily HTML to a list plus top-N detail pages | \~2 hours |

Brief to hand Muse for the P0 work:

```
Pause dcf-second-pass and dcf-second-pass-parallel. Disable dcf-sweep-parallel.
Build engine v5 before scoring more companies:
1. Data gate: if SBC, capex, diluted shares or a USD price is missing for any of the
   last 3 FY, or the filer reports in a non-USD currency or trades as an ADR, emit
   DATA_GAP:<field> and do not emit a tier. Try AllocatedShareBasedCompensationExpense,
   construction-in-process and capitalized-software tags first. Compute fragility
   flags before the Tier F branch.
2. ttm.py: compute TTM OCF, capex, SBC and shares from 10-Q YTD facts in code.
   Agents never do TTM arithmetic by hand again.
3. make_score.py: build score.json from dcf_numbers.json plus judgment.json.
   Agents write judgment.json and analysis.md only.
4. queue.py claim/done/block/reap with an fcntl lock, atomic writes and a
   90-minute lease.
5. Set TZ=America/New_York and a real SEC User-Agent email.
Then re-run the 38 done companies under v5 and report which tiers changed.
```
