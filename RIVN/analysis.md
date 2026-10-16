# RIVN — Rivian Automotive, Inc.
v5 run, 2026-10-15. In scope (market cap $15.442B at $13.02, nasdaq_quote_api — under the $40B cutoff).

All figures below are copied from dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed. Research figures are attributed to the cited search results.

## What it is
US electric-vehicle maker: premium R1T pickup / R1S SUV, commercial delivery vans (anchor customer Amazon), and the midsize R2 SUV, which began external deliveries in June 2026. Plus software and services, dominated by the Volkswagen joint venture (RV Tech) licensing Rivian's electrical architecture and software. Research (Q2 2026): revenue $1.658B, +27% YoY; consolidated gross profit $179M (automotive still a gross loss, software/services the profit); net loss $837M; production 12,613, deliveries 12,194; 2026 guidance raised to 65,000–70,000 deliveries, adjusted EBITDA −$2.00B to −$1.80B, capex $1.70–$1.80B. Q3 2026 deliveries were reported at 19,248, +45.8% YoY, with the 65,000–70,000 guide maintained. Liquidity at Q2 end was reported as $5.310B in cash, cash equivalents and short-term investments, $7.163B pro forma including a July follow-on equity offering and ABL capacity.

## Owner's earnings
**FY2025 (10-K via EDGAR):** revenue $5,387,000,000 (latest YoY +8.39%); operating cash flow −$779,000,000; capex $1,710,000,000; SBC $741,000,000 (always a real cost in this sweep).
- **Conservative owner's earnings FY2025: −$3,230,000,000 = −$2.72/share** (base_oe_total_latest_fy and base_oe_latest_per_share, dcf_numbers.json).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): −$1,928,000,000 — also deeply negative; the two definitions agree on the sign.
- **Normalized base used (engine default): median of last 3 FY OE/share = −$3.50/share** (−$3.5035). OE positive in 0 of the last 5 fiscal years — every filed year is negative, and the latest year is not an exception.
- Net debt $861,000,000 (dcf_numbers.json); cash $3,579,000,000 and long-term debt $4,440,000,000 at FY2025 end per financials_history.csv. The balance sheet is not yet the binding constraint — reported liquidity is multi-billion — but it is funded by partners and shareholders, not by the business: operating cash flow itself is negative, before capex and SBC.
- The blocker is structural, not one leg: OCF was −$779,000,000 in FY2025 and capex ($1,710,000,000) is real plant spending for the R2/Georgia ramp, not discretionary. Even zeroing SBC would not make conservative OE positive on the FY2025 figures as filed.

**TTM check via ttm.py (filing-direct, through Q2 2026 — quoted inputs):**
- OCF: FY −$779,000,000 − prior YTD −$124,000,000 + current YTD −$1,190,000,000 = **TTM −$1,845,000,000**
- Capex: FY $1,710,000,000 − prior YTD $800,000,000 + current YTD $734,000,000 = **TTM $1,644,000,000**
- SBC: FY $741,000,000 − prior YTD $377,000,000 + current YTD $433,000,000 = **TTM $797,000,000**
- Shares (current-YTD weighted diluted): **1,287,000,000**
- **TTM OE total −$4,286,000,000 → TTM OE/share −$3.33** (−$3.3302)

The TTM base was NOT pinned via `--ttm`: it is negative, like the median, the latest FY, and the maintenance version. Every defensible base is negative, so no scenario DCF is supportable — the engine's F branch fired. TTM OCF deteriorated versus FY2025 on the R2 ramp / inventory build reported in Q2 2026, so staleness does not hide an inflection to positive OE.

