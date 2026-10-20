# FCFS — FirstCash Holdings, Inc.
Pass-1 run, 2026-10-20, engine release 5.5.0. Price $214.78 (nasdaq_quote_api), market cap $9,563,294,280 — in scope under $40B.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, fundamentals.json or financials_history.csv — none are recomputed.

## What it is
The largest international operator of retail pawn stores: more than 3,300 stores across the U.S., Latin America and the U.K. (profile.json, 10-K Item 1; ~22,000 employees), plus the AFF (American First Finance) retail point-of-sale payment-solutions segment. Pawn loans are small, short-term and collateralized by personal property; unredeemed collateral is sold at retail. Management guides the combined pawn segments to over 90% of 2026 net revenue and segment pre-tax income, with AFF shrinking.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $585,942,000; capex $54,906,000 (PaymentsToAcquireProductiveAssets); SBC $20,250,000 (always a real cost).
- **Conservative owner's earnings FY2025: $510,786,000 = $11.47/share** (base_oe_latest_per_share $11.4716)
- Maintenance version: not printed separately in the computed outputs for this filer (D&A is not tagged), so no second figure is quoted.
- OE positive 5 of the last 5 fiscal years. Net debt $2,083,237,000 at FY2025 (total debt $2,208,434,000 less cash $125,197,000), plus operating lease liabilities of $360,225,000.
- Annual OE/share path: FY2023 $7.49, FY2024 $10.12, FY2025 $11.47; the engine's normalized (3-yr median) base is $10.1162/share.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct):**
- OCF: FY $585,942,000 − prior YTD $243,494,000 + current YTD $330,405,000 = **TTM $672,853,000**
- Capex: FY $54,906,000 − prior YTD $30,298,904 (OVERRIDE, prorated) + current YTD $30,298,904 (OVERRIDE, prorated) = **TTM $54,906,000** — the two estimated YTD legs are equal-length and cancel; the filed FY leg is the whole TTM capex figure
- SBC: FY $20,250,000 − prior YTD $9,050,000 + current YTD $10,750,000 = **TTM $21,950,000**
- Shares (current-YTD weighted diluted): **44,142,000**
- **TTM OE total $595,997,000 → base OE/share $13.5018** (base_source: ttm_json)
- The TTM base is used because the last fiscal year ended 9.6 months ago and 2026 prints are materially above FY2025 (fundamentals.json TTM to 2026-06-30: total revenue $4,120,337,000, +21.6% YoY; net income $388,148,000, +33.0%; OCF +21.3%). The normalized median ($10.12) is retained in the reporting; a run on the median base instead printed a weighted IRR of 10.6% (Tier C) in this run's preliminary pass — the method range on the base choice alone is roughly 10.6%–13.0%, Tier C either way.

## OVERRIDE — capex (TTM legs only)
- **The gap:** FirstCash files capex annually in the 10-K but tags no capex in its 10-Qs; ttm.py's first pass exited 3 ("capex: no post-FY YTD fact"). No annual year is missing — annual capex is filed for every year in the history, so there is no DATA_GAP and the override fills no annual period (dcf_numbers.json overrides_applied is empty).
- **The decision (bounded estimate authority):** judgment.json carries `capex_override = {value: 61100000, kind: "estimate", source: "Average of the last three filed fiscal years' capex from financials_history.csv (FY2023 $60,148,000; FY2024 $68,245,000; FY2025 $54,906,000; PaymentsToAcquireProductiveAssets, 10-K filed 2026-02-09)"}` — 1.11× the last filed value, inside the 0.1×–10× band. Filed capex has run $35.6M–$68.2M/yr over the last decade, so the run-rate anchor is stable.
- **How it was applied:** ttm.py filled only the two YTD capex legs, prorated by days ($30,298,904 over 181 days each; ttm.json overrides_used). Because both legs cover the same 181-day span, they cancel exactly and TTM capex equals the filed FY2025 figure of $54,906,000 — the estimate moves the TTM base by construction by ~nothing; its effect is binary (without it no TTM base exists). make_score records it as a TTM-legs-only override (scope "ttm_legs") and measures its impact on the TTM base.

