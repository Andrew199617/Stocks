# JLL — Jones Lang LaSalle Incorporated

**Superseded 2026-10-19: scored Tier D (weighted IRR 7.52%, base $9.81/sh) on engine 5.5 — see "## Engine 5.5 re-score (2026-10-19)" below; the 2026-10-17 status that follows is kept as the dated record.**

**STATUS: BLOCKED — NEEDS_MAIN_AGENT: sbc. No score.json is emitted and no tier ships.**
The DCF work below is finished and saved so a re-run after the engine decision is fast.
judgment.json (moat, probs, filing capex override) carries over unchanged.

## What it is

Global #2 commercial real estate services franchise (NYSE: JLL, SIC 6531 Real Estate
Agents & Managers; Nasdaq screener sector "Finance", industry "Real Estate").
Leasing advisory, capital markets, property/facilities and workplace management
(Real Estate Management Services), project management, and LaSalle Investment
Management, across ~80 countries, ~113,000 employees. Revenue is gross and includes
large pass-through reimbursables: FY2025 revenue $26,115.6M, operating income
$1,098.0M (~4-5% operating margin), net income $792.1M (all financials_history.csv).
Market cap at the run price: $305.51 × 48,312,000 diluted shares = $14,759.8M
(dcf_numbers.json market_cap_est) — in scope under $40B.

## The blocker: the engine's SBC leg counts the wrong slice

