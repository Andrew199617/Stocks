# ED — Consolidated Edison, Inc.
v5 run, 2026-10-14 (supersedes the 2026-10-13 v4-era analysis; the v5 engine now reads the `PaymentsForConstructionInProcess` capex tag itself, FY2023–25, so the capex that v4 zero-filled is in the numbers). In scope (market cap $38.675B at $107.82, nasdaq_quote_api — just under the $40B cutoff).

All figures below are copied from dcf_numbers.json or financials_history.csv — none are recomputed.

## What it is
Regulated energy-delivery utility: CECONY provides electric, gas, and steam service in New York City and Westchester County; Orange & Rockland serves southeastern NY / northern NJ / northeastern PA; plus Con Edison Transmission. Almost entirely rate-regulated — earnings are set by rate cases, not by the market. 52 consecutive years of dividend increases; FY2026 adjusted EPS guidance $6.00–$6.20 (company guidance, via search results); average rate base ~$47.3B at Q2 2026 and guided to compound ~8.7%/yr over five years on a ~$38B grid buildout (electrification, resilience, reliability).

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $17,049M; net income $2,023M; operating cash flow $4,800M; capex $4,764M (tag: PaymentsForConstructionInProcess, FY2023–25); SBC $55M (tag: AllocatedShareBasedCompensationExpense — trivial for a utility, but filed and counted).
- **Conservative owner's earnings FY2025: −$19M = −$0.05/share** (OCF − capex − SBC). Capex consumes essentially all of operating cash flow — that is the structural fact of this business, not a one-off year.
- **OE positive 0 of the last 5 fiscal years** on the conservative definition (FY2021–25 all negative: −$1,266M / −$594M / −$2,250M / −$1,191M / −$19M, from financials_history.csv).
- Maintenance version FY2025 (NI + D&A − min(capex, D&A) − ΔNWC): **+$2,173M** — positive because it caps capex at D&A ($2,321M). The gap between the two definitions IS the story: for a growing regulated utility, most capex is growth capex that enters rate base and earns an allowed return, so the maintenance definition is arguably the fairer one — but the sweep's base case is the conservative definition, and on it there is no owner's earnings to discount.
- **Base used = the engine's normalized base (median of last 3 FY OE/share): −$3.43/share** (latest FY alone: −$0.05/share). Both are ≤ 0, so the choice does not change the verdict. No TTM base was used — see STALE_FY below.
- Balance sheet: net debt $24,172M (dcf_numbers.json) against equity of $24,190M (FY2025, financials_history.csv) — a levered regulated balance sheet, funded continuously with debt and new equity.

