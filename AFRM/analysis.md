# AFRM — Affirm Holdings, Inc.
v5 run, 2026-10-14. Market cap $24.454B at $70.10 (nasdaq_quote_api) — in scope under $40B.

All figures below are copied from dcf_numbers.json, financials_history.csv, or ttm.py output — none are recomputed.

## What it is
US buy-now-pay-later consumer lender / two-sided payment network (fiscal year ends June 30). Merchants (571K active, $50.2B FY2026 GMV per the FY2026 10-K coverage) pay for checkout conversion; consumers pay interest on longer loans (no late fees). Growth is real and durable-looking: Q4 FY2026 revenue +33% YoY, GMV +36% (11th straight quarter of >30% GMV growth), FY2027 GMV guided above $64B, Affirm Card active cardholders more than doubled to 5.2M. It is also, structurally, a lender: a debt-funded loan book, credit losses, and funding costs sit between GMV and owner's earnings, and that is what this DCF prices.

## Owner's earnings
**FY2026 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,230,974,000; capex $238,346,000; SBC $304,671,000 (always a real cost).
- **Conservative owner's earnings FY2026: $687,957,000 = $1.97/share** (base_oe_latest_per_share $1.97).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,994,780,000 — **rejected as the headline**: FY2026 net income of $1,929,793,000 carries a $1,437,067,000 income-tax benefit (financials_history.csv tax line) from releasing the valuation allowance on domestic deferred tax assets — a one-time, non-cash entry (about $1.45B of Q4's net income per the earnings coverage). The OCF-based conservative figure excludes it; the NI-based maintenance figure is built on it.
- OE positive only **2 of the last 5 fiscal years**: FY2024 conservative OE was −$53,669,000, FY2025 +$280,287,000, FY2026 +$687,957,000 — a genuine inflection, but a young one.
- Net debt $8,164,020,000 (see HIGH_NET_DEBT under Flags — for a lender this is mostly loan-book funding, not corporate leverage in the usual sense, but it makes OE funding-dependent).

**Base used = the engine's normalized base, median of last 3 FY OE/share = $0.82/share** (base_source: median_of_last_3_fy_oe_per_share). The latest FY ($1.97) was NOT used as the headline base, and ttm.py could not arbitrate: it exited non-zero with "no post-FY YTD fact (no 10-Q since the 2026-06-30 fiscal year end)" for OCF, SBC, shares and capex — no quarter has been filed since the fiscal year ended 3.5 months ago, so there is no TTM evidence confirming the FY2026 level is a run-rate rather than a single benign-credit print. The median admittedly understates the current run-rate (its three years include the FY2024 loss year), so the method range was measured, not hand-waved — see Thoughts.

