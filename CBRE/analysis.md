# CBRE — CBRE Group, Inc. (NYSE: CBRE)
v5 re-run, 2026-10-14 (supersedes the v4 pass of 2026-10-13; verdict unchanged). Price $129.67 (nasdaq_quote_api), market cap $38.998B — in scope (<$40B), near the top of it.

All figures below are copied from key_numbers.md, dcf_numbers.json, financials_history.csv, or ttm.py output — none are recomputed. Quarter and deal figures are from the web searches of this run.

## What it is
The world's largest commercial real estate services and investment firm. Four segments after the 2025 resegmentation: **Advisory** (leasing, property sales, capital markets, mortgage origination, valuation — the cyclical, transactional core), **Building Operations & Experience** (facilities management / enterprise accounts — long-term outsourcing contracts, the largest and most recurring block; includes the fast-growing critical-infrastructure / data-center services business), **Project Management** (Turner & Townsend majority-owned), and **Real Estate Investments** (CBRE Investment Management + Trammell Crow development). The strategic story is mix shift: resilient outsourcing/PM/IM revenue now outweighs pure transaction fees, which dampens — but does not remove — cycle exposure. FY2025 revenue $39,900,000,000 (financials_history.csv), latest rev YoY 13.41% (key_numbers.md). Note gross revenue includes large pass-through costs (especially in facilities management), so it overstates economic scale vs fee revenue.

## Owner's earnings
History (SEC EDGAR 10-K via financials_history.csv; conservative = OCF − capex − SBC; maintenance = NI + D&A − min(capex, D&A) − ΔNWC; capex_tag / sbc_tag columns record the tag used per period — capex is `PaymentsToAcquireProductiveAssets` in the recent years, SBC is `ShareBasedCompensation` throughout):

| FY | OCF | Capex | SBC | Conservative OE | Maintenance OE |
|---|---|---|---|---|---|
| 2021 | $2,364,000,000 | $209,851,000 | $185,000,000 | $1,969,149,000 | $2,727,578,000 |
| 2022 | $1,629,000,000 | $260,140,000 | $160,000,000 | $1,208,860,000 | $1,595,405,000 |
| 2023 | $480,000,000 | $305,000,000 | $96,000,000 | $79,000,000 | $533,000,000 |
| 2024 | $1,708,000,000 | $307,000,000 | $146,000,000 | $1,255,000,000 | $1,897,000,000 |
| 2025 | $1,559,000,000 | $366,000,000 | $120,000,000 | $1,073,000,000 | $1,749,000,000 |

- OE positive 5/5 years (key_numbers.md), but violently cyclical: the 2023 collapse (OCF $480,000,000 in the rate-shock transaction freeze) and the 2024 snap-back are working-capital and transaction-volume swings, not changes in franchise value. Maintenance OE runs consistently above conservative OE (capex is genuinely light for a people business) — the conservative figure is the right base-case definition here.
- **Base used = normalized 3-yr median = $3.57/share** (base_source: median_of_last_3_fy_oe_per_share; latest FY OE/share is also $3.57, latest FY OE total $1.073B — key_numbers.md). OE yield 2.75% at $129.67.
- **TTM check (ttm.py, filing-direct, run for STALE_FY — saved to ttm.json, quoted in full, NOT used as the base):**
  - OCF: FY $1,559,000,000 − prior YTD −$489,000,000 + current YTD −$687,000,000 = **TTM $1,361,000,000** (FY period 2025-01-01 to 2025-12-31; YTD periods to 2026-06-30)
  - Capex: FY $366,000,000 − prior YTD $138,000,000 + current YTD $195,000,000 = **TTM $423,000,000**
  - SBC: FY $120,000,000 − prior YTD $63,000,000 + current YTD $107,000,000 = **TTM $164,000,000**
  - Shares (current-YTD weighted diluted): **295,411,671**
  - **TTM OE total $774,000,000 → TTM OE/share $2.62**
  - Reason the TTM base was not adopted (ADM precedent in this sweep): it is distorted down by CBRE's H1 cash machine — annual bonuses/comp are paid in H1 and collections are H2-weighted, so H1 OCF is deeply negative every year, and H1 2026 ran at a larger scale on acquisition-assisted growth while the earnings evidence pointed the other way: Q2 2026 core EPS rose 30% YoY and management *raised* FY2026 core EPS guidance (search results below). Swapping the through-cycle median for this seasonal-timing snapshot would trade a normalized base for an artifact. The verdict is Tier D on either base (see method range), so the choice is not load-bearing — the median is the more generous of the two and it still fails by a wide margin.
