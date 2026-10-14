# ZM — Zoom Communications, Inc.
v5 run, 2026-10-14. Market cap $29.26B at $95.21 (nasdaq_quote_api) — in scope under $40B.

All figures below are copied from dcf_numbers.json, ttm.json, or financials_history.csv — none are recomputed.

## What it is
Video-first unified communications platform, now an "AI-first work platform": Meetings core, plus Zoom Phone (10M+ paid seats), Contact Center (high-double-digit growth), Workvivo, and AI Companion. Revenue is split between Enterprise (growing) and Online (flat, churn-prone). FY ends Jan 31.

## Owner's earnings
**FY2026 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,989,048,000; capex $64,961,000; SBC $760,776,000 (always a real cost — and it is the whole story of this P&L: SBC has fallen every year from its FY2023 peak of $1,285,752,000).
- **Conservative owner's earnings FY2026: $1,163,311,000 = $3.79/share** (latest FY OE/share, dcf_numbers.json).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $2,005,426,000 — materially above the conservative figure because FY2026 net income ($1,900,148,000) is flattered by non-operating gains; the OCF-based conservative figure is the cleaner one and is used throughout.
- OE positive 4 of the last 5 fiscal years — FY2023 conservative OE was negative (-$99,316,000) purely because SBC peaked at $1.29B against $1,290,262,000 of OCF. The OE series is therefore mostly an SBC-normalization series, not an operating-collapse/recovery series.

**Base used = TTM owner's earnings through Q2 FY2027 (period ended 2026-07-31), from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,989,048,000 − prior YTD $1,005,201,000 + current YTD $1,016,361,000 = **TTM $2,000,208,000**
- Capex: FY $64,961,000 − prior YTD $33,876,000 + current YTD $43,466,000 = **TTM $74,551,000**
- SBC: FY $760,776,000 − prior YTD $390,268,000 + current YTD $358,737,000 = **TTM $729,245,000**
- Shares (current-YTD weighted diluted): **300,021,287**
- **TTM OE total $1,196,412,000 → base OE/share $3.99** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $2.78/share — rejected as the base: it averages in the peak-SBC trough years. Latest FY ($3.79) and TTM ($3.99) agree with each other; the median is the distorted figure (see BASE_DIVERGENCE below).

## Moat: 5/10 — moderate, real but contested
Justification: a default-brand enterprise installed base and a broadening platform give Zoom genuine retention in Enterprise, but the core meeting product faces a bundled near-zero-marginal-price competitor (Microsoft Teams inside M365), enterprise net dollar expansion sits at 99% (existing customers are not expanding), and AI features are being given away by rivals — no proven pricing power at the platform level yet.
- FOR: default brand and large enterprise installed base; meetings workflow embedded in daily operations
- FOR: platform breadth beyond meetings — Zoom Phone at 10M+ paid seats, Contact Center growing high-double-digits, Workvivo — raises switching costs for customers who adopt more than one product
- FOR: ~79% non-GAAP gross margin and a debt-free, cash-rich balance sheet (see overlay) fund sustained R&D and buybacks
- AGAINST: Microsoft Teams bundled into Microsoft 365 competes at effectively zero incremental price; Google Meet does the same in its suite
- AGAINST: enterprise trailing-12-month net dollar expansion of 99% (Q2 FY2027 reporting) — the installed base is not expanding spend
- AGAINST: Online segment roughly flat with ~2.9% average monthly churn — low switching costs where Zoom is weakest
- AGAINST: AI monetization still early; rivals bundle comparable AI features free, so AI is currently a retention cost, not yet a pricing lever
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Growth recalibration (written reason): the engine's blended growth is 8.30%, but two blend components are artifacts — OE/share CAGR 2y of 67.75% is SBC-trough arithmetic, not operating growth, and the 12.93% 5-yr revenue CAGR is COVID-era. The revenue signals that mean something: FY2026 revenue +4.36% YoY, Q2 FY2027 revenue +4.9% YoY, FY2027 guided revenue of ~$5.09B vs FY2026 revenue of $4,868,769,000. Scenario starts were therefore set via offsets (−0.15 / −0.083 / −0.033 / +0.017 / +0.067 vs g_base) to −6.7 / 0 / **5** / 10 / 15%. The 5% base start is revenue growth in line with prints plus a modest OE/share tailwind from continued SBC decline and buybacks (TTM diluted shares 300,021,287 vs 307,333,185 for FY2026). The super-bull 15% start is deliberately above any revenue print: it is an OE/share figure, and it requires enterprise acceleration, paid AI attach, and continued SBC/buyback leverage all at once — that is why it only gets 10%. Probabilities 10/25/30/25/10 (defaults); OE multipliers 0.75/0.90/1.00/1.10/1.25 (defaults). Price $95.21.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -6.7% | 0.75 | Teams bundling bites; seats contract, OE shrinks | $16.69 | 4.45% |
| Bear | 25% | 0.0% | 0.90 | Flat OE — revenue creep offset by AI spend and pricing pressure | $26.52 | 5.90% |
| Base | 30% | 5.0% | 1.00 | Mid-single-digit OE/share growth on ~4.5% revenue growth + buyback/SBC tailwind | $36.29 | 7.36% |
| Bull | 25% | 10.0% | 1.10 | Enterprise reacceleration holds; Phone/Contact Center mix lifts OE | $49.08 | 9.20% |
| Super bull | 10% | 15.0% | 1.25 | AI monetizes, expansion rate back above 100%, SBC keeps falling | $68.44 | 11.79% |

