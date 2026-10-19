#!/usr/bin/env python3
"""
Standardized owner's-earnings DCF engine v2 (screening grade, consistent across all companies).

Key correctness rules learned from the APP pilot:
- EDGAR companyfacts 'fy' is the FILING's fiscal year — comparative columns share it.
  All series are keyed by PERIOD END DATE, never by fy. Latest filing wins per period
  (so history is on the latest restated / continuing-operations basis).
- Price comes from the Nasdaq quote API (Stooq hangs from this VM); fallback = universe.csv price.
- Capex: if no PPE-capex line exists for a period but the company files a full cash-flow
  statement, capex is treated as 0 and flagged (asset-light filers like APP do this).

Outputs: <TICKER>/financials_history.csv, <TICKER>/dcf_numbers.json
Usage: python3 dcf_engine.py TICKER [--price 123.45] [--moat 0-10] [--probs sb,b,base,bull,sbull] [--offsets pp,pp,pp,pp,pp] [--mults x,x,x,x,x]

v3 (2026-10-12, Andrew's edit): FIVE scenarios (super_bear, bear, base, bull, super_bull), each with
an agent-assigned probability (must sum to 1.0). Headline value = probability-weighted expected
cash-flow path -> weighted IV at 10/12/15% and a probability-weighted implied IRR; the hurdle
tier comes from the WEIGHTED IRR (base-case IRR kept for reference).

v4 (2026-10-12, brittleness audit — full list in DCF_AUDIT.md):
- Base OE is the MEDIAN of the last 3 fiscal years' OE/share (normalized), not the single
  latest year. --base-oe-ps overrides with an agent-supplied TTM figure when the FY is stale.
- Growth is a BLEND: median of rev CAGR 5y, rev CAGR 3y, latest rev YoY, and OE/share CAGR,
  then adjusted for share-count trend (buybacks add, dilution subtracts, clamped ±5pp).
- Fade holds g0 for 2 years, then converges to terminal over the CAP in either direction.
- Candidate EDGAR tags are merged per period (tag switches no longer truncate history).
- Terminal growth is a parameter (--gterm, default 2.5%).
- Every run emits diagnostics + fragility_flags (stale FY, base divergence, low OE yield,
  TV share, scenario spread, leverage, dilution, basis breaks, volatility, thin history,
  sector mismatch). The analyzing agent must address every flag in analysis.md.
MOAT-DRIVEN FADE: revenue/OE growth does not fade on a fixed schedule. It fades linearly from
g0 to the 2.5% terminal rate over the Competitive Advantage Period CAP = clamp(2 + 1.3*moat, 2, 15)
years (moat 0 -> ~2y, moat 5 -> ~8.5y, moat 10 -> 15y), with a 15-year explicit projection.
The moat score (0-10) is the analyzing agent's judgment, justified in analysis.md — the engine
only turns it into fade math. Defaults if unflagged: moat 5, probs 10/25/30/25/10,
growth offsets -12/-5/0/+5/+12pp vs the capped historical base growth,
OE level multipliers 0.75/0.90/1.00/1.10/1.25.

v5 (2026-10-13, external audit — see README Fixes & lessons): DATA GATE. Missing data used
to become zero silently (capex assumed $0, SBC dropped from OE) and fake tiers shipped.
Now: SBC tries AllocatedShareBasedCompensationExpense as a fallback tag; capex tries
construction-in-process / other-productive-assets tags; the tag actually used is recorded
per period in the CSV. If SBC, capex or diluted shares are missing for ANY of the last 3
fiscal years, the price is unavailable, or the filer reports in a non-USD currency
(non-USD unit present on revenue/NI/OCF facts), the engine writes dcf_numbers.json with a
data_gap list + DATA_GAP:<field> fragility flags, tier_by_numbers = null, prints a
DATA_GAP line and exits 4 (price-only gap exits 3, like NO_DATA) — it NEVER emits a tier
on a data gap. Fragility flags are computed BEFORE the Tier F branch so F names carry
theirs too. Dates use America/New_York, not the VM's UTC clock.

v5.1 (2026-10-13, Andrew's override rule — code flags gaps, the agent decides, and
every decision lands in a field): judgment.json may carry structured overrides
(capex_override / sbc_override / shares_override, each {value, source, reason,
kind: "filing"|"estimate"}). An override fills ONLY periods where the filing tag is
absent (the CSV tag column records OVERRIDE for those periods) — it never replaces
a filed value. Gaps fully covered by overrides proceed with a tier; partially
covered gaps still exit 4 listing only the uncovered ones. dcf_numbers.json records
data_gap (the original gaps found), data_gap_uncovered, overrides_applied, and
override_impact — the DCF run both ways (zero-fill baseline vs with-override) on
the engine-native base. `--measure` runs the math with no file writes and no gate
exit (used for the impact runs); DCF_NO_OVERRIDES=1 disables override loading.

v5.2 (2026-10-14, round-2 re-audit — the gate's perimeter was narrower than
"incomplete data"): (1) OCF joins the gate — missing operating cash flow for
ANY of the last 3 FY is DATA_GAP:ocf, with
NetCashProvidedByUsedInOperatingActivitiesContinuingOperations as a fallback
tag (a continuing-ops-only filer previously got a fake Tier F); the tag used
is recorded as ocf_tag. (2) Override sanity bounds — a negative override is
refused outright; a value outside 0.1x-10x of the last FILED value for that
field (or with no filed value at all) is out of band, flagged
OVERRIDE_OUT_OF_BAND, and make_score refuses it without an ack_reason in
judgment.json. (3) TTM pin provenance — `--ttm` reads the base from
<TICKER>/ttm.json (written by ttm.py); make_score refuses a pinned base
that differs from ttm.json by >0.1% unless judgment.json declares a
base_override. (4) Currency check scoped to the last 3 FY (a stray 2016 EUR
fact blocked a whole company); foreign-form filers (20-F/40-F, from EDGAR
submissions) need an ads_ratio judgment field — the engine applies it to
per-share figures and records it, make_score refuses without one. (5) IRR
solver: value still above price at a 200% discount rate now returns a
capped 2.0 with an IRR_CAPPED flag instead of a blank that tiered D.
(6) Diluted shares missing with only BASIC shares filed is DATA_GAP:shares
(diluted) — no silent swap. (7) Provenance: dcf_numbers.json carries a
content_hash (sha256 over the canonical payload); make_score recomputes
and refuses on mismatch or absence.

v5.3 (2026-10-14, Andrew's IFRS go decision): period_series merges across
TAXONOMIES (us-gaap candidates first, then ifrs-full) the same way v4 merged
across tags, with an ifrs-full concept map for every field (Revenue,
ProfitLoss, CashFlowsFromUsedInOperatingActivities,
PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities,
AdjustmentsForSharebasedPayments, AdjustedWeightedAverageShares = the
diluted denominator, etc.). Currency: values keep their filed unit per
period. A filer whose monetary facts are filed in USD — including the
issuer's own USD convenience translations (JD files CNY + USD) — is no
longer a currency gap. A single non-USD reporting currency is converted to
USD at period-end ECB reference rates (frankfurter.app); the rates used
are recorded in dcf_numbers.json (fx_conversion) and flagged FX_CONVERTED.
Flow facts use the period-end rate too — a screening simplification the
agent must note. Mixed reporting currencies, or a currency with no ECB
rate, remain DATA_GAP:currency. ADS handling is unchanged (v5.2).
v5.3.1 (same day, Codex review of Stocks PR #1 — four fixes): units merge
per period within a tag (v5.3 picked one unit per tag and dropped
local-currency-only years); conversion eligibility is judged on the
last-3-FY core facts, not all history (one stray historical currency
disabled conversion entirely); monetary judgment overrides are declared
in the reporting currency and are FX-converted at the period-end rate
before being applied (v5.3 inserted them verbatim into USD series); the
override sanity band anchors on the last filed value in its filed unit.

2026-10-19 (insurer payable-earnings base, Andrew's decision; engine_release
stays 5.4.0 — no existing run changes): `--base-judgment` pins the base to the
judgment.json base_override of basis "payable_earnings_5y" (five filed annual
operating-income-to-common figures / latest diluted shares, scaled by the ADS
ratio), recomputed and checked here (`load_payable_base`,
`payable_base_per_share`), recorded as dcf_numbers.json `payable_base` with
base_source "judgment_base_override"; a declaration that does not reproduce,
a share count that is not this run's latest, or an FX-converted filer is
refused (BAD_BASE_OVERRIDE, exit 3). make_score.py verifies and measures it.

v5.4 (2026-10-14, formula audit of the whole engine — every item below is a
behaviour change and is recorded as engine_release "5.4.0"; engine_version
stays 5 for the data-gate check):
(1) Share-count adjustment was DOUBLE-COUNTED (audit round-1 "Model design",
    never fixed): the ±5pp buyback/dilution adjustment was added on top of a
    blend that already contains OE/share CAGR, which embeds the share-count
    trend. Now the adjustment is applied to the three REVENUE components only;
    the OE/share CAGR enters the median unadjusted.
(2) The v5.2 "basic-only shares = DATA_GAP" rule was DEAD CODE for almost every
    filer: a basic-only period fell through to CommonStockSharesOutstanding /
    dei cover-page counts and shipped a tier with no flag. Now any non-diluted
    share source in the last 3 FY is DATA_GAP:shares (the fallback count is
    named in the flag so a filing override is one lookup away); older periods
    may use a fallback for history, with the source recorded per period in a
    new shares_tag CSV column and a SHARES_FALLBACK flag. dei counts match a
    period only within 90 days after its end (they are cover-page dates).
(3) Debt: LongTermDebt (a TOTAL including current maturities) sat in the
    noncurrent candidate list and stacked on DebtCurrent. Total-debt tags are
    now a separate debt_total series used only when no noncurrent tag exists;
    short-term borrowings / commercial paper / lease-inclusive tags added;
    the basis is recorded per period (debt_tag column) and a period with no
    debt tag at all raises DEBT_TAGS_BLANK instead of a silent net-cash read.
(4) IRR floor: the terminal value used max(r - g, 0.005), so no IRR could be
    solved below terminal growth + 0.5% and names at that floor ranked on a
    fake ~3.0%. The Gordon value does not converge at r <= g; present_value
    now returns +inf there, the solver converges onto g, and the run is
    flagged IRR_AT_FLOOR (diagnostics.irr_at_floor) — the true IRR is at or
    below terminal growth.
(5) IRR band + hurdle prices: irr_bear / irr_bull / tier_bear / tier_bull are
    emitted next to the weighted headline (audit P2: rank on a band, not a
    point), plus weighted iv_at_20 / iv_at_25 — the prices at which the A and
    S hurdles clear — and the full 15-year per-share paths (paths) and growth
    schedules (growth_paths) for every scenario and the weighted case.
(6) Tier F is split: f_subtype "sbc_exceeds_cash" (OCF - capex > 0 but SBC
    eats it) vs "no_cash_generation" (OCF - capex <= 0) — different stories.
(7) Portability: BASE comes from $STOCKS_BASE or the script's parent folder,
    so the engine runs anywhere; the math is in module-level functions
    (project_path / present_value / solve_irr / tier_for_irr) that the HTML
    builder and the test-suite import — one implementation, no drift.

v5.5 (2026-10-19, Andrew's rulings on the seven 5.5 spec drafts — engine_release
"5.5.0"; engine_version stays 5; the valuation math functions are untouched):
(1) ADS market cap: market_cap_est = price x shares / ads_ratio when a ratio
    applies (the engine had multiplied the ADS price by the ORDINARY count),
    and the normalized-OE total behind net_debt_to_normalized_oe /
    HIGH_NET_DEBT / BIG_NET_CASH uses the same basis (per-ADS OE x ADS count).
    Helpers market_cap_est (the one cap formula) / normalized_oe_total; record market_cap_basis.
(2) Share basis: (a) share-scale guard — base OE/share > 20x price, or the
    latest diluted count outside 1/100-100x a recent cover-page (dei) count,
    is DATA_GAP:shares (gap key share_scale, never coverable by an override)
    unless a declared base_override pin carries the base (then flagged
    SHARE_SCALE_SUSPECT); the market cap is rescaled by a power of ten read
    from the dei count (or the pin). (b) split basis — a filed split ratio
    dated after the latest FY end and confirmed by a post-event dei count
    (which must itself differ from the latest diluted count by more than
    15%: a dei that shows no basis change confirms nothing)
    rescales the history share counts filed before it (SHARE_BASIS_ADJUSTED);
    with no confirmed split, a 10-K filer whose post-FY dei count and latest
    diluted count sit with one more than 25% below the other (dei / diluted
    outside DIVERGENCE_BAND 0.75x-1.333x) prices its market cap on the dei
    count (SHARE_BASIS_DIVERGENCE).
    (c) a declared judgment.json share_class_mismatch (true, or {value: true,
    ...}) is DATA_GAP:shares (gap key share_class) — nothing rescues it; any
    other non-false shape is recorded as {"malformed": ...} without a gap
    (M5, below). Records share_scale, share_basis, share_class_mismatch; CSV
    column shares_split_factor.
(3-5) Capex assembly (capex_for_period): the PP&E roll-up
    (PaymentsToAcquirePropertyPlantAndEquipment or an IFRS PP&E tag) is
    authoritative when filed; otherwise the filed additive components (E&P,
    other PP&E, construction in process, productive assets, capital
    improvements) are SUMMED (one unit, older-filed identical-value re-tags
    dropped, and a value filed twice under two tags in ONE filing counted
    once). Zero-guard: a $0 from a non-primary candidate never blocks a
    non-zero later candidate. Intangible purchases (us-gaap
    PaymentsToAcquire(Other)IntangibleAssets, IFRS
    PurchaseOfIntangibleAssetsClassifiedAsInvestingActivities) are ADDED on
    top of any PP&E leg — never on the IFRS combined PP&E+intangibles tag,
    never on an OVERRIDE-filled period. capex_tag is the '+'-joined list of
    tags summed; CSV columns capex_ppe / capex_intangibles / capex_source;
    record capex_provenance and used_tags.capex_components. New flags
    CAPEX_COVERAGE_LOW (capex < 50% of D&A in each of the last 3 FY at a
    filer with positive PP&E) and OVERRIDE_SUPERSEDED_BY_FILED_TAG:capex.
(6) SBC: when ShareBasedCompensation and AllocatedShareBasedCompensationExpense
    report the same period in the SAME unit and Allocated is larger, Allocated
    is used (sbc_tag records it) and SBC_TAG_RECONCILED is raised; record
    sbc_provenance.
(7) USD overrides: an override declared currency "USD" (kind filing), or one
    whose field's last filed unit is USD, is used verbatim — not FX-converted;
    override_checks.<field>.currency_basis and
    fx_conversion.overrides_usd_verbatim record which rule fired.
[ADDITION — ECHO, after the retro-scan; not in the rulings — it stops an
    approved change (the decision-5 intangible leg) from producing a wrong
    number silently] An intangible capex fact is dropped for a period when the
    same tag carries the identical non-zero value (same unit) on a context
    longer than 380 days: a cumulative total filed on an annual context (ECHO:
    PaymentsToAcquireIntangibleAssets 30,000,000,000 on FY2024 and on
    2008-01-01..2023-12-31 / 2018-01-01..2025-12-31, which made FY2024 capex
    31,544,877,000 against 1,252,697,000 of OCF). Helper
    cumulative_context_values -> capex_for_period(cumulative=...); recorded in
    capex_provenance.<period>.dropped with reason 'cumulative_duplicate'.
    Intangible leg only (new in 5.5, so no 5.4 number can move); ttm.py
    applies the same helper per leg.
    Two make_score.py refusals ride on this release's records ([ADDITION]s,
    make_score docstring): a capex_override still declared beside
    OVERRIDE_SUPERSEDED_BY_FILED_TAG:capex (WY), and an override used verbatim
    under currency_basis 'last_filed_unit_usd' at a filer whose
    fx_conversion.from_currency is not USD without an explicit currency "USD"
    (HTHT). The engine's behaviour for both is unchanged.
[ADDITION — verifier round 1 (2026-10-19), the main agent's rulings E1-E11 on the
    round-1 findings; each stops an approved 5.5 change from producing a wrong number
    or a wrong record]
    E1  Share-scale rescue: a defect is carried by a pin only when the pin came from
        --base-oe-ps, judgment.json declares a base_override WITHOUT `basis` whose
        value equals the pin within 0.1%, and the pin itself passes test (a)
        (|pin| <= 20x price) — share_scale_pin_rescue / load_declared_base_override.
        5.5 rescued any --base-oe-ps number (a mis-scaled TTM figure scored where the
        same figure through --ttm gapped). A rejected pin is named in
        share_scale.pin_rejected and in the DATA_GAP:shares — SHARE_SCALE text; the
        pin feeds the cap's power-of-ten factor only when it rescues.
    E2  A share-scale defect whose share series breaks scale inside the growth window
        (two adjacent counts among the last 4 more than 100x apart — VIV) drops the
        share-count CAGR and the OE/share CAGR from the growth blend (share
        adjustment 0): share_scale.scale_breaks / growth_inputs_dropped(_values),
        named in SHARE_SCALE_SUSPECT / DATA_GAP:shares — SHARE_SCALE. A consistently
        scaled series (NTNX) keeps them.
    E3  A rescued defect with no power-of-ten factor and no usable dei (test (b) not
        evaluable): net_debt_to_normalized_oe is not computed and HIGH_NET_DEBT /
        BIG_NET_CASH are not tested (share_scale.leverage_unverifiable; the flag
        says so). With a dei that passed test (b) (VIV) they stand.
    E4  A filed share count <= 0 (any share tag, diluted or fallback, and a dei
        cover count) is treated as not filed: the next candidate tag with a positive
        count fills the period, else raw_missing shares (DATA_GAP:shares in the last
        3 FY — TLN FY2022's diluted 0). share_basis.nonpositive_counts. The median
        window itself is unchanged (it still skips a year with no OE/share — a
        listed follow-up).
    E5  Capex components: a component equal within 0.5% to the sum of two or more
        other components of its period (same unit) is the total — kept, the parts
        dropped ('parts_of_total'; GLPI FY2024). No other near-equal rule.
    E6  Intangible leg: a negative fact is dropped ('negative'); a $0 fact contributes
        nothing and joins nothing (capex_tag, intangible_tags, the OVERRIDE_APPLIED
        'not added' note, ttm.py's warning). PP&E legs unchanged.
    E7  An assumed-zero row (no PP&E leg) does not add the intangible leg: capex 0,
        capex_tag blank, capex_intangibles records the amount, capex_provenance
        intangibles_not_added 'no_ppe_leg'.
    E8  used_tags.sbc = the latest CSV row's filed sbc_tag (after reconciliation).
    E9  SHARE_BASIS_ADJUSTED names the split from its ratio (split_label: 1-for-20,
        1-for-15) and lists the adjusted years one by one, plus "except FY<y>
        (OVERRIDE count, not rescaled)" (share_basis.split.periods_override_not_rescaled).
    E10 (ttm.py) an override-backed capex leg now filled off-band by a tag outside the
        5.4 list warns and is recorded in ttm.json capex_override_superseded_legs.
    E11 share_basis.in_history_split_facts lists split facts dated on or before the
        latest FY end (informational; nothing is rescaled — TPL's in-history split
        is a listed limitation).
    M5 (engine half) load_share_class_mismatch: only bool true, an object whose
        `value` is bool true, or an object without `value` carrying a non-empty
        source declares (DATA_GAP:shares — SHARE_CLASS_MISMATCH); false, null,
        {value: false} and {} declare nothing; strings ("false", "no", "true"),
        numbers and other shapes are recorded as {"malformed": <repr>} with NO gap
        (make_score refuses them).
[ADDITION — verifier round 2 (2026-10-19); each stops an approved 5.5 change from
    producing a wrong number or record, inside the round-1 rulings' own reasons]
    R2-E3 (extends E3) leverage_unverifiable also when a usable dei EXISTS but test
        (b) failed (the latest diluted count is more than 100x off the cover page)
        and no power-of-ten factor was found: the cover page then proves the cap's
        count wrong, which E3's "unverified" covers a fortiori (a synthetic filer
        printed HIGH_NET_DEBT 666.7x). With a dei that passed test (b) (VIV) the
        diagnostics still stand. Put to Andrew beside E3.
    R2-CAP scale_factor_for_cap: a usable dei within 25% of the latest diluted count
        (k = 0) confirms that count — no factor, and the pin is never consulted (a
        VIV-shaped pin equal to native/1000 multiplied a confirmed count by 1,000:
        a $19.76T cap). DESIGN §2a's own VIV line ("dei ratio 1 -> no factor").
        WITHDRAWN in round 3 — replaced by R3-CAP below.
    R2-PIN test (a) is evaluated on the base actually used as well: a pin
        (--ttm, --base-oe-ps, --base-judgment) whose |value| exceeds 20x the price
        is a share-scale defect (share_scale.pin_over_price; gap key share_scale —
        the pin fails E1 (3), so nothing rescues it), whether or not the native
        median shows one. Ruling 2's text is "base OE/share > 20x price"; with a pin
        the base IS the pin (a TTM leg filed in thousands scored Tier S at 73x).
    R2-E2 (refines E2 by its own reason) the OE/share CAGR leaves the growth blend
        only when a scale break lies between its two endpoints (oe_ps_hist[-3] ..
        oe_ps_hist[-1]); a break before FY t-2 leaves both endpoints on one scale and
        the CAGR valid. share_cagr still drops on any break in the last four counts
        (its window always spans the break); share_scale.growth_inputs_dropped lists
        what was dropped, share_scale.growth_inputs_kept a kept OE/share CAGR, and
        the flag text says it stays in the blend (R4-E2 compares the two endpoint
        counts only).
    R2-E4 a cover-page (dei) count <= 0 that dei_for_period skips for a fallback year
        is recorded in share_basis.nonpositive_counts too (series "dei", its cover
        date, replaced_by the positive cover count used, or null) — LTM 2017.
[ADDITION — verifier round 3 (2026-10-19); each stops an approved 5.5 change from
    producing a wrong number]
    R3-CAP (replaces R2-CAP) the pin's power of ten measures the scale of the count
        behind the native median, but the cap factor multiplies the LATEST count:
        scale_factor_for_cap's pin path applies only when the median's defining
        year's count and the latest count (the endpoints of median_window_counts)
        are on one scale — no more than 100x apart (round 3 tested every adjacent
        pair of the window; R4-CAP below narrows it to the endpoints). The dei
        path stays first; R2-CAP's "dei within 25% -> no factor"
        return is withdrawn (the window test handles VIV; the return had kept a
        1,000x-small cap when every count, the dei included, was in thousands).
        A power-of-ten pin ratio withheld by a break is recorded in
        share_scale.pin_factor_withheld and named in SHARE_SCALE_SUSPECT; E3 /
        R2-E3 then decide the leverage diagnostics (no dei -> unverifiable). A
        correct latest count beside thousands-scaled median years had taken
        x1,000: a $3.0T cap for a $3.0B synthetic filer (no dei, a dei 0.67x the
        count, or a 20-F cover count in other units).
    R3-SPLIT confirm_split tests the post-event dei against the latest FILED count
        (the most recent history row whose count is not an OVERRIDE), not against an
        override in the latest FY: a shares_override must be on the post-split basis
        (D7), so it equals the post-event dei and confirmed nothing — the filed
        history stayed pre-split (base 0.6509 for 1.9526, Tier C -> D, no flag).
        share_basis.split.confirmed_against_period names the row; the
        SHARE_BASIS_ADJUSTED text adds "against the FY<y> filed count" when it is
        not the latest FY. Overrides are still never rescaled.
[ADDITION — verifier round 4 (2026-10-19); each completes a round-2/3 fix by its own
    stated rule, so it stops an approved 5.5 change from producing a wrong number]
    R4-CAP "the median year's count and the latest count on one scale" is tested on
        those two counts (median_latest_scale_breaks: the endpoints of
        median_window_counts), not on every adjacent pair of the window. A year
        between them on another scale — filed on the true scale, or filled by a
        true-scale shares_override — had withheld a correct x1,000 (FY2023 and FY2025
        both 2,000,000, FY2024 2,000,000,000: cap $60M for $60B, in_scope_under_40b
        forced true, leverage suppressed, and SHARE_SCALE_SUSPECT saying the two
        equal counts were "on another scale"). pin_factor_withheld.breaks and the
        flag name the endpoint pair.
    R4-E2 (refines R2-E2) the OE/share CAGR reads only oe_ps_hist[-3] and
        oe_ps_hist[-1], so it leaves the growth blend only when THOSE two counts
        are more than 100x apart; an alternating series between them no longer
        drops it (dropping it had cut a synthetic filer's g_base from 7.68% to
        6.66%). share_cagr is
        unchanged (ruling E2: any break among the last four counts drops it).
    R4-E3 (extends E3 / R2-E3) a rescued defect with no cap factor whose dei PASSED
        test (b) is unverifiable too when test (a) fired on the native median and
        the latest count is on the median year's scale (no endpoint break): the
        latest count then carries the scale test (a) found wrong, so the agreeing
        dei is filed on the same basis (every count and the cover page in
        thousands, a TTM pin 2.4% off native/1,000: cap 1,000x small, a false
        HIGH_NET_DEBT 500x). net_debt_to_normalized_oe is not computed, the leverage
        flags are not tested and the flag says why (no "agrees within 25%"
        reassurance). The cap itself is still price x the filed count (no factor
        is invented) — a listed follow-up. VIV keeps its diagnostics (endpoint
        break). Put to Andrew beside E3 / R2-E3.
"""
import json, sys, os, csv, urllib.request, datetime, re, time, subprocess, hashlib, statistics
from fractions import Fraction
from itertools import combinations
from zoneinfo import ZoneInfo

