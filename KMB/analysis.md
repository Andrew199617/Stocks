# KMB — Kimberly-Clark Corporation
v5 run, 2026-10-14. In scope (market cap $32.774B at $98.36, nasdaq_quote_api — under the $40B cutoff).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed.

## What it is
Consumer staples: Huggies diapers, Kleenex/Scott tissue, Kotex, Depend/Poise, plus K-C Professional (WypAll, Kimtech). Three reported segments — Personal Care, Consumer Tissue, K-C Professional — selling into slow-growth, private-label-exposed categories against P&G and store brands. The company is mid-transformation: it sold its Brazil tissue/K-C Professional business in 2023, is contributing its international tissue/professional business (~$3.3B of 2024 net sales) to a Suzano-controlled joint venture (Suzano 51%, KMB 49%, ~$3.4B valuation, expected to close mid-2026 per the June 2025 announcement), and has agreed to acquire Kenvue in a ~$48.7B cash-and-stock deal announced November 2025 that management said on the Q2 2026 call is on track to close in Q4 2026. The filed history below is therefore a shrinking/restating perimeter, not a like-for-like organic series.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $2,777M; capex $1,138M (tag PaymentsToAcquireProductiveAssets); SBC $140M (always a real cost).
- **Conservative owner's earnings FY2025: $1,499M = $4.50/share** (latest FY OE/share in dcf_numbers.json).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,960M for FY2025 — above the conservative figure, mainly because the maintenance definition caps capex at D&A while FY2025 capex ran well above D&A. The conservative figure is the one used; it charges the actual investment-cycle capex.
- OE positive 5 of the last 5 fiscal years. SBC is small for a company this size ($131–169M/yr across the recent history) — no dilution/SBC-load flag.
- Balance-sheet caveat: the engine's net_debt_latest is $6M and the CSV's long-term-debt column is blank for recent years (the tag was not captured), so the near-zero net debt must NOT be read as "Kimberly-Clark is debt-free" — it only reflects the debt tags the engine captured (current debt $694M vs cash $688M at FY2025). The pending Kenvue deal is also expected to add substantial assumed/financed debt (press coverage of the announcement cited ~$8B of net debt being assumed). No leverage credit is taken in the verdict; if anything the true balance sheet is heavier than the engine shows.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $2,777,000,000 − prior YTD $1,097,000,000 + current YTD $1,653,000,000 = **TTM $3,333,000,000**
- Capex: FY $1,138,000,000 − prior YTD $401,000,000 + current YTD $776,000,000 = **TTM $1,513,000,000**
- SBC: FY $140,000,000 − prior YTD $73,000,000 + current YTD $64,000,000 = **TTM $131,000,000**
- Shares (current-YTD weighted diluted): **333,300,000**
- **TTM OE total $1,689,000,000 → base OE/share $5.07** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $7.07/share — rejected as the base: it is built from lower-capex years (FY2023–24 capex of $766M/$721M vs $1,138M in FY2025 and a $1,513M TTM run-rate, with H1 2026 capex of $776M vs $401M in H1 2025 — an investment cycle that is still running, not a one-year blip) and from a pre-shrink perimeter (the international tissue business being moved into the Suzano JV was still fully consolidated). The latest FY figure ($4.50) is the opposite distortion — it charges peak capex against a trough OCF year. The TTM base sits between them, charges the current elevated capex in full, and is the defensible one. Method range check: the preliminary run on the $7.07 median base produced a weighted IRR of 8.36% (also Tier D), so the tier does not depend on this choice.