- The engine's SBC series uses the us-gaap `ShareBasedCompensation` tag. For JLL that
  tag is NOT total stock compensation: in the FY2025 10-K it is the $2.7M
  "stock-based compensation expense for post-acquisition retention awards" line inside
  the Restructuring and acquisition charges note (FY2024: $2.3M; FY2023: $3.4M — the
  exact values in financials_history.csv's sbc column).
- The filer's total stock-comp cost is two orders larger: cash-flow statement
  "Amortization of stock-based compensation" $114.7M (FY2025), $97.4M (FY2024),
  $78.3M (FY2023), and `AllocatedShareBasedCompensationExpense` $112.0M / $95.1M /
  $74.9M for the same years (EDGAR companyfacts). The engine only falls back to the
  Allocated tag when ShareBasedCompensation is absent, so the small slice wins.
- Materiality, from filing figures: the ~$109M/yr gap is ~13% of a corrected median
  base. Rebuilding the median from the filing's own year-specific capex and allocated
  SBC — FY2023 (575.8 − 186.9 − 74.9) / 48.288M, FY2024 (785.3 − 185.5 − 95.1) /
  48.372M, FY2025 (1,194.1 − 215.6 − 112.0) / 48.312M — gives a median of ~$10.43/sh
  vs the engine's $11.73/sh even after the capex override. ttm.py has the same defect
  (its TTM SBC leg is $1.5M).
- Why the worker cannot cure it in bounds: an override only fills a period where no
  value is filed ("an override never replaces a filed value"), and a base_override
  may only be built from figures this run's outputs printed — the correct SBC total
  appears in no run output. This is the DD pattern (filed-but-wrong basis, override
  cannot reach it), not a DATA_GAP the bounded authority covers. Escalated as
  NEEDS_MAIN_AGENT: sbc — the fix is an engine tag-priority decision (e.g. prefer /
  reconcile AllocatedShareBasedCompensationExpense when ShareBasedCompensation is a
  restructuring-note slice), which is Andrew's call.
- Direction is not in doubt: even on the SBC-flattered engine base the name is Tier D
  by numbers (below). The correction lowers the base, IV and IRR further. What would
  ship without the fix is a materially overstated base/IV — exactly what the data
  gate exists to prevent.

## Owner's earnings

Both definitions, engine run WITH the filing capex override applied (dcf_numbers.json):

- Conservative (OCF − capex − SBC, engine SBC): base = median of last 3 FY OE/share
  = **$11.7299/sh** (base_source: median_of_last_3_fy_oe_per_share); latest FY2025
  = $20.1979/sh. Zero-fill counterfactual (override_impact): base $16.1871/sh,
  weighted IRR 10.53% → with the capex override base $11.7299/sh, weighted IRR 8.44%.
- FY2025 legs (financials_history.csv, capex as overridden): OCF $1,194.1M, capex
  $215.6M, SBC $2.7M (engine slice — see blocker), diluted shares 48,312,000.
- TTM (ttm.json): TTM OCF $1,362.0M (FY2025 $1,194.1M − H1 2025 −$434.8M + H1 2026
  −$266.9M); ttm.py OE $24.1703/sh is NOT used as a pin — its SBC leg carries the
  same $1.5M defect and its capex YTD legs are the prorated override ($215.6M flat),
  whereas the 10-Qs file actual net capital additions of $88.9M (H1 2025) and
  $115.0M (H1 2026). The median base is the defensible base for this cyclical name.

## MOAT — 5/10 (CAP 8.5 years)

Evidence first: roic_proxy (fundamentals.json) 12.5% (2021), 9.6% (2022), 7.0%
(2023), 9.3% (2024), 11.4% (2025) — around the cost of capital through the cycle,
no wide-moat signature. Gross margin is not filed (services P&L, no COGS tag);
operating margin is ~4-5% of gross revenue. CBRE, the #1 franchise, scored 6/10 in
this sweep; JLL sits one notch below.

FOR: scale global platform (#2, integrated leasing + capital markets + management
across ~80 countries); recurring contractual management-services base (company
materials cite ~99% top-client retention and ~80% resilient revenue, Q2 2026);
LaSalle investment-management AUM fees; client embed (95% of top-100 investors,
~50% of Fortune 500 are clients); data/tech platform raising cross-sell.
AGAINST: people business — producers can walk, no lock-in on the brokerage fee
pool; ROIC only ~cost of capital; transaction revenue un-moated (OE/share $18.33
in 2021 → $3.93 in 2022 in the pre-correction engine history); thin margins and
hard-negotiating institutional clients.

## Five scenarios (diagnostic run, engine SBC — all figures dcf_numbers.json)

Probs 15/30/30/15/10 (bear weight widened from the 10/25/30/25/10 default for
OE volatility and cyclicality). Growth starts vs engine blend 11.17%:

| Scenario | Prob | g_start | OE mult | IRR | IV@15% |
|---|---|---|---|---|---|
| Super bear | 15% | −0.83% | 0.75 | 4.97% | $62.79 |
| Bear | 30% | 6.17% | 0.90 | 6.75% | $100.84 |
| Base | 30% | 11.17% | 1.00 | 8.44% | $137.70 |
| Bull | 15% | 16.17% | 1.10 | 10.50% | $185.78 |
| Super bull | 10% | 23.17% | 1.25 | 14.11% | $279.88 |

Weighted: **IRR 8.44%, IV@15% $136.84 vs price $305.51** (upside_at_15 −55.2%).
Tier by numbers D (bear D, bull C). Hurdle prices: 15% → $136.84, 20% → $94.36,
25% → $71.30. Diagnostics: OE yield 3.84%, net debt $290.8M = 0.51× normalized OE,
lease liabilities $941.1M, TV share at 15% 20.2%.

Growth-start sanity check: base start 11.17% matches the actual prints — FY2025
revenue +11.4% YoY (growth_components rev_yoy_latest), TTM revenue +11.2% YoY
(fundamentals.json), Q2 2026 revenue +11% YoY with adjusted EPS +59-61% and
full-year adjusted EPS guidance raised to +34% at the midpoint (Q2 2026 reports).
Bull 16.17% sits above revenue prints on operating leverage in a transaction
recovery — written reason, not a cap artifact. The oe_ps_cagr_2y component
(65.28%) is an inflection artifact off the depressed FY2023 OE base and does not
drive the blend (median of revenue components).

## FLAGS — every flag on the final run resolved

- DATA_GAP:capex (preliminary run) — RESOLVED in bounds: filing capex_override
  $215,600,000 (kind "filing") from the FY2025 10-K Consolidated Statements of Cash
  Flows, "Net capital additions – property and equipment" $(215.6)M FY2025 /
  $(185.5)M FY2024 / $(186.9)M FY2023. JLL files no standard capex tag after FY2019.
  Override impact measured by the engine: base $16.1871 → $11.7299/sh, weighted
  IRR 10.53% → 8.44%.
- STALE_FY — latest FY ended 2025-12-31, ~10 months before the run. TTM checked
  (above): TTM OCF $1,362.0M and TTM revenue +11.2% YoY confirm the recovery is
  real, but the TTM pin is not used (SBC leg defect + prorated capex legs).
- OE_VOLATILE (preliminary run) — confirmed cyclical: OE/share spanned $3.93
  (2022) to $24.66 (2025) on the zero-fill history, and 4/5 positive years on the
  corrected run (2022 goes negative once real capex is charged). Handled via the
  median base and bear-heavy probs (15/30/30/15/10).
- NI_OCF_DIVERGENCE (2023) — net income $225.4M vs OCF $575.8M: FY2023 net income
  was depressed by $194.1M of equity losses (non-cash investment writedowns, added
  back in the OCF reconciliation) and $100.7M of restructuring and acquisition
  charges (10-K cash-flow statement and restructuring note). OCF is the clean leg;
  the OE base is built on it, so the divergence does not flatter the base.
- SECTOR_MODEL_MISMATCH — screener sector "Finance" (SIC is Real Estate Agents &
  Managers). A people/services OE/capex DCF is a rough fit; confidence low.
- OVERRIDE_APPLIED:capex — see DATA_GAP:capex above; the override fills only
  missing periods and replaces no filed value.
- BASE_DIVERGENCE — latest FY OE/share $20.1979 vs median $11.7299: the latest
  year is a cyclical peak (record OCF $1,194.1M on the transaction recovery) and
  the median spans the 2023 trough; for a cyclical the median is the right base
  and the latest year is the distorted one. Both are SBC-flattered (blocker).
- WIDE_SCENARIO_SPREAD — super-bull IV is 4.46× super-bear IV
  (scenario_spread_iv15); confidence capped at low.
- TIER_BAND — bear tier D (6.75%) vs bull tier C (10.50%): any verdict sizes to
  the bear end.

## Thoughts / method range / verdict

On every defensible base this is far below the 15% hurdle at $305.51: engine base
(SBC-flattered) weighted IRR 8.44%, IV@15% $136.84; the filing-corrected median
base (~$10.43/sh) would print lower still. The market is paying for the Q2 2026
adjusted-EPS trajectory (+34% guided growth) — an earnings-multiple story the
owner's-earnings record (ROIC ~7-12%, OE/share still below its 2021 level on a
corrected basis) does not yet support. Verdict, sized to the bear end: Tier D
territory, hurdle-clearing price at or below ~$137 even before the SBC
correction — but NO tier is scored until the main agent rules on the SBC tag
defect. Confidence low (sector misfit, wide spread, unresolved SBC leg).