## Moat: 5/10 — moderate / narrow
Justification: largest international pawn operator with scale in collateral appraisal and liquidation, licensing barriers and a proven acquisition platform (H&T closed 2025, Ramsdens pending). Evidence first: fundamentals.json's roic_proxy series is null for every year because the filer does not tag operating income, so the return evidence is ROE and margins — ROE rose 11.0% (FY2023) → 12.6% (FY2024) → 14.5% (FY2025), and gross margin on total revenue rose 47.8% → 48.1% → 50.3% over the same years (50.5% TTM). Returns are above a plausible cost of capital but not wide-moat level, and they are earned in a regulated, transactional business.
- FOR: scale — largest international pawn operator, 3,300+ stores in the U.S., Latin America and U.K.; collateral appraisal and liquidation expertise built over decades, hard to replicate store-by-store; licensing and regulatory compliance barriers across many jurisdictions; acquisition platform in a fragmented industry (H&T 2025, Ramsdens pending) with geographic diversification; counter-cyclical pawn demand and durable gross margins (47.8% FY23 to 50.3% FY25).
- AGAINST: no network effects or switching costs — pawn customers are transactional and price-sensitive; fragmented local competition from independent pawnshops, online lenders and lease-to-own providers; regulatory risk — pawn-rate caps and consumer-credit rules (incl. the AFF point-of-sale business); FX exposure (Mexican peso and now sterling) and gold-price exposure via jewelry collateral; AFF segment shrinking (management guides its net revenue down 20–25% in 2026) and a goodwill-heavy balance sheet from acquisitions.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — final run (2026-10-20)
Growth: the engine's blended start is 12.25% (components, on the filer's contract-revenue line: 5-yr CAGR 9.18%, 3-yr CAGR 9.78%, latest YoY 10.70%, OE/share CAGR 2-yr 23.73%, plus a +2.01pp buyback adjustment on the revenue components). Sanity check against actual prints: total revenue grew +8.0% in FY2025 and +21.6% TTM to Q2 2026, with Q2 2026 alone +29.4% — but the TTM/Q2 prints include the acquired H&T U.K. business and favorable FX translation; same-store pawn receivables grew +22% in Q2 2026, and guidance for H2 2026 is mid-teens-or-better pawn-fee growth, U.S. retail merchandise sales +10–15% and ~+20% Latin America pawn fees in USD, against AFF net revenue guided down 20–25%. A 12.25% base start sits on the guided organic range and below the acquisition-inflated prints — that is the written reason the base (and even the 17.25% bull start) sit below the latest +29.4% print: the prints annualize an acquisition step-up that does not repeat. Default offsets (−12/−5/0/+5/+12pp) and OE multipliers (0.75/0.90/1.00/1.10/1.25) are kept; probabilities are the defaults 10/25/30/25/10. Price $214.78.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 0.25% | 0.75 | Pawn demand rolls over, rates capped, peso/gold reverse | $75.61 | 6.82% |
| Bear | 25% | 7.25% | 0.90 | Growth fades to high-single digits; AFF drag bites | $121.38 | 9.73% |
| Base | 30% | 12.25% | 1.00 | Guided organic pawn growth decays over the CAP | $165.68 | 12.35% |
| Bull | 25% | 17.25% | 1.10 | Same-store momentum persists; Ramsdens adds a second U.K. leg | $223.42 | 15.44% |
| Super bull | 10% | 24.25% | 1.25 | TTM print rates (~+22–29%) sustain for years | $336.33 | 20.57% |

