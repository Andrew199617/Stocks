# ENTG — Entegris, Inc.
v5 run, 2026-10-15. In scope (market cap $22.90B at $150.47, nasdaq_quote_api).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed. Earnings-quarter figures are from cited web search results, summarized.

## What it is
Semiconductor materials supplier: products that purify, protect, and handle the chemicals and gases used in chip fabs — filtration and purification (microcontamination control), fluid/gas handling, and CMP slurries and pads for planarization (the Advanced Planarization Solutions business came with CMC Materials). Customers are the large fabs (TSMC, Intel and peers); the products are small in cost relative to a fab but yield-critical — a contamination failure can scrap a production batch. The July 2022 CMC Materials acquisition (about $5.7B total purchase price including debt retired, cash portion debt-financed, per the closing release summarized in search results) is the defining event in the filed history: revenue stepped up, debt stepped up, and amortization stepped up with it.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $3,196,600,000; operating cash flow $695,400,000; capex $299,200,000; SBC $69,300,000 (always a real cost).
- **Conservative owner's earnings FY2025: $326,900,000 = $2.15/share** (base_oe_latest_per_share)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $208,300,000 for FY2025 — below the conservative figure; in FY2024 the same definition printed $537,303,000 vs the conservative $250,200,000. The maintenance line is whipsawed by the working-capital term, so the OCF-based conservative series is the one used throughout.
- OE positive 4 of the last 5 fiscal years. The negative year is FY2022: conservative OE −$169,640,000 (OCF $363,129,000 against capex $466,192,000 and SBC $66,577,000) — the CMC close year, when capex and deal disruption peaked.
- The 3-year path of conservative OE (financials_history.csv): FY2023 $126,300,000; FY2024 $250,200,000; FY2025 $326,900,000. It is recovering, but from a trough the acquisition and the semi downcycle dug together.
- Net debt $3,337,200,000 (dcf_numbers.json). Share count is diluting, not shrinking: share CAGR +2.06%/yr, already deducted via the −2.06pp share-count adjustment in the engine's blended growth.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $695,400,000 − prior YTD $253,900,000 + current YTD $339,200,000 = **TTM $780,700,000**
- Capex: FY $299,200,000 − prior YTD $174,500,000 + current YTD $80,800,000 = **TTM $205,500,000**
- SBC: FY $69,300,000 − prior YTD $32,000,000 + current YTD $35,100,000 = **TTM $72,400,000**
- Shares (current-YTD weighted diluted): **153,400,000**
- **TTM OE total $502,800,000 → base OE/share $3.28** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $1.65/share — it averages in the FY2023 trough year and is reported for the method range below. Caveat on the TTM base, in the filed numbers themselves: TTM capex ($205,500,000) sits well below FY2025 capex ($299,200,000) because the current-YTD capex leg ($80,800,000) ran at roughly half the prior-YTD leg ($174,500,000). If the capex step-down is construction timing rather than a new run-rate, the TTM base flatters OE. The verdict does not depend on resolving this — see the method range.

## Moat: 6/10 — moderate-strong, not wide
Justification: genuine qualification lock-in in yield-critical consumables and a duopoly position in CMP slurry, but the moat did not protect earnings through the 2023–25 downcycle, giant foundry customers hold real pricing power, strong rivals contest the core niches, and the CMC debt load (net debt $3,337,200,000) limits how the company can respond.
- FOR: Qualification lock-in — products are qualified into a fab's process and switching means a costly, risky re-qualification against a tiny saving
- FOR: CMP slurry/pads position at advanced nodes is effectively a two-supplier market (Entegris and Fujimi, per search-result research summaries)
- FOR: Leading filtration/purification positions in advanced fabs, with sole-source niches
- FOR: Deep patent portfolio and decades of materials-purity know-how that are hard to replicate
- FOR: Content per wafer rises as nodes shrink and purity requirements tighten — Q2 2026 showed it: revenue $883.2M, up 11.5% YoY, with Q3 guided at a $920M midpoint (search results)
- AGAINST: Semiconductor cyclicality — revenue fell in FY2024 ($3,241,200,000) and FY2025 ($3,196,600,000) from the FY2023 peak ($3,523,900,000) despite the moat
- AGAINST: Concentrated giant customers (foundries) with pricing power over a much smaller supplier
- AGAINST: Large, capable rivals in filtration/purification and materials (Pall and others)
- AGAINST: CMC-acquisition leverage still on the balance sheet; share count dilutes +2.06%/yr instead of shrinking
- AGAINST: Heavy Asia fab exposure — Taiwan/China demand and export controls are outside the company's control
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Growth recalibration (written reason): the engine's blended growth is 5.29% and g_base is 3.22%, but the blend's components straddle the CMC break and the downcycle — revenue CAGR 5y +11.45% (inflated by the inorganic 2022 step-up), revenue CAGR 3y −0.88%, latest FY revenue YoY −1.38%, OE/share CAGR 2y +60.14% (an artifact off the trough base). The current print is better than the stale FY figures: Q2 2026 revenue grew +11.5% YoY with Q3 guided higher (search results). Scenario starts were therefore reset via offsets (−0.0522 / −0.0022 / +0.0578 / +0.1078 / +0.1678 vs g_base) to −2 / +3 / **+9** / +14 / +20%. Base +9% sits slightly below the +11.5% Q2 print for a stated reason: it is the first double-digit quarter after two down years, printed off a trough, and the filed FY trend behind it is still negative — treating one recovery quarter as the multi-year start rate would repeat the OE-CAGR artifact in the other direction. Bull (+14%) and super bull (+20%) sit above the latest print, as they should. Probabilities at the defaults 10/25/30/25/10; OE multipliers at the defaults 0.75/0.90/1.00/1.10/1.25. Price $150.47. Base = TTM $3.28/share (--ttm).

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | −2.0% | 0.75 | Semi downturn returns; AI capex pauses; leverage bites | $16.50 | 3.77% |
| Bear | 25% | 3.0% | 0.90 | Recovery stalls at low-single-digit growth | $24.74 | 4.57% |
| Base | 30% | 9.0% | 1.00 | Q2-style recovery holds, then fades over the CAP | $35.89 | 5.71% |
| Bull | 25% | 14.0% | 1.10 | AI/HBM content growth outruns the market for years | $49.29 | 7.04% |
| Super bull | 10% | 20.0% | 1.25 | Full supercycle; share gains plus margin expansion | $72.96 | 9.21% |