Enrichment note: fundamentals.py ran (fundamentals.json written, ROIC quoted
above). prices/segments/statements/profile/reprice are skipped — they run after
a score exists; reprice.py skips unscored names by design. They run on the
re-score after the block is cleared.

## Engine 5.5 re-score (2026-10-19)

**STATUS: SCORED. Tier D by numbers, final tier D, no tier override, confidence low.**
This supersedes the BLOCKED status at the top of this file. The 2026-10-17 text above
is the dated record of the block and stays unedited. Model figures in this section come
from the final run's key_numbers.md, dcf_numbers.json and ttm.json (engine_release 5.5.0,
as of 2026-10-19). The filing figures used to check them are labelled with their source.

### Old vs new

| | Old (2026-10-17, engine 5.4) | New (2026-10-19, engine 5.5.0) |
|---|---|---|
| Base OE/share | none (blocked) | $9.81 (median_of_last_3_fy_oe_per_share) |
| Weighted IRR | none (blocked) | 7.52% (base case 7.51%) |
| Tier | none (blocked) | D (numbers D, final D; band bear D → bull D) |

JLL was never scored before. The 5.4 figures in the record above came from a diagnostic
run only. Its SBC leg was the slice the 5.5 rule replaces, so they are superseded rather
than compared.

### What engine 5.5 changed for this filer

- **SBC tag (the change that unblocks JLL).** Ruling 6 applies here. For every period
  where both tags report in the same unit and AllocatedShareBasedCompensationExpense
  exceeds ShareBasedCompensation, the engine now uses Allocated. key_numbers.md prints the
  reconciled years used in the base:
  - FY2023: Allocated $74.9M used over Share $3.4M
  - FY2024: Allocated $95.1M used over Share $2.3M
  - FY2025: Allocated $112.0M used over Share $2.7M

  The same rule covers the history years FY2018–FY2022. `used_tags.sbc` now names
  AllocatedShareBasedCompensationExpense, and `sbc_tag` records it per row in
  financials_history.csv. Arithmetic check on the latest year (AGENTS check 1): latest FY
  OE total $866.5M (key_numbers.md) = OCF $1,194.1M (ttm.json FY leg) − capex $215.6M −
  SBC $112.0M.
