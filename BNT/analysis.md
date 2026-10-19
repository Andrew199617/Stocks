# BNT — Brookfield Wealth Solutions Ltd.

**STATUS: BLOCKED — NEEDS_MAIN_AGENT: shares. No score.json is emitted and no tier ships.**
The work below is finished and saved so a re-score after the share-basis decision is fast.
Preliminary engine run 2026-10-18 (engine 5.4.0) exited 4 DATA_GAP (sbc, shares) plus
ADS_RATIO_MISSING; the shares gap is not what it first looks like — see the blocker.

## What it is

Bermuda-domiciled Brookfield paired entity (formerly Brookfield Reinsurance Ltd., renamed
September 2024), SEC foreign private issuer filing Form 20-F under U.S. GAAP (CIK 1837429).
Insurance group built by contribution and acquisition inside Brookfield: retail/institutional
annuities (incl. American Equity Life, acquired May 2024; American National), property &
casualty (float ~$8B), life insurance. FY2025 (20-F filed 2026-03-26): revenue $11,635M,
net income $863M, total assets $157,181M, equity $17,917M (financials_history.csv).
Distributable operating earnings FY2025 $1.7B vs $1.4B FY2024 (company year-end release);
annuity sales originated $20B in 2025. Just Group plc (UK) acquisition announced
2025-07-31, guided to close H1 2026 — a further basis break after the last 20-F.

## The blocker: the filed share count is Class C only; the traded share is a different class

- The engine's per-share base divides consolidated owner's earnings by the only share
  count EDGAR carries, `WeightedAverageNumberOfSharesOutstandingBasic`: 224,030,265
  (FY2025), 126,003,542 (FY2024), 64,215,726 (FY2023). Note 25 (Earnings Per Share) of the
  FY2025 20-F shows those are **weighted average Class C shares**, and EPS is presented
  **for Class C shares only**: "Class A exchangeable shares and class B shares are not
  considered participating securities nor considered to be common stock, and consequently
  earnings per share is not applicable to these classes of shares." No diluted EPS is
  presented anywhere in the filing (basic Class C EPS $3.35 / $8.69 / $10.51).
- Note 23 (Share Capital), Dec 31, 2025: Class A exchangeable shares — the traded BNT
  security — 59,934,825 outstanding (65,307,416 issued incl. 5,372,591 treasury); Class B
  36,000; **Class C 272,687,160, all held by Brookfield**, carrying amount $12,311M of the
  $13.6B total share capital. Class C is Brookfield's residual capital stake, issued for
  contributed assets (FY2025: 41,670,076 Class C for $3.5B of BAM shares on 2025-06-25,
  5,081,523 for $250M of investments, 24,818,914 against a promissory note; FY2024:
  preferred conversion 53,947,528, AEL consideration funding 26,586,622, plus 18,525,713).
  The 64M→126M→224M weighted-count growth the engine reads as 93.5%/yr "dilution" is
  Brookfield capital contributions, not dilution of the traded class — Class A count
  actually fell in FY2025 on buybacks (2,352,539 shares repurchased).
