# HUT — Hut 8 Corp.

Price $68.45 · market cap (est) $7.210B · Tier **F** (sub-type: no cash generation) · confidence low · engine 5.4.0, run 2026-10-19
All figures below are copied from `key_numbers.md`, `dcf_numbers.json`, `ttm.json` or the cited filings — none recomputed.

## What it is

Energy-infrastructure platform built out of a Bitcoin miner: Power, Digital Infrastructure
and Compute segments across 19 sites in the US and Canada — five Bitcoin mining / hosting /
Managed Services sites, five HPC data centers, four Ontario power-generation assets — formed
in its current shape by the November 2023 business combination with U.S. Bitcoin Corp.
(FY2025 10-K, Note 1). Majority-owned American Bitcoin Corp. (ABTC, Nasdaq-listed after its
2025 merger) holds the group's strategic Bitcoin accumulation; non-controlling interests were
$267,545,000 at Dec 31, 2025. EDGAR SIC is 6199 (Finance Services) — a classification misfit
for what is operationally a power/compute infrastructure company (see SECTOR_MODEL_MISMATCH).

## Owner's earnings

OE = operating cash flow − total capex − stock-based compensation. **OE-positive years in the
last 5: 0/5.** Operating cash flow itself was negative in every scored fiscal year, before any
capex is deducted.

- **Conservative (normalized) base:** median of last 3 FY OE/share = **−$3.43/sh** (latest FY
  OE/share also −$3.43; latest FY OE total −$360.9M on the override-applied capex).
- **TTM base (used; STALE_FY):** **−$3.50/sh** from `ttm.json` (base_source `ttm_json`).
  TTM legs, trailing twelve months to June 30, 2026: OCF FY2025 −$139,226,000 − H1 2025
  −$82,636,000 + H1 2026 −$32,845,000 = **TTM OCF −$89,435,000**; capex **$163,888,000**
  (filing override, below — no candidate tag exists, so every leg is the override);
  SBC FY2025 $57,802,000 − H1 2025 $11,433,000 + H1 2026 $102,113,000 = **TTM SBC
  $148,482,000**; TTM OE total **−$401,805,000** over 114,794,476 diluted shares (current-YTD
  weighted average) = **−$3.5002/sh**.
- **Maintenance version** (capex capped at D&A): not printed by the engine for this run; in
  words only — FY2025 D&A of $101,901,000 (FY2025 10-K cash-flow statement) against FY2025 OCF
  of −$139,226,000 means even a zero-capex base is negative. The F does not rest on deducting
  growth capex: there is no positive cash generation to capitalize (f_subtype
  `no_cash_generation` — OCF − capex is not positive).

**Which base and why:** the TTM pin is the engine standard under STALE_FY and is used; it
changes nothing — TTM (−$3.50), normalized median (−$3.43) and latest FY (−$3.43) are all
deeply negative, and on per-year filed capex instead of the single override value the median
of the last 3 FY OE/share (from `financials_history.csv` legs: Dec-2023 −$0.78, FY2024 −$2.51,
FY2025 −$3.94) is −$2.51/sh — still Tier F. The method range here is one tier wide: F on
every defensible base.

## OVERRIDE — capex (filing, $163,888,000)

