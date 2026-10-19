# CRL — Charles River Laboratories International, Inc.
Engine 5.4 pass-1 run, 2026-10-17. In scope (market cap $14.877B at $300.15, nasdaq_quote_api).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
The largest preclinical contract research organization: Research Models & Services (research models, cell solutions), Discovery & Safety Assessment (the core preclinical testing franchise), and Manufacturing Solutions (biologics testing, CDMO). Revenue $4,015,382,000 in FY2025, down 0.9% — the third year of the post-COVID biotech-funding downturn. Q2 2026 showed the first stabilization: revenue $1.00B (reported −2.7% on divestitures, organic +0.1%, the first organic growth since Q3 2023), DSA net book-to-bill ~1.2x — a four-year high — and management raised FY2026 guidance to 0–1% organic revenue growth, non-GAAP EPS $11.15–$11.45, and free cash flow of $400–420M.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $737,646,000; capex $219,152,000; SBC $71,083,000 (always a real cost).
- **Conservative owner's earnings FY2025: $447,411,000 = $9.03/share** (latest FY OE/share, key_numbers.md)
- Maintenance version FY2025: $141,222,000 — far below the conservative figure because it is built on net income, which carries $376M of non-cash impairments (see NI_OCF_DIVERGENCE below). The OCF-based conservative figure is the clean one here; the impairments never touched cash.
- OE positive 5 of the last 5 fiscal years. Net debt $1,925,984,000 (FY2025: total debt $2,139,754,000 vs cash $213,770,000), plus lease liabilities of $491,711,000. Share count is shrinking slowly (share count CAGR −1.15%; diluted 49,564,000 latest FY, 48,486,000 in the current YTD period).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $737,646,000 − prior YTD $376,300,000 + current YTD $220,802,000 = **TTM $582,148,000**
- Capex: FY $219,152,000 − prior YTD $94,622,000 + current YTD $87,013,000 = **TTM $211,543,000**
- SBC: FY $71,083,000 − prior YTD $30,184,000 + current YTD $42,162,000 = **TTM $83,061,000**
- Shares (current-YTD weighted diluted): **48,486,000**
- **TTM OE total $287,544,000 → base OE/share $5.93** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $8.36/share — rejected as the base: it averages in pre-divestiture earnings power, and FY2025's $9.03 was flattered by a working-capital release (delta NWC −$101,400,000 in financials_history.csv). The TTM figure is the current, smaller portfolio's actual cash run-rate. The honest counterweight: TTM OCF is H1-weighted into a guided H2 recovery (FY2026 FCF guided to $400–420M), so $5.93 may be trough-ish — that uncertainty is carried in the scenario multipliers and in the method range below, not by picking the friendlier base.

## Moat: 5/10 — moderate, cyclical
Justification: scale leader in preclinical safety assessment with an integrated NHP supply chain and real switching friction, but returns were only modest even in good years and demand is hostage to the biotech funding cycle.
- FOR: largest preclinical CRO — scale and capacity in Discovery & Safety Assessment that sponsors cannot easily replicate; integrated nonhuman-primate supply chain, a scarce and hard-to-copy input; switching friction — safety studies sit on clients' regulatory critical path and track record matters; Research Models installed base and recurring services revenue.
- AGAINST: demand is cyclical — the biotech funding downturn cut revenue and OE for three straight years; ROIC was only ~9–11% even in good years and ~0% in FY2025 (below); non-animal methods (NAMs) and regulatory drift threaten the animal-testing core long-term; net debt 6.55x normalized OE limits flexibility through the trough; Chinese CRO price competition and large-pharma insourcing.
- **ROIC evidence (roic_proxy in fundamentals.json):** 8.6% / 11.4% / 9.6% / 8.9% / 9.1% / 9.9% / 9.4% / 8.5% across FY2016–FY2023 — consistently a bit above a typical cost of capital, never wide-moat territory — then 3.3% in FY2024 and 0.4% in FY2025 as impairments crushed operating income (operating margin 13.4–16.7% in FY2019–FY2023, 0.6% in FY2025). A 5 sits on that record: a real franchise whose returns cap out near 10% through a cycle. (The gross_margin field in fundamentals.json is not meaningful for CRL — its cost-of-services tagging produces a services-misclassified figure — so the moat call rests on ROIC and operating margin instead.)
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — engine 5.4 final run (2026-10-17)
Growth recalibration (written reason): the engine's blended growth is 4.58%, but that blend sits above every current print — latest FY revenue YoY −0.85%, Q2 2026 reported revenue −2.7% (organic +0.1%), FY2026 organic guidance 0–1% — and its loudest component, OE/share CAGR 2y of 25.93%, is a rebound artifact off the trough FY2023 base ($5.70/share), not a growth rate. Scenario starts were therefore set via offsets (−0.13 / −0.07 / −0.03 / +0.01 / +0.06 vs the blend) to −8.4 / −2.4 / **+1.6** / +5.6 / +10.6%: base ≈ guidance plus the early DSA bookings recovery; super bull ≈ a return to the FY2021–22 growth era on a full funding-cycle recovery. Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25. Price $300.15.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -8.4% | 0.75 | Funding downturn resumes; RMS/academic weakness spreads; leverage bites | $23.09 | 3.31% |
| Bear | 25% | -2.4% | 0.90 | Recovery stalls at flat; TTM cash conversion stays weak | $35.64 | 3.89% |
| Base | 30% | 1.6% | 1.00 | Guidance path: flat-to-1% organic, gradual H2 improvement | $46.81 | 4.43% |
| Bull | 25% | 5.6% | 1.10 | DSA book-to-bill converts; margins recover on lower NHP costs | $60.81 | 5.11% |
| Super bull | 10% | 10.6% | 1.25 | Full biotech funding recovery; back to FY21–22 growth | $84.94 | 6.29% |

