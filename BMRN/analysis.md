# BMRN — BioMarin Pharmaceutical Inc
Pass-1 run, 2026-10-19, engine 5.4.0. All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json or fundamentals.json — none are recomputed.

## What it is
Rare-disease biotech (SIC 2834, Pharmaceutical Preparations): eight approved therapies for genetic / metabolic conditions — Voxzogo (achondroplasia), Palynziq and Kuvan (PKU), Vimizim, Naglazyme, Aldurazyme (enzyme therapies), Brineura, and Roctavian (hemophilia gene therapy). Closed the acquisition of Amicus Therapeutics on April 27, 2026 (Q2 2026 reporting), adding Galafold and Pombiliti + Opfolda. FY2025 revenue $3,221,253,000 (financials_history.csv), up 12.87% YoY (key_numbers.md). Q2 2026 total revenue was $990M, +20% YoY, helped by the first Amicus contribution, Voxzogo patient additions and Palynziq demand; management raised 2026 revenue, Voxzogo (~$1B low end) and non-GAAP EPS guidance (Q2 2026 results reporting, cited in research).

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $827,994,000; capex $103,038,000; SBC $181,409,000 (always a real cost).
- **Conservative owner's earnings FY2025: $543,547,000 = $2.75/share** (key_numbers.md: latest FY OE/share $2.75)
- Maintenance version: $148,718,000 on the filed history — far below the conservative figure because it charges the full change in net working capital; the conservative OCF-based figure is the one used throughout.
- OE positive 3 of the last 5 fiscal years (key_numbers.md): FY2023 OE/share -$0.75, FY2024 $1.45, FY2025 $2.75 — a genuine inflection from losses to cash generation, not a one-year spike: the TTM below confirms it.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct):**
- OCF: FY $827,994,000 − prior YTD $359,665,000 + current YTD $388,760,000 = **TTM $857,089,000**
- Capex: FY $103,038,000 − prior YTD $33,869,000 + current YTD $49,739,000 = **TTM $118,908,000**
- SBC: FY $181,409,000 − prior YTD $85,231,000 + current YTD $119,152,000 = **TTM $215,330,000**
- Shares (current-YTD weighted diluted): **194,147,000**
- **TTM OE total $522,851,000 → base OE/share $2.69** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $1.45/share — rejected as the base: the median year is FY2024 and the window still contains loss-year FY2023 (-$0.75/share), so the median is the distorted figure (see BASE_DIVERGENCE). It is retained in key_numbers.md for the method range below.
- TTM caveat: the Amicus deal closed April 27, 2026, so the TTM legs contain only ~2 months of Amicus contribution and essentially none of its cost synergy (cited ~$220M non-GAAP, fully realized 2028) — the TTM base is, if anything, understated on earnings and (see DEBT_TAGS_BLANK) the FY2025 balance sheet badly understates post-deal leverage. Both effects are named, neither is hand-adjusted.

## Moat: 6/10 — narrow-to-moderate
Justification: orphan-drug exclusivity and a global rare-disease commercial machine give real pricing power, but the measured returns on capital do not yet support a wide or strong score.
- FOR: Orphan-drug exclusivity (7y US / 10y EU) and patent protection across eight approved therapies; Galafold exclusivity extended to 2037 via the Amicus deal. Global commercial infrastructure in 75+ countries — reimbursement and specialist-channel scale smaller rivals cannot replicate. Proven pricing power: gross margin 77.7% in FY2025 (fundamentals.json; range 71.8%–81.2% over the last decade). Diversifying installed base: Voxzogo heading to ~$1B, Palynziq +27% YoY in Q2 2026, plus Galafold / Pombiliti + Opfolda with combined peak potential cited at $2.6B.
- AGAINST: ROIC history is the binding constraint — roic_proxy (fundamentals.json) was negative from 2016 through 2021, 3.9% in 2022 and 2023, 8.1% in 2024 and 6.2% in 2025: heavy R&D has not earned the cost of capital through a cycle, so per the rubric a 7+ is not justified. Voxzogo faced its first U.S. competitor in 2026 (~90% of U.S. children remained on therapy through July 2026 — retention held, share of new starts is the open question). Roctavian's commercial disappointment shows the gene-therapy leg is not a moat. IRA / U.S. pricing pressure and government-order timing outside the U.S. (Vimizim, Naglazyme) add policy and concentration risk.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — final run (2026-10-19)
Growth sanity check: the engine blend is 11.41% (rev CAGR 5y 11.61%, 3y 15.40%, latest rev YoY 12.87%, share-count adj −1.47%). Q2 2026 printed +20% revenue YoY, but that print contains the first-time Amicus consolidation — it is not a repeatable organic rate, which is the written reason the bull start (16.4%) and base start (11.4%) sit below it; against organic prints (FY2025 +12.87%, Voxzogo +14%, Palynziq +27% in Q2) the starts are in line. Probabilities were shifted to 15/25/30/20/10 (from the 10/25/30/25/10 default) per the OE_VOLATILE instruction to widen bear weight, and because post-Amicus leverage and Voxzogo competition are live downside paths. Default offsets (−12/−5/0/+5/+12pp) and OE multipliers (0.75/0.90/1.00/1.10/1.25) retained. Price $54.68.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -0.6% | 0.75 | Voxzogo loses new starts to the new competitor; synergies slip; pricing pressure | $14.43 | 5.67% |
| Bear | 25% | 6.4% | 0.90 | Organic growth halves; Amicus integration costs linger | $23.65 | 8.08% |
| Base | 30% | 11.4% | 1.00 | Current organic trajectory decays over the CAP | $32.81 | 10.34% |
| Bull | 20% | 16.4% | 1.10 | Voxzogo holds share, Amicus annualized, synergies land | $45.03 | 13.06% |
| Super bull | 10% | 23.4% | 1.25 | Full Amicus peak trajectory plus label expansions (hypochondroplasia) | $69.58 | 17.68% |