UA = {"User-Agent": "Muse research andrewmauro199612@gmail.com"}
BASE = os.environ.get("STOCKS_BASE") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYS = f"{BASE}/_system"
ENGINE_RELEASE = "5.5.0"
ET_TODAY = datetime.datetime.now(ZoneInfo("America/New_York")).date()
MEASURE = "--measure" in sys.argv   # compute + print JSON only: no file writes, no gate exit
HOLD_YEARS = 2          # v4: growth holds at g0 for 2 years before the fade starts
PROJECTION_YEARS = 15
DEFAULT_GTERM = 0.025
GROWTH_CAP_BASE = 0.35  # g_base cap (20% until 2026-10-12 — see README Fixes & lessons)
GROWTH_CAP_START = 0.50 # scenario start cap
GROWTH_FLOOR_BASE, GROWTH_FLOOR_START = -0.05, -0.10


# ---------------------------------------------------------------------------
# Valuation math (module-level so make_score / build_daily_html / tests import
# the SAME functions the engine runs — v5.4).
# ---------------------------------------------------------------------------
def growth_path(g0, cap_years, gterm=DEFAULT_GTERM, n=PROJECTION_YEARS, hold=HOLD_YEARS):
    """Per-year growth rate: holds at g0 for `hold` years, then converges
    linearly to gterm over cap_years — in either direction, never overshooting."""
    step = (g0 - gterm) / cap_years if cap_years > 0 else (g0 - gterm)
    out = []
    for t in range(1, n + 1):
        g = g0 - step * max(0, t - hold)
        g = min(g, g0) if g0 > gterm else max(g, g0)      # never overshoot past g0
        g = max(g, gterm) if g0 > gterm else min(g, gterm)  # never cross past terminal
        out.append(g)
    return out


def project_path(oe0, g0, cap_years, gterm=DEFAULT_GTERM, n=PROJECTION_YEARS, hold=HOLD_YEARS):
    """15 per-share owner's-earnings flows from base oe0 along growth_path()."""
    flows, cur = [], oe0
    for g in growth_path(g0, cap_years, gterm, n, hold):
        cur *= (1 + g); flows.append(cur)
    return flows


def present_value(flows, r, gterm=DEFAULT_GTERM):
    """PV of the explicit flows plus a Gordon terminal value on the last flow.
    v5.4: the terminal value does not converge at r <= gterm — the old
    max(r - g, 0.005) floor manufactured a finite value there and no IRR
    could be solved below g + 0.5%. +inf is the honest answer."""
    if r <= gterm:
        return float("inf")
    v = sum(f / (1 + r) ** (t + 1) for t, f in enumerate(flows))
    tv = flows[-1] * (1 + gterm) / (r - gterm)
    return v + tv / (1 + r) ** len(flows)


def terminal_share(flows, r, gterm=DEFAULT_GTERM):
    total = present_value(flows, r, gterm)
    if not total or total == float("inf"):
        return None
    tv = flows[-1] * (1 + gterm) / (r - gterm) / (1 + r) ** len(flows)
    return tv / total


def solve_irr(flows, px, gterm=DEFAULT_GTERM):
    """(irr, capped, at_floor). capped: value at a 200% rate still exceeds
    the price (round-2 fix — recorded as 2.0, not blank). at_floor (v5.4):
    the bisection converged onto the Gordon boundary, i.e. the true IRR is at
    or below terminal growth; the returned value is the floor, not a solution."""
    if present_value(flows, 2.0, gterm) > px:
        return 2.0, True, False
    lo, hi = -0.5, 2.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if present_value(flows, mid, gterm) > px: lo = mid
        else: hi = mid
    irr = (lo + hi) / 2
    # A perpetuity growing at g has an IRR above g at ANY finite price, so the
    # model cannot express a return below g_terminal: anything within 0.5pp of
    # it (the region the old 0.005 denominator floor distorted) is "at floor".
    return irr, False, (irr - gterm) <= 0.005 + 1e-12


def tier_for_irr(irr):
    if irr is None:
        return None
    return "S" if irr >= 0.25 else "A" if irr >= 0.20 else "B" if irr >= 0.15 else "C" if irr >= 0.10 else "D"


def cap_years_for_moat(moat):
    """Competitive advantage period: clamp(2 + 1.3 * moat, 2, 15) years."""
    moat = max(0.0, min(10.0, float(moat)))
    return max(2.0, min(15.0, 2 + 1.3 * moat))


def replay_paths(numbers):
    """(paths, growth_paths) for a recorded dcf_numbers.json payload — the
    flows the scored run discounted, replayed from its recorded inputs
    exactly as the engine computed them (g0 = clamp(g_base + offset),
    project_path(base * mult, g0, CAP(moat), g_terminal), weighted =
    probability-weighted sum). Mirrors build_daily_html.forecast_paths; used
    by reprice.py so the live IRR is solved on the SAME flows as the scored
    IRR (bit-for-bit at the scored price).

    Engine 5.4 also stores `paths` / `growth_paths`, rounded to 6 decimals
    for the file. Those are the fallback, not the first choice: the replay
    is exact, the stored copy is not. The stored copy is returned only when
    the inputs are missing (a hand-built or foreign record) or when the
    replay disagrees with it beyond rounding (the record is the engine's
    own output and wins over a drifted replay). (None, None) when neither
    is available. Additive (v5.4 reprice)."""
    if not isinstance(numbers, dict):
        return None, None
    stored = None
    if numbers.get("paths") and numbers.get("growth_paths"):
        stored = (numbers["paths"], numbers["growth_paths"])
    inp, scn = numbers.get("inputs") or {}, numbers.get("scenarios") or {}
    try:
        base = float(numbers.get("base_oe_per_share"))
        gb = float(numbers.get("g_base"))
    except (TypeError, ValueError):
        return stored or (None, None)
    if not inp or not scn:
        return stored or (None, None)
    labels = ["super_bear", "bear", "base", "bull", "super_bull"]
    gterm = inp.get("g_terminal", DEFAULT_GTERM)
    cap = cap_years_for_moat(inp.get("moat", 5))
    paths, gpaths = {}, {}
    try:
        for i, k in enumerate(labels):
            g0 = max(GROWTH_FLOOR_START, min(GROWTH_CAP_START, gb + inp["offsets"][i]))
            paths[k] = project_path(base * inp["mults"][i], g0, cap, gterm)
            gpaths[k] = growth_path(g0, cap, gterm)
        probs = inp["probs"]
        paths["weighted"] = [sum(probs[i] * paths[labels[i]][t] for i in range(5)) for t in range(len(paths["base"]))]
    except Exception:
        return stored or (None, None)
    if stored is not None and not _paths_agree(paths, stored[0]):
        return stored
    return paths, gpaths


def _paths_agree(replayed, stored, tol=1e-5):
    """True when every stored path (rounded to 6 dp by the engine) matches the
    replayed one within `tol` per flow — i.e. they differ only by rounding."""
    try:
        for k, flows in stored.items():
            rep = replayed.get(k)
            if rep is None or len(rep) != len(flows):
                return False
            if any(abs(float(a) - float(b)) > tol * max(1.0, abs(float(b))) for a, b in zip(rep, flows)):
                return False
        return True
    except (TypeError, ValueError, AttributeError):
        return False

def load_overrides(ticker):
    """Structured judgment overrides from {ticker}/judgment.json. A malformed or
    incomplete override (non-numeric value, kind outside filing|estimate, blank
    source/reason) is ignored here; make_score.py validates strictly and refuses
    on any disagreement between judgment.json and what the engine applied."""
    if os.environ.get("DCF_NO_OVERRIDES"):
        return {}
    try:
        j = json.load(open(f"{BASE}/{ticker}/judgment.json", encoding="utf-8"))
    except Exception:
        return {}
    out = {}
    for field, key in (("capex", "capex_override"), ("sbc", "sbc_override"), ("shares", "shares_override")):
        o = j.get(key) if isinstance(j, dict) else None
        if (isinstance(o, dict) and isinstance(o.get("value"), (int, float))
                and not isinstance(o.get("value"), bool)
                and o.get("kind") in ("filing", "estimate")
                and str(o.get("source") or "").strip() and str(o.get("reason") or "").strip()):
            out[field] = {"value": float(o["value"]), "kind": o["kind"],
                          "source": o["source"], "reason": o["reason"],
                          "ack_reason": str(o["ack_reason"]).strip() if isinstance(o.get("ack_reason"), str) and o["ack_reason"].strip() else None}
            # v5.5 (decision 7): an explicit currency declaration is passed
            # through upper-cased; make_score validates it ("USD", kind filing).
            if isinstance(o.get("currency"), str) and o["currency"].strip():
                out[field]["currency"] = o["currency"].strip().upper()
    return out

PAYABLE_BASIS = "payable_earnings_5y"
# SIC codes the payable-earnings rule is scoped to (P&C insurers and reinsurers):
# 6331 Fire, Marine & Casualty Insurance; 6351 Surety Insurance. Life (6311),
# accident & health (6321), banks and REITs keep the OCF base + notch rule.
PAYABLE_SIC = frozenset({"6331", "6351"})

def payable_base_per_share(figures, shares, ads_ratio=None):
    """Insurer payable-earnings base (Andrew, 2026-10-19): the average of the
    last five fiscal years' operating income available to common shareholders
    (filing USD, dollars) over the latest diluted share count, scaled by the
    ADS ratio so the pin is comparable to the traded price (per-share pins are
    not scaled anywhere else — see the ADS flag text)."""
    figs = [float(x) for x in figures]
    if len(figs) != 5 or not shares or float(shares) <= 0:
        raise ValueError("payable base needs exactly five annual figures and a positive share count")
    ratio = float(ads_ratio["ratio"]) if ads_ratio else 1.0
    return sum(figs) / 5.0 / float(shares) * ratio

def load_payable_base(ticker):
    """judgment.json base_override with basis payable_earnings_5y:
    {value (per ORDINARY share, filing USD), kind "filing", basis, figures [5],
    shares, source, reason}. Returns the dict, or raises ValueError naming the
    defect — the engine refuses the run rather than guessing."""
    try:
        j = json.load(open(f"{BASE}/{ticker}/judgment.json", encoding="utf-8"))
    except Exception as e:
        raise ValueError(f"judgment.json unreadable ({e})")
    o = j.get("base_override") if isinstance(j, dict) else None
    if not isinstance(o, dict):
        raise ValueError("judgment.json carries no base_override object")
    if o.get("basis") != PAYABLE_BASIS:
        raise ValueError(f"base_override.basis must be {PAYABLE_BASIS!r}")
    if o.get("kind") != "filing":
        raise ValueError("base_override.kind must be 'filing' (the figures come from the filer's releases / 10-K)")
    figs = o.get("figures")
    if not (isinstance(figs, list) and len(figs) == 5
            and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in figs)):
        raise ValueError("base_override.figures must list exactly five annual operating-income-to-common figures (dollars)")
    if not isinstance(o.get("shares"), (int, float)) or isinstance(o.get("shares"), bool) or o["shares"] <= 0:
        raise ValueError("base_override.shares must be the latest diluted share count (a positive number)")
    if not isinstance(o.get("value"), (int, float)) or isinstance(o.get("value"), bool):
        raise ValueError("base_override.value must be a number (per ordinary share)")
    if not str(o.get("source") or "").strip() or not str(o.get("reason") or "").strip():
        raise ValueError("base_override.source and .reason must be non-empty")
    per_ord = sum(float(x) for x in figs) / 5.0 / float(o["shares"])
    if abs(per_ord - float(o["value"])) > 0.005:  # cent-level: the construction must reproduce to the cent
        raise ValueError(f"base_override.value {o['value']} does not reproduce from figures/shares ({per_ord:.6f}) to the cent")
    o = dict(o); o["value"] = per_ord  # the recomputed figure is the one recorded and pinned
    return o

def load_declared_base_override(ticker):
    """[ADDITION — verifier round 1, ruling E1] judgment.json's base_override object as declared (None when absent or
    unreadable) — read for the share-scale rescue test (share_scale_pin_rescue), never applied here: the pin itself
    still arrives through --base-oe-ps and make_score validates the declaration."""
    try:
        j = json.load(open(f"{BASE}/{ticker}/judgment.json", encoding="utf-8"))
    except Exception:
        return None
    o = j.get("base_override") if isinstance(j, dict) else None
    return o if isinstance(o, dict) else None


def load_share_class_mismatch(ticker):
    """v5.5 (decision 2 §5, flag route): judgment.json `share_class_mismatch`
    declares that the filed share count is a different class from the traded
    security. [ADDITION — M5, round-1 verification] Strict shapes (the same
    rule as make_score.share_class_status):
      - declared: bool true, an object whose `value` is bool true, or an
        object without `value` that carries a non-empty source ->
        {"declared": True, "source", "reason"} (truthy: DATA_GAP:shares —
        SHARE_CLASS_MISMATCH; a bare `true` counts, and make_score refuses a
        declaration lacking source/reason — it never ignores one);
      - not declared: absent, null, false, {value: false}, an empty object ->
        None;
      - malformed: anything else (strings such as "false" / "no" / "true",
        numbers, lists, an object whose `value` is not a bool, a non-empty
        object with neither `value` nor a source) -> {"malformed": repr(value)},
        recorded in dcf_numbers.json without a gap (the caller raises the
        share_class gap only for a record with "declared": a typo is not a
        declaration); make_score refuses it, naming the accepted shapes."""
    def _text(x):
        return x.strip() if isinstance(x, str) and x.strip() else None

    try:
        j = json.load(open(f"{BASE}/{ticker}/judgment.json", encoding="utf-8"))
    except Exception:
        return None
    v = j.get("share_class_mismatch") if isinstance(j, dict) else None
    if v is None or v is False:
        return None
    if v is True:
        return {"declared": True, "source": None, "reason": None}
    if isinstance(v, dict):
        src, why = _text(v.get("source")), _text(v.get("reason"))
        if "value" in v:
            if v["value"] is True:
                return {"declared": True, "source": src, "reason": why}
            if v["value"] is False:
                return None
        elif src:
            return {"declared": True, "source": src, "reason": why}
        elif not v:
            return None
    return {"malformed": repr(v)}

def load_ads_ratio(ticker):
    """ads_ratio from judgment.json ({ratio, source, reason}) for foreign-form
    filers: ratio = ordinary shares per ADS. Per-share EDGAR figures for a
    20-F/40-F filer are per ordinary share while the traded price is per ADS."""
    try:
        j = json.load(open(f"{BASE}/{ticker}/judgment.json", encoding="utf-8"))
    except Exception:
        return None
    a = j.get("ads_ratio") if isinstance(j, dict) else None
    if (isinstance(a, dict) and isinstance(a.get("ratio"), (int, float))
            and not isinstance(a.get("ratio"), bool) and float(a["ratio"]) > 0
            and str(a.get("source") or "").strip() and str(a.get("reason") or "").strip()):
        return {"ratio": float(a["ratio"]), "source": a["source"], "reason": a["reason"]}
    return None


def market_cap_est(price, shares, ads_ratio=None, fallback=None):
    """Traded market cap. `price` is per traded unit — per ADS for a
    foreign-form filer — while `shares` is the ordinary share count from
    EDGAR, so when an ads_ratio applies the ordinary count is divided by
    it (ordinary shares / shares-per-ADS = ADS count; x per-ADS price =
    traded cap). No ratio (or ratio 1) is the identity — bit-identical to
    the pre-fix price * shares. Missing price/shares returns `fallback`
    (the universe screener cap, already a traded cap, never rescaled).
    v5.5: `ads_ratio` may be the engine's {ratio, ...} dict or a plain number
    (make_score / reprice pass the recorded ratio); a missing, zero, negative
    or boolean ratio is no ratio. This is the one market-cap formula — the
    engine, make_score's pre-5.5 ADS correction and reprice's live cap all
    call it."""
    if price and shares:
        r = _ratio_value(ads_ratio)
        ratio = r if (r is not None and r > 0) else 1.0
        return price * shares / ratio
    return fallback

def _content_hash(payload):
    """sha256 over the canonical dcf_numbers payload (everything except the
    hash itself). make_score.py recomputes it and refuses on mismatch or
    absence — hand-edited numbers cannot pass as engine output."""
    canon = json.dumps({k: v for k, v in payload.items() if k != "content_hash"},
                       sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canon.encode()).hexdigest()

def _measure_run(ticker, price, no_overrides):
    """Re-run this engine in --measure mode (no writes, no gate exit) and return
    (base_oe_per_share, implied_irr_weighted). --base-oe-ps is dropped: the impact
    measurement compares the engine-native bases of the two worlds."""
    args = [sys.executable, os.path.abspath(__file__)]
    argv = sys.argv[1:]
    i = 0
    while i < len(argv):
        if argv[i] == "--base-oe-ps":
            i += 2
            continue
        if argv[i] in ("--measure", "--ttm", "--base-judgment"):  # pin sources like --base-oe-ps: dropped
            i += 1
            continue
        args.append(argv[i])
        i += 1
    if "--price" not in argv and price is not None:
        args += ["--price", repr(price)]
    args.append("--measure")
    env = dict(os.environ)
    if no_overrides:
        env["DCF_NO_OVERRIDES"] = "1"
    try:
        out = subprocess.run(args, capture_output=True, text=True, timeout=600, env=env)
        txt = out.stdout or ""
        j = json.loads(txt[txt.index("{"):])
        return j.get("base_oe_per_share"), j.get("implied_irr_weighted")
    except Exception:
        return None, None

def _override_impact(ticker, price, headline_base, headline_irr):
    zb, zi = _measure_run(ticker, price, True)
    if "--base-oe-ps" in sys.argv or "--base-judgment" in sys.argv:
        # Any pin: replay the with-override world on the engine-native base too,
        # so both sides of this block are on the same (native) basis.
        fb, fi = _measure_run(ticker, price, False)
    else:
        fb, fi = headline_base, headline_irr
    return {"base_oe_per_share_zero_fill": zb, "base_oe_per_share_final": fb,
            "weighted_irr_zero_fill": zi, "weighted_irr_final": fi,
            "basis": "engine-native normalized base (median of last 3 FY) and weighted IRR, DCF run both ways (zero-fill baseline vs with-override); a --base-oe-ps TTM base or a --base-judgment payable base is excluded from both sides — its override effect shows in ttm.py output / make_score's payable_5y impact"}

def filer_sic(cik):
    """(sic, sicDescription) from EDGAR submissions — the authoritative industry
    code the payable-earnings rule is gated on (PAYABLE_SIC)."""
    try:
        sub = get_json(f"https://data.sec.gov/submissions/CIK{cik:010d}.json")
        return (str(sub.get("sic") or "") or None), (sub.get("sicDescription") or None)
    except Exception:
        return None, None

def filer_annual_form(cik):
    """The filer's most recent annual form (10-K / 20-F / 40-F) from EDGAR
    submissions — foreign-form filers need ADS-ratio handling (see ads_ratio)."""
    try:
        sub = get_json(f"https://data.sec.gov/submissions/CIK{cik:010d}.json")
        for f in sub.get("filings", {}).get("recent", {}).get("form", []):
            if f in ("10-K", "10-K/A", "20-F", "40-F"):
                return f.replace("/A", "")
    except Exception:
        pass
    return None

def get_json(url, headers=UA, timeout=90):
    last = None
    for attempt in range(3):  # simple retry with backoff on transient EDGAR/Nasdaq failures
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read())
        except Exception as e:
            last = e
            if attempt < 2: time.sleep(2 ** attempt)
    raise last

_fx_cache = {}
def fx_rate(ccy, date_str):
    """ccy->USD rate on date_str from frankfurter.app (ECB reference rates;
    returns the closest available business day). None when the currency is
    not ECB-covered or the fetch fails — the caller keeps the currency gap."""
    key = (ccy, date_str)
    if key in _fx_cache: return _fx_cache[key]
    rate = None
    try:
        d = get_json(f"https://api.frankfurter.app/{date_str}?from={ccy}&to=USD", timeout=30)
        rate = float(d["rates"]["USD"])
    except Exception:
        rate = None
    _fx_cache[key] = rate
    return rate

def nasdaq_price(ticker):
    try:
        d = get_json(f"https://api.nasdaq.com/api/quote/{ticker}/info?assetclass=stocks", headers={"User-Agent": "Mozilla/5.0"}, timeout=25)
        p = d.get("data", {}).get("primaryData", {}).get("lastSalePrice", "")
        return float(p.replace("$", "").replace(",", ""))
    except Exception:
        return None

# Codex review of PR #2 (HBAN FY2025: net debt read on 17.221B of debt while the
# statements pipeline shows 18.482B): the debt_total tags are of two kinds. A
# LONG-TERM total (LongTermDebt, LongTermDebtAndCapitalLeaseObligationsIncluding-
# CurrentMaturities) carries the current maturities of long-term debt but not
# the short-term borrowings a filer reports on their own line (debt_cur_st:
# ShortTermBorrowings / CommercialPaper / NotesPayableCurrent / IFRS
# ShorttermBorrowings), so those are added — never the current maturities,
# which are inside it. An aggregate of long- AND short-term debt
# (DebtLongtermAndShorttermCombinedAmount, IFRS Borrowings) stands alone.
# Debt feeds diagnostics only (net_debt_latest, HIGH_NET_DEBT / BIG_NET_CASH):
# no valuation input moves, so engine_release stays 5.4.0.
LT_DEBT_TOTAL_TAGS = frozenset({"LongTermDebt", "LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities"})


def debt_from_total_tag(tot, tot_tag, st=None, st_tag=None, same_unit=True):
    """(total debt, debt_tag) for a period whose only long-term figure is a
    debt_total tag; st = the short-term-borrowings component (debt_cur_st) and
    same_unit = whether it is in tot's unit after the FX pass (never added
    across currencies)."""
    if tot_tag in LT_DEBT_TOTAL_TAGS and st is not None:
        if same_unit:
            return tot + st, f"TOTAL:{tot_tag}+{st_tag}"
        return tot, f"TOTAL:{tot_tag} (short-term {st_tag} filed in another unit, not added)"
    return tot, f"TOTAL:{tot_tag}"


