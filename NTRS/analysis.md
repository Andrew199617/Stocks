# NTRS — Northern Trust Corporation
v5 run, 2026-10-14. In scope (market cap $31.017B at $161.34, nasdaq_quote_api).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed. Web figures are paraphrased from the filer's earnings releases and reporting on them, not quoted.

## What it is
Chicago-founded (1889) custody bank: asset servicing (custody, fund administration) for institutions, wealth management for affluent families/family offices, asset management, and banking. As of June 30, 2026 it reported assets under custody/administration of $20.0 trillion and assets under management of $2.0 trillion; wealth-management AUM was $534 billion. Revenue is mostly recurring: trust, investment and other servicing fees were $5,017.8M in FY2025 (+6% vs FY2024) and net interest income $2,411.0M (+11%), for total revenue of $8,086.4M in FY2025 per the filer's Q4 2025 release. (The engine's revenue series is the contract-revenue tag only and excludes net interest income, so its revenue CAGRs — 5y 4.67%, 3y 4.22% — describe the fee line, not the whole top line.)

## Owner's earnings
**Filed history (financials_history.csv, conservative OE = OCF − capex − SBC):**
- FY2023: OCF $2,625,600,000; net income $1,107,300,000; conservative OE $2,390,900,000; maintenance OE $1,625,400,000
- FY2024: OCF −$486,000,000; net income $2,031,100,000; conservative OE −$706,900,000; maintenance OE $2,646,400,000
- FY2025: OCF $5,533,500,000; capex $74,000,000; SBC $126,500,000; net income $1,736,900,000; conservative OE $5,333,000,000 ($27.74/share); maintenance OE $2,442,000,000

That is the whole story of this name in this model: a bank's reported operating cash flow is dominated by balance-sheet flows (derivative-counterparty collateral, deposit/securities positioning, other operating activities), not by earnings. Net income never collapsed or spiked the way OCF did — the maintenance definition (NI-based) is comparatively steady across the same three years, while the conservative definition swings from negative to $5.333B. OE positive 4 of the last 5 fiscal years on the conservative definition, with FY2024 the negative year.

**Base used = normalized median of the last 3 FY OE/share: $11.52/share** (base_source: median_of_last_3_fy_oe_per_share). It is the least distorted of the engine's candidates: the latest FY ($27.74) is an OCF-surge year, and the median sits near the earnings power implied by the steadier maintenance series and by recent quarterly net income prints (see STALE_FY).

**TTM base — run, quoted, and NOT used.** ttm.py (filing-direct) inputs, YTD through Q2 2026 (ytd_end 2026-06-30):
- OCF: FY $5,533,500,000 − prior YTD $4,619,300,000 + current YTD −$384,900,000 = **TTM $529,300,000**
- Capex: FY $74,000,000 − prior YTD $24,800,000 + current YTD $34,800,000 = **TTM $84,000,000**
- SBC: FY $126,500,000 − prior YTD $90,100,000 + current YTD $127,100,000 = **TTM $163,500,000**
- Shares (current-YTD weighted diluted): **185,709,785**
- **TTM OE total $281,800,000 → TTM OE/share $1.52**

The TTM pin is rejected for a documented reason (HBAN precedent in this sweep): for a custodian bank the OCF leg is a balance-sheet flow, and H1 2026's negative OCF print says nothing about earnings — quarterly net income over the same window was stable and growing (Q3 2025 $457.6M, Q4 2025 $466.0M, Q1 2026 $525.5M, Q2 2026 $792.2M per the filer's quarterly trend data, the Q2 figure flattered by a Visa Class B exchange gain; adjusted EPS $2.97 vs GAAP $4.23). Pinning a $1.52 base would manufacture a Tier F/D out of a collateral swing. The median base is used instead, and the staleness cost is carried in the scenario weights and low confidence.

