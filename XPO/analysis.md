# XPO — XPO, Inc.
v5 run, 2026-10-15. In scope (market cap $22.471B at $188.83, nasdaq_quote_api).

All figures below are copied from dcf_numbers.json, ttm.py output, financials_history.csv, or cited search results — none are recomputed.

## What it is
Asset-based freight transportation: North American less-than-truckload (LTL) is the core — one of the largest LTL networks in North America, ~9% share of the U.S. market (estimated $52B in 2025, per the Q1 2026 10-Q via search), ~300 service centers covering 99% of U.S. ZIP codes, ranked No. 4 among LTL carriers — plus a lower-margin European Transportation segment (Q2 2026: $927M revenue, a $6M operating loss on restructuring, per the Q2 2026 release via search). The equity story is LTL margin convergence: adjusted operating ratio improved 300 bps YoY to a company-record 79.9% in Q2 2026, with a management target of a low-70s OR over time and an 11–13% LTL adjusted EBITDA CAGR target for 2021–2027.

## Owner's earnings
**Filed history (financials_history.csv, continuing-operations basis from 2022):**
- FY2023: revenue $7,744M; OCF $694M; capex $1,533M; SBC $78M → **conservative OE −$917M**; maintenance OE $261M
- FY2024: revenue $8,072M; OCF $808M; capex $789M; SBC $87M → **conservative OE −$68M**; maintenance OE $139M
- FY2025: revenue $8,157M; OCF $986M; capex $657M; SBC $77M → **conservative OE $252M = $2.12/share**; maintenance OE $390M
- OE positive 3 of the last 5 fiscal years. Net debt $2,943M (dcf_numbers.json).

The 3-yr median (normalized) base is **−$0.57/share** — the preliminary engine run printed Tier F on it. That median is distorted, not representative: FY2023 capex of $1,533M is roughly 4x FY2023 D&A of $376M and includes the $870M purchase of 28 Yellow Corp terminals out of bankruptcy (Dec 2023, per search) plus fleet/network investment; FY2024 capex of $789M was still ~1.8x D&A of $432M. The maintenance definition (which caps capex at D&A) is positive in all three years, confirming the negative conservative figures are a growth-capex bulge, not a business that loses cash at maintenance spend. But the bulge is not free either — terminals and tractors are the product in LTL — so neither the median (F) nor a maintenance-only view is the right base.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $986,000,000 − prior YTD $389,000,000 + current YTD $491,000,000 = **TTM $1,088,000,000**
- Capex: FY $657,000,000 − prior YTD $395,000,000 + current YTD $238,000,000 = **TTM $500,000,000**
- SBC: FY $77,000,000 − prior YTD $31,000,000 + current YTD $30,000,000 = **TTM $76,000,000**
- Shares (current-YTD weighted diluted): **119,000,000**
- **TTM OE total $512,000,000 → base OE/share $4.30** (base_source: ttm_json)
- TTM capex of $500M sits inside management's FY2026 gross capex guidance of $500–600M (Q2 2026 materials via search) and close to FY2025 D&A of $467M — i.e. the TTM base is struck at roughly maintenance-plus-modest-growth capex, not at the Yellow-bulge level and not at zero.

## MOAT: 6/10 — moderate-strong, real network, not wide
Justification: LTL density and scarce terminal real estate are genuine advantages and the post-Yellow industry is consolidated and pricing-disciplined, but XPO still trails Old Dominion on efficiency, freight is cyclical, and the network consumes structural capex every year.
- FOR: Scale and density — ~9% U.S. LTL share, ~300 service centers, 99% ZIP coverage, day-definite network that smaller carriers cannot replicate
- FOR: Scarce terminal footprint — 28 Yellow terminals bought for $870M in a bankruptcy auction; large metro terminal sites are expensive and hard to secure, and dock-door capacity is up 15% since 2021
- FOR: Consolidated, pricing-disciplined industry after Yellow's exit; yield ex-fuel +4.4% YoY in Q2 2026 on top of share gains
- FOR: Proprietary technology and insourcing — outsourced linehaul miles cut from 25.2% (2020) to 6.1% (Q2 2026), AI load/route tools, damage claims ratio at a record <0.2%, supporting premium service pricing
- AGAINST: Still the efficiency laggard vs the benchmark — XPO's record 79.9% adjusted OR vs Old Dominion's mid-70s; the convergence path is execution, not entitlement
- AGAINST: Cyclical industrial freight — Q2 2026 tonnage per day only +1% YoY (April −1.5%, May +0.5%); volume recovery is not yet proven
- AGAINST: Structural capex intensity — fleet and terminals must be fed every year (FY2026 guided gross capex $500–600M); OE is what is left after that, and it was negative as recently as FY2024 on the conservative definition
- AGAINST: Leverage and the European drag — net debt $2,943M is 5.7x TTM OE; European Transportation posted a Q2 2026 operating loss and dilutes the pure-LTL story
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Growth recalibration (written reason): the engine's blended growth is 1.86% (rev CAGR 3y 1.86%, latest FY rev YoY +1.05%, 5y CAGR 5.75%) and g_base is 1.01% after the −0.85pp share-count adjustment — those are trough-freight revenue prints. They understate OE growth, which is being driven by operating-ratio convergence, not revenue: Q2 2026 total revenue +13.2% YoY, LTL revenue +15.2% YoY, adjusted EPS +56% YoY (per the Q2 2026 release via search), and TTM OE/share of $4.30 vs $2.12 in FY2025. Scenario starts were therefore set via offsets (−0.07 / 0.00 / +0.08 / +0.14 / +0.20 vs g_base) to −6.0 / +1.0 / **+9.0** / +15.0 / +21.0% — the base start sits just under management's 11–13% LTL EBITDA CAGR target band, discounted for the unproven volume recovery; even the super-bull start (21.0%) is below the current adjusted-EPS print, with the written reason that the Q2 print annualizes a record-OR quarter off a soft base. Probabilities at defaults 10/25/30/25/10; OE multipliers at defaults 0.75/0.90/1.00/1.10/1.25. Price $188.83.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -6.0% | 0.75 | Freight recession; OR gains stall, capex stays heavy against 5.7x leverage | $18.14 | 3.53% |
| Bear | 25% | 1.0% | 0.90 | Soft tonnage persists; yield only matches cost inflation | $29.71 | 4.42% |
| Base | 30% | 9.0% | 1.00 | OR convergence continues at guided capex; modest volume recovery | $47.13 | 5.85% |
| Bull | 25% | 15.0% | 1.10 | Industrial recovery lands; share gains compound off the expanded terminal base | $67.63 | 7.46% |
| Super bull | 10% | 21.0% | 1.25 | Full convergence toward best-in-class OR with a volume upcycle | $100.09 | 9.79% |

