# AXON — Axon Enterprise, Inc.
v5 run, 2026-10-14 (supersedes the v4 analysis of 2026-10-13; the v4 pass's SBC-cause finding is carried forward under Owner's earnings). In scope (market cap $34.431B at $418.00, nasdaq_quote_api — under the $40B cutoff).

All figures below are copied from dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed.

## What it is
Public-safety technology platform: TASER conducted-energy weapons, body-worn and in-car cameras, and the Axon Cloud / Evidence.com software ecosystem that stores and manages digital evidence, sold mostly as bundled hardware-plus-subscription contracts to law-enforcement agencies. Newer lines (Platform Solutions, the Dedrone counter-drone business, AI Era products) are scaling fast. Research (Q2 2026 shareholder letter coverage): Q2 2026 revenue $904M, +35% YoY — the 10th consecutive quarter above 30% growth; annual recurring revenue ~$1.6B, +39%, with net revenue retention of 126%; future contracted bookings $15.1B, +41%; FY2026 revenue growth guidance raised to 32–34%.

## Owner's earnings
**FY2025 (10-K via EDGAR):** revenue $2,779,536,000 (+33.47% YoY); operating cash flow $211,339,000; capex $136,258,000; SBC $634,231,000 (always a real cost in this sweep).
- **Conservative owner's earnings FY2025: −$559,150,000 = −$6.79/share** (latest FY OE/share, dcf_numbers.json).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): −$152,603,000 — also negative; the two definitions agree on the sign.
- **Normalized base used (engine default): median of last 3 FY OE/share = −$0.68/share.** OE positive in only 1 of the last 5 fiscal years.
- Net debt (latest, dcf_numbers.json): $609,575,000. Post-period event: in September 2026 Axon announced a $1B 0% convertible senior note offering due 2031 with capped calls — more potential dilution layered on the SBC dilution below.
- The SBC step-up is identified, not mysterious: SBC ran $131,358,000 (FY2023) → $382,604,000 (FY2024) → $634,231,000 (FY2025) in the filed history, and the prior v4 pass's 10-K review attributed the step-up to the 2024 eXponential Stock Plan plus the 2024 CEO Performance Award vesting in tranches. It recurs in guidance: FY2026 SBC is guided at $590–620M (per Q2 2026 reporting), i.e. the new level is the run-rate, not a one-off.

**TTM check via ttm.py (filing-direct, through Q2 2026 — quoted inputs):**
- OCF: FY $211,339,000 − prior YTD −$65,910,000 + current YTD −$11,440,000 = **TTM $265,809,000**
- Capex: FY $136,258,000 − prior YTD $47,815,000 + current YTD $44,174,000 = **TTM $132,617,000**
- SBC: FY $634,231,000 − prior YTD $279,483,000 + current YTD $278,697,000 = **TTM $633,445,000**
- Shares (current-YTD weighted diluted): **82,518,000**
- **TTM OE total −$500,253,000 → TTM OE/share −$6.06**

The TTM base was NOT pinned via `--ttm`: it is negative, like the median, the latest FY, and the maintenance version. Every defensible base is negative, so no scenario DCF is supportable — the engine's F branch fired. The story is one line long: Axon's SBC ($634,231,000 in FY2025, $633,445,000 TTM) exceeds its entire operating cash flow after capex. Even as revenue grows ~33%/yr, SBC is guided roughly flat in dollars, which is the only path by which OE eventually turns positive.

## MOAT: 8/10 — strong
Justification: Axon owns the default public-safety ecosystem — TASER plus body cameras plus Evidence.com — with high switching costs once an agency's evidence workflow, training, and procurement are built around it; ARR +39% at 126% net revenue retention and $15.1B of future contracted bookings are the measurable signature of that lock-in. It is not a 9–10: the customer is the public sector, contracts go through budget cycles and competitive bidding, and Motorola Solutions contests the same agencies.
- FOR: dominant TASER + body-camera installed base bundled with Evidence.com cloud — an integrated ecosystem, not point products
- FOR: high switching costs — evidence storage, chain-of-custody workflow, officer training, and multi-year bundled contracts
- FOR: recurring-revenue engine compounding — ARR ~$1.6B (+39%), net revenue retention 126%, future contracted bookings $15.1B (+41%)
- FOR: brand and trust position in law enforcement; proven ability to expand wallet share per agency (cameras → software → drones/AI)
- AGAINST: public-sector customers — budget cycles, political scrutiny, and open competitive bidding cap pricing power
- AGAINST: Motorola Solutions and others contest the same agencies; no consumer-style network effect
- AGAINST: growth increasingly carried by newer lines (Dedrone, Platform Solutions, AI) whose moats are thinner and unproven through a cycle
- A moat of 8 gives CAP = 12.4 years — moot for the valuation here, since there is no positive OE base to fade.

## DCF — v5 final run (2026-10-14)
Final engine pass: `--moat 8 --probs 0.10 0.25 0.30 0.25 0.10` (default probabilities; offsets/multipliers never reached, because the F branch fires first). Engine output: tier_by_numbers **F**, implied IRR null, weighted IV null. The five scenario slots carry the default likelihoods for the record, each with its story — no IVs or IRRs exist, by design:

| Scenario | Prob | Growth start | OE mult | Story | IV@15% | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | n/a — no OE base | n/a | SBC stays at guided levels indefinitely, municipal budgets tighten, Motorola takes renewals; OE never turns positive | n/a (OE < 0) | n/a |
| Bear | 25% | n/a | n/a | Revenue grows ~25–30% but the award tranches keep SBC near guidance for years; first positive OE is late-decade and small vs a $34.4B cap | n/a (OE < 0) | n/a |
| Base | 30% | n/a | n/a | Growth decelerates gracefully toward the ~$6B 2028 target zone and SBC grinds down toward the <2.5%/yr dilution target — OE turns positive, but years too late to support $418 on an OE DCF run today | n/a (OE < 0) | n/a |
| Bull | 25% | n/a | n/a | 30%+ growth persists, SBC normalizes fast post-tranche, software mix lifts OCF margins; positive, fast-growing OE by 2028–29 — value sits beyond the OE screen's base window | n/a (OE < 0) | n/a |
| Super bull | 10% | n/a | n/a | Axon becomes the unchallenged public-safety OS globally and SBC discipline arrives early — a narrative/consensus-EPS valuation story, not an owner's-earnings story today | n/a (OE < 0) | n/a |

- **Probability-weighted IV@15% / weighted IRR: not computable — no positive owner's earnings in any base period.**
- Revenue growth is real and verified against prints (5-yr CAGR 32.49%, 3-yr CAGR 32.78%, latest FY +33.47%, Q2 2026 +35%, FY26 guided 32–34%) — growth is not the problem and no scenario-start sanity issue arises. The failure is below the revenue line.
- **Hurdle math:** there is no price at which AXON "clears 15%" on current owner's earnings, because the earnings themselves are negative after SBC, and therefore no margin-of-safety price can be quoted from this method. At $418.00 the market is paying today for an SBC normalization that the filings do not yet show. What would change the verdict: SBC falling as a share of revenue fast enough that OCF − capex − SBC turns sustainably positive (the 2028 framework — ~$6B revenue target, dilution targeted below 2.5%/yr — points that way, but it is a target, not a print).

## FLAGS — every fragility flag resolved
- **STALE_FY** (latest FY ended 2025-12-31, ~9 months ago): resolved with ttm.py — TTM OE through Q2 2026 is −$6.06/share (inputs quoted above). Staleness does not rescue the name; the TTM base confirms the FY base. No `--ttm` pin was used because the pin would be negative and the F branch keys on the normalized base regardless.
- **DILUTION** (share count +4.33%/yr): real and structural. Diluted shares rose from 75,456,000 (FY2023) to 82,370,000 (FY2025); there is no buyback offsetting SBC issuance, and the September 2026 $1B convertible adds a further potential layer. Already deducted via the −4.33pp share-count adjustment in the growth blend; the deeper point is that SBC is the dilution — FY2025 SBC of $634,231,000 against OCF of $211,339,000.
- **NI_OCF_DIVERGENCE** (2025: net income $124,656,000 vs OCF $211,339,000): explained by the SBC mechanics, not a hidden one-off gain. Net income is stated after the $634,231,000 non-cash SBC charge; OCF adds that charge back, so OCF sits above net income mechanically. FY2025 also carried a $105,682,000 income-tax benefit (tax line in financials_history.csv) supporting net income, and a $277,259,000 working-capital drag on OCF. The OCF-based conservative OE deducts SBC in full, so it lands below both figures — the divergence does not contaminate the base; it IS the base story.

## My thoughts / overlay
- Quality vs. score: this is one of the strongest franchises in the sweep universe (moat 8, ~33% growth held for ten straight quarters, 126% NRR) and it still screens F, because the sweep's standing rule — SBC is always a real cost — is exactly the rule Axon fails. That is the screen working as designed, not a data error: on a pre-SBC free-cash-flow basis the company looks merely expensive; on an owner's-earnings basis it has not yet earned anything for shareholders after paying its people.
- The bull case is a trajectory argument (revenue compounding ~33% against guided-flat SBC dollars eventually flips OE positive), and it may well be right — but it is a forecast about compensation discipline, not a reading of current filings. The method range here is unusually honest: every basis the engine can compute (median, latest FY, TTM, maintenance) is negative, so there is no defensible alternative tier today.
- Balance sheet is not the risk: net debt $609,575,000 is modest against the revenue base; the risks are valuation (the price embeds the SBC normalization in advance), dilution compounding at +4.33%/yr until the promised <2.5%/yr discipline shows up in prints, and public-sector budget/political exposure.

## Final verdict
- **Final tier: F** (tier_by_numbers F; no override — there is no positive normalized owner's earnings to underwrite any hurdle)
- Confidence: **Medium** (high that current OE is negative on every filing basis; the F says nothing about whether the guided SBC path eventually flips it — that is the live question for a future re-run)
- One-liner: Elite public-safety franchise, moat 8/10, growing ~33%/yr — but SBC ($634M in FY2025) exceeds OCF after capex, so conservative owner's earnings are negative on every basis and it cannot clear 15% at $418; Tier F until SBC normalizes.
