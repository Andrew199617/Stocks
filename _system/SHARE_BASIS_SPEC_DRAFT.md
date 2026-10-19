# DRAFT SPEC — Share-basis guard for the DCF engine (v5.4.0)

Status: DRAFT, prepared 2026-10-16 (proactive research run). Not implemented.
Engine untouched. Decision needed from Andrew: implement, implement a
subset, or keep relying on workers catching these by hand.
Updated 2026-10-18: BNT and IESC added — seven cases. (Both workers
independently called theirs "the sixth instance"; they are #6 and #7.)

This consolidates seven separate incidents that were surfaced to Andrew
piecemeal (NTNX and VIV as fake-Tier-S alerts on 2026-10-16, DD as a blocked
name in the 5.4 port report, WF as a note inside its analysis.md, TEM added
2026-10-17, BNT and IESC added 2026-10-18). They are
one defect family: the engine trusts filed share counts and its own
market-cap estimate without ever checking them against the traded price,
the latest dei outstanding count, or the ADS ratio it already applied.

## The seven verified cases

1. **NTNX (Nutanix) — share counts filed in thousands.**
   Weighted-average share counts are filed in thousands and read as units,
   inflating OE/share ~1,000x (base $1,355/share vs a $69.98 stock) and
   printing a fake Tier S at the IRR cap. Worker caught it; corrected with
   a bounded base_override ($1.3553/share, cross-checked against the 10-K's
   printed diluted EPS). Final: Tier D, weighted IRR 5.71%.

2. **VIV (Telefônica Brasil) — thousands + pre-transaction basis.**
   FY2023/24 diluted counts in `financials_history.csv` are 1,658,604 /
   1,643,132 (thousands, pre-transaction) against FY2025's 3,195,606,352
   (post-transaction); FY2022 prints 1,663,556,731,000. Median base came
   out $1,034.28/ADS — another fake Tier S. Worker caught it; corrected
   with ads_ratio 2 (FY2025 20-F) plus a base_override pinning the base to
   the one clean year: $1.2804/ADS. Final: Tier C, weighted IRR 14.57%.
   (Detail: `~/workspace/stocks/VIV/analysis.md`.)

3. **DD (DuPont) — reverse split post-dating the last 10-K. BLOCKED, not scored.**
   A 1-for-3 reverse split effective 2026-06-24 (Q2 2026 10-Q) post-dates
   the FY2025 10-K, so the engine's share history is pre-split (419.2M
   diluted) while price and TTM are post-split. `market_cap_est` printed
   $55.6B (real: ~$17.5B; 135,042,975 shares outstanding per the 10-Q
   filed 2026-08-04) and make_score refused `in_scope_under_40b=true`.
   The DCF work is finished and saved in `~/workspace/stocks/DD/` —
   TTM base $4.8032/share, weighted IRR 6.59%, IV@15 $42.35 vs $132.70,
   Tier D — but no score can be emitted. `shares_override` cannot fix it:
   the engine applies an override only where no diluted tag is filed, and
   here a (stale-basis) tag *is* filed. Queue status: `blocked_no_data`,
   NEEDS_MAIN_AGENT: shares. This is the first case where the defect
   *blocks* a name instead of corrupting one.

4. **WF (Woori Financial) — market cap ignores the ADS ratio it applied.**
   The engine applied ads_ratio 3 (per-share figures are per ADS), then
   computed `market_cap_est` = per-ADS price ($70.07) x ordinary share
   count = $52.03B — a 3x overstatement. make_score therefore read the
   name as out-of-scope and judgment.json's `in_scope_under_40b` was set
   false *to match the computed value*, even though the actual KRX cap is
   KRW 23.72T (genuinely in scope). Scored Tier D anyway, with the
   artifact documented only in `~/workspace/stocks/WF/analysis.md`.