- **Capex tags: no change for JLL. The capex_override is kept.** Engine 5.5 adds
  PaymentsForCapitalImprovements, the additive PP&E components and intangible purchases.
  None of them is filed for FY2023–FY2025. `capex_provenance` shows ppe_source "override"
  in every year from FY2017 to FY2025, and key_numbers.md prints "PP&E $215.6M + intangibles
  $0.00" for FY2023, FY2024 and FY2025. The filing override therefore still fills those
  years (see OVERRIDE_APPLIED:capex below).
- **Share basis: no adjustment.** `share_scale.defect` is false. The latest diluted count,
  48,312,000, is 1.05× the cover-page count of 46,007,703 (dei, as of 2026-06-30), well
  inside the guard. `share_basis` records no split, no divergence and no unconfirmed split
  fact.
- **Market cap: no ADS ratio.** The cap is $14.760B on the diluted_latest basis
  (price × shares), in scope under $40B, and in_scope_under_40b is true.
- **USD-override branch: not applicable.** JLL is a USD filer. The capex override's
  `currency_basis` is no_fx, so no `currency` key is needed.

### New 5.5 flag, resolved by name

- **SBC_TAG_RECONCILED.** The engine used Allocated in every year it lists, because the
  Share tag at JLL is a fragment of total stock compensation, not a rounding difference.
  - **Size of the gap.** It is far above the flag's 1% rounding line: FY2025 is listed at
    +4048.1%, FY2024 at +4034.8% and FY2023 at +2102.9%.
  - **What the Share tag is.** It is the post-acquisition retention-award line in the
    restructuring note (record above).
  - **Cash-flow check.**
    - The 10-K cash-flow addback, "Amortization of stock-based compensation", is quoted
      in the 2026-10-17 record above. It equals Allocated plus the Share slice in each of
      the three years.
    - EDGAR companyfacts' AdjustmentsToAdditionalPaidInCapitalSharebasedCompensationRequisiteServicePeriodRecognitionValue
      carries the same totals: $114.7M FY2025, $97.4M FY2024, $78.3M FY2023.
    - So Allocated is the right primary figure. The engine's SBC is still short of the
      cash-flow addback by exactly the Share slice: $3.4M / $2.3M / $2.7M.
  - **Residual.** That residual flatters the base by a few cents a share, too little to
    move the tier. No override can add it, because a filed SBC value exists and an override
    never replaces a filed value.
  - **TTM legs.** ttm.json reconciled only the FY leg (`sbc_reconciled_legs`: fy, $112.0M
    over $2.7M). It warns that the TTM mixes tags across legs. The 10-Qs file only
    ShareBasedCompensation (companyfacts carries Allocated on 10-K annual facts only), so
    the two YTD legs are slices: $1.4M (H1 2025) and $0.2M (H1 2026). The 10-Q for the
    period ended 2026-06-30 prints the real totals as "Amortization of stock-based
    compensation": $66.0M (H1 2025) and $78.1M (H1 2026). ttm.json's TTM SBC of $110.8M
    is therefore understated. On the cash-flow totals the TTM is $114.7M − $66.0M + $78.1M
    = $126.8M, which is $16.0M more (sized under STALE_FY below). This is one of the
    reasons below for not pinning the TTM.

### Every flag on the final run

