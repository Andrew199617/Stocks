# IOT — Samsara Inc.
v5 run, 2026-10-15. In scope (market cap $23.226B at $40.50, nasdaq_quote_api — under the $40B cutoff).

All figures below are copied from dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed.

## What it is
Connected Operations Platform for physical operations: vehicle telematics and GPS, AI dash cameras / video safety, equipment and asset monitoring, site visibility, and connected workflows/forms, sold as installed hardware plus a cloud subscription, mainly to transportation, logistics, construction, field services, and public-sector fleets. Research (Q2 FY2027 results, quarter ended August 1, 2026): revenue $508.4M, +30% YoY; ending ARR $2.125B, +30% YoY; net new ARR $134.1M, +28% YoY; GAAP EPS $0.03 — the fourth consecutive quarter of GAAP profitability; large-customer momentum is the growth engine (3,605 customers over $100K ARR; the $1M+ ARR cohort generated over $500M of ARR, growing over 50% YoY for the third consecutive quarter).

## Owner's earnings
**FY2026 (10-K via EDGAR, year ended January 31, 2026):** revenue $1,618,635,000 (latest YoY +29.57%); operating cash flow $236,210,000; capex $28,766,000; SBC $314,983,000 (always a real cost in this sweep).
- **Conservative owner's earnings FY2026: −$107,539,000 = −$0.19/share** (latest FY OE/share −$0.1875, dcf_numbers.json).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): −$57,056,000 — also negative; the two definitions agree on the sign.
- **Normalized base used (engine default): median of last 3 FY OE/share = −$0.30/share** (−$0.2991). OE positive in 0 of the last 5 fiscal years.
- Net debt: the engine reports net_debt_latest as null (no debt tags filed under the candidate tags); cash at FY2026 end was $318,789,000 per financials_history.csv. Balance sheet is not the story here either way.
- The blocker is identified, not mysterious: SBC has risen every recent year in the filed history — $237,082,000 (FY2024) → $277,870,000 (FY2025) → $314,983,000 (FY2026) → $330,625,000 TTM — and now exceeds the company's entire operating cash flow. SBC, not capex ($28,766,000 FY2026) or demand, is what makes owner's earnings negative.

**TTM check via ttm.py (filing-direct, through Q2 FY2027 — quoted inputs):**
- OCF: FY $236,210,000 − prior YTD $102,773,000 + current YTD $154,937,000 = **TTM $288,374,000**
- Capex: FY $28,766,000 − prior YTD $12,889,000 + current YTD $17,019,000 = **TTM $32,896,000**
- SBC: FY $314,983,000 − prior YTD $158,214,000 + current YTD $173,856,000 = **TTM $330,625,000**
- Shares (current-YTD weighted diluted): **589,069,554**
- **TTM OE total −$75,147,000 → TTM OE/share −$0.13** (−$0.1276)

The TTM base was NOT pinned via `--ttm`: it is negative, like the median, the latest FY, and the maintenance version. Every defensible base is negative, so no scenario DCF is supportable — the engine's F branch fired. One nuance from recent quarters: the GAAP profitability streak is real but flattered — Q1 FY2027 net income included a $30.3M arbitration gain against Motive Technologies recognized in that quarter (per the Q1 FY2027 release), a one-off that does not change the OCF-minus-SBC picture.