## Moat: 5/10 — moderate / narrow
Justification: a real two-sided network with rented distribution — merchants and consumers both multi-home, the biggest partners are non-exclusive and have switched before (Walmart to Klarna), funding is wholesale rather than deposits, and the credit book has never been through a deep recession.
- FOR: Two-sided network at scale — 571K merchants, $50.2B FY2026 GMV, repeat consumers driving the large majority of transactions; merchant dollar-based net expansion ~120% over the past three years.
- FOR: Checkout distribution that rivals must displace — Amazon renewed through January 2031, Shopify expanding internationally, Apple Pay integration.
- FOR: Underwriting data advantage — transaction-level credit data at >$50B/yr GMV, first BNPL lender reporting to Experian/TransUnion/FICO; interest-bearing mix (72% of transactions) monetizes far better than Klarna's zero-interest-heavy book.
- FOR: Affirm Card — 5.2M active cardholders, more than doubled YoY, ~19% attach; moves Affirm from a checkout button to everyday spend and raises consumer switching friction.
- AGAINST: Distribution is rented, not owned — partnerships are non-exclusive; Walmart shifted its primary BNPL relationship to Klarna, proving a top partner can walk.
- AGAINST: Competition from every direction — Klarna (~3x Affirm's global GMV), PayPal, Block/Afterpay, and card issuers' own installment products; consumers multi-home with no switching cost at checkout.
- AGAINST: No deposit funding — warehouse lines, securitization and loan buyers at a ~5.8% cost of funds vs banks' deposit costs; funding can reprice or close in a credit event.
- AGAINST: Credit is the product and the cycle is untested — delinquencies and provisions for credit losses are already rising; no deep-recession loss history.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Growth inputs: engine blended growth 29.62% (rev CAGR 5y 27.45%, rev CAGR 3y 32.05%, latest rev YoY 29.62% — the revenue tag is contract revenue; total-revenue prints run a few points higher), adjusted −5pp for the 5.7%/yr share-count growth → g_base 24.62%. Default offsets and OE multipliers; probabilities 10/25/30/25/10. Price $70.10.

Sanity check against actual prints: Q4 FY2026 GMV +36%, revenue +33%, FY2027 GMV guided above $64B vs $50.2B in FY2026. The base start (24.62%) sits below those prints — written reason: the −5pp dilution adjustment is already inside it, the FY2027 GMV guide itself implies deceleration from +36%, and a lender's OE does not scale 1:1 with GMV because provisions and funding costs grow with the book. Bull (29.62%) matches the latest revenue YoY; super bull (36.62%) matches the Q4 GMV print and needs a guidance beat plus operating leverage — possible, not the base case. Super bear (12.62%) is a credit-shock halving of growth with the OE multiplier at 0.75.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 12.62% | 0.75 | Credit shock: losses spike, funding reprices, growth halves | $7.68 | 4.03% |
| Bear | 25% | 19.62% | 0.90 | Normalization: growth fades fast, provisions eat leverage | $12.24 | 5.05% |
| Base | 30% | 24.62% | 1.00 | Guided deceleration, current OE level holds | $16.62 | 6.01% |
| Bull | 25% | 29.62% | 1.10 | Revenue growth holds at the latest print; card keeps compounding | $22.27 | 7.20% |
| Super bull | 10% | 36.62% | 1.25 | GMV-print growth persists with operating leverage | $33.22 | 9.31% |

- **Probability-weighted: IV@15% $17.70 (−74.7% vs price), IV@12% $24.60, IV@10% $32.41, weighted IRR 6.26%, base-case IRR 6.01%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 1.17%, terminal value 23.3% of IV@15%, scenario spread 4.33x, net debt 28.47x normalized OE, 3.5 months since FY end.
- Even the super-bull scenario (9.31% IRR) does not clear 10%, let alone the 15% hurdle — on the normalized base, the price is not a close call.

## Flags — every fragility flag resolved
- **BASE_DIVERGENCE** (latest FY $1.97 vs 3-yr median $0.82): both are distorted, in opposite directions. The median is dragged by the FY2024 loss year at a much smaller scale; the latest FY is a single print at the top of a benign credit/funding stretch, and for a lender OCF (hence OE) swings with loan-origination and loan-sale timing. ttm.py cannot arbitrate (no 10-Q since FY end — quoted above). Resolution: headline stays on the standardized median; the latest-FY alternative was measured with a full engine re-run (same moat/probs/offsets/mults, base pinned to $1.97) and is reported as the method range in Thoughts instead of being silently picked or silently dropped.
- **NI_OCF_DIVERGENCE** (2024, 2025, 2026): identified per year. 2026: net income $1,929,793,000 vs OCF $1,230,974,000 — the $1,437,067,000 deferred-tax valuation-allowance release sits in net income and is non-cash. 2025: net income $52,186,000 vs OCF $793,909,000, and 2024: net income −$517,757,000 vs OCF $450,138,000 — lender working capital (loan originations/sales, provisions) drives OCF far from NI in both directions. The base uses the OCF-based conservative OE throughout, so the tax one-off does not flatter it; it does flatter the maintenance definition, which is why that definition is not the headline.
- **SECTOR_MODEL_MISMATCH** (Finance): real and binding. For a lender, "capex" is not the reinvestment — growing the loan book is — and the engine's balance-sheet capture misses the loan assets the debt funds. Confidence graded **low**, tier treated as soft: the DCF is a valuation-discipline check (what OE path the price requires), not a precise lender model.
- **HIGH_NET_DEBT** (net debt $8,164,020,000 = 28.47x normalized OE): mostly securitization/warehouse debt funding the loan book, not plant-style corporate leverage — the engine records no offsetting loan-receivable asset (assets_current is null in the pull), so the 28.5x ratio overstates solvency risk. The genuine risk it points at is funding dependence: if loan buyers or warehouse lenders step back, OE stops regardless of demand. Folded into the verdict via the bear/super-bear OE multipliers (0.90/0.75) and the low confidence.
- **DILUTION** (share count +5.7%/yr): shares diluted 295,343,466 (FY2023) → 309,857,129 (FY2024) → 341,023,566 (FY2025) → 348,846,647 (FY2026). SBC dollars are falling — $451,709,000 (FY2023) → $344,511,000 → $321,433,000 → $304,671,000 (FY2026) — but the count keeps rising because there is no buyback offset. Already deducted via the −5pp growth adjustment; not double-counted.
- **LOW_OE_YIELD** (1.17%): at $70.10 the valuation rests almost entirely on the growth path — there is no current-OE cushion. This is exactly why the tier is fragile to the base choice (see method range) and why the verdict sizes to the conservative end.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.33x super-bear IV): real — the outcome range for a young lender at an inflection IS wide. Confidence is low (also capped by the sector mismatch), and even the widest end of the spread does not rescue the price: super bull IRR is 9.31% on the headline base.