The preliminary run exited 4, `DATA_GAP:capex`: Hut 8 files no capex under any tag in the
engine's candidate list. The filed cash-flow lines are "Purchases of property and equipment"
(tag `PaymentsToAcquireMachineryAndEquipment`), "Deposit paid to purchase miners and mining
equipment" (`PaymentsToAcquireMiningAssets`) and "Additions to intangible assets"
(`PaymentsToAcquireIntangibleAssets`) — FY2025 10-K (filed 2026-02-25, accession
0001104659-26-019392), Consolidated Statements of Cash Flows: $202,928k / $14,000k / $1,011k
for FY2025 and $123,991k / $39,611k / $286k for FY2024; full-calendar-2023 legs from the prior
10-K (filed 2025-03-03): $1,542,000 + $966,000 = $2,508,000. True annual totals: FY2023
$2,508,000, FY2024 $163,888,000, FY2025 $217,939,000; the override is the median, $163,888,000,
kind "filing", applied by the engine to every missing period. It overstates FY2023 capex by
$161,380,000 (conservative direction) and understates FY2025 by $54,051,000 (flattering; the
TTM pin charges the same $163,888,000 against TTM OCF, below FY2025's filed $217,939,000 run
rate). Excluded from capex, with reasons in `judgment.json`: Bitcoin purchased ($405,147,000
FY2025) and other digital assets purchased ($25,000,000) — treasury asset purchases presented
separately by the filer, not capex; deposits for future sites ($162,691,000 FY2025, custom
tag) — a deposit, no asset acquired, and including it leaves the median unchanged. The
mechanical `OVERRIDE_OUT_OF_BAND` flag (band computed against a last-filed value that does
not exist under any engine tag — `last_filed_value` is null) is acknowledged in the override's
`ack_reason`. Measured impact (`score.json` override_impact): TTM base −$2.07/sh without the
override → −$3.50/sh with it; the override unblocks the tier (without it the gap blocks
scoring entirely).

## Moat: 3/10 — weak; power scarcity without earned returns

CAP = 5.9 years (2 + 1.3 × 3).

**Evidence (from `fundamentals.json`):** `roic_proxy` series: −23.5% (FY2022-06), −319.3%
(FY2023-06, tiny capital base), +1.4% (Dec-2023), **+28.9% (FY2024 — digital-asset fair-value
gains sitting inside operating income, not earned operations)**, −18.5% (FY2025). Gross margin
(excl. D&A): 65.0% (FY2022-06), 47.5% (FY2023-06), 43.6% (Dec-2023), 46.6% (FY2024), 54.2%
(FY2025) — recovering, but it has never converted into positive operating cash flow.

**FOR**
- Secured power and interconnection pipeline is the binding constraint in AI infrastructure
  and takes years to replicate (1,020 MW under management, 330 MW under construction,
  1,230 MW under development at Dec 31, 2025 per the FY2025 10-K; 8,660 MW total pipeline at
  June 30, 2026 per the Q2 2026 release).
- Long-duration contracted AI data-center leases signed in 2026 (River Bend and Beacon Point
  Phase 1, 15-year terms, financed with $7.5B of non-recourse investment-grade project debt
  per the Q2 2026 release) give forward revenue visibility the mining book never had.
- Vertically integrated power platform (Ontario generation assets, King Mountain JV) and a
  large Bitcoin treasury (consolidated ~17,316 BTC at June 30, 2026 per Q2 2026 reporting)
  provide collateral and self-funding options peers lack.

**AGAINST**
- Mining is a commodity price-taker: revenue and margins are set by Bitcoin price, network
  difficulty and power cost — no pricing power; the April 2024 halving structurally compresses
  block rewards.
- Earned returns negative through the cycle (ROIC evidence above); OCF negative in 5 of the
  last 5 fiscal years.
- Extreme dilution funds the model: diluted share count +45.1%/yr (engine share CAGR 45.07%),
  SBC $13,564,000 (Dec-2023) → $20,783,000 (FY2024) → $57,802,000 (FY2025) → $148,482,000 TTM,
  plus repeated ATM equity issuance ($314,350,000 at parent level in FY2025, and ABTC-level
  issuance of $237,744,000 + $205,275,000 in FY2025 per the FY2025 10-K financing section).
- Capital intensity exploding, execution unproven: construction in progress $77,403,000 at
  Dec 31, 2025 → $808,356,000 at June 30, 2026 (Q2 2026 10-Q), against leases whose NOI is in
  no scored period.
- Consolidated figures include majority-owned ABTC: $267,545,000 of the Dec 31, 2025 equity
  is non-controlling interest — a material share of consolidated asset value and future mining
  earnings belongs to minority holders.

A moat of 7+ would need ROIC held well above the cost of capital through a cycle; Hut 8's
only positive print is a mark-to-market artifact. 3/10.

