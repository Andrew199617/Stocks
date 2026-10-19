# PEN — Penumbra, Inc
Engine 5.4.0 run, 2026-10-18. Market cap $12.607B at $320.86 (nasdaq_quote_api) — in scope under $40B.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json or fundamentals.json — none are recomputed.

## What it is
Alameda, California medical-device company — the world's leading thrombectomy company. Computer-assisted vacuum thrombectomy (CAVT) and aspiration systems remove blood clots head-to-toe: neurovascular (ischemic stroke), venous thromboembolism / pulmonary embolism, arterial, plus embolization and vascular-access products. Single-use catheters and disposables sold to hospitals in 100+ countries; revenue is procedure-linked and recurring. Q2 2026 revenue $390.0M, +14.9% YoY (thrombectomy $259.0M, +12.5%; embolization & access $131.1M, +20.0%), gross margin 67.9% (Q2 2026 8-K / earnings release, via search).

**Dominating fact — pending acquisition:** on 2026-01-14 Penumbra entered a merger agreement with Boston Scientific valuing each share at $374 (elect $374 cash or 3.8721 BSX shares, prorated to ~73% cash / ~27% stock; ~$14.5B enterprise value), expected to close by the end of 2026 subject to stockholder and regulatory approvals. Boston Scientific confirmed on 2026-09-10 the deal remains on track (search). The $320.86 price is a merger-arbitrage price anchored to the $374 consideration, not a standalone-fundamentals price. The DCF below is the standalone business, i.e. what the shares rest on if the deal breaks.

## Owner's earnings
**FY2025 (10-K via EDGAR, financials_history.csv):** operating cash flow $238,663,000; capex $63,729,000; SBC $59,213,000 (always a real cost).
- **Conservative owner's earnings FY2025: $115,721,000 = $2.95/share** (latest FY OE/share).
- Maintenance version is not usable this year: it is dragged far negative by the ΔNWC leg in the filed history, while the OCF-based conservative figure is corroborated by the TTM build below — the conservative series is used throughout.
- OE positive only 3 of the last 5 fiscal years: OE/share was −$2.04 (2021), −$2.97 (2022), $0.81 (2023), $2.58 (2024), $2.95 (2025) — a genuine inflection from scale-driven losses to profitability, not a mature cash machine's history.
- History: revenue CAGR 20.16% (5y) / 18.33% (3y); FY2025 revenue $1,403,665,000, +17.50% YoY.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $238,663,000 − prior YTD $93,916,000 + current YTD $133,055,000 = **TTM $277,802,000**
- Capex: FY $63,729,000 − prior YTD $29,046,000 + current YTD $27,213,000 = **TTM $61,896,000**
- SBC: FY $59,213,000 − prior YTD $28,019,000 + current YTD $28,304,000 = **TTM $59,498,000**
- Shares (current-YTD weighted diluted): **39,572,347**
- **TTM OE total $156,408,000 → base OE/share $3.95** (base_source: ttm_json)
- The engine's normalized base (median of last 3 FY OE/share) is $2.58 — rejected as the base because it averages in the pre-profitability inflection years; it is still reported here. Even the higher TTM base gives an OE yield of only 1.23% at $320.86.

## Moat: 5/10 — moderate / narrow
Justification: leading pure-play thrombectomy franchise (CAVT computer-assisted vacuum technology, proprietary IP, physician training and workflow switching costs, 67–68% gross margins), but ROIC has not stayed above the cost of capital through a cycle and Medtronic/Stryker compete with far larger scale and distribution.
- FOR: world's leading thrombectomy company, pure-play CAVT/aspiration focus across neuro, venous, pulmonary and arterial clots; proprietary technology and IP validated by clinical evidence (STORM-PE randomized trial, STRIKE-PE registry); physician training, workflow integration and the installed pump base create switching costs, with single-use disposables giving recurring procedure-linked revenue; gross margin 67.1% FY2025 and 67.9% Q2 2026, up from 63.2% FY2024.
- AGAINST: measured returns are weak and volatile — roic_proxy (fundamentals.json) was −0.66% (2021), 0.52% (2022), 5.74% (2023), 0.75% (2024) and 13.21% (2025); gross margin over the last five fiscal years was 63.6% / 63.2% / 64.5% / 63.2% / 67.1% — good, but the ROIC record is an inflection, not a proven through-cycle franchise, so a 7+ is not justified; Medtronic (Solitaire) and Stryker (Trevo) lead neurovascular thrombectomy per 2025 market analysis (search) with far larger distribution and R&D breadth; revenue concentrated in one category; reimbursement/payback pressure (the Italian payback provision) and SBC of $59,498,000 TTM.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — engine 5.4.0 final run (2026-10-18)
Growth sanity check: the engine blend is 17.98% (rev CAGR 5y 20.16%, 3y 18.33%, latest YoY 17.50%, OE/share CAGR 2y 91.08% — the last is an inflection artifact off the depressed 2023 base and was not allowed to set scenario starts). Actual recent prints: FY2025 revenue +17.5%, TTM revenue +17.55% (fundamentals.json TTM), Q2 2026 +14.9%. The default super-bull start of 29.98% sits above every recent print (the highest forward signal was Q4 2025 growth of ~21.4–22.0% in the merger release), so scenario starts were recalibrated via offsets (−0.12 / −0.06 / −0.02 / +0.03 / +0.07 vs the blended 17.98%) to 5.98 / 11.98 / **15.98** / 20.98 / 24.98% — the base start sits between the Q2 print and the TTM/FY prints, and even super-bull stays near the best print the company has produced. Probabilities 15/25/30/20/10 (bear weight widened per OE_VOLATILE); OE multipliers 0.75/0.90/1.00/1.10/1.25. Price $320.86.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | 5.98% | 0.75 | Deal breaks into a share-price air pocket; growth halves, giants take share | $28.09 | 3.64% |
| Bear | 25% | 11.98% | 0.90 | Growth settles at the Q2-print level or below; margins stall | $43.17 | 4.36% |
| Base | 30% | 15.98% | 1.00 | Mid-teens growth decaying over the CAP on the TTM base | $56.47 | 5.00% |
| Bull | 20% | 20.98% | 1.10 | CAVT share gains in PE/venous sustain ~20% growth | $76.02 | 5.93% |
| Super bull | 10% | 24.98% | 1.25 | Category-killer path: PE/neuro expansion plus margin leverage | $101.35 | 7.08% |