- Latest quarter (Q2 2026, web search of the earnings release coverage): revenue $11.23B, up 16% YoY; GAAP EPS $0.69; core EPS $1.56, up 30% YoY; every segment grew segment operating profit by more than 25%; FY2026 core EPS guidance raised to $7.80–7.90 from $7.60–7.80. Infrastructure/data-center services were the highlighted growth engine. Q3 2026 results are scheduled for October 22, 2026.

## MOAT — score 6/10 (moderate-strong, not wide). CAP = 9.8 years
Justification: Global #1 CRE services scale and breadth, recurring facilities/outsourcing + project management + investment management mix with real switching costs, unmatched data/talent density — against a people-based advisory core whose producers can walk, un-moated transaction cyclicality, hard-negotiating institutional clients, and growth increasingly bought via M&A.
- FOR:
  - Global #1 at scale across leasing, sales, outsourcing and investment management simultaneously — no rival (JLL, Cushman & Wakefield, Colliers, Newmark) matches the breadth.
  - Recurring facilities-management/outsourcing contracts embedded in client operations, plus project-management and IM fees — real switching costs: switching a global facilities provider is an operational disruption, not a phone call.
  - Largest managed portfolio and transaction dataset in the industry; scale funds tech/AI spend smaller rivals cannot match.
  - Diversification across property types and geographies softened the 2023 trough vs a pure brokerage (OE stayed positive; resilient segments kept growing).
- AGAINST:
  - People business at the profit core: producers own the client relationships and can walk to rivals; no owned asset, patent, or network effect locks in the advisory fee pool.
  - Cyclicality is un-moated: conservative OE total fell to $79,000,000 in 2023 when rates froze transactions. A moat that cannot stop that is a scale advantage, not a wide moat.
  - Sophisticated institutional clients negotiate fees hard; pricing power is unproven through a full cycle.
  - Growth increasingly bought via M&A (Pearce, acquired late 2025 for ~$1.2B cash plus an earn-out; Industrious, ~$841M total consideration per the Q1 2026 10-Q summary in search results) — goodwill/integration risk, and it flatters reported growth vs organic OE compounding.
  - AI/automation threatens standardized valuation, brokerage and reporting tasks; CBRE invests heavily, but so do rivals, with no proven durable tech edge.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Inputs: base OE $3.57/share (normalized median, above), moat 6 (CAP 9.8 yrs), price $129.67, OE yield 2.75%.

**Growth recalibration (written reason, sanity check vs recent prints):** the engine's g_base is 15.27% (growth blend 12.45% → g_base 15.27%; components: rev CAGR 5y 11.48%, rev CAGR 3y 9.76%, latest rev YoY 13.41%, OE/share CAGR 2y 275.36% — the last is an artifact off the trough base and is neutralized by the median blend; share-count adjustment +2.82pp is inside the blend). 15.27% is too high as a sustained OE start: the blend is built on *gross* revenue, which includes pass-through costs and acquisition contributions (Pearce/Industrious), not organic fee growth. Recent prints — FY2025 rev YoY 13.41%, Q2 2026 revenue +16% and core EPS +30% with FY2026 core EPS guidance implying a recovery year — are recovery + buyback + M&A prints, not a compoundable OE rate for a mature services leader. Scenario starts were therefore set via offsets (−0.1927 / −0.1227 / −0.0727 / −0.0227 / +0.0273 vs g_base) to −4% / +3% / **+8%** / +13% / +18%. The bull and super-bull starts sit at/below the latest gross-revenue prints deliberately, for the reason just stated — that is the written reason the sanity check requires. Probabilities skewed bear-ward from the 10/25/30/25/10 defaults to 15/25/30/20/10 per the OE_VOLATILE instruction to widen bear weight; OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25.

