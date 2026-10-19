# GDDY — GoDaddy Inc.
Engine 5.4 pass-1 run, 2026-10-17. Price $105.96 (nasdaq_quote_api), market cap $14.90B — in scope under $40B.

All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv or fundamentals.json — none are recomputed.

## What it is
The largest domain registrar and small-business web-presence platform: Core Platform (domains, hosting, presence) plus Applications & Commerce (websites, commerce, email, and the Airo AI builder). Subscription, paid-upfront model serving small businesses and creators. Q2 2026: revenue $1,298M (+7% YoY), Applications & Commerce $515M (+11%), Core Platform $783M (+4%), normalized EBITDA margin 33.4%, free cash flow $443M in the quarter. FY2026 guidance narrowed to $5,215–$5,255M revenue (~+6% at midpoint) with ~$1.8B free cash flow reaffirmed; Q3 2026 guided to $1,315–$1,335M (~+5%).

## Owner's earnings
**FY2025 (10-K, financials_history.csv):** operating cash flow $1,599,400,000; SBC $317,800,000 (always a real cost); capex $23,900,000.
- **Conservative owner's earnings FY2025: $1,257,700,000 = $8.94/share** (base_oe_latest_per_share in dcf_numbers.json)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,367,600,000 — same ballpark, which raises confidence in the OCF-based figure.
- OE positive 5 of the last 5 fiscal years. Net debt $2,699,400,000 (debt $3,780,300,000 less the combined cash tag $1,080,900,000; see CASH_INCLUDES_RESTRICTED below), lease liabilities $82,300,000. Net debt is 1.82x the normalized OE base in the final run's diagnostics (2.90x on the preliminary median-base run).
- Buyback engine: the company states >95% of free cash flow over the last 4 years went to repurchases; diluted shares fell from the FY2025 weighted 140,621,000 to 132,766,000 on the current-YTD basis in ttm.json, and the Q2 2026 presentation shows fully diluted shares 127M vs 142M a year earlier (−11%).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,599,400,000 − prior YTD $784,600,000 + current YTD $914,000,000 = **TTM $1,728,800,000**
- SBC: FY $317,800,000 − prior YTD $161,400,000 + current YTD $145,500,000 = **TTM $301,900,000**
- Capex: FY $23,900,000 − prior YTD $7,700,000 + current YTD $9,700,000 = **TTM $25,900,000**
- Shares (current-YTD weighted diluted): **132,766,000**
- **TTM OE total $1,401,000,000 → base OE/share $10.55** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $6.62/share — rejected as the base: the OE/share series is a rising trend, not noise around a level — FY2023 $4.68, FY2024 $6.62, FY2025 $8.94, TTM $10.55 — driven by operating margin expanding from 12.9% (2023) to 22.8% (FY2025) in fundamentals.json plus the shrinking share count. The median is the lagging middle year of that trend. The preliminary median-base run printed weighted IRR 12.59% / IV@15% $83.69 (Tier C); that is the conservative end of the method range, not the headline.