# ---------------------------------------------------------------------------
# v5.5 pure helpers — module level so ttm.py and the tests share ONE
# implementation (ttm.py imports the tag lists and capex_for_period /
# reconcile_sbc / the split helpers from here). None of them touch the
# network or the file system.
# ---------------------------------------------------------------------------
IF = "ifrs-full"

# Capex (decisions 3, 4, 5). A ROLL-UP is a PP&E total and is authoritative
# when filed; COMPONENTS are additive PP&E lines summed only when no roll-up
# reports the period; INTANGIBLE purchases are added on top of any PP&E leg
# except the IFRS COMBINED PP&E+intangibles tag, which already contains them.
CAPEX_ROLLUP_TAGS = ["PaymentsToAcquirePropertyPlantAndEquipment",
                     (IF, "PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities"),
                     (IF, "PurchaseOfPropertyPlantAndEquipment"),
                     (IF, "PurchaseOfPropertyPlantAndEquipmentIntangibleAssetsOtherThanGoodwillInvestmentPropertyAndOtherNoncurrentAssets")]
CAPEX_COMPONENT_TAGS = ["PaymentsToExploreAndDevelopOilAndGasProperties", "PaymentsToAcquireOilAndGasProperty",
                        "PaymentsToAcquireOtherPropertyPlantAndEquipment", "PaymentsForConstructionInProcess",
                        "PaymentsToAcquireProductiveAssets", "PaymentsToAcquireOtherProductiveAssets",
                        "PaymentsForCapitalImprovements"]
CAPEX_INTANGIBLE_TAGS = ["PaymentsToAcquireIntangibleAssets", "PaymentsToAcquireOtherIntangibleAssets",
                         (IF, "PurchaseOfIntangibleAssetsClassifiedAsInvestingActivities")]
CAPEX_COMBINED_TAGS = {"PurchaseOfPropertyPlantAndEquipmentIntangibleAssetsOtherThanGoodwillInvestmentPropertyAndOtherNoncurrentAssets"}
PRIMARY_ROLLUP = "PaymentsToAcquirePropertyPlantAndEquipment"
# The 5.4 first-tag-wins capex candidates: a period whose PP&E leg uses none of
# them had NO filed capex under 5.4 (an override filled it), so a value there
# is "now filed" for OVERRIDE_SUPERSEDED_BY_FILED_TAG:capex (WY: capital
# improvements newly read beneath a total-capex override).
CAPEX_TAGS_54 = frozenset({"PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsForConstructionInProcess",
                           "PaymentsToAcquireOtherPropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets",
                           "PaymentsToAcquireOtherProductiveAssets",
                           "PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities", "PurchaseOfPropertyPlantAndEquipment",
                           "PurchaseOfPropertyPlantAndEquipmentIntangibleAssetsOtherThanGoodwillInvestmentPropertyAndOtherNoncurrentAssets"})
# Share basis (decision 2).
SPLIT_RATIO_TAGS = ["StockholdersEquityNoteStockSplitConversionRatio1", "StockholdersEquityNoteStockSplitConversionRatio"]
DEI_MIN_COUNT = 10_000          # dei placeholders (FOX/FOXA 1, WMG 1,069, VOD 0) are not share counts
DEI_MAX_AGE_DAYS = 548          # a dei count older than 18 months before the latest FY end is stale
SHARE_SCALE_PRICE_MULT = 20     # ruling: base OE/share > 20x price is a scale defect
SHARE_SCALE_DEI_BAND = (1 / 100, 100)
SPLIT_CONFIRM_TOL = 0.15        # post-event dei / latest diluted within ±15% of the ratio (or its inverse)
SPLIT_COLLAPSE_DAYS = 180
DIVERGENCE_BAND = (0.75, 1.333)  # SHARE_BASIS_DIVERGENCE: dei / latest diluted outside 0.75x-1.333x (25% fewer or a third more)
# PP&E positivity for CAPEX_COVERAGE_LOW (sign only; not an engine series).
PPE_POSITIVE_TAGS = ["PropertyPlantAndEquipmentNet", "RealEstateInvestmentPropertyNet",
                     (IF, "PropertyPlantAndEquipment"), (IF, "InvestmentProperty")]


def _tag_name(t):
    """'Tag' or ('taxonomy', 'Tag') -> 'Tag'."""
    return t if isinstance(t, str) else t[1]


def _ratio_value(ads_ratio):
    """The ads_ratio as a float (accepts the engine's {ratio, ...} dict too); None when it does not apply."""
    if isinstance(ads_ratio, dict):
        ads_ratio = ads_ratio.get("ratio")
    if isinstance(ads_ratio, bool) or not isinstance(ads_ratio, (int, float)) or not ads_ratio:
        return None
    return ads_ratio


def normalized_oe_total(oe_ps, shares, ads_ratio):
    """oe_ps × shares ÷ ratio (per-ADS OE × ADS count) when a ratio applies, oe_ps × shares otherwise; None when shares
    is falsy or oe_ps is None. Same operation order as market_cap_est; ads_ratio is the dict or a plain number."""
    if oe_ps is None or not shares:
        return None
    r = _ratio_value(ads_ratio)
    return (oe_ps * shares) / r if r else oe_ps * shares


def latest_dei_count(dei_entries, latest_fy_end):
    """(value, date) of the latest usable dei EntityCommonStockSharesOutstanding: entries with val >= 10,000 and a date
    no earlier than latest_fy_end − 548 days (18 months); the latest (end, filed) wins; several facts sharing that
    (end, filed) are summed (class counts). (None, None) when nothing qualifies."""
    cutoff = None
    if latest_fy_end:
        try:
            cutoff = datetime.date.fromisoformat(str(latest_fy_end)) - datetime.timedelta(days=DEI_MAX_AGE_DAYS)
        except ValueError:
            cutoff = None
    groups = {}
    for e in dei_entries or []:
        try:
            v, end = e["val"], e["end"]
            d = datetime.date.fromisoformat(end)
        except (KeyError, TypeError, ValueError):
            continue
        if isinstance(v, bool) or not isinstance(v, (int, float)) or v < DEI_MIN_COUNT:
            continue
        if cutoff is not None and d < cutoff:
            continue
        groups.setdefault((end, e.get("filed") or ""), []).append(e)
    if not groups:
        return None, None
    key = max(groups)
    seen, total = set(), 0
    for e in groups[key]:
        sig = (e.get("accn"), e["val"])   # the same fact repeated in one filing is not a second class
        if sig not in seen:
            seen.add(sig)
            total += e["val"]
    return total, key[0]


PIN_LABELS = {"ttm_json": "the --ttm pin (ttm.json ttm_oe_per_share)", "base_oe_ps_arg": "the --base-oe-ps pin",
              "judgment_base_override": "the --base-judgment pin (payable-earnings base)"}


def share_scale_check(oe_ps_norm, price, shares_latest, dei_count, pin=None, pin_source=None):
    """{'defect': bool, 'tests': {'a': bool, 'b': bool}, 'reasons': [str], 'dei_ratio': shares_latest/dei or None,
        'pin_over_price': bool}
    (a) price and oe_ps_norm not None and abs(oe_ps_norm) > 20 × price        (VIV 168×, TEM 61×)
    (b) dei_count and shares_latest and not (1/100 <= shares_latest/dei_count <= 100)   (NTNX 0.00108, NVMI 0.00112)
    [ADDITION — verifier round 2, R2-PIN] test (a) on the base actually used: when a pin carries the base (`pin`, with
    `pin_source` 'ttm_json' / 'base_oe_ps_arg' / 'judgment_base_override'), price known and abs(pin) > 20 × price ->
    pin_over_price, a defect whatever the native median says (ruling 2: "base OE/share > 20x price"; a TTM leg filed in
    thousands made ttm.py's pin 73x the price on clean FY counts). No pin -> pin_over_price False, and the result is
    the 5.5 one."""
    tests, reasons = {"a": False, "b": False}, []
    dei_ratio = (shares_latest / dei_count) if (dei_count and shares_latest) else None
    if price and oe_ps_norm is not None and abs(oe_ps_norm) > SHARE_SCALE_PRICE_MULT * price:
        tests["a"] = True
        reasons.append(f"base OE/share {oe_ps_norm:,.2f} is {abs(oe_ps_norm) / price:,.0f}x the price {price:,.2f} "
                       f"(limit {SHARE_SCALE_PRICE_MULT}x)")
    if dei_ratio is not None and not (SHARE_SCALE_DEI_BAND[0] <= dei_ratio <= SHARE_SCALE_DEI_BAND[1]):
        tests["b"] = True
        reasons.append(f"latest diluted count {shares_latest:,.0f} is {dei_ratio:.6g}x the cover-page count "
                       f"{dei_count:,.0f} (outside 1/100-100x)")
    pin_over = bool(price and pin is not None and abs(pin) > SHARE_SCALE_PRICE_MULT * price)
    if pin_over:
        reasons.append(f"{PIN_LABELS.get(pin_source, 'the pinned base')} {pin:,.2f} is {abs(pin) / price:,.0f}x the price "
                       f"{price:,.2f} (limit {SHARE_SCALE_PRICE_MULT}x) — the base actually used")
    return {"defect": tests["a"] or tests["b"] or pin_over, "tests": tests, "reasons": reasons, "dei_ratio": dei_ratio,
            "pin_over_price": pin_over}


def pin_power_of_ten(native_base, pinned_base):
    """[ADDITION — verifier round 3, R3-CAP] 10^k (integer k != 0, |k| <= 9) when native_base / pinned_base is within
    2% of it, else None: DESIGN §2a's pin test, shared by scale_factor_for_cap and the engine's
    share_scale.pin_factor_withheld record."""
    if native_base is None or not pinned_base:
        return None
    ratio = native_base / pinned_base
    for k in range(-9, 10):
        if k and abs(ratio / 10 ** k - 1) <= 0.02:
            return 10 ** k
    return None


def scale_factor_for_cap(shares_latest, dei_count, native_base, pinned_base, window_counts=None):
    """(factor, basis): basis 'dei' when dei_count exists and shares_latest × 10^k is within 25% of dei_count for some
    integer k ≠ 0 (factor 10^k); else basis 'pin' when native_base / pinned_base is within 2% of 10^k, k ≠ 0
    (factor 10^k); else (None, None).
    [ADDITION — verifier round 3, R3-CAP; replaces round 2's R2-CAP] the pin's 10^k measures the scale of the count
    behind the native MEDIAN, while the factor multiplies the LATEST count, so the pin path applies only when
    `window_counts` — [(period, count)] from the earliest fiscal year whose OE/share defines the native median through
    the latest fiscal year (median_window_counts) — has the median year's count and the latest count on one scale
    (no more than 100x apart; see R4-CAP below). No window (None or
    empty) -> the pin is not consulted. Round 2's early return (a dei within 25% of the latest count -> no factor and
    the pin never consulted) is withdrawn: the window test withholds VIV's factor by itself (break FY2024 -> FY2025),
    and that return had "confirmed" a mis-scaled latest count when every count, the dei included, was filed in
    thousands (cap 1,000x small, a false HIGH_NET_DEBT 512.8x). Without the window test a correct latest count beside
    thousands-scaled median years (no dei, a dei 0.67x the count, a 20-F cover count in other units) took the pin's
    x1,000: a $3.0T cap for a $3.0B filer, in_scope_under_40b refused and net debt / OE 1,000x too small.
    [ADDITION — verifier round 4, R4-CAP] "on one scale" is tested on the window's two ENDPOINTS only — the median
    year's count and the latest count (median_latest_scale_breaks) — not on every adjacent pair: a year between them
    on another scale (filed on the true scale, or filled by a true-scale shares_override) says nothing about the
    latest count, and the round-3 adjacent-pair test withheld a correct x1,000 there (cap 1,000x too small)."""
    ks = [k for k in range(-9, 10) if k != 0]
    if dei_count and shares_latest:
        for k in ks:
            if abs(shares_latest * 10 ** k / dei_count - 1) <= 0.25:
                return 10 ** k, "dei"
    fac = pin_power_of_ten(native_base, pinned_base)
    if fac and window_counts and not median_latest_scale_breaks(window_counts):
        return fac, "pin"
    return None, None


def median_window_counts(oe_ps_hist, counts, latest_period):
    """[ADDITION — verifier round 3, R3-CAP] [(period, count)] of `counts` (the history's [(period, diluted count)])
    from the earliest fiscal year whose OE/share defines the native median through `latest_period` (the year whose
    count a cap factor multiplies). The defining years of oe_ps_hist[-3:]: with three values the year(s) holding the
    middle value, with two both (their mean is the median), with one that year. [] when oe_ps_hist is empty."""
    last3 = list(oe_ps_hist[-3:])
    if not last3 or not latest_period:
        return []
    if len(last3) == 3:
        med = statistics.median([v for _, v in last3])
        start = min(p for p, v in last3 if v == med)
    else:
        start = last3[0][0]
    return [(p, c) for p, c in counts if start <= p <= latest_period]


def _snap_pq(xf):
    """(p, q): the integers 1 <= p, q <= 10 with p/q within 1% of xf (the closest; the first found on a tie, so lowest
    terms), else None. The grid snap_split_ratio and split_label share."""
    best = None
    for p in range(1, 11):
        for q in range(1, 11):
            err = abs(xf / (p / q) - 1)
            if err <= 0.01 and (best is None or err < best[0]):
                best = (err, p, q)
    return (best[1], best[2]) if best else None


def snap_split_ratio(x):
    """p/q with integers 1 <= p, q <= 10 within 1% of x (0.333 → 1/3), else x."""
    try:
        xf = float(x)
    except (TypeError, ValueError):
        return x
    pq = _snap_pq(xf)
    return pq[0] / pq[1] if pq else x


def split_events_post_fy(split_entries, latest_fy_end):
    """[(event_date, ratio_filed)] from StockholdersEquityNoteStockSplitConversionRatio1 / …Ratio entries (unit pure,
    any form) whose context end is AFTER latest_fy_end, ratio != 1 and 0.01 <= ratio <= 100; same ratio within 180 days
    collapses to its first date. Facts dated on or before the latest FY end describe splits the annual filing already
    reflects (or annual re-disclosures — MLI, CSGP, DXCM, CFG, BWA, COKE) and are never events."""
    return _split_facts(split_entries, latest_fy_end, post_fy=True)


def _split_facts(split_entries, latest_fy_end, post_fy):
    """[(date, ratio_filed)]: split-ratio entries (unit pure, any form, ratio != 1, 0.01 <= ratio <= 100) whose context
    end is AFTER latest_fy_end (post_fy True) or ON / BEFORE it (post_fy False); the same ratio within 180 days
    collapses to its first date. Shared by split_events_post_fy and split_facts_in_history."""
    if not latest_fy_end:
        return []
    fy = datetime.date.fromisoformat(str(latest_fy_end))
    cands = []
    for e in split_entries or []:
        if e.get("unit") not in (None, "pure"):
            continue
        try:
            r, end = float(e["val"]), datetime.date.fromisoformat(e["end"])
        except (KeyError, TypeError, ValueError):
            continue
        if (end <= fy if post_fy else end > fy) or r == 1 or not (0.01 <= r <= 100):
            continue
        cands.append((end, r))
    events = []
    for end, r in sorted(cands):
        if any(abs(snap_split_ratio(r) - snap_split_ratio(er)) <= 1e-9 * max(1.0, abs(er))
               and 0 <= (end - ed).days <= SPLIT_COLLAPSE_DAYS for ed, er in events):
            continue
        events.append((end, r))
    return [(d.isoformat(), r) for d, r in events]


def confirm_split(events, shares_latest, dei_count, dei_date):
    """(event_date, ratio_used, evidence) for the latest event that a post-event dei confirms: dei_date > event_date and
    dei_count / shares_latest within ±15% of r (ratio_used = snap(r)) or of 1/r (ratio_used = snap(1/r)); else None.
    [READING — the ruling's "split-basis check against the latest dei"]: a dei count that sits within ±15% of the
    latest diluted count shows NO basis change, so it confirms nothing — a ratio near 1 (BWA's 1.13 spin-off
    conversion ratio, a small stock dividend) would otherwise be "confirmed" by ordinary buyback / issuance drift
    (BWA: dei / shares 0.941 vs 1/1.13 = 0.885) and rescale an already-consistent history. DD (0.322) and MLI
    (1.984) are unaffected."""
    if not events or not shares_latest or not dei_count or not dei_date:
        return None
    obs = dei_count / shares_latest
    if abs(obs - 1) <= SPLIT_CONFIRM_TOL:
        return None
    for ev_date, r in sorted(events, key=lambda ev: ev[0], reverse=True):
        if not datetime.date.fromisoformat(str(dei_date)) > datetime.date.fromisoformat(str(ev_date)):
            continue
        if abs(obs / r - 1) <= SPLIT_CONFIRM_TOL:
            used, matched = snap_split_ratio(r), "ratio"
        elif abs(obs * r - 1) <= SPLIT_CONFIRM_TOL:
            used, matched = snap_split_ratio(1 / r), "inverse"
        else:
            continue
        return ev_date, used, {"ratio_filed": r, "matched": matched, "dei_count": dei_count, "dei_date": dei_date,
                               "shares_latest": shares_latest, "dei_to_shares": obs}
    return None


def split_facts_in_history(split_entries, latest_fy_end):
    """[ADDITION — verifier round 1, ruling E11] [(date, ratio_filed)] for the split-ratio facts split_events_post_fy
    ignores: context end ON OR BEFORE latest_fy_end (same unit / ratio filters, same 180-day collapse of one ratio).
    Informational only (share_basis.in_history_split_facts) — nothing is rescaled: a history row sourced from a filing
    older than such a split can sit on the pre-split basis (TPL), a known limitation."""
    return _split_facts(split_entries, latest_fy_end, post_fy=False)


def split_label(ratio):
    """[ADDITION — verifier round 1, ruling E9] 'p-for-q' naming the split behind a multiplier: p/q (integers <= 10,
    lowest terms) within 1% of the ratio — snap_split_ratio's grid — else '1-for-round(1/r)' for a reverse split
    (0.05 -> '1-for-20', 1/15 -> '1-for-15') or 'round(r)-for-1'. The 5.5 text used limit_denominator(10), which
    printed '1-for-10' for a 1-for-20."""
    r = float(ratio)
    pq = _snap_pq(r)
    if pq:
        fr = Fraction(*pq)
        return f"{fr.numerator}-for-{fr.denominator}"
    return f"1-for-{round(1 / r)}" if r < 1 else f"{round(r)}-for-1"


SCALE_BREAK_MULT = 100   # [ADDITION — ruling E2] two adjacent fiscal-year share counts more than 100x apart


def share_series_scale_breaks(counts, limit=SCALE_BREAK_MULT):
    """[ADDITION — verifier round 1, ruling E2] [(period_from, count_from, period_to, count_to)] for every pair of
    ADJACENT entries of `counts` ([(period, count)], the share_cagr window — the last 4 fiscal-year counts) whose
    larger / smaller exceeds `limit` (VIV: 1,663,556,731,000 -> 1,658,604 -> 1,643,132 -> 3,195,606,352). A
    consistently scaled series (NTNX: every count in thousands) has none. Non-positive counts are skipped."""
    out = []
    for (p0, c0), (p1, c1) in zip(counts, counts[1:]):
        if not c0 or not c1 or c0 <= 0 or c1 <= 0:
            continue
        if max(c0, c1) / min(c0, c1) > limit:
            out.append((p0, c0, p1, c1))
    return out


def median_latest_scale_breaks(window_counts, limit=SCALE_BREAK_MULT):
    """[ADDITION — verifier round 4, R4-CAP] share_series_scale_breaks over the two ENDPOINTS of `window_counts`
    (median_window_counts: the earliest year whose OE/share defines the native median ... the latest year): [] when
    the median year's count and the latest count are within `limit`x of each other (one scale) or the window has
    fewer than two entries, else [(period_from, count_from, period_to, count_to)] for that one pair. The years between
    the endpoints do not enter: the pin's power of ten measures the median year's count and multiplies the latest
    (an alternating FY2023 2,000,000 -> FY2024 2,000,000,000 -> FY2025 2,000,000 series has both endpoints in
    thousands, so x1,000 is right for the latest count). Tied median years share one OE/share value, so they share
    the scale of the earliest."""
    if not window_counts or len(window_counts) < 2:
        return []
    return share_series_scale_breaks([window_counts[0], window_counts[-1]], limit)


def share_scale_pin_rescue(pin_source, pin, price, declared):
    """[ADDITION — verifier round 1, ruling E1] (rescues: bool, why_not: [str]). A share-scale defect is carried by a
    pin only when ALL hold: (1) the pin came from --base-oe-ps (pin_source 'base_oe_ps_arg' — a --ttm pin divides by
    the same mis-scaled counts, a --base-judgment pin is the payable shape); (2) judgment.json declares a base_override
    WITHOUT `basis` (`declared`: the judgment's base_override object, None when absent) whose value equals the pin
    within 0.1%; (3) the pin itself passes test (a): |pin| <= 20 x price when the price is known. 5.5 rescued ANY
    --base-oe-ps pin, so a mis-scaled TTM figure passed as a number scored where the same figure through --ttm gapped."""
    why = []
    if pin_source != "base_oe_ps_arg" or pin is None:
        return False, ["no --base-oe-ps pin"]
    ok_decl = (isinstance(declared, dict) and not declared.get("basis")
               and isinstance(declared.get("value"), (int, float)) and not isinstance(declared.get("value"), bool)
               and abs(float(declared["value"]) - pin) <= 0.001 * abs(pin))
    if not ok_decl:
        if not isinstance(declared, dict):
            why.append("judgment.json declares no base_override")
        elif declared.get("basis"):
            why.append(f"judgment.json's base_override has basis {declared.get('basis')!r} (the payable shape is pinned "
                       "through --base-judgment, never --base-oe-ps)")
        else:
            why.append(f"judgment.json's base_override value {declared.get('value')!r} does not equal the pin {pin:.6g} "
                       "within 0.1%")
    if price and abs(pin) > SHARE_SCALE_PRICE_MULT * price:
        why.append(f"the pin itself is {abs(pin) / price:,.0f}x the price {price:,.2f} (limit {SHARE_SCALE_PRICE_MULT}x) — "
                   "it inherits the mis-scaled counts")
    return not why, why


def _majority_unit(facts):
    """The unit carried by most facts (USD on a tie, else the first tied unit in list order)."""
    counts = {}
    for f in facts:
        counts[f[2]] = counts.get(f[2], 0) + 1
    if not counts:
        return None
    top = max(counts.values())
    tied = [u for u in counts if counts[u] == top]
    return "USD" if "USD" in tied else tied[0]


def _drop_equal_value_duplicates(facts, dropped):
    """The facts (tag, value, unit, filed) of one leg, one unit, minus the duplicates among DIFFERENT tags with
    non-zero values: a fact is dropped when a twin within 0.5% was filed LATER ('retag_duplicate' — the line was
    re-tagged, the newer filing wins; DESIGN §3-5), or when a twin with the IDENTICAL value sits in the SAME filing
    earlier in list order ('same_filing_duplicate' — one line tagged twice, IP FY2022 931,000,000 under both
    tags). Within one filing only identity counts: two different values the filer reports side by side are two
    disclosures (GLPI FY2022 23,865,000 / 23,864,000), never merged. Dropped facts are appended to `dropped`."""
    kept = []
    for i, f in enumerate(facts):
        reason = None
        if f[1] != 0:
            for k, g in enumerate(facts):
                if k == i or g[0] == f[0] or g[1] == 0 or abs(g[1] - f[1]) > 0.005 * max(abs(g[1]), abs(f[1])):
                    continue
                gf, ff = g[3] or "", f[3] or ""
                if gf > ff:
                    reason = "retag_duplicate"
                    break
                if gf == ff and k < i and g[1] == f[1]:
                    reason = "same_filing_duplicate"
            if reason:
                dropped.append((f[0], f[1], reason))
                continue
        kept.append(f)
    return kept


