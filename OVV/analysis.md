# OVV — Ovintiv Inc.
v5 run, 2026-10-16. In scope (market cap $17.182B at $66.16, nasdaq_quote_api, key_numbers.md).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed. Post-FY2025 company-reported figures are from the company's Q1/Q2 2026 earnings releases (search results), labelled as such where used.

## What it is
North American oil and gas E&P, now concentrated in two plays after a 2026 portfolio swap: the Permian (Midland Basin) and the condensate-rich Alberta Montney. It closed the NuVista Energy acquisition on February 3, 2026 (cash and stock, ~$2.7B; ~100 MBOE/d, ~930 net well locations, ~140,000 net acres adjacent to its existing Montney position) and closed the sale of its Anadarko assets on April 9, 2026 (~$2.82B cash proceeds; ~360,000 net acres, per the Q2 2026 release). Q2 2026 production was 615 MBOE/d (206 Mbbls/d oil and condensate); full-year 2026 guidance is 630–645 MBOE/d on unchanged capital of $2.25–$2.35B, with ~4% oil production growth per share (company release).

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $3,652,000,000; capex $2,147,000,000; SBC $57,000,000 (AllocatedShareBasedCompensationExpense — small, always deducted as a real cost).
- **Conservative owner's earnings FY2025: $1,448,000,000 = $5.58/share** (key_numbers.md: latest FY OE/share $5.58, latest FY OE total $1.448B)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,017,000,000 — below the conservative figure, mainly because capex runs close to D&A in a shale business where drilling is what holds production flat; the conservative OCF-based figure is the one used throughout.
- OE positive 5 of the last 5 fiscal years. Conservative OE totals were remarkably flat across the last three filed years ($1,376,000,000 in 2023, $1,352,000,000 in 2024, $1,448,000,000 in 2025) even as revenue fell — cost and mix, not growth.
- Net debt (latest, FY2025 balance sheet): $5.167B (key_numbers.md). See HIGH_NET_DEBT under Flags for the post-sale position.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $3,652,000,000 − prior YTD $1,886,000,000 + current YTD $2,688,000,000 = **TTM $4,454,000,000**
- Capex: FY $2,147,000,000 − prior YTD $1,138,000,000 + current YTD $1,179,000,000 = **TTM $2,188,000,000**
- SBC: FY $57,000,000 − prior YTD $27,000,000 + current YTD $29,000,000 = **TTM $59,000,000**
- Shares (current-YTD weighted diluted): **274,100,000**
- **TTM OE total $2,207,000,000 → base OE/share $8.05** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $5.21/share. The TTM base was used because STALE_FY requires a current base and the current share count and asset perimeter are post-NuVista — but the TTM figure is NOT a clean run rate, for two reasons stated plainly: (1) H1 2026 contains an overlap period in which Ovintiv owned both NuVista (from Feb 3) and Anadarko (until Apr 9), a perimeter that no longer exists — Q1 2026 production printed 679 MBOE/d against full-year guidance of 630–645 MBOE/d; (2) H1 2026 prices were strong (Q2 cash from operating activities alone was ~$1.6B per the company release). That elevation is handled by bear-weighting the scenarios, widening the super-bear multiplier, and holding base growth flat — not by pretending $8.05/share is mid-cycle. The preliminary median-base run is documented under Thoughts as the other end of the method range.

## Moat: 4/10 — weak (cost and inventory, no pricing power)
Justification: real cost and inventory advantages — deep premium drilling inventory in the Permian (Midland) and Montney, cost leadership in the Montney and top-2 lowest costs in the Midland Basin, highest-productivity oil wells in both plays — but Ovintiv is a pure commodity price-taker: oil, gas and NGL prices are set by the market, reserves deplete and must be re-drilled just to hold production flat, and returns are capped by basis differentials, takeaway and the energy transition. Cost leadership survives a cycle; it does not compound like a wide moat.
- FOR: Deep premium inventory in Permian (Midland) and Montney — 3,200+ locations added since 2023, plus 930 NuVista locations; Cost leadership: undisputed lowest-cost Montney operator, top-2 lowest cost in the Midland Basin; Highest-productivity oil wells in the Midland Basin and Montney; Infrastructure/processing access adjacent to the Montney position; ~$100M/yr of expected NuVista cost synergies.
- AGAINST: Pure commodity price-taker — no pricing power over oil, gas or NGL prices; Reserves deplete — continuous capex required just to hold production flat; AECO/NYMEX basis and takeaway exposure on Montney gas volumes; Long-term energy-transition demand risk for oil and gas.
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — v5 final run (2026-10-16)
Growth sanity check (written reason): the engine's blended growth is 0.14% and g_base −0.03% — every component is a commodity-price or perimeter artifact, not organic growth (rev CAGR 5y 9.48%, rev CAGR 3y −15.31%, latest rev YoY −3.13%, OE/share CAGR 2y 3.41%). A flat base start matches the company's own plan: hold production at 630–645 MBOE/d on flat capital, with ~4% per-share oil growth from buybacks — so the default offsets were kept (starts −10.0 / −5.0 / −0.0 / +5.0 / +12.0%): the bull start (+5.0%) sits right at the guided per-share growth rate, and the super-bull start (+12.0%) is a price case, not a volume case, weighted at only 10%. Probabilities were bear-weighted to 15/30/30/15/10 (45% on bear-or-worse) and the super-bear OE multiplier widened to 0.60 (bear 0.85) because the filed record shows what a price trough does to this business — conservative OE was $126,000,000 in 2020 against $1,448,000,000 in FY2025 (financials_history.csv). Price $66.16.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -10.0% | 0.60 | Price trough like 2020; OE compresses hard off the elevated TTM base | $24.30 | 6.67% |
| Bear | 30% | -5.0% | 0.85 | Prices normalize lower; Anadarko-less perimeter, flat volumes | $41.88 | 10.18% |
| Base | 30% | -0.0% | 1.00 | Flat OE/share: guided volumes and buybacks offset price normalization | $59.88 | 13.79% |
| Bull | 15% | 5.0% | 1.10 | Guided per-share growth lands; prices hold near H1 2026 levels | $79.84 | 17.53% |
| Super bull | 10% | 12.0% | 1.25 | Sustained high oil prices on the high-graded Permian/Montney portfolio | $118.22 | 23.84% |

