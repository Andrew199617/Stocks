# LECO — Lincoln Electric Holdings, Inc.
Engine 5.4.0 pass-1 run, 2026-10-17. In scope (market cap $14.64B at $262.10, nasdaq_quote_api).

All figures below are copied from dcf_numbers.json, ttm.json, fundamentals.json, or financials_history.csv — none are recomputed.

## What it is
The global leader in arc welding: welding equipment, consumables (electrodes, wire), cutting systems, welding automation, and the Harris Products Group (brazing/soldering alloys, HVAC components). Three segments — Americas Welding, International Welding, Harris Products. Sells direct and through distributors to general fabrication, automotive/transportation, construction/infrastructure, energy, and heavy fabrication. Founded 1895, Cleveland, Ohio. Main rivals: ESAB and ITW's Miller Electric; the top five makers hold roughly half the global electrodes market, with Lincoln the long-standing leader.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $4,233,003,000 (+5.6% YoY); operating cash flow $661,173,000; capex $126,974,000; SBC $20,348,000 (always a real cost; small — ~3% of OCF).
- **Conservative owner's earnings FY2025: $513,851,000 = $9.20/share**
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $402,462,000 — below the conservative figure because FY2025 working capital absorbed $118,071,000 (ΔNWC in financials_history.csv); the OCF-based conservative figure is the cleaner base here.
- OE positive 5 of the last 5 fiscal years. OE/share path: $4.64 (2021), $4.87 (2022), $9.45 (2023), $8.01 (2024), $9.20 (2025) — the 2023 step-up was an OCF spike year ($667,542,000 vs $383,386,000 in 2022), which is why the median-of-3 base is preferred over any single year.
- Balance sheet: net debt $985,219,000 (LongTermDebtNoncurrent + DebtCurrent basis, dcf_numbers.json), 1.87x normalized OE; lease liabilities $53,521,000. Manageable, not a flag.
- Capital return: DPS TTM $3.12, 17 consecutive growth years, buybacks TTM $237,276,000 (fundamentals.json); diluted share count shrinking −1.66%/yr (share_cagr, dcf_numbers.json).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $661,173,000 − prior YTD $329,521,000 + current YTD $355,934,000 = **TTM $687,586,000**
- Capex: FY $126,974,000 − prior YTD $52,392,000 + current YTD $70,600,000 = **TTM $145,182,000**
- SBC: FY $20,348,000 − prior YTD $12,277,000 + current YTD $14,455,000 = **TTM $22,526,000**
- Shares (current-YTD weighted diluted): **55,206,000**
- **TTM OE total $519,878,000 → base OE/share $9.42** (base_source: ttm_json)
- The engine's normalized base (median of last 3 FY OE/share) is $9.20/share — nearly identical to TTM, so the base choice is not load-bearing here.

## Moat: 7/10 — strong
Justification: the global #1 welding franchise with demonstrated pricing power and returns on capital that stayed well above the cost of capital through the cycle, tempered by capable scaled rivals (ESAB, ITW/Miller), partly commoditized consumable categories, and hard end-market cyclicality.
- FOR: ROIC (roic_proxy, fundamentals.json) held 22.5–28.2% over the last five fiscal years — 27.3% (2021), 23.9% (2022), 28.2% (2023), 22.6% (2024), 22.5% (2025) — and even the 2020 COVID trough printed 17.6%; gross margin expanded from 32.8% (2020) to 36.2% (2025), 36.7% at the 2024 peak — pricing power, not just volume.
- FOR: proven price realization in the current print — Q2 2026 organic growth +10.1% was +7.7pp price / +2.4pp volume (Q2 2026 earnings reports, search-cited), and management raised FY2026 guidance to low-double-digit net sales growth.
- FOR: brand, global distribution, and application engineering — welds are specified into fabricator processes, and consumables pull through the installed equipment base; #1 share in a moderately consolidated industry.
- FOR: automation/robotic welding and the consumables annuity raise switching friction versus bare equipment.
- AGAINST: ESAB and ITW (Miller) are large, well-resourced rivals competing across the same portfolio; no network effects, and electrodes/consumables face regional and private-label price pressure.
- AGAINST: demand is industrial capex — nine consecutive quarters of volume decline preceded the Q2 2026 inflection; Europe/International volumes and margins were still falling in Q2 2026.
- AGAINST: commodity input costs (steel, specialty metals) and tariff/trade-policy exposure compress margins in adverse years; operating margin dipped to 10.6% in 2020.
- A 7 gives CAP = 11.1 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 11.1 years, 15-year projection.

