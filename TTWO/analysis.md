# TTWO — Take-Two Interactive Software, Inc.
v5 re-run, 2026-10-13 (supersedes the v4 analysis of 2026-10-12; verdict unchanged). In scope: market cap $36.839B < $40B (key_numbers.md), watchlist name.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, financials_history.csv, or the sensitivity engine run recorded in this file — none are recomputed.

## What it is
A hit-driven game publisher built from three labels: Rockstar Games (Grand Theft Auto, Red Dead Redemption — owned IP, very long cycles), 2K (NBA 2K annual sports franchise, licensed league IP, heavy recurrent spending), and Zynga (mobile, acquired May 2022 — Toon Blast, Match Factory, Empires & Puzzles, Words With Friends, Zynga Poker; mobile was 53% of Q1 FY2027 net bookings per company reporting). FY2026 (ended Mar 31, 2026): revenue $6,656.4M (+18.16% YoY, latest rev YoY in key_numbers.md), Net Bookings $6.72B. The near-term story is one date: Grand Theft Auto VI launches November 19, 2026 (twice delayed), at a $79.99 price point, pre-orders open since June 25, 2026, which management calls unprecedented. FY2027 guidance (reiterated at Q1): Net Bookings $8.0–8.2B, GAAP revenue $7.9–8.1B, GAAP net income only $104–143M, operating cash flow above $1B — i.e., even the GTA VI year is guided to barely a 1–2% net margin.

Latest quarter (Q1 FY2027, ended Jun 30, 2026, company reporting via search): GAAP revenue $1.53B (+2.0% YoY), Net Bookings $1.39B (−3%), net loss −$34.1M including a $43.4M impairment on a cancelled unannounced title, adjusted EBITDA $167M (−26% YoY), mobile bookings $739.5M (−7%), console bookings +11%, recurrent consumer spending 84% of net bookings.

## Owner's earnings (SEC EDGAR, filing-direct)
Conservative OE = OCF − capex − SBC (financials_history.csv totals):

| Fiscal year | Revenue | OCF | Capex | SBC | Conservative OE |
|---|---|---|---|---|---|
| FY2022 | $3,504.8M | $258.0M | $158.6M | $183.0M | −$83.6M |
| FY2023 | $5,349.9M | $1.1M | $204.2M | $317.8M | −$520.9M |
| FY2024 | $5,349.6M | −$16.1M | $141.7M | $335.6M | −$493.4M |
| FY2025 | $5,633.6M | −$45.2M | $169.4M | $324.0M | −$538.6M |
| FY2026 | $6,656.4M | $624.3M | $162.8M | $305.3M | **+$156.2M** |

- OE positive in **1 of the last 5 fiscal years** (key_numbers.md: 1/5). Latest FY OE/share **+$0.85** against a $200.32 price — a 0.4% yield on the sensitivity run's diagnostics.
- **Normalized base (3-yr median OE/share) = −$2.90/share** (key_numbers.md) → Tier F by numbers. The FY2023–25 collapse is post-Zynga: revenue stepped up on consolidation but operating cash flow ran at ~zero for three years while SBC ran $317.8–335.6M/yr.
- Maintenance version FY2026 (financials_history.csv): **−$1,583.7M** — far worse than the conservative figure and not credible as a base: it is dragged by the engine's ΔNWC swing ($1,321.2M in the CSV) and by net income carrying acquired-intangible amortization and impairment residue. The OCF-based conservative figure is the clean one here.
- **Base used = TTM owner's earnings through Q1 FY2027, from ttm.py (filing-direct, no hand math) — final engine pass used `--base-oe-ps -0.07035445757250268`:**
  - OCF: FY (2025-04-01→2026-03-31) $624,300,000 − prior YTD (2025-04-01→2025-06-30) −$44,700,000 + current YTD (2026-04-01→2026-06-30) −$168,800,000 = **TTM $500,200,000**
  - Capex: FY $162,800,000 − prior YTD $25,100,000 + current YTD $25,000,000 = **TTM $162,700,000**
  - SBC: FY $305,300,000 − prior YTD $40,700,000 + current YTD $86,000,000 = **TTM $350,600,000**
  - Shares (current-YTD weighted): **186,200,000**
  - **TTM OE total −$13,100,000 → TTM OE/share −$0.07** (key_numbers.md base OE/share $-0.07, source: agent_supplied_ttm_override)
  - Q1 is seasonally OCF-negative, but Q1 FY2027 genuinely deteriorated vs Q1 FY2026 on the ttm.py inputs: OCF worsened (−$44.7M → −$168.8M YTD legs) and SBC more than doubled ($40.7M → $86.0M). The latest FY's return to positive OE did **not** hold on a TTM basis.