| Scenario | Prob | Growth start | OE mult | Story | IV@15% | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −4.0% | 0.75 | 2023-style transaction freeze repeats; levered OE compresses hard | $16.43 | 3.92% |
| Bear | 25% | 3.0% | 0.90 | Slow capital-markets recovery; resilient segments carry the P&L | $26.92 | 5.11% |
| Base | 30% | 8.0% | 1.00 | Mid-cycle growth: outsourcing/PM/IM compounding, transactions normalize | $37.36 | 6.32% |
| Bull | 20% | 13.0% | 1.10 | Capital-markets boom plus data-center/infrastructure momentum sustained | $51.31 | 7.87% |
| Super bull | 10% | 18.0% | 1.25 | Full boom: transactions, development gains and infrastructure all fire together | $72.72 | 10.07% |

- **Probability-weighted: IV@15% $37.94 (−70.7% vs price), IV@12% $50.99, IV@10% $65.64, weighted IRR 6.42%, base-case IRR 6.32%**
- **Tier by numbers: D.** Diagnostics (key_numbers.md): OE yield 2.75%, terminal value 20.0% of IV@15% (the low IV is not a terminal-value artifact — the cash flows themselves are too small for the price), scenario spread 4.43x, net debt 3.04x normalized OE, 9.4 months since FY end.

## FLAGS — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 9.4 months ago): ttm.py was run and its full inputs are quoted above (TTM OE/share $2.62, saved to ttm.json). The TTM base was *not* adopted — H1 bonus/WC seasonality amplified by acquisition-driven scale, with Q2 earnings and raised guidance pointing the other way; the median base is used and the TTM figure is disclosed as bear-side evidence. Current-quarter evidence is reflected in the scenario starts instead.
- **BUYBACK_TAILWIND** (share count shrinking 2.8%/yr; key_numbers.md: share count CAGR −2.82%): confirmed and already credited via the +2.82pp growth adjustment inside the blend — not double-counted in the verdict. Diluted shares have fallen from 340,522,871 (FY2019, financials_history.csv) to 300,751,541 (FY2025). At $129.67 against a $37.94 weighted IV@15%, buybacks retire stock far above intrinsic value on this model, which destroys rather than creates per-share value at this price; the tailwind is arithmetic, not a bargain signal.
- **OE_VOLATILE** (OE/share range over the last 5 yrs spans >3x): confirmed in totals — conservative OE $1,969,149,000 (2021) → $79,000,000 (2023) → $1,255,000,000 (2024) → $1,073,000,000 (2025). Resolution: normalized median base (not a single year), bear weight widened to 40% combined, super-bear start set negative with the 0.75 OE multiplier carrying the trough risk. This flag is the single best description of the stock: the franchise is durable, the earnings stream is not smooth.
- **NI_OCF_DIVERGENCE** (net income and operating cash flow differ by >40% in 2024): found and explained — working-capital timing, not an earnings-quality one-off. 2023: net income $986,000,000 vs OCF $480,000,000, with ΔNWC a $770,000,000 use (financials_history.csv). 2024: net income $968,000,000 vs OCF $1,708,000,000, with ΔNWC swinging to a $562,000,000 release as the 2023 build unwound, alongside D&A of $674,000,000. No tax deposit, impairment, or one-off gain drives the gap; it is the mirror image of OE_VOLATILE and is exactly why the base is a 3-yr median of the OCF-based series rather than either single year.
- **SECTOR_MODEL_MISMATCH** (Finance sector — OE/capex DCF fits finance names poorly; grade confidence low): classification artifact, addressed head-on. CBRE sits in the universe's Finance/Real Estate bucket, but it is an operating services company — no loan book, no insurance float, no deposit funding — and the OE/capex DCF fits it materially better than a bank or insurer (asset-light, real OCF, clean EDGAR history; capex and SBC are filed for every year of the last 3 FY — data_gap is empty). The genuine model-fit caveats are the Real Estate Investments segment's co-invest/development exposure and pass-through revenue inflation, both handled above. Per the sweep rule, confidence is graded **low** and the tier is treated as soft.
- **WIDE_SCENARIO_SPREAD** (super-bull IV is 4.43x super-bear IV): real, not a modeling defect — it is the honest shape of a cyclical services franchise (2023 conservative OE was $79,000,000; a boom year prints multiples of that). Consequence applied: confidence is low (also capped by the sector rule), bear weight widened to 40% combined, and the verdict is sized to the weighted/conservative end.
- **HIGH_NET_DEBT** (net debt is 3.04x normalized OE): FY2025 net debt $3.257B (key_numbers.md) against trough-sensitive OE — in a 2023-repeat, OE of $79,000,000 would not cover interest comfortably, so the leverage is real. Search results for the Q1 2026 10-Q show long-term debt of $5,149M at March 31, 2026 after funding the Pearce and Industrious acquisitions, so leverage has risen since FY-end. Mitigants: OE is measured after cash interest (no double-count in the DCF), maturities are termed out, and H2 collections seasonally rebuild cash. Folded into the verdict via the 40% combined bear weight and the super-bear OE multiplier — leverage is a reason the bear cases bite, not a separate tier override.