PARTS_OF_TOTAL_TOL = 0.005   # [ADDITION — ruling E5] a component within 0.5% of the sum of two or more others


def _drop_parts_of_total(facts, dropped):
    """[ADDITION — verifier round 1, ruling E5] The PP&E component facts (tag, value, unit, filed) of one period, one
    unit, minus the PARTS of a total: a component whose value equals the sum of two or more of the OTHER non-zero
    components within 0.5% is the filer's total line — it is kept and the parts are dropped (reason
    'parts_of_total'). GLPI FY2024: other PP&E 39,688,000 = construction in process 39,542,000 + capital improvements
    134,000 (+ an untagged 12,000) -> 39,688,000, not the 79,364,000 sum. Candidates are tried largest first; among
    the subsets that match, the closest sum wins (then the larger subset). No other near-equal rule is added: two
    components with no third (GLPI FY2025) stay summed."""
    live = list(range(len(facts)))
    for i in sorted(live, key=lambda k: -abs(facts[k][1])):
        if i not in live or facts[i][1] == 0:
            continue
        total = facts[i][1]
        others = [k for k in live if k != i and facts[k][1] != 0]
        best = None
        for size in range(2, len(others) + 1):
            for combo in combinations(others, size):
                diff = abs(sum(facts[k][1] for k in combo) - total)
                if diff <= PARTS_OF_TOTAL_TOL * abs(total) and (best is None or (diff, -size) < best[0]):
                    best = ((diff, -size), combo)
        if best:
            for k in best[1]:
                live.remove(k)
                dropped.append((facts[k][0], facts[k][1], "parts_of_total"))
    return [facts[k] for k in live]


CUMULATIVE_CONTEXT_DAYS = 380   # [ADDITION — ECHO] a context longer than this spans more than one fiscal year


def cumulative_context_values(facts, tags, units=None):
    """[ADDITION — ECHO] {(tag, unit, value)}: every NON-ZERO value a tag in `tags` ('Tag' or (taxonomy, 'Tag'))
    carries on a context longer than CUMULATIVE_CONTEXT_DAYS (end - start), from any filing; `units` limits the
    units read (ttm.py passes ('USD',)). capex_for_period drops an intangible fact whose (tag, unit, value) is in
    this set (reason 'cumulative_duplicate'): ECHO files PaymentsToAcquireIntangibleAssets 30,000,000,000 on its
    FY2024 annual context AND on 2008-01-01..2023-12-31 / 2018-01-01..2025-12-31 contexts — a cumulative spectrum
    total tagged as one year's purchases (capex 1,544,877,000 -> 31,544,877,000 against 1,252,697,000 of OCF).
    Shared by dcf_engine.py and ttm.py so the two never drift."""
    out = set()
    for t in tags:
        taxonomy, name = t if isinstance(t, tuple) else ("us-gaap", t)
        for unit_key, entries in ((facts.get("facts", {}).get(taxonomy, {}).get(name) or {}).get("units") or {}).items():
            if units is not None and unit_key not in units:
                continue
            for e in entries:
                start, end, val = e.get("start"), e.get("end"), e.get("val")
                if not start or not end or isinstance(val, bool) or not isinstance(val, (int, float)) or val == 0:
                    continue
                try:
                    span = (datetime.date.fromisoformat(end) - datetime.date.fromisoformat(start)).days
                except ValueError:
                    continue
                if span > CUMULATIVE_CONTEXT_DAYS:
                    out.add((name, unit_key, val))
    return out


def capex_for_period(rollups, components, intangibles, cumulative=None):
    """Per fiscal period. Each argument is a list of facts (tag, value, unit, filed) — the latest filing per tag for
    this period, in list order. Returns
    {'ppe': float|None, 'ppe_unit', 'ppe_tags': [...], 'ppe_source': 'rollup'|'components'|'components_mixed_filings'|None,
     'intangibles': float (0.0 when none), 'intangibles_unit', 'intangible_tags': [...],
     'dropped': [(tag, value, reason)], 'provenance': '+'.join(tags actually summed)}
    PP&E leg:
      - roll-up: the first roll-up fact in priority order with a non-zero value; a $0 roll-up is used only when no later
        candidate (roll-up or component) is non-zero — EXCEPT a $0 under PRIMARY_ROLLUP, which stays authoritative
        (ruling 3(a): the zero-guard covers non-primary candidates). When a roll-up is used, components are never added.
      - else components: sum the per-tag latest facts in ONE unit (the unit carried by most components, USD on a tie;
        other-unit facts dropped with reason 'unit'); drop an older-filed component whose value equals a newer-filed
        component of a DIFFERENT tag within 0.5% (reason 'retag_duplicate': IP 1,141M OtherPPE 2025 = ProductiveAssets
        2026). A $0 component contributes 0 and never blocks the others (zero-guard). Source 'components_mixed_filings'
        when the summed facts come from more than one filing date.
      - nothing → ppe None.
    Intangible leg: sum of intangible facts in one unit (same unit rule), added unless the PP&E leg's tag is in
    CAPEX_COMBINED_TAGS (then intangible_tags = [] and dropped gets reason 'combined_tag').
    [READING — design silent; ruling 5's "never double-counted"] the equal-value rule also covers two DIFFERENT tags
    carrying the IDENTICAL non-zero value in the SAME filing: one cash-flow line tagged twice (IP FY2022:
    PaymentsToAcquireOtherPropertyPlantAndEquipment and PaymentsToAcquireProductiveAssets both 931,000,000 in the
    2024-02-16 and 2025-02-21 10-Ks) counts once — the first in list order is kept, the other dropped with reason
    'same_filing_duplicate'. Applied to the component and the intangible legs alike.
    [ADDITION — ECHO] `cumulative` (cumulative_context_values over the intangible tags; None = no check): an
    intangible fact whose (tag, unit, value) the same tag also carries on a context longer than 380 days is a
    cumulative figure on an annual context — dropped with reason 'cumulative_duplicate' before the unit rule.
    Intangible leg only (new in 5.5, so no 5.4 number moves); the PP&E legs are never checked.
    [ADDITION — ruling E5] after the equal-value rule, a component equal within 0.5% to the sum of two or more other
    non-zero components is the total: kept, the parts dropped ('parts_of_total' — _drop_parts_of_total).
    [ADDITION — ruling E6] a negative intangible fact is dropped ('negative'); a $0 intangible fact is ignored — it
    joins neither intangible_tags nor the provenance string."""
    def norm(fs):
        return [(_tag_name(f[0]), f[1], f[2], f[3] if len(f) > 3 else None)
                for f in (fs or []) if f is not None and f[1] is not None]
    rollups, components, intangibles = norm(rollups), norm(components), norm(intangibles)
    out = {"ppe": None, "ppe_unit": None, "ppe_tags": [], "ppe_source": None,
           "intangibles": 0.0, "intangibles_unit": None, "intangible_tags": [],
           "dropped": [], "provenance": ""}
    # ---- PP&E leg: roll-up first ----
    chosen = None
    for i, f in enumerate(rollups):
        if f[1] != 0 or f[0] == PRIMARY_ROLLUP:
            chosen = f
            break
        later_nonzero = any(g[1] != 0 for g in rollups[i + 1:]) or any(c[1] != 0 for c in components)
        if not later_nonzero:
            chosen = f
            break
        out["dropped"].append((f[0], f[1], "zero_guard"))
    if chosen is not None:
        out.update(ppe=chosen[1], ppe_unit=chosen[2], ppe_tags=[chosen[0]], ppe_source="rollup")
    elif components:
        unit = _majority_unit(components)
        same_unit = []
        for f in components:
            if f[2] != unit:
                out["dropped"].append((f[0], f[1], "unit"))
            else:
                same_unit.append(f)
        summed = _drop_equal_value_duplicates(same_unit, out["dropped"])
        summed = _drop_parts_of_total(summed, out["dropped"])   # [ADDITION — ruling E5]
        total = 0
        for f in summed:
            total += f[1]
        out.update(ppe=total, ppe_unit=unit, ppe_tags=[f[0] for f in summed],
                   ppe_source="components_mixed_filings" if len({f[3] for f in summed}) > 1 else "components")
    # ---- intangible leg ----
    # [ADDITION — verifier round 1, ruling E6] a NEGATIVE intangible fact is dropped (reason 'negative': FTAI FY2019
    # -606,000, PHG FY2016 EUR -95M lowered capex); a $0 fact contributes nothing and joins nothing — not
    # intangible_tags, not the provenance string, not an 'intangibles not added' note (169 periods / 67 folders
    # carried a $0 tag in capex_tag). The PP&E legs keep their 5.4 semantics.
    _neg = [f for f in intangibles if f[1] < 0]
    out["dropped"].extend((f[0], f[1], "negative") for f in _neg)
    intangibles = [f for f in intangibles if f[1] > 0]
    if intangibles:
        if out["ppe_tags"] and out["ppe_tags"][0] in CAPEX_COMBINED_TAGS:
            out["dropped"].extend((f[0], f[1], "combined_tag") for f in intangibles)
        else:
            live = []
            for f in intangibles:
                if cumulative and (f[0], f[2], f[1]) in cumulative:
                    out["dropped"].append((f[0], f[1], "cumulative_duplicate"))   # [ADDITION — ECHO]
                    continue
                live.append(f)
            if live:
                unit = _majority_unit(live)
                same_unit = []
                for f in live:
                    if f[2] != unit:
                        out["dropped"].append((f[0], f[1], "unit"))
                        continue
                    same_unit.append(f)
                total = 0.0
                for f in _drop_equal_value_duplicates(same_unit, out["dropped"]):
                    total += f[1]
                    out["intangible_tags"].append(f[0])
                out.update(intangibles=total, intangibles_unit=unit)
    out["provenance"] = "+".join(out["ppe_tags"] + out["intangible_tags"])
    return out


SBC_SHARE_TAG, SBC_ALLOCATED_TAG = "ShareBasedCompensation", "AllocatedShareBasedCompensationExpense"


def reconcile_sbc(share, allocated):
    """share, allocated: (value, unit) or None. Returns (value, unit, tag_used, reconciled: bool, note).
    Both present, SAME unit, allocated > share → (allocated, unit, 'AllocatedShareBasedCompensationExpense', True, …).
    Different units → share kept, note 'unit_mismatch' (JD/BEKE/LI/HTHT: USD translation vs CNY — never reconciled).
    Otherwise share kept (or allocated when share is absent — today's fallback)."""
    if share is None or share[0] is None:
        if allocated is not None and allocated[0] is not None:
            return allocated[0], allocated[1], SBC_ALLOCATED_TAG, False, "allocated_only"
        return None, None, None, False, None
    sv, su = share[0], share[1]
    if allocated is None or allocated[0] is None:
        return sv, su, SBC_SHARE_TAG, False, None
    av, au = allocated[0], allocated[1]
    if au != su:
        return sv, su, SBC_SHARE_TAG, False, "unit_mismatch"
    if av > sv:
        pct = f", +{(av / sv - 1) * 100:.1f}%" if sv else ""
        return av, au, SBC_ALLOCATED_TAG, True, f"allocated {av:,.0f} > share {sv:,.0f} {au}{pct}"
    return sv, su, SBC_SHARE_TAG, False, "share_ge_allocated"


def override_currency_basis(o, fx_info, last_filed_unit):
    """'shares' | 'no_fx' (no fx_info: used verbatim as today) | 'declared_usd' (o.currency == 'USD' and kind 'filing') |
    'last_filed_unit_usd' (last_filed_unit == 'USD') | 'converted'."""
    o = o or {}
    if o.get("field") == "shares" or last_filed_unit == "shares":
        return "shares"
    if not fx_info:
        return "no_fx"
    if str(o.get("currency") or "").strip().upper() == "USD" and o.get("kind") == "filing":
        return "declared_usd"
    if last_filed_unit == "USD":
        return "last_filed_unit_usd"
    return "converted"


def _num(x):
    """float(x) for a number or numeric CSV string; None for blanks / non-numbers."""
    if isinstance(x, bool) or x is None:
        return None
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def capex_coverage_low(rows_last3, ppe_positive):
    """(bool, detail_str). True when, for EACH of the last 3 fiscal-year rows, total capex and D&A are present,
    D&A > 0 and capex / D&A < 0.5, at a filer whose latest PP&E is positive (ppe_positive True; None = unknown → no
    flag). detail_str lists the ratios ('FY2023 12%, FY2024 9%, FY2025 11%')."""
    rows = list(rows_last3 or [])[-3:]
    if len(rows) < 3 or not ppe_positive:
        return False, ""
    parts = []
    for r in rows:
        capex, da = _num(r.get("capex")), _num(r.get("da"))
        if capex is None or da is None or da <= 0 or capex / da >= 0.5:
            return False, ""
        label = r.get("fy_label") or str(r.get("period_end") or "")[:4]
        parts.append(f"FY{label} {capex / da * 100:.0f}%")
    return True, ", ".join(parts)


def _ppe_positive(facts):
    """True when the latest annual instant value of any PP&E tag in PPE_POSITIVE_TAGS is > 0, False when they are all
    <= 0, None when none is filed (unknown PP&E → CAPEX_COVERAGE_LOW stays silent). Sign only: no FX needed."""
    latest = []
    for t in PPE_POSITIVE_TAGS:
        vals = period_series(facts, [t], False)[0]
        if vals:
            latest.append(vals[max(vals)])
    if not latest:
        return None
    return any(v is not None and v > 0 for v in latest)


def scale_growth_note(share_scale):
    """[ADDITION — ruling E2] '' or the clause SHARE_SCALE_SUSPECT / DATA_GAP:shares — SHARE_SCALE append when the
    share-derived growth inputs were dropped (share_scale.growth_inputs_dropped / .scale_breaks)."""
    brk = share_scale.get("scale_breaks") or []
    if not brk:
        return ""
    vals = share_scale.get("growth_inputs_dropped_values") or {}
    names = {"share_cagr": "the share-count CAGR", "oe_ps_cagr_2y": "the OE/share CAGR"}
    dropped = [f"{names.get(k, k)} ({vals[k] * 100:+.1f}%/yr)" if isinstance(vals.get(k), (int, float)) else names.get(k, k)
               for k in share_scale.get("growth_inputs_dropped") or []]
    where = ", ".join(f"FY{b['from_period'][:4]} {b['from_count']:,.0f} -> FY{b['to_period'][:4]} {b['to_count']:,.0f}" for b in brk)
    # [ADDITION — verifier round 2, R2-E2] an OE/share CAGR whose endpoints share one scale stays
    # ([ADDITION — verifier round 4, R4-E2] the endpoints' counts are compared, so a break between them that the
    # CAGR never reads — an alternating series — does not drop it)
    kept = ("; the OE/share CAGR reads only its two endpoints, whose counts are on one scale, so it stays in the blend"
            if "oe_ps_cagr_2y" in (share_scale.get("growth_inputs_kept") or []) else "")
    if not dropped:
        return (f"; the share-count series breaks scale inside the growth window ({where}) (no share-derived growth "
                f"input to drop){kept}")
    return (f"; the share-count series breaks scale inside the growth window ({where}), so " + " and ".join(dropped)
            + (" was" if len(dropped) == 1 else " were") + f" dropped from the growth blend (share adjustment 0){kept}")


def _v55_flags(share_scale, share_basis, pin, market_cap_basis, sbc_recon, periods, hist, facts, overrides,
               capex_assembly, raw_missing, last3_periods, override_checks):
    """The v5.5 fragility flags that do not depend on the scenario math (main() appends them to flags_pre, so Tier F
    and DATA_GAP runs carry them too): SHARE_SCALE_SUSPECT, SHARE_BASIS_ADJUSTED, SHARE_BASIS_DIVERGENCE,
    SBC_TAG_RECONCILED, CAPEX_COVERAGE_LOW, OVERRIDE_SUPERSEDED_BY_FILED_TAG:capex. The last one fires only for a
    last-3-FY period whose PP&E leg is NOW filed (none of its tags was a 5.4 candidate, so 5.4 filled it from the
    override) and records override_checks['capex']['superseded_periods']."""
    flags = []
    if share_scale["defect"] and share_scale["rescued_by_pin"]:
        if not market_cap_basis.get("shares_used"):
            # no price (or no count): the cap is universe.csv's — no share count was multiplied
            basis = (f"universe.csv's market cap (no price × shares; the scale factor found was "
                     f"{share_scale['scale_factor'] or 'none'})")
        elif share_scale["scale_factor"]:
            basis = (f"the latest diluted count x {share_scale['scale_factor']:g} ({share_scale['factor_basis']} basis: "
                     f"{market_cap_basis['shares_used']:,.0f} shares)")
        else:
            _dr = share_scale.get("dei_ratio")
            _wh = share_scale.get("pin_factor_withheld")
            # [ADDITION — verifier round 4, R4-E3] no "agrees" reassurance when that agreement verifies nothing
            agree = ("the cover-page count agrees with it within 25%; "
                     if (_dr is not None and abs(_dr - 1) <= 0.25 and not share_scale.get("leverage_unverifiable"))
                     else "")
            if _wh:   # [ADDITION — verifier round 3, R3-CAP] a power-of-ten pin ratio withheld by a scale break
                brk = ", ".join(f"FY{b['from_period'][:4]} {b['from_count']:,.0f} -> FY{b['to_period'][:4]} "
                                f"{b['to_count']:,.0f}" for b in _wh["breaks"])
                why = (f"the pin's x{_wh['factor']:g} ratio to the native base measures the count behind the "
                       f"FY{_wh['window'][0]['period'][:4]} median, which is on another scale than the latest count "
                       f"({brk}), so it does not apply")
            else:
                why = "no power-of-ten factor found in the dei count or the pin"
            basis = f"the latest diluted count as filed ({agree}{why})"
        # [ADDITION — ruling E3] no factor and no cover-page count to test the latest diluted count against;
        # [ADDITION — verifier round 2, R2-E3] or a cover-page count that the latest diluted count fails (test (b))
        if not share_scale.get("leverage_unverifiable"):
            lev = ""
        elif share_scale.get("dei_ratio") is not None and not share_scale["tests"].get("b"):
            # [ADDITION — verifier round 4, R4-E3] a dei that passed test (b) against a latest count on the median
            # year's (mis-scaled) basis
            lev = (f"; the cover-page count {share_scale['dei_count']:,.0f} ({share_scale['dei_date']}) agrees with the "
                   f"latest diluted count ({share_scale['dei_ratio']:.6g}x), but that count is on the same scale as the "
                   "count behind the native median, which test (a) found mis-scaled, so the cover page is filed on the "
                   "same basis and verifies nothing; with no power-of-ten factor the cap basis and the leverage "
                   "diagnostics are unverifiable — net_debt_to_normalized_oe was not computed and HIGH_NET_DEBT / "
                   "BIG_NET_CASH were not tested")
        elif share_scale.get("dei_ratio") is not None:
            lev = (f"; the cover-page count {share_scale['dei_count']:,.0f} ({share_scale['dei_date']}) puts the latest "
                   f"diluted count at {share_scale['dei_ratio']:.6g}x it (test (b) failed) and no power-of-ten factor "
                   "reconciles them, so the cap basis and the leverage diagnostics are unverifiable — "
                   "net_debt_to_normalized_oe was not computed and HIGH_NET_DEBT / BIG_NET_CASH were not tested")
        else:
            lev = ("; with no cover-page count to test the latest diluted count and no power-of-ten factor, the cap basis "
                   "and the leverage diagnostics are unverifiable — net_debt_to_normalized_oe was not computed and "
                   "HIGH_NET_DEBT / BIG_NET_CASH were not tested")
        flags.append(f"SHARE_SCALE_SUSPECT: {'; '.join(share_scale['reasons'])}; the declared base_override pin "
                     f"{pin:.6g} carries the base; market cap uses {basis}{lev}{scale_growth_note(share_scale)}")
    split = share_basis.get("split")
    if split and split["periods_adjusted"]:
        # [ADDITION — ruling E9] the split named from its own ratio (a 1-for-20 printed as 1-for-10 under
        # limit_denominator(10)) and the adjusted years listed one by one, OVERRIDE counts named as not rescaled
        ov = split.get("periods_override_not_rescaled") or []
        ov_s = (f" except {', '.join('FY' + p[:4] for p in ov)} (OVERRIDE count{'s' if len(ov) > 1 else ''}, not rescaled)"
                if ov else "")
        flags.append(f"SHARE_BASIS_ADJUSTED: {split_label(split['ratio_used'])} split (filed ratio {split['ratio_filed']:g}, "
                     f"effective {split['event_date']}) post-dates the filings behind "
                     f"{', '.join('FY' + p[:4] for p in split['periods_adjusted'])}{ov_s}; their share "
                     f"counts were multiplied by {split['ratio_used']:.6g} so the history and the current price share one basis "
                     f"(dei {split['dei_count']:,.0f} on {split['dei_date']} confirms"
                     # [ADDITION — verifier round 3, R3-SPLIT] confirmed against an earlier filed year when the latest
                     # FY's count is an OVERRIDE
                     + (f" against the FY{split['confirmed_against_period'][:4]} filed count"
                        if (split.get("confirmed_against_period") and hist
                            and split["confirmed_against_period"] != hist[-1]["period_end"]) else "") + ")")
    div = share_basis.get("divergence")
    if div and div["applied"]:
        flags.append(f"SHARE_BASIS_DIVERGENCE: the latest cover-page share count {div['dei_count']:,.0f} ({div['dei_date']}) differs "
                     f"from the latest diluted count {div['shares_latest']:,.0f} by x{div['dei_to_shares']:.3f} and no filed split "
                     "ratio explains it (issuance, a merger or an unfiled split since the fiscal year end); market cap uses the "
                     "cover-page count, per-share history stays on the filed basis — check the latest 10-Q")
    parts = []
    for p in periods:
        r = sbc_recon.get(p)
        if r and r["reconciled"]:
            s, a, u = r["share"][0], r["allocated"][0], r["share"][1]
            pct = f", +{(a / s - 1) * 100:.1f}%" if s else ""
            parts.append(f"FY{p[:4]} ({s:,.0f} vs {a:,.0f}{'' if u == 'USD' else ' ' + str(u)}{pct})")
    if parts:
        flags.append("SBC_TAG_RECONCILED: AllocatedShareBasedCompensationExpense exceeds ShareBasedCompensation for "
                     + ", ".join(parts) + "; the Allocated figure was used — the Share tag carries only part of stock "
                     "compensation at this filer (a difference under 1% is tag rounding and needs one line in the analysis)")
    low, detail = capex_coverage_low(hist[-3:], _ppe_positive(facts))
    if low:
        flags.append(f"CAPEX_COVERAGE_LOW: capex is below 50% of D&A in each of the last 3 fiscal years ({detail}) at a filer "
                     "with positive PP&E — reconcile total capex against the cash-flow statement's investing section "
                     "(construction in progress, capitalised software, land-use rights, spectrum, intangible purchases) "
                     "before trusting the owner's-earnings base")
    o = overrides.get("capex")
    if o:
        sup = []
        for p in last3_periods:
            asm = capex_assembly.get(p)
            if p in raw_missing["capex"] or not asm or asm["ppe"] is None:
                continue
            if any(t in CAPEX_TAGS_54 for t in asm["ppe_tags"]):
                continue   # filed under 5.4 as well: the override never filled this period, nothing was superseded
            filed = asm["ppe"]
            off = (o["value"] != 0) if filed == 0 else not (0.5 <= o["value"] / filed <= 2)
            if off:
                sup.append({"period": p, "override": o["value"], "filed_ppe": filed, "filed_unit": asm["ppe_unit"],
                            "filed_tags": "+".join(asm["ppe_tags"])})
        if sup:
            override_checks.setdefault("capex", {})["superseded_periods"] = sup
            flags.append("OVERRIDE_SUPERSEDED_BY_FILED_TAG:capex — judgment.json capex_override "
                         f"{o['value']:,.0f} is outside 0.5x-2x of the PP&E capex now FILED for "
                         + ", ".join(f"FY{s['period'][:4]} ({s['filed_ppe']:,.0f} {s['filed_unit']}, {s['filed_tags']})" for s in sup)
                         + "; the filed value is used there (an override never replaces a filed value), so the override fills "
                         "nothing — reconcile it against the cash-flow statement and remove it or justify it in analysis.md")
    return flags