## Moat: 6/10 — strong franchise, capped economics
Justification: an exclusive regulated delivery franchise in New York City is about as durable a position as exists — nobody builds a competing grid — but the regulator sets the return (9.4% allowed ROE in CECONY's 2026 electric/gas plans, 48% equity ratio), so durability does not convert into excess returns, and a new NY affordability law caps rate-case increases below inflation.
- FOR: exclusive franchise monopoly for electric/gas/steam delivery in NYC and Westchester — no competitor can replicate the network; essential service with inelastic demand; rate base compounding ~8.7%/yr guided on a ~$38B capital program, with capex recovered through rates plus an allowed return; 52 straight years of dividend growth through multiple cycles and regulators.
- AGAINST: returns are capped by the regulator, not set by pricing power — allowed ROE 9.4% is a ceiling, and NY's affordability law now requires rate-case proposals to keep bill increases below inflation (the 2026–28 plan settled far below the initial request); perpetual external funding — up to $1.1B of new common equity guided for 2026, ~$1.2B for 2027, ~$3.3B for 2028–30 — dilutes per-share compounding (management guides adjusted EPS growth of only 6–7% vs ~8.7% rate-base growth); heavy leverage (net debt $24,172M) and constant refinancing needs; long-run gas/steam transition and electrification-policy risk sits with the PSC, not the company.
- A 6 gives CAP = 9.8 years — academic here, since there is no positive OE stream to fade.

## DCF — v5 final run (2026-10-14)
The final engine pass was run with moat 6 and default probabilities 10/25/30/25/10 (offsets −12/−5/0/+5/+12pp, multipliers 0.75/0.90/1.00/1.10/1.25), but **the engine emits no scenario table, IV, or IRR: the normalized base OE is −$3.43/share, so there is no positive owner's-earnings path to discount at any scenario weighting.** Tier by numbers: **F**.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | n/a | 0.75 | Adverse rate cases, affordability caps bite | n/a — negative base | n/a |
| Bear | 25% | n/a | 0.90 | Capex stays at/above OCF, equity issuance accelerates | n/a — negative base | n/a |
| Base | 30% | n/a | 1.00 | Capex ≈ OCF indefinitely; OE ≈ 0 | n/a — negative base | n/a |
| Bull | 25% | n/a | 1.10 | Rate-base growth converts to FCF sooner than history suggests | n/a — negative base | n/a |
| Super bull | 10% | n/a | 1.25 | Structural FCF inflection | n/a — negative base | n/a |

- **Probability-weighted IV/IRR: not computable (negative base). Tier by numbers: F.**
- Sanity check on growth inputs: the engine's blended growth is 7.23% (rev CAGR 5y 7.23%, 3y 3.33%, latest YoY +10.21%) — reasonable against actual prints (Q2 2026 revenue +13.2% YoY per search results; FY2026 EPS guided $6.00–$6.20), but growth is irrelevant to the verdict: it multiplies a negative base.
- Recent prints (search results, for the record): Q2 2026 EPS $0.83 vs $0.67 a year earlier, revenue $4,069M; H1 2026 net income $1,232M. The earnings engine is healthy — it is the capex load, not profitability, that zeroes out conservative OE.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 2025-12-31, 9 months ago): ttm.py was run and **exited non-zero**: "ttm.py: cannot compute TTM for ED (CIK 1047862): sbc: no post-FY YTD fact (no 10-Q since the 2025-12-31 fiscal year end)" — ED's 10-Q facts do not give ttm.py a usable post-FY YTD SBC leg, so no TTM base exists. Per the sweep rules, the engine's median base (−$3.43/share) is used instead, with the reason stated here. This does not change the outcome: the latest full FY is also ≤ 0 (−$0.05/share), and Q1/Q2 2026 earnings prints give no indication capex has fallen below OCF.
- **NI_OCF_DIVERGENCE** (2025: net income $2,023M vs OCF $4,800M): explained, not a one-off — the gap is the standard utility non-cash addback pattern, dominated by D&A of $2,321M (financials_history.csv), which is subtracted to reach net income but added back in operating cash flow. No tax deposit, impairment, or working-capital one-off is needed to explain it, and the conservative OE series is OCF-based throughout, so the divergence does not contaminate the base.
- **SECTOR_MODEL_MISMATCH** (Utilities): accepted in full — the OE/capex DCF fits regulated utilities poorly, because growth capex is rate-base investment earning a regulated return, not value destruction. Confidence is graded **low** and the tier is read as "not modelable on this screen," not as "bad business." The maintenance-OE definition (+$2,173M in FY2025) is the standing evidence of the mismatch.

## My thoughts / overlay
- This is the model's known blind spot, flagged as such: ED is a profitable, dividend-growing regulated monopoly whose conservative owner's earnings are negative across the filed history pulled (0 of the last 5 years positive) because grid capex runs at or above operating cash flow every year. The dividend is funded the utility way — rate recovery plus continuous debt and equity issuance — which an OE screen reads as zero distributable cash.
- On numbers a utility investor actually uses (from search results, not the engine): FY2026 adjusted EPS guided $6.00–$6.20 at a $107.82 price, allowed ROE 9.4%, rate base guided to compound ~8.7%, EPS guided to compound 6–7% after dilution. That is a bond-like mid-single-digit equity return profile before any multiple change — nowhere near Andrew's 15% hurdle on any defensible reading, so the F here happens to agree with the hurdle conclusion even though the model's mechanism (negative OE) is a sector artifact.
- Hurdle-clearing price: not computable from this model — with no positive OE base there is no IV@15% at any price, and stating one would require a different model (dividend/rate-base), which is out of scope for this sweep. No tier override: the numbers tier F is retained, with the mismatch documented, rather than inventing a tier the method cannot support.
- Real risks for a holder (outside the model): NY regulatory affordability politics capping allowed bill growth below inflation, the size of the equity-issuance program diluting per-share growth, and leverage (net debt $24,172M) refinanced at current rates.

## Final verdict
- **Final tier: F** (tier by numbers F — no positive normalized conservative owner's earnings; OE DCF not supportable)
- Confidence: **Low** (sector-model mismatch: the F is a model artifact for a regulated utility, though no alternative reading clears a 15% hurdle either)
- One-liner: Durable regulated NYC franchise, moat 6/10, but conservative owner's earnings are negative 0 of the last 5 years (capex ≈ all of OCF) — Tier F on this screen; a bond-like ~6–7% guided EPS compounder that does not clear 15% on any reading.