- **Probability-weighted: IV@15% $48.96 (−83.7% vs price), IV@12% $64.51, IV@10% $81.80, weighted IRR 4.55%, base-case IRR 4.43%**
- **Tier by numbers: D** (bear tier D, bull tier D — no TIER_BAND). Diagnostics (key_numbers.md): OE yield 1.98%, terminal value 17.9% of IV@15%, scenario spread 3.68x, net debt 6.55x normalized OE, 9.7 months since FY end.
- Hurdle-clearing prices (weighted path): clears 15% at $48.96, 20% at $34.90, 25% at $27.11.

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 10 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above.
- **NI_OCF_DIVERGENCE** (2024, 2025): identified — non-cash impairments in the Manufacturing segment's Biologics Solutions reporting unit. Q4 2024 carried a $215.0M goodwill impairment (FY2024 net income $22,203,000 vs OCF $734,577,000); Q4 2025 carried $376M of impairments — $211.0M intangible (Biologics Solutions and the Cell Solutions business) plus $165.0M goodwill (Biologics Solutions) — driving FY2025 to a net loss of −$144,338,000 against OCF of $737,646,000 (all from financials_history.csv and the FY2025 earnings release). The charges are non-cash and sit below the OCF line the conservative OE is built on, so the base is not contaminated — but they are real evidence that acquisition-era capital in Manufacturing was overpaid, which feeds the moat call.
- **LOW_OE_YIELD** (base OE yield 2.0%): real and decisive. At $300.15 the stock is not priced on owner's earnings at all — it is priced on a full, fast recovery. Even the super-bull IV@15% ($84.94) sits 72% below the price; no scenario in the model gets within 3.5x of the market price.
- **HIGH_NET_DEBT** (net debt 6.6x normalized OE): confirmed from the filing — FY2025 total debt $2,139,754,000 vs cash $213,770,000 = net debt $1,925,984,000 (financials_history.csv), plus $491,711,000 of lease liabilities the net-debt figure excludes. Against the TTM OE actually used as the base the leverage is heavier still. The bear cases carry OE multipliers of 0.75–0.90 for exactly this reason; there is no distress case in the model because OCF has stayed positive through the trough (5/5 OE-positive years), but the equity cushion at this price is the recovery, not the balance sheet.
- Preliminary-run flag **WIDE_SCENARIO_SPREAD** (4.5x on the median base) narrowed to 3.68x on the TTM base with recalibrated growth; it remains wide in absolute terms and, with the leverage, caps confidence at low.

## My thoughts / overlay
- The honest headline is the method range, and here it does not rescue the stock: the preliminary run on the engine's normalized median base ($8.36/share, default scenario offsets) printed a weighted IRR of 5.97% and IV@15% of $80.08 — Tier D. The TTM-base final run: 4.55% and $48.96 — Tier D. Both defensible bases, same tier; the range is D→D.
- The market is paying for the turn, not the present: the shares are up ~81% over the past year and ~49% in 2026 (press coverage of the Q2 print), on a four-year-high DSA book-to-bill, raised guidance, divestitures of non-core businesses (which took a $63.7M GAAP loss in Q2 2026 and remove $200M+ of reported revenue — a basis break that will keep reported growth prints looking worse than organic through 2026), and expected H2 margin help from lower NHP sourcing costs. All of that can be true and the stock can still be far ahead of the owner's-earnings math: guided FY2026 non-GAAP EPS of $11.15–$11.45 is an adjusted figure; the filing-derived TTM owner's earnings are $5.93/share after capex and SBC.
- What would change the answer: OE/share actually recovering toward the FY2025 level ($9.03) on the smaller portfolio, with net debt falling — i.e., the bull path delivered in filings, not in bookings commentary. At that point the base, not the multiple, does the work.

## Final verdict
- **Final tier: D** (weighted IRR 4.55% on the TTM base; the median-base method also prints D — the verdict is not base-sensitive)
- Confidence: **Low** (filing-solid base, but wide scenario spread, 6.55x leverage on normalized OE, and a recovery-dependent price)
- One-liner: Real CRO franchise, moat 5/10, but at $300.15 the price already pays for a full recovery and more — TTM OE/share of $5.93 supports only a 4.6% weighted IRR (weighted IV@15% $48.96); the shares would need to fall to ~$49 to clear the 15% hurdle.

## Data note
Enrichment completed (fundamentals, prices, segments, statements, profile, reprice all written). One non-blocking gap: profile.py found no 10-K Item 1 Business description outside the table of contents (10-K filed 2026-02-18), so profile.json's description is null; the score does not depend on it.
