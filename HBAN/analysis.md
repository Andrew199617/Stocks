# HBAN — Huntington Bancshares Incorporated
v5 run, 2026-10-14. In scope (engine market cap $22.588B at $15.01, nasdaq_quote_api — on the pre-merger FY2025 share count; still under $40B on the post-merger count, see below). **Finance sector — the OE/capex DCF fits banks poorly; confidence is low by rule, and the tier is a screen result, not a bank valuation. Final tier is softened one notch from tier-by-numbers — see Final verdict.**

All figures below are copied from dcf_numbers.json, financials_history.csv, ttm.json, or the cited search results — none are recomputed.

## What it is
Columbus, Ohio super-regional bank holding company: full-service consumer and commercial banking (deposits, lending, payments, treasury management, wealth, vehicle finance) through Huntington National Bank. The footprint transformed in five months: Veritex (Dallas, Texas) closed October 20, 2025 ($1.7B, $12.0B assets added per the FY2025 10-K summary in search results), then Cadence Bank closed February 1, 2026 in an all-stock deal — 2.475 Huntington shares per Cadence share, roughly 462 million new shares issued (search results, merger filings) — making Huntington the eighth-largest bank in Texas and #1 in Mississippi by deposits, with nearly 1,400 branches in 21 states and roughly $279B of assets at the close. Q2 2026: total assets $284.0B, total revenue $2.86B (+46% YoY, merger-driven), net income $727M, GAAP diluted EPS $0.33 inclusive of $152M of pretax acquisition-related notable items, adjusted EPS $0.39, ROTCE 15.1% (17.5% adjusted), CET1 10.0%, tangible book value/share $9.65 (Q2 2026 release, via search results).

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $2,482,000,000; capex $267,000,000 (PaymentsToAcquirePropertyPlantAndEquipment); SBC $113,000,000 (ShareBasedCompensation, always a real cost).
- **Conservative owner's earnings FY2025: $2,102,000,000 = $1.3968/share** (base_oe_latest_per_share, and also the 3-yr median — the median year prints the same $1.3968).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $2,706,000,000 — above the conservative figure; for a bank both definitions are approximations (loan growth, the real "capex" of a bank, is an investing outflow neither captures), which is exactly the sector-mismatch caveat.
- OE positive 5 of the last 5 fiscal years. Net debt as the engine computes it is $17,221,000,000 (long-term debt minus cash — deposits, a bank's real funding, are not in this figure; see HIGH_NET_DEBT below).
- History shape (financials_history.csv): conservative OE was $2,420,000,000 in FY2023, fell to $1,587,000,000 in FY2024, recovered to $2,102,000,000 in FY2025 — OCF for a bank swings with loan-held-for-sale and balance-sheet flows, so single years are noisy; the median base is the right anchor of the two engine options.

**Base used = normalized median of the last 3 FY OE/share: $1.3968/share.** This is a pre-Cadence (legacy Huntington + Veritex) base — the merger step-up is modelled in the scenario growth starts, not in the base (see DCF section).

**TTM base — run, quoted, and NOT used.** ttm.py (filing-direct) inputs, YTD through Q1 2026 only (ytd_end 2026-03-31):
- OCF: FY $2,482,000,000 − prior YTD $513,000,000 + current YTD $524,000,000 = **TTM $2,493,000,000**
- Capex: FY $267,000,000 − prior YTD $54,000,000 + current YTD $124,000,000 = **TTM $337,000,000**
- SBC: FY $113,000,000 − prior YTD $21,000,000 + current YTD $45,000,000 = **TTM $137,000,000**
- Shares (current-YTD weighted diluted): **1,900,647,000**
- **TTM OE total $2,019,000,000 → TTM OE/share $1.0623**
- Why rejected (ADM/ARES/CBRE precedent in this sweep): the denominator is the distorted leg. The current-YTD share count (1,900,647,000) already carries the ~462M Cadence shares issued February 1, 2026, while the numerator contains Cadence earnings for only part of Q1 and none of the pre-close period — a merger timing mismatch that mechanically depresses per-share OE. It also stops at Q1 2026 even though Q2 2026 has reported (net income $727M, adjusted EPS $0.39). Pinning the base to $1.0623 would print a spurious result on a share-count artifact. The TTM variant is still run and reported as the method-range low end (see Thoughts).

## Moat: 4/10 — weak-to-moderate, standard regional-bank franchise, currently diluted by integration
Justification: a sticky regional deposit franchise and genuine relationship banking (Fair Play consumer brand, middle-market commercial relationships), against a commodity product with no structural pricing power — demonstrated in September 2026 when management cut the 2027 EPS outlook on funding costs and loan/deposit competition — plus full credit/rate-cycle exposure and two unintegrated acquisitions.
- FOR:
  - Sticky core deposit franchise — deposits rose 37% YoY to $223.4B average in Q2 2026 (merger-assisted); local relationship banking in the Midwest, now extended to Texas and the South
  - Fair Play consumer brand — fee transparency (24-Hour Grace, Standby Cash, Early Pay) is a real differentiation in its markets and supports deposit retention
  - Scale step-up — roughly $284B of assets at Q2 2026, #1 deposit share in Mississippi, eighth-largest in Texas; broader fee businesses (payments, treasury, wealth, vehicle finance)
  - Through-cycle profitability on the legacy franchise — OE positive 5 of last 5 FY, Q2 2026 adjusted ROTCE 17.5%
  - Capital return restarting — planned 2027 repurchases raised by $200M to $1.3–1.4B (September 2026 update, via search results)
- AGAINST:
  - Commodity product, no pricing power — deposits and loans are fungible; on September 16, 2026 management cut 2027 EPS guidance to $1.75–1.83 from $1.90–1.93, citing higher funding costs and competition for loans and deposits constraining NIM expansion (via search results)
  - Integration risk, twice over — Veritex (Oct 2025) and Cadence (Feb 2026) both unseasoned; Q2 2026 already carries $152M of pretax acquisition-related notable items, and Cadence system conversion was slated for mid-2026
  - Credit-cycle exposure — a much larger loan book ($189.3B average loans in Q2 2026) bought at the top of a long benign credit stretch; ACL was 1.78% of loans at Q2 2026
  - Capital-constrained growth — CET1 10.0% at Q2 2026, down from 10.2% the prior quarter; buybacks, loan growth and integration all compete for the same capital
  - Dilution overhang in the per-share math — roughly 462M shares issued for Cadence; per-share earnings power has to be re-earned through synergies ($435M annualized cost savings guided on track, per the Q2 2026 call summary in search results)
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Growth recalibration (written reasons): (1) The engine's revenue series is the contract-revenue tag, which for a bank excludes interest income — the CSV revenue line ($881M in FY2018 rising to $1,562M in FY2025) is a fraction of a bank's actual total revenue (Q2 2026 alone printed $2.86B), so rev_cagr_5y (12.06%), rev_cagr_3y (5.82%) and the resulting g_base of 5.22% are not usable as printed (same defect documented in the MTB run). OE/share CAGR 2y is −7.94%, off the FY2023 OCF peak. (2) The base is pre-Cadence, so the early projection years must carry the merger step-up or the model values a bank that no longer exists: management's 2027 EPS outlook of $1.75–1.83 (September 2026, via search results) sits well above the $1.3968 base, and even after the September cut it implies the combined franchise's per-share earnings power steps up from the legacy base before settling to bank-like growth. Scenario starts were therefore set via offsets (−0.1122 / −0.0322 / +0.0578 / +0.1178 / +0.1878 vs g_base) to −6.0 / +2.0 / **+11.0** / +17.0 / +24.0%: the base case's +11% start, held 2 years then faded over the 7.2-year CAP, is the step-up to the guided range followed by low-single-digit bank growth — it is NOT a claim that a regional bank compounds at 11% through a cycle. The bear case (+2.0%) assumes the step-up is mostly eaten by the funding-cost/NIM pressure that caused the September guidance cut plus integration costs; the super bear pairs a credit cycle with a −6.0% start and the 0.75 multiplier. Super-bull +24.0% is below the Q2 2026 merger-inflated revenue print (+46% YoY) and requires full synergy delivery plus the guided ROTCE path; it carries only 10%. Probabilities 10/30/30/20/10 — skewed bear-ward vs the 10/25/30/25/10 default because of the guidance cut and integration load. OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $15.01.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -6.0% | 0.75 | Credit cycle turns on the enlarged loan book; provisions spike, NIM compresses, buybacks halt | $6.17 | 7.35% |
| Bear | 30% | +2.0% | 0.90 | Merger step-up mostly eaten by funding costs and integration; guidance cut proves prescient | $10.11 | 10.91% |
| Base | 30% | +11.0% | 1.00 | Step-up to the guided 2027 EPS range in the first 2 years, then bank-like fade | $15.82 | 15.63% |
| Bull | 20% | +17.0% | 1.10 | $435M cost synergies land, Texas revenue synergies build, $1.3–1.4B buybacks shrink the count | $21.75 | 19.90% |
| Super bull | 10% | +24.0% | 1.25 | Full synergy + ROTCE path delivered, credit stays benign through the CAP | $31.89 | 26.11% |

- **Probability-weighted: IV@15% $15.94 (+6.2% vs price), IV@12% $21.39, IV@10% $27.49, weighted IRR 15.71%, base-case IRR 15.63%**
- **Tier by numbers: B — softened to C in the final tier (see Final verdict).** Diagnostics (dcf_numbers.json): OE yield 9.31%, terminal value 19.7% of IV@15%, scenario spread 5.17x, net debt 8.19x normalized OE, 9.4 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.4 months ago): ttm.py was run and its full inputs are quoted in the OE section; its TTM base ($1.0623/share) was NOT used, for the documented reason that its share denominator (1,900,647,000) is post-Cadence while its numerator is only part-period Cadence, and it stops at Q1 2026 despite Q2 having reported. The median base is used instead, with the merger step-up that a clean TTM would have captured modelled explicitly in the scenario growth starts and checked against the guided 2027 EPS range ($1.75–1.83).
- **SECTOR_MODEL_MISMATCH** (Finance): accepted in full. A bank's OCF-based "owner's earnings" are not its distributable cash — loan growth consumes regulatory capital, provisions are a through-cycle cost the OCF line only partially carries, and bank value is normally judged on ROTCE vs cost of equity and tangible book ($9.65/share at Q2 2026), neither of which this model computes. Confidence is low, and the final tier is softened one notch (HIG/ACGL/ARES precedent in this sweep).
- **WIDE_SCENARIO_SPREAD** (5.17x): real — a bank's outcome range across a credit cycle, now with merger execution layered on, IS wide (super-bear IV $6.17 vs super-bull $31.89). Confidence is low (also mandated by the sector flag), and the verdict is sized to the conservative end.
- **HIGH_NET_DEBT** (8.19x normalized OE): an artifact of applying an industrial leverage lens to a bank. The engine's net debt is long-term borrowings minus cash ($17,221,000,000); it excludes the deposit base that actually funds the bank and the loan book that actually backs it. The leverage that matters is regulatory capital: CET1 10.0% at Q2 2026 (down from 10.2% at Q1 2026), tangible common equity ratio 7.1% — adequate, drifting the wrong way as buybacks and loan growth consume capital, and flagged in the moat AGAINST list. The bear scenarios carry the credit stress this flag asks for.

