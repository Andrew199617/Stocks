# DOCU — Docusign, Inc.
Engine 5.4.0 run, 2026-10-17. Market cap $15.61B at $74.65 (nasdaq_quote_api) — in scope under $40B.

All figures below are copied from dcf_numbers.json, ttm.json, or fundamentals.json — none are recomputed.

## What it is
The e-signature category leader (1.9M+ customers, 180+ countries) pivoting to Intelligent Agreement Management (IAM) — AI-driven agreement drafting, workflow and repository on top of the signing base. Subscription SaaS, ~79% GAAP gross margin, no debt, and an aggressive buyback (diluted shares down 8% YoY in Q2 FY27; $2.1B authorization remaining per the Q2 FY27 call). Growth has decelerated into high single digits: FY26 revenue $3,219.5M (+8.2%), Q2 FY27 revenue $875.7M (+9.4% YoY), FY27 guided to $3,499–3,507M (+9% at midpoint including ~1pp of FX). IAM was 15.1% of ARR at Jul 2026 (12.6% in Q1 FY27, 2.3% in Jan 2025), guided to 18–19% of ARR exiting FY27.

## Owner's earnings
**FY2026 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,165,007,000; capex $106,445,000; SBC $622,321,000 (always a real cost).
- **Conservative owner's earnings FY2026: $436,241,000 = $2.09/share**
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $478,461,000 — same ballpark, raises confidence in the OCF-based figure.
- OE positive 4 of the last 5 fiscal years (negative through FY2023 on the SBC-heavy growth era; the series inflected in FY2024 when OCF roughly doubled).

**Base used = TTM owner's earnings through Q2 FY27 (period ended 2026-07-31), from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,165,007,000 − prior YTD $497,512,000 + current YTD $656,234,000 = **TTM $1,323,729,000**
- Capex: FY $106,445,000 − prior YTD $52,049,000 + current YTD $71,042,000 = **TTM $125,438,000**
- SBC: FY $622,321,000 − prior YTD $306,134,000 + current YTD $289,981,000 = **TTM $606,168,000**
- Shares (current-YTD weighted diluted): **194,763,000** — the buyback is visible here vs 211,878,000 in the prior-year YTD period
- **TTM OE total $592,123,000 → base OE/share $3.04** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $1.47/share — rejected as the base; see BASE_DIVERGENCE under Flags. It remains the conservative reference: on the median base the weighted IRR was 6.0% (preliminary run), so the method range is D either way.

## Moat: 5/10 — moderate / narrow
Justification: category leadership and enterprise workflow embedding are real, but the core signature product is commoditizing and growth has slowed to high single digits.
- FOR: e-signature category leader — 1.9M+ customers across 180+ countries, the default brand for the workflow; enterprise workflow embedding and integrations create real switching friction in regulated, high-volume signing; IAM expands the surface fast (2.3% of ARR in Jan 2025 → 15.1% at Jul 2026, guided 18–19% exiting FY27); stable ~79% GAAP gross margin (FY24 79.3%, FY25 79.1%, FY26 79.4% — fundamentals.json) and ~31% non-GAAP operating margin; no debt and heavy buybacks.
- AGAINST: core e-signature is commoditizing — Adobe Sign, Dropbox Sign, PandaDoc and platform bundles compete on price; revenue growth decelerated from a 17.2% 5-yr CAGR to ~8–9%; SMB/self-serve switching costs are weak and retention has hovered near 100% rather than expanding; IAM/AI agreement tooling is contested by every suite vendor, and the agreement-data advantage is not yet proven durable.
- ROIC evidence (spec-required): the `roic_proxy` series in fundamentals.json is too distorted to carry a wide-moat claim — the invested-capital denominator (equity + debt − cash) was near zero or negative in the early years, printing meaningless values (FY19 −3.49, FY23 0.66). Recent readings improve (FY24 0.075, FY25 0.117, FY26 0.202), but they rise off a buyback-shrunk equity base, not a through-cycle record. That caps the moat at 5.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — engine 5.4.0 final run (2026-10-17)
Growth sanity check: the engine's blended start is 11.56% for OE/share. Revenue prints are lower — FY26 +8.2%, TTM revenue +8.6% (fundamentals.json), Q2 FY27 +9.4%, FY27 guide +9% — but OE/share legitimately grows faster than revenue here: diluted shares fell ~8% YoY on buybacks and SBC is falling as a share of revenue (17% of revenue in Q2 FY27, down 3pp YoY per the call), so an 11.6% OE/share start is supported without recalibration. The 2-yr OE/share CAGR component (27.0%) is flattered by the FY24 inflection and is not extrapolated — the blend's revenue components (5-yr 17.2%, 3-yr 8.6%, latest YoY 8.2%) anchor it. Bull (16.6%) and super-bull (23.6%) starts sit above revenue prints by design: they are OE/share paths that require IAM acceleration plus continued buyback pace, and they are weighted accordingly. Super-bear start −0.4% prices a commoditization stall. Default offsets (−12/−5/0/+5/+12pp) and OE multipliers (0.75/0.90/1.00/1.10/1.25) kept; probabilities shifted to 10/30/30/20/10 (bear widened from 25% to 30%, bull trimmed to 20%) per the OE_VOLATILE flag. Price $74.65.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | −0.4% | 0.75 | Signature commoditization stalls OE; IAM fails to offset | $16.54 | 5.18% |
| Bear | 30% | 6.6% | 0.90 | Revenue grinds at ~7%; buyback only partly offsets | $26.56 | 7.09% |
| Base | 30% | 11.6% | 1.00 | ~9% revenue growth + buyback + SBC discipline, fading over CAP | $36.26 | 8.88% |
| Bull | 20% | 16.6% | 1.10 | IAM re-accelerates ARR; margin leverage continues | $48.92 | 11.07% |
| Super bull | 10% | 23.6% | 1.25 | IAM becomes a second growth engine; OE/share compounds at 20%+ | $73.67 | 14.86% |

