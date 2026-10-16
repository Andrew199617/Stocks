# FOXA — Fox Corporation
v5 run, 2026-10-14. In scope (market cap $27.310B at $62.21, nasdaq_quote_api). All figures below are copied from key_numbers.md, dcf_numbers.json, or financials_history.csv — none are recomputed.

## What it is
US media company built on live content: Fox News (the top-rated US cable news network), Fox Sports (NFL, MLB, college football, marquee soccer), the Fox broadcast network and local stations, Tubi (free ad-supported streaming), and the recently launched FOX One direct-to-consumer service. Revenue is distribution (affiliate/carriage fees) plus advertising, with advertising highly exposed to live sports and the political cycle. Per its FY2026 earnings release (Aug 6, 2026), full-year revenue was $17.13B and adjusted EBITDA $3.91B, both described as records; Q4 revenue rose sharply on the FIFA Men's World Cup broadcast and Tubi growth. Management also said the company has announced an acquisition of Roku — terms and closing are not in this run's computed outputs, so no figure for it is used anywhere below; it is treated as an overlay risk only.

## Owner's earnings
**FY2026 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,970,000,000; capex $502,000,000; SBC $132,000,000 (always a real cost).
- **Conservative owner's earnings FY2026: $1.336B** (key_numbers.md: latest FY OE total $1.336B, latest FY OE/share $3.04)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC), from financials_history.csv: $1,473,000,000 — same ballpark as the conservative figure, which supports the base.
- OE positive 5 of the last 5 fiscal years. Net debt $6.606B (key_numbers.md).
- **Lumpiness is the central quality issue:** conservative OE total was $1,405,000,000 in FY2024, $2,858,000,000 in FY2025, and $1,336,000,000 in FY2026 (financials_history.csv). FY2025 was a Fox Super Bowl + US election year; FY2026 had the World Cup in Q4 but a much lower full-year OCF print. Single-year bases are therefore unreliable in both directions.

**Base used = normalized base, median of last 3 FY OE/share: $3.04/share** (base_source: median_of_last_3_fy_oe_per_share). It equals the latest FY figure ($3.04), so there is no BASE_DIVERGENCE to resolve — the median is doing exactly its job here, refusing to capitalize the FY2025 event-cycle spike. No STALE_FY flag (3.5 months since FY end; FY2026 ended 2026-06-30 and was reported 2026-08-06), so no ttm.py run was required and no TTM base was used.

## Moat: 6/10 — moderate-strong, not wide
Justification: Fox News is the top-rated US cable news network with a loyal, highly engaged audience and proven affiliate-fee pricing power, and live sports rights (NFL through 2033, MLB, college football, marquee soccer) are scarce, DVR-proof inventory distributors must carry. Tubi adds scale in free ad-supported streaming (110M monthly active users at FY2026 close, record revenue quarter in Q4 FY26). Against that, the core content is rented not owned — sports rights reprice upward at renewal and leagues keep the leverage — the linear distribution base shrinks secularly with cord-cutting, the audience/event calendar is cyclical (Super Bowl, elections, World Cup rotate through Fox years), and the announced Roku acquisition would materially change the risk and leverage profile.
- FOR: Fox News: #1 cable news, loyal engaged audience, affiliate-fee pricing power; scarce live sports rights (NFL to 2033, MLB, college, soccer) — must-carry, DVR-proof; Tubi scale in free AVOD streaming — 110M MAU, record Q4 FY26 revenue; live news/sports mix resilient to time-shifting and subscription fatigue; aggressive buybacks compounding per-share value (shares -6.1%/yr).
- AGAINST: Sports rights are rented, not owned — renewal costs escalate, leagues hold leverage; cord-cutting shrinks the linear cable/broadcast distribution base secularly; event cyclicality: Super Bowl / elections / World Cup rotate, making OE lumpy; announced Roku acquisition adds integration, price and leverage risk; Murdoch family control / governance concentration; news-brand advertiser and litigation exposure.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.
- Governance note: the 2025 Murdoch family trust settlement left Lachlan Murdoch with sole voting control through 2050 (per search reporting of the settlement) — that removes succession deadlock risk, and it is also a permanent control concentration for Class A holders. Both effects are in the AGAINST/FOR balance above; neither changes the cash-flow inputs.

