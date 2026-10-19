# VIAV — Viavi Solutions Inc.
Engine 5.4.0 run, 2026-10-18. All figures below are copied from dcf_numbers.json, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
Network test & measurement and optical products, ex-JDS Uniphase. Two segments: Network and Service Enablement (NSE — lab, production and field test for networks; FY26 revenue $1.18B, 77.9% of total per company earnings reporting, now including the Spirent high-speed Ethernet / security product lines and Inertial Labs acquired in fiscal Q2 2026) and Optical Security and Performance Products (OSP — 3D sensing and anti-counterfeiting optical products; Q4 FY26 revenue $89.2M at a 55.2% gross margin and 40% operating margin per the Q4 call). The data-center ecosystem is now ~50% of NSE revenue; aerospace & defense ~17%. Market cap $7.66B at $33.38 (nasdaq_quote_api) — in scope under $40B.

## Owner's earnings
**FY2026 (10-K, period ended 2026-06-27, filed 2026-08-13):** operating cash flow $113,900,000; capex $31,100,000; SBC $55,400,000 (always a real cost — and here it is 49% of OCF).
- **Conservative owner's earnings FY2026: $27,400,000 = $0.119/share** (OCF − capex − SBC).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): **−$76,000,000** — net income −$30,400,000 + D&A $40,400,000 − capex $31,100,000 − ΔNWC $54,900,000 (working-capital build into the growth/acquisition year). The maintenance definition is *worse* than the conservative one, so the conservative base is the generous choice, not a penal one.
- OE positive 5 of the last 5 fiscal years on the conservative definition, but thin and volatile: OE/share $0.605 (FY21), $0.224 (FY22), $0.052 (FY23), $0.213 (FY24), $0.039 (FY25), $0.119 (FY26).
- **Base used = normalized base, $0.119/share** (base_source: median_of_last_3_fy_oe_per_share — the median of FY24/FY25/FY26 equals the FY26 figure, so there is no stale-median distortion to fix). No STALE_FY flag (FY ended 3.7 months ago) and no TTM override: fundamentals.json's TTM through 2026-06-27 is the same fiscal year (TTM OE/share $0.119, identical legs).
- Balance sheet (filing): cash $647,800,000, debt_current $244,800,000 → **net cash $403,000,000** on the engine's CURRENT_ONLY:DebtCurrent basis, lease liabilities $43,000,000, equity $1,448,500,000. In Q4 FY26 the company issued ~12.78M shares at $45 for $575M gross (fundamentals.json: share issuance TTM $575,000,000) and used the proceeds to repay the remaining Term Loan B, per the Q4 earnings call. Dilution note: shares outstanding (DEI) 246,749,828 at 2026-07-28 vs 229,500,000 diluted weighted average for FY26 — the offering landed late in the year, so forward per-share figures carry the bigger count.

## Moat: 4/10 — weak-to-narrow
Justification: a real #2 position in network test (14–16% share vs Keysight's 18–20%, per market-research summaries) and a genuinely strong niche in OSP, but consolidated returns say no durable wide moat: the roic_proxy series in fundamentals.json runs 9.8% (FY21), 23.2% (FY23), 7.8% (FY24), 8.5% (FY25), 7.9% (FY26) — recent years sit around the cost of capital, not well above it (the FY20/FY22 prints of 96%/81% are artifacts of a tiny invested-capital denominator on a net-cash balance sheet, not economics). Gross margin has been flat for a decade: 58.5% (FY20), 59.6%, 59.8%, 57.8%, 57.6%, 57.3%, 57.7% (FY26) — no pricing-power expansion even as mix shifted to data center.
- FOR: #2 share in network test & measurement (14–16%) in a concentrated oligopoly with high R&D/IP barriers; Spirent deal gives a 40–45% high-share position in AI data-center Ethernet validation (Appledore via RCR Wireless); OSP niche — anti-counterfeiting and 3D sensing at 55.2% gross / 40% operating margin (Q4 FY26 call); tools embedded in carrier and hyperscaler lab/field workflows, with calibration/service attach.
- AGAINST: Keysight is larger, broader and better resourced across every overlapping category; consolidated ROIC ~8% in FY24–26, at the cost of capital; gross margin flat at ~57–60% for ten years — no demonstrated pricing power; end demand is cyclical capex (revenue fell FY22 $1,292M → FY24 $1,000M before the AI snap-back); SBC runs 49–59% of OCF (FY25–26), a persistent transfer to employees; growth is partly bought (Spirent + Inertial Labs) at the cost of amortization and restructuring charges.
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — final run (engine 5.4.0, 2026-10-18)
**Growth-start sanity check (mandatory):** the engine blend is 7.59% (rev CAGR 5y 4.85%, rev CAGR 3y 11.18%, latest rev YoY +40.03%, OE/share CAGR 2y −25.27%). Every scenario start is below the latest *revenue* prints (FY26 +40.0%, Q4 +52.5%, Q1 FY27 guided $450–460M vs $299.1M in Q1 FY26) — written reason: those prints are revenue, not owner's earnings, and they are acquisition-inflated (Spirent product lines contributed $145M of FY26 revenue; a full Spirent quarter lands in Q1 FY27). OE/share *fell* over the same window — FY26 OE/share $0.119 vs $0.605 in FY21 on higher revenue — because SBC, acquired-intangible amortization and restructuring scale with the deals. Scenario starts are OE growth rates off a depressed $0.119 base, and even the super-bull start (19.6%) sits far below the revenue prints for that reason. Probabilities were skewed bearish vs the 10/25/30/25/10 default (15/30/30/15/10) per the OE_VOLATILE flag's instruction to widen bear weight. Offsets −12/−5/0/+5/+12pp and OE multipliers 0.75/0.90/1.00/1.10/1.25 are the defaults. Price $33.38.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −4.4% | 0.75 | AI test capex digestion; carrier softness returns, OE shrinks | $0.56 | 2.69% (at floor) |
| Bear | 30% | 2.6% | 0.90 | Growth fades to terminal almost immediately; SBC stays ~half of OCF | $0.88 | 2.83% (at floor) |
| Base | 30% | 7.6% | 1.00 | Engine blend: mid-single-digit OE growth fading over the 7.2-yr CAP | $1.19 | 2.97% (at floor) |
| Bull | 15% | 12.6% | 1.10 | Data-center validation share holds; operating leverage finally reaches OE | $1.58 | 3.15% |
| Super bull | 10% | 19.6% | 1.25 | Spirent integration pays off, OSP compounds, OE margins normalize | $2.32 | 3.51% |

