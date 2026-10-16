# OTIS — Otis Worldwide Corporation
v5 run, 2026-10-15. In scope (market cap $27.548B at $69.76, nasdaq_quote_api).

All figures below are copied from dcf_numbers.json, ttm.json / ttm.py output, or financials_history.csv — none are recomputed. Research figures are from the web searches cited in-line in the text.

## What it is
The world's largest elevator and escalator company, spun out of United Technologies in 2020. Two segments: New Equipment (cyclical, construction-driven, thinner margins) and Service (maintenance, repair and modernization on an installed base estimated at over 2.5 million units — recurring, high-margin, and the source of most segment profit). It competes in a consolidated oligopoly with KONE, Schindler, TK Elevator and Mitsubishi Electric, where scale and the density of the technician network decide who wins service contracts.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,596,000,000; capex $152,000,000 (tag PaymentsToAcquireProductiveAssets); SBC $80,000,000 (tag ShareBasedCompensation, always a real cost).
- **Conservative owner's earnings FY2025: $1,364,000,000 = $3.45/share** (base_oe_latest_per_share $3.4540389972144845 in dcf_numbers.json)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,574,000,000 in FY2025 — above the conservative figure, so the conservative base is not flattered by the maintenance definition.
- OE positive 5 of the last 5 fiscal years. Net debt $6,860,000,000 (dcf_numbers.json). Stockholders' equity was −$5,392,000,000 at FY2025 (financials_history.csv) — the leveraged spin-off capital structure: dividends and buybacks are funded on top of a large debt stack, not an equity cushion.
- Historical growth is genuinely slow on the filed record: revenue CAGR 5y 2.50%, revenue CAGR 3y 1.78%, latest FY revenue YoY 1.19%, OE/share CAGR 2y 0.25% (growth_components in dcf_numbers.json).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,596,000,000 − prior YTD $405,000,000 + current YTD $680,000,000 = **TTM $1,871,000,000**
- Capex: FY $152,000,000 − prior YTD $70,000,000 + current YTD $77,000,000 = **TTM $159,000,000**
- SBC: FY $80,000,000 − prior YTD $44,000,000 + current YTD $39,000,000 = **TTM $75,000,000**
- Shares (current-YTD weighted diluted): **386,400,000**
- **TTM OE total $1,637,000,000 → base OE/share $4.24** (ttm_oe_per_share $4.236542443064182; base_source: ttm_json)
- The engine's normalized base (3-yr median) is $3.44/share (base_oe_normalized_per_share $3.4370477568740956). The TTM base was used per the STALE_FY resolution below. Caution attached to it: the TTM step-up is a cash-flow step-up, not an earnings step-up — Q2 2026 adjusted EPS was $1.01, down 4% year over year (search result, earnings reports July 22, 2026), and management cut full-year 2026 adjusted EPS guidance to $4.01–$4.05 for the second consecutive quarter, with adjusted free cash flow guidance of $1.50–$1.55B (search results). The verdict below is therefore sized to the conservative end and the probabilities are skewed bear-ward.

## Moat: 7/10 — strong
Justification: the largest installed base in a regulated oligopoly converts into dense-network service economics and real switching friction, and service has held high margins through cycles; it stops short of wide because maintenance contracts are contestable at renewal by independents and rival OEMs, pricing power proved limited in 2026 (management tempered maintenance pricing to protect retention), and the New Equipment half of the business is a cyclical, China-exposed commodity contest.
- FOR: Largest global installed base (estimated at over 2.5 million units) feeding recurring maintenance, repair and modernization revenue
- FOR: Densest global technician/service network — response time is the deciding factor for building managers
- FOR: Safety regulation, codes and downtime risk create real switching friction on service contracts
- FOR: Consolidated oligopoly (KONE, Schindler, TK Elevator, Mitsubishi) with high entry barriers — regulatory approvals plus service infrastructure
- FOR: Aging installed base in North America/Europe drives a modernization cycle — Q2 2026 modernization orders up 24% and backlog up 26% at constant currency (search result)
- FOR: Proven through-cycle service profitability and pricing on the installed base
- AGAINST: Service contracts are contestable at renewal; independent providers undercut OEM pricing
- AGAINST: Pricing power has limits — Q2 2026 maintenance micro-pricing was tempered to preserve retention and adjusted operating margin fell 180 bps to 15.2% (search result)
- AGAINST: Skilled-technician labor shortage and wage/material inflation squeeze the service margin the moat is supposed to protect
- AGAINST: New Equipment is cyclical and China-exposed — Q2 2026 China new-equipment sales fell in the high teens and New Equipment operating profit fell 41% (search result)
- AGAINST: KONE's acquisition of TK Elevator (shareholder-approved mid-2026, expected to complete in 2027 per search result) creates a larger scaled service rival
- AGAINST: Leveraged spin-off balance sheet — net debt $6,860,000,000 and negative book equity limit the shock absorbers
- A 7 gives CAP = 11.1 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 11.1 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Growth sanity check and recalibration (written reason): the engine's blended growth is 1.49% and g_base is 3.75% after the +2.26pp buyback adjustment (share count −2.26%/yr). Recent prints: latest FY revenue YoY 1.19% and OE/share CAGR 2y 0.25% on the filed record, but Q2 2026 net sales rose 7.3% year over year with organic sales up 6% and Service organic sales up 9% (search results), while adjusted EPS fell 4% — sales are accelerating, earnings conversion is not. The default offsets were therefore compressed: the default super-bull start of 15.75% has no support in any recent print (the fastest real print is Service organic +9%), so offsets were set to −0.10 / −0.04 / 0.00 / +0.03 / +0.06, giving starts of −6.25% / −0.25% / 3.75% / 6.75% / 9.75%. The super-bull start of 9.75% is anchored on Service organic growth of 9% plus the buyback tailwind, conditional on margin recovery. Probabilities were skewed bear-ward to 15/25/30/20/10 (from the 10/25/30/25/10 default) for two consecutive 2026 guidance cuts, the China New Equipment slump, and the leverage below. OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $69.76. Base = TTM $4.24/share (above).

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -6.25% | 0.75 | China NE slump spreads; retention pricing and labor costs cut the OE level; leverage bites | $17.31 | 5.17% |
| Bear | 25% | -0.25% | 0.90 | Flat guided EPS extends; margin pressure persists; modernization backlog converts slowly | $27.48 | 7.27% |
| Base | 30% | 3.75% | 1.00 | Service grows mid-single digits, New Equipment flat, margins stabilize at the guided level | $36.86 | 9.17% |
| Bull | 20% | 6.75% | 1.10 | Modernization backlog converts; service margin recovers as management guided for H2; buybacks continue | $46.73 | 11.05% |
| Super bull | 10% | 9.75% | 1.25 | Service flywheel plus modernization super-cycle plus a New Equipment recovery and margin expansion | $61.22 | 13.60% |