## DCF — v5 final run (2026-10-19)

The normalized base is negative, so the engine emits no scenario IVs or IRRs (scenarios are
not supportable on a negative base); probabilities used were the defaults
10/25/30/25/10 — recorded but inert here: with no scenario IVs emitted, the vector weights
nothing in any published figure. Diagnostics from `key_numbers.md`: growth blend 39.79% (rev CAGR 5y 39.22%,
3y 52.15%, latest rev YoY 44.79%) with a −5.00pp share-count adjustment (share count CAGR
45.07%).

**Growth-start sanity check (moot for the tier, recorded per spec):** the blended 39.79%
start sits below the latest FY revenue print (+44.79% YoY FY2025) and well below Q2 2026
revenue growth (+81.4% YoY, per the Q2 2026 release), so no scenario start overstates the
recent prints; the blend is inflated by the post-merger basis break (see flags) in any case.
None of this matters to the verdict: growth applied to a negative base produces no DCF.

| Scenario | Prob. | Result |
|---|---|---|
| Super bear | 10% | no IV/IRR — negative base |
| Bear | 25% | no IV/IRR — negative base |
| Base | 30% | no IV/IRR — negative base |
| Bull | 25% | no IV/IRR — negative base |
| Super bull | 10% | no IV/IRR — negative base |

**Weighted result: Tier F.** `alert_eligible: false`.

## Flags — every fragility flag resolved

- **DATA_GAP:capex** — resolved by the filing override above (median of the filer's own
  FY2023–25 cash-flow capex lines, $163,888,000). `data_gap_uncovered` is empty in the final
  run.
- **STALE_FY** — resolved: `ttm.py` run and `--ttm` passed; the base is the TTM pin
  (−$3.50/sh, legs quoted in the OE section). TTM capex is the filing override (no candidate
  tag exists in any period, so ttm.py's legs are the override, prorated — full-year legs net
  to exactly $163,888,000).
- **DILUTION** — real and accelerating. Diluted shares: 49,121,720 (Dec-2023) → 101,047,739
  (FY2024) → 105,328,890 (FY2025) → 114,794,476 (H1 2026 YTD average), with 123,259,468
  outstanding at July 31, 2026 (engine dei figure). SBC trend: $13,564,000 → $20,783,000 →
  $57,802,000 → $148,482,000 TTM — the H1 2026 YTD SBC leg alone is $102,113,000 vs $11,433,000
  in H1 2025. Funding is equity-led: FY2025 ATM proceeds $314,350,000 at the parent plus
  $443,019,000 of ABTC stock issuance (FY2025 10-K financing activities). The −5pp growth
  adjustment does not capture SBC of this size; it is fully deducted in OE as filed.
- **BASIS_BREAK_SUSPECT** — named: (1) the November 2023 U.S. Bitcoin Corp. business
  combination and the fiscal year-end change from June 30 to December 31 (the history carries
  both a FY2023-06 year and a Dec-2023 year); (2) the 2025 American Bitcoin / Gryphon merger
  and ABTC consolidation (goodwill $53,082,000 → $210,087,000; NCI $3,910,000 → $267,545,000);
  (3) Far North power assets moved to held-for-sale / discontinued presentation in FY2025
  (assets held for sale $38,719,000; liabilities held for sale $25,764,000 at Dec 31, 2025).
  No CAGR straddling these breaks is trusted — and none is needed: the verdict rests on the
  sign of OE, not on growth.
- **NI_OCF_DIVERGENCE (2023, 2024)** — the one-off is digital-asset fair-value accounting.
  FY2024 net income was $331,882,000 against OCF of −$68,535,000: the FY2024 cash-flow
  statement (FY2025 10-K) subtracts $509,337,000 of (gains) on digital assets — non-cash
  mark-to-market gains inside net income — plus a $3,060,000 bargain-purchase gain, partly
  offset by working-capital and deferred-tax moves ($111,758,000 deferred tax addback). The
  Dec-2023 period shows the same pattern at smaller scale (−$32,626,000 digital-asset gains).
  Net income at this company is a Bitcoin-price print, not an earnings print; the OE base
  correctly keys off OCF.