- **Probability-weighted: IV@15% $177.10 (−17.5% vs price), IV@12% $240.02, IV@20% $121.29, IV@25% $91.11, weighted IRR 13.01%, base-case IRR 12.35%**
- **Tier by numbers: C.** Diagnostics (dcf_numbers.json): OE yield 6.29%, terminal value 20.7% of IV@15%, scenario spread 4.45x, net debt 3.47x normalized OE, 9.6 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.6 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above. ttm.py's first pass exited 3 because no capex is tagged in the 10-Qs; the bounded capex estimate in the OVERRIDE section fills only those two legs.
- **BUYBACK_TAILWIND** (share count shrinking 2.0%/yr): already credited via the +2.01pp growth adjustment in the blend; not double-counted in the verdict. The buyback is real cash: share repurchases were $115,849,000 in FY2025 (statements.json) alongside $70,875,000 of dividends paid.
- **NI_OCF_DIVERGENCE** (net income vs OCF differ by >40% in 2023, 2024, 2025): persistent and structural, not a one-off. OCF exceeds net income in all three years ($416,142,000 vs $219,301,000; $539,958,000 vs $258,815,000; $585,942,000 vs $330,375,000 — statements.json). Of the gap, the computed outputs itemize SBC ($13,674,000 / $14,786,000 / $20,250,000) and deferred income taxes (−$13,476,000 / −$7,377,000 / +$19,354,000), with working-capital lines small; the standardized statements do not break out the remaining non-cash addbacks (depreciation and amortization, including acquired-intangible amortization, are not tagged separately by this filer — D&A is blank in financials_history.csv), so the remainder is stated in words rather than assigned a figure. The OCF-based conservative OE is the series used throughout, and net income itself compounding (+33.0% TTM, fundamentals.json) corroborates that the cash earnings are not an accounting artifact.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.45x super-bear IV): real — the range is driven by whether the current acquisition-and-gold-inflated growth prints persist. Confidence is capped at medium, and the verdict is sized to the conservative end.
- **HIGH_NET_DEBT** (net debt 3.5x normalized OE on the TTM base; 4.6x on the normalized median base in the preliminary run): balance sheet from the filings — total debt $2,208,434,000 and cash $125,197,000 at FY2025 (net debt $2,083,237,000), plus $360,225,000 of operating lease liabilities the ratio excludes. The debt funded the H&T acquisition and store growth; it is the main reason the bear cases are stressed (bear OE mult 0.90 on a levered base) and why the verdict sizes to the bear end.
- **TIER_BAND** (bear-case tier D at 9.73% vs bull-case tier B at 15.44%): the verdict spans tiers; any position should be sized to the bear end — at the current price even the base case (12.35%) does not clear 15%.

## My thoughts / overlay
- The honest headline is the range: on the stale 3-yr median base the same scenario set prints a 10.6% weighted IRR; on the current TTM base it prints 13.0%. Both are Tier C and both sit below the 15% hurdle at $214.78 — the disagreement is about how far below, not about the verdict.
- Quality is genuinely good: OE positive 5/5 years, OE/share compounding from $7.49 to $11.47 (FY) to $13.50 (TTM), gross margin expanding, and capital returned every year (FY2025 buybacks $115,849,000 + dividends $70,875,000). The problem is price, not business quality: the market is paying for the H&T step-up and the current pawn-demand surge as if they were the permanent growth rate.
- Risks: leverage at 3.5x normalized OE (leases excluded) into a business whose collateral values track gold and consumer stress; peso/sterling translation; pawn-rate and consumer-credit regulation on both the pawn and AFF sides; acquisition execution (Ramsdens still to close, goodwill already large); AFF in guided decline.
- Hurdle prices (weighted): clears 15% at or below $177.10, 20% at or below $121.29, 25% at or below $91.11. Street consensus is Buy with a $254.00 mean target (street.json, 6 analysts) — this model's weighted IV@15% sits well below the Street, which is the disagreement a buyer has to underwrite.

## Final verdict
- **Final tier: C** (weighted IRR 13.01% on the TTM base; bear D 9.73%, bull B 15.44% — sized to the bear end per TIER_BAND)
- Confidence: **Medium** (TTM base is filing-direct except for one self-cancelling estimated capex leg; WIDE_SCENARIO_SPREAD caps confidence)
- One-liner: Quality pawn franchise, moat 5/10 — TTM owner's earnings $13.50/share but the weighted IRR is 13.0% at $214.78, short of the 15% hurdle; it clears 15% at or below the $177.10 weighted IV@15%.