## My thoughts / overlay
- **Method range (measured, both runs are engine runs on this date):** normalized-median base $0.82 → weighted IRR 6.26%, IV@15% $17.70, Tier D. Latest-FY base $1.97 (all other inputs identical) → weighted IRR 10.70%, IV@15% $42.48, Tier C, upside at 15% −39.4%. The defensible range is **D to C** — the base choice moves the tier, but no defensible base gets near the 15% hurdle at $70.10. That range, not the single D, is the honest headline.
- What the price requires: roughly the latest-FY OE level sustained AND super-bull growth — i.e., $70.10 pays today for the inflection being permanent, credit staying benign, and funding staying cheap, all at once.
- Quality is improving, genuinely: first GAAP operating profit in FY2026 (operating income $416,977,000 vs −$87,273,000 in FY2025, from financials_history.csv), SBC dollars falling three straight years, GMV growth >30% for 11 straight quarters. None of that is in dispute; the dispute is only what it's worth, and on owner's earnings it isn't worth $70.10 yet.
- Hurdle-clearing price: the weighted IV@15% is **$17.70** on the headline base and $42.48 on the most generous defensible base — a buyer who believes the FY2026 run-rate fully still needs a price in the low $40s or below to clear 15% with any margin of safety.
- Watch items that would change the base: the Q1 FY2027 10-Q (first post-FY print — ttm.py becomes computable), delinquency/provision trajectory, and any loss of a top distribution partner on the Walmart pattern.

## Final verdict
- **Final tier: D** (weighted IRR 6.26% on the normalized base; method range D to C across defensible bases — sized to the conservative end because the spread is wide and the sector model fits poorly)
- Confidence: **Low** (SECTOR_MODEL_MISMATCH on a lender, WIDE_SCENARIO_SPREAD 4.33x, base divergence unresolved by any filed TTM data)
- One-liner: Fast-growing BNPL lender with a real profitability inflection and a moderate 5/10 moat — but at $70.10 it prices in the inflection as permanent; weighted IRR 6.3% on the normalized base (10.7% even on the latest-FY base), IV@15% $17.70 vs $70.10 — clears 15% only in the low $40s at best.
