# CPNG — Coupang, Inc.
v5 run, 2026-10-14. In scope (market cap $26.517B at $14.295, nasdaq_quote_api).

All figures below are copied from dcf_numbers.json, financials_history.csv, or ttm.py output — none are recomputed.

## What it is
South Korea's leading e-commerce company — the "Amazon of Korea." Core Product Commerce (first-party retail + marketplace) delivered through its owned Rocket Delivery / dawn-delivery logistics network and the Rocket Wow membership; around it sit Developing Offerings — Taiwan expansion, Coupang Eats, Coupang Play, fintech, and Farfetch (luxury, acquired Dec 2023). Q2 2026 (search-sourced): revenue $8.9B, +4% reported / +10% constant currency; Product Commerce $7.4B (+8% CC); Developing Offerings $1.4B (+24% CC); 24.7M active Product Commerce customers. The quarter carried a $410M administrative fine (data-breach related, in OG&A, under appeal), a $556M operating loss and a $570M net loss; management guided Developing Offerings to $950M–$1.0B of adjusted EBITDA losses for FY2026, mostly Taiwan, and expects Product Commerce margins to recover toward pre-incident levels by mid-2027.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $34,534,000,000 (+14.09% YoY, latest rev YoY in dcf_numbers.json); operating cash flow $1,773,000,000; capex $1,251,000,000; SBC $475,000,000 (always a real cost).
- **Conservative owner's earnings FY2025: $47,000,000 = $0.03/share** (base_oe_latest_per_share $0.0253) — down from $574,000,000 in FY2024 and $1,430,000,000 in FY2023 (totals from financials_history.csv). The collapse is arithmetic, not one line: OCF stagnated ($2,652M → $1,886M → $1,773M over FY23–25) while capex rose to $1,251M and SBC to $475M.
- Maintenance version FY2025: $1,657,000,000 — far above the conservative figure because it charges only min(capex, D&A) instead of total capex. The gap IS the investment question: a large share of capex is Taiwan/automation growth build-out rather than maintenance of the Korean core. The standardized conservative definition is the headline (per method); the maintenance figure is why the method range below is not zero.
- OE positive 3 of the last 5 fiscal years. Net debt −$5,670,000,000 (net cash; see BIG_NET_CASH flag).

**Base used = the engine's normalized base, median of last 3 FY OE/share = $0.3143/share** (base_source: median_of_last_3_fy_oe_per_share) — NOT the TTM pin, for the reason under STALE_FY / BASE_DIVERGENCE below.

**TTM check (ttm.py, filing-direct, no hand math) — run because of STALE_FY:**
- OCF: FY $1,773,000,000 − prior YTD $899,000,000 + current YTD $551,000,000 = **TTM $1,425,000,000**
- Capex: FY $1,251,000,000 − prior YTD $538,000,000 + current YTD $613,000,000 = **TTM $1,326,000,000**
- SBC: FY $475,000,000 − prior YTD $234,000,000 + current YTD $283,000,000 = **TTM $524,000,000**
- Shares (current-YTD weighted diluted): **1,812,000,000**
- **TTM OE total −$425,000,000 → TTM OE/share −$0.2345** — negative. It corroborates the direction (current run-rate OE is worse than the median base, not better) but is not usable as the projection base: H1 2026 OCF absorbs the $410M Q2 fine and data-incident voucher/reacquisition costs, which are one-off in nature (the fine is under appeal), and pinning a negative base would convert a one-off charge into a permanent Tier F. The median base is therefore the normalized base, and the verdict is sized knowing even it flatters the current run-rate.