- Balance sheet (key_numbers.md / CSV): net debt $942.5M; FY2026 cash $1,545.5M vs long-term debt $2,488.0M. Leverage is modest in absolute terms — it is not the problem; the missing earnings are.
- Corroboration from the pass-2 forensic review (second_pass.md): Take-Two capitalises software development costs (balance $1,845.6M at Mar 31, 2025 → $2,169.2M at Dec 31, 2025), and capitalised development spend is **not** deducted in the engine's PP&E-only capex — so the conservative OE above is, if anything, generous. Any fuller cash-cost OE would be more negative, not less.

## Moat: 6/10 — moderate-strong at franchise level, diluted at company level
Justification: GTA is a durable owned franchise with proven pricing power ($79.99, unprecedented pre-orders) and NBA 2K is entrenched with recurrent spending at 84% of Q1 FY2027 bookings, but roughly half the company is Zynga mobile (bought traffic, low switching costs, goodwill impairments of $2,342M in FY2024 and $3,545M in FY2025), NBA 2K is licensed not owned, there is no owned platform, and one title drives the FY2027 step-up after two delays.
- FOR: GTA — durable owned franchise, the prior mainline entry has sold for 13 years, GTA Online recurrent spending, premium $79.99 pricing with pre-order demand management calls unprecedented (real pricing power on owned IP); NBA 2K — entrenched annual franchise with habitual recurrent spending, hard to displace in basketball; recurrent consumer spending at 84% of Q1 FY2027 net bookings gives a live-services base less binary than pure boxed sales; Rockstar's quality bar and development know-how are a capability moat rivals cannot simply buy.
- AGAINST: Concentration and lumpiness — one title drives the FY2027 step-up, mainline GTA gaps run over a decade, and this one has already slipped twice; Zynga mobile ~half the company — low switching costs, traffic bought through user-acquisition spend, mobile bookings −7% in Q1 FY2027, and goodwill impairments of $2,342M (FY2024) and $3,545M (FY2025) with equity falling from $9,042.5M at FY2023 to $2,137.7M at FY2025 (CSV); NBA 2K is licensed, not owned — the league takes its cut and the licence must be renewed; no owned platform — Sony/Microsoft storefront economics sit between Take-Two and its console players; AAA cost inflation raises the capital at risk per release, and capitalised development costs excluded from engine capex make OE generous, not harsh.
- CAP from moat 6: clamp(2 + 1.3×6) = **9.8 years** (recorded as cap_years 9.8 in the sensitivity run) — moot for the final DCF (no positive OE base to fade), but it records that even the fade window is carried by one franchise.

## DCF — v5 final run (2026-10-13)
Price: **$200.32** (nasdaq_quote_api, key_numbers.md); market cap $36.839B. The engine cannot project scenarios on a negative base, and forcing one would be inventing numbers — so the final run has no scenario IVs or IRRs, by design (no positive normalized OE = Tier F, flagged not forced). The five scenario slots carry the default likelihoods (10/25/30/25/10) and default offsets/mults for the record:

| Scenario | Prob | Growth start | OE mult | Story | IV@15% | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | n/a — no OE base | 0.75 | GTA VI slips again or underwhelms, mobile keeps shrinking, SBC stays ~$350M/yr; OE stays negative and the FY2027 guide collapses | n/a (OE < 0) | n/a |
| Bear | 25% | n/a | 0.90 | GTA VI launches on time but the guided incremental bookings prove to be most of the story; post-launch bookings cliff in FY2028, OE barely positive one year then fades | n/a (OE < 0) | n/a |
| Base | 30% | n/a | 1.00 | Management's own path: FY2027 bookings $8.0–8.2B and guided operating cash flow above $1B deliver the first solidly positive OE year — a forward year, not a filing-derived base today | n/a (OE < 0) | n/a |
| Bull | 25% | n/a | 1.10 | GTA VI repeats its predecessor's decade-long tail via a new online mode; OE/share compounds from the FY2027 step-up — value sits beyond the OE screen's trailing window | n/a (OE < 0) | n/a |
| Super bull | 10% | n/a | 1.25 | GTA VI becomes the largest entertainment launch ever and sustains it; Take-Two converts to a structurally cash-generative publisher — a franchise-valuation story, not a current owner's-earnings story | n/a (OE < 0) | n/a |