- **Probability-weighted: IV@15% $57.97 (−12.4% vs price), IV@12% $76.10 (+15.0%), IV@10% $96.23, weighted IRR 13.44%, base-case IRR 13.79%**
- **Tier by numbers: C.** Diagnostics (key_numbers.md): OE yield 12.17%, terminal value 17.6% of IV@15%, scenario spread 4.87x, net debt 2.47x normalized OE, 9.5 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above, with its overlap/price caveats handled in the scenario design.
- **BASIS_BREAK_SUSPECT**: two breaks, both identified. (1) Price: revenue swung $5,509,000,000 (2020) → $10,468,000,000 (2021) → $14,263,000,000 (2022) → $8,663,000,000 (2025) in financials_history.csv — the >60% moves are the commodity cycle, so no filed revenue CAGR was trusted as an organic growth signal. (2) Perimeter: NuVista consolidated from February 3, 2026 and Anadarko left on April 9, 2026, so FY2025 and TTM are different companies in part; growth inputs were set from production guidance (flat volumes, ~4% per-share oil growth), not from any CAGR straddling either break.
- **NI_OCF_DIVERGENCE** (2023, 2024, 2025): explained, and it does not contaminate the OE base. Net income was $2,085,000,000 / $1,125,000,000 / $1,242,000,000 against OCF of $4,167,000,000 / $3,721,000,000 / $3,652,000,000 (financials_history.csv). The dominant bridge is non-cash depreciation, depletion & amortization — $1,825,000,000 / $2,290,000,000 / $2,179,000,000 in those years — with risk-management mark-to-market and periodic non-cash impairments on top (Q1 2026 alone carried a $1.2B after-tax ceiling-test impairment per the company release, which is why that quarter printed a net loss alongside $1.1B of operating cash flow). Owner's earnings here are built on OCF, so the divergence is a net-income-quality note, not an OE defect.
- **WIDE_SCENARIO_SPREAD** (4.87x): real — a commodity producer's outcome range IS this wide. Confidence is low, and the verdict is sized to the conservative end.
- **HIGH_NET_DEBT** (preliminary run only; dropped from the final flag list at 2.47x normalized OE): the flag fired on the FY2025 balance sheet — net debt $5.167B, 3.82x the preliminary run's median-base OE. The post-FY picture is materially better and is folded into the verdict: after the Anadarko sale the company reported net debt of $2.995B at June 30, 2026, Net Debt to Adjusted EBITDA of 0.6x, ~$4.4B of liquidity and no debt maturities until 2030 (Q2 2026 release, search results). Leverage is therefore not the binding risk at recent prices — but in the super-bear case levered OE still compresses fast, which is why that scenario's IV@15% is $24.30 and why the bear weight is 45%.

## My thoughts / overlay
- Method range: **C to C, with very different point estimates.** The preliminary run (median base $5.21/share, default probabilities/multipliers, moat 5) printed weighted IRR 10.31% and weighted IV@15% $41.40. The final TTM-base run prints 13.44% / $57.97. Both are Tier C: at $66.16 the market is already paying for the strong H1 2026 run rate to persist, whichever base you choose. That agreement is the finding.
- Quality is genuinely good for an E&P: conservative OE held ~$1.35–1.45B through a falling-revenue period, SBC is immaterial ($57,000,000 in FY2025), the portfolio is now concentrated in the two best North American oil plays, the balance sheet was fortified by the Anadarko proceeds, and the company returned ~63% of Q2 2026 Non-GAAP free cash flow via buybacks and dividends (company release). None of that creates pricing power — it lowers the cost floor and lengthens inventory, which is worth a fair multiple on mid-cycle OE, not a growth multiple on an overlap-period TTM base.
- The honest mid-cycle question: if oil and gas average nearer a normal year than H1 2026, OE/share lands closer to the bear/base IVs ($41.88–$59.88) than to the price. The stock at $66.16 needs the bull case (17.53% IRR) to clear the 15% hurdle with room.
- Margin of safety: the price that clears 15% on the weighted path is the weighted IV@15% itself, **$57.97**. A buyer who wants to be paid even in the bear case needs an entry nearer the bear IV@15% of $41.88.

## Final verdict
- **Final tier: C** (weighted IRR 13.44% on the v5 final inputs; no tier override — the median-base preliminary run also printed C)
- Confidence: **Low** (wide scenario spread 4.87x, commodity-price-driven and perimeter-overlapping TTM base)
- One-liner: High-quality Permian/Montney E&P, moat 4/10 — does not clear 15% at $66.16 (weighted IRR 13.4%, weighted IV@15 $57.97) because the TTM base embeds an acquisition-overlap period and strong H1 2026 prices; clears 15% at ~$57.97.