- **DEBT_TAGS_BLANK** — balance sheet stated from the filing (FY2025 10-K, Consolidated
  Balance Sheets, Dec 31, 2025, in thousands): cash $44,914; restricted cash $2,373; digital
  assets — held in custody $661,979, pledged for miner purchase $84,688 current + $242,937
  non-current, pledged as collateral $396,624; property and equipment, net $643,244; total
  assets $2,753,720. Loans, notes payable and other financial liabilities: $199,926 current +
  $210,235 non-current = $410,161 of debt the engine's tags missed (filed under a combined
  caption). Miner purchase liability (Bitmain equipment financing, debt-like): $100,910
  current + $332,153 non-current = $433,063. Total liabilities $1,064,250; total equity
  $1,689,470 including $267,545 NCI. Net debt on loans/notes alone is $410,161k − $44,914k
  cash = $365,247k; including the miner purchase liability, $798,310k — against $1,386,228k of
  digital assets carried on the same balance sheet. Post-period (Q2 2026 release): the parent
  since converted the $150.0M Coatue convertible and refinanced its $200.0M Bitcoin-backed
  facility (FalconX, 7.0%), and $7.5B of non-recourse project debt was closed at the
  River Bend / Beacon Point level — leverage is migrating to the project level, not
  disappearing.
- **SECTOR_MODEL_MISMATCH** — EDGAR SIC 6199 "Finance Services" (per `fundamentals.json`
  profile) misclassifies an energy/compute infrastructure operator; the OE/capex DCF is in
  fact the right shape for this business (real capex, real OCF), but per spec the flag caps
  confidence at low and the ranking lists the name under sector misfits. Confidence: **low**.
- **OVERRIDE_APPLIED:capex** — see the override section; the out-of-band mechanics are
  acknowledged in `judgment.json` (`ack_reason`).

## My thoughts / overlay

The market is not pricing scored cash flow — there is none. At $68.45 the $7.210B market cap
pays for the 2026 story: 949 MW of contracted AI data-center IT load and ~$26.6B of expected
base-term lease value (Q2 2026 reporting, post-period), an 8,660 MW pipeline, and a ~17,316
BTC consolidated treasury. That story may even be real — River Bend and Beacon Point carry
15-year take-or-pay leases and investment-grade non-recourse financing — but every dollar of
it is post-period, pre-revenue in the scored statements, and being built with construction in
progress that went from $77,403,000 to $808,356,000 in six months while TTM SBC hit
$148,482,000. Q2 2026 itself: revenue $74,932,000 (+81.4% YoY, per the Q2 2026 10-Q reporting)
with a net loss of $177.1M driven by $138.6M of unrealized digital-asset losses —
the same mark-to-market engine that manufactured FY2024's "profit." Basis note on that
$177.1M: it is the loss as presented in the company's Q2 2026 release / 10-Q income
statement, before allocating losses to non-controlling interests; the XBRL `NetIncomeLoss`
series in `fundamentals.json` prints −$150.2M for the quarter, which is the loss
attributable to common stockholders after the $27.0M non-controlling-interest share of the
loss (the two tie: −$177.1M + $27.0M = −$150.2M). Method range: F on the TTM base, F on the normalized median, F on
per-year filed capex — there is no defensible base on which this company has positive
owner's earnings today. A re-rating case has to be argued from contracted NOI that has not
yet appeared in any filing period, which is a venture underwriting, not a DCF input.

**Hurdle-clearing price:** none exists on current numbers — with a negative base OE/share
there is no price at which the model clears 15%; the IV@15 is not a low number, it is
undefined until OE turns positive.

## Final verdict

**Tier F — sized to the conservative end by construction (every base is negative).**
Power-scarcity optionality and a genuinely contracted AI lease book, wrapped around a mining
business with negative operating cash flow in five straight fiscal years, +45.1%/yr share
count growth and SBC compounding faster than revenue. No alert (Tier F,
`alert_eligible: false`).