def period_series(facts, tags, duration=True, with_filed=False):
    """({period_end: value}, first_used_tag, {period_end: tag}, {period_end: unit}) —
    annual periods only, latest filing wins. v4: MERGES across candidate tags per
    period (in priority order). v3 returned only the first tag that had any data,
    silently truncating history when a filer switched tags. v5: also returns which
    tag supplied each period (provenance — the audit found used_tags hiding years
    that were silently zero-filled). v5.3: `tags` items are either "Tag" (us-gaap)
    or ("taxonomy", "Tag") pairs, merged across taxonomies in priority order;
    values stay in their filed unit and the unit used per period is returned so
    the caller can FX-convert non-USD periods. v5.5: with_filed=True returns a
    5th dict {period_end: filed date of the supplying fact} (the share series
    for the split-basis cutoff and the capex / SBC leg builders use it); the
    default keeps the 4-tuple API."""
    merged, used, tag_by_period, unit_by_period, filed_by_period = {}, None, {}, {}, {}
    pairs = [(t if isinstance(t, tuple) else ("us-gaap", t)) for t in tags]
    for taxonomy, tag in pairs:
        tax_facts = facts.get("facts", {}).get(taxonomy, {})
        if tag not in tax_facts: continue
        units = tax_facts[tag].get("units", {})
        # v5.3.1 (Codex review of Stocks PR #1): units merge PER PERIOD, in
        # preference order — v5.3 picked ONE unit per tag, so a tag with USD
        # facts for some years and local-currency facts for others silently
        # dropped the local-only years. USD wins a period when it has one;
        # other units fill the periods USD lacks, with the unit recorded.
        pref = [u for u in ("USD", "shares", "USD/shares") if u in units]
        pref += [u for u in units if u not in pref]
        for unit_key in pref:
            best = {}
            for e in units[unit_key]:
                if e.get("fp") != "FY": continue
                if e.get("form", "") not in ("10-K", "10-K/A", "20-F", "40-F"): continue
                end = e.get("end"); start = e.get("start")
                if not end: continue
                if duration:
                    if not start: continue
                    days = (datetime.date.fromisoformat(end) - datetime.date.fromisoformat(start)).days
                    if not (330 <= days <= 380): continue
                else:
                    if start and start != end: continue
                prev = best.get(end)
                if prev is None or e.get("filed", "") > prev.get("filed", ""):
                    best[end] = e
            for k, v in best.items():
                if k not in merged:
                    merged[k] = v["val"]
                    tag_by_period[k] = tag
                    unit_by_period[k] = unit_key
                    filed_by_period[k] = v.get("filed")
                    if used is None: used = tag
    if with_filed:
        return merged, used, tag_by_period, unit_by_period, filed_by_period
    return merged, used, tag_by_period, unit_by_period


def annual_facts_by_unit(facts, tag, duration=True):
    """{(period_end, unit): (value, filed)} for ONE tag ('Tag' or (taxonomy, 'Tag')) under period_series' filters
    (fp FY, annual forms, 330-380 day durations / instants, latest filing per period) but keeping EVERY unit —
    v5.5 SBC reconciliation compares two tags only within the same unit (JD files Share in USD translations and
    Allocated in CNY only)."""
    taxonomy, name = tag if isinstance(tag, tuple) else ("us-gaap", tag)
    units = (facts.get("facts", {}).get(taxonomy, {}).get(name) or {}).get("units", {})
    out = {}
    for unit_key, entries in units.items():
        best = {}
        for e in entries:
            if e.get("fp") != "FY" or e.get("form", "") not in ("10-K", "10-K/A", "20-F", "40-F"):
                continue
            end, start = e.get("end"), e.get("start")
            if not end:
                continue
            if duration:
                if not start:
                    continue
                days = (datetime.date.fromisoformat(end) - datetime.date.fromisoformat(start)).days
                if not (330 <= days <= 380):
                    continue
            elif start and start != end:
                continue
            prev = best.get(end)
            if prev is None or e.get("filed", "") > prev.get("filed", ""):
                best[end] = e
        for end, e in best.items():
            out[(end, unit_key)] = (e["val"], e.get("filed"))
    return out

