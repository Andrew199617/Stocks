# CPRT — Copart, Inc.
v5 run, 2026-10-15. In scope (market cap $25.271B at $26.41, nasdaq_quote_api).

All figures below are copied from key_numbers.md, dcf_numbers.json, or financials_history.csv — none are recomputed. Earnings-release and deal facts are paraphrased from the cited search results (FY2026 earnings release via Business Wire/Morningstar, Q4 call coverage, ACV deal coverage).

## What it is
The dominant US salvage-vehicle auction marketplace: insurers, dealers, fleets and finance companies assign damaged and total-loss vehicles to Copart's 250+ locations in 11 countries, and ~1M members in 185+ countries bid online. Mostly a fee-for-service model (it facilitates sales rather than owning inventory), with a smaller purchased-vehicle segment. RB Global's IAA is the principal rival — effectively a duopoly.

## Owner's earnings
**FY2026 (10-K via EDGAR, from financials_history.csv):** revenue $4,666,209,000; operating cash flow $1,604,492,000; capex $337,363,000 (tag: PaymentsToAcquirePropertyPlantAndEquipment); SBC $38,818,000 (always a real cost, and small here).
- **Conservative owner's earnings FY2026: $1,228,311,000 = $1.28/share** (latest FY OE/share, key_numbers.md)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,691,164,000 — above the conservative figure because capex ran well above D&A in FY2026 (yard/land investment) and net working capital released cash; the conservative OCF-based figure is the one used, so the base is not flattered by the gap.
- OE positive 5 of the last 5 fiscal years. Base used = the engine's normalized base, **median of last 3 FY OE/share = $1.22/share** (latest FY $1.28). No STALE_FY flag — FY2026 ended 2026-07-31, 2.5 months ago — so no TTM override was needed or used.
- Balance sheet: the engine's net-debt field is null (recent-year cash/debt tags not populated in the history pull), so no net-debt figure is quoted from the engine. Per the FY2026 earnings release, Copart ended the year with ~$1.91B of cash, equivalents and restricted cash plus $2.58B of held-to-maturity securities against ~$913.9M of total liabilities — a debt-free, large net-cash balance sheet. It also deployed $1.63B into share repurchases during FY2026 (per the Q4 call coverage) and has agreed to pay ~$1.9B cash for ACV Auctions (below) without denting solvency.
- FY2026 quality caveat: revenue grew only +0.41% and net income fell (FY net income $1,484,270,000 vs $1,552,449,000 in FY2025, per financials_history.csv); Q4 net income fell 17.4% YoY per the earnings release. Global units sold fell 5.5% for the year (−3.1% excluding catastrophe units), and FY2025 comparisons were inflated by one-time hurricane (Helene/Milton) revenue. OE/share still grew because capex normalized down ($337M vs $569M in FY2025) and buybacks shrank the count (956,860,000 diluted shares, latest).

