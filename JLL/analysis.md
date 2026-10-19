# JLL — Jones Lang LaSalle Incorporated

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