- **Probability-weighted: IV@15% $50.30 (−73.4% vs price), IV@12% $67.99, IV@10% $87.89, weighted IRR 6.15%, base-case IRR 5.85%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 2.28%, terminal value 20.6% of IV@15%, scenario spread 5.52x, net debt 5.7x normalized (TTM) OE, 9.5 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above with all four legs.
- **NI_OCF_DIVERGENCE** (2023, 2025): mostly non-cash D&A, not a one-off that contaminates the base. FY2023 net income $189M vs OCF $694M with D&A of $376M (financials_history.csv); FY2025 net income $316M vs OCF $986M with D&A of $467M. D&A explains the bulk of both gaps; the residual is ordinary working-capital/other items. The conservative OE series is built from OCF directly, so the NI gap does not flow into the base either way. The real 2023 distortion sits one line down — in capex (the Yellow terminal purchase), addressed in the base choice above.
- **WIDE_SCENARIO_SPREAD** (5.52x): real — the range between a freight recession on a levered, capex-hungry network and full OR convergence is genuinely wide. Confidence is capped at medium, and the verdict does not need the spread resolved: even the super-bull IV@15% ($100.09) is roughly half the price.
- **HIGH_NET_DEBT** (net debt 5.7x normalized OE): folded into the verdict explicitly. Net debt $2,943M against TTM OE of $512M means the equity's OE stream is a levered residual — in the bear cases (OE mult 0.75–0.90) there is little left after fleet/terminal capex, which is why the bear IVs sit at $18–30. It does not change the tier (the unlevered operating picture already fails the hurdle at this price), but it removes any "cheap on assets" fallback argument.

## My thoughts / overlay
- The method range is F→D and it is not close either way: the 3-yr median base is negative (Tier F by the preliminary run), the latest-FY base is $2.12/share, and the most generous defensible base — TTM at normalized capex — gives Tier D at 6.15% weighted IRR. No defensible base gets this price within sight of the 15% hurdle.
- The market is not pricing owner's earnings; it is pricing the OR-convergence story on EBITDA/EPS. That story is executing (record 79.9% OR, +56% adjusted EPS in Q2 2026), but at $188.83 the buyer pays for convergence and a volume upcycle in advance: even granting both in the super-bull case, the OE IRR is 9.79%.
- Quality is real but the OE conversion is the constraint: this is a business that must spend ~$500M+ a year on tractors, trailers and terminals to stand still competitively. SBC is modest ($76M TTM) and is charged in full; share count is roughly flat (+0.85%/yr trend, a small dilution headwind already in g_base).
- Price that clears 15%: the weighted IV@15% is $50.30 — that is the hurdle-clearing price on the final inputs, roughly a quarter of the current quote. There is no margin-of-safety framing that bridges a gap this size; the honest statement is that the stock would need to fall to near $50 before this screen would call it a 15% proposition.

## Final verdict
- **Final tier: D** (weighted IRR 6.15% on the v5 final inputs; method range F on the median base to D on the TTM base)
- Confidence: **Medium** (filing-derived TTM base and a verdict that survives every scenario, capped by the 5.52x scenario spread and the capex-normalization judgment inside the TTM base)
- One-liner: Strong LTL network, moat 6/10, margins inflecting — but at $188.83 the OE yield is 2.28% and even the super-bull case returns only 9.8%; it clears 15% only near $50.30, so Tier D.
