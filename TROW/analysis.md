# TROW — T. Rowe Price Group, Inc.
v5 run, 2026-10-15. In scope (market cap $22.358B at $101.49, nasdaq_quote_api — under the $40B cutoff).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed.

## What it is
Large active asset manager: mutual funds, target-date / retirement products (roughly two-thirds of AUM is retirement-related), fixed income, multi-asset, and a fast-growing active-ETF and SMA shelf. Revenue is overwhelmingly investment advisory fees charged as a percentage of AUM, so earnings are a leveraged play on market levels. Record AUM of $1.89 trillion at Q2 2026 (search result, Q2 2026 earnings release) — but the level is market appreciation, not client demand: net outflows were $6.5B in Q2 2026, $56.9B for full-year 2025, and a reported $28.3B in Q3 2026, concentrated in active equity.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,753,400,000; capex $274,200,000 (tag PaymentsToAcquirePropertyPlantAndEquipment); SBC $216,900,000 (tag ShareBasedCompensation — always a real cost).
- **Conservative owner's earnings FY2025: $1,262,300,000 = $5.73/share** (latest FY OE/share, key_numbers.md).
- Maintenance version: not computable — the engine found no D&A tag and no current-asset/liability series for this filer (used_tags da / assets_current / liab_current are null, oe_maintenance column blank), so only the conservative definition is available. For an asset manager this is the less damaging gap: capex is a small leg next to OCF (TTM capex $258,400,000 vs TTM OCF $1,932,200,000, ttm.py output).
- OE positive 5 of the last 5 fiscal years, but the totals swing with the market cycle: $2,938,300,000 (FY2021) → $1,836,400,000 (FY2022) → $645,600,000 (FY2023) → $1,014,900,000 (FY2024) → $1,262,300,000 (FY2025), all from financials_history.csv.
- Balance sheet: cash $3,378,200,000 at FY2025 (financials_history.csv) and no debt series under the engine's tags (net_debt_latest is null in dcf_numbers.json) — effectively a debt-free, cash-rich balance sheet, which supports the dividend/buyback but does not fix the fee-AUM math below.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,753,400,000 − prior YTD $1,162,800,000 + current YTD $1,341,600,000 = **TTM $1,932,200,000**
- Capex: FY $274,200,000 − prior YTD $144,200,000 + current YTD $128,400,000 = **TTM $258,400,000**
- SBC: FY $216,900,000 − prior YTD $96,900,000 + current YTD $89,800,000 = **TTM $209,800,000**
- Shares (current-YTD weighted diluted): **215,900,000**
- **TTM OE total $1,464,000,000 → base OE/share $6.78** (base_source: ttm_json)
- The engine's normalized base (median of last 3 FY OE/share) is $4.55/share. The TTM base was used because FY2023's $2.87/share-equivalent year (OE total $645,600,000, the OCF-dip year flagged under NI_OCF_DIVERGENCE) drags the median below both the latest FY ($5.73) and the current run-rate; the median-base result is kept as the conservative end of the method range below.

## Moat: 5/10 — moderate / narrow
Justification: scale, brand, and a sticky retirement/target-date franchise are real, but the core product — fundamental active equity — is in structural outflow against passive, and the effective fee rate is compressing (38.1 bps in Q2 2026 vs 39.6 bps a year earlier, per search results). Pricing power is negative, not positive.
- FOR: $1.89T AUM scale and an 85+ year brand in US retirement channels; target-date / defined-contribution placement is sticky — retirement assets are roughly two-thirds of AUM and turn over slowly; debt-free, cash-rich balance sheet funds buybacks (share count −1.01%/yr, share_cagr in dcf_numbers.json) through drawdowns; ETF/SMA and alternatives build-out plus the Goldman Sachs partnership are gaining flows inside a shrinking core.
- AGAINST: persistent net outflows ($56.9B in 2025; $6.5B in Q2 2026; a reported $28.3B in Q3 2026), concentrated in the highest-fee active equity book; structural shift to passive/index undercuts the core product with no network effect to stop it; fee-rate compression from mix shift to lower-fee vehicles (38.1 bps and falling); rising technology and distribution costs squeezing margins (Q2 2026 operating expenses +9.8% YoY, search results); revenue is a percentage of market levels, so a bear market cuts OE mechanically — no moat against the tape.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Growth inputs: engine blended growth 3.71% (rev CAGR 5y 3.34%, rev CAGR 3y 4.08%, latest rev YoY 3.12%, OE/share CAGR 2y 41.22% — the last is a rebound artifact off the depressed FY2023 base and is not a trend), plus +1.01pp buyback adjustment = g_base 4.72%. Default offsets kept (−12/−5/0/+5/+12pp). Probabilities skewed one notch bearish vs default (bear 30%, bull 20%) on the outflow/fee evidence; OE multipliers at defaults.
Sanity check vs actual prints: FY2025 revenue grew +3.12% and Q2 2026 revenue grew +10.7% YoY on market-lifted average AUM (average AUM +15.7% YoY in Q2 2026, search results). Base start 4.72% sits between the FY print and the market-driven Q2 print — reasonable with outflows and fee compression offsetting market lift. Bull 9.72% ≈ the Q2 print. Super-bull 16.72% exceeds any recent revenue print and is only defensible as a sustained-equity-bull-market AUM scenario at 10% weight — flagged as such, not as a company-execution scenario. Bear/super-bear starts (−0.28% / −7.28%) model the mechanical AUM-fee hit of flat-to-down markets.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -7.28% | 0.75 | Market drawdown cuts AUM and fees; outflows accelerate | $27.68 | 5.56% |
| Bear | 30% | -0.28% | 0.90 | Flat markets, outflows and fee compression grind OE sideways-down | $44.56 | 7.88% |
| Base | 30% | 4.72% | 1.00 | Modest market growth offsets outflows; buybacks shrink the count | $60.97 | 10.09% |
| Bull | 20% | 9.72% | 1.10 | Q2 2026-style market lift persists; ETF/SMA flows scale | $82.47 | 12.79% |
| Super bull | 10% | 16.72% | 1.25 | Sustained bull market inflates fee-bearing AUM | $124.76 | 17.48% |