## MOAT: 6/10 — moderate
Justification: a broad, scaled connected-operations platform — installed telematics/camera hardware in the vehicle, years of operational data, and workflow integration create real switching costs, and multi-product expansion inside large accounts is visible in the prints ($1M+ ARR cohort ARR up over 50% YoY). It is not 7+: the fleet-management market is fragmented (top-10 vendors ~13% of revenue in third-party market research), Geotab and Motive contest the same fleets, hardware is increasingly commoditized / OEM-embedded, and Samsara has never converted its position into positive owner's earnings or proven returns on capital through a cycle.
- FOR: installed hardware + cloud platform in vehicles/assets — replacing it means re-instrumenting fleets, retraining, and losing historical data
- FOR: multi-product platform breadth (telematics, video safety, equipment, sites, workflows) driving expansion inside large accounts — $1M+ ARR cohort over $500M ARR, +50%+ YoY
- FOR: scale data asset — ARR $2.125B growing +30% at 77% GAAP gross margin (Q2 FY2027), funding AI features smaller rivals cannot match as easily
- AGAINST: fragmented market with strong direct rivals — Geotab (ABI Research's top-ranked commercial telematics vendor, Samsara second), Motive, Verizon Connect, PowerFleet
- AGAINST: hardware commoditization and OEM-embedded telematics erode the installed-base advantage over time
- AGAINST: no proven pricing power into profitability — SBC-funded talent model has kept owner's earnings negative at every scale so far; physical-operations customers are cost-sensitive and cyclical
- A moat of 6 gives CAP = 9.8 years — moot for the valuation here, since there is no positive OE base to fade.

## DCF — v5 final run (2026-10-15)
Final engine pass: `--moat 6 --probs 0.10 0.25 0.30 0.25 0.10` (default probabilities; offsets/multipliers never reached, because the F branch fires first). Engine output: tier_by_numbers **F**, implied IRR null, weighted IV null. The five scenario slots carry the default likelihoods for the record, each with its story — no IVs or IRRs exist, by design:

| Scenario | Prob | Growth start | OE mult | Story | IV@15% | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | n/a — no OE base | n/a | Freight/industrial downturn cuts seat growth, Motive/Geotab price hard, SBC stays at TTM levels; OE negative indefinitely | n/a (OE < 0) | n/a |
| Bear | 25% | n/a | n/a | Revenue decelerates into the teens while SBC compounds with headcount; first positive OE is late-decade and small vs a $23.2B cap | n/a (OE < 0) | n/a |
| Base | 30% | n/a | n/a | ~25-30% growth persists near term and SBC growth finally slows below OCF growth — OE turns positive, but years too late to support $40.50 on an OE DCF run today | n/a (OE < 0) | n/a |
| Bull | 25% | n/a | n/a | Large-customer expansion and new products hold ~30% growth while SBC flattens in dollars; strongly positive OE by FY2029-30 — value sits beyond the OE screen's base window | n/a (OE < 0) | n/a |
| Super bull | 10% | n/a | n/a | Samsara becomes the default operations OS for physical industries globally and SBC discipline arrives early — a narrative/forward-multiple story, not an owner's-earnings story today | n/a (OE < 0) | n/a |

- **Probability-weighted IV@15% / weighted IRR: not computable — no positive owner's earnings in any base period.**
- Revenue growth is real and verified against prints (5-yr CAGR 45.28%, 3-yr CAGR 35.25%, latest FY +29.57%, Q2 FY2027 +30% with ARR +30%) — growth is not the problem and no scenario-start sanity issue arises. The engine's blended growth (35.25%, at the blend level before the share-count adjustment) is therefore not recalibrated; it is simply unusable on a negative base. The failure is below the revenue line, in SBC.
- **Hurdle math:** there is no price at which IOT "clears 15%" on current owner's earnings, because the earnings themselves are negative after SBC, and therefore no margin-of-safety price can be quoted from this method. At $40.50 the market is paying today for an SBC normalization the filings do not yet show. What would change the verdict: SBC growing materially slower than OCF for several prints, so OCF − capex − SBC turns sustainably positive — the TTM gap (−$75,147,000) is the number to watch.

## FLAGS — every fragility flag resolved
- **STALE_FY** (latest FY ended 2026-01-31, 8 months ago): resolved with ttm.py — TTM OE through Q2 FY2027 is −$0.13/share (inputs quoted above). Staleness does not rescue the name; the TTM base confirms the FY base and shows the gap narrowing (TTM −$75,147,000 vs FY2026 −$107,539,000) but not closing. No `--ttm` pin was used because the pin would be negative and the F branch keys on the normalized base regardless.
- **DILUTION** (share count growing 3.7%/yr — engine share CAGR 3.69%): real and structural, and it is the SBC. Diluted shares rose from 514,279,230 (FY2023) to 573,483,155 (FY2026), with the current-YTD TTM count at 589,069,554 and no buyback offset in the filed history. Already deducted via the −3.69pp share-count adjustment in the growth blend; the deeper point is that the dilution and the negative OE are the same fact — $330,625,000 of TTM SBC paid in shares.
- **BASIS_BREAK_SUSPECT** (a >60% revenue jump/drop in the last 5 years): investigated — the jump sits in the earliest filed years (revenue $249,905,000 in FY2021 → $428,345,000 in FY2022), when this was a newly-public hypergrowth company scaling off a small base, not a divestiture, big M&A, or restatement; no basis break appears in the recent history the base is built from, and growth since has decelerated in an orderly way (3-yr CAGR 35.25%, latest YoY +29.57%, Q2 FY2027 +30%). The 5-yr CAGR (45.28%) is flattered by that early base and was not used to justify any tier — the F verdict does not depend on any CAGR.
- **NI_OCF_DIVERGENCE** (net income vs OCF differ by >40% in 2024, 2025, 2026): explained by the SBC mechanics, not a hidden one-off. Net income is stated after the non-cash SBC charge; OCF adds it back, so OCF sits far above net income mechanically (FY2026: net income −$9,117,000 vs OCF $236,210,000, with SBC of $314,983,000 between them). The conservative OE deducts SBC in full from OCF, so it lands below both figures — the divergence does not contaminate the base; it IS the base story. The one genuine one-off found sits just after the FY window: the $30.3M Motive arbitration gain recognized in Q1 FY2027 net income (noted above).

## My thoughts / overlay
- Quality vs. score: this is a genuinely strong growth franchise (moat 6, +30% growth at $2.1B ARR, 77% gross margins, large-customer cohort compounding fastest) and it still screens F, because the sweep's standing rule — SBC is always a real cost — is exactly the rule Samsara fails. That is the screen working as designed: on a pre-SBC free-cash-flow basis the company looks merely expensive; on an owner's-earnings basis it has not yet earned anything for shareholders after paying its people in stock.
- The trajectory is improving, honestly: TTM OE (−$75,147,000) is less negative than FY2026 (−$107,539,000) and far less than the FY2024/FY2025 conservative figures in the filed history (−$259,850,000 / −$166,388,000), because OCF is scaling faster than SBC in dollars recently. If that crossover completes, a future re-run gets a real DCF. But a Tier today must be earned on filed numbers, and there is no defensible alternative base — median, latest FY, TTM, and maintenance are all negative, so the method range is F on every basis, with no tier_override.
- Risks beyond SBC: freight/industrial cyclicality in the customer base, Motive litigation/appeal overhang around the arbitration award, hardware supply and OEM-embedded telematics, and a valuation ($23.2B) that already capitalizes the SBC normalization bull case.

## Final verdict
- **Final tier: F** (tier_by_numbers F; no override — there is no positive normalized owner's earnings to underwrite any hurdle)
- Confidence: **Medium** (high that current OE is negative on every filing basis; the F says nothing about whether the improving OCF-vs-SBC trajectory eventually flips it — that is the live question for a future re-run)
- One-liner: Strong connected-operations platform, moat 6/10, revenue +30% at $2.125B ARR — but SBC ($330.6M TTM) exceeds TTM operating cash flow ($288.4M), so owner's earnings are negative on every basis (median −$0.30/sh, TTM −$0.13/sh) and it cannot clear 15% at $40.50; Tier F until SBC normalizes.