- **STALE_FY.** The latest FY ended 9.6 months before the run. ttm.py was re-run and its
  legs (ttm.json) are:
  - OCF: FY $1,194.1M − prior YTD −$434.8M + current YTD −$266.9M = TTM $1,362.0M
  - Capex: TTM $215.6M. All three legs are the override prorated by days: the FY leg is
    $215.6M and each half-year leg is $106.9M.
  - SBC: FY $112.0M (Allocated) − prior YTD $1.4M + current YTD $0.2M (both Share) = TTM
    $110.8M
  - Shares: 47,368,000 (current-YTD diluted)
  - TTM OE: $1,035.6M, or $21.86/share

  **The TTM is not pinned. The final run uses the 3-yr median.** This departs from
  WORKER_SPEC step 4, which says STALE_FY means passing `--ttm` in the final run and names
  only IFRS filers as an exception. JLL files us-gaap, so the choice is escalated to Andrew
  (see "Open for Andrew" at the end of this section). The worker gave three reasons:
  - **Capex leg.** ttm.json's capex is the prorated override. The 10-Qs file the actual
    line, "Net capital additions – property and equipment": $(88.9)M for H1 2025 and
    $(115.0)M for H1 2026 (10-Q, period ended 2026-06-30). statements.json, which reads
    that line from the 10-Qs, prints TTM capex of $241.7M. A TTM pin would therefore carry
    capex below the filed figure, which is the incomplete-capex case.
  - **SBC legs.** The H1 legs are Share slices (see SBC_TAG_RECONCILED above).
  - **Cycle.** The TTM is a transaction-upswing print, not a normalized level (see
    BASE_DIVERGENCE).

  The first two defects both flatter the TTM, and neither can be repaired in bounds. ttm.py
  prorates a single override value, the 10-Q files no Allocated SBC, and a base_override
  may use only figures this run printed. CBRE, the peer scored earlier in this sweep, also
  kept its 3-yr median and set its TTM aside, for H1 seasonality in that case.

  **Size of the first two defects** (arithmetic on the figures above, not an engine
  output):
  - Capex: statements.json TTM $241.7M − ttm.json $215.6M = $26.1M.
  - SBC: cash-flow TTM $126.8M − ttm.json $110.8M = $16.0M.
  - Together: $42.1M, or $0.89 a share on ttm.json's 47,368,000 shares. A corrected TTM
    OE is about $1,035.6M − $42.1M = $993.5M, or $20.97 a share, against ttm.json's
    $21.86. That is about 4%.

  The first two reasons therefore do not decide the base. A TTM pin reads Tier C by numbers
  whether or not its legs are corrected. A diagnostic `--measure` run with the same
  judgment inputs, pinned to ttm.json, reads Tier C. An offline replay of the final run's
  recorded `inputs` and `g_base` (dcf_numbers.json) at $20.97 also reads Tier C. Neither
  writes a file, and their IRRs are not quoted here. The median rests on the third reason,
  the cycle argument, alone.

  The choice moves the numbers tier (D on the median, C on a TTM pin) and the IRR shown,
  which sets the ranking position. Under the rules as written it does not move the
  published tier:
  - JLL is a sector misfit (score.json model_fit: misfit). The engine raises
    SECTOR_MODEL_MISMATCH for the Finance, Real Estate and Utilities sectors, so JLL would
    be a misfit whether its sector read Finance (the screener label) or Real Estate (its
    SIC 6531 industry).
  - The 2026-10-15 policy (AGENTS.md "Sector misfits") sizes a misfit's final tier one
    notch below its numbers tier. WORKER_SPEC step 4 exempts only P&C insurers and
    reinsurers on the payable-earnings base. Every other misfit keeps the 2026-10-15 rule.
  - A TTM pin would therefore publish Tier D, through a tier_override whose reason carries
    the pinned IRR.

  One policy point is left for Andrew: whether to exempt JLL from the notch. The rationale
  AGENTS.md gives for finance misfits is policyholder, deposit or loan flows in OCF, and
  JLL's OCF carries none (see SECTOR_MODEL_MISMATCH below). Only with that exemption would
  a TTM pin publish Tier C.
- **BASE_DIVERGENCE.** Latest FY OE/share is $17.94 against a 3-yr median of $9.81.
  Neither base contains a one-off. The gap is the transaction cycle.
  - **FY2023 trough.** FY2023 is the trough year. Its net income was depressed by
    non-cash equity losses (record above), and its OCF was the low point of the window.
  - **FY2025 and TTM upswing.**
    - Net income was $792.1M in FY2025 against $546.8M in FY2024 (statements.json).
    - OCF was $1,194.1M in FY2025 against $785.3M in FY2024 (financials_history.csv /
      statements.json).
    - Receivables absorbed cash in both years (statements.json change in receivables: an
      increase of $207.9M in FY2024 and $148.8M in FY2025), so the FY2025 OCF jump is
      earnings-led rather than a working-capital release.
    - The TTM ($21.86) extends the same upswing. Per the 10-Q, H1 2026 net income was
      $373.7M against $168.0M in H1 2025.
  - **Which base is distorted.** For a business whose OE/share went negative in 2022 and
    spans more than 3× over five years (OE_VOLATILE), the latest FY and the TTM are the
    cyclically elevated prints. The 3-yr median, whose median year is the recovery year
    FY2024, is the normalized base.
  - **Bias of the median.** It is conservative on two counts:
    - The median year carries the override's $215.6M of capex against the $185.5M FY2024
      filing figure in the override's own source text (key_numbers.md).
    - No scenario holds the FY2025 earnings level. The super-bull path starts at $15.11
      OE/share in year 1 (dcf_numbers.json paths), below the latest FY $17.94.

    I accept that cost because the verdict is sized to the conservative end and the final
    tier is D on either base.
