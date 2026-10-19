# IONQ — IonQ, Inc.
Engine 5.4.0 run, 2026-10-16. Price $31.28 (nasdaq_quote_api), market cap est. $8.77B — in scope under $40B.

All figures below are copied from dcf_numbers.json, financials_history.csv, or ttm.py output — none are recomputed.

## What it is
Pure-play quantum computing company (trapped-ion systems), plus quantum networking and sensing via acquisitions. Revenue is scaling fast off a tiny base — FY2025 revenue $130,016,000 vs $43,073,000 in FY2024 — and Q2 2026 printed a record $80.1M (+287% YoY) with FY2026 guidance raised to $450–460M including SkyWater Technology (closed 2026-07-31). None of that has yet produced a dollar of owner's earnings.

## Owner's earnings
**FY2025 (10-K via EDGAR):** operating cash flow −$283,187,000; capex $16,417,000; SBC $312,032,000 (always a real cost — and here it is larger than revenue).
- **Conservative owner's earnings FY2025: −$611,636,000 = −$2.18/share**
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): −$1,545,216,000 — even worse, driven by the huge ΔNWC swing in financials_history.csv.
- OE positive **0 of the last 5 fiscal years** (oe_positive_years_of_last_5: "0/5"). Conservative OE/share by year: 2021 −$0.31, 2022 −$0.43, 2023 −$0.80, 2024 −$1.08, 2025 −$2.18 — losses per share are widening, not narrowing, because SBC and cash burn grow faster than revenue.
- **Normalized base (3-yr median, the engine base): −$1.08/share.** Latest FY alone: −$2.18/share. Both deeply negative.

**TTM check (ttm.py, through Q2 2026):** TTM OCF −$452,369,000; TTM capex $31,499,000; TTM SBC $449,973,000; TTM shares (current-YTD weighted diluted) 363,265,843 → **TTM OE total −$933,841,000 = −$2.57/share**. The TTM base is worse than the FY base — there is no positive base on any window, so no --ttm override is possible or warranted.

## Moat: 2/10 — none demonstrated yet
Justification: a technology lead in trapped-ion fidelity is real but unproven as an economic moat — no positive returns on capital in any year, no demonstrated pricing power, and the field is contested by IBM, Google, Honeywell/Quantinuum, Rigetti and D-Wave with far larger balance sheets. ROIC proxy cannot be quoted as positive evidence: operating income is negative in every filed year (FY2025 operating loss −$633,715,000 on $130,016,000 of revenue), so returns on invested capital are deeply negative through the whole history — a moat of 7+ would need exactly the through-cycle ROIC evidence this company does not have.
- FOR: trapped-ion architecture with high gate fidelity and a published error-correction roadmap; first-mover commercial revenue among pure plays (record quarters, $485M remaining performance obligations per Q2 2026 reporting); growing government/defense and international demand; vertical integration via the SkyWater fab acquisition and Oxford Ionics.
- AGAINST: no profitable year, ever — negative OE in 5 of 5 years and widening per-share losses; SBC ($312M in FY2025, $450M TTM) exceeds revenue and dilutes holders at a 12.3%/yr share-count CAGR; competing architectures (superconducting, photonic, neutral-atom) backed by IBM/Google/Honeywell R&D budgets dwarf IonQ's; quantum advantage at commercial scale remains unproven — revenue is mostly systems sales and government programs, not recurring high-margin cloud economics.
- A 2 gives CAP = 4.6 years — moot here, since there is no positive base to project.

## DCF
No scenario table: the engine returns **Tier F, subtype no_cash_generation** — "No positive NORMALIZED (3-yr median) conservative owner's earnings — OE DCF not supportable on numbers alone" (sum of the last 3 fiscal years' OCF − capex is not positive). This is not a data gap: data_gap is empty, every field filed. The growth blend (175.5%, capped artifacts from a near-zero revenue base) is meaningless against a negative base and is not used. No IV or IRR exists to report; inventing one would require assuming the entire future profitability path.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9 months ago): resolved — ttm.py run through Q2 2026; TTM OE/share −$2.57 is worse than the FY figure, confirming the F rather than overturning it. Quoted above.
- **DILUTION** (share count +12.3%/yr): real and structural — SBC was $312,032,000 in FY2025 and $449,973,000 TTM, exceeding revenue in both windows; diluted shares rose from 213,029,365 (FY2024) to 280,345,046 (FY2025) to 363,265,843 TTM. This is the single largest destroyer of per-share value here.
- **BASIS_BREAK_SUSPECT** (>60% revenue jump): the jump is organic-from-tiny plus acquisition layering (Oxford Ionics 2025; SkyWater closed 2026-07-31, after the FY2025 statements) — revenue went $2.1M → $11.1M → $22.0M → $43.1M → $130.0M. No divestiture or restatement in the filed history. Either way, no CAGR is trusted for valuation because the OE base is negative.
- **NI_OCF_DIVERGENCE** (2023, 2024, 2025): explained by non-cash SBC — net income losses (−$157.8M / −$331.6M / −$510.4M) are far larger than OCF burn (−$78.8M / −$105.7M / −$283.2M) chiefly because SBC ($69.7M / $106.9M / $312.0M) is added back in OCF. The conservative OE definition deducts SBC in full, so the divergence does not flatter the base; if anything the OCF-based figure is the honest one.
- **SHARES_FALLBACK** (2020): noted — the 2020 history year uses the outstanding count (no diluted count filed), so 2020 per-share figures are approximate. Immaterial to the verdict; every year is negative regardless.
- **DEBT_TAGS_BLANK**: balance sheet from the filed history (FY2025): cash $1,030,865,000, no debt tags reported, lease liabilities $30,021,000, total liabilities $2,756,666,000 against equity $3,799,517,000 and assets $6,570,358,000. The company is funded by equity issuance, not leverage — solvency is not the issue; cash burn against that cash pile is (FY2025 OCF burn −$283M and rising, partly offset by the large cash/investments position reported at Q2 2026).

## My thoughts / method range
- There is no defensible method range to quote: every window (latest FY, 3-yr median, TTM) gives a negative base, so the OE DCF returns F under all of them. The stock is a venture-style option on fault-tolerant quantum computing, priced at ~$8.8B on $130M of FY2025 revenue — valuation rests on 2030s revenue scenarios, not on owner earnings.
- What would change the verdict: OCF turning positive on a TTM basis with SBC falling as a share of revenue. Neither is close — TTM SBC alone is $450M against guided FY2026 revenue of $450–460M (which itself now includes SkyWater's foundry revenue, a lower-margin business than the quantum narrative implies).
- Insider selling across the quantum pure plays and a ~43% drawdown in the shares from late May to late August 2026 are sentiment facts, not valuation inputs; the F rests on the filings alone.

## Final verdict
- **Final tier: F** (no positive conservative owner's earnings on any basis — FY, median, or TTM)
- Confidence: **High** on the F itself (complete filing data, no gaps, every window negative); the uncertainty is about the distant future, which this method deliberately does not price.
- One-liner: Pre-profit quantum pure play, moat 2/10 — negative owner's earnings in 5 of 5 years and −$2.57/share TTM with SBC exceeding revenue; no OE base exists, so it cannot clear 15% at any price on this method.
