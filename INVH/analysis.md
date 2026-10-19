# INVH — Invitation Homes Inc.
Engine 5.4.0 run, 2026-10-16. All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
The largest U.S. single-family rental REIT: 85,509 wholly owned homes for lease at 2026-06-30, plus 8,069 jointly owned and 15,639 third-party managed homes, concentrated in the West, Florida and the Southeast across 16 core markets (10-Q filed 2026-07-30, via search summary of the filing). Revenue is rent plus a growing homebuilding / builder-partnership leg (ResiBuilt) and value-added services. SIC 6510 — Real Estate Operators & Lessors (fundamentals.json).

## Owner's earnings
**FY2025 (10-K, financials_history.csv):** operating cash flow $1,206,230,000; capex (PaymentsToAcquireOtherProductiveAssets) $242,752,000; SBC $27,830,000.
- **Conservative owner's earnings FY2025: $935,648,000 = $1.5259/share** (dcf_numbers.json base_oe_latest_per_share).
- Maintenance version FY2025 (NI + D&A − min(capex, D&A) − ΔNWC, financials_history.csv): $1,092,105,000 total — above the conservative figure, mainly because depreciation ($746,933,000) far exceeds the filed capex tag. For a housing landlord that gap is the central model caveat: roofs, HVAC and turns are real recurring costs, and the filed capex tag may not capture all of them, so the conservative OCF-based figure is the safer base.
- OE positive 5 of the last 5 fiscal years. Net debt $8,250,049,000 (dcf_numbers.json; basis TOTAL:LongTermDebt, cash $129,971,000 at FY2025). Market cap est. $16,414,769,867 at $26.77 (nasdaq_quote_api) — in scope under $40B.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct):**
- OCF: FY $1,206,230,000 − prior YTD $682,978,000 + current YTD $676,663,000 = **TTM $1,199,915,000**
- Capex: FY $242,752,000 − prior YTD $110,863,000 + current YTD $111,304,000 = **TTM $243,193,000**
- SBC: FY $27,830,000 − prior YTD $18,621,000 + current YTD $20,046,000 = **TTM $29,255,000**
- Shares (current-YTD weighted diluted): **599,328,126** — down from 613,177,806 FY2025 after ~$600M of buybacks since December 2025 at an average ~$26.30/share (Q2 2026 release, via search).
- **TTM OE total $927,467,000 → base OE/share $1.5475** (base_source: ttm_json)
- The engine's normalized base (median of last 3 FY OE/share) is $1.3965/share — lower because it averages FY2023–24; the TTM base is used because it is current, filing-derived, and already reflects the shrunken share count.

## Moat: 4/10 — weak-moderate
Justification: real local-density and scale economies in maintenance, leasing and builder sourcing, but rent is a market price, leases are annual with no switching costs, the SFR market is dominated by mom-and-pop owners, and measured returns are low.
- FOR: Largest SFR platform (~109k homes owned/JV/managed) with local density in 16 markets that lowers per-home maintenance and turn costs (in-house technicians vs contracted peers); vertically integrated acquire-renovate-lease-manage platform built since 2012; builder partnerships / ResiBuilt and construction lending give sourced supply competitors cannot easily match at scale; structural housing shortage and rent-vs-own cost gap support 97.1% Q2 2026 same-store occupancy.
- AGAINST: No network effects and no tenant switching costs — annual leases, rent set by local market, not by INVH; SFR supply is overwhelmingly fragmented mom-and-pop stock, so scale is an efficiency edge, not a barrier; AMH and other institutional landlords can replicate the model with capital; property-tax, insurance and maintenance cost inflation is largely uncontrollable; political/regulatory hostility to institutional landlords is a standing risk.
- Evidence on returns: fundamentals.json carries no roic_proxy for 2018–2025 (operating income is not tagged in those years) and no gross margin series (no COGS tag for this REIT) — those figures are not in the computed outputs, so they are not quoted. What is computed: ROE rose only from 2.67% (2021) to 6.17% (2025) in fundamentals.json, and the DCF OE yield at price is 5.78% (dcf_numbers.json diagnostics) — returns at or below a plausible cost of capital through the recent cycle. That is why the moat is 4, not the 7+ the rubric reserves for franchises with ROIC durably well above the cost of capital.
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — 5.4 final run (2026-10-16)
Growth recalibration (written reason): the engine's blended start is 5.62% (rev CAGR 5y 8.41%, 3y 6.84%, latest YoY 4.21%, OE/share CAGR 2y 4.53%), but that blend straddles the portfolio-expansion era. The organic engine today is much slower: Q2 2026 same-store core revenue +1.6% and same-store NOI +1.5%, with FY2026 guidance narrowed to same-store core revenue growth 1.5%–2.3% and same-store NOI growth 0.4%–1.9% (Q2 2026 release, via search). Total revenue +9.7% in Q2 was flattered by homebuilding revenue. Offsetting that, capital recycling (FY2026 wholly-owned disposition guidance raised to $750–$950M vs acquisition guidance $150–$350M) funds buybacks that lift per-share OE. Scenario growth starts were therefore set via offsets (−0.076 / −0.046 / −0.016 / +0.014 / +0.044 vs the blend) to −2.0 / +1.0 / **+4.0** / +7.0 / +10.0%. Even the super-bull start (10.0%) sits below Q2's reported total-revenue print (+9.7% is roughly at it, and that print includes homebuilding) and well above the same-store guide — it requires resumed portfolio growth plus mid-single-digit rent growth, which is why it carries only 10%. Probabilities 10/25/30/25/10 (defaults, kept — the distribution of outcomes is genuinely two-sided); OE multipliers 0.75/0.90/1.00/1.10/1.25 (defaults). Price $26.77.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | −2.0% | 0.75 | Sun Belt supply / tax & insurance squeeze; NOI shrinks, leverage bites | $8.00 | 6.11% |
| Bear | 25% | +1.0% | 0.90 | Same-store growth stays at the low end of guidance; costs outrun rent | $10.79 | 7.49% |
| Base | 30% | +4.0% | 1.00 | ~2% same-store growth plus buyback-driven per-share lift from recycling | $13.45 | 8.83% |
| Bull | 25% | +7.0% | 1.10 | Rent growth re-accelerates, builder/lending channels scale, buybacks compound | $16.59 | 10.37% |
| Super bull | 10% | +10.0% | 1.25 | Portfolio growth resumes at high-single-digit rent growth | $21.12 | 12.49% |