- **OE_VOLATILE.** Confirmed cyclical: 4/5 OE-positive years (key_numbers.md), with FY2022
  negative once the override capex and reconciled SBC are charged. Handled through the
  median base and the bear-heavy probabilities 15/30/30/15/10, unchanged from the saved
  judgment.
- **NI_OCF_DIVERGENCE (2023).** Resolved in the record above and unchanged by 5.5. FY2023
  net income was depressed by non-cash equity losses and restructuring charges, which OCF
  adds back. The OE base is built on OCF, so the divergence does not flatter it.
- **SECTOR_MODEL_MISMATCH.** The screener sector is Finance. The SIC is 6531 (real estate
  agents and managers), and judgment.json's sector is Real Estate.
  - **Is OCF distorted the way a bank's is?** I checked whether JLL's mortgage-banking
    warehouse activity runs through OCF. It does not: the 10-Q's operating section (period
    ended 2026-06-30) has no warehouse-receivable lines and sums to the −$266.9M and
    −$434.8M legs in ttm.json. So OCF carries no deposit, loan or policyholder flows.
  - **Why the label still stands.** Fee-business cyclicality makes the OE DCF a rough fit.
    Confidence is low and the ranking lists JLL under sector misfits (score.json
    model_fit: misfit, alert_eligible false, exit_alert_eligible false with the reason
    "sector model misfit; tier exists only because of a judgment override").
  - **Notch.** The 2026-10-15 policy would size the final tier one notch below the numbers
    tier. The numbers tier is already D (weighted IRR 7.52%), and there is no lower notch,
    because F means no positive OE. So tier_override stays null. The notch only matters if
    the TTM is pinned (a C numbers tier). Under the written rule it would then size the
    final tier to D. Whether JLL should be exempted is the open question under STALE_FY
    above.
  - **Payable base.** JLL is not an insurer, so the payable-earnings base does not apply.
- **OVERRIDE_APPLIED:capex / DATA_GAP:capex.** dcf_numbers.json `data_gap` lists capex as
  found and covered, and `data_gap_uncovered` is empty, so no uncovered gap stands beside
  the tier.
  - **The override (unchanged).** Kind "filing", value $215.6M, from the FY2025 10-K
    cash-flow statement line "Net capital additions – property and equipment". It fills
    FY2017–FY2025.
  - **Measured impact on the 3-yr median base actually used** (key_numbers.md): base
    OE/share falls from $14.27 without the override to $9.81 with it (−31.24%). Weighted
    IRR falls from 9.64% to 7.52% (−2.12pp). Unblocks tier: YES.
  - **statements.json cross-check (AGENTS check 4).**
    - statements.json reads this cash-flow line from the tag
      PaymentsForProceedsFromProductiveAssets: FY2023 $186.9M, FY2024 $185.5M, FY2025
      $215.6M. These equal the filing figures in the override's source.
    - The CSV's capex is $215.6M in all three years, because the engine applies the single
      override value to every period with no read tag.
    - FY2025 matches exactly. FY2023 and FY2024 are overstated against the filed $186.9M
      and $185.5M. The gap is in the conservative direction: it lowers the median base and
      does not hide capex.
    - **Size of the gap** (arithmetic on financials_history.csv and statements.json, not
      an engine output). With the filed capex in each year, the median year is still
      FY2024, at ($785.3M − $185.5M − $95.1M) ÷ 48,372,000 = $10.43 a share, against the
      engine's $9.81. An offline replay of the final run's recorded inputs at $10.43 still
      reads Tier D (weighted, bear and bull), so the tier holds.
    - The engine's capex list does not include PaymentsForProceedsFromProductiveAssets, a
      net-of-disposals tag. That is why 5.5 still needs the override: a code follow-up for
      the main agent, not a worker fix. Once the engine reads that tag (after a check of
      the 10-K investing section that no material disposal proceeds are netted into it),
      the filed $186.9M / $185.5M / $215.6M all sit inside 0.5×–2× of the override. The
      override would then stop filling with no flag, and capex_override should be removed
      from judgment.json on that re-score.
  - **Coverage.** CAPEX_COVERAGE_LOW does not fire.
