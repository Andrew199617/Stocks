# ROP — Roper Technologies, Inc.
v5 re-run, 2026-10-14 (supersedes the v4 analysis of 2026-10-13). All figures below are copied from dcf_numbers.json, ttm.py output (ttm.json), financials_history.csv, or key_numbers.md — none are recomputed.

**Scope note:** the engine's market-cap estimate is $40,473,746,440 at the final-run price of $374.06, computed on the stale FY2025 diluted count of 108,200,000 shares — mechanically just over the sweep's $40B line, so judgment.json records in_scope_under_40b = false per the engine rule. In substance the count has shrunk since FY-end: H1 2026 buybacks retired 9.0 million shares for $3.2 billion over three quarters (Q2 2026 release), and the TTM diluted count in ttm.json is 102,600,000.

## What it is
A diversified vertical-market software and technology compounder — the "Berkshire for software" model. ~29 niche, category-leading businesses run decentrally across Application Software (Deltek government-contractor accounting, Vertafore insurance agency systems, Aderant legal, CentralReach autism-therapy SaaS), Network Software (DAT freight load board and related), and Technology Enabled Products (Neptune smart water meters, Verathon medical devices). The flywheel: high-margin recurring cash flow funds acquisitions of mission-critical niche leaders (Procare in 2024; CentralReach and Subsplash in 2025), whose margins are then lifted under Roper's operating model. Organic growth is mid-single digits; the rest is bought. Q2 2026 (release, Jul 23 2026): revenue +9% with organic +5% and acquisition contribution +3%; full-year 2026 guidance raised to total revenue growth 8%+, organic ~6%, adjusted DEPS $22.15–$22.30.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $7,902,500,000 (+12.26% YoY per dcf_numbers.json); operating cash flow $2,540,300,000; capex $47,400,000 (tag: PaymentsToAcquireOtherProductiveAssets); SBC $166,300,000 (always a real cost).
- **Conservative owner's earnings FY2025: $2,326,600,000 = $21.50/share** (base_oe_latest_per_share $21.5028 in dcf_numbers.json).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC, from financials_history.csv): $2,342,200,000 — within 1% of the conservative figure, which raises confidence in the level.
- OE positive 5 of the last 5 fiscal years. Normalized base (median of last 3 FY OE/share): **$20.20/share** ($20.1972).
- Net debt (latest, engine basis, Dec 31 2025): $9,003,600,000 — see HIGH_NET_DEBT below.
- **What changed vs the v4 run:** v4 read capex as $0 (tag basis at the time) and built its TTM base on a single-quarter share count, giving $24.63/share. v5's expanded capex tags find real capex in every period, and ttm.py standardizes the share count — the v5 TTM base below is the cleaner figure.

**Base used — TTM through Q2 2026, from ttm.py (filing-direct, no hand math; full inputs in ttm.json):**
- OCF: FY $2,540,300,000 − prior YTD (H1 2025) $932,800,000 + current YTD (H1 2026) $1,061,600,000 = **TTM $2,669,100,000**
- Capex: FY $47,400,000 − prior YTD $26,000,000 + current YTD $25,300,000 = **TTM $46,700,000**
- SBC: FY $166,300,000 − prior YTD $82,700,000 + current YTD $108,200,000 = **TTM $191,800,000**
- Shares (current-YTD weighted diluted, per ttm.py basis): **102,600,000**
- **TTM OE total $2,430,600,000 → base OE/share $23.69** (base_source: ttm_json)
- The TTM OE flow is clean of the period's big non-cash item: H1 2026 GAAP results include a ~$1,002.5M equity gain on the Indicor stake (per the Q2 2026 10-Q reporting), but that gain never enters operating cash flow, so the OCF-based OE is unaffected by it.