## Moat: 6/10 — moderate-strong, not wide
Justification: scale, brand and a paid-upfront renewal base plus Applications & Commerce attach give real durability, and returns now support it — but the core product is price-transparent and transferable, so this is not a 7+.
- Evidence first (fundamentals.json): roic_proxy rose 9.2% (2020), 13.5% (2021), 18.1% (2022), 12.6% (2023), 20.8% (2024), 33.2% (FY2025); operating margin expanded 8.2% (2020) → 22.8% (FY2025) → 24.8% TTM. Gross margin is not quoted: fundamentals.json carries no COGS / gross-profit series for the recent fiscal years (null there), so operating margin and ROIC are the margin evidence in the computed outputs.
- FOR: largest registrar by scale (~10.8% share of registrations vs ~3.5% for the next rival, Namecheap, in 2026 registrar comparisons) with the widest TLD selection; durable subscription renewal base — primary domains revenue ~$1.8B annualised growing ~5–6% CAGR, paid upfront; attach economics into Applications & Commerce (+11% in Q2 2026; Airo AI builder bookings run-rate rose 5x to $50M in one quarter); ROIC now well above cost of capital and still expanding; buybacks (>95% of FCF for 4 years) shrink the count ~3.1%/yr on the engine's share CAGR and faster recently.
- AGAINST: core domains are a near-commodity — Namecheap, Cloudflare (at-cost), Porkbun and Dynadot undercut GoDaddy's ~$20–22 .com renewals; technical switching costs are low (a transfer is a standardised ICANN process — retention is inertia and bundling, not lock-in); Core Platform growth is only low-single-digit (Q2 2026 +4%) and the .CO registry contract expiration is a >200bp cumulative revenue headwind in the FY26 guide; renewal-price / upsell reputation invites churn and scrutiny; bookings decelerated to +5% in Q4 2025 on a $4.99 promotional offer that contradicted the stated high-intent strategy — now the subject of a securities class action (Johnson v. GoDaddy Inc., 26-cv-7144, SDNY, lead-plaintiff deadline Oct 26, 2026), and a reported Gen Digital takeover approach adds event uncertainty.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — final run (2026-10-17)
Growth sanity check (mandatory): the engine blend is 11.36% (rev CAGR 5y 8.34%, 3y 6.56%, latest YoY 8.26%, OE/share CAGR 2y 38.16% — the last is a margin-expansion / buyback artifact, not a revenue signal; revenue components carry the +3.06pp share-count adjustment). Against actual prints: revenue grew +8.26% in FY2025, +7% in Q2 2026, and FY2026 is guided to ~+6% — so an 11.36% OE/share start sits ABOVE the revenue prints and is only defensible per-share: TTM OE total grew +22.9% YoY and FY2025 OE/share grew from $6.62 to $8.94 on margin expansion plus an 11% YoY drop in diluted shares. The scenario starts are therefore read as OE/share growth, not revenue growth: base 11.36% is below the latest OE/share prints, bear 6.36% matches the guided revenue rate with no further margin / buyback help, super-bull 23.36% matches the TTM OE growth print (+22.9%) rather than exceeding it. Probabilities were shifted toward the bear side (12/28/30/20/10 vs the 10/25/30/25/10 default) per the OE_VOLATILE flag; offsets and OE multipliers are the defaults (−12/−5/0/+5/+12pp; 0.75/0.90/1.00/1.10/1.25). Price $105.96.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 12% | −0.6% | 0.75 | Promo-driven low-value mix sticks, bookings stay at +5% or worse, litigation / deal distraction, margin expansion reverses | $56.44 | 9.01% |
| Bear | 28% | 6.4% | 0.90 | Guided revenue growth only; no further margin or buyback tailwind per share | $92.49 | 13.48% |
| Base | 30% | 11.4% | 1.00 | Revenue ~6–7% plus continued buyback shrink and slower margin gains fade over the CAP | $128.34 | 17.36% |
| Bull | 20% | 16.4% | 1.10 | A&C / Airo attach accelerates; buybacks stay at the recent pace | $176.13 | 21.77% |
| Super bull | 10% | 23.4% | 1.25 | TTM OE growth rate (+22.9%) persists; Airo becomes a second engine | $272.14 | 28.83% |

- **Probability-weighted: IV@15% $133.61 (+26.1% vs price), IV@12% $181.59, IV@10% $235.63, weighted IRR 17.84%, base-case IRR 17.36%**
- **Tier by numbers: B.** Bear-case tier C (13.48%), bull-case tier A (21.77%) — see TIER_BAND. Diagnostics (dcf_numbers.json): OE yield 9.96%, terminal value 21.1% of IV@15%, scenario spread 4.82x, net debt 1.82x normalized OE, 9.5 months since FY end.
- Hurdle prices: clears 15% at $133.61 (the weighted IV@15%), 20% at $91.21, 25% at $68.38 — at the $105.96 price it clears 15% but not 20%.