- **WIDE_SCENARIO_SPREAD.** Super-bull IV@15 is 4.46× super-bear (key_numbers.md).
  Confidence is low and never high.
- **Flags no longer firing.** TIER_BAND fired on the 5.4 diagnostic run. The final band is
  bear 6.07% (tier D) → bull 9.30% (tier D), so it no longer fires. No other 5.5 flag
  fires: none of SHARE_SCALE_SUSPECT, SHARE_BASIS_ADJUSTED, SHARE_BASIS_DIVERGENCE,
  CAPEX_COVERAGE_LOW or OVERRIDE_SUPERSEDED_BY_FILED_TAG:capex.

### Balance sheet

- **Net debt.** Net debt is $290.8M, which is 0.61× normalized OE (key_numbers.md).
  - It is computed on the DebtLongtermAndShorttermCombinedAmount total (dcf_numbers.json
    net_debt_basis). That total is broader than statements.json's long-term debt of
    $805.9M (FY2025), so the engine did not miss a borrowing tag.
  - The mortgage warehouse facilities are excluded. They fund the mortgage loans JLL
    originates for resale (warehouse receivables).
  - Operating lease liabilities of $941.1M (dcf_numbers.json) are outside net debt by
    method.
  - Neither HIGH_NET_DEBT nor BIG_NET_CASH fires.
- **Minority interests.** These are small, and JLL has no listed subsidiary, so
  consolidated OE is essentially all attributable to JLL shareholders.

### Scenarios (final run, key_numbers.md)

The moat is 5/10 with a CAP of 8.5 years and terminal growth of 2.50%. The growth blend is
11.17%, giving a g_base of 11.17%. Its components are:

- 5-year revenue CAGR: 9.50%
- 3-year revenue CAGR: 7.77%
- Latest revenue YoY: 11.45%
- 2-year OE/share CAGR: 74.16%. This is an inflection artifact off the FY2023 trough and
  does not drive the blend.

The share-count CAGR is −0.70%, which adds 0.70% to growth. Probabilities, offsets and
multipliers are unchanged from the saved judgment (15/30/30/15/10, default offsets and
multipliers).

| Scenario | Prob | Growth start | OE mult | IV@15 | IV@12 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -0.8% | 0.75 | $52.52 | $68.47 | 4.57% |
| Bear | 30% | 6.2% | 0.9 | $84.35 | $112.07 | 6.07% |
| Base | 30% | 11.2% | 1.0 | $115.18 | $154.93 | 7.51% |
| Bull | 15% | 16.2% | 1.1 | $155.40 | $211.41 | 9.30% |
| Super bull | 10% | 23.2% | 1.25 | $234.11 | $323.08 | 12.47% |

- **Weighted result.** IRR is 7.52%. Weighted IV is $114.46 at 15%, $154.39 at 12% and
  $199.19 at 10%, against a price of $305.50. Upside at 15% is -62.5%.
- **Hurdle prices** (weighted path): 15% at $114.46, 20% at $78.93, 25% at $59.64.
- **Diagnostics.** OE yield 3.21%, TV share at 15% 20.2%, net debt / normalized OE 0.61×.
- **Guidance vs model (WORKER_SPEC step 4).**
  - The Q2 2026 release (July 30, 2026) reported revenue up 11% and adjusted EPS up 59%.
    Management raised its FY2026 adjusted EPS target to a range reported as
    $24.60–$25.90, which implies 34% growth at the midpoint.
  - The base-case start of 11.2% matches the revenue prints. It sits below the guided
    adjusted-EPS growth, which is a non-GAAP earnings figure on an upswing. The model is
    therefore not above guidance.
  - The bull start of 16.2% and super-bull start of 23.2% cover the operating-leverage
    case.

### Why the tier is D

On the base this run defends, the weighted IRR is 7.52%. The bull case reaches only
9.30%, and the super bull 12.47%. The price of $305.50 sits far above every hurdle-clearing
price: 15% at $114.46.

