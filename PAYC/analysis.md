# PAYC — Paycom Software, Inc.
Pass-1 run, 2026-10-19, engine 5.4.0. In scope: market cap $14.197B at $253.00 (nasdaq_quote_api).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, fundamentals.json or statements.json — none are recomputed.

## What it is
Single-database payroll and human-capital-management (HCM) software for US employers (core market ~50–10,000 employees): payroll (flagship Beti employee-driven payroll), time/attendance, talent, benefits and HR on one record per employee. ~95% recurring revenue. Founder-led (Chad Richison), headquartered in Oklahoma City. Q2 2026 revenue $531M, +10% YoY (recurring +11%); FY2026 guidance is revenue $2.197–2.212B (+7–8%) and adjusted EBITDA $1.007–1.022B (~46% margin at midpoint).

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $678,900,000; capex $270,900,000 (PaymentsToAcquirePropertyPlantAndEquipment — includes the HQ/data-center build and capitalized software); SBC $118,700,000 (always a real cost).
- **Conservative owner's earnings FY2025: $289,300,000 = $5.16/share** (base_oe_latest_per_share in dcf_numbers.json).
- Method note: statements.json carries a separate PaymentsToAcquireIntangibleAssets line — $4,200,000 (FY2023), $4,400,000 (FY2024), $4,500,000 (FY2025) — that the engine's single-tag capex leg does not add to capex (tracked additive-capex-tag backlog item, same family as TXRH/MICC). Counting it would lower FY2025 OE by $4,500,000 (~1.6%) and TTM OE by roughly 1%; the verdict is Tier D on every variant, including the super-bull scenario, so the omission does not affect the tier.
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC, financials_history.csv): $349,000,000 — same ballpark.
- OE positive 5 of the last 5 fiscal years.
- **FY2024 is distorted:** SBC printed **−$22,900,000** because of a $117.5M reversal of previously recognized stock-compensation expense when the 2020 CEO performance award was forfeited on Chad Richison's February 2024 transition to Co-CEO (FY2025 10-K G&A disclosure). Subtracting a negative SBC inflates FY2024 OE to $6.46/share; it is a one-off accounting credit, not run-rate economics. FY2023 OE/share was $2.80.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $678,900,000 − prior YTD $305,000,000 + current YTD $427,600,000 = **TTM $801,500,000**
- Capex: FY $270,900,000 − prior YTD $99,400,000 + current YTD $54,900,000 = **TTM $226,400,000**
- SBC: FY $118,700,000 − prior YTD $60,600,000 + current YTD $31,600,000 = **TTM $89,700,000**
- Shares (current-YTD weighted diluted, ttm.py basis): **48,492,000**
- **TTM OE total $485,400,000 → base OE/share $10.01** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $5.16/share. It is not used as the base: the median year is FY2025 itself, which predates both the H1 2026 operating step-up and the ~20% share-count reduction, so it understates current per-share economics. The TTM figure is used instead, with two cautions stated plainly: (1) ttm.py's denominator is the current-YTD share count (48,492,000), while fundamentals.json's duration-weighted TTM share count (52,213,055) gives TTM OE/share of $9.29 on the same $485,300,000 TTM OE total — the $10.01 base is the generous end; (2) the verdict does not depend on the choice — the preliminary median-base run also produced Tier D (see method range).

**Balance sheet (resolves DEBT_TAGS_BLANK):** at FY2025 year-end Paycom carried **no borrowings** — statements.json shows long-term debt and current portion of long-term debt as none for FY2023–FY2025 (the last filed balance was $29,000,000 total debt in FY2022), against cash of $370,000,000 and operating lease liabilities of $90,300,000 (dcf_numbers.json). The engine's blank net debt means "no debt tag filed," and here that is genuinely a debt-free year-end, not missing leverage. That changed after year-end: to fund buybacks the company drew debt in 2026 — statements.json quarterly balance sheet shows long-term debt of $675,000,000 at Q1 2026 and $900,000,000 at Q2 2026, with cash down to $198,000,000 at 2026-06-30. Separately, the $4,762,500,000 restricted cash in financials_history.csv is funds held for clients (payroll float), not corporate cash. H1 2026 repurchases were $1.39B (fundamentals.json shareholder-yield basis, PaymentsForRepurchaseOfCommonStock YTD fact filed 2026-08-06); shares outstanding fell to 45,071,619 (dei, as of 2026-07-28, dcf_numbers.json) from 56,116,000 diluted shares in FY2025.