## My thoughts / overlay
- Method range is the honest headline: the preliminary default run printed Tier C (weighted IRR 14.01%, IV@15% $13.73 at $14.98); the final median-base run with the merger step-up in the growth starts prints B (15.71%); the same final configuration on the ttm.py base prints C (weighted IRR 12.74%, IV@15% $12.12). Defensible inputs span C to B, and the B print sits only 0.71pp above the hurdle on an assumption (the step-up) that has not yet survived a full audited combined year.
- Quality is not the debate: the legacy franchise is a solid, profitable regional with a real deposit brand, and management is guiding to a materially higher per-share earnings level in 2027 even after cutting that guide. The debate is execution and price: two acquisitions in five months, a guidance cut seven months after the Cadence close, CET1 drifting down, and a stock that already pays for the base case.
- Price that clears 15%: on engine numbers the weighted IV@15% is $15.94, essentially the current $15.01 price — no margin of safety. With a margin of safety against the method range, the clearing level is the bear/TTM zone: roughly the bear IV@15% of $10.11 to the TTM-variant weighted IV@15% of $12.12.
- What would change the verdict: two clean combined quarters with CET1 rebuilt, the Cadence conversion completed without deposit attrition, and the 2027 guide re-raised — or a price in the low teens.

## Final verdict
- **Final tier: C** (tier_override from tier-by-numbers B: SECTOR_MODEL_MISMATCH — a bank's OCF-based OE overstates distributable earnings, the weighted IRR of 15.71% clears the hurdle by only 0.71pp on a merger step-up assumption, and both other defensible runs — the default preliminary at 14.01% and the TTM-base variant at 12.74% — print C; softened one notch, HIG/ACGL/ARES precedent, confidence low)
- Confidence: **Low** (sector-model mismatch plus a 5.17x scenario spread; the FY base itself is filing-solid)
- One-liner: Solid super-regional bank, moat 4/10 — engine prints Tier B (weighted IRR 15.71%, IV@15% $15.94 vs $15.01) only by modelling the Cadence step-up into growth, so the final tier is softened to C at low confidence; it clears 15% with a margin of safety only below ~$12; bank-model mismatch, confidence low.