- **Probability-weighted: IV@15% $63.40 (−37.53% vs price), IV@12% $84.30, IV@10% $107.64, weighted IRR 10.44%, base-case IRR 10.09%**
- **Tier by numbers: C.** Diagnostics (key_numbers.md): OE yield 6.68%, terminal value 18.83% of IV@15%, scenario spread 4.51x, 9.46 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.46 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above.
- **OE_VOLATILE** (OE/share range >3x over the last 5 years): real and structural, not an artifact — OE totals run $645,600,000 (FY2023) to $2,938,300,000 (FY2021) because fees ride market levels and OCF dipped in 2023. Handled by raising the bear weight to 30%, keeping the median-base result in the method range, and capping the verdict at the conservative end.
- **NI_OCF_DIVERGENCE** (2023): FY2023 net income was $1,788,700,000 against OCF of $1,219,100,000 (financials_history.csv) — the same pattern as FY2016-17, when OCF printed far below net income; for this filer OCF carries consolidated-investment-product and working-capital swings that net income does not. Resolution: the conservative OE series is built directly on the lower OCF figure, so the divergence makes the base conservative rather than inflated; no adjustment taken.
- **SECTOR_MODEL_MISMATCH** (Finance): agreed — an asset manager's "capex" is mostly premises/technology and its OE is really fee income minus comp, so the standardized OE/capex DCF is a rough screen here. Confidence graded **low** per the flag, and no tier override taken on the strength of the model.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.51x super-bear IV): real — the outcome is dominated by future market levels, which no analysis pins down. Confidence is not high; verdict sized to the conservative end.

## My thoughts / overlay
- The honest headline is the method range: the preliminary median-base run (default probabilities) printed weighted IRR 8.05% / IV@15% $43.76 (Tier D); the final TTM-base run prints 10.44% / $63.40 (Tier C). Both sit far below the $101.49 price — the disagreement is about how bad, not whether the hurdle is cleared.
- Quality is not the debate: debt-free, cash-rich, 5/5 positive OE years, durable dividend-and-buyback machine. The debate is price vs a fee stream that shrinks organically (outflows every recent period, fee rate 38.1 bps and compressing) and only grows when markets bail it out.
- Q3 2026's reported $28.3B outflow quarter, after the TTM window, points the near-term flow trend the wrong way; the next catalyst is the late-October 2026 earnings print on flows, pricing, and expense guidance.
- Hurdle math: the weighted IV@15% is $63.40 — that is the price at which the weighted case clears 15%. At $101.49 a buyer is paying for the bull/super-bull market path (combined 30% weight) and still only reaching a 10.44% weighted IRR.

## Final verdict
- **Final tier: C** (weighted IRR 10.44% on the v5 final inputs; method range D to C across defensible bases)
- Confidence: **Low** (sector-model mismatch on a finance name, plus a 4.51x scenario spread driven by unmodelable market levels)
- One-liner: High-quality, debt-free retirement-franchise asset manager, moat 5/10 — but structural outflows and fee compression mean it does not clear 15% at $101.49 (weighted IRR 10.4%, IV@15% $63.40); it clears the hurdle only at or below ~$63.40.