## Moat: 6/10 — moderate, economically proven but growth-durability unproven
Justification: ROIC has stayed far above any plausible cost of capital for a decade and gross margin is stable in the low-to-mid 80s, which supports a real franchise; the score is capped at 6 because revenue growth has decelerated from ~30% to high single digits, its own automation (Beti) cannibalized a revenue line it used to charge for, and larger and newer rivals attack from both ends.
- Evidence (fundamentals.json): roic_proxy 30.1% (FY2021), 33.7% (FY2022), 32.3% (FY2023), 41.8% (FY2024 — flattered by the SBC-reversal credit in operating income), 30.5% (FY2025). Gross margin: 84.7% / 84.5% / 83.7% / 82.2% / 83.2% over the same years; TTM gross margin 83.7%.
- FOR: payroll is mission-critical and switching is risky and painful (compliance, tax filing, historical data) — high practical switching costs; single-database architecture (one record per employee, no integrations to break) vs rivals' assembled product families; ~95% recurring revenue; proven pricing power and 30%+ ROIC through a cycle; Beti/IWant automation deepens the workflow lock-in.
- AGAINST: growth decelerated from a 5-yr revenue CAGR of 19.5% to +8.9% latest FY and +7–8% guided — the mid-market land-grab phase is over; Beti automated away corrective-payroll charges, proof a core revenue stream can be disrupted by automation including its own; competition from ADP/Paychex (scale, compliance depth), Workday (enterprise) and Rippling/Gusto (modern UX, IT/finance bundling); opaque per-module pricing and high setup fees are recurring buyer complaints; founder concentration and US/mid-market concentration.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — final run (2026-10-19)
**Growth recalibration (written reason):** the engine's blended start is 18.08%, built from stale signals — 5-yr revenue CAGR 19.52%, 3-yr 14.26%, and an OE/share 2-yr CAGR of 35.55% whose endpoints are the depressed FY2023 print ($2.80/share — peak capex and SBC against $485M OCF) and the stepped-up FY2025 print ($5.16/share), so it describes endpoint recovery, not the current run-rate. The prints that describe the company today are: latest FY revenue YoY +8.95%, TTM revenue YoY +9.2% (fundamentals.json), Q2 2026 revenue +10%, and FY2026 guidance of +7–8%. Scenario starts were therefore set via offsets (−0.1808 / −0.1308 / −0.0808 / −0.0308 / +0.0392 vs g_base) to 0 / 5 / **10** / 15 / 22%: the base start sits on the current revenue print, with per-share OE growth above revenue growth justified only by guided margin expansion (adjusted EBITDA margin ~43% → ~46%) and buyback shrink; bull/super-bull require that buyback-plus-margin engine to keep compounding, and even the super-bull start (22%) is below the endpoint-flattered OE/share CAGR. Probabilities 15/25/30/20/10 (bear side widened for OE_VOLATILE); OE multipliers 0.75/0.90/1.00/1.10/1.25. Price $253.00.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | 0.0% | 0.75 | Growth stalls, buyback ends, Rippling/ADP take share | $55.09 | 5.13% |
| Bear | 25% | 5.0% | 0.90 | Guided growth decays, margins plateau | $82.58 | 6.69% |
| Base | 30% | 10.0% | 1.00 | Current print holds, margin + buyback lift per-share OE | $114.60 | 8.48% |
| Bull | 20% | 15.0% | 1.10 | Automation upsell re-accelerates growth | $157.33 | 10.71% |
| Super bull | 10% | 22.0% | 1.25 | Buyback + margin + re-acceleration all compound | $243.25 | 14.60% |