## Moat: 7/10 — strong, portfolio-built
Justification: a portfolio of ~29 niche category leaders selling mission-critical systems of record with very high retention, proprietary vertical data, and a proven decentralized M&A model that lifts acquired margins — capped at 7 because the moats are narrow and per-business, organic growth is only ~5–6% so compounding depends on perpetual fairly-priced acquisitions, AI-native tools could erode switching costs, and leverage is structural.
- FOR: Mission-critical systems of record across niche vertical leaders (Deltek, Vertafore, Aderant, CentralReach) — switching means re-platforming core workflows and retraining staff, retention is very high, and annual price increases stick.
- FOR: DAT freight marketplace — a genuine two-sided network effect inside the portfolio.
- FOR: Proprietary vertical data assets (DAT load-board data, Neptune's installed metering base) that compound with scale and feed vertical-specific AI features.
- FOR: A capital-allocation moat on top of the product moats: three decades of disciplined M&A, a decentralized model that has repeatedly lifted acquired units' margins, and mid-teens FCF/share compounding as the explicit long-term target.
- FOR: Diversification — no single vertical, customer, or product drives the result.
- AGAINST: The moats are narrow and per-business, not one wide portfolio moat; each niche is small enough for a focused entrant, a horizontal platform, or an AI-native startup to attack one unit at a time.
- AGAINST: Growth is bought, not just built: organic growth is only ~5–6%, so the story requires a perpetual supply of fairly priced targets; deal multiples have risen and goodwill/intangibles dominate the balance sheet.
- AGAINST: AI cuts both ways — AI-native tools could lower switching costs or let customers insource workflows Roper's software currently owns.
- AGAINST: Technology Enabled Products is real hardware (meters, medical devices) with cyclical, capex-bearing economics unlike the software core.
- AGAINST: Leverage is part of the model, not an accident — it narrows the room for a deal mistake.
- A 7 gives CAP = 11.1 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 11.1 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Growth recalibration (written reason, per the standing rule): the engine's blended growth is g_base 12.56% (blend components: revenue CAGR 5y 14.46%, 3y 13.73%, latest YoY +12.26%, OE/share CAGR 2y 11.91%, share-count adjustment −0.43pp). Those revenue signals are acquisition-inflated — they include CentralReach/Procare/Subsplash contributions. What the company actually prints organically is +5% in Q2 2026 with FY2026 guidance of ~6% organic and 8%+ total revenue growth. The preliminary run's default super-bull start of 24.56% sits above every per-share print the company has produced — rejected. The exceptional buyback pace (9.0M shares, ~8% of the count, in three quarters) is also not a repeatable annual rate: management said on the Q2 call that near-term capital deployment will favor de-leveraging over opportunistic buybacks. Scenario starts were therefore set directly via offsets (−0.1256 / −0.0756 / −0.0256 / +0.0144 / +0.0544 vs g_base): super bear 0.0%, bear 5.0%, **base 10.0%** (≈ guided total growth plus normal, not heroic, buybacks, and below the 11.91% OE/share CAGR print), bull 14.0%, super bull 18.0% (requires an acquisition vintage as good as 2023–25 plus sustained buybacks). Probabilities kept at defaults 10/25/30/25/10 — the leverage argues against trimming the bear weights. Multipliers at defaults 0.75/0.90/1.00/1.10/1.25. Price $374.06.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 0.0% | 0.75 | A vertical sours + a bad deal vintage; leverage bites, growth stalls | $129.54 | 6.69% |
| Bear | 25% | 5.0% | 0.90 | Organic-only growth, M&A pauses, Indicor proceeds go to debt | $196.76 | 9.21% |
| Base | 30% | 10.0% | 1.00 | Guided path: ~6% organic + tuck-ins + normal buybacks | $277.12 | 12.01% |
| Bull | 25% | 14.0% | 1.10 | CentralReach-calibre deals keep landing; buybacks continue | $368.68 | 14.84% |
| Super bull | 10% | 18.0% | 1.25 | Acquisition pace re-accelerates at good prices, organic lifts | $506.70 | 18.54% |

- **Probability-weighted: IV@15% $288.12 (−22.98% vs price), IV@12% $391.22, IV@10% $507.46, weighted IRR 12.39%, base-case IRR 12.01%**
- **Tier by numbers: C.** Diagnostics (dcf_numbers.json): OE yield 6.33%, terminal value 21.10% of IV@15%, scenario spread 3.91x, net debt 3.51x normalized OE, 9.4 months since FY end.
- No scenario reaches the 20% tier; even super bull (18.54%) stays below it, and only super bull clears 15%.

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 9.4 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, with its inputs quoted in full above. The TTM base ($23.69) is higher than both the latest-FY ($21.50) and the 3-yr median ($20.20), because H1 2026 OCF grew and the share count fell; using it is the generous, current choice, and the stock still lands in Tier C.
- **OE_VOLATILE** (OE/share range over the last 5 years spans >3x): resolved — the volatility is a divestiture artifact, not operating cyclicality. The trough is 2022 in financials_history.csv: operating cash flow collapsed to $734,600,000 and conservative OE to $576,000,000 in the year Roper closed the Indicor majority sale and the TransCore discontinued-operations disposition — the same year net income printed $4,544,700,000 against operating income of $1,524,500,000 (divestiture gains in net income, cash taxes on those gains running through operating cash flow). Ex-2022 the OE series is a steady staircase on the filed history. The normalized/TTM bases handle the artifact; no extra bear weight was added for cyclicality that isn't there.
- **HIGH_NET_DEBT** (net debt 3.51x normalized OE): engine basis (Dec 31, 2025) net debt is $9,003,600,000. It rose further in H1 2026 as the $3.2B buyback program was substantially debt-funded; management put leverage at ~3.4x adjusted EBITDA on the Q2 call and guided to de-levering through second-half cash flow plus the Indicor instrumentation-sale proceeds (~$1.3B pre-tax, ~$1.1B after tax, per Q2 reporting) before resuming heavier M&A ($5B+ of deployment contemplated over the next 12–18 months). Mitigants, stated plainly: OE here is a levered flow (US-GAAP operating cash flow is already after interest paid) and revenue is predominantly recurring. Resolution: leverage is folded into the verdict by keeping default bear weights (35% combined bear/super-bear), capping confidence at medium, and noting that in the super-bear case the equity sits behind that debt stack against a stalled OE stream — that is exactly the $129.54 IV scenario.
- **WIDE_SCENARIO_SPREAD** (preliminary run only, 4.45x): narrowed to 3.91x in the final run by the recalibrated growth starts, so the flag no longer fires — but 3.91x is still wide in substance (genuine uncertainty about acquisition-dependent growth, not a modeling artifact). Confidence is therefore **medium**, not high.

## My thoughts / overlay
- Quality is not the debate. This is one of the best capital-allocation machines in the large/mid-cap universe: the two OE definitions agree within 1% in FY2025, OE/share has compounded at 11.91% (2y CAGR, engine), retention and margins are elite, and management demonstrated conviction by repurchasing ~8% of the share count in three quarters.
- The debate is price and the growth the price assumes. At $374.06 the market pays a full multiple of TTM owner's earnings (OE yield 6.33%) for a business whose organic growth is 5–6% — the rest of the per-share compounding must be bought, year after year, at today's deal multiples, now with 3.51x normalized-OE leverage on the balance sheet. The DCF says that package is worth ~12.4%, not 15%+.
- Method range: the preliminary run (median base $20.20, moat 5, engine growth, default scenarios) gave weighted IRR 11.89%; this final run (TTM base, recalibrated growth, moat 7) gives 12.39%; the prior v4 run gave 12.8% — every defensible input set lands in Tier C (≈12–13%). Unlike the APP pilot, the tier is not assumption-fragile.
- Hurdle math: the stock clears a 15% IRR at or below the weighted IV@15% of **$288.12**. That is a margin against the weighted case, not against the bear cases (bear IV@15% $196.76 sits far below the $374.06 price) — a buyer wanting insurance rather than just the weighted expectation needs a price much closer to the bear IV than to $288.12. Management's own H1 2026 buyback average ($346.34/share, per Q2 10-Q reporting) sits between the two — inside the "fair" zone, above the "clears 15%" zone.

## Final verdict
- **Final tier: C** (tier by numbers C; no override — weighted IRR 12.39%, and even the super-bull scenario only reaches 18.54%)
- Confidence: **Medium** (high on OE quality and the TTM base — both OE definitions agree and the TTM flow is free of the Indicor gain; capped at medium by 3.51x leverage and a still-wide 3.91x scenario spread)
- One-liner: Elite vertical-software compounder, moat 7/10 — but at $374 it is priced for the bull case: weighted IRR 12.4% (Tier C) on TTM OE of $23.69/share; clears the 15% hurdle only below ~$288, and with a real margin of safety nearer the bear case.