## MOAT: 4/10 — weak
Justification: real brand and technology differentiation — a loyal premium adventure brand, vertically integrated software/electrical architecture that Volkswagen paid billions to access through the JV, and an Amazon commercial-van anchor — but no durable cost advantage, no network effect, low consumer switching costs, and no proven pricing power or returns on capital: the company has never produced positive owner's earnings at any scale so far, and third-party assessors (Morningstar, per research) assign it no moat. Scale is the core gap — guided 65,000–70,000 deliveries in 2026 against incumbent automakers and Tesla at millions of units.
- FOR: software / electrical architecture validated externally — Volkswagen JV (RV Tech) is a major, high-margin software-and-services revenue source and a strategic capital partner
- FOR: premium adventure brand with demonstrated demand — R2 launch demand, a reported record 57,000 demo drives in Q2 2026, deliveries growing into a shrinking US EV market
- FOR: Amazon commercial-van anchor relationship and Uber robotaxi commitment diversify revenue beyond premium consumer SUVs
- FOR: direct sales/service model and vertical integration give control of the customer experience and the vehicle data/autonomy stack
- AGAINST: no scale or cost advantage vs Tesla and legacy OEMs — automotive gross profit was still negative in Q2 2026 even as software/services carried consolidated gross profit
- AGAINST: customer/partner concentration — research reports the VW JV at roughly 60% of software and services revenue, and Amazon is the dominant commercial-van customer
- AGAINST: capital intensity with no self-funding — negative OCF, ~$1.7B/yr capex, a Georgia plant to build, and repeated equity issuance; US EV demand fell after the $7,500 federal credit expired in September 2025, and price competition is intense
- AGAINST: no proven pricing power into profitability — losses persist at every volume printed so far; brand preference in premium EVs has proven fickle across the industry
- A moat of 4 gives CAP = 7.2 years — moot for the valuation here, since there is no positive OE base to fade.

## DCF — v5 final run (2026-10-15)
Final engine pass: `--moat 4 --probs 0.10 0.25 0.30 0.25 0.10` (default probabilities; offsets/multipliers never reached, because the F branch fires first). Engine output: tier_by_numbers **F**, implied IRR null, weighted IV null. The five scenario slots carry the default likelihoods for the record, each with its story — no IVs or IRRs exist, by design:

| Scenario | Prob | Growth start | OE mult | Story | IV@15% | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | n/a — no OE base | n/a | US EV demand keeps shrinking post-credit, R2 ramp disappoints, VW/Amazon concentration bites; burn forces heavily dilutive raises and OE stays negative | n/a (OE < 0) | n/a |
| Bear | 25% | n/a | n/a | R2 scales but automotive gross margin stays near zero; software/JV revenue cannot cover plant capex + SBC; first positive OE is late-decade and small vs a $15.4B cap | n/a (OE < 0) | n/a |
| Base | 30% | n/a | n/a | Deliveries grow toward several hundred thousand over years, R2 reaches positive gross margin, OCF turns positive — but years too late, and after more dilution, to support $13.02 on an OE DCF run today | n/a (OE < 0) | n/a |
| Bull | 25% | n/a | n/a | R2 becomes a volume hit, JV licensing expands to other OEMs, autonomy/Uber robotaxi revenue materializes; strongly positive OE eventually — value sits beyond the OE screen's base window | n/a (OE < 0) | n/a |
| Super bull | 10% | n/a | n/a | Rivian becomes the software-defined-vehicle platform for the Western industry plus a top-3 US EV maker — a narrative/forward-multiple story, not an owner's-earnings story today | n/a (OE < 0) | n/a |

- **Probability-weighted IV@15% / weighted IRR: not computable — no positive owner's earnings in any base period.**
- Growth sanity check: the engine's blended growth (48.10%) and the 5-yr / 3-yr revenue CAGRs (214.59% / 48.10%) are production-ramp artifacts off a zero/near-zero pre-2022 base — latest FY revenue YoY was only +8.39%, and Q2 2026 printed +27% YoY. No scenario start was set from those CAGRs; they are simply unusable, and on a negative base they change nothing.
- **Hurdle math:** there is no price at which RIVN "clears 15%" on current owner's earnings, because the earnings themselves are negative — OCF, not just OE after capex/SBC. No margin-of-safety price can be quoted from this method. At $13.02 the market is paying for a multi-year ramp (R2 scale, JV licensing, robotaxis) that the filings do not yet convert into cash. What would change the verdict: OCF turning sustainably positive and then covering capex + SBC — the TTM OE gap (−$4,286,000,000) is the number to watch.