## Thoughts / overlay
- **Method range:** every defensible input set lands in Tier D. Preliminary v5 run (median base $3.57, default growth/probs, moat 5): weighted IRR 8.08%, IV@15% $52.88 (preliminary dcf_numbers.json of this run). Final run (recalibrated growth, bear-skewed probs, moat 6): 6.42%, $37.94. The TTM base ($2.62/share, ttm.json) is lower than the median base used, so a TTM-based run would land deeper in D. Even the final run's *super-bull alone* — 18.0% growth start, OE ×1.25 — yields only a 10.07% IRR at $129.67. There is no honest version of this model where today's price clears 15%; it does not clear 10% on the weighted path.
- Quality is not the debate: #1 global franchise, mix shifting toward recurring revenue, data-center/infrastructure exposure is a genuine AI-adjacent tailwind (Q2 2026 segment profit growth above 25% in every segment, guidance raised). The debate is purely price: at an OE yield of 2.75% on normalized OE, the buyer pre-pays for a decade of clean compounding from an earnings stream whose conservative OE total was $79,000,000 three fiscal years ago, funded partly with rising debt.
- **Hurdle math:** the stock clears a 15% IRR at ≈ **$37.94** (the weighted IV@15%). A margin of safety would require a price materially below that figure. At $129.67 the market price embeds the bull case as the base case.
- Watch items: a rate-driven transaction boom large enough to lift OE/share sustainably well above the normalized base; capital-return and leverage discipline after the Pearce/Industrious debt build; whether Pearce/infrastructure margins hold once acquisition accounting washes out; Q3 2026 results on October 22, 2026.

## Final verdict
- **Final tier: D** (weighted IRR 6.42%; tier by numbers D, no override — the numbers and the overlay agree)
- Confidence: **Low** (per the SECTOR_MODEL_MISMATCH rule, reinforced by the 4.43x scenario spread and genuine OE cyclicality — the flag section explains why the model still broadly fits this operating company)
- One-liner: No. 1 global CRE services franchise, moat 6/10 — but at $129.67 (OE yield 2.75% on normalized OE of $3.57/sh) the weighted IRR is just 6.42% with IV@15% of $37.94; even the super-bull case only reaches 10.07%, so it clears the 15% hurdle only at ~$37.94.