- **Probability-weighted: IV@15% $1.18 (−96.5% vs price), IV@12% $1.57, IV@10% $2.00, weighted IRR 2.97% — at the solver floor, i.e. "at most ~3.0%" (see IRR_AT_FLOOR). Base-case IRR 2.97%.**
- **Tier by numbers: D** (bear D, bull D — no tier band). Diagnostics: OE yield 0.36%, terminal value 19.0% of IV@15%, scenario spread 4.14x, net debt −14.71x normalized OE (net cash), 3.7 months since FY end.
- Hurdle-clearing prices: the stock clears 15% only at or below **$1.18**, 20% at $0.82, 25% at $0.63.

## Flags — every fragility flag resolved
- **OE_VOLATILE** (OE/share spans >3x over 5 years): real cyclicality, not an inflection — OE/share went $0.605 → $0.052 → $0.119 across FY21–26 as carrier capex rolled over and came back. Handled by the normalized (median) base and by widening bear weight (super bear + bear = 45%).
- **NI_OCF_DIVERGENCE** (2024, 2025, 2026): structural, not a tax-deposit one-off. FY26 net income −$30,400,000 vs OCF $113,900,000 — the $144.3M gap is non-cash charges: SBC $55,400,000 and depreciation $40,400,000 (both tagged), plus acquired-intangible amortization and the restructuring charge (a ~5% workforce reduction announced in Q2 FY26, ~$32M of charges for ~$30M of annual savings per the Q2 call) inside net income. Because the conservative OE definition deducts SBC in full, the divergence does not flatter the base — the base is $0.119/share *after* that deduction.
- **IRR_AT_FLOOR** (super bear, bear, base, weighted): accepted as the finding. At $33.38 the price is beyond the model's range; the expected return reads "at most ~3.0%", not a precise 2.97%. This also suppresses any alert (moot — Tier D).
- **LOW_OE_YIELD** (base OE yield 0.4%): the core of the verdict. At $33.38 the buyer pays ~280x conservative owner's earnings; the entire valuation rests on OE growth that has not yet appeared in a single fiscal year at this revenue scale.
- **WIDE_SCENARIO_SPREAD** (4.14x): real — super-bull IV@15% is still only $2.32. Confidence is capped at medium; in practice the spread does not matter because every scenario is a D.
- **BIG_NET_CASH** (net cash 14.7x normalized OE): noted — net cash is $403,000,000, but that is only ~5% of the $7.66B market cap; the cash pile is large next to the tiny OE base, not next to the price. It does not rescue the verdict.

## My thoughts / overlay
- The market is pricing VIAV on non-GAAP earnings (FY26 non-GAAP EPS $1.00, Q1 FY27 guided $0.40–0.42 at a 27.1% non-GAAP operating margin). The owner's-earnings lens strips out exactly what non-GAAP adds back — SBC ($55.4M, ~half of OCF) and deal amortization — and on that lens the company earned $0.12/share against a $33.38 price. Even crediting the bull case in full, IV@15% is $1.58.
- The honest bull argument is operating leverage: revenue +40% with non-GAAP operating margin +630bp to 20.6% in FY26, and Q4 OCF of $66.7M annualizes far above the FY26 OCF. If GAAP costs converge toward non-GAAP over the next two years, OE/share could multiply off this base. That is a forecast, not a filing: FY26 is the highest-revenue year in the company's history and it still produced a GAAP net loss and negative maintenance OE.
- Method range: there isn't one worth reporting — median base, latest-FY base and TTM base are all $0.119/share, and both OE definitions are at or below that. Every defensible method lands on Tier D.
- Balance-sheet risk is low (net cash, Term Loan B repaid); the risk is purely the price and the dilution used to get here ($575M raised at $45 in Q4 FY26 — above today's $33.38, so at least the raise itself was well timed for existing holders).

## Final verdict
- **Final tier: D** (weighted IRR 2.97%, at the floor — read as at most ~3.0%; IV@15% $1.18 vs $33.38)
- Confidence: **Medium** (high on the OE arithmetic — both definitions agree the base is tiny; the uncertainty is whether GAAP-to-non-GAAP convergence ever delivers the OE the price already assumes)
- One-liner: Real AI data-center test franchise, moat 4/10 — but owner's earnings are $0.12/share against a $33.38 price (weighted IRR at most ~3.0%, IV@15% $1.18); clears 15% only below ~$1.18.