- **Probability-weighted: IV@15% $35.99, IV@12% $47.62, IV@10% $60.58, weighted IRR 9.03%, base-case IRR 9.17%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 6.07%, terminal value 18.38% of IV@15%, scenario spread 3.54x, net debt 4.10x normalized OE, 9.46 months since FY end.
- Even the super-bull scenario does not clear the hurdle: its IV@15% of $61.22 is below the $69.76 price and its IRR is 13.60%.

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 9.46 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, with all four legs quoted in the Owner's earnings section above. The earnings-vs-cash caution on that TTM base is stated there and handled through bear-skewed probabilities.
- **BUYBACK_TAILWIND** (share count shrinking 2.3%/yr): already credited via the +2.26pp growth adjustment in g_base; not double-counted in the verdict. Note the buybacks run on a leveraged, negative-equity balance sheet, so the tailwind is debt-supported.
- **HIGH_NET_DEBT** (net debt 4.10x normalized OE in the final run): folded into the verdict explicitly — net debt is $6,860,000,000 against TTM OE of $1,637,000,000 (both as printed in dcf_numbers.json / ttm.json), book equity is negative, and the super-bear/bear cases carry 40% combined probability with OE multipliers of 0.75/0.90 precisely because levered OE can shrink fast. This is a reason the tier stays at the numbers, with no override.
- **WIDE_SCENARIO_SPREAD** (present in the preliminary run at 4.51x, 3.54x in the final run): the spread is real — outcomes hinge on whether service margin pressure is transitory. Confidence is held at medium and the verdict is sized to the conservative end; no tier override.

## My thoughts / overlay
- Method range: the preliminary median-base run gave a weighted IRR of 8.33% and weighted IV@15% of $31.80; the final TTM-base run gives 9.03% and $35.99. Both are Tier D — the verdict does not depend on which base is chosen, which strengthens it.
- Quality is not the debate: OE positive 5/5 years, a recurring service book on the largest installed base, modernization orders up 24% and backlog up 26% at constant currency in Q2 2026 (search result), and a 5% dividend raise with buybacks continuing (search result). The debate is purely price versus the growth the filed record actually shows (revenue CAGR 5y 2.50%, OE/share CAGR 2y 0.25%).
- Red flags, all priced into the scenarios rather than waved off: two consecutive 2026 adjusted EPS guidance cuts (now $4.01–$4.05, essentially flat), adjusted operating margin down 180 bps in Q2 2026, China New Equipment sales down in the high teens with segment profit down 41%, retention-driven pricing concessions, technician labor inflation, and the KONE–TK Elevator combination creating a bigger service rival.
- Hurdle-clearing price: the weighted IV@15% is $35.99 — that is the price at which the weighted case clears 15%, roughly half the current $69.76. There is no margin of safety at the current price in any scenario run, including super bull.

## Final verdict
- **Final tier: D** (weighted IRR 9.03% on the v5 final inputs; Tier D under both the median and TTM bases)
- Confidence: **Medium** (high on the filing-derived OE record and the service franchise; medium on the TTM base, whose step-up is cash-timing ahead of a flat EPS guide)
- One-liner: High-quality service compounder, moat 7/10 — does not clear 15% at $69.76 (weighted IRR 9.0%, weighted IV@15 $35.99, hurdle-clearing price $35.99); even the super-bull case (13.6% IRR, $61.22 IV@15) stays below the hurdle.
