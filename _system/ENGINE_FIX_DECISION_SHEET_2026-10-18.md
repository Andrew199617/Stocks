# Engine-fix decision sheet — one ruling pass (prepared 2026-10-18)

Status: PREPARED, not implemented. Engine untouched (v5.4.0 live).
Update 2026-10-19: item 2 (ADS market cap) was ruled and implemented on
2026-10-18 (Andrew) — see ADS_MARKET_CAP_SPEC_DRAFT.md, now marked
IMPLEMENTED; the other five items remain unimplemented.
Sweep state at preparation: 432 scored folders of 2,617 (checked 2026-10-18
~17:55 UTC from ~/workspace/stocks/*/score.json count).

Six spec drafts are sitting in _system/, each surfaced to Andrew piecemeal.
This sheet consolidates them so they can be ruled on in one pass.
Six names are blocked solely by these defects today: DD, TLK, ELS, JLL,
PUK, CX.

## The six, smallest/safest first

| # | Spec file | One-line fix | Cases | Blocked | Risk if not fixed |
|---|-----------|--------------|-------|---------|-------------------|
| 1 | CAPEX_TAG_CAPITAL_IMPROVEMENTS_SPEC_DRAFT.md (2026-10-18) | Append `PaymentsForCapitalImprovements` to the capex tag list in BOTH dcf_engine.py (~line 574) and ttm.py CAPEX_TAGS — append at end, so it only fills gaps, never displaces a filed PPE value | 6: ELS blocked; CR, IT, MAA, RBC, SNA scored via single-value overrides with disclosed per-year distortions | ELS | Every REIT / capital-improvements filer hits the same hole; overrides distort per-year capex |
| 2 | ADS_MARKET_CAP_SPEC_DRAFT.md (2026-10-18) | `market_cap_est = price * shares / ads_ratio` in dcf_engine.py (line 950 area) — one formula, handles ratio >1 and <1 (FMS 0.5 proves direction) — **IMPLEMENTED 2026-10-18** | 8: TLK blocked; JD, CHT, VOD, PAC, TS, WF scored with falsified scope flags; FMS understated 2x | TLK | Scope flags keep lying; VOD's corrected cap lands near the $40B line, so its in/out-of-sweep call is currently being made on a 10x-wrong number |
| 3 | USD_OVERRIDE_FX_SPEC_DRAFT.md (2026-10-17) | Fix `_override_usd()` (~line 761): a filing override already in USD should not demand a foreign-currency ECB rate for every fill period | 2, both blocked | PUK, CX | USD-reporting filers with stray historical FX facts stay unscoreable despite clean filing overrides on file |
| 4 | SBC_TAG_PRIORITY_SPEC_DRAFT.md (2026-10-17) | SBC tag merge: `ShareBasedCompensation` is not always the total (JLL: $2.7M slice vs $114.7M total, ~40x). Needs a merge/priority rule, not just a reorder — see spec for the 6-name EDGAR retro-check | 1 blocked + silent-understatement risk wherever both tags are filed | JLL | SBC understated ~40x on exposed filers = OE overstated; this one can corrupt scored names silently, not just block |
| 5 | SHARE_BASIS_SPEC_DRAFT.md (updated 2026-10-18, 7 cases) | Share-basis guard: sanity-check OE/share and implied share count against price / latest dei outstanding / ADS ratio; refuse or flag scale breaks (thousands filing, post-filing splits) instead of trusting filed counts | 7: NTNX, VIV (fake Tier S, worker-caught, corrected), DD (blocked), WF, TEM, BNT, IESC (blocked, 2-for-1 split 2026-08-21 post-dates filings) | DD, IESC | The recurring class: 7 verified instances, 2 fake Tier S prints. Workers have caught every one so far — that is the current guard, and it is human |
| 6 | TELECOM_CAPEX_SPEC_DRAFT.md (2026-10-14) | Policy, not just code: add a total-capex leg for telecoms (spectrum + intangible capex + lease principal + cash interest) or keep handling by manual tier override (VOD precedent: printed Tier S at 32.57% on a base ~4x too high; real adj. FCF €2.5B vs engine OE $11.8B) | VOD scored/overridden; CHT, ERIC exposed next | none blocked | Fake-high tiers on every IFRS telecom until ruled; the only one of the six that is a modelling-policy call rather than a bug fix |

## Suggested ruling order

1–3 are narrow bug fixes with regression shapes already written out in
their specs (synthetic cases, bit-identical non-affected names). They
unblock ELS, TLK, PUK, CX and clean up 13 already-scored records' scope/
capex basis.
4 is a bug fix but the merge rule needs Andrew's eye on the spec's
proposed priority logic before implementation.
5 is the biggest build (a new guard) and the highest recurrence count —
it is also the one where "workers catch it" has worked 7/7 so far, so it
is the most defensible to defer explicitly rather than leave ambiguous.
6 is a policy decision (total-capex leg vs manual override precedent),
separate from the code fixes.

## What a "yes" triggers (per standing workflow)

- Implementation on the engine, regression checks named in each spec run
  BEFORE any re-score (APP/STZ/CCJ exact-match pattern from the 5.4 port).
- Blocked names re-run: make_score + enrichment + queue done + build_site.
- Already-scored affected names re-run only where their spec lists them
  (ADS: JD, CHT, VOD, PAC, TS, WF, FMS scope only, tiers unchanged;
  capex-tag: CR, IT, MAA, RBC, SNA without their overrides).
- Nothing here touches pass 2 (still paused) or the alert gates
  (low-confidence S/A suppression stays stripped, per 2026-10-16 ruling).

## Addendum — 2026-10-18 22:13 UTC (after this sheet was delivered)

A 7th spec arrived after preparation, from the AR (Antero Resources)
pass-1 run. It is NOT covered by items 1–6 above and needs its own ruling:

| # | Spec file | One-line fix | Cases | Blocked | Risk if not fixed |
|---|-----------|--------------|-------|---------|-------------------|
| 7 | EP_CAPEX_TAGS_SPEC_DRAFT.md (2026-10-18) | Additive E&P capex component group: when the roll-up `PaymentsToAcquirePropertyPlantAndEquipment` is absent for a period, sum the filed components (`PaymentsToExploreAndDevelopOilAndGasProperties` + `PaymentsToAcquireOilAndGasProperty` + `PaymentsToAcquireOtherPropertyPlantAndEquipment`, …); when the roll-up IS present it stays authoritative (FY2022 proves roll-up = sum of components, never sum both). Apply in both dcf_engine.py and ttm.py | AR blocked (worse variant — see below); APA scored Tier C via single-value override (different variant, gate worked); PR is an E&P on the retro-check list, not yet scored | AR | Silent fake tiers on E&Ps, not just blocks |

Why AR is the worse variant: AR *does* file a candidate capex tag
(`PaymentsToAcquireOtherPropertyPlantAndEquipment` at $5.4M FY2025), so no
DATA_GAP fires and the fill-only `capex_override` cannot help. The engine
scored AR on ~0.5–1.5% of true capex ($5.4M counted of $944M FY2025 true,
components summed from EDGAR companyfacts). Preliminary print was a fake
Tier B (weighted IRR 17.27%, IV@15 $46.92 at $38.65); corrected 3-yr median
base is $0.21/sh vs the engine's $2.95/sh (~14× overstatement). The worker
blocked it NEEDS_MAIN_AGENT rather than stamp a hand-sized tier.
Regression shape is in the spec: AR FY2022 must stay $943,971,000
bit-identical (roll-up present); FY2023–25 must print the summed totals;
APA must reproduce override-free.

Ruling note: items 1–3 were suggested as the narrow/safe first batch.
Item 7 has the same shape (tag list + regression cases written) but is
additive-sum logic, not a simple append — read the spec's roll-up-vs-sum
guard before ruling.

## Not in this sheet

Sector/definition calls that are not engine bugs: IBKR, PRU, SUNB capex
packets, ESS REIT capex definition, AER flight-equipment capex, CRBG —
those remain separate decisions and are not unblocked by any fix above.