- The traded Class A share's claim is defined against Brookfield Corporation, not against
  this company's OE: each exchangeable share is exchangeable at the holder's option for
  one Brookfield Class A share (or cash equivalent at Brookfield's election) and receives
  distributions at the same time and in the same amounts as dividends on Brookfield Class
  A shares (FY2025 20-F, Item 7.B / MD&A). Its $36.54 price (dcf_numbers.json, Nasdaq)
  tracks BN, not BNT consolidated OE per any class.
- The economics are split by class in Note 25: of FY2025 net income $863M, $750M is
  attributable to the Class C shareholder, $16M to Class A exchangeable + Class B
  shareholders, $97M to non-controlling interests. There is no class whose per-share OE
  can be set against the $36.54 traded price: the engine's $21.37/sh normalized base
  (median of last 3 FY consolidated OE ÷ Class C weighted count) prices a non-traded
  residual class against an exchangeable share whose value is a Brookfield pass-through.
  `market_cap_est` $8,186.1M is the same mix-up (224.0M Class C × Class A price); the
  traded class alone is ~59.9M × $36.54 ≈ $2.2B, total equity is $17,917M.

## Why no in-bounds fix exists

- `shares_override` kind "filing" from the EPS note — the route the DATA_GAP flag
  suggests — yields the Class C basic count (there is no diluted count in the note to
  take). Scoring on it emits precisely the fake-basis number the v5.4 share-basis family
  (NTNX, VIV, DD, WF, TEM — SHARE_BASIS_SPEC_DRAFT.md) exists to prevent, except no
  scale factor or ADS-style ratio exists to correct it: a Class C share and a Class A
  exchangeable share are different claims, not the same claim at a different scale.
- `base_override` may only be built from figures this run's own outputs printed
  (dcf_numbers.json / ttm.json / financials_history.csv). The class-attributable split
  ($750M / $16M / $97M) appears in none of them, and no attributable-OE ÷ shares ÷ price
  pairing from any single class is economically meaningful for the traded security.
- Secondary gap, also out of bounds: `DATA_GAP:sbc` — EDGAR companyfacts carry no SBC
  tag for this filer in either us-gaap or ifrs-full, for any year. Share-based plans
  exist (BWS Restricted Stock Plan, adopted 2023; escrowed share awards to NEOs), but no
  consolidated share-based compensation expense figure is disclosed or tagged in the
  FY2025 20-F, so there is no "filing" value to declare and no last-filed anchor for an
  "estimate" (the bounded band is 0.1×–10× of the last engine-filed value; there is none).

## Resolved for the re-run (not blockers)

- **ADS_RATIO_MISSING — resolvable, ratio 1.0.** BNT is not an ADS: "American Depositary"
  appears nowhere in the FY2025 20-F; the cover/Item 9 register the Class A exchangeable
  shares themselves, listed directly on NYSE and TSX under "BNT". judgment for the re-run
  should carry ads_ratio {ratio: 1.0, source: FY2025 20-F cover — securities registered
  are the Class A exchangeable shares, listed NYSE/TSX, no depositary/ADS facility}.
- **STALE_FY:** FY2025 ended 2025-12-31 (10 months before this run); 20-F filed
  2026-03-26; interim 6-K results for Q2 2026 filed 2026-08-14 exist. ttm.py is not the
  binding constraint here — the share basis is.
- **BASIS_BREAK_SUSPECT:** real and named — AEL acquisition (May 2024, Class C-funded),
  repeated Brookfield asset/BAM-share contributions for Class C stock (2023–2025), the
  Aug 2024 Class A-1 redesignation, the Oct 9, 2025 three-for-two split of Class A/B
  (Class C not split), Just Group closing after period end. No CAGR in the engine output
  (rev 5y +86.6%, 3y +38.1%, latest YoY −17.5%) describes an organic business.
- **NI_OCF_DIVERGENCE (2023–2025):** insurer accounting — OCF carries premium/float and
  reserve movements; FY2025 net income $863M vs the company's own DOE $1.7B shows the
  same gap from the other side (market/reserve marks hit NI, not DOE). Any eventual
  score inherits SECTOR_MODEL_MISMATCH (Finance) and the standing insurer-float
  softening: an OCF-based OE base capitalizes float, so a numbers-tier would be sized
  down with confidence low regardless.
- **DEBT_TAGS_BLANK:** engine found no debt tag for the latest FY, so net debt is
  unknown from the engine; the filing carries borrowings in Note 21 (Corporate and
  non-recourse borrowings) against total liabilities $139,264M (mostly policyholder
  obligations — leverage verdicts need the note, not the engine).
- **OE_VOLATILE / SHARES_FALLBACK:** both are the Class C contribution history above,
  not traded-class economics.

## What would unblock

A main-agent decision on paired exchangeable structures — e.g. add BNT to the
SHARE_BASIS_SPEC_DRAFT family as a sixth case (different-claims basis, not different
scale), score it on a total-capital basis outside the per-share engine, or exclude it.
Until then any tier printed for BNT would be a fabricated comparison, so none is.

## Engine 5.5 re-score (2026-10-19)

This is a dated addendum. The 2026-10-18 text above stays as written; where this section disagrees with it, this section is current. BNT is still blocked, so make_score was not run and there is no score.json or key_numbers.md. Every figure below comes from the final run's dcf_numbers.json and financials_history.csv: `dcf_engine.py BNT`, engine release 5.5.0, as_of 2026-10-19, default inputs, **exit 4**.

| | Pre-5.5 (2026-10-18, engine 5.4.0, preliminary run) | Engine 5.5.0 (2026-10-19) |
|---|---|---|
| Base OE/share | none (blocked) | none (blocked) |
| Weighted IRR | none (blocked) | none (blocked) |
| Tier (numbers / final) | none (blocked) | none (blocked) |
| Engine exit / data_gap | 4 / sbc, shares | 4 / sbc, shares, share_class |

Both runs still print the mechanical median `base_oe_per_share` $21.37 (consolidated OE ÷ the Class C weighted count). That number was never a base and is not one now: `tier_by_numbers`, `implied_irr_weighted` and `implied_irr_base` are null.

### What this run declared (judgment.json, new file)
- **`share_class_mismatch` {value: true, source, reason}.** This is ruling 2 §5, the flag route (WORKER_SPEC step 8, Engine 5.5). The source cites the FY2025 Form 20-F (filed 2026-03-26): Note 25 Earnings Per Share presents EPS for the Class C shares only, and Note 23 Share Capital shows 59,934,825 Class A exchangeable shares outstanding against 272,687,160 Class C shares, all held by Brookfield. The reason: the only filed share count is the non-traded Class C, while the traded Class A exchangeable share tracks Brookfield Corporation's price. So no per-share base can be priced against the traded share. These are the facts documented in "The blocker" above.
- **`ads_ratio` {ratio: 1.0, source, reason}.** Source: the FY2025 Form 20-F cover and Item 9. The registered securities are the Class A exchangeable shares themselves, listed directly on NYSE and TSX, with no depositary or ADS facility. This is the declaration "Resolved for the re-run" above proposed.
- No moat, probabilities or field overrides were declared, because no tier can be emitted. The engine used its default moat of 5.0 only to fill the record's mechanics.

### What engine 5.5 changed for this filer
- **Share basis: the declared class mismatch (ruling 2 §5).** The engine read the declaration (`share_class_mismatch.declared` true in dcf_numbers.json). It added the gap key `share_class` to `data_gap` and `data_gap_uncovered` and printed `DATA_GAP:shares — SHARE_CLASS_MISMATCH … NEEDS_MAIN_AGENT — no tier emitted`. No `shares_override`, `base_override` or pin covers this gap.
- **Share-scale guard (ruling 2 §1–3): no defect, and it could not catch this case.** `share_scale.defect` is false, with tests (a) and (b) both false. The $21.37 mechanical median is below 20× the $36.54 price. The only cover-page count on file is 15,311,749, dated 2023-12-31. That is more than 18 months before the FY2025 year end, so it is not a usable dei count (`share_scale.dei_count` null) and test (b) has nothing to compare. BNT's counts are not mis-scaled; they belong to another class. No scale test can see that, which is why the declaration route exists.
- **Split basis: nothing rescaled.** `share_basis.split` and `share_basis.divergence` are null. One in-history split fact is recorded: 2025-10-09, ratio 1.5. That is the three-for-two split of the Class A/B shares named under BASIS_BREAK_SUSPECT above; the Class C shares were not split. It is dated before the FY2025 year end, so the engine rescales no count. It should not: the counts it would scale are Class C. `SHARE_BASIS_ADJUSTED` and `SHARE_BASIS_DIVERGENCE` are not raised.
- **Market cap (ruling 1).** The formula is now price × shares ÷ ads_ratio (`market_cap_basis`: diluted_latest, ratio 1.0), and a ratio of 1.0 is the identity. `market_cap_est` is unchanged at $8,186.1M = 224,030,265 × $36.54. It is still the Class C count times the Class A price, the mix-up described above. It is not a traded cap, and with no score.json it sets no scope.
- **Capex (rulings 3–5): the last 3 FY are unchanged.** BNT files no PP&E roll-up, so the additive-component branch reads its one line, `PaymentsToAcquireProductiveAssets` (`capex_source` components): FY2023 $135M, FY2024 $40M, FY2025 $69M, the same as 5.4. The IFRS intangible tag `PurchaseOfIntangibleAssetsClassifiedAsInvestingActivities` is filed only for history years:
  - FY2021: $1M is added (capex $1M → $2M; `capex_tag` `PaymentsToAcquireProductiveAssets+PurchaseOfIntangibleAssetsClassifiedAsInvestingActivities`).
  - FY2020: $1M is not added, because that year has no PP&E leg (`intangibles_not_added: no_ppe_leg`).

  OE for FY2023–25 is unchanged at $1,372M / $4,529M / $2,545M.
- **SBC (ruling 6): no change.** No SBC tag is filed in either taxonomy, and `sbc_provenance` is empty, so nothing was reconciled. `DATA_GAP:sbc` stands for FY2023–25.
- **USD-override branch (ruling 7): not engaged.** BNT reports in USD (`fx_conversion` null), declares no field override, and `overrides_applied` is empty.

### Flags: every new or changed 5.5 flag, by name
- **DATA_GAP:shares — SHARE_CLASS_MISMATCH (new): resolved by blocking, which is the intended outcome.** The filed count is the Class C weighted basic count (224,030,265 for FY2025). The traded security is the Class A exchangeable share, priced as a Brookfield pass-through. Block reason: `NEEDS_MAIN_AGENT: shares — SHARE_CLASS_MISMATCH: FY2025 Form 20-F (filed 2026-03-26), Note 25 Earnings Per Share and Note 23 Share Capital`.
- **ADS_RATIO_APPLIED (replaces 5.4's ADS_RATIO_MISSING): resolved.** The ratio is 1.0 per the 20-F cover and Item 9, so the per-share figures and the cap pass through unchanged. The ads_ratio ground for a make_score refusal is gone. The share-class and SBC grounds remain.
- **Checked and not raised:** SHARE_SCALE_SUSPECT and DATA_GAP:shares — SHARE_SCALE; SHARE_BASIS_ADJUSTED; SHARE_BASIS_DIVERGENCE; CAPEX_COVERAGE_LOW (FY2023 capex of $135M is above half of that year's $50M D&A, so the three-year test fails); SBC_TAG_RECONCILED; OVERRIDE_SUPERSEDED_BY_FILED_TAG; OVERRIDE_APPLIED.
- **Carried from 5.4, with the resolutions above unchanged:**
  - DATA_GAP:sbc: a separate blocker. There is no filed figure and no anchor for an estimate.
  - DATA_GAP:shares (diluted count missing): the `shares_override` route the flag text suggests stays closed, because it would only return the Class C basic count.
  - STALE_FY; DILUTION (93.5%/yr, which is Brookfield's Class C contributions); BASIS_BREAK_SUSPECT; OE_VOLATILE; NI_OCF_DIVERGENCE; SHARES_FALLBACK; DEBT_TAGS_BLANK.
  - SECTOR_MODEL_MISMATCH (Finance): any eventual score has confidence low and the one-notch misfit sizing.

### Why there is no tier
`data_gap` is sbc, shares and share_class, all three uncovered, and the engine exits 4. make_score was not run, so there is no score.json. That means no tier and no alert: neither alert gate exists without a score. BNT stays **NEEDS_MAIN_AGENT: shares — SHARE_CLASS_MISMATCH** (FY2025 Form 20-F Note 25 / Note 23). It is also blocked separately by **DATA_GAP:sbc**, which would still block a score even after a main-agent decision on the share class. queue.py was not run in this pass. The unblock route is the one in "What would unblock" above: a main-agent decision on paired exchangeable structures (a total-capital basis outside the per-share engine, or exclusion), plus a filed SBC figure or a decision on SBC.