## FLAGS — every fragility flag resolved
- **STALE_FY** (latest FY ended 2025-12-31, 9 months ago): resolved with ttm.py — TTM OE through Q2 2026 is −$3.33/share on a TTM total of −$4,286,000,000 (inputs quoted above). Staleness does not rescue the name; the TTM base confirms the FY base and TTM OCF (−$1,845,000,000) is worse than FY2025 OCF. No `--ttm` pin was used because the pin would be negative and the F branch keys on the normalized base regardless.
- **DILUTION** (share count growing 9.1%/yr — engine share CAGR 9.11%): real and ongoing. Diluted shares in the filed history rose from 913,000,000 (FY2022) to 1,186,000,000 (FY2025), with the current-YTD TTM count at 1,287,000,000; research reports a 2026 follow-on offering of 75,000,000 shares (plus overallotment) and an Uber-linked private placement on top of SBC of $741,000,000 (FY2025) / $797,000,000 (TTM). Already deducted via the −5.00pp share-count adjustment in the growth blend; the deeper point is that a cash-burning, capital-intensive ramp is being funded substantially in stock.
- **BASIS_BREAK_SUSPECT** (a >60% revenue jump/drop in the last 5 years): investigated — the jumps are the start of production, not a divestiture, big M&A, or restatement: revenue was $0 in FY2019–FY2020, $55,000,000 in FY2021, then $1,658,000,000 in FY2022 as R1 deliveries began. That is why the 5-yr CAGR (214.59%) is meaningless. Recent history is on one consistent basis and decelerating in an orderly way (FY2025 YoY +8.39%); the F verdict does not depend on any CAGR.
- **NI_OCF_DIVERGENCE** (net income vs OCF differ by >40% in 2024, 2025): explained by non-cash charges, not a hidden one-off. Net income is stated after D&A and SBC; OCF adds them back (FY2025: net income −$3,646,000,000 vs OCF −$779,000,000, with D&A $784,000,000 and SBC $741,000,000 in the filed history, plus working-capital movement — the maintenance OE's ΔNWC leg was −$1,718,000,000 in FY2025). The conservative OE deducts capex and SBC in full from OCF, so it lands below both figures — the divergence does not contaminate the base; both series are deeply negative on any reading.

## My thoughts / overlay
- Quality vs. score: the operating story is genuinely improving at the gross line (first full year of consolidated gross profit in FY2025 per research, Q2 2026 gross profit $179M, record Q3 deliveries) and it still screens F, because the sweep values owner's earnings and Rivian's are negative at every level — revenue, gross profit, OCF, and OE. That is the screen working as designed for a pre-profitability, capital-intensive manufacturer.
- The method range is F on every basis — median (−$3.50/sh), latest FY (−$2.72/sh), TTM (−$3.33/sh), and maintenance OE (−$1,928,000,000 total) are all negative, so there is no defensible alternative base and no tier_override.
- The bull case is not imaginary — R2 broadening the market, VW JV licensing, the Uber robotaxi commitment, and multi-billion reported liquidity — but it is a scale-and-multiple case that must survive several more years of burn and dilution (including the Georgia plant) before it becomes an owner's-earnings case. Partner concentration (VW for software revenue, Amazon for vans) and a post-tax-credit US EV downturn are the standing external risks.

## Final verdict
- **Final tier: F** (tier_by_numbers F; no override — there is no positive normalized owner's earnings to underwrite any hurdle)
- Confidence: **Medium** (high that current OE is negative on every filing basis; the F says nothing about whether the R2/JV ramp eventually flips OCF and OE positive — that is the live question for a future re-run)
- One-liner: Weak-moat EV maker, moat 4/10, R2 ramp and VW software JV are real — but owner's earnings are negative in all 5 filed years (median −$3.50/sh, TTM −$3.33/sh) with operating cash flow itself negative, so it cannot clear 15% at $13.02; Tier F until OCF turns positive enough to cover capex + SBC.
