# SMTC — Semtech Corporation
Engine 5.4.0 run, 2026-10-16. All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
Fabless analog/mixed-signal semiconductor company. Three segments: Signal Integrity (optical and copper interconnect for data centers — CopperEdge active copper cables, linear pluggable optics), Analog Mixed Signal and Wireless (protection, RF, PerSe sensing), and IoT Systems and Connectivity (LoRa long-range low-power wireless, plus the Sierra Wireless cellular module business acquired in January 2023, part of which is now slated for divestiture — management's fiscal-2030 framework excludes $166M of cellular module revenue as held for sale). The current story is AI data-center interconnect plus LoRa growth; the balance-sheet story is the debt-funded Sierra deal and its aftermath.

## Owner's earnings
**FY2026 (10-K, ended 2026-01-25, from financials_history.csv):** operating cash flow $181,168,000; capex $9,783,000; SBC $57,723,000 (always a real cost).
- **Conservative owner's earnings FY2026: $113,662,000 = $1.29/share** (base_oe_latest_per_share $1.2861475094484802 in dcf_numbers.json).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): −$53,580,000 for FY2026 — negative because GAAP net income is still negative (−$40,376,000) after non-cash charges; the OCF-based conservative figure is the cleaner series here and is the one used throughout.
- OE positive 3 of the last 5 fiscal years. The 3-yr median (normalized) base is **−$0.25/share** — the median of FY2024 (−$2.546), FY2025 (−$0.250) and FY2026 (+$1.286). That median is the distorted figure: FY2024 carries the Sierra Wireless impairment (see NI_OCF_DIVERGENCE below) and FY2025 is the trough year. The preliminary engine run therefore printed Tier F (subtype `sbc_exceeds_cash`: over the median window, SBC consumes the OCF − capex stream). The latest FY and the TTM are both positive, so the run proceeds on the TTM base rather than scoring the impairment-window median.

**Base used = TTM owner's earnings from ttm.py (filing-direct, no hand math), through Q1 FY2027 (period ended 2026-04-26):**
- OCF: FY $181,168,000 − prior YTD $27,824,000 + current YTD $36,183,000 = **TTM $189,527,000**
- Capex: FY $9,783,000 − prior YTD $1,650,000 + current YTD $8,172,000 = **TTM $16,305,000**
- SBC: FY $57,723,000 − prior YTD $6,835,000 + current YTD $26,446,000 = **TTM $77,334,000**
- Shares (current-YTD weighted diluted): **98,028,000**
- **TTM OE total $95,888,000 → base OE/share $0.978** (base_source: ttm_json)
- TTM caveat: SBC is rising fast (TTM $77.3M vs FY2026 $57.7M) and the diluted count rose from 88,374,000 (FY2026) to 98,028,000 (TTM YTD) — that is why TTM OE/share ($0.978) sits below the latest FY ($1.286) despite higher OCF.
- Balance sheet (latest FY, financials_history.csv / dcf_numbers.json): total debt $491,234,000 (LongTermDebtNoncurrent + LongTermDebtCurrent), cash $195,179,000, **net debt $296,055,000**, lease liabilities $26,760,000. Debt peaked at $1,371,039,000 in FY2024 after the Sierra acquisition and has been paid down since.

## Moat: 4/10 — weak-to-moderate; real IP, unproven economics
Evidence first (fundamentals.json): ROIC proxy (after-tax operating income over equity + debt − cash) ran 20.5% in FY2022 and 3.9% in FY2023, then −79.8% in FY2024 (impairment year, equity went negative), 4.2% in FY2025 and 3.0% in FY2026. Gross margin was 62.2% (FY2022) and 63.3% (FY2023), crashed to 34.1% in FY2024 on the Sierra module mix and restated discontinued-operations basis, and has recovered only to 50.2% (FY2025) and 51.6% (FY2026) — still ~11pp below the pre-Sierra level. A moat of 7+ needs ROIC well above the cost of capital through a cycle; the last three years show the opposite, so the score sits at 4 despite genuine IP.
- FOR: LoRa — Semtech owns the core LoRa IP and anchors the LoRaWAN ecosystem/standard, a real specification-and-design-in moat in low-power wide-area IoT; leading position in the emerging active-copper-cable (CopperEdge) and linear-pluggable-optics niches for AI data-center interconnect, with reported design wins at hyperscalers; PerSe sensing IP in consumer devices.
- AGAINST: signal-integrity rivals are Broadcom, Marvell and MACOM — far larger R&D budgets, and ACC/LPO standards can shift to DSP-based or rival approaches at each speed generation (800G → 1.6T), so the lead is re-earned per cycle; ROIC of 3–4% for two straight years and a gross margin still well below pre-Sierra levels say the franchise has not yet converted position into returns; the Sierra acquisition destroyed capital (FY2024 net loss −$1,092,000,000, equity −$307,434,000) — capital allocation is part of the moat question and it failed; semiconductor cyclicality and hyperscaler capex concentration.
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — engine 5.4.0 final run (2026-10-16)
Price $141.16 (nasdaq_quote_api); market cap est. $12,474,873,840 — in scope under $40B.
Growth sanity check (mandatory): the engine's blended start is 7.07% — a backward-looking blend (5-yr revenue CAGR 12.07%, 3-yr 11.59%, latest FY YoY 15.47%, each cut by the −5pp share-count adjustment) that averages in the Sierra trough. Actual recent prints are hotter: FY2026 revenue +15.5% YoY, and Q2 FY2027 revenue was reported at $341.9M, +32.7% YoY (press coverage of the August 2026 print; that 10-Q, period 2026-07-26 filed 2026-08-26, is not yet in EDGAR companyfacts, so it is in no OE leg — see STALE_FY). Scenario starts were therefore recalibrated via offsets (−0.15 / −0.07 / +0.08 / +0.18 / +0.28 vs the blend) to −7.9 / +0.1 / **+15.1** / +25.1 / +35.1%: the base start equals the FY2026 print rather than the latest quarter's because OE/share growth lags revenue growth here — the diluted count is compounding at 11.4%/yr and SBC is rising in dollars, both of which tax per-share OE directly. Bull (+25.1%) and super bull (+35.1%) bracket the +32.7% Q2 revenue print. Probabilities 10/25/30/25/10 (defaults — the distribution of outcomes is genuinely two-sided); OE multipliers 0.75/0.90/1.00/1.10/1.25 (defaults).

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | −7.9% | 0.75 | AI interconnect cycle turns; ACC/LPO share lost at the 1.6T transition | $4.00 | 2.81% (at floor) |
| Bear | 25% | +0.1% | 0.90 | Data-center ramp stalls at current scale; LoRa grows slowly; SBC keeps eating OCF | $6.57 | 3.07% |
| Base | 30% | +15.1% | 1.00 | FY2026 growth rate decays normally over the CAP; margins recover gradually | $12.89 | 3.77% |
| Bull | 25% | +25.1% | 1.10 | Data-center revenue compounds near the reported Q2 pace; operating leverage reaches OE | $20.42 | 4.62% |
| Super bull | 10% | +35.1% | 1.25 | Management's high-growth path broadly lands; OE/share scales with revenue | $33.00 | 6.00% |

- **Probability-weighted: IV@15% $14.32 (−89.9% vs price), IV@12% $19.47, IV@10% $25.26, weighted IRR 3.96%, base-case IRR 3.77%**
- **Tier by numbers: D** (bear D, bull D — no TIER_BAND issue; every scenario is a D).
- Diagnostics (dcf_numbers.json): OE yield 0.69%, terminal value 21.0% of IV@15%, scenario spread 8.24x, net debt 3.42x normalized OE, 8.67 months since FY end.
- Hurdle prices (weighted): clears 15% only at **$14.32**, 20% at $9.75, 25% at $7.28 — roughly a tenth of the current price.

## Flags — every fragility flag resolved
- **STALE_FY** (latest FY ended ~9 months ago): resolved by construction — the base is the ttm.py TTM figure through Q1 FY2027 (2026-04-26), legs quoted above. One residual staleness remains and is stated plainly: fundamentals.py warns the Q2 FY2027 10-Q (period 2026-07-26, filed 2026-08-26) is not yet in EDGAR companyfacts, so no tool output includes Q2. Reported Q2 revenue of $341.9M (+32.7% YoY) is used only in the growth sanity check, not in any OE figure.
- **DILUTION** (share count +11.4%/yr): real and worsening in dollars. Diluted shares: 64,127,000 (FY2024) → 71,606,000 (FY2025) → 88,374,000 (FY2026) → 98,028,000 (TTM YTD) — convertible-note conversions plus equity issuance; SBC rose from $40,170,000 (FY2024) to $68,036,000 (FY2025), $57,723,000 (FY2026) and $77,334,000 TTM. The engine already deducted −5pp from the revenue growth components for this; the TTM base also captures it directly (it is why TTM OE/share < FY2026 OE/share). Not double-counted beyond that.
- **NI_OCF_DIVERGENCE** (NI vs OCF differ >40% in 2024, 2025, 2026): FY2024 is the Sierra Wireless impairment — net income −$1,092,000,000 and operating income −$944,322,000 against OCF of −$93,920,000; the gap is the non-cash goodwill/intangible write-down of the January 2023 acquisition. FY2025 (NI −$161,896,000 vs OCF +$57,987,000) and FY2026 (NI −$40,376,000 vs OCF +$181,168,000) are the same pattern at smaller scale: SBC ($68.0M / $57.7M) and D&A ($33.2M / $29.9M) addbacks plus residual non-cash charges against small GAAP losses. The conservative OE series is OCF-based throughout, so the impairment does not contaminate the base — it contaminates only the 3-yr median, which is why the median was rejected as the base (see Owner's earnings).
- **IRR_AT_FLOOR** (super bear): the super-bear IRR of 2.81% sits within 0.5pp of the 2.5% terminal growth rate — read it as "at most ~3%", not a precise figure. The weighted IRR (3.96%) is not at the floor, but the substantive point stands: at $141.16 the price is beyond what this OE stream can express a return on.
- **LOW_OE_YIELD** (base OE yield 0.69%): real — at $0.978 of TTM OE against a $141.16 price, the valuation rests almost entirely on growth that has not yet reached the OE line. This is the core of the verdict.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 8.24x super-bear IV): real — outcomes range from cycle bust to management's FY2030 framework. Confidence is low, and the verdict is sized to the conservative end.
- **HIGH_NET_DEBT** (net debt 3.42x normalized OE): balance sheet stated from the filing above — debt $491,234,000, cash $195,179,000, net debt $296,055,000, leases $26,760,000. Leverage is much improved from the FY2024 peak ($1,242,454,000 net debt) and is not distress-level against TTM OE of $95,888,000, but it removes any cushion if the data-center ramp disappoints.

## My thoughts / overlay
- The honest headline is the gap, not a point estimate: the market price embeds something close to management's fiscal-2030 framework (revenue compounding toward $3.2B with ~35%-of-revenue free cash flow, per the October 2026 analyst-day coverage) being delivered nearly in full, while filing-based owner's earnings today are $0.978/share TTM with SBC consuming $77.3M of a $189.5M OCF stream. Even the super-bull scenario — 35.1% OE/share growth start, 1.25x OE multiplier — produces an IV@15% of $33.00, under a quarter of the price.
- Method range: on the rejected normalized base (−$0.25/share) the name is a straight F (no positive normalized OE); on the TTM base used here it is a D at 3.96% weighted IRR; on the latest FY alone ($1.286/share) it would still be a D by a wide margin. Every defensible base gives the same tier family — the disagreement is F-vs-D, not cheap-vs-expensive.
- What would change the answer: OE/share actually compounding — SBC flattening in dollars, the diluted count stabilizing post-convertibles, and data-center revenue converting to OCF at fabless margins. Q2 FY2027's reported print (revenue +32.7% YoY, not yet in companyfacts) is directionally that, but one quarter of revenue is not owner's earnings, and the TTM SBC trend points the other way.
- The stock fell ~17% on the analyst-day coverage (per press reports) and still sits ~10x the price at which it would clear a 15% hurdle on current OE. This is a price problem, not a business-existence problem.

## Final verdict
- **Final tier: D** (weighted IRR 3.96% on the TTM base; F on the impairment-window median base — the method range is F to D)
- Confidence: **Low** (WIDE_SCENARIO_SPREAD 8.24x, TTM one quarter behind the latest reported print, super-bear IRR at the solver floor)
- One-liner: Real LoRa and AI-interconnect franchise (moat 4/10) but owner's earnings are $0.98/share TTM against a $141.16 price — 3.96% weighted IRR, IV@15% $14.32; it clears 15% only below ~$14.