- **Probability-weighted: IV@15% $57.29 (−82.1% vs price), weighted IRR 5.06%, base-case IRR 5.00%**
- **Tier by numbers: D — and D in every scenario, bear and bull alike (no TIER_BAND).**
- Diagnostics: OE yield 1.23%, terminal value 21.3% of IV@15%, scenario spread 3.61x, 9.6 months since FY end.
- Hurdle prices: clears 15% only at or below $57.29, 20% at $38.89, 25% at $28.99.

## Flags — every fragility flag resolved
- **STALE_FY** (FY2025 ended 9.6 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above. TTM OE/share $3.95 vs latest-FY $2.95 and median $2.58.
- **OE_VOLATILE** (OE/share spans >3x over 5 years, in fact from −$2.97 to $2.95): real — it is the loss-to-profit inflection, not ordinary cyclicality. Handled by the TTM base plus widened bear-side weight (super bear 15%, bear 25%).
- **NI_OCF_DIVERGENCE (2024)**: found — FY2024 net income was only $14,012,000 against OCF of $168,481,000 because H1 2024 carried a $76,945,000 non-cash impairment charge and $36,184,000 of inventory write-downs (10-Q cash-flow reconciliation, via search); GAAP operating income was $9,279,000 for FY2024 vs $106.6M non-GAAP per the FY2024 release. The non-cash charges depress net income, not operating cash flow, so the OCF-based conservative OE base is not contaminated.
- **DEBT_TAGS_BLANK**: stated from the filing — Penumbra files no debt tags because it carries no borrowings: FY2025 total liabilities were $398,916,000 against equity of $1,427,603,000, cash $186,897,000 plus short-term investments $357,919,000 (fundamentals.json), operating/finance lease liabilities $196,592,000 (financials_history.csv). Q2 2026 release: cash $205.3M plus marketable investments $453.5M. Net debt is unknown to the engine but the filed balance sheet is effectively net cash ex-leases; no leverage verdict is needed for a Tier D driven by price vs OE, not by debt.
- **LOW_OE_YIELD** (1.23% on the TTM base): real and decisive — at $320.86 the valuation rests almost entirely on growth and, in practice, on the $374 merger consideration. Confidence is capped at low.
- The preliminary run's **WIDE_SCENARIO_SPREAD** (4.39x) fell to 3.61x in the final run after the growth recalibration; confidence stays low for the LOW_OE_YIELD / merger reasons above.

## My thoughts / overlay
- The standalone DCF and the market price are pricing two different things. Every scenario — including super-bull at a 24.98% growth start and a 1.25 OE multiplier — values the standalone business at $101.35 or less against a $320.86 price. Boston Scientific's $374 is a strategic price (buying the neurovascular franchise it exited in 2011, synergies, and scarcity value after Stryker/Inari), not an owner's-earnings price. If the deal closes by end-2026 as guided, holders get the $374 election value; if it breaks, the standalone anchor from this model is an order of magnitude below the current quote, even allowing that the model is harsh on a just-inflected OE base.
- Method range: on the rejected median base ($2.58) the preliminary run printed weighted IRR 4.47% and IV@15% $42.59; on the TTM base ($3.95) the final prints 5.06% / $57.29. The base choice moves the answer ~35%, and both are Tier D by a wide margin — the tier is robust to the method argument.
- Quality is real but young: gross margin expanding into the high-60s, TTM OE +41% YoY per fundamentals.json, no debt. What is missing is a through-cycle ROIC record and any owner's-earnings yield at this price. SBC at $59,498,000 TTM is 38% of TTM OE — a real, ongoing dilution cost already charged in the base.
- Data notes: enrichment outputs (fundamentals/prices/segments/statements/profile/reprice) are run after scoring per spec; any failure is non-blocking and would be noted here — none affected the figures above, which come from the engine, ttm.py and fundamentals.json.

## Final verdict
- **Final tier: D** (weighted IRR 5.06% on the TTM base; every scenario is D)
- Confidence: **Low** (OE yield 1.23%, volatile OE history, and a price set by a pending merger rather than by standalone cash flows)
- One-liner: Quality thrombectomy leader, moat 5/10 — standalone DCF does not clear 15% at any scenario (weighted IRR 5.1%, IV@15% $57.29 vs $320.86 price; clears 15% only below ~$57); the price is anchored to Boston Scientific's pending $374/share acquisition, not to standalone owner's earnings.