## Moat: 6/10 — moderate, a real custody franchise in a compressing-fee oligopoly
Justification: asset servicing is a scale oligopoly with deep operational integration and high switching costs, a recurring trust-fee base growing organically, and a sticky UHNW/family-office wealth niche — capped at 6 because fees are basis-point-priced and compressing, BNY and State Street out-scale it, fee revenue rides market levels, and bank earnings are capital-constrained and rate/credit-cycle exposed.
- FOR: custody scale oligopoly — $20.0T assets under custody/administration at Q2 2026, one of three global custody majors; high switching costs — custody, fund administration and servicing are operationally embedded in institutional clients; recurring trust-fee base — $5,017.8M in FY2025, +6% YoY, with eight straight quarters of positive organic fee growth to Q2 2026; wealth franchise — $534B wealth AUM in UHNW/family-office niches; through-cycle profitability — return on average common equity 14.4% in FY2025, net income positive and substantial every filed year.
- AGAINST: fee compression — custody/servicing is basis-point-priced and the two larger rivals set the price; market-linked revenue — servicing fees and AUM ride market levels, so a drawdown cuts fees mechanically; rate sensitivity — NII depends on the curve and deposit repricing; capital-constrained bank model — growth and buybacks compete for regulatory capital, with credit-cycle exposure on the loan book; expense pressure — H1 2026 expenses rose, including Q2 2026 charges for software dispositions, severance and a one-time equity grant.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Probabilities were skewed from the defaults (10/25/30/25/10 → 10/30/30/20/10) to widen the bear weight, as the OE_VOLATILE flag instructs; offsets and multipliers are the defaults (−12/−5/0/+5/+12pp; 0.75/0.90/1.00/1.10/1.25). Price $161.34.

Sanity check against recent prints: the base growth start (8.1%) sits between FY2025 trust-fee growth (+6%) and the H1 2026 prints (trust fees +10% YoY and NII +11% YoY in Q2 2026; total revenue ex-notable items +13% YoY) — defensible. The engine's OE/share CAGR 2y component (55.14%) is an artifact of the OCF swing (negative FY2024 → surge FY2025) and was NOT treated as a growth signal; the blend (5.40%) is carried by the revenue components plus the buyback adjustment. The super-bull start (20.1%) is an OE/share rate, not a revenue rate — it requires the Q2 2026 pattern (adjusted EPS +40% YoY on trading strength and operating leverage, plus buybacks) to persist, which is why it gets only 10% weight and a written flag here rather than a higher one.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -3.9% | 0.75 | Market drawdown cuts AUC/AUM fees; NII compresses; credit costs rise | $53.36 | 6.33% |
| Bear | 30% | 3.1% | 0.90 | Fee compression + flat markets; earnings grow only with buybacks | $87.41 | 9.30% |
| Base | 30% | 8.1% | 1.00 | Mid-single-digit fee growth + NII stability, faded over the 9.8y CAP | $121.32 | 12.06% |
| Bull | 20% | 13.1% | 1.10 | H1 2026 momentum (fees +10%, NII +11%) largely holds | $166.61 | 15.36% |
| Super bull | 10% | 20.1% | 1.25 | Trading/fee surge + operating leverage + buybacks compound | $257.80 | 20.88% |