5. **TEM (Tempus AI) — share counts filed in thousands, negative base.**
   FY2025 diluted shares filed as 174,264 (thousands scale; ~174M actual),
   so the normalized base printed -$3,932.44/share against a $64.72 price
   and `market_cap_est` printed $11,278,366.08 — 1,000x too *small*
   (real cap approaches $12B). Worker caught it; corrected with a bounded
   base_override built from the run's own outputs (dcf_numbers base
   ÷ 1,000 = -$3.9324/share; same construction as NTNX). Final: Tier F,
   no fake tier — the base was negative either way, so this instance
   corrupts the recorded per-share base and market-cap estimate rather
   than the tier. Filing proof in `~/workspace/stocks/TEM/analysis.md`
   (filed diluted EPS -$1.41 on net income -$245.0M only reconciles at
   ~174M shares; Q3 2025 10-Q cover: 172,863,470 Class A + 5,043,789
   Class B outstanding).

6. **BNT (Brookfield Wealth Solutions) — filed count is a different class
   from the traded share. BLOCKED, not scored.**
   The only share count EDGAR carries (224,030,265 weighted basic, FY2025)
   is Class C — Brookfield's non-traded residual stake. The FY2025 20-F
   (Notes 23/25) states EPS is presented for Class C only and is "not
   applicable" to the traded Class A exchangeable shares (59,934,825
   outstanding), each of which is exchangeable 1:1 into a Brookfield Corp
   Class A share and tracks BN's price ($36.54), not BNT's consolidated
   OE. The engine's $21.37/sh base divides consolidated OE by the Class C
   count and prices it against the Class A price; `market_cap_est`
   $8,186.1M repeats the mix-up (traded class alone ≈ $2.2B). No scale
   factor fixes this — the two classes are different claims, not the same
   claim at a different scale — and the class-attributable OE split
   ($750M Class C / $16M Class A+B / $97M NCI of $863M FY2025 NI) appears
   in none of the run's outputs, so no in-bounds override exists. A
   secondary DATA_GAP:sbc compounds it: no SBC figure is disclosed or
   tagged anywhere in the 20-F. Queue status: blocked, NEEDS_MAIN_AGENT:
   shares. (Detail: `~/workspace/stocks/BNT/analysis.md`, which itself
   proposed adding BNT to this spec as a sixth case.)

7. **IESC (IES Holdings) — forward split post-dating all filings.
   BLOCKED, not scored.**
   A 2-for-1 forward split (record 2026-08-14, distribution 2026-08-21,
   announced in the Q3 FY2026 release 2026-07-31) post-dates every filing
   the engine reads: FY2025 10-K diluted 20,182,797 and Q3 FY2026 10-Q
   dei outstanding 19,924,356 (2026-07-27) are pre-split, while the
   $251.96 price is post-split. Every per-share figure printed 2x too
   high — TTM OE/share $10.59 vs ~$5.29 on ~40.37M post-split diluted
   shares; `market_cap_est` $5.09B vs ~$10.2B real. The preliminary run
   printed a Tier C on the corrupted basis; the worker blocked it
   unscored. Same override dead-end as DD: `shares_override` only fills
   missing tags (a stale-basis tag *is* filed), and a `base_override`
   would need the external 2x factor, which fails the "built exclusively
   from this run's outputs" rule. Unblocks on the FY2026 10-K (FY ends
   2026-09-30) restating counts post-split, or on fix #2 below shipping.
   The re-run must also treat the DBM Global acquisition (closed
   2026-10-05, ~$691M) as a basis break. (Detail:
   `~/workspace/stocks/IESC/analysis.md`.)

## Why hand-catching is not enough

NTNX and VIV were caught by workers noticing an absurd base. Both printed
Tier S *before* the catch — a missed catch fires Andrew a fake Tier S
alert (alerts fire regardless of confidence, per his 2026-10-15 call).
DD shows the same family also silently stalls names. The checks below are
mechanical comparisons of numbers the engine already has.

## Proposed changes (engine, narrow)

1. **Share-scale guard (the proposal already put to Andrew 2026-10-16, unanswered).**
   Before emitting a tier, raise DATA_GAP (no tier, no alert) when either:
   - base OE/share is absurd against price (suggested: >20x price), or
   - the implied share count (OE total / OE per share, or the diluted
     count used) diverges from shares outstanding by ~1,000x.
   Catches NTNX and VIV mechanically.