- **Probability-weighted: IV@15% $38.30 (−59.8% vs price), IV@12% $50.96, IV@10% $65.10, weighted IRR 7.68%, base-case IRR 7.36%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 4.19%, terminal value 18.9% of IV@15%, scenario spread 4.10x, 8.4 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 8.4 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 FY2027, quoted above.
- **BASE_DIVERGENCE** (latest FY $3.79 vs 3-yr median $2.78): the median is the distorted one — it averages in FY2024, when SBC was still $1,057,161,000. SBC has since fallen to $729,245,000 TTM, and the latest FY and TTM bases agree ($3.79 / $3.99). TTM base used; the median is retained in reporting only.
- **NI_OCF_DIVERGENCE** (2024, 2025): explained by SBC, a non-cash expense added back in OCF — FY2024 net income $637,462,000 vs OCF $1,598,836,000 with SBC of $1,057,161,000; FY2025 net income $1,010,238,000 vs OCF $1,945,308,000 with SBC of $931,309,000 (all from financials_history.csv). The conservative OE deducts SBC explicitly, so the divergence does not inflate the base; if anything it confirms the OE series is the honest one.
- **WIDE_SCENARIO_SPREAD** (4.10x): real — the range runs from Teams-driven contraction to full AI monetization. Confidence is capped at medium, and the verdict is sized to the conservative end.

## My thoughts / overlay
- The engine's balance-sheet line is empty (net_debt_latest: null — Zoom files no debt under the tags read), and the DCF credits none of Zoom's cash. Per Q2 FY2027 reporting, cash, cash equivalents and marketable securities were $7.2B with essentially no debt. That is a real offset the model ignores — but it does not flip the verdict: even the super-bull IV@15% ($68.44) sits well below the $95.21 price before any cash credit, and the cash is a one-time stock, not a growth engine.
- Q2 FY2027 GAAP net income was heavily flattered by a fair-value gain on Zoom's Anthropic stake (reported at ~$1.6B in the quarter). Non-operating and correctly excluded — owner's earnings here are OCF-based, so the windfall never enters the base. Anyone screening ZM on GAAP EPS or on FCF that excludes SBC will see a cheaper stock than this method does; under the sweep's standing rule SBC is a real cost, and at $729M TTM it is the difference between a ~4.2% and a ~6.5% cash yield.
- Quality is not the debate: ~$2.0B TTM operating cash flow on minimal capex, SBC falling in absolute dollars, share count now shrinking (buybacks retired the FY2026 count and a further $1B authorization was added in 2026), RPO growing double digits. The debate is purely price: at $95.21 the market is paying for the bull path plus the cash pile plus the Anthropic stake, and the owner's-earnings stream alone supports none of that.
- Method range: every defensible variant run today lands in Tier D — the preliminary median-base run gave a weighted IRR of 6.84%, the final TTM-base run 7.68%, and even the super-bull scenario alone is 11.79%. There is no input choice within the rules that gets ZM near 15% at this price.
- Hurdle math: the price that clears 15% on the weighted case is the weighted IV@15% itself, **$38.30**; a margin-of-safety entry would need to be below that. The current price is roughly two and a half times that level.

## Final verdict
- **Final tier: D** (weighted IRR 7.68% on the v5 final inputs; no tier override)
- Confidence: **Medium** (high on the TTM base and OE quality; the scenario spread is 4.10x, which caps confidence)
- One-liner: Debt-free cash machine with a moderate, contested moat (5/10) — TTM owner's earnings of $3.99/share are real and growing mid-single-digits, but at $95.21 the weighted IRR is only 7.7% (IV@15% $38.30); it clears Andrew's 15% hurdle only below ~$38.