- **Probability-weighted: IV@15% $37.65 (−49.6% vs price), IV@12% $50.90, IV@10% $65.77, weighted IRR 9.17%, base-case IRR 8.88%**
- **Tier by numbers: D.** Bear tier D (7.09%), bull tier C (11.07%) — TIER_BAND, verdict sized to the bear end. Diagnostics (dcf_numbers.json): OE yield 4.07%, terminal value 20.5% of IV@15%, scenario spread 4.45x, 8.5 months since FY end.
- **Hurdle prices:** clears 15% only at or below $37.65; 20% at $25.88; 25% at $19.50. Even the super-bull scenario (10%) tops out at a 14.86% IRR at this price — no scenario clears the 15% hurdle at $74.65.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 8.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 FY27 (2026-07-31), legs quoted above.
- **BASE_DIVERGENCE** (latest FY $2.09 vs 3-yr median $1.47): the median is the distorted one. The 3-yr window (FY24 $1.29, FY25 $1.47, FY26 $2.09) sits on the SBC-heavy era's tail; since then OCF has grown (FY26 $1,165.0M, TTM $1,323.7M), SBC has flattened in dollars (FY26 $622.3M, TTM $606.2M) and fallen as a share of revenue, and buybacks cut the diluted count from 211.9M (prior YTD) to 194.8M (current YTD). The TTM base ($3.04) is the current run-rate; the median is retained as the conservative reference and the verdict is D on both.
- **OE_VOLATILE** (OE/share spans >3x over 5 years): real — it is the SBC-era-to-cash-compounder inflection (negative OE through FY23, $1.29 → $1.47 → $2.09 → $3.04 TTM), not cyclicality. Handled by widening the bear weight to 30% and trimming bull to 20%.
- **NI_OCF_DIVERGENCE** (2024, 2026): explained — SBC is the bridge. FY24 net income $74.0M vs OCF $979.5M, with SBC of $616.8M added back in OCF; FY26 net income $309.1M vs OCF $1,165.0M, with SBC of $622.3M. FY25 net income ($1,067.9M) was itself flattered by a −$819.9M tax benefit (valuation-allowance release; tax column in financials_history.csv). Net income is the unreliable series in all three years; the OCF-based conservative OE used throughout is unaffected.
- **DEBT_TAGS_BLANK** (no debt tag in the latest FY — net debt unknown to the engine): resolved from the filing record and the Q2 FY27 earnings call (CFO, Sep 2026): "We have no debt on the balance sheet," ending the quarter with just under $1B of cash, cash equivalents and investments. FY26 10-K (financials_history.csv): cash $602,442,000, total liabilities $2,311,730,000 against assets $4,229,550,000 — the liabilities are predominantly deferred revenue and operating leases (lease liabilities $185,119,000), not borrowings. Net cash, no leverage verdict needed.
- **SHARES_FALLBACK** (no diluted count filed for 2018, 2019): noted — those history years use the outstanding count (shares_tag FALLBACK in financials_history.csv); per-share history there is approximate and neither year enters the base or the blend's binding components.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.45x super-bear): real — the range is driven by whether IAM re-accelerates OE/share growth. Confidence capped at medium; verdict sized to the bear end.
- **TIER_BAND** (bear D vs bull C): the verdict spans tiers; sized to the bear end — D.
- Preliminary-run flag **LOW_OE_YIELD** (2.0% on the median base) cleared on the TTM base: OE yield is now 4.07%.

## My thoughts / overlay
- The method range is narrow for once: median base gives a 6.0% weighted IRR, TTM base 9.2% — Tier D on both, and even the super-bull path (23.6% OE/share growth start, 1.25x OE) only reaches a 14.86% IRR at $74.65. The stock is priced for the IAM re-acceleration to already be happening.
- The business quality is not the problem: ~79% gross margin, ~31% non-GAAP operating margin, no debt, ~$1B cash and investments, FCF over $1B TTM, and a buyback shrinking the count ~8%/yr. The problem is arithmetic: at $74.65 the price sits at roughly double the weighted IV@15% ($37.65) for a company growing revenue at ~9%.
- What would change the answer: a price near $37.65 (the 15% hurdle price on the weighted case), or IAM pushing revenue growth durably back into the teens — watch ARR growth (guided 8.5–9.0% for FY27) and the IAM share of ARR (15.1% and rising) as the two tells.
- SBC discipline is the quiet swing factor: SBC was $622.3M in FY26 (19% of revenue) and is guided down as a share of revenue; if that stalls, the conservative OE base stalls with it, because SBC is charged in full here.

## Final verdict
- **Final tier: D** (weighted IRR 9.17% on the TTM base; Tier D on the median base too — method range D to D, bull case only reaches C)
- Confidence: **Medium** (filing-direct TTM base and a verdict that holds in every scenario, capped from high by the 4.45x scenario spread)
- One-liner: Durable cash compounder with a narrow moat (5/10) — even on the current TTM base of $3.04/sh, weighted IRR is only 9.2% at $74.65 and no scenario clears 15%; it clears the 15% hurdle only under ~$37.65.