## Moat: 8/10 — strong, near-wide
Justification: Dominant salvage-auction marketplace in a structural duopoly with RB Global's IAA: long-term insurer seller relationships, a scarce permitted land bank of 250+ yards near metro areas, and a global buyer network whose bidding depth raises seller proceeds and locks in assignments. Proven pricing power (revenue per unit rose even as FY2026 volumes fell), asset-light service model, debt-free balance sheet, and high returns on capital held through cycles. Not a 9-10: volume is hostage to insurance claims activity and insurer total-loss behavior, international buyers are FX/tariff-sensitive, and RB Global is a credible, consolidating rival.
- FOR: Salvage duopoly with RB Global/IAA; dominant share of insurer salvage assignments
- FOR: Scarce, permitted land bank — 250+ locations near metro areas, hard to replicate
- FOR: Global buyer network (~1M members, 185+ countries) deepens bids and seller proceeds
- FOR: Proven pricing power — revenue per unit rose while FY2026 volumes fell
- FOR: Asset-light service model; debt-free with large net cash
- AGAINST: Volumes hostage to insurance claims activity and insurer total-loss thresholds
- AGAINST: Insurer concentration — a few large carriers drive assignment flow
- AGAINST: International buyers bought 38.2% of US units in FY2026 — FX/tariff sensitive
- AGAINST: RB Global/IAA is a credible consolidating rival
- AGAINST: ACV integration and dealer-channel expansion is unproven for Copart
- An 8 gives CAP = 12.4 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 12.4 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Growth sanity check (mandatory): the engine's blended growth is 9.03% → g_base 9.37%, but its components disagree — rev CAGR 5y 11.63%, rev CAGR 3y 6.44%, latest rev YoY only +0.41%, OE/share CAGR 2y 16.24%. The latest prints (FY2026 revenue +0.41%, Q4 revenue +2.4%, units −5.5%) sit far below the blend because FY2025 carried one-time hurricane revenue and FY2026 claims volume softened; the OE/share CAGR is flattered by the FY2025 capex spike rolling off and buybacks. Scenario starts were therefore recalibrated with offsets (−0.12 / −0.06 / −0.02 / +0.03 / +0.10 vs g_base) to center the base at 7.4% — between the 3-yr and 5-yr revenue CAGRs, above the depressed latest print for a written reason: hurricane comps wash out, total-loss frequency has a structural tailwind from repair costs and vehicle complexity, and ACV is guided accretive from FY2028. Probabilities were skewed slightly bear-ward (10/30/30/20/10 vs the 10/25/30/25/10 default) because the current volume/margin trend is negative; OE multipliers left at defaults 0.75/0.90/1.00/1.10/1.25. Price $26.41.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -2.6% | 0.75 | Claims volumes keep shrinking; insurers in-source or shift share to IAA | $5.83 | 5.00% |
| Bear | 30% | 3.4% | 0.90 | Hurricane comps wash out but volume/margin pressure persists | $9.40 | 7.00% |
| Base | 30% | 7.4% | 1.00 | Volumes normalize; fee-per-unit growth carries mid-single-digit growth | $12.76 | 8.83% |
| Bull | 20% | 12.4% | 1.10 | Volume recovery + ACV dealer channel adds a second growth lane | $18.06 | 11.48% |
| Super bull | 10% | 19.4% | 1.25 | Full remarketing platform compounds at historical rates for a decade | $29.30 | 16.07% |

- **Probability-weighted: IV@15% $13.77 (−47.8% vs price), IV@12% $18.69, IV@10% $24.23, weighted IRR 9.43%, base-case IRR 8.83%**
- **Tier by numbers: D.** Diagnostics (key_numbers.md): OE yield 4.62%, terminal value 21.1% of IV@15%, scenario spread 5.02x, 2.5 months since FY end.

## Flags — every fragility flag resolved
- **WIDE_SCENARIO_SPREAD** (5.02x, super-bull IV $29.30 vs super-bear $5.83): real — the range between "volumes keep shrinking" and "ACV platform compounds" is genuinely wide at this price. Confidence is capped at medium, and the verdict is sized to the conservative end: even the bull case (11.48% IRR) does not clear 15%; only the 10%-weighted super bull does.

## My thoughts / overlay
- This is a quality/price mismatch, not a quality problem: a debt-free duopoly with a 4.62% OE yield at $26.41 simply does not leave room for a 15% return unless the super-bull path materializes. Even on the engine's unadjusted preliminary run (default offsets, base start 9.37%), the weighted IRR was only ~9.5% — the verdict is not an artifact of my recalibration; the method range across both runs stays in Tier D.
- ACV Auctions deal (announced 2026-09-10, per deal coverage): $10.50/share cash, ~$1.9B equity value, funded from cash on hand; tender offer extended to Oct 15, 2026 while the antitrust waiting period runs; management guides EPS-neutral in the first full year and accretive from FY2028. It buys a dealer-to-dealer wholesale lane Copart does not have, at a full price for a GAAP-loss-making business — a growth bet, treated here as bull-case fuel, not base case.
- Management transition: CEO Jeff Liaw stepped down effective 2026-07-31 and founder Jay Adair resumed the CEO role (per CollisionWeek's Copart coverage) — continuity risk is low, but it coincides with the volume downturn.
- Margin of safety: none at $26.41 — the price sits 47.8% above the weighted IV@15%. The stock clears Andrew's 15% hurdle only at roughly the weighted IV@15% of **$13.77 or below** (and clears it with a margin of safety only well under that). At $26.41 a buyer is paying for the bull/super-bull path in advance.

## Final verdict
- **Final tier: D** (weighted IRR 9.43% on the v5 final inputs; tier by numbers also D, no override)
- Confidence: **Medium** (high on OE quality and the balance sheet; the scenario spread is 5.02x, so no higher)
- One-liner: Wide-moat (8/10) salvage-auction compounder, but at $26.41 the weighted IRR is 9.4% (IV@15% $13.77) — it only clears Andrew's 15% hurdle at roughly $13.77 or below.