- **Probability-weighted: IV@15% $38.22 (−74.60% vs price), IV@12% $51.62, IV@10% $66.68, weighted IRR 5.98%, base-case IRR 5.71%**
- **Tier by numbers: D.** Diagnostics (key_numbers.md): OE yield 2.18%, terminal value 20.4% of IV@15%, scenario spread 4.42x, net debt 6.69x normalized OE, 9.5 months since FY end.
- The decisive fact: even the super-bull scenario — 20% growth start, 1.25x OE level — yields only a 9.21% IRR and a $72.96 IV@15% at this price. No scenario in the set clears even the 10% tier boundary.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026 (YTD end 2026-06-27), quoted in full above.
- **NI_OCF_DIVERGENCE** (2023, 2024, 2025): structural, not a one-off tax deposit. In each named year net income (FY2023 $180,700,000; FY2024 $292,800,000; FY2025 $235,600,000) sits far below operating cash flow (FY2023 $644,500,000; FY2024 $631,700,000; FY2025 $695,400,000) because OCF adds back the large non-cash charges the CMC deal loaded onto the P&L — D&A stepped up from $135,371,000 in FY2022 to $172,700,000 / $188,100,000 / $205,300,000 in 2023/24/25 (acquired-intangible amortization plus depreciation), alongside SBC of $61,400,000 / $65,900,000 / $69,300,000 — plus working-capital swings, which are also why the maintenance-OE line whipsaws between years. Resolution: net income understates cash earnings for this filer; the OCF-based conservative OE used for the base already deducts capex and SBC in cash terms, so the divergence does not contaminate the base. It does mean NI-based multiples flatter nothing here — if anything they overstate how cheap the stock is not.
- **WIDE_SCENARIO_SPREAD** (4.42x): real — the range between a renewed downturn and an AI supercycle is genuinely this wide for a levered semi-materials name. Confidence is capped at medium, and the verdict needs no sizing subtlety: every scenario, including super bull, lands in Tier D at this price.
- **HIGH_NET_DEBT** (net debt 6.69x normalized OE on the final run; the preliminary median-base run flagged 13.3x): folded into the verdict explicitly. The debt is the CMC acquisition financing, still $3,337,200,000 net after several years of paydown. It is why the super-bear case carries a 0.75 OE multiplier, why there are no buybacks to offset the +2.06%/yr dilution, and why an earnings air-pocket would hit equity holders first. It does not change the tier — the tier is D on growth-vs-price arithmetic alone — but it removes any "quality compounder at any price" defense.
- **LOW_OE_YIELD** (preliminary run only, 1.09% on the median base): the final TTM base lifts the OE yield to 2.18% (diagnostics), which is why the flag no longer fires — but 2.18% is still a thin cash yield at $150.47, and the valuation still rests almost entirely on future growth. Noted, not waved off.

## My thoughts / overlay
- Method range: the preliminary run (median base $1.65/share, default scenario offsets, price $151.08) printed weighted IRR 3.78% and weighted IV@15% $14.92. The final run (TTM base $3.28/share, recovery-recalibrated growth) prints 5.98% and $38.22. The defensible-input range is therefore roughly $15–$38 of IV@15% against a $150.47 price — the methods disagree about how overvalued the stock is, not about whether it is. Both are Tier D, and so is every individual scenario in the final run. This is the opposite of the APP situation: there the spread crossed tiers; here it doesn't come close.
- What the price is paying for: at $150.47 the market is capitalizing the Q2 2026 recovery (+11.5% YoY, 18.6% operating margin per search results, Q3 guide $920M midpoint) as if it compounds for a decade at high rates with the debt melting away. The TTM OE yield of 2.18% and net debt of $3,337,200,000 say the current cash economics don't support that yet.
- Quality is not the debate: the qualification moat is real (moat 6/10), the planarization position is structurally strong, and the recovery print is real. The debate is only price. The same business at the weighted IV@15% of $38.22 would clear Andrew's 15% hurdle by construction; even the super-bull IV@15% of $72.96 — the rosiest defensible print — is less than half the current price, so there is no margin-of-safety framing in which $150.47 works on owner's earnings.
- Watch items that could change the picture on a future run: whether capex stays at the TTM pace ($205,500,000) or returns toward the FY2025 pace ($299,200,000); whether the share count stops diluting; and the pace of net-debt paydown from the $3,337,200,000 level.

## Final verdict
- **Final tier: D** (weighted IRR 5.98% on the v5 final inputs; Tier D under the median base, the TTM base, and every individual scenario including super bull at 9.21%)
- Confidence: **Medium** (capped by the 4.42x scenario spread; the tier itself is unusually robust — no defensible input set tested clears even 10%)
- One-liner: Real-moat semi materials name (6/10) in a genuine recovery, but at $150.47 it prices in a decade of supercycle — weighted IRR 5.98%, IV@15% $38.22; it clears 15% only at $38.22, less than a third of the price.