## DCF — v5 final run (2026-10-14)
Growth inputs: growth blend 4.89% (rev CAGR 5y 5.82%, rev CAGR 3y 4.72%, latest rev YoY 5.07%, OE/share CAGR 2y 1.97%), share-count adjustment +5.00% (share CAGR -6.14%), giving g_base 9.89%. Default probabilities 10/25/30/25/10, default offsets and OE multipliers were kept — no company-specific skew was defensible enough to override them.
**Sanity check vs actual prints:** the base start (9.9%) is an OE/share rate, not a revenue rate — it sits above the ~5% revenue prints because the buyback adjustment is already inside it; do not read it as a revenue forecast. The super-bull start (21.9%) is well above any recent revenue print and is justified only as a low-probability (10%) OE-recovery path: FY2026 OCF was depressed versus FY2025, the share count is shrinking fast, and the FY2027 midterm political cycle lands in the window. The bear start (4.9%) tracks the revenue blend and the super-bear start (-2.1%) is the cord-cutting / rights-cost stress case. Price $62.21.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -2.1% | 0.75 | Cord-cutting accelerates, sports rights reprice hard, Roku deal adds cost/leverage | $15.25 | 5.38% |
| Bear | 25% | 4.9% | 0.90 | Revenue grows at its blend rate, margins give back the FY2026 EBITDA step-up | $24.98 | 7.63% |
| Base | 30% | 9.9% | 1.00 | ~5% revenue growth plus continued buybacks drive OE/share | $34.67 | 9.77% |
| Bull | 25% | 14.9% | 1.10 | Tubi/FOX One monetization and political cycle lift OE/share faster | $47.60 | 12.38% |
| Super bull | 10% | 21.9% | 1.25 | OE recovers toward event-cycle highs while buybacks compound | $73.60 | 16.84% |

- **Probability-weighted: IV@15% $37.43 (-39.8% vs price), IV@12% $50.73 (-18.4%), IV@10% $65.70, weighted IRR 10.39%, base-case IRR 9.77%**
- **Tier by numbers: C.** Diagnostics (key_numbers.md): OE yield 4.89%, terminal value 20.8% of IV@15%, scenario spread 4.83x, net debt 4.94x normalized OE, 3.5 months since FY end.
- Decisive bound: even the super-bull case (10% weight) yields only 16.84% IRR. At $62.21 the stock clears Andrew's 15% hurdle only on the super-bull path — base and bull both fall short. That makes the C verdict robust to reasonable input disputes.

## Flags — every fragility flag resolved
- **BUYBACK_TAILWIND** (share count shrinking 6.1%/yr): already credited via the +5.00% growth adjustment inside g_base (share CAGR -6.14%); not double-counted in the verdict. Caveat recorded: this tailwind is a capital-allocation choice, not operating growth — if the announced Roku acquisition absorbs the cash now used for buybacks, the +5pp adjustment is the first input that breaks, and the base case falls toward the bear case.
- **WIDE_SCENARIO_SPREAD** (super-bull IV is 4.8x super-bear IV; key_numbers spread 4.83x): real — it reflects genuine event-cycle and rights-cost uncertainty, not a modeling artifact. Confidence is held at medium (never high under this flag) and the verdict is sized to the conservative end: the price fails the hurdle in every scenario except super bull.
- **HIGH_NET_DEBT** (net debt is 4.9x normalized OE; key_numbers: net debt $6.606B, 4.94x): folded into the verdict explicitly. Leverage of ~5x a lumpy, event-driven OE stream is why the bear cases are weighted 35% combined and why no leverage-driven tier upgrade is entertained: in the bear/super-bear paths (IV@15% $24.98 / $15.25) levered OE compresses fast, and any debt-funded Roku closing would raise this multiple further on the same OE base.

## My thoughts / overlay
- This is a genuinely good business priced for a better one. The OE stream is real, positive 5/5 years, low-capex relative to OCF, and per-share compounding from buybacks is material — but the normalized OE yield at the current price is only 4.89%, and the weighted DCF cannot reach the price at a 15% discount rate.
- The FY2025 spike is the trap in this name: capitalizing an election + Super Bowl year would flatter any single-year model. The median base ($3.04) is the honest anchor, and it happens to equal the latest (World Cup) year, which cuts both ways as a cross-check.
- Method sensitivity, stated honestly: the verdict is not one fragile input away from B. Clearing 15% on the weighted path requires either a materially higher base than the 3-year median or super-bull growth — neither is supported by the filed history in this run's outputs.
- Price that clears 15%: the weighted IV@15% of $37.43 is by construction the hurdle-clearing price on these inputs; a buyer wanting a margin of safety against the bear cases ($24.98) would demand a price well below $37.43, not merely at it.
- Watch items (no figures asserted): Roku acquisition terms/closing and any debt funding; pace of buybacks after it; sports-rights renewals; Tubi/FOX One monetization versus linear distribution decline.

## Final verdict
- **Final tier: C** (weighted IRR 10.39% on the v5 final inputs; tier_override: none)
- Confidence: **Medium** (capped by WIDE_SCENARIO_SPREAD; base and flags are clean, growth path and pending Roku deal are not)
- One-liner: Quality live news/sports cash generator, moat 6/10, but at $62.21 it does not clear 15% — weighted IRR 10.4%, weighted IV@15% $37.43; it would need to trade near $37 to clear the 15% hurdle.