- **Probability-weighted IV@15% / IRR: not computable — normalized and TTM conservative OE are both negative** (score.json: iv_at_15 null, implied_irr null).
- **Tier by numbers: F.**
- Growth sanity check for the record: FY2026 revenue +18.16%, Q1 FY2027 revenue +2.0% / bookings −3%, FY2027 bookings guided $8.0–8.2B. Growth blend 14.57% (components: rev CAGR 5y 14.57%, 3y 7.55%, latest YoY 18.16%, OE/share CAGR 2y —; key_numbers.md). No growth start rescues a negative base.
- **Method range / sensitivity (documented, not the verdict):** capitalising the single positive year at face value — engine run with `--base-oe-ps 0.8493746601413812` (latest FY OE/share), moat 6, probs 10/25/30/25/10, default offsets/mults, g_base 9.80% (blend 14.57% − 4.77pp dilution adjustment), CAP 9.8 yrs — yields:

| Scenario | Prob | Growth start | OE mult | IV@15% | IRR |
|---|---|---|---|---|---|
| Super bear | 10% | −2.2% | 0.75 | $4.24 | −1.98% |
| Bear | 25% | 4.8% | 0.90 | $6.94 | 2.26% |
| Base | 30% | 9.8% | 1.00 | $9.64 | 3.17% |
| Bull | 25% | 14.8% | 1.10 | $13.23 | 3.48% |
| Super bull | 10% | 21.8% | 1.25 | $20.45 | 4.11% |

  Weighted: **IV@15% $10.40, IV@12% $14.09, IV@10% $18.25, weighted IRR 3.25% → Tier D** on that generous base. Diagnostics from that run: OE yield 0.42%, terminal value 20.78% of IV@15%, scenario spread 4.83x, net debt 6.03x normalized OE, 6.44 months since FY end. So the defensible trailing-input range is F to D, and even the most generous trailing base puts fair value at ~1/20th of the $200.32 price. The gap is the market capitalising GTA VI forward earnings that have not yet appeared in any filing.