2. **Split-basis check against latest dei outstanding.**
   When the latest dei share count (EntityCommonStockSharesOutstanding
   from the most recent filing, incl. 10-Q/6-K) diverges from the diluted
   history count used for the base by a factor near a filed split factor
   (fundamentals.py already detected DD's tagged 0.333 factor at
   2026-06-30), split-adjust the filed history to the current basis
   instead of scoring/blocking on the stale basis. Fallback if no split
   factor is filed: use the dei count for the market-cap estimate and
   flag SHARE_BASIS_DIVERGENCE. Unblocks DD on its saved work. IESC is
   the second instance of this exact mechanism (forward 2-for-1 instead
   of DD's reverse 1-for-3) and unblocks the same way.

3. **Market-cap estimate must respect ads_ratio.**
   `market_cap_est` = price x (share count / ads_ratio) when the price is
   per-ADS and an ads_ratio has been applied; per-ordinary price x
   ordinary count otherwise. Never mix the two bases. Fixes WF's false
   out-of-scope read and any future ADS name's scope gate.

4. **shares_override applicability — DECISION POINT, not assumed.**
   DD's block exists because overrides only fill *missing* periods.
   Option A: allow a filing-sourced shares_override to replace a filed
   count when the worker documents a split-basis break (expands bounded
   worker authority — Andrew's call). Option B: keep authority as-is and
   let fix #2 handle it in the engine. Recommendation: B for the engine,
   A only as a stopgap if #2 slips.

5. **Traded-class check (new, from BNT).**
   When a filer's EPS note presents EPS for a class other than the traded
   security — or the traded security is an exchangeable/paired share
   whose price tracks a parent — the engine must not divide consolidated
   OE by the filed class count and price it against the traded class.
   Minimum viable form: a worker-declared judgment flag
   (e.g. `share_class_mismatch: true`, filing-sourced from the EPS note)
   that forces DATA_GAP / NEEDS_MAIN_AGENT with no tier and no alert,
   instead of relying on the worker to block by hand. A fully mechanical
   version is not proposed — class structure lives in filing prose, not
   tags — so this case needs the flag route or an explicit exclusion
   list. Andrew's call: flag route, exclusion, or score paired entities
   on a total-capital basis outside the per-share engine.

## Acceptance tests

- NTNX re-run: guard fires on the uncorrected basis (DATA_GAP, no tier);
  with the existing override, reproduces Tier D / $1.3553 base.
- VIV re-run: same — guard fires pre-override; final Tier C reproduced.
- DD re-run from its saved folder: split-adjusted history, market cap
  ~$17.5B, in-scope true, and the saved Tier D score (IRR 6.59%,
  IV@15 $42.35) is emitted with no override.
- WF re-run: market_cap_est ≈ actual cap / ads-corrected, in-scope true,
  Tier D unchanged.
- TEM re-run: guard fires on the uncorrected basis (DATA_GAP, no tier);
  with the existing override, reproduces Tier F / -$3.9324 base and a
  market_cap_est near the real ~$12B, not $11.28M.
- IESC re-run: split check fires on the pre-split basis; split-adjusted
  history reproduces a TTM base near $5.29/share and market_cap_est near
  ~$10.2B, and the name scores with no override (DBM treated as a basis
  break).
- BNT: with the class-mismatch flag set from the FY2025 20-F EPS note,
  the engine emits DATA_GAP / NEEDS_MAIN_AGENT — no tier, no alert, and
  no $21.37/sh base recorded against the $36.54 traded price.
- Regressions bit-identical: APP (B, 18.43%), STZ (D, 9.8%), CCJ (D,
  5.91%) — the same battery used for the 5.4 port.

## What this does NOT do

- No engine change until Andrew approves; DD stays blocked meanwhile.
- No retroactive rescoring beyond the seven named cases' acceptance runs.
- No change to worker override authority unless Andrew picks Option A in §4.
- Does not cover the separate capex-tag pile (telecom spec draft,
  oil & gas drilling tags) — those stay their own decisions.