## Moat: 6/10 — moderate, real brands in slow categories
Justification: genuine brand equity and shelf scale with demonstrated pricing power, but the categories grow slowly, private label caps pricing, P&G contests every category, and the portfolio is being reshaped by deals rather than compounding organically.
- FOR: Iconic brands (Huggies, Kleenex, Scott, Kotex, Depend) with decades of shelf presence and retailer scale; proven pricing power — 2023 organic sales +5% was driven by ~+6% price with volumes only −2%; essential, non-cyclical demand (people buy diapers and tissue in recessions); scale economies in pulp purchasing, manufacturing and distribution vs smaller rivals; 10th straight quarter of volume growth reported in Q2 2026.
- AGAINST: Categories are structurally low-growth and private label takes share whenever household budgets tighten; P&G is a stronger, larger rival in the core categories (diapers, tissue); organic growth is currently minimal — Q2 2026 net sales +0.6% YoY with organic sales roughly flat, H1 2026 organic +1.2%; a China diaper social-media crisis cut ~140bp from Q2 organic growth and forced a full-year guidance cut (brand trust is a live vulnerability); growth is increasingly deal-bought (Kenvue) rather than organic, with integration and leverage risk attached.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Growth recalibration (written reason): the engine's blended growth is −4.78% (g_base −4.28%), but its components are contaminated by the portfolio reshaping — the revenue CAGRs (−2.99% 5-yr, −6.58% 3-yr) and the −23.52% OE/share CAGR measure divestitures, discontinued-operations restatement and the capex spike, not organic demand. The organic prints are: 2023 organic sales +5%, Q2 2026 sales +0.6% with organic roughly flat, H1 2026 organic +1.2% with volume +1.3%, Q2 2026 adjusted EPS +10.4% on productivity savings (>6% of adjusted COGS) — i.e. flat-to-low-single-digit sales with earnings growing faster than sales while capex stays elevated. Scenario starts were therefore set via offsets (−0.017 / +0.023 / +0.058 / +0.093 / +0.133 vs g_base) to −5.98 / −1.98 / **+1.52** / +5.02 / +9.02%. Sanity check against prints: the base start (+1.5%) sits right on the H1 2026 organic print (+1.2%); the bull/super-bull starts are above current prints, justified only if capex normalizes from the $1,513M TTM run-rate and productivity keeps converting to EPS — they are NOT below what the company just printed, so no growth-cap artifact is present. Probabilities kept at the 10/25/30/25/10 defaults; OE multipliers at the 0.75/0.90/1.00/1.10/1.25 defaults. Price $98.36.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | −5.98% | 0.75 | Private label + China drag persist; capex stays at peak; Kenvue integration stumbles | $21.38 | 4.90% |
| Bear | 25% | −1.98% | 0.90 | Organic sales shrink slowly; elevated capex becomes the new normal | $30.64 | 6.19% |
| Base | 30% | +1.52% | 1.00 | H1 2026 trajectory: ~flat organic sales, productivity offsets capex | $39.78 | 7.51% |
| Bull | 25% | +5.02% | 1.10 | Capex normalizes; volume streak continues; productivity compounds | $51.14 | 9.11% |
| Super bull | 10% | +9.02% | 1.25 | Capex normalizes fast and Kenvue synergies land on the combined base | $69.42 | 11.53% |

- **Probability-weighted: IV@15% $41.46 (−57.85% vs price), IV@12% $54.59, IV@10% $69.19, weighted IRR 7.78%, base-case IRR 7.51%**
- **Tier by numbers: D.** Diagnostics: OE yield 5.15%, terminal value 17.9% of IV@15%, scenario spread 3.25x, net debt 0.00x normalized OE (see the balance-sheet caveat above — the debt tags captured are incomplete), 9.4 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.4 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above.
- **BASE_DIVERGENCE** (latest FY $4.50 vs 3-yr median $7.07): both are distorted in opposite directions — the median uses pre-investment-cycle capex years and a pre-shrink perimeter; the latest FY charges peak capex against a trough OCF year. TTM base ($5.07) used; the median-base run was also Tier D (8.36%), so the verdict is not base-sensitive.
- **NI_OCF_DIVERGENCE** (2023, NI vs OCF >40% apart): the named one-off is in the filing record — Q2 2023 carried a $658M non-cash impairment of intangible assets (plus pension-settlement charges), partly offset by a net benefit from the Brazil tissue/K-C Professional divestiture. Non-cash impairments depress net income but not operating cash flow, which is exactly the observed gap (FY2023 NI $1,764M vs OCF $3,542M in financials_history.csv). The OCF-based conservative OE used throughout is unaffected by the impairment, so the base is not contaminated.

## Thoughts / overlay
- This is a dividend-and-stability stock being screened on a 15% owner's-earnings hurdle, and it fails on arithmetic, not quality: at $98.36 the TTM OE yield is 5.15%, and even the super-bull path (capex normalization + deal synergies) only reaches an 11.53% IRR. No defensible input set clears 15% — the median-base variant gives 8.36% weighted, so the method range is D to D.
- The pending Kenvue close (expected Q4 2026) will change the share count, debt load and earnings mix materially; this DCF is standalone-KMB at today's price and does not capitalize synergies beyond the super-bull case. That is a reason to revisit after close, not a reason to override the tier now.
- Hurdle math: the stock clears a 15% hurdle only at the weighted IV@15% of **$41.46**; even with a margin of safety demanded on top, the entry point is nowhere near $98.36. Verdict sized to the conservative end: **Tier D — a sound, moat-6 staple priced for ~7.8% owner's-earnings returns, roughly half of Andrew's hurdle.**