- **Probability-weighted: IV@15% $13.79 (−48.5% vs price), IV@12% $18.24, IV@10% $23.19, weighted IRR 9.01%, base-case IRR 8.83%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 5.78%, terminal value 18.27% of IV@15%, scenario spread 2.64x, net debt 8.69x normalized OE, 9.49 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.49 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above. TTM OE/share $1.5475 sits modestly above both the latest FY ($1.5259) and the 3-yr median ($1.3965).
- **SECTOR_MODEL_MISMATCH** (Finance sector — OE/capex DCF fits poorly): agreed and central. INVH is a REIT; the market prices it on Core FFO/AFFO (FY2026 guidance: Core FFO $1.92–$1.98, AFFO $1.62–$1.68 per the Q2 release) and on NAV, not on OCF-minus-capex. The engine's capex tag captures only part of recurring home capital spend while depreciation is $746,933,000/yr, so this DCF can misstate true maintenance economics in either direction. Confidence is **low** per the spec, and the name belongs with the sector misfits in the ranking.
- **HIGH_NET_DEBT** (net debt 8.69x normalized OE): balance sheet from the filings — total indebtedness $8,593M at 2026-06-30 with 92.4% fixed-rate or swapped, net debt / TTM Adjusted EBITDAre 5.4x (below the 5.5–6.0x target range), $1,546M liquidity, and a July 2026 $500M 4.950% senior note issue to 2032 used to prepay 2027 secured debt (Q2 2026 release, via search). Leverage is investment-grade and laddered, not distressed — but at 8.7x OE it is exactly why the bear cases are stressed with 0.75–0.90 multipliers and why the verdict sizes to the bear end.
- **TIER_BAND** (bear tier D at 7.49% vs bull tier C at 10.37%): the verdict spans D–C; sized to the bear end — final tier D. Even the super-bull case (12.49% IRR, IV@15% $21.12) does not clear the price, so the band does not change the conclusion.
- Preliminary run also flagged **WIDE_SCENARIO_SPREAD** (4.50x): after the growth recalibration the final spread is 2.64x; confidence is held at low anyway by the sector mismatch.

## My thoughts / overlay
- The honest headline is a method range, and both methods say "not cheap": on this OE DCF the weighted IV@15% is $13.79, roughly half the $26.77 price, and the price that clears a 15% hurdle is $13.79 (20%: $9.78; 25%: $7.57). On the market's own AFFO yardstick, FY2026 AFFO guidance is $1.62–$1.68/share against the $26.77 price, with a TTM dividend of $1.19/share (fundamentals.json) — a yield/income asset priced for stability, not for a 15% compounding return.
- Quality is real but unexceptional: OE positive 5/5 years, occupancy 97.1%, buybacks now shrinking the count, disciplined dispositions into strong private-market bids. None of that manufactures per-share growth much above low-single-digits organically.
- Risks: Sun Belt new-supply pockets, property-tax reassessments, insurance costs, institutional-landlord regulation, and refinancing at higher rates on the non-fixed 7.6% of debt. The offsetting tailwind is the structural U.S. housing shortage and the rent-vs-own affordability gap management cited on the Q2 call.
- Data section: enrichment ran in the standard order (fundamentals, prices, segments, statements, profile, reprice) with no failures. Non-blocking warnings: segments.json carries no tables (no dimensioned facts for the tracked concepts on the segment/product/geography axes), and profile.json found no headcount sentence in the 2026-02-19 10-K.

## Final verdict
- **Final tier: D** (weighted IRR 9.01% on the final 5.4 inputs; bear D 7.49% → bull C 10.37%, super-bull still only 12.49%)
- Confidence: **Low** (sector model mismatch for a REIT, plus 8.69x net debt to normalized OE)
- One-liner: Quality SFR landlord, moat 4/10 — at $26.77 it does not clear 15% on any scenario (weighted IRR 9.0%, IV@15% $13.79); it would need ~$13.79 to clear the hurdle.
