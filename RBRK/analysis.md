# RBRK — Rubrik, Inc.
v5 run, 2026-10-15. In scope (market cap $22,377,705,200 at $113.90, nasdaq_quote_api — under the $40B cutoff).

All figures below are copied from dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed.

## What it is
Data security and cyber-resilience platform (Rubrik Security Cloud): backup and recovery, threat analytics, and identity recovery for on-premises, cloud, and SaaS data, sold mainly as subscriptions through channel partners to mid-sized and large organizations. A second suite for governing AI agents launched in early 2026 is an option, not the current earnings driver. Research (Q2 FY2027 results, quarter ended 2026-07-31, via search): revenue $427.3M, +38% YoY; subscription ARR $1.66B, +33% YoY; 3,084 customers with at least $100,000 in subscription ARR, +23% YoY; full-year FY2027 revenue guidance raised to $1.685B–$1.693B. The growth is real — the problem in this screen is below the revenue line, in stock-based compensation.

## Owner's earnings
**FY2026 (10-K via EDGAR, fiscal year ended 2026-01-31):** revenue $1,316,191,000; operating cash flow $282,908,000; capex $29,631,000; SBC $329,374,000 (always a real cost in this sweep).
- **Conservative owner's earnings FY2026: −$76,097,000 = −$0.387/share** (latest FY OE/share, dcf_numbers.json).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): −$929,519,000 — also negative, and far more so; the two definitions agree on the sign.
- **Normalized base (engine): median of last 3 FY OE/share = −$0.387/share.** OE positive in 0 of the last 4 fiscal years in the filed history.
- History (financials_history.csv): FY2023 OE −$12,684,000; FY2024 OE −$22,566,000; FY2025 OE −$882,570,000; FY2026 OE −$76,097,000. The FY2025 collapse is the IPO SBC spike resolved under NI_OCF_DIVERGENCE below — SBC was $913,913,000 that year, against $5,715,000 in FY2024 and $6,954,000 in FY2023.
- Equity is negative on the filed history (−$519,562,000 at FY2026) — an accumulated-deficit balance sheet from years of GAAP losses. The engine's net_debt_latest is null, so no net-debt ratio is quoted; balance-sheet leverage is not the verdict driver here, the SBC line is.

**TTM check via ttm.py (filing-direct, through Q2 FY2027 — quoted inputs):**
- OCF: FY $282,908,000 − prior YTD $104,379,000 + current YTD $158,535,000 = **TTM $337,064,000**
- Capex: FY $29,631,000 − prior YTD $6,348,000 + current YTD $9,876,000 = **TTM $33,159,000**
- SBC: FY $329,374,000 − prior YTD $161,997,000 + current YTD $174,386,000 = **TTM $341,763,000**
- Shares (current-YTD weighted diluted): **204,903,000**
- **TTM OE total −$37,858,000 → TTM OE/share −$0.185**

The TTM base was pinned via `--ttm` in the final run (base_source: ttm_json) and it is still negative — like the median, the latest FY, and the maintenance version. Every defensible base is negative, so no scenario DCF is supportable and the engine's F branch fired. The one-line story: TTM SBC ($341,763,000) exceeds the entire TTM operating cash flow ($337,064,000) before capex is even deducted. The trajectory is improving — TTM OE/share −$0.185 vs FY2026 −$0.387 — because OCF is growing faster than the SBC run-rate, but it has not crossed zero in any filing.

## MOAT: 6/10 — moderate
Justification: A Gartner Leaders-box data-protection platform with a security-forward differentiation (immutable recovery, threat analytics, identity recovery) and subscription retention above 120% in company reporting — real lock-in once an enterprise's backup, recovery workflow, and protected data sit on the platform. It is not a 7–8: Veeam, Cohesity (now combined with Veritas), Commvault, and Dell contest the same renewals from the same Leaders box, cloud-native entrants attack from the cloud-first side, and there is no network effect — each deployment stands alone.
- FOR: Leader position in backup and data protection with security-led differentiation — ransomware recovery, threat analytics, and identity recovery, not commodity backup
- FOR: Subscription model with expansion inside the base — subscription ARR $1.66B (+33% YoY in Q2 FY2027), customers at $100,000+ ARR +23% YoY, net retention above 120% in company reporting
- FOR: Switching costs once recovery workflows, retention policies, and protected estates are built on the platform; backup is mission-critical and rarely ripped out casually
- FOR: High gross-margin, asset-light model (capex $29,631,000 in FY2026 against revenue $1,316,191,000) with expansion paths into identity security and AI-agent governance
- AGAINST: Crowded Leaders box — Veeam, Cohesity/Veritas, Commvault, and Dell all compete for the same enterprise renewals; no clear scale or network-effect gap
- AGAINST: Cloud-native and hyperscaler-native protection tools attack the fastest-growing estates from below
- AGAINST: Go-to-market runs through channel partners — distribution is partly rented, and partner concentration is a recurring risk disclosure for this name
- AGAINST: No proven pricing power through a full cycle as a public company (IPO in 2024) and no GAAP profitability yet to evidence it
- A moat of 6 gives CAP = 9.8 years — moot for the valuation here, since there is no positive OE base to fade.

## DCF — v5 final run (2026-10-15)
Final engine pass: `--moat 6 --probs 0.10,0.25,0.30,0.25,0.10 --ttm` (default probabilities, offsets, and multipliers; they are never reached, because the F branch fires first). Engine output: tier_by_numbers **F**, implied IRR null, weighted IV null. The five scenario slots carry the default likelihoods for the record, each with its story — no IVs or IRRs exist, by design:

| Scenario | Prob | Growth start | OE mult | Story | IV@15% | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | n/a — no OE base | n/a | SBC run-rate holds near TTM levels, ARR growth decelerates toward the low-20s, Veeam/Cohesity take renewals; OE stays negative for years | n/a (OE < 0) | n/a |
| Bear | 25% | n/a | n/a | Revenue keeps growing but SBC grinds down slowly; first positive OE is late and small against a $22.4B market cap | n/a (OE < 0) | n/a |
| Base | 30% | n/a | n/a | Current trajectory continues — OCF compounding at recent rates outgrows a roughly flat SBC dollar line and OE crosses zero — but too late and too small to support $113.90 on an OE DCF run today | n/a (OE < 0) | n/a |
| Bull | 25% | n/a | n/a | ARR holds 30%+ growth, identity/AI-agent lines attach, SBC falls fast as a share of revenue; solidly positive OE within ~2 years — value sits beyond the OE screen's base window | n/a (OE < 0) | n/a |
| Super bull | 10% | n/a | n/a | Rubrik becomes the default cyber-resilience layer for the AI era with peer-level SBC discipline — a narrative/forward-earnings valuation story, not an owner's-earnings story today | n/a (OE < 0) | n/a |

- **Probability-weighted IV@15% / weighted IRR: not computable — no positive owner's earnings in any base period.**
- Sanity check on growth (standing rule): the revenue prints are strong and verified — latest FY revenue YoY +48.46% and revenue CAGR 29.94% (dcf_numbers.json), Q2 FY2027 revenue +38% YoY and subscription ARR +33% YoY (search, above), with FY2027 guidance raised. No scenario-start issue arises: growth is not the failure point, and no growth rate applied to a negative base produces a DCF. The failure is the SBC line between OCF and the owner.
- **Hurdle math:** there is no price at which RBRK "clears 15%" on current owner's earnings, because the earnings themselves are negative after SBC, and therefore no margin-of-safety price can be quoted from this method. At $113.90 the market is paying today for an SBC normalization and an OE crossover that the filings do not yet show.

## FLAGS — every fragility flag resolved
- **STALE_FY** (latest FY ended 2026-01-31, 8 months ago): resolved with ttm.py — TTM OE through Q2 FY2027 (ended 2026-07-31) is −$0.185/share, with the full inputs quoted above. Staleness does not rescue the name; the TTM base confirms the FY base, in a less negative form. The final run used the `--ttm` pin.
- **DILUTION** (share count growing 48.8%/yr): the headline rate is an IPO artifact, not a steady-state print — and it still matters. Diluted shares were 60,628,000 in FY2024, then 154,294,000 in FY2025 and 196,468,000 in FY2026, with 204,903,000 on the current-YTD TTM basis (financials_history.csv / ttm.py). The step-up is the April 2024 IPO: preferred conversion and the vesting/expense recognition of pre-IPO equity awards, followed by ongoing SBC issuance with no buyback offset in the filed history. The engine already deducts the trend via the −5pp share-count adjustment in the growth blend; the deeper point is that SBC is the dilution — TTM SBC of $341,763,000 is paid in shares.
- **NI_OCF_DIVERGENCE** (2024, 2025, 2026): explained by the SBC mechanics and the IPO spike, not by a hidden one-off gain. Net income is stated after the non-cash SBC charge; OCF adds that charge back. FY2025 is the extreme case: net income −$1,154,820,000 vs OCF +$48,228,000, with SBC of $913,913,000 — earnings coverage of the FY2025 results attributed the widened loss primarily to IPO-related stock compensation. FY2026 shows the normalized version of the same gap: net income −$348,828,000 vs OCF +$282,908,000, with SBC of $329,374,000. The pre-IPO years are the mirror image: SBC of only $6,954,000 (FY2023) and $5,715,000 (FY2024) flattered those years' OE, and OE was still negative in both. The OCF-based conservative OE deducts SBC in full in every year, so the divergence does not contaminate the base — it is the base story.

## My thoughts / overlay
- Quality vs. score: this is a genuinely strong growth franchise (revenue +48.46% in FY2026, subscription ARR +33% in the latest quarter, guidance raised) that still screens F, because the sweep's standing rule — SBC is always a real cost — is exactly the rule Rubrik fails today. On a pre-SBC free-cash-flow basis the company is cash-generative (FY2026 FCF $253,277,000 in the filed history); after paying its people in stock, owners are still underwater on every basis the engine can compute (median, latest FY, TTM, maintenance).
- Unlike a distant crossover, this F is closing: OE/share improved from the FY2025 IPO-spike year to −$0.387 in FY2026 to −$0.185 TTM, driven by OCF growth, not by SBC cuts — TTM SBC ($341,763,000) is actually above the FY2026 figure ($329,374,000). The crossover case therefore rests entirely on OCF continuing to compound faster than a flat-to-rising SBC line. That is plausible at current growth rates; it is a forecast, not a filing.
- Method range: there is none to hide behind — every defensible conservative base is negative, so no alternative tier is supportable today. What would change the verdict: two consecutive filings showing TTM conservative OE above zero, with the diluted share count flattening — at that point RBRK gets a real five-scenario DCF, and at $113.90 it would still need sustained high growth to clear 15%.

## Final verdict
- **Final tier: F** (tier_by_numbers F; no override — there is no positive normalized owner's earnings to underwrite any hurdle)
- Confidence: **Medium** (high that current OE is negative on every filing basis; the F says nothing about whether the OCF trajectory flips OE positive within a year or two — that is the live question for a future re-run)
- One-liner: Strong cyber-resilience franchise, moat 6/10, ARR +33% — but TTM SBC ($341.8M) exceeds all of its TTM operating cash flow ($337.1M), so owner's earnings are negative on every basis (TTM −$0.18/share) and it cannot clear the 15% hurdle at any price at $113.90; Tier F until SBC discipline shows up in a filing.