def main():
    ticker = sys.argv[1].upper()
    price_arg = float(sys.argv[sys.argv.index("--price") + 1]) if "--price" in sys.argv else None

    uni = {}
    with open(f"{SYS}/universe.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f): uni[row["ticker"]] = row
    sec = json.load(open(f"{SYS}/sec_tickers_exchange.json", encoding="utf-8"))
    cik_by_ticker = {}
    for rec in sec["data"]: cik_by_ticker.setdefault(rec[2].upper(), rec[0])
    cik = None
    if "--cik" in sys.argv:  # agent-supplied override for entity/CIK-change cases (see NO_DATA)
        cik = int(sys.argv[sys.argv.index("--cik") + 1])
    else:
        for cand in (ticker, ticker.replace("/", "-"), ticker.replace("/", ".")):
            if cand in cik_by_ticker: cik = cik_by_ticker[cand]; break
    if cik is None and ticker in uni and uni[ticker].get("cik"): cik = int(uni[ticker]["cik"])
    if cik is None: print(f"NO_CIK for {ticker}"); sys.exit(2)

    facts = get_json(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json")
    name = facts.get("entityName", (uni.get(ticker) or {}).get("name", ticker))
    cik_fallback_note = None
    # v4.1: CIK/entity trap (found on XOM): the tickers file can map a ticker to a NEW holding-
    # company CIK with no filing history (2026: XOM -> ExxonMobil Holdings Corp, CIK 2115436,
    # while all history sits under CIK 34088). If the primary CIK yields <3 years of net income,
    # probe the older company_tickers.json mapping and use whichever CIK has more history.
    def _ni_periods(f):
        s, _, _, _ = period_series(f, ["NetIncomeLoss", "ProfitLoss", ("ifrs-full", "ProfitLoss")], True)
        return len(s)
    if _ni_periods(facts) < 3:
        try:
            alt_list = get_json("https://www.sec.gov/files/company_tickers.json")
            alt_cik = None
            for rec in alt_list.values():
                if rec.get("ticker", "").upper() == ticker: alt_cik = int(rec["cik_str"]); break
            if alt_cik and alt_cik != cik:
                alt_facts = get_json(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{alt_cik:010d}.json")
                if _ni_periods(alt_facts) > _ni_periods(facts):
                    cik_fallback_note = f"CIK_FALLBACK: tickers_exchange CIK {cik} ({name}) has thin history; used CIK {alt_cik} ({alt_facts.get('entityName')}) instead — verify this is the right operating parent"
                    facts, cik = alt_facts, alt_cik
                    name = facts.get("entityName", name)
        except Exception:
            pass

    # v5.3: each field's candidates are us-gaap tags first, then ("ifrs-full", tag)
    # pairs — period_series merges across both in this priority order. IFRS picks
    # verified against real companyfacts pulls (CCJ / TECK / GFI) 2026-10-14:
    # AdjustedWeightedAverageShares is the DILUTED denominator (one value per
    # period, consistently just above basic WeightedAverageShares);
    # AdjustmentsFor* are the cash-flow-statement addbacks, the same role the
    # us-gaap ShareBasedCompensation / DDA tags play.
    IF = "ifrs-full"
    dur_defs = {
        "revenue": ["RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet", "Revenues", "RevenueFromContractWithCustomerIncludingAssessedTax",
                    (IF, "Revenue"), (IF, "RevenueFromContractsWithCustomers")],
        "net_income": ["NetIncomeLoss", "ProfitLoss", (IF, "ProfitLoss")],
        "operating_income": ["OperatingIncomeLoss", (IF, "ProfitLossFromOperatingActivities")],
        # v5.2: continuing-operations OCF as fallback — a filer tagging OCF only
        # there previously produced oe_cons = None and a fake Tier F (round-2).
        "ocf": ["NetCashProvidedByUsedInOperatingActivities", "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
                (IF, "CashFlowsFromUsedInOperatingActivities"), (IF, "CashFlowsFromUsedInOperatingActivitiesContinuingOperations")],
        # v5: construction-in-process (ED files capex there FY23+) and other-productive-assets
        # (ROP) added as fallbacks — both verified against real companyfacts pulls 2026-10-13.
        # v5.5: capex is no longer a first-tag-wins merge. The PP&E leg is assembled per
        # period by capex_for_period (roll-up authoritative, else the additive components
        # SUMMED, zero-guarded) and intangible purchases ride on top — see the assembly
        # below the series loop. This entry only lists the PP&E candidates.
        "capex": CAPEX_ROLLUP_TAGS + CAPEX_COMPONENT_TAGS,
        "da": ["DepreciationDepletionAndAmortization", "DepreciationAmortizationAndAccretionNet", "DepreciationAndAmortization", "Depreciation",
               (IF, "AdjustmentsForDepreciationAndAmortisationExpense"), (IF, "DepreciationAndAmortisationExpense")],
        # v5: DFTX and many others file SBC only under the allocated tag.
        "sbc": ["ShareBasedCompensation", "AllocatedShareBasedCompensationExpense",
                (IF, "AdjustmentsForSharebasedPayments"), (IF, "ExpenseFromSharebasedPaymentTransactionsWithEmployees")],
        "tax": ["IncomeTaxExpenseBenefit", (IF, "IncomeTaxExpenseContinuingOperations"), (IF, "IncomeTaxExpense")],
        "shares_diluted": ["WeightedAverageNumberOfDilutedSharesOutstanding", "WeightedAverageNumberOfSharesOutstandingDiluted", "WeightedAverageNumberOfSharesOutstandingBasic",
                           (IF, "AdjustedWeightedAverageShares"), (IF, "WeightedAverageShares")],
    }
    inst_defs = {
        "cash": ["CashAndCashEquivalentsAtCarryingValue", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents", (IF, "CashAndCashEquivalents")],
        # Codex review of PR #2: the combined cash+restricted fallback must not be
        # netted against debt as if it were free — restricted cash is tracked and
        # subtracted when tagged, flagged when not (see the per-period loop).
        "restricted_cash": ["RestrictedCashAndCashEquivalents", "RestrictedCash", "RestrictedCashAndCashEquivalentsAtCarryingValue",
                            "RestrictedCashCurrent", (IF, "RestrictedCashAndCashEquivalents")],
        "assets_current": ["AssetsCurrent", (IF, "CurrentAssets")],
        "liab_current": ["LiabilitiesCurrent", (IF, "CurrentLiabilities")],
        # v5.4 debt: CURRENT and NONCURRENT candidate lists hold only tags of
        # that classification; TOTAL tags (LongTermDebt includes current
        # maturities; the audit found it stacking on DebtCurrent) live in
        # debt_total and are used only when no noncurrent tag reports.
        # Codex review of PR #2: current debt is an AGGREGATE tag when filed; when
        # it is not, the components are ADDITIVE (current maturities of long-term
        # debt + short-term borrowings) and must be summed, not treated as
        # fallbacks that keep only the first one present. Within each component
        # group the tags are alternatives (one of them per period).
        "debt_current": ["DebtCurrent", (IF, "CurrentBorrowingsAndCurrentPortionOfNoncurrentBorrowings")],
        "debt_cur_ltd": ["LongTermDebtAndCapitalLeaseObligationsCurrent", "LongTermDebtCurrent", (IF, "CurrentPortionOfLongtermBorrowings")],
        "debt_cur_st": ["ShortTermBorrowings", "CommercialPaper", "NotesPayableCurrent", (IF, "ShorttermBorrowings")],
        "debt_lt": ["LongTermDebtNoncurrent", "LongTermDebtAndCapitalLeaseObligations", "LongTermNotesPayable",
                    (IF, "LongtermBorrowings"), (IF, "NoncurrentPortionOfNoncurrentBorrowings")],
        "debt_total": ["LongTermDebt", "DebtLongtermAndShorttermCombinedAmount", "LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities",
                       (IF, "Borrowings")],
        "lease_liab_current": ["OperatingLeaseLiabilityCurrent", (IF, "CurrentLeaseLiabilities")],
        "lease_liab_lt": ["OperatingLeaseLiabilityNoncurrent", (IF, "NoncurrentLeaseLiabilities")],
        "assets": ["Assets", (IF, "Assets")],
        "liabilities": ["Liabilities", (IF, "Liabilities")],
        "ppe_net": ["PropertyPlantAndEquipmentNet", (IF, "PropertyPlantAndEquipment")],
        "equity": ["StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest", (IF, "Equity")],
        "shares_out_inst": ["CommonStockSharesOutstanding", (IF, "NumberOfSharesOutstanding")],
    }
    DILUTED_SHARE_TAGS = {"WeightedAverageNumberOfDilutedSharesOutstanding", "WeightedAverageNumberOfSharesOutstandingDiluted",
                          "AdjustedWeightedAverageShares", "OVERRIDE"}
    # Tags that carry only a BASIC share count — a period sourced from one is a
    # shares (diluted) gap, never a silent swap (v5.2 rule, extended to IFRS).
    BASIC_SHARE_TAGS = {"WeightedAverageNumberOfSharesOutstandingBasic", "WeightedAverageShares"}
    series, used, series_tags, series_units = {}, {}, {}, {}
    for k, tags in dur_defs.items():
        if k == "capex":   # v5.5: assembled per period below (slot reserved so key order is unchanged)
            series[k], used[k], series_tags[k], series_units[k] = {}, None, {}, {}
            continue
        series[k], used[k], series_tags[k], series_units[k] = period_series(facts, tags, True)
    for k, tags in inst_defs.items(): series[k], used[k], series_tags[k], series_units[k] = period_series(facts, tags, False)
    # v5.5: filing dates of the share counts (the split-basis cutoff rescales only
    # counts filed BEFORE a split event).
    share_filed = period_series(facts, dur_defs["shares_diluted"], True, with_filed=True)[4]
    out_inst_filed = period_series(facts, inst_defs["shares_out_inst"], False, with_filed=True)[4]
    # [ADDITION — verifier round 1, ruling E4] a filed share count <= 0 is not a share count: the fact is treated as
    # not filed, so the period takes the next candidate tag that files a positive count (a basic-only count then
    # gaps / falls back exactly as v5.4 rules), else no count at all (raw_missing shares -> the fallback chain ->
    # DATA_GAP:shares in the last 3 FY). TLN files WeightedAverageNumberOfDilutedSharesOutstanding 0 (and basic 0) for
    # FY2022: the row used to vanish from the median window with no gap. Recorded in share_basis.nonpositive_counts.
    nonpositive_counts = []
    for _k, _tags, _dur, _filed_map in (("shares_diluted", dur_defs["shares_diluted"], True, share_filed),
                                        ("shares_out_inst", inst_defs["shares_out_inst"], False, out_inst_filed)):
        _bad = sorted(p for p, v in series[_k].items() if isinstance(v, (int, float)) and not isinstance(v, bool) and v <= 0)
        if not _bad:
            continue
        _per_tag = [(_tag_name(t), period_series(facts, [t], _dur, with_filed=True)) for t in _tags]
        for p in _bad:
            _rec = {"period": p, "series": _k, "tag": series_tags[_k].get(p), "value": series[_k][p], "replaced_by": None}
            nonpositive_counts.append(_rec)
            for _name, (_vals, _, _, _units, _filed) in _per_tag:
                _v = _vals.get(p)
                if isinstance(_v, (int, float)) and not isinstance(_v, bool) and _v > 0:
                    series[_k][p], series_tags[_k][p], series_units[_k][p] = _v, _name, _units.get(p)
                    _filed_map[p] = _filed.get(p)
                    _rec["replaced_by"] = _name
                    break
            else:
                del series[_k][p]
                series_tags[_k].pop(p, None)
                series_units[_k].pop(p, None)
                _filed_map.pop(p, None)

    # ---- v5.5 capex assembly (decisions 3, 4, 5) ----
    # Per tag, period_series semantics (FY, annual forms, 330-380 days, latest
    # filing per period, USD preferred then other units); per period,
    # capex_for_period builds the PP&E leg (series "capex" — drives the gate,
    # the override fill and the band anchor exactly as the 5.4 merged value
    # did) and the intangible leg (pseudo-series "capex_intang", added on top
    # in the per-period loop).
    def _per_tag(tags):
        out = []
        for t in tags:
            vals, _, _, units, filed = period_series(facts, [t], True, with_filed=True)
            out.append((_tag_name(t), vals, units, filed))
        return out
    capex_groups = (_per_tag(CAPEX_ROLLUP_TAGS), _per_tag(CAPEX_COMPONENT_TAGS), _per_tag(CAPEX_INTANGIBLE_TAGS))
    # [ADDITION — ECHO] intangible values the same tag also files on a multi-year (>380-day) context: an annual
    # fact repeating one of them is a cumulative total, dropped from the intangible leg (capex_provenance.dropped).
    capex_cumulative = cumulative_context_values(facts, CAPEX_INTANGIBLE_TAGS)
    capex_legs, capex_assembly = {}, {}
    for p in sorted({p for grp in capex_groups for _, vals, _, _ in grp for p in vals}):
        capex_legs[p] = tuple([(name, vals[p], units[p], filed.get(p)) for name, vals, units, filed in grp if p in vals]
                              for grp in capex_groups)
        capex_assembly[p] = capex_for_period(*capex_legs[p], cumulative=capex_cumulative)
    series["capex"] = {p: a["ppe"] for p, a in capex_assembly.items() if a["ppe"] is not None}
    series_units["capex"] = {p: a["ppe_unit"] for p, a in capex_assembly.items() if a["ppe"] is not None}
    series_tags["capex"] = {p: "+".join(a["ppe_tags"]) for p, a in capex_assembly.items() if a["ppe"] is not None}
    series["capex_intang"] = {p: a["intangibles"] for p, a in capex_assembly.items() if a["intangible_tags"]}
    series_units["capex_intang"] = {p: a["intangibles_unit"] for p, a in capex_assembly.items() if a["intangible_tags"]}
    # used["capex"] is set to the latest FY's provenance once the periods are known (v5.5)

    # ---- v5.5 SBC reconciliation (decision 6) ----
    # Where the priority merge picked ShareBasedCompensation and
    # AllocatedShareBasedCompensationExpense reports the same period in the
    # SAME unit with a larger value, the Allocated figure is used. Units must
    # match: JD/BEKE/LI/HTHT file Share as USD translations and Allocated in
    # CNY only — a cross-currency compare would 'reconcile' the FX rate.
    _alloc = annual_facts_by_unit(facts, SBC_ALLOCATED_TAG)
    sbc_recon = {}
    for p in sorted(series["sbc"]):
        if series_tags["sbc"].get(p) != SBC_SHARE_TAG:
            continue
        u = series_units["sbc"].get(p)
        alloc_units = [uu for (pp, uu) in _alloc if pp == p]
        if not alloc_units:
            continue
        au = u if u in alloc_units else ("USD" if "USD" in alloc_units else alloc_units[0])
        share_v = series["sbc"][p]
        v, vu, tag_used, reconciled, note = reconcile_sbc((share_v, u), (_alloc[(p, au)][0], au))
        if reconciled:
            series["sbc"][p], series_tags["sbc"][p] = v, tag_used
        sbc_recon[p] = {"share": [share_v, u], "allocated": [_alloc[(p, au)][0], au], "used": tag_used,
                        "reconciled": reconciled, "note": note}

    annual_form = filer_annual_form(cik)
    ads_ratio = load_ads_ratio(ticker)
    share_class = load_share_class_mismatch(ticker)
    # Currency handling is v5.3 (see the FX conversion pass below and the gate):
    # filed units are tracked per period in series_units; the issuer's own USD
    # translations are used as filed, and a single foreign reporting currency
    # is converted at period-end ECB rates. The pre-v5.3 rule (any non-USD unit
    # on core facts in the last 3 FY = gap) is gone.
    # v4.2 share-count fallback: some filers (XOM) stopped tagging weighted diluted shares in
    # XBRL years ago. Fill missing years from dei EntityCommonStockSharesOutstanding (instant).
    dei_shares, dei_entries = {}, []
    try:
        dei = facts.get("facts", {}).get("dei", {}).get("EntityCommonStockSharesOutstanding", {})
        for unit_vals in dei.get("units", {}).values():
            for e in unit_vals:
                dei_entries.append(e)   # v5.5: every cover-page fact, for latest_dei_count's hygiene rules
                end = e.get("end")
                if end and (end not in dei_shares or e.get("filed", "") > dei_shares[end][0]):
                    dei_shares[end] = (e.get("filed", ""), e["val"])
        dei_filed = {k: v[0] for k, v in dei_shares.items()}
        dei_shares = {k: v[1] for k, v in dei_shares.items()}
    except Exception:
        dei_shares, dei_filed = {}, {}

    def dei_for_period(p):
        """v5.4: dei EntityCommonStockSharesOutstanding is dated by the COVER
        PAGE, not the period end (audit: it rarely matched a period). Accept
        the earliest cover-page count within 90 days AFTER the period end."""
        try:
            pe = datetime.date.fromisoformat(p)
        except Exception:
            return None, None
        best, skipped = None, []
        for d, v in dei_shares.items():
            try:
                dd = datetime.date.fromisoformat(d)
            except Exception:
                continue
            lag = (dd - pe).days
            if isinstance(v, bool) or not isinstance(v, (int, float)) or v <= 0:
                # [ADDITION — ruling E4] a cover-page count <= 0 (VOD 0) is not a share count
                if 0 <= lag <= 90 and not isinstance(v, bool) and isinstance(v, (int, float)):
                    skipped.append((d, v))
                continue
            if 0 <= lag <= 90 and (best is None or lag < best[0]):
                best = (lag, v, d)
        # [ADDITION — verifier round 2, R2-E4] the skipped zero is recorded beside the series' zero counts, so a
        # fallback year that lost its cover count says why (LTM 2017: dei 0 on 2017-12-31)
        for d, v in sorted(skipped):
            if not any(x["series"] == "dei" and x["period"] == p and x.get("date") == d for x in nonpositive_counts):
                nonpositive_counts.append({"period": p, "series": "dei", "tag": "EntityCommonStockSharesOutstanding",
                                           "value": v, "date": d,
                                           "replaced_by": (f"dei:EntityCommonStockSharesOutstanding@{best[2]}"
                                                           if best else None)})
        return (best[1], best[2]) if best else (None, None)
    latest_dei = max(dei_shares.items(), key=lambda kv: kv[0]) if dei_shares else None

    # v5.3.1 (Codex review of Stocks PR #1): the override sanity band anchors
    # on the last FILED value in its FILED unit, captured here before the FX
    # pass converts the series — override values are declared in the filer's
    # reporting currency, so a post-conversion (USD) anchor compares unlike
    # units and misjudges the band on every converted name.
    last_filed_raw, last_filed_unit = {}, {}
    for _k in ("capex", "sbc", "shares_diluted"):
        _ps = [p for p in sorted(series[_k]) if series[_k][p] is not None]
        if _ps:
            last_filed_raw[_k] = series[_k][_ps[-1]]
            last_filed_unit[_k] = series_units.get(_k, {}).get(_ps[-1])

    # ---- v5.3 FX conversion: monetary series are in filed units (series_units).
    # A single non-USD reporting currency is converted to USD at period-end ECB
    # rates; flow facts use the period-end rate too (screening simplification,
    # flagged FX_CONVERTED). Dates with no available rate stay unconverted and
    # the currency gate below decides whether they matter (last-3-FY core facts).
    monetary_keys = [k for k in list(dur_defs) + list(inst_defs) if k not in ("shares_diluted", "shares_out_inst")]
    filed_currencies = set()
    for k in monetary_keys:
        for u in series_units.get(k, {}).values():
            if u not in ("USD", "shares", "USD/shares"): filed_currencies.add(u)
    # v5.3.1 (Codex review of Stocks PR #1): conversion eligibility is decided
    # by the last-3-FY CORE facts (revenue / net income / OCF), not by every
    # currency anywhere in history — one stray historical second-currency fact
    # used to disable conversion for a filer that is single-currency today.
    # Exactly one recent core currency: convert it, plus any stray-currency
    # periods elsewhere, each at its own period-end rate. Two or more: a
    # genuinely mixed filer — convert nothing and let the gate fire. No recent
    # core currency (core filed as USD translations): fall back to the
    # all-history set (the JD shape — USD core, one CNY-only debt series).
    _core_periods = sorted({p for k in ("revenue", "net_income", "ocf") for p in series.get(k, {})})[-3:]
    recent_core_ccys = {series_units[k][p] for k in ("revenue", "net_income", "ocf")
                        for p in _core_periods
                        if series_units.get(k, {}).get(p) not in (None, "USD", "shares", "USD/shares")}
    if len(recent_core_ccys) == 1:
        conv_ccys = set(filed_currencies)
    elif len(recent_core_ccys) == 0 and len(filed_currencies) == 1:
        conv_ccys = set(filed_currencies)
    else:
        conv_ccys = set()
    fx_info, fx_unconverted_dates, fx_converted_periods = None, set(), set()
    rates_by_ccy = {}
    if conv_ccys:
        for ccy in sorted(conv_ccys):
            need_dates = sorted({p for k in monetary_keys for p, u in series_units.get(k, {}).items() if u == ccy})
            rates = {}
            for d in need_dates:
                r = fx_rate(ccy, d)
                if r is None: fx_unconverted_dates.add(d)
                else: rates[d] = r
            if rates: rates_by_ccy[ccy] = rates
        if rates_by_ccy:
            converted_fields = []
            for k in monetary_keys:
                for p, u in list(series_units.get(k, {}).items()):
                    r = (rates_by_ccy.get(u) or {}).get(p)
                    if r is not None and series[k].get(p) is not None:
                        series[k][p] = series[k][p] * r
                        fx_converted_periods.add((k, p))
                        if k not in converted_fields: converted_fields.append(k)
            primary = next(iter(recent_core_ccys)) if recent_core_ccys else next(iter(conv_ccys))
            fx_info = {"from_currency": primary, "to_currency": "USD",
                       "source": "frankfurter.app — ECB reference rates (closest business day to each period end)",
                       "converted_fields": converted_fields,
                       "rates": rates_by_ccy.get(primary, {}),
                       "rates_by_currency": rates_by_ccy}
    # v5.5: the intangible capex leg converts at its OWN unit's period-end rate
    # (JD: PP&E as a USD translation, intangibles in CNY), using only rates the
    # pass above already holds — it never enters the conversion-eligibility
    # decision. A non-USD leg with no rate for its date is dropped for that
    # period (capex_provenance records intangibles_dropped: no_rate).
    intang_dropped = {}
    for p, u in list(series_units["capex_intang"].items()):
        if u == "USD":
            continue
        r = (rates_by_ccy.get(u) or {}).get(p) if fx_info else None
        if r is None:
            intang_dropped[p] = "no_rate"
            del series["capex_intang"][p]
        else:
            series["capex_intang"][p] = series["capex_intang"][p] * r
            fx_converted_periods.add(("capex_intang", p))
            if "capex_intang" not in fx_info["converted_fields"]:
                fx_info["converted_fields"].append("capex_intang")   # the record names every converted series
    # Did the engine rely on the issuer's own USD convenience translations?
    # (A core tag whose filed units include both USD and a foreign currency,
    # with USD the unit actually used — e.g. JD's CNY + USD.)
    usd_translation_used = False
    for k in ("revenue", "net_income", "ocf"):
        for t in dur_defs[k]:
            tax, tag = t if isinstance(t, tuple) else ("us-gaap", t)
            unit_keys = list((facts.get("facts", {}).get(tax, {}).get(tag) or {}).get("units", {}).keys())
            if "USD" in unit_keys and any(u not in ("USD", "shares", "USD/shares") for u in unit_keys):
                usd_translation_used = True

    periods = sorted(set(series["revenue"]) | set(series["net_income"]) | set(series["ocf"]))[-10:]
    overrides = load_overrides(ticker)
    # v5.2 override sanity bounds (round-2 audit: a capex override typed as 19
    # instead of 19,000,000 lifted a test company B -> A; a negative one made
    # Tier S). Negative values are impossible — refuse outright, here and in
    # make_score. A value outside 0.1x-10x of the last FILED value for that
    # field (or with no filed value at all) is out of band: flagged
    # OVERRIDE_OUT_OF_BAND below, and make_score refuses it unless
    # judgment.json carries an ack_reason acknowledging the out-of-band value.
    for field, o in overrides.items():
        if o["value"] < 0:
            print(f"dcf_engine.py: REFUSED — judgment.json {field}_override value {o['value']} is negative; "
                  "an override can never be negative (capex / SBC / share counts are >= 0). Fix judgment.json.", file=sys.stderr)
            sys.exit(1)
    ov_fx_fields, ov_usd_verbatim = set(), {}
    OV_SERIES_KEY = {"capex": "capex", "sbc": "sbc", "shares": "shares_diluted"}
    def _ov_basis(field):
        """v5.5 (decision 7): which currency rule applies to this override."""
        return override_currency_basis(dict(overrides[field], field=field), fx_info,
                                       last_filed_unit.get(OV_SERIES_KEY[field]))
    def _override_usd(field, p):
        """The judgment override for `field` expressed in USD for period p.
        v5.3.1 (Codex review of Stocks PR #1): override values are declared
        in the filer's reporting currency (they are read from the filing),
        but v5.3 inserted them verbatim into the USD-converted series —
        silently corrupting owner's earnings on every FX-converted name.
        Monetary overrides convert at the same period-end rate as the filed
        series; share counts are never converted. None when there is no
        override, or when that period's rate is unavailable (the fill does
        not happen and the gap stands). v5.5 (decision 7): an override
        declared currency "USD" (kind filing), or one whose field's last
        filed unit is USD (the issuer's USD statements / translations), is
        already a dollar figure — used verbatim, never converted. The sanity
        band (override_checks, filed unit) is computed separately and is
        untouched by this branch."""
        o = overrides.get(field)
        if o is None: return None
        basis = _ov_basis(field)
        if basis in ("shares", "no_fx"): return o["value"]
        if basis in ("declared_usd", "last_filed_unit_usd"):
            ov_usd_verbatim[field] = basis
            return o["value"]
        r = (fx_info.get("rates_by_currency", {}).get(fx_info["from_currency"]) or {}).get(p)
        if r is None: return None
        ov_fx_fields.add(field)
        return o["value"] * r

    override_checks = {}
    for field, key in OV_SERIES_KEY.items():
        _lf = last_filed_raw.get(key)
        _o = overrides.get(field)
        if _o is None:
            continue
        if _lf is None:
            _oob = True
        elif _lf == 0:
            _oob = _o["value"] != 0
        else:
            _oob = not (0.1 <= abs(_o["value"] / _lf) <= 10)
        override_checks[field] = {"value": _o["value"], "last_filed_value": _lf,
                                  "last_filed_unit": last_filed_unit.get(key),
                                  "out_of_band": bool(_oob),
                                  "ack_reason_present": bool(_o.get("ack_reason")),
                                  "currency_basis": _ov_basis(field)}
    filled = {"capex": [], "sbc": [], "shares": []}        # period ends an override filled
    raw_missing = {"capex": set(), "sbc": set(), "shares": set(), "ocf": set()}  # periods with NO filed value
    basic_only = set()  # periods where only BASIC shares are filed (no diluted figure)
    share_fallback = {}  # v5.4: period -> (fallback count, source tag) when no diluted figure is filed
    debt_blank = []      # v5.4: periods with no debt tag at all (net debt unknown, not zero)
    cash_restricted_periods = []  # periods whose only cash tag includes restricted cash (Codex review of PR #2)
    share_filed_used = {}  # v5.5: period -> filing date of the fact that supplied its share count
    intang_not_added = {}  # v5.5: OVERRIDE-filled capex periods whose filed intangible purchases were not stacked on it
    intang_no_ppe = {}     # [ADDITION — ruling E7] assumed-zero (no PP&E leg) periods whose intangible purchases were not added
    hist, prev_nwc = [], None
    for p in periods:
        g = lambda k: series[k].get(p)
        # v5.5: capex_raw is the PP&E LEG (roll-up, or summed components) —
        # it drives raw_missing / the gate / the override fill exactly as the
        # 5.4 merged value did; intangible purchases are added on top below.
        capex_raw = g("capex")
        if capex_raw is None:
            raw_missing["capex"].add(p)
        asm = capex_assembly.get(p)
        capex_tag_p = series_tags["capex"].get(p)
        capex_ov = _override_usd("capex", p)
        if capex_raw is None and capex_ov is not None:
            capex = capex_ov; capex_tag_p = "OVERRIDE"
            capex_assumed_zero = False; filled["capex"].append(p)
            capex_source_p = "override"
        else:
            capex_assumed_zero = capex_raw is None and g("ocf") is not None
            capex = 0 if capex_assumed_zero else capex_raw
            capex_source_p = "assumed_zero" if capex_assumed_zero else (asm["ppe_source"] if asm and capex_raw is not None else None)
        capex_ppe = capex
        intang = g("capex_intang")
        capex_intang_added = None
        if intang is not None and capex is not None:
            if capex_tag_p == "OVERRIDE":
                # [READING] an override is the filer's TOTAL capex line (FMS:
                # 'PP&E and capitalized development costs') — intangibles are
                # not stacked on it; the OVERRIDE_APPLIED flag says so.
                intang_not_added[p] = asm["intangibles"]
            elif capex_assumed_zero:
                # [ADDITION — verifier round 1, ruling E7] no PP&E leg (an
                # assumed-zero row): the intangible leg is NOT added — capex
                # stays 0 and capex_tag blank, so the row stays an assumed-zero
                # row (the last-3-FY gate is unchanged); capex_intangibles
                # records the filed amount and capex_provenance notes
                # intangibles_not_added 'no_ppe_leg'.
                intang_no_ppe[p] = intang
                capex_intang_added = intang
            else:
                if intang:
                    capex = capex + intang
                capex_intang_added = intang
                capex_tag_p = "+".join(([capex_tag_p] if capex_tag_p else []) + asm["intangible_tags"])
        sbc_raw = g("sbc")
        if sbc_raw is None:
            raw_missing["sbc"].add(p)
        sbc_tag_p = series_tags["sbc"].get(p)
        sbc_ov = _override_usd("sbc", p)
        if sbc_raw is None and sbc_ov is not None:
            sbc = sbc_ov; sbc_tag_p = "OVERRIDE"; filled["sbc"].append(p)
        else:
            sbc = sbc_raw
        sh_tag_p = series_tags["shares_diluted"].get(p)
        sh_merged = g("shares_diluted")
        # v5.2: BASIC shares are not a silent substitute for diluted (round-2:
        # the basic tag sat in the diluted candidate list and tiers shipped on
        # it unflagged). v5.4: that rule was dead code — a basic-only period
        # fell straight through to CommonStockSharesOutstanding / dei counts
        # and shipped unflagged. Now ANY non-diluted source is a shares gap
        # for the gated years; the fallback count is kept (and named in the
        # flag) so the worker can declare a filing override in one step, and
        # older periods use it for history with the source recorded.
        sh_diluted = sh_merged if sh_tag_p in DILUTED_SHARE_TAGS else None
        shares_src = None
        if sh_diluted is not None:
            shares_val, shares_src = sh_diluted, sh_tag_p
            share_filed_used[p] = share_filed.get(p)
        else:
            raw_missing["shares"].add(p)
            fb, fb_filed = None, None
            if sh_merged is not None:
                basic_only.add(p); fb = (sh_merged, sh_tag_p); fb_filed = share_filed.get(p)
            elif g("shares_out_inst") is not None:
                fb = (g("shares_out_inst"), series_tags["shares_out_inst"].get(p)); fb_filed = out_inst_filed.get(p)
            else:
                dv, dd = dei_for_period(p)
                if dv is not None: fb = (dv, f"dei:EntityCommonStockSharesOutstanding@{dd}"); fb_filed = dei_filed.get(dd)
            if fb: share_fallback[p] = fb
            if "shares" in overrides:
                shares_val = overrides["shares"]["value"]; shares_src = "OVERRIDE"; filled["shares"].append(p)
            elif fb:
                shares_val, shares_src = fb[0], f"FALLBACK:{fb[1]}"
                share_filed_used[p] = fb_filed
            else:
                shares_val = None
        if g("ocf") is None:
            raw_missing["ocf"].add(p)
        # v5.4 debt basis per period: noncurrent + current when a noncurrent
        # tag reports; else a TOTAL tag alone (never stacked on current); else
        # unknown — recorded, flagged, never read as zero debt.
        if g("debt_current") is not None:
            d_cur, d_cur_tag = g("debt_current"), series_tags["debt_current"].get(p)
        else:
            _parts = [(k, g(k)) for k in ("debt_cur_ltd", "debt_cur_st") if g(k) is not None]
            d_cur = sum(v for _, v in _parts) if _parts else None
            d_cur_tag = "+".join(str(series_tags[k].get(p)) for k, _ in _parts) if _parts else None
        d_lt, d_tot = g("debt_lt"), g("debt_total")
        if d_lt is not None:
            total_debt = d_lt + (d_cur or 0)
            debt_tag_p = f"{series_tags['debt_lt'].get(p)}+{d_cur_tag or 'none'}"
        elif d_tot is not None:
            _eff_unit = lambda k: "USD" if (k, p) in fx_converted_periods else series_units.get(k, {}).get(p)
            total_debt, debt_tag_p = debt_from_total_tag(d_tot, series_tags["debt_total"].get(p), g("debt_cur_st"), series_tags["debt_cur_st"].get(p),
                                                         same_unit=_eff_unit("debt_total") == _eff_unit("debt_cur_st"))
        elif d_cur is not None:
            total_debt = d_cur
            debt_tag_p = f"CURRENT_ONLY:{d_cur_tag}"
        else:
            total_debt, debt_tag_p = None, None
            debt_blank.append(p)
        # Codex review of PR #2: when the only cash tag is the combined
        # cash + restricted-cash total, subtract the restricted part if it is
        # tagged; otherwise the period is flagged and net debt is understated
        # in a known direction rather than silently.
        cash_avail, cash_tag_p = g("cash"), series_tags["cash"].get(p)
        if cash_avail is not None and cash_tag_p == "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents":
            if g("restricted_cash") is not None:
                cash_avail = cash_avail - g("restricted_cash"); cash_tag_p = f"{cash_tag_p} minus {series_tags['restricted_cash'].get(p)}"
            else:
                cash_restricted_periods.append(p)
        net_debt_p = (total_debt - (cash_avail or 0)) if total_debt is not None else None
        lease_liab = None
        if g("lease_liab_lt") is not None or g("lease_liab_current") is not None:
            lease_liab = (g("lease_liab_lt") or 0) + (g("lease_liab_current") or 0)
        rev, ni, ocf, da = g("revenue"), g("net_income"), g("ocf"), g("da")
        fcf = (ocf - capex) if (ocf is not None and capex is not None) else None
        oe_cons = (fcf - sbc) if (fcf is not None and sbc is not None) else fcf
        nwc = None
        if g("assets_current") is not None and g("liab_current") is not None:
            nwc = (g("assets_current") - (g("cash") or 0)) - (g("liab_current") - (g("debt_current") or 0))
        d_nwc = (nwc - prev_nwc) if (nwc is not None and prev_nwc is not None) else None
        if nwc is not None: prev_nwc = nwc
        oe_maint = None
        if ni is not None and da is not None and capex is not None:
            oe_maint = ni + da - min(capex, da) - (d_nwc or 0)
        hist.append({"period_end": p, "fy_label": p[:4], "revenue": rev, "net_income": ni,
                     "operating_income": g("operating_income"), "ocf": ocf,
                     "ocf_tag": series_tags["ocf"].get(p), "capex": capex,
                     "capex_assumed_zero": capex_assumed_zero,
                     "capex_tag": capex_tag_p, "sbc_tag": sbc_tag_p,
                     "da": da, "sbc": sbc, "fcf": fcf,
                     "oe_conservative": oe_cons, "oe_maintenance": oe_maint, "delta_nwc": d_nwc,
                     "shares_diluted": shares_val, "shares_tag": shares_src, "cash": cash_avail,
                     "cash_tag": cash_tag_p, "restricted_cash": g("restricted_cash"),
                     "debt_current": d_cur, "debt_lt": d_lt, "debt_total": total_debt, "debt_tag": debt_tag_p,
                     "net_debt": net_debt_p, "lease_liabilities": lease_liab,
                     "assets": g("assets"), "liabilities": g("liabilities"),
                     "ppe_net": g("ppe_net"), "equity": g("equity"), "tax": g("tax"),
                     "oe_per_share": (oe_cons / shares_val) if (oe_cons is not None and shares_val) else None,
                     "fcf_per_share": (fcf / shares_val) if (fcf is not None and shares_val) else None,
                     # v5.5 trailing provenance columns (capex = capex_ppe + capex_intangibles, except on an
                     # assumed-zero row, where capex_intangibles records the purchases NOT added — ruling E7)
                     "capex_ppe": capex_ppe, "capex_intangibles": capex_intang_added,
                     "capex_source": capex_source_p, "shares_split_factor": None})

    if fx_info and ov_fx_fields:
        # v5.3.1: monetary override values were converted from the reporting
        # currency at period-end rates before being applied (see _override_usd).
        fx_info["overrides_converted"] = sorted(ov_fx_fields)
    overrides_applied = []
    for field in ("capex", "sbc", "shares"):
        if filled[field]:
            o = overrides[field]
            overrides_applied.append({"field": field, "value": o["value"], "kind": o["kind"],
                                      "source": o["source"], "reason": o["reason"],
                                      "periods_filled": filled[field],
                                      "out_of_band": override_checks.get(field, {}).get("out_of_band", False),
                                      "last_filed_value": override_checks.get(field, {}).get("last_filed_value")})
    if len(hist) < 2:
        # No usable history is a DATA failure, not a Tier F verdict. Exit distinctly so the
        # sweep marks blocked_no_data instead of publishing a fake F (the XOM trap).
        print(f"NO_DATA for {ticker}: only {len(hist)} usable fiscal years under CIK {cik} ({name}) — possible entity/CIK change (e.g. a 2026 holding-company reorganization). The analyzing agent should find the operating parent's CIK (web search the company + 'CIK 10-K') and rerun with --cik <CIK>; if none exists, mark blocked_no_data.")
        sys.exit(3)

    # ---- v5.5 capex provenance (decisions 3-5): used_tags and the per-period record ----
    def _leg_detail(p, group_idx, tags):
        legs = capex_legs.get(p, ([], [], []))[group_idx]
        return {name: val for name, val, _, _ in legs if name in tags}
    capex_provenance, capex_tags_used = {}, set()
    for h in hist:
        p = h["period_end"]
        asm = capex_assembly.get(p)
        rec = {"ppe_source": h["capex_source"], "ppe": {}, "ppe_unit": None, "intangibles": {},
               "intangibles_unit": None, "dropped": [], "filed": {}}
        if asm:
            used_ppe = asm["ppe_tags"] if h["capex_tag"] != "OVERRIDE" and h["capex_source"] != "assumed_zero" else []
            used_int = asm["intangible_tags"] if (h["capex_intangibles"] is not None and p not in intang_no_ppe) else []
            rec.update(ppe={**_leg_detail(p, 0, used_ppe), **_leg_detail(p, 1, used_ppe)}, ppe_unit=asm["ppe_unit"] if used_ppe else None,
                       intangibles=_leg_detail(p, 2, used_int), intangibles_unit=asm["intangibles_unit"] if used_int else None,
                       dropped=[list(d) for d in asm["dropped"]],
                       filed={name: fd for grp in capex_legs[p] for name, _, _, fd in grp if name in used_ppe or name in used_int})
            capex_tags_used.update(used_ppe + used_int)
            if p in intang_not_added:
                rec["intangibles_not_added"] = "override_present"
                rec["intangibles_filed"] = _leg_detail(p, 2, asm["intangible_tags"])
            elif p in intang_no_ppe:   # [ADDITION — ruling E7]
                rec["intangibles_not_added"] = "no_ppe_leg"
                rec["intangibles_filed"] = _leg_detail(p, 2, asm["intangible_tags"])
            if p in intang_dropped:
                rec["intangibles_dropped"] = intang_dropped[p]
        capex_provenance[p] = rec
    _filed_capex = [h for h in hist if h["capex_tag"] and h["capex_tag"] != "OVERRIDE"]
    used["capex"] = (hist[-1]["capex_tag"] if hist[-1]["capex_tag"] and hist[-1]["capex_tag"] != "OVERRIDE"
                     else (_filed_capex[-1]["capex_tag"] if _filed_capex else None))
    used["capex_components"] = "+".join(sorted(capex_tags_used)) or None
    # [ADDITION — verifier round 1, ruling E8] used_tags.sbc names the tag the latest period actually used after the
    # SBC reconciliation (as used_tags.capex does): period_series' first-used tag kept reading ShareBasedCompensation
    # at JLL while every row used AllocatedShareBasedCompensationExpense. An OVERRIDE row yields the latest filed
    # tag; with no filed tag in the CSV years the first-used tag stands.
    _filed_sbc = [h for h in hist if h["sbc_tag"] and h["sbc_tag"] != "OVERRIDE"]
    if _filed_sbc:
        used["sbc"] = _filed_sbc[-1]["sbc_tag"]

    # ---- v5.5 share basis (decision 2b, Option B: the engine handles splits) ----
    # A split ratio filed for a context AFTER the latest FY end, confirmed by a
    # post-event cover-page (dei) count, means the annual history counts and
    # the current price sit on different bases: every count filed before the
    # event (never an OVERRIDE) is multiplied by the confirmed ratio. In-history
    # ratio facts are re-disclosures the annual filing already reflects
    # (MLI/CSGP/DXCM/CFG/BWA/COKE) and never adjust anything.
    latest_fy_end = hist[-1]["period_end"]
    dei_count, dei_date = latest_dei_count(dei_entries, latest_fy_end)
    _split_entries = [e for t in SPLIT_RATIO_TAGS
                      for e in ((facts.get("facts", {}).get("us-gaap", {}).get(t) or {}).get("units", {}).get("pure") or [])]
    split_events = split_events_post_fy(_split_entries, latest_fy_end)
    # [ADDITION — verifier round 3, R3-SPLIT] the split is confirmed against the latest FILED count (the most recent
    # row whose count is not an OVERRIDE): a shares_override must already be on the post-split basis (ruling D7,
    # WORKER_SPEC step 8), so a post-split override in the latest FY equals the post-event dei and, used here, had
    # confirmed nothing — the filed history stayed on the pre-split basis (base 1/3 of the right figure, Tier C ->
    # D, no flag). Overrides are still never rescaled, so the rescaled history and the override share one basis.
    _filed_sh = [h for h in hist if h.get("shares_diluted") and h["shares_tag"] != "OVERRIDE"]
    split_confirm_row = _filed_sh[-1] if _filed_sh else None
    split_conf = confirm_split(split_events, split_confirm_row["shares_diluted"] if split_confirm_row else None,
                               dei_count, dei_date)
    share_basis = {"split": None, "divergence": None,
                   "unconfirmed_split_facts": [{"date": d, "ratio_filed": r} for d, r in split_events
                                               if not split_conf or d != split_conf[0]],
                   # [ADDITION — ruling E11] split facts dated on or before the latest FY end: informational only
                   "in_history_split_facts": [{"date": d, "ratio_filed": r}
                                              for d, r in split_facts_in_history(_split_entries, latest_fy_end)],
                   # [ADDITION — ruling E4] filed share counts <= 0 treated as not filed
                   "nonpositive_counts": [x for x in nonpositive_counts if x["period"] in periods]}
    split_adjusted = []
    if split_conf:
        ev_date, ratio_used, evidence = split_conf
        for h in hist:
            fd = share_filed_used.get(h["period_end"])
            if h["shares_diluted"] and h["shares_tag"] != "OVERRIDE" and fd and fd < ev_date:
                h["shares_diluted"] = h["shares_diluted"] * ratio_used
                h["shares_split_factor"] = ratio_used
                h["oe_per_share"] = (h["oe_conservative"] / h["shares_diluted"]) if h["oe_conservative"] is not None else None
                h["fcf_per_share"] = (h["fcf"] / h["shares_diluted"]) if h["fcf"] is not None else None
                split_adjusted.append(h["period_end"])
        share_basis["split"] = {"event_date": ev_date, "ratio_filed": evidence["ratio_filed"], "ratio_used": ratio_used,
                                "matched": evidence["matched"], "dei_count": dei_count, "dei_date": dei_date,
                                "dei_to_shares": evidence["dei_to_shares"], "periods_adjusted": split_adjusted,
                                # [ADDITION — verifier round 3, R3-SPLIT] the filed row the dei was tested against
                                "confirmed_against_period": split_confirm_row["period_end"],
                                # [ADDITION — ruling E9] OVERRIDE counts are never rescaled; the flag names them
                                "periods_override_not_rescaled": [h["period_end"] for h in hist
                                                                  if h["shares_tag"] == "OVERRIDE" and h["shares_diluted"]]}

    latest = hist[-1] if hist else {}
    shares = latest.get("shares_diluted")
    net_debt = latest.get("net_debt")  # v5.4: per-period basis (see debt_tag); None = unknown, never zero

    price = price_arg or nasdaq_price(ticker)
    if price_arg is not None: price_source = "manual"  # v5: a hand-passed price was labelled nasdaq_quote_api (audit)
    elif price: price_source = "nasdaq_quote_api"
    else: price_source = None
    if price is None and ticker in uni:
        try: price = float(uni[ticker]["price"]); price_source = "universe_screener"
        except Exception: price = None
    # v5.5: the market cap is computed after the share-basis checks below
    # (market_cap_est: price × shares ÷ ads_ratio).

    def cagr(key, periods_n):
        vals = [(h["period_end"], h[key]) for h in hist if h.get(key)]
        if len(vals) < 2: return None
        (d0, v0), (d1, v1) = vals[-min(periods_n, len(vals))], vals[-1]
        yrs = (datetime.date.fromisoformat(d1) - datetime.date.fromisoformat(d0)).days / 365.25
        if v0 and v0 > 0 and v1 > 0 and yrs > 0.5: return (v1 / v0) ** (1 / yrs) - 1
        return None
    rev_cagr5, rev_cagr3 = cagr("revenue", 6), cagr("revenue", 4)
    oe_vals = [h["oe_conservative"] for h in hist if h.get("oe_conservative") is not None]

    # ---- v4: per-share OE history + NORMALIZED base (median of last 3 years) ----
    # v3 used the single latest fiscal year as the DCF base — the most fragile choice in the
    # model: one cyclical peak/trough, one-off, or SBC/WC spike year became the foundation.
    # (statistics is imported at module level — v5.4)
    oe_ps_hist = [(h["period_end"], h["oe_conservative"] / h["shares_diluted"])
                  for h in hist if h.get("oe_conservative") is not None and h.get("shares_diluted")]
    if ads_ratio:
        # Per-share figures become per-ADS (x ordinary shares per ADS) so they
        # are comparable to the ADS price. Ratio is a constant scale: growth
        # rates are unaffected. A TTM pin (--base-oe-ps / --ttm) is NOT scaled —
        # pins are taken as per-ADS already (see the ADS flag text).
        oe_ps_hist = [(d, v * ads_ratio["ratio"]) for d, v in oe_ps_hist]
    oe_ps_latest = oe_ps_hist[-1][1] if oe_ps_hist else None
    last3 = [v for _, v in oe_ps_hist[-3:]]
    oe_ps_norm = statistics.median(last3) if len(last3) >= 2 else oe_ps_latest
    # Base pin: --base-oe-ps wins for compatibility; --ttm reads the pin from
    # <TICKER>/ttm.json (ttm.py's saved output) so the base is never a free
    # number typed at a shell — make_score verifies it against ttm.json.
    pin_source = None
    payable_base = None
    if "--base-oe-ps" in sys.argv:
        base_override = float(sys.argv[sys.argv.index("--base-oe-ps") + 1]); pin_source = "base_oe_ps_arg"
    elif "--ttm" in sys.argv:
        try:
            with open(f"{BASE}/{ticker}/ttm.json", encoding="utf-8") as _f:
                base_override = float(json.load(_f)["ttm_oe_per_share"])
            pin_source = "ttm_json"
        except Exception as e:
            print(f"NO_TTM for {ticker}: --ttm given but {BASE}/{ticker}/ttm.json is missing or unreadable ({e}) — run ttm.py {ticker} first so the pin has provenance")
            sys.exit(3)
    elif "--base-judgment" in sys.argv:
        # Insurer payable-earnings base (2026-10-19): the pin is the declared
        # 5-yr average operating income to common / latest diluted shares, in
        # judgment.json, recomputed here and scaled by the ADS ratio. Refused
        # (exit 3) when the declaration is malformed, does not reproduce, the
        # share count is not this run's latest diluted count, or the filer's
        # series were FX-converted (the figures must already be USD).
        try:
            pb = load_payable_base(ticker)
            if not shares or abs(float(pb["shares"]) - float(shares)) >= 1.0:  # exact: the denominator IS the latest count
                raise ValueError(f"base_override.shares {pb['shares']:,.0f} is not this run's latest diluted count {shares if shares else 'n/a'}")
            sic, sic_desc = filer_sic(cik)
            if sic not in PAYABLE_SIC:
                raise ValueError(f"the payable-earnings rule is scoped to P&C insurers/reinsurers (SIC {sorted(PAYABLE_SIC)}); "
                                 f"EDGAR lists SIC {sic or 'unknown'} ({sic_desc or 'n/a'}) — keep the OCF base and the 2026-10-15 notch")
            if fx_info and fx_info.get("from_currency") and fx_info.get("from_currency") != "USD":
                raise ValueError("payable base is only defined for USD filers (series were FX-converted) — escalate NEEDS_MAIN_AGENT")
            base_override = payable_base_per_share(pb["figures"], pb["shares"], ads_ratio)
        except ValueError as e:
            print(f"BAD_BASE_OVERRIDE for {ticker}: --base-judgment given but {e}")
            sys.exit(3)
        pin_source = "judgment_base_override"
        payable_base = {"basis": PAYABLE_BASIS, "figures": [float(x) for x in pb["figures"]],
                        "average": sum(float(x) for x in pb["figures"]) / 5.0,
                        "shares": float(pb["shares"]), "per_ordinary_share": float(pb["value"]),
                        "ads_ratio": float(ads_ratio["ratio"]) if ads_ratio else 1.0,
                        "pinned_per_share": base_override, "sic": sic, "sic_description": sic_desc}
    else:
        base_override = None
    if base_override is not None:
        oe_ps, base_source = base_override, ("ttm_json" if pin_source == "ttm_json"
                                             else "judgment_base_override" if pin_source == "judgment_base_override"
                                             else "agent_supplied_ttm_override")
    elif oe_ps_norm is not None:
        oe_ps, base_source = oe_ps_norm, "median_of_last_3_fy_oe_per_share"
    else:
        oe_ps, base_source = None, "none"
    base_oe = latest.get("oe_conservative")

    # ---- v4: blended growth (median of independent signals) + share-count adjustment ----
    rev_yoy_latest = None
    revs = [(h["period_end"], h["revenue"]) for h in hist if h.get("revenue")]
    if len(revs) >= 2 and revs[-2][1]:
        rev_yoy_latest = revs[-1][1] / revs[-2][1] - 1
    oe_ps_cagr = None
    if len(oe_ps_hist) >= 3 and oe_ps_hist[-3][1] and oe_ps_hist[-3][1] > 0 and oe_ps_hist[-1][1] > 0:
        yrs = (datetime.date.fromisoformat(oe_ps_hist[-1][0]) - datetime.date.fromisoformat(oe_ps_hist[-3][0])).days / 365.25
        if yrs > 0.5: oe_ps_cagr = (oe_ps_hist[-1][1] / oe_ps_hist[-3][1]) ** (1 / yrs) - 1
    share_cagr = None
    sh = [(h["period_end"], h["shares_diluted"]) for h in hist if h.get("shares_diluted")]
    if len(sh) >= 2:
        (d0, s0), (d1, s1) = sh[-min(4, len(sh))], sh[-1]
        yrs = (datetime.date.fromisoformat(d1) - datetime.date.fromisoformat(d0)).days / 365.25
        if s0 and s0 > 0 and s1 > 0 and yrs > 0.5: share_cagr = (s1 / s0) ** (1 / yrs) - 1
    growth_components = {"rev_cagr_5y": rev_cagr5, "rev_cagr_3y": rev_cagr3,
                         "rev_yoy_latest": rev_yoy_latest, "oe_ps_cagr_2y": oe_ps_cagr}  # v5: was mislabelled oe_ps_cagr_3y — the span from t-3 to t-1 endpoints is 2 years
    share_adj = max(-0.05, min(0.05, -(share_cagr or 0.0)))  # buybacks lift OE/share growth; dilution drags it
    # v5.4: the share-count adjustment is applied to the REVENUE components
    # only. v4 added it to the median of all four signals, but the OE/share
    # CAGR already embeds the share-count trend — the audit's "double-counted
    # dilution" finding. The per-share CAGR enters the median unadjusted.
    growth_components_adjusted = {"rev_cagr_5y": None if rev_cagr5 is None else rev_cagr5 + share_adj,
                                  "rev_cagr_3y": None if rev_cagr3 is None else rev_cagr3 + share_adj,
                                  "rev_yoy_latest": None if rev_yoy_latest is None else rev_yoy_latest + share_adj,
                                  "oe_ps_cagr_2y": oe_ps_cagr}
    comp_vals = [v for v in growth_components_adjusted.values() if v is not None]
    g_blend = statistics.median(comp_vals) if comp_vals else 0.03

    # v5.3: the currency gap is judged on the periods actually used. Not a gap:
    # facts filed in USD (including the issuer's own USD convenience
    # translations) or FX-converted above. Still a gap: mixed reporting
    # currencies in the last 3 FY, or a last-3-FY core fact whose period-end
    # rate was unavailable and so stayed unconverted.
    # v5.3.1: a last-3-FY core period is a currency gap iff it was filed in a
    # non-USD unit and the FX pass did not convert it (mixed filer, or no ECB
    # rate for its currency) — one rule for every filer shape.
    # (v5.5: computed here, ahead of the gate, because the share-scale guard
    # is skipped on a currency gap — KSPI's 26x is unconverted KZT.)
    last3_periods = [h["period_end"] for h in hist[-3:]]
    currency_gap = any(series_units.get(k, {}).get(p) not in (None, "USD", "shares", "USD/shares")
                       and (k, p) not in fx_converted_periods
                       for k in ("revenue", "net_income", "ocf") for p in last3_periods)

    # ---- v5.5 share-scale guard (decision 2a) and the market-cap share basis ----
    ads_r = ads_ratio["ratio"] if ads_ratio else None
    shares_for_cap = shares
    shares_source = "diluted_latest_split_adjusted" if (split_adjusted and latest.get("period_end") in split_adjusted) else "diluted_latest"
    share_scale = {"defect": False, "tests": {"a": False, "b": False}, "reasons": [], "dei_count": dei_count,
                   "dei_date": dei_date, "dei_ratio": None, "scale_factor": None, "factor_basis": None,
                   "rescued_by_pin": False, "skipped": "currency_gap" if currency_gap else None,
                   # [ADDITION — verifier round 1, rulings E1-E3] see share_scale_pin_rescue /
                   # share_series_scale_breaks and the leverage note below
                   "pin_rejected": None, "leverage_unverifiable": False, "scale_breaks": [],
                   "growth_inputs_dropped": [], "growth_inputs_dropped_values": {},
                   # [ADDITION — verifier round 2, R2-PIN / R2-E2] test (a) on the pin actually used; a share-derived
                   # growth input kept beside a scale break (the OE/share CAGR whose endpoints share one scale)
                   "pin_over_price": False, "growth_inputs_kept": [],
                   # [ADDITION — verifier round 3, R3-CAP] a power-of-ten pin ratio the window test withheld
                   "pin_factor_withheld": None}
    if not currency_gap:
        _chk = share_scale_check(oe_ps_norm, price, shares, dei_count,
                                 pin=base_override if pin_source else None, pin_source=pin_source)
        share_scale.update(defect=_chk["defect"], tests=_chk["tests"], reasons=_chk["reasons"], dei_ratio=_chk["dei_ratio"],
                           pin_over_price=_chk["pin_over_price"])
        if _chk["defect"]:
            # [ADDITION — ruling E1] only a --base-oe-ps pin that judgment.json declares as a (non-payable)
            # base_override, and that is not itself mis-scaled, carries a share-scale defect.
            _rescue, _why = share_scale_pin_rescue(pin_source, base_override if pin_source == "base_oe_ps_arg" else None,
                                                   price, load_declared_base_override(ticker))
            share_scale["rescued_by_pin"] = _rescue
            if pin_source == "base_oe_ps_arg" and not _rescue:
                share_scale["pin_rejected"] = _why
            # [ADDITION — verifier round 3, R3-CAP] the pin factor needs the median year's count and the latest count
            # on one scale (scale_factor_for_cap's window test); a power-of-ten pin ratio withheld by a scale break is
            # recorded in share_scale.pin_factor_withheld and named in SHARE_SCALE_SUSPECT
            _win = median_window_counts(oe_ps_hist, sh, latest.get("period_end"))
            _factor, _basis = scale_factor_for_cap(shares, dei_count, oe_ps_norm, base_override if _rescue else None,
                                                   window_counts=_win)
            _pin_pow = pin_power_of_ten(oe_ps_norm, base_override) if _rescue else None
            # [ADDITION — verifier round 4, R4-CAP] the median year's count vs the latest count (the window's
            # endpoints), not every adjacent pair of the window
            _end_breaks = median_latest_scale_breaks(_win)
            if _pin_pow and not _factor and _win:
                share_scale["pin_factor_withheld"] = {
                    "factor": _pin_pow, "window": [{"period": p, "count": c} for p, c in _win],
                    "breaks": [{"from_period": a, "from_count": b, "to_period": c, "to_count": d}
                               for a, b, c, d in _end_breaks]}
            share_scale.update(scale_factor=_factor, factor_basis=_basis)
            if _factor and shares:
                shares_for_cap, shares_source = shares * _factor, "diluted_latest_scale_corrected"
            # [ADDITION — ruling E3] a rescued defect with no power-of-ten factor and no usable cover-page count
            # (test (b) not evaluable): the cap's count is unverified, so the normalized-OE total and the leverage
            # diagnostics built on it are not computed (a 1,000x-small total printed HIGH_NET_DEBT 400x).
            # [ADDITION — verifier round 2, R2-E3] likewise when a dei EXISTS and test (b) failed (the latest count is
            # more than 100x off the cover page) with no factor: the cover page proves the count wrong (HIGH_NET_DEBT
            # 666.7x). Only a dei that passed test (b) (VIV) keeps the diagnostics.
            # [ADDITION — verifier round 4, R4-E3] ... and only when that agreement is evidence: when test (a) fired on
            # the native median and the latest count is on the median year's scale (no endpoint break), the latest
            # count carries the scale test (a) found wrong, so a dei that agrees with it is filed on the same basis
            # (every count and the cover page in thousands, a TTM pin no power of ten off the native base: cap
            # 1,000x small, a false HIGH_NET_DEBT 500x). VIV (its latest count on another scale than its median
            # year) keeps the diagnostics.
            share_scale["leverage_unverifiable"] = bool(
                _rescue and not _factor
                and (_chk["dei_ratio"] is None or _chk["tests"]["b"]
                     or (_chk["tests"]["a"] and bool(_win) and not _end_breaks)))
            # [ADDITION — ruling E2] a scale break inside the growth window (two adjacent counts among the last 4
            # more than 100x apart) makes the share-count CAGR an artefact of the units: it leaves the growth blend
            # and the share adjustment is 0. A consistently scaled series keeps it.
            # [ADDITION — verifier round 2, R2-E2] the OE/share CAGR (oe_ps_hist[-3] -> oe_ps_hist[-1]) leaves the
            # blend only when a break lies between its own endpoints — "computed on the same broken series" (E2's
            # reason); a break before FY t-2 leaves both endpoints on one scale and the CAGR valid.
            _breaks = share_series_scale_breaks(sh[-4:])
            if _breaks:
                _gone = {}
                if share_cagr is not None:
                    _gone["share_cagr"] = share_cagr
                # [ADDITION — verifier round 4, R4-E2] the CAGR reads only its two endpoints, so their two counts
                # are compared (not every adjacent pair between them: an alternating series kept a valid CAGR out)
                _shd = dict(sh)
                _oe_break = bool(len(oe_ps_hist) >= 3 and share_series_scale_breaks(
                    [(p, _shd.get(p)) for p in (oe_ps_hist[-3][0], oe_ps_hist[-1][0])]))
                if oe_ps_cagr is not None and _oe_break:
                    _gone["oe_ps_cagr_2y"] = oe_ps_cagr
                share_scale.update(scale_breaks=[{"from_period": a, "from_count": b, "to_period": c, "to_count": d}
                                                 for a, b, c, d in _breaks],
                                   growth_inputs_dropped=list(_gone), growth_inputs_dropped_values=_gone,
                                   growth_inputs_kept=["oe_ps_cagr_2y"] if (oe_ps_cagr is not None and not _oe_break) else [])
                share_cagr, share_adj = None, 0.0
                growth_components_adjusted = {"rev_cagr_5y": rev_cagr5, "rev_cagr_3y": rev_cagr3,
                                              "rev_yoy_latest": rev_yoy_latest,
                                              "oe_ps_cagr_2y": None if _oe_break else oe_ps_cagr}
                comp_vals = [v for v in growth_components_adjusted.values() if v is not None]
                g_blend = statistics.median(comp_vals) if comp_vals else 0.03
    # SHARE_BASIS_DIVERGENCE fallback (2b): no confirmed split, a cover-page
    # count dated after the latest FY end that differs from the latest diluted
    # count with one more than 25% below the other (dei / diluted outside
    # DIVERGENCE_BAND 0.75x-1.333x: issuance, a merger or an unfiled split). Only a
    # 10-K filer's dei count is in the traded share's units — at 20-F / 40-F /
    # ADS filers it may count CPOs, ADSs or one class (CX: 3x), so there it is
    # recorded with no switch and no flag.
    if (not split_conf and not share_scale["defect"] and dei_count and shares and dei_date
            and dei_date > latest_fy_end and not (DIVERGENCE_BAND[0] <= dei_count / shares <= DIVERGENCE_BAND[1])):
        _foreign = annual_form in ("20-F", "40-F") or bool(ads_r and ads_r != 1)
        share_basis["divergence"] = {"dei_count": dei_count, "dei_date": dei_date, "shares_latest": shares,
                                     "dei_to_shares": dei_count / shares, "applied": not _foreign,
                                     "note": ("foreign-form / ADS filer: the cover-page count may be in other units — recorded, not applied"
                                              if _foreign else "market cap uses the cover-page count")}
        if not _foreign:
            shares_for_cap, shares_source = dei_count, "dei_latest"
    mktcap = market_cap_est(price, shares_for_cap, ads_r)
    if mktcap is None:
        # The 5.4 fallback (no price or no share count): universe.csv's cap, or none. The
        # basis record then names no share count — none was used (make_score / reprice read it).
        mktcap = float(uni[ticker]["market_cap"]) if ticker in uni and uni[ticker].get("market_cap") else None
        market_cap_basis = {"shares_used": None,
                            "shares_source": "universe_market_cap" if mktcap is not None else None,
                            "ads_ratio": ads_r,
                            "formula": "universe.csv market_cap (no price or no share count)" if mktcap is not None else None}
    else:
        market_cap_basis = {"shares_used": shares_for_cap, "shares_source": shares_source, "ads_ratio": ads_r,
                            "formula": "price × shares ÷ ads_ratio" if ads_r else "price × shares"}

    result = {"ticker": ticker, "name": name, "cik": cik, "engine_version": 5, "engine_release": ENGINE_RELEASE,
              "as_of": ET_TODAY.isoformat(),
              "price": price, "price_source": price_source, "shares_diluted_latest": shares,
              "shares_outstanding_dei_latest": (latest_dei[1] if latest_dei else None),
              "shares_outstanding_dei_asof": (latest_dei[0] if latest_dei else None),
              "market_cap_est": mktcap, "net_debt_latest": net_debt, "net_debt_basis": latest.get("debt_tag"),
              "lease_liabilities_latest": latest.get("lease_liabilities"),
              "latest_period_end": latest.get("period_end"),
              "rev_cagr_5y": rev_cagr5, "rev_cagr_3y": rev_cagr3,
              "oe_positive_years_of_last_5": f"{sum(1 for v in oe_vals[-5:] if v>0)}/{len(oe_vals[-5:])}",
              "base_oe_total_latest_fy": base_oe, "base_oe_per_share": oe_ps,
              "base_oe_latest_per_share": oe_ps_latest, "base_oe_normalized_per_share": oe_ps_norm,
              "base_source": base_source, "growth_components": growth_components,
              "growth_components_adjusted": growth_components_adjusted,
              "g_blend": g_blend, "share_cagr": share_cagr, "share_count_adj": share_adj,
              "share_adj_basis": "applied to revenue components only (v5.4); OE/share CAGR enters unadjusted",
              "used_tags": used,
              "filer_annual_form": annual_form, "ads_ratio": ads_ratio, "fx_conversion": fx_info,
              "payable_base": payable_base,
              "override_checks": override_checks,
              # v5.5 records (decisions 1-6): see the module docstring
              "market_cap_basis": market_cap_basis, "share_scale": share_scale, "share_basis": share_basis,
              "share_class_mismatch": share_class, "capex_provenance": capex_provenance,
              "sbc_provenance": {p: sbc_recon[p] for p in periods if p in sbc_recon}}
    if fx_info:
        # v5.5 (decision 7): overrides used verbatim as USD figures, and which rule fired
        # ({} when every override was converted, or none is declared).
        fx_info["overrides_usd_verbatim"] = dict(sorted(ov_usd_verbatim.items()))

    # ---- v3 scenario / moat inputs ----
    def arglist(flag, default):
        if flag in sys.argv:
            return [float(x) for x in sys.argv[sys.argv.index(flag) + 1].split(",")]
        return default
    moat = float(sys.argv[sys.argv.index("--moat") + 1]) if "--moat" in sys.argv else 5.0
    moat = max(0.0, min(10.0, moat))
    cap_years = cap_years_for_moat(moat)
    probs = arglist("--probs", [0.10, 0.25, 0.30, 0.25, 0.10])
    offsets = arglist("--offsets", [-0.12, -0.05, 0.0, 0.05, 0.12])
    mults = arglist("--mults", [0.75, 0.90, 1.00, 1.10, 1.25])
    psum = sum(probs)
    probs = [p / psum for p in probs] if psum > 0 else [0.2] * 5

    gterm = float(sys.argv[sys.argv.index("--gterm") + 1]) if "--gterm" in sys.argv else DEFAULT_GTERM

    # ---- v5: fragility flags that do NOT depend on the scenario math are computed HERE,
    # before the Tier F branch — v4 computed flags only inside the positive-OE branch, so
    # every F name shipped with an empty flag list (audit finding). ----
    flags_pre, months_stale = [], None
    if latest.get("period_end"):
        months_stale = (ET_TODAY - datetime.date.fromisoformat(latest["period_end"])).days / 30.44
        if months_stale > 7: flags_pre.append(f"STALE_FY: latest fiscal year ended {months_stale:.0f} months ago — check TTM/quarterly OE and consider --base-oe-ps override")
    if share_cagr is not None and share_cagr > 0.03: flags_pre.append(f"DILUTION: share count growing {share_cagr*100:.1f}%/yr — already deducted via the growth adjustment; check SBC trend")
    if share_cagr is not None and share_cagr < -0.02: flags_pre.append(f"BUYBACK_TAILWIND: share count shrinking {-share_cagr*100:.1f}%/yr — already credited via the growth adjustment")
    rev_yoys = [revs[i][1] / revs[i - 1][1] - 1 for i in range(1, len(revs)) if revs[i - 1][1]][-5:]
    if any(abs(y) > 0.60 for y in rev_yoys): flags_pre.append("BASIS_BREAK_SUSPECT: a >60% revenue jump/drop in the last 5 yrs — check for divestitures, big M&A, or restatements before trusting any CAGR")
    pos_oe = [v for _, v in oe_ps_hist[-5:] if v > 0]
    if len(pos_oe) >= 3 and max(pos_oe) / min(pos_oe) > 3: flags_pre.append("OE_VOLATILE: OE/share range over the last 5 yrs spans >3x — normalized base helps but the business is cyclical; widen bear weight")
    ni_ocf_gap_years = [h["period_end"][:4] for h in hist[-3:]
                        if h.get("net_income") is not None and h.get("ocf") not in (None, 0)
                        and abs(h["net_income"] - h["ocf"]) / abs(h["ocf"]) > 0.40
                        and abs(h["net_income"] - h["ocf"]) > (h.get("da") or 0)]
    if ni_ocf_gap_years: flags_pre.append(f"NI_OCF_DIVERGENCE: net income and operating cash flow differ by >40% in {', '.join(ni_ocf_gap_years)} — find the one-off (tax deposits, impairments, WC swings) before trusting the OE base")
    if cik_fallback_note: flags_pre.append(cik_fallback_note)
    if fx_info:
        flags_pre.append(f"FX_CONVERTED: reporting currency {fx_info['from_currency']} converted to USD at period-end ECB reference rates (frankfurter.app) — flow facts use the period-end rate, not a period average; the rates used are recorded in dcf_numbers.json fx_conversion")
    if usd_translation_used:
        flags_pre.append("USD_TRANSLATIONS_USED: the issuer files its own USD convenience translations alongside its reporting currency; the engine used the filed USD figures")
    if annual_form in ("20-F", "40-F"):
        if ads_ratio:
            flags_pre.append(f"ADS_RATIO_APPLIED: {annual_form} filer — per-share figures scaled x{ads_ratio['ratio']} ordinary shares per ADS "
                             f"({ads_ratio['source']}) so they are comparable to the ADS price; TTM pins are taken as per-ADS already")
        else:
            flags_pre.append(f"ADS_RATIO_MISSING: {annual_form} filer — per-share figures are per ordinary share but the traded price is per ADS; "
                             "make_score refuses (DATA_GAP:ads_ratio) until judgment.json carries an ads_ratio {ratio, source, reason}")
    for field, chk in override_checks.items():
        if chk["out_of_band"] and not chk["ack_reason_present"]:
            lf = chk["last_filed_value"]
            lf_s = f"${lf:,.0f}" if isinstance(lf, (int, float)) else "no filed value at all"
            flags_pre.append(f"OVERRIDE_OUT_OF_BAND:{field} — override value {chk['value']:,.0f} is outside 0.1x-10x of the last filed value "
                             f"({lf_s}) and judgment.json carries no ack_reason — make_score will refuse until the out-of-band value is explicitly acknowledged")
    if len(hist) < 4: flags_pre.append(f"THIN_HISTORY: only {len(hist)} fiscal years of data")
    _fb_hist = sorted(p[:4] for p in share_fallback if p not in [h["period_end"] for h in hist[-3:]] and p in [h["period_end"] for h in hist])
    if _fb_hist:
        flags_pre.append(f"SHARES_FALLBACK: no diluted share count filed for {', '.join(_fb_hist)} — those history years use the basic / outstanding / dei count recorded in the shares_tag column; per-share history there is approximate")
    if debt_blank and latest.get("period_end") in debt_blank:
        flags_pre.append("DEBT_TAGS_BLANK: no debt tag reports for the latest fiscal year — net debt is UNKNOWN (not zero); no leverage verdict is possible from the engine, state the balance sheet from the filing in analysis.md")
    if cash_restricted_periods and latest.get("period_end") in cash_restricted_periods:
        flags_pre.append("CASH_INCLUDES_RESTRICTED: the only cash tag filed for the latest fiscal year is the combined cash + restricted-cash total and no restricted-cash tag separates it — net debt is UNDERSTATED by the restricted amount (escrow / collateral / regulatory); check the balance sheet before trusting HIGH_NET_DEBT's absence")
    flags_pre.extend(_v55_flags(share_scale, share_basis, base_override, market_cap_basis, sbc_recon, periods,
                                hist, facts, overrides, capex_assembly, raw_missing, last3_periods, override_checks))
    sector_u = (uni.get(ticker) or {}).get("sector", "")
    if sector_u in ("Finance", "Real Estate", "Utilities"):  # v5: was Finance only — IRM (REIT) and ED/PCG/PEG (utilities) slipped through unflagged
        flags_pre.append(f"SECTOR_MODEL_MISMATCH: {sector_u} sector — OE/capex DCF fits {sector_u.lower()} names poorly; grade confidence low")

    # ---- v5 DATA GATE: missing data must never silently become zero again. ----
    # Gaps are judged on the FILED values (raw_missing), before any override fill.
    # (last3_periods / currency_gap are computed above, ahead of the share-scale guard.)
    gap_fields, gap_years = [], {}
    for field in ("sbc", "capex", "shares", "ocf"):
        missing = [p[:4] for p in last3_periods if p in raw_missing[field]]
        if missing: gap_fields.append(field); gap_years[field] = missing
    # v5.5 (decision 2): two share gaps no override can cover — a declared
    # share-class mismatch, and mis-scaled share counts not carried by a
    # declared base_override pin.
    if share_class and share_class.get("declared"): gap_fields.append("share_class")  # M5: a {"malformed"} record raises no gap
    if share_scale["defect"] and not share_scale["rescued_by_pin"]: gap_fields.append("share_scale")
    if currency_gap: gap_fields.append("currency")
    if price is None: gap_fields.append("price")
    # A gap is covered only if a judgment override actually filled that field.
    covered = [f for f in gap_fields if f in ("capex", "sbc", "shares") and filled[f]]
    uncovered = [f for f in gap_fields if f not in covered]
    for f in covered:
        _ov_note = ""
        _ina = {p: v for p, v in intang_not_added.items() if v}   # [ADDITION — ruling E6] a $0 leg is never listed
        if f == "capex" and _ina:
            _ov_note = (" — intangible purchases filed for " + ", ".join(f"FY{p[:4]} ({v:,.0f})" for p, v in sorted(_ina.items()))
                        + " were not added on top of the override; if the override excludes them, revise it to the total")
        flags_pre.append(f"OVERRIDE_APPLIED:{f} — filing gap in the last 3 FY filled by a judgment override "
                         f"({overrides[f]['kind']}: {overrides[f]['source']}); an override never replaces a filed "
                         f"value — see overrides_applied and override_impact{_ov_note}")
    if uncovered and not MEASURE:
        gap_flags = []
        # [ADDITION — ruling E4] name the filed counts <= 0 that the gate treated as not filed
        _np = [x for x in nonpositive_counts if x["period"] in last3_periods and x["series"] == "shares_diluted"]
        _nonpos_note = ("; a filed count <= 0 is not a share count and was treated as not filed ("
                        + ", ".join(f"FY{x['period'][:4]} {x['tag']} {x['value']:,.0f}" for x in _np) + ")") if _np else ""
        for f in uncovered:
            if f == "currency": gap_flags.append("DATA_GAP:currency — last-3-FY core facts are filed in a non-USD currency that could not be converted to USD (mixed reporting currencies, or no ECB reference rate for the currency) — no tier emitted")
            elif f == "price": gap_flags.append("DATA_GAP:price — no price available from Nasdaq, --price, or the universe file — no tier emitted")
            elif f == "share_class":
                gap_flags.append("DATA_GAP:shares — SHARE_CLASS_MISMATCH: judgment.json declares that the filed share count is a different class "
                                 f"from the traded security ({share_class.get('source') or 'no source given'}); no per-share base can be priced "
                                 "against the traded share — NEEDS_MAIN_AGENT — no tier emitted")
            elif f == "share_scale":
                _rej = (f"; the --base-oe-ps pin {base_override:.6g} does not carry it: {'; '.join(share_scale['pin_rejected'])}"
                        if share_scale.get("pin_rejected") else "")   # [ADDITION — ruling E1]
                gap_flags.append(f"DATA_GAP:shares — SHARE_SCALE: {'; '.join(share_scale['reasons'])}; the filed diluted share counts look "
                                 "mis-scaled (thousands filed as units or a mixed basis), so no per-share figure is reliable — NEEDS_MAIN_AGENT; "
                                 "an already-declared base_override pin is honoured (judgment.json base_override equal to the --base-oe-ps "
                                 f"pin within 0.1%, the pin itself within 20x the price){_rej}{scale_growth_note(share_scale)} — no tier emitted")
            elif f == "shares" and any(p in share_fallback for p in last3_periods if p[:4] in gap_years[f]):
                _fbs = "; ".join(f"{p[:4]}: {share_fallback[p][0]:,.0f} ({share_fallback[p][1]})" for p in last3_periods if p in share_fallback)
                gap_flags.append(f"DATA_GAP:shares — DILUTED shares missing for fiscal year(s) {', '.join(gap_years[f])} of the last 3; only a non-diluted count is filed ({_fbs}) — no silent swap (v5.4). Declare shares_override kind \"filing\" from the 10-K EPS note{_nonpos_note} — no tier emitted")
            else: gap_flags.append(f"DATA_GAP:{f} — {f} missing for fiscal year(s) {', '.join(gap_years[f])} of the last 3{_nonpos_note if f == 'shares' else ''} — no tier emitted")
        result.update({"tier_by_numbers": None, "implied_irr_weighted": None, "implied_irr_base": None,
                       "moat_score": moat, "cap_years": round(cap_years, 1), "g_terminal": gterm,
                       "data_gap": gap_fields, "data_gap_uncovered": uncovered,
                       "overrides_applied": overrides_applied,
                       "fragility_flags": gap_flags + flags_pre,
                       "note": "DATA_GAP: required filing data is missing (see data_gap / data_gap_uncovered). v5 never emits a tier on an uncovered data gap — a missing value is not a zero."})
        result["content_hash"] = _content_hash(result)
        folder = f"{BASE}/{ticker}"; os.makedirs(folder, exist_ok=True)
        with open(f"{folder}/financials_history.csv", "w", newline="", encoding="utf-8") as f:
            if hist:
                w = csv.DictWriter(f, fieldnames=list(hist[0].keys())); w.writeheader(); w.writerows(hist)
        json.dump(result, open(f"{folder}/dcf_numbers.json", "w", encoding="utf-8"), indent=1)
        print(f"DATA_GAP for {ticker}: {', '.join(uncovered)} — no tier emitted (dcf_numbers.json written with data_gap + flags)")
        print(json.dumps(result, indent=1))
        sys.exit(3 if uncovered == ["price"] else 4)  # price-only failure exits like NO_DATA, never Tier F

    # v5.4: the valuation math lives in module-level functions (project_path /
    # present_value / solve_irr / tier_for_irr) shared with the HTML builder
    # and the test-suite. The fade: growth HOLDS at g0 for 2 years (near-term
    # prints have visibility; v3 faded from year 1), then converges LINEARLY
    # to the terminal rate over cap_years — in EITHER direction.
    labels = ["super_bear", "bear", "base", "bull", "super_bull"]
    if oe_ps and oe_ps > 0 and price:
        # Blended growth (median of share-adjusted rev CAGRs / latest YoY and the raw OE/ps CAGR),
        # capped [-5%, 35%] (cap history: 20% until 2026-10-12 — see README Fixes & lessons).
        g_base = max(GROWTH_FLOOR_BASE, min(GROWTH_CAP_BASE, g_blend))
        scenarios, all_flows, capped_labels, floor_labels = {}, [], [], []
        paths, gpaths = {}, {}
        for i, label in enumerate(labels):
            g0 = max(GROWTH_FLOOR_START, min(GROWTH_CAP_START, g_base + offsets[i]))
            flows = project_path(oe_ps * mults[i], g0, cap_years, gterm)
            all_flows.append(flows)
            paths[label] = [round(f, 6) for f in flows]
            gpaths[label] = [round(g, 6) for g in growth_path(g0, cap_years, gterm)]
            _irr, _capped, _floor = solve_irr(flows, price, gterm)
            if _capped: capped_labels.append(label)
            if _floor: floor_labels.append(label)
            scenarios[label] = {"prob": round(probs[i], 4), "g_start": round(g0, 4), "oe_mult": mults[i],
                                "iv_at_10": present_value(flows, 0.10, gterm), "iv_at_12": present_value(flows, 0.12, gterm),
                                "iv_at_15": present_value(flows, 0.15, gterm), "iv_at_20": present_value(flows, 0.20, gterm),
                                "iv_at_25": present_value(flows, 0.25, gterm), "irr": _irr, "irr_at_floor": _floor}
        wflows = [sum(probs[i] * all_flows[i][t] for i in range(5)) for t in range(PROJECTION_YEARS)]
        paths["weighted"] = [round(f, 6) for f in wflows]
        _wirr, _wcapped, _wfloor = solve_irr(wflows, price, gterm)
        if _wcapped: capped_labels.append("weighted")
        if _wfloor: floor_labels.append("weighted")
        weighted = {"iv_at_10": present_value(wflows, 0.10, gterm), "iv_at_12": present_value(wflows, 0.12, gterm),
                    "iv_at_15": present_value(wflows, 0.15, gterm), "iv_at_20": present_value(wflows, 0.20, gterm),
                    "iv_at_25": present_value(wflows, 0.25, gterm), "irr": _wirr, "irr_at_floor": _wfloor}
        irr = weighted["irr"]
        tier = tier_for_irr(irr)
        irr_bear, irr_bull = scenarios["bear"]["irr"], scenarios["bull"]["irr"]

        # ---- diagnostics & scenario-dependent fragility flags (flags_pre, computed before
        # this branch, carries the rest — the agent MUST address every flag in analysis.md) ----
        flags = list(flags_pre)
        if capped_labels:
            flags.append(f"IRR_CAPPED: implied IRR exceeds the 200% solver cap at the current price ({', '.join(capped_labels)}) — recorded as 2.0 (capped); the stock is cheaper than the solver's range, not a D")
        if floor_labels:
            flags.append(f"IRR_AT_FLOOR: implied IRR sits within 0.5pp of terminal growth {gterm*100:.1f}% ({', '.join(floor_labels)}) — a perpetuity growing at g has an IRR above g at any price, so the model cannot express a return below ~{gterm*100:.1f}%; this price is beyond the model's range and the expected return is 'at most ~{(gterm+0.005)*100:.1f}%', not the recorded figure")
        if oe_ps_latest and oe_ps_norm and oe_ps_norm > 0 and abs(oe_ps_latest / oe_ps_norm - 1) > 0.35:
            flags.append(f"BASE_DIVERGENCE: latest FY OE/share {oe_ps_latest:.2f} vs 3-yr median {oe_ps_norm:.2f} — one of them is distorted; find out which and why")
        oe_yield = oe_ps / price
        if oe_yield < 0.02: flags.append(f"LOW_OE_YIELD: base OE yield {oe_yield*100:.1f}% — valuation rests almost entirely on growth; tier is fragile")
        tvs = terminal_share(wflows, 0.15, gterm)
        if tvs and tvs > 0.70: flags.append(f"HIGH_TV_SHARE: terminal value is {tvs*100:.0f}% of IV@15% — result is mostly a terminal assumption")
        ivsb, ivsbu = scenarios["super_bear"]["iv_at_15"], scenarios["super_bull"]["iv_at_15"]
        spread = (ivsbu / ivsb) if ivsb and ivsb > 0 else None
        if spread and spread > 4: flags.append(f"WIDE_SCENARIO_SPREAD: super-bull IV is {spread:.1f}x super-bear IV — uncertainty is huge; confidence should not be high")
        # v5.5 (decision 1): per-ADS OE × the ADS count (shares ÷ ads_ratio) — the
        # same basis as market_cap_est; the 5.4 product was per-ADS OE × ordinary shares.
        base_oe_total_norm = (None if share_scale.get("leverage_unverifiable")   # [ADDITION — ruling E3]
                              else normalized_oe_total(oe_ps, shares_for_cap, ads_r))
        nd_ratio = (net_debt / base_oe_total_norm) if (net_debt is not None and base_oe_total_norm) else None
        if nd_ratio is not None and nd_ratio > 3: flags.append(f"HIGH_NET_DEBT: net debt is {nd_ratio:.1f}x normalized OE — levered OE can vanish fast; stress the bear cases")
        if nd_ratio is not None and nd_ratio < -2: flags.append(f"BIG_NET_CASH: net cash is {-nd_ratio:.1f}x normalized OE — part of the price is a cash pile, not the operating business; note it in the verdict")
        tier_bear, tier_bull = tier_for_irr(irr_bear), tier_for_irr(irr_bull)
        if tier_bear != tier_bull:
            flags.append(f"TIER_BAND: bear-case tier {tier_bear} ({irr_bear*100:.1f}%) vs bull-case tier {tier_bull} ({irr_bull*100:.1f}%) — the verdict spans tiers; size any position to the bear end")
        result.update({"g_base": g_base, "moat_score": moat, "cap_years": round(cap_years, 1), "g_terminal": gterm,
                       "inputs": {"moat": moat, "probs": probs, "offsets": offsets, "mults": mults,
                                  "g_terminal": gterm, "base_oe_ps_arg": base_override, "base_pin_source": pin_source},
                       "data_gap": gap_fields, "data_gap_uncovered": uncovered,
                       "overrides_applied": overrides_applied,
                       "scenarios": scenarios, "weighted": weighted,
                       "paths": paths, "growth_paths": gpaths,
                       "implied_irr_weighted": irr, "implied_irr_base": scenarios["base"]["irr"],
                       "irr_bear": irr_bear, "irr_bull": irr_bull,
                       "irr_low": min(s["irr"] for s in scenarios.values()), "irr_high": max(s["irr"] for s in scenarios.values()),
                       "tier_by_numbers": tier, "tier_bear": tier_bear, "tier_bull": tier_bull,
                       "hurdle_prices": {"15": weighted["iv_at_15"], "20": weighted["iv_at_20"], "25": weighted["iv_at_25"]},
                       "upside_at_15": weighted["iv_at_15"] / price - 1, "upside_at_12": weighted["iv_at_12"] / price - 1,
                       "iv_at_15": weighted["iv_at_15"], "iv_at_12": weighted["iv_at_12"],
                       "iv_at_20": weighted["iv_at_20"], "iv_at_25": weighted["iv_at_25"],
                       "diagnostics": {"oe_yield": oe_yield, "tv_share_at_15": tvs, "scenario_spread_iv15": spread,
                                       "net_debt_to_normalized_oe": nd_ratio, "months_since_fy_end": months_stale,
                                       "irr_capped": bool(capped_labels), "irr_at_floor": bool(_wfloor)},
                       "fragility_flags": flags})
    else:
        # v5.4: Tier F is split — "SBC exceeds cash generation" and "no cash
        # generation" are different stories (audit round-1, Model design).
        # Codex review of PR #2: classify on the SAME basis that produced the
        # non-positive base — the ttm.json legs for a TTM pin, else the last
        # three fiscal years (the median window) summed — and actually test
        # SBC against FCF, never the latest year alone.
        f_fcf = f_sbc = None
        f_basis = None
        if pin_source == "ttm_json":
            try:
                with open(f"{BASE}/{ticker}/ttm.json", encoding="utf-8") as _f:
                    _t = json.load(_f)
                f_fcf = float(_t["ttm_ocf"]) - float(_t["ttm_capex"]); f_sbc = float(_t["ttm_sbc"]); f_basis = "ttm.json legs (TTM pin)"
            except Exception:
                f_fcf = f_sbc = None
        if pin_source == "judgment_base_override" and payable_base:
            # The non-positive base is the five-year payable average: classify
            # on that, not on OCF/capex/SBC, which may well be positive here.
            f_basis = "five-year average of operating income available to common (payable pin)"
            f_fcf, f_sbc = None, None
        elif f_fcf is None:
            _w = [h for h in hist[-3:] if h.get("fcf") is not None]
            if _w:
                f_fcf = sum(h["fcf"] for h in _w); f_sbc = sum((h.get("sbc") or 0) for h in _w)
                f_basis = f"sum of the last {len(_w)} fiscal years (the median window)"
        if oe_ps is None:
            f_subtype = "no_base"
        elif pin_source == "judgment_base_override" and payable_base:
            f_subtype = "payable_earnings_nonpositive"
        elif f_fcf is None:
            f_subtype = "indeterminate"
        elif f_fcf <= 0:
            f_subtype = "no_cash_generation"
        elif f_sbc is not None and f_sbc >= f_fcf:
            f_subtype = "sbc_exceeds_cash"
        else:
            f_subtype = "indeterminate"  # FCF > SBC on this basis yet the base is non-positive (an agent-supplied pin without legs)
        result.update({"tier_by_numbers": "F", "f_subtype": f_subtype, "f_subtype_basis": f_basis,
                       "implied_irr_weighted": None, "implied_irr_base": None, "moat_score": moat,
                       "cap_years": round(cap_years, 1), "g_terminal": gterm,
                       "inputs": {"moat": moat, "probs": probs, "offsets": offsets, "mults": mults,
                                  "g_terminal": gterm, "base_oe_ps_arg": base_override, "base_pin_source": pin_source},
                       "data_gap": gap_fields, "data_gap_uncovered": uncovered,
                       "overrides_applied": overrides_applied,
                       "fragility_flags": flags_pre,  # v5: F names carry their flags too
                       "note": "No positive NORMALIZED (3-yr median) conservative owner's earnings — OE DCF not supportable on numbers alone. If the latest year alone is positive, that is a flag to investigate, not a pass."
                               + (f" F sub-type: payable earnings non-positive (five-year average operating income available to common {payable_base['average']:,.0f} on the --base-judgment pin; OCF-based OE is not the basis here)." if f_subtype == "payable_earnings_nonpositive"
                                  else " F sub-type: SBC exceeds cash generation (OCF - capex is positive; SBC consumes it)." if f_subtype == "sbc_exceeds_cash"
                                  else " F sub-type: no cash generation (OCF - capex is not positive)." if f_subtype == "no_cash_generation" else "")})

    if overrides_applied and not MEASURE:
        result["override_impact"] = _override_impact(ticker, price,
                                                     result.get("base_oe_per_share"),
                                                     result.get("implied_irr_weighted"))
    result["content_hash"] = _content_hash(result)
    folder = f"{BASE}/{ticker}"; os.makedirs(folder, exist_ok=True)
    if not MEASURE:
        with open(f"{folder}/financials_history.csv", "w", newline="", encoding="utf-8") as f:
            if hist:
                w = csv.DictWriter(f, fieldnames=list(hist[0].keys())); w.writeheader(); w.writerows(hist)
        json.dump(result, open(f"{folder}/dcf_numbers.json", "w", encoding="utf-8"), indent=1)
    print(json.dumps(result, indent=1))

if __name__ == "__main__":
    main()