## Flags — every fragility flag resolved
- **STALE_FY** (latest FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above.
- **BASE_DIVERGENCE** (latest FY $8.94 vs 3-yr median $6.62): the median is the distorted one — it is the middle year of a rising series (FY23 $4.68 → FY24 $6.62 → FY25 $8.94 → TTM $10.55) lifted by documented margin expansion and buybacks, not a one-year spike. TTM base used; the median-base run (12.59% weighted IRR, Tier C) is retained above as the conservative end of the method range.
- **NI_OCF_DIVERGENCE** (2025 NI $875,000,000 vs OCF $1,599,400,000, >40%): explained by non-cash add-backs and the paid-upfront model, not a one-off distortion of OE — SBC $317,800,000 plus D&A $116,600,000 account for $434,400,000 of the $724,400,000 gap, and the maintenance OE definition in financials_history.csv ($1,367,600,000, which starts from net income) lands in the same ballpark as the conservative OCF-based $1,257,700,000 after its working-capital term (ΔNWC −$399,900,000, i.e. deferred-revenue / upfront collections ahead of recognition). The OCF-based series is used throughout, so the divergence does not contaminate the base.
- **OE_VOLATILE** (OE/share range >3x over 5 years): the span is a rising trend (margin expansion + buybacks), not cyclicality — OE total rose every year in the filed history from $488,800,000 (2019) to $1,257,700,000 (2025). Handled anyway as the flag directs: bear-side probability weight raised to 40% combined (super bear 12% + bear 28%).
- **BUYBACK_TAILWIND** (share count shrinking 3.1%/yr): already credited via the +3.06pp growth adjustment in the blend; not double-counted in the verdict. Note the recent pace is faster (−11% YoY diluted in Q2 2026) — treated as upside in the bull cases, not extrapolated in the base.
- **SHARES_FALLBACK** (no diluted count filed for 2017, 2018): those history years use the basic / outstanding count recorded in financials_history.csv; per-share history there is approximate. It does not touch the base (TTM shares are filed diluted, 132,766,000) or the recent OE/share series (diluted counts filed 2023–2025).
- **CASH_INCLUDES_RESTRICTED** (the only cash tag for FY2025 is the combined cash + restricted-cash total, $1,080,900,000, with no restricted tag separating it): net debt $2,699,400,000 is therefore understated by whatever restricted amount is inside that total. Balance-sheet check: total debt $3,780,300,000 against that combined cash — even if the entire restricted portion were excluded, leverage stays moderate (1.82x normalized OE on the reported figure, and Q2 2026 reporting put trailing net leverage at 1.4x EBITDA with $1.2B cash vs $3.8B debt). The verdict does not rest on net debt being zero; it rests on it being ~2x OE, which survives this flag.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.82x super-bear IV): real — the range is driven by whether margin expansion and the buyback pace persist. Confidence is capped at medium and the verdict is sized to the bear end.
- **TIER_BAND** (bear C 13.48% vs bull A 21.77%): the verdict spans tiers; the position, if any, should be sized to the bear (C) end, per the spec.

## My thoughts / overlay
- Method range is the honest headline: median base + default weights = Tier C (12.59% weighted IRR, IV@15% $83.69); TTM base + bear-shifted weights = Tier B (17.84%, $133.61); TTM base + default weights = Tier B at 18.32%. Every TTM-based run clears 15%; no run clears 20% on weighted numbers. The disagreement is entirely about whether the FY23–25 margin / buyback ramp is the new level (TTM says yes, and Q1–Q2 2026 prints corroborate it) or a peak the median smooths away.
- Quality is high and improving: capex is $25.9M TTM against $1,728.8M OCF (asset-light), SBC is falling in absolute TTM terms ($301.9M vs $317.8M FY) even as OCF grows, and free cash flow TTM in fundamentals.json is $1,702,900,000.
- Risks: the core domains engine grows at low single digits and just lost the .CO registry contract; growth must come from A&C / Airo attach, which is promising ($50M run-rate) but small against a $5.1B revenue base. The $4.99 promo episode and the resulting class action are a governance / disclosure mark, and the reported Gen Digital approach makes the near-term price partly an event price rather than a fundamentals price.
- Margin of safety: the weighted IV@15% sits 26.1% above the price, but the bear IV@15% ($92.49) and super-bear IV@15% ($56.44) both sit below $105.96 — a buyer here is paid for the base case, not insured against the bear case. The 20% hurdle price is $91.21.

## Final verdict
- **Final tier: B** (weighted IRR 17.84% on the TTM base; method range C to B across the defensible bases, bear-to-bull scenario band C to A)
- Confidence: **Medium** (high on the TTM base and OE quality; the scenario spread is 4.82x and the tier band spans C to A, so never high)
- One-liner: Durable registrar cash machine, moat 6/10 — clears 15% on the TTM base (17.8% weighted IRR, IV@15% $133.61 vs $105.96 price) but the bear-to-bull band spans C to A, so size it to the bear end; it would need to fall to ~$91.21 to clear 20%.