## FLAGS — resolving every fragility flag
Final run flags (dcf_numbers.json / key_numbers.md):
- **DILUTION** — share count growing 4.8%/yr (key_numbers.md: share count CAGR 4.77%, growth adj −4.77pp, already deducted in the sensitivity run's g_base). Composition: the Zynga stock consideration (diluted shares 116.8M FY2022 → 159.9M FY2023, CSV) plus ongoing SBC — and the trend worsened in the latest quarter: SBC TTM $350.6M with the Q1 FY2027 YTD leg at $86.0M vs $40.7M a year earlier (ttm.py inputs above); diluted shares 183.9M FY2026 → 186.2M Q1 FY2027 (ttm.py). Resolved: dilution is real, ongoing, and already charged — SBC is subtracted in full in conservative OE.
- **NI_OCF_DIVERGENCE** — NI vs OCF differ by >40% in 2024, 2025, 2026. Resolved: the FY2024 gap (NI −$3,744.2M vs OCF −$16.1M, CSV) and FY2025 gap (NI −$4,478.9M vs OCF −$45.2M) are dominated by non-cash goodwill impairments of $2,342M and $3,545M respectively ($0 in FY2026). The FY2026 gap (NI −$298.2M vs OCF +$624.3M) is the reverse mix: SBC add-back ($305.3M), acquired-intangible amortization, and the absence of impairment. OE is built on OCF and subtracts SBC explicitly, so it is clean of the impairment marks — which is exactly why the OE story (OCF ~zero for three years) is a *cash* problem, not an accounting one.

Flags that fired only in the sensitivity run (on the single-positive-year base), resolved here:
- **LOW_OE_YIELD** — 0.42% on the latest-FY base; on the TTM base the yield is negative. Essentially all of the price is payment for future earnings.
- **WIDE_SCENARIO_SPREAD** — 4.83x (super-bull IV $20.45 vs super-bear $4.24). Real — outcomes genuinely hinge on one launch — and it caps confidence below high.
- **HIGH_NET_DEBT** — 6.03x normalized OE in the sensitivity diagnostics. Resolved in context: absolute net debt is $942.5M (key_numbers.md) — no solvency or refinancing concern. The ratio fires because the OE denominator is tiny/negative, which is the finding, not a leverage warning.

Checked and not firing in the final run, for the record:
- **STALE_FY** — FY2026 ended 6.44 months before this run (sensitivity diagnostics), under the 7-month threshold. The TTM base was computed anyway via ttm.py, and it is *worse* than the latest-FY base (−$0.07 vs +$0.85) — staleness is not hiding a better number.
- **BASE_DIVERGENCE** — in substance the central question: latest FY +$0.85 vs 3-yr median −$2.90 vs TTM −$0.07. The median is distorted by the three post-Zynga OCF-collapse years, but the latest year is a single thin year ($156.2M on $6,656.4M revenue) and the TTM already relapses below zero — neither distortion argument produces a positive *normalized* base. Per the engine's own note, a lone positive latest year is a flag to investigate, not a pass.
- **BASIS_BREAK_SUSPECT** — does not cross the engine's threshold, but the break is real: Zynga closed May 2022, revenue jumped in FY2023 and the share count jumped the same year (CSV). Every historical CAGR straddles the deal, and the pre-deal company (OE +$732.9M in FY2021, CSV) is not the company being priced.
- **OE_VOLATILE** — in substance: conservative OE totals of −$520.9M / −$493.4M / −$538.6M / +$156.2M across FY2023–26, positive in 1 of the last 5 years. Acquisition indigestion plus hit-cycle lumpiness, not a stable earnings stream to normalize.
- **HIGH_TV_SHARE / BIG_NET_CASH / THIN_HISTORY / SECTOR_MODEL_MISMATCH** — TV share 20.78% in the sensitivity run (the shortfall there is the base, not the terminal); no net cash (net debt, above); history is 10 fiscal years, not thin; sector is Technology and the OE/capex model fits a publisher's cost structure — the F is informative precisely because the model is not missing anything: capex is small and real, and SBC is counted as the cost it is.

## My thoughts / overlay
- This F has the shortest shelf life of any F so far — by design of the calendar, not the method. GTA VI launches November 19, 2026. Management guides FY2027 operating cash flow above $1B on $8.0–8.2B of bookings; if that files as guided, FY2027 conservative OE turns solidly positive and the TTM base flips during FY2027. The sweep does not capitalise guidance — it prices filed owner's earnings — and on filed numbers the buyer at $200.32 pays $36.839B for a company whose last twelve months produced −$13.1M of owner's earnings (ttm.py) and whose only positive OE year in five produced $156.2M.
- Note what the guided GTA VI year itself says about earnings quality: $8.0–8.2B of bookings guided to just $104–143M of GAAP net income. Even in the bull narrative, near-term conversion of the biggest launch in entertainment history into per-share owner's earnings is thin — development and marketing costs, platform cuts, and SBC see to that. The equity case rests on the *tail* (a decade of online recurrent spending), which is precisely what a trailing OE screen cannot see and should not pretend to.
- Method range: F (normalized median and filing-derived TTM — the final verdict) to D (single-positive-year capitalisation, weighted IRR 3.25%, IV@15% $10.40). No defensible trailing input set gets TTWO anywhere near the 15% hurdle, so there is **no hurdle-clearing price to quote on the final base**; on the generous sensitivity base the clearing price would be $10.40 itself, and a price with a real margin of safety would sit below that — numbers that simply restate how much of the price is forward franchise value.
- What would change the tier: two consecutive filings with TTM conservative OE solidly positive — i.e., the GTA VI quarters actually filing at guided OCF with SBC held near the guided path — plus a bookings trajectory that holds after the launch quarter. Re-run after the Q3 FY2027 10-Q (the launch quarter) files.

## Final verdict
- **Final tier: F** (= tier by numbers; no override — normalized and TTM conservative owner's earnings are both negative, and the lone positive year capitalises to only Tier D)
- Confidence: **Medium** — high confidence in the arithmetic (OE is negative under the normalized and TTM bases, and the generous-base sensitivity still yields only 3.25%); the F's shelf life is explicitly short because a guided, dated catalyst (Nov 19, 2026) will rewrite the base within two filings.
- One-liner: Elite franchise portfolio, moat 6/10, priced entirely on a launch that hasn't filed yet — owner's earnings are negative on normalized (−$2.90/share) and TTM (−$0.07/share) bases with only 1 positive year in 5, so it cannot clear the 15% hurdle at $200.32 on an OE DCF today; even capitalising that single positive year gives IV@15% of just $10.40.