- **Probability-weighted: IV@15% $127.06 (−21.2% vs price), IV@12% $171.13 (+6.1%), IV@10% $220.59, weighted IRR 12.53%, base-case IRR 12.06%**
- **Tier by numbers: C.** Diagnostics (key_numbers.md): OE yield 7.14%, terminal value 20.2% of IV@15%, scenario spread 4.83x, 9.4 months since FY end, net debt not computed by the engine for this filer (— in key_numbers.md; an industrial net-debt lens is not meaningful for a deposit-funded bank).

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.4 months ago): ttm.py was run and its full inputs are quoted in the OE section; its TTM base ($1.52/share) was NOT used, for the documented reason that a custodian bank's OCF leg is a balance-sheet flow and H1 2026 net income prints contradict the TTM OE collapse. The median base is used; staleness is priced via the widened bear weight and low confidence.
- **BASE_DIVERGENCE** (latest FY $27.74 vs 3-yr median $11.52): the latest FY is the distorted one — FY2025 OCF of $5,533,500,000 against net income of $1,736,900,000 is a balance-sheet-flow surge, not earnings. The median is also not clean (the same 3-year window contains FY2024's −$706,900,000 conservative OE), but it is the least distorted engine candidate and is corroborated by the steady maintenance-OE totals and recent quarterly net income. Median used.
- **NI_OCF_DIVERGENCE** (2023, 2024, 2025): structural for a bank, with identifiable one-offs on top. The OCF side swings with derivative-counterparty collateral and other operating activities (the filer's own cash-flow statements carry multi-billion-dollar lines for these). The NI side was flattered in FY2024, when other operating income was $1,157.4M vs $207.7M in FY2025 per the filer's Q4 2025 release — the Visa Class B monetization pattern, which recurred in Q2 2026 as a Visa exchange gain inside the $792.2M net income quarter (adjusted EPS $2.97 vs GAAP $4.23). Neither side is a clean earnings series; that is exactly why the normalized median, not any single year, is the base.
- **OE_VOLATILE** (OE/share spans >3x over 5 years): real in the conservative series, but it is OCF-flow volatility, not earnings volatility — net income and maintenance OE are far steadier. Handled as instructed: bear probability widened to 30% (bull cut to 20%), and confidence held at low.
- **BUYBACK_TAILWIND** (share count −2.73%/yr): already credited via the +2.73pp growth adjustment in g_base (blend 5.40% → 8.13%); not double-counted in the verdict. Note the TTM share count (185,709,785) shows the buyback continuing into 2026.
- **SECTOR_MODEL_MISMATCH** (Finance): accepted in full. A bank's OCF-based owner's earnings are not its distributable cash — loan growth consumes regulatory capital, provisions are a through-cycle cost the OCF line only partially carries, and bank value is normally judged on ROE vs cost of equity and tangible book, neither of which this model computes. Confidence is low and the tier is soft. No tier_override is applied: the by-numbers tier is already a mid-range C (12.53%, not a borderline clear of the 15% hurdle), so there is no flattering result to soften — unlike HBAN, where a borderline B was softened to C.
- **WIDE_SCENARIO_SPREAD** (4.83x): real — the range runs from a fee drawdown in a market fall to a trading-led surge, and the model's own base uncertainty (median vs TTM vs latest FY spans $1.52–$27.74/share) is wider than the scenario table. Confidence is low (also mandated by the sector flag), and the verdict is sized to the conservative end.

## My thoughts / overlay
- The honest headline is the base problem, not the scenario table: three defensible-looking bases from the same filings span $1.52 (TTM) to $27.74 (latest FY) per share, with the $11.52 median in between. The median is chosen because the two extremes are both OCF-flow artifacts, and because the NI-based maintenance totals and the quarterly net income run-rate corroborate a base in that neighbourhood — but any single IRR quoted for NTRS without its base attached is hiding the ball.
- Quality is not the debate: a top-three global custodian with $20.0T under custody/administration, recurring fees, a 14.4% FY2025 return on average common equity, and a shrinking share count. The debate is price and model fit: at $161.34 the market is already paying for the bull-leaning path (bull IV@15% $166.61), while the weighted case is $127.06.
- Red flags / watch items: Q2 2026's headline beat leaned on a one-off Visa exchange gain and on restructuring-type charges (software dispositions, severance, one-time equity grant) going the other way — underlying expense discipline still has to be proven; fee compression from BNY/State Street is structural; a CFO transition was announced in late September 2026, a minor governance watch item, not a thesis item.
- Price that clears 15%: at or below the weighted IV@15% of $127.06 — roughly a fifth below the current price — and a buyer who wants the bear case ($87.41) covered needs a far lower entry. There is no margin of safety at $161.34 on these numbers.

## Final verdict
- **Final tier: C** (weighted IRR 12.53% on the v5 final inputs; tier by numbers C, no override)
- Confidence: **Low** (SECTOR_MODEL_MISMATCH plus WIDE_SCENARIO_SPREAD 4.83x; the base itself is a judgment call among OCF-distorted candidates)
- One-liner: Quality custody bank, moat 6/10 — normalized OE base is credible but the OCF-based model fits a bank poorly; weighted IRR 12.53% (IV@15% $127.06 vs $161.34) is Tier C at low confidence, and it clears 15% only at or below ~$127.