- **Probability-weighted: IV@15% $119.08 (−52.9% vs price), IV@12% $161.24, weighted IRR 8.77%, base-case IRR 8.48%**
- **Tier by numbers: D.** Bear tier D, bull tier C (TIER_BAND) — sized to the bear end: D. Diagnostics (dcf_numbers.json): OE yield 3.96%, terminal value 20.7% of IV@15%, scenario spread 4.42x, 9.6 months since FY end. Hurdle prices: IV@20% $81.72, IV@25% $61.54. Even the super-bull scenario (14.60% IRR, IV@15 $243.25) does not clear 15% at $253.00.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.6 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above.
- **OE_VOLATILE** (OE/share spans >3x over 5 years): identified, not cyclical — the range is driven by (1) the FY2024 SBC-reversal one-off (+$117.5M credit; FY2024 OE/share $6.46 is not run-rate) and (2) the genuine H1 2026 step-up in OCF plus a ~20% debt-funded share-count cut. Handled with the TTM base (which excludes the FY2024 distortion from the base year), bear-side probability widened to 15/25 on super-bear/bear, and growth starts anchored to revenue prints rather than the endpoint-driven OE/share CAGR.
- **DEBT_TAGS_BLANK** (no debt tag for the latest FY): resolved from the filing in the balance-sheet paragraph above — debt-free at FY2025 year-end (cash $370,000,000, lease liabilities $90,300,000), then $900,000,000 of long-term debt drawn by Q2 2026 to fund buybacks, cash $198,000,000 at 2026-06-30 (statements.json). The leverage verdict is: newly levered for capital return, modest against TTM OE of $485,400,000, but it converts the buyback from balance-sheet slack into a debt obligation.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.42x super-bear IV): real — the outcome hinges on whether per-share compounding from buybacks and margin survives a high-single-digit revenue grower. Confidence is capped at medium and the verdict is sized to the bear end.
- **TIER_BAND** (bear D at 6.69% vs bull C at 10.71%): sized to the bear end — the final tier is D; no scenario, including super-bull, reaches the 15% hurdle at this price, so the band does not change the verdict's direction, only its depth.

## My thoughts / overlay
- The honest headline is the *range*: the preliminary run (median base $5.16/share, engine-blend growth 18.08%) gave weighted IRR 7.26% and IV@15% $85.60; the final run (TTM base $10.01/share, growth recalibrated to current prints) gives 8.77% and $119.08. On fundamentals.json's duration-weighted TTM share count the base would be $9.29/share and the result lower still. Every defensible method lands in Tier D — the disagreement is only about how overvalued, not whether.
- The stock roughly doubled from its spring 2026 lows (~$115–128, where the company itself was buying) to $253.00 after Q2. The buyback arithmetic is real — $1.39B retired ~20% of the shares at prices far below today's — but at $253 the market is paying today for per-share compounding that has already happened, on a business guiding revenue +7–8%.
- Quality is not the debate: 30%+ ROIC for five straight years, ~83% gross margins, ~95% recurring revenue, TTM OE of $485,400,000, guided FCF above $650M for 2026 (company guidance, Q2 2026 release). The debate is purely price: at an OE yield of 3.96% on the generous TTM base, the buyer needs the super-bull path merely to approach a 15% return.
- Risks: growth settling at mid-single digits as Beti-style automation spreads; debt-funded buyback leaves less slack if OCF disappoints; founder/key-man concentration; SBC remains a real ~$90–119M/yr cost outside the FY2024 one-off.

## Final verdict
- **Final tier: D** (weighted IRR 8.77% on the final inputs; method range D on every defensible base)
- Confidence: **Medium** (high on the filing arithmetic and the direction of the verdict; the TTM share-count basis and the buyback's durability keep it from high, and WIDE_SCENARIO_SPREAD caps it)
- One-liner: High-quality HCM franchise, moat 6/10, 30%+ ROIC — but at $253.00 it does not clear 15% on any scenario (weighted IRR 8.77%); it clears 15% only at or below the weighted IV@15% of $119.08.