The SBC correction is what engine 5.5 changed. It lowers the base from the
SBC-flattered diagnostic in the record above to $9.81. The direction the 2026-10-17 block
anticipated is confirmed.

A TTM pin would lift the numbers tier to C, even after its capex and SBC legs are
corrected (about $0.89 a share together, see STALE_FY). The median is kept on the cycle
argument. That departs from WORKER_SPEC step 4, so Andrew is asked to rule on it. Under
the written 2026-10-15 misfit rule, a TTM pin would still publish D, one notch below its C
numbers tier. Only an exemption from the notch, also put to Andrew, would let a TTM pin
publish C. Until he rules, the published tier is D on the 3-yr median. Verdict, sized to
the bear end: **Tier D**, hurdle-clearing price
$114.46. Confidence is low because of the sector misfit, the wide scenario spread and an
override-dependent tier.

### Research (2026-10-19)

- JLL, "JLL reports financial results for second quarter 2026" (jll.com newsroom, July 30,
  2026). Revenue +11%, adjusted EPS +59%, leasing advisory +24% in local currency, FY2026
  adjusted EPS target raised to +34% at the midpoint, and $410M of H1 2026 share
  repurchases.
- MarketBeat, "Jones Lang LaSalle Q2 earnings call highlights" (2026-07-31). Reports the
  $24.60–$25.90 adjusted EPS range.
- JLL Form 10-Q for the period ended 2026-06-30 (sec.gov, accession 0001037976-26-000152),
  condensed cash-flow statement. Stock-comp amortization: $78.1M / $66.0M. Net capital
  additions: $(115.0)M / $(88.9)M. No warehouse-receivable lines in operating activities.
- EDGAR companyfacts (CIK 1037976), fetched once for the SBC and capex tag checks above.

### Data and enrichment (2026-10-19)

- **Scripts run.** dcf_engine.py (preliminary, then final with `--moat 5 --probs
  0.15,0.3,0.3,0.15,0.1`, no pin; the diagnostic `--measure` runs write no file),
  ttm.py, make_score.py, then fundamentals.py, prices.py,
  segments.py, statements.py, profile.py and reprice.py. All exited 0.
- **profile.py warning.** No headcount sentence was found in the 10-K (employees null).
- **Code follow-up for the main agent: enrichment SBC rows.** statements.json's
  "Stock-based compensation" row still carries the ShareBasedCompensation values ($3.4M /
  $2.3M / $2.7M for FY2023–25, TTM $1.5M). So do fundamentals.json's `sbc` series and its
  TTM, and fundamentals.json's `capex` is null in every year after FY2014. The engine's
  5.5 rule (ruling 6) is not applied in statements.py or fundamentals.py.
  - statements.json's derived "Owner's earnings" row reads $385.5M / $597.5M / $975.8M
    for FY2023–25 (TTM $1,118.8M). The CSV's oe_conservative is $285.3M / $474.6M /
    $866.5M (ttm.json TTM $1,035.6M). In every year the gap is the stock compensation
    that the ShareBasedCompensation slice leaves out. The capex difference adds to it in
    FY2023–24, where the override sits above the filed line, and offsets part of it in
    the TTM, where ttm.json's capex sits below statements.json's.
  - The company page's statements viewer therefore shows owner's earnings about $100M a
    year above the valuation's. dcf_numbers.json and key_numbers.md are authoritative.

### Open for Andrew (2026-10-19)

1. **Base choice.** Keep the 3-yr median ($9.81, numbers Tier D) on the cycle argument,
   which needs a written exception for cyclical names in WORKER_SPEC step 4? Or pin the
   TTM as step 4 says, which reads numbers Tier C (published D under the notch)?
2. **Misfit notch at JLL.** As written, the 2026-10-15 notch applies to every misfit not on
   the payable-earnings base. A TTM pin would therefore need a tier_override D whose reason
   carries the pinned IRR. Should JLL be exempted, given that its OCF has no deposit, loan
   or policyholder flows? With an exemption, a TTM pin publishes Tier C.
3. **Code follow-ups (separate code PR).** (a) Read PaymentsForProceedsFromProductiveAssets
   as capex, or allow per-period override values; then remove capex_override here.
   (b) Apply the 5.5 SBC rule in statements.py and fundamentals.py.