## Moat: 6/10 — moderate-strong in Korea, unproven outside it
Justification: the owned dawn-delivery logistics network and Wow habit loop are real and were stress-tested by the data breach — customers stayed — but the business has not converted scale into durable margins, and the moat does not travel yet (Taiwan/Farfetch consume the core's cash).
- FOR: Owned end-to-end Rocket Delivery network (100+ fulfillment centers, dawn/next-day delivery) that rivals have not replicated in Korea; Rocket Wow membership habit and switching friction — active customers rose to 24.7M in Q2 2026 and spend per active customer grew after the breach disclosure; scale/data flywheel in the world's densest e-commerce market; net-cash balance sheet funds the build-out without dilution stress.
- AGAINST: Naver holds a large domestic share off search distribution; AliExpress/Temu attack on price with Alibaba-funded local logistics; structurally thin retail margins — no demonstrated pricing power (gross margin contracted in H1 2026); Korean regulatory hostility is now a recurring cost, not a tail risk (privacy fine, FTC actions, added tax assessment — all search-sourced from Q2 2026 reporting); Developing Offerings burn guided at $950M–$1.0B EBITDA losses in FY2026 dilutes the core's economics; founder super-voting control.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Growth sanity check: the engine's blended growth is 16.46% (rev CAGR 5y 23.61%, 3y 18.82%, latest YoY 14.09%, OE/share CAGR 2y −82.11%), share-count adjustment −1.67pp for dilution (share CAGR +1.67%/yr), g_base 14.79%. Against actual prints: revenue growth is decelerating — FY2025 +14.09%, Q2 2026 +10% CC (+4% reported), Q3 2026 guided +8–9% CC (search-sourced). The scenario starts below are OE/share growth off a depressed $0.31 base, not revenue growth: the base start (14.8%) requires margin/fine normalization, not revenue acceleration, and the bull/super-bull starts (19.8% / 26.8%) are recovery arithmetic off a base that fell from the FY2023 level — they are NOT extrapolations of current OE momentum, which is negative (TTM OE −$0.23/share). That is the written reason the bull starts can sit above current prints while the stock still fails: even the super-bull IV lands below the price. Probabilities were skewed bear-ward vs defaults (15/30/30/15/10 vs 10/25/30/25/10) per the OE_VOLATILE flag and the three-year OE downtrend; offsets and multipliers left at defaults (−12/−5/0/+5/+12pp; 0.75/0.90/1.00/1.10/1.25). Price $14.295.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | 2.8% | 0.75 | Fines/regulation recur, Taiwan burn persists, Naver/C-commerce take share | $1.96 | 4.22% |
| Bear | 30% | 9.8% | 0.90 | Margins recover slowly; Developing losses stay near guide | $3.21 | 5.55% |
| Base | 30% | 14.8% | 1.00 | Fines lapse, Product Commerce margins recover by mid-2027 per guidance | $4.45 | 6.85% |
| Bull | 15% | 19.8% | 1.10 | Taiwan scales toward breakeven, ads/fintech attach lifts OE | $6.10 | 8.49% |
| Super bull | 10% | 26.8% | 1.25 | Full platform payoff — Korea cash machine plus Taiwan second engine | $9.41 | 11.41% |

- **Probability-weighted: IV@15% $4.45 (−68.9% vs price), IV@12% $6.09, IV@10% $7.95, weighted IRR 6.89%, base-case IRR 6.85%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 2.20%, terminal value 21.9% of IV@15%, scenario spread 4.80x, net debt −9.72x normalized OE, 9.4 months since FY end.
- Every scenario — including super bull at 11.41% IRR — sits below the $14.295 price and below the 15% hurdle. The price that clears 15% on the weighted case is the weighted IV@15% itself: **$4.45**.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.4 months ago): ttm.py was run and its full inputs are quoted above. TTM OE is −$0.2345/share, so no --ttm pin was used: the TTM window contains the $410M Q2 2026 administrative fine and data-incident voucher/reacquisition costs (search-sourced from Q2 2026 reporting), and a negative pin would project a one-off fine as permanent. The median normalized base was used instead, with the TTM result disclosed here as evidence the current run-rate is worse than the base.
- **BASE_DIVERGENCE** (latest FY $0.03 vs 3-yr median $0.31): both are distorted in opposite directions. The latest FY is depressed by the capex step-up ($879M → $1,251M) and SBC rise on flat OCF; the median (the FY2024 year) pre-dates the data incident, the fines, and the full Taiwan loss ramp, so it flatters the present. The median was kept as the normalized base because the TTM alternative is negative for one-off reasons — but the verdict does not lean on the median being current; on any of the three bases (latest, median, TTM) the tier is D-or-worse.
- **OE_VOLATILE** (OE/share spans >3x over 5 years): real and trending, not noise — conservative OE totals fell $1,430M → $574M → $47M over FY23–25. Handled by widening bear weight (super bear 15%, bear 30%) and by confidence low.
- **NI_OCF_DIVERGENCE** (2023, 2024, 2025): identified. FY2023 net income ($1,360,000,000) was inflated by a −$776,000,000 tax line (benefit) against operating income of only $473,000,000, while OCF ran far above net income in all three years on non-cash SBC ($326M / $433M / $475M) plus D&A add-backs and working-capital inflows (delta NWC −$1,480M / −$442M / −$1,449M, financials_history.csv). In FY2024–25 the tax line flipped to expense ($407M / $383M), crushing reported net income ($154M / $208M) relative to OCF. The OCF-based conservative OE series used throughout is unaffected by the tax-benefit distortion.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.80x super-bear): real — outcomes hinge on Taiwan/Farfetch and regulatory costs. Confidence is low, and the verdict is sized to the conservative end; note even the super-bull end fails the hurdle at this price, so the spread does not rescue the verdict.
- **BIG_NET_CASH** (net cash 9.7x normalized OE): net debt is −$5,670,000,000 — a genuine cushion that funds Taiwan and the buyback (search-sourced: ~$459M repurchased in Q2 2026) and rules out balance-sheet distress. But it is already inside the price: at $14.295 the market is paying for the cash pile plus a recovery the OE line has not yet printed. It softens downside, it does not clear the hurdle.

## My thoughts / overlay
- The method range: on the conservative definition the answer is D on the median base (6.89%) and worse on latest/TTM bases. The only lens that argues higher is the maintenance-OE definition ($1,657,000,000 in FY2025), which treats most capex as growth — defensible for Taiwan, but the standardized screen charges total capex precisely because "growth capex" at Coupang has so far bought losses (Farfetch, Taiwan at a guided ~$1B EBITDA loss). Even crediting the bull case in full (11.41% super-bull IRR) does not reach 15%.
- Quality vs price: the Korean core is a real business with a real logistics moat and proven customer stickiness through a 33M-account breach. None of that is the debate. The debate is that owner's earnings after SBC and total capex have fallen for three straight years while the price still capitalizes a recovery.
- Red flags carried into the verdict: recurring regulatory fines/tax assessments in Korea; data-incident costs still flowing through H1 2026; Developing Offerings losses guided up, not down; dilution +1.67%/yr share CAGR despite buybacks; a July fulfillment-center fire loss noted in Q2 reporting (search-sourced).
- Margin of safety: there is none at $14.295 on this method — the weighted IV@15% ($4.45) is 68.9% below the price, and the price would need to fall to ~$4.45 to clear 15% on the weighted case.

## Final verdict
- **Final tier: D** (weighted IRR 6.89% on the v5 final inputs; no scenario clears 15%, super bull included)
- Confidence: **Low** (WIDE_SCENARIO_SPREAD, negative TTM OE, and a base that flatters the current run-rate — direction is clear, the exact depth is not)
- One-liner: Real Korean logistics moat (6/10) but owner's earnings have collapsed for three years — at $14.30 it clears nothing (weighted IRR 6.9%, IV@15% $4.45); it would need ~$4.45 to clear the 15% hurdle.