## DCF — 5.4 final run (2026-10-17)
**Growth sanity check (mandatory):** engine blend g_base = 6.46% (components: 5-yr revenue CAGR 9.78%, 3-yr CAGR 4.02%, latest FY YoY +5.60%, OE/share 2-yr CAGR −1.36%; share-count adjustment +1.66pp applied to revenue components only). Recent prints: Q2 2026 sales +12.0% YoY with organic +10.1%, and FY2026 guidance raised to low-double-digit net sales growth. The base start of 6.46% sits BELOW the latest print for a written reason: Q2 is a cyclical inflection after nine quarters of volume compression and +7.7pp of its organic growth is price (cost/tariff pass-through) that annualizes out of the growth rate; the through-cycle anchors are the 3-yr revenue CAGR of 4.02% and the negative OE/share 2-yr CAGR. Scenario starts were compressed from the engine defaults (super-bull default 18.46% has no support in any print) via offsets −0.10 / −0.04 / 0.00 / +0.04 / +0.07 → −3.54% / 2.46% / **6.46%** / 10.46% / 13.46%. The super-bull start of 13.46% modestly exceeds the +12.0% Q2 print — acceptable only as a 10%-probability case in which the volume recovery plus the automation cycle sustains double-digit OE/share growth off buyback shrinkage; even it does not clear the hurdle (see table). Probabilities 10/25/30/25/10 (defaults kept — no evidence to skew them); OE multipliers 0.75/0.90/1.00/1.10/1.25 (defaults).

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | −3.5% | 0.75 | Industrial recession repeats the 2023–25 volume compression, price gives back | $43.64 | 4.36% |
| Bear | 25% | 2.5% | 0.90 | Recovery stalls; Europe stays weak; mid-cycle margins | $69.38 | 5.81% |
| Base | 30% | 6.5% | 1.00 | Blend growth decays normally over the 11.1-yr CAP | $93.14 | 7.14% |
| Bull | 25% | 10.5% | 1.10 | Q2 momentum largely holds; automation mix lifts margins | $123.87 | 8.80% |
| Super bull | 10% | 13.5% | 1.25 | Sustained double-digit OE growth + buybacks compound | $162.34 | 10.70% |

- **Probability-weighted: IV@15% $96.85 (−63.0% vs price), IV@12% $129.88, IV@10% $166.91, weighted IRR 7.38%, base-case IRR 7.14%**
- **Tier by numbers: D** (bear D, bull D — no band ambiguity). Diagnostics (dcf_numbers.json): OE yield 3.59%, terminal value 19.8% of IV@15%, scenario spread 3.72x, net debt 1.87x normalized OE, 9.5 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY2025 ended ~10 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026 (legs quoted above). TTM OE/share $9.42 vs FY $9.20: the interim period is modestly accretive, no distortion either way.
- The preliminary run's **WIDE_SCENARIO_SPREAD** (4.49x) narrowed to 3.72x in the final run after the scenario starts were compressed to evidence — but the spread is still wide because the price sits far above every scenario's IV; confidence is capped at medium and the verdict is sized to the conservative end.
- No other flags fired: no DATA_GAP (all of sbc/capex/shares/ocf filed), no BASE_DIVERGENCE (TTM $9.42 vs median $9.20 — bases agree), no NI_OCF_DIVERGENCE, no SECTOR_MODEL_MISMATCH (standard industrial model fits), no IRR_AT_FLOOR.

## My thoughts / overlay
- This is a quality-versus-price case, not a quality debate: ROIC 22–28%, gross margin up ~340bp over five years, 17 straight dividend increases, buybacks shrinking the count, OE positive 5/5 years. The problem is arithmetic: at $262.10 the OE yield is 3.59%, and even the super-bull path (13.5% growth start, 1.25x OE) only produces a 10.70% IRR — below the 15% hurdle. The bear and bull tiers agree (both D), so the method range is narrow: every defensible input set lands in D.
- Hurdle-clearing prices (dcf_numbers.json): clears 15% at **$96.85**, 20% at $67.41, 25% at $51.38. The market is pricing LECO as if mid-teens OE growth were the base case; the filing record (3-yr revenue CAGR 4.02%, OE/share 2-yr CAGR −1.36%) does not support that outside a cyclical peak print.
- The live risk to this verdict is a structural re-rating of welding automation (robotics exposure is real and growing), which would show up first as sustained double-digit volume growth rather than price-led growth — Q2 2026's +2.4% volume is a start, not proof.

## Final verdict
- **Final tier: D** (weighted IRR 7.38% on the final 5.4 inputs; bear D / bull D, method range narrow)
- Confidence: **Medium** (high on the OE base — TTM and median agree within 2.4% — medium on any single growth path given the 3.72x scenario spread and the cyclical inflection)
- One-liner: High-quality welding franchise, moat 7/10 with 22–28% ROIC — but at $262.10 it cannot clear 15% in any scenario (weighted IRR 7.4%, IV@15% $96.85); it clears the 15% hurdle only at ~$97.