- **Probability-weighted: IV@15% $33.89 (−38.0% vs price), IV@12% $46.05, IV@10% $59.76, weighted IRR 10.63%, base-case IRR 10.34%**
- **Tier by numbers: C.** IRR band: bear 8.08% (tier D) → bull 13.06% (tier C). Hurdle-clearing prices (weighted): 15% at $33.89, 20% at $23.13, 25% at $17.34.
- Diagnostics (key_numbers.md): OE yield 4.93%, terminal value 21.1% of IV@15%, scenario spread 4.82x, 9.6 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.6 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above.
- **BASE_DIVERGENCE** (latest FY $2.75 vs 3-yr median $1.45): the median is the distorted one — its window (FY2023 −$0.75, FY2024 $1.45, FY2025 $2.75) averages a loss year from before the inflection. Latest FY and TTM ($2.69) agree, so the TTM base is used; the median run is kept as the method-range low end.
- **OE_VOLATILE** (OE/share spans >3x over 5 years): real — it is an inflection from losses (FY2023 −$0.75/share) to strong positive OE, not mid-cycle noise. Handled by the TTM base plus bear-side probabilities raised to 40% combined (super bear 15% + bear 25%).
- **NI_OCF_DIVERGENCE** (2025: net income $348,901,000 vs OCF $827,994,000): the gap is non-cash addbacks in the filed cash-flow statement — SBC $181,409,000 and depreciation & amortization $79,557,000 alone account for $260,966,000 of the $479,093,000 difference (all figures financials_history.csv), with the balance in other non-cash and working-capital items. No tax-deposit or impairment one-off was found in the computed outputs. The OCF-based conservative OE already deducts SBC in full, so the divergence does not inflate the base.
- **DEBT_TAGS_BLANK** (engine found no debt tag; net debt unknown, NOT zero): from the FY2025 10-K (Note 10, Debt), the company carried $600.0M principal of 1.250% convertible notes due May 2027, carrying value $597,176,000, against cash and equivalents of $1,311,679,000 plus marketable securities of $248,930,000 short-term and $492,242,000 long-term (10-K balance-sheet reporting) — net cash pre-deal. That picture is stale in the other direction: the Amicus acquisition closed April 27, 2026 and its pro forma balance sheet (8-K/A, July 2026) shows long-term debt of $4,132,122,000 and cash of $547,423,000; Q2 2026 reporting cites total debt of ~$4.2B against cash of $874,005,000 (10-Q, June 30, 2026) with a target of gross leverage below 2.5x by mid-2027. The engine's enterprise-value math carries no net-debt figure for this name; treat the equity IVs as computed and the leverage as a post-deal risk overlay, not as zero debt.
- **WIDE_SCENARIO_SPREAD** (4.82x): real — outcomes genuinely range from competitive erosion to full Amicus delivery. Confidence is capped at medium and the verdict is sized to the conservative (bear) end.
- **TIER_BAND** (bear D at 8.08% vs bull C at 13.06%): the verdict is sized to the bear end — even the bull case only reaches Tier C, so no sizing case above C exists on these inputs.

## My thoughts / overlay
- Method range is the honest headline alongside the tier: on the engine's median base ($1.45/share) the preliminary run gave weighted IRR 7.07% and IV@15% $18.41 (Tier D); on the TTM base ($2.69/share) the final gives 10.63% and $33.89 (Tier C). Both bases are filing-derived; the TTM is preferred because FY2025 and the TTM agree and the median averages in a pre-inflection loss year.
- Quality vs price are separate questions. The business has inflected: revenue CAGR 15.40% over 3 years, OCF $857,089,000 TTM, SBC a real and rising cost ($215,330,000 TTM — deducted in full). What the price asks is the problem: at $54.68 the market is paying well above even the bull scenario's IV@15% of $45.03; only the 10%-weighted super bull ($69.58) clears the price at a 15% discount rate.
- Watch items: Voxzogo share of new U.S. starts against the new competitor, Amicus synergy delivery (~$220M cited, by 2028) against the new ~$4.2B debt load, the May 2027 convertible maturity, and whether ROIC can push durably above the cost of capital — that is what would earn a higher moat and a longer fade.

## Final verdict
- **Final tier: C** (weighted IRR 10.63% on the TTM base; method range D to C)
- Confidence: **Medium** (filing-direct TTM base and resolved flags; capped by the 4.82x scenario spread and the post-Amicus basis change still flowing through the TTM)
- One-liner: Real rare-disease franchise, moat 6/10, now genuinely cash-generative on a TTM base — but at $54.68 it does not clear 15%: weighted IRR 10.6%, weighted IV@15% $33.89; it clears 15% only below ~$33.89.
