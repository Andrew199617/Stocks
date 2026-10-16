# KHC — The Kraft Heinz Company
v5 run, 2026-10-14. In scope (market cap $26.94B at $22.70, nasdaq_quote_api).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed.

## What it is
One of the largest packaged-food companies in the world, formed by the 2015 Kraft–Heinz merger: Heinz ketchup and condiments, Philadelphia, Kraft Mac & Cheese and Singles, Oscar Mayer, Lunchables, Maxwell House. Three reported groups — North America, International Developed Markets, Emerging Markets. The story since the merger is a decade of flat-to-declining volumes, private-label share gains, and repeated admissions via impairment that the merged brand portfolio was overvalued. A planned split into Global Taste Elevation Co. and North American Grocery Co. (announced September 2025) was paused in February 2026 by new CEO Steve Cahillane (took over January 1, 2026), who redirected the money into roughly $600–700M of incremental brand investment in 2026.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $24,942,000,000 (−3.50% YoY, latest rev YoY in dcf_numbers.json); operating cash flow $4,462,000,000; capex $801,000,000 (tag: PaymentsToAcquirePropertyPlantAndEquipment); SBC $95,000,000 — small and always charged as a real cost.
- **Conservative owner's earnings FY2025: $3,566,000,000 = $3.00/share** (base_oe_latest_per_share $3.0042). OE positive 5 of the last 5 fiscal years.
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): **−$5,345,000,000** — not usable this year: it is built on net income of −$5,846,000,000, which is dominated by non-cash goodwill/intangible impairments (see NI_OCF_DIVERGENCE below). The OCF-based conservative figure is the clean one; the impairment never touched cash flow.
- Balance sheet as captured by the engine: cash $2,615,000,000 and equity $41,664,000,000 at FY2025 (financials_history.csv). The engine's debt tags (debt_current / debt_lt) came back null, so net debt is **not in the computed outputs** and no leverage ratio is quoted here — qualitatively, this is a heavily indebted staples balance sheet and the dividend ($0.40/quarter, unchanged since the 2019 cut) is a large fixed claim on the OE; treat the equity as a leveraged claim on a flat cash stream.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $4,462,000,000 − prior YTD $1,929,000,000 + current YTD $2,088,000,000 = **TTM $4,621,000,000**
- Capex: FY $801,000,000 − prior YTD $425,000,000 + current YTD $429,000,000 = **TTM $805,000,000**
- SBC: FY $95,000,000 − prior YTD $53,000,000 + current YTD $53,000,000 = **TTM $95,000,000**
- Shares (current-YTD weighted diluted): **1,186,000,000**
- **TTM OE total $3,721,000,000 → base OE/share $3.14** (base_source: ttm_json)
- The engine's normalized base (median of last 3 FY OE/share) is $2.51/share. It is the middle of a rising-but-volatile series (FY2023–25 conservative OE/share ran from a 2022 OCF trough through recovery), and it is stale by ~10 months; the TTM base is filing-derived through June 2026 and already includes the H1 2026 brand-investment drag on operating income, so it is the better anchor. The method range is documented under Thoughts — both bases land in Tier C, so the choice does not drive the verdict.

## Moat: 4/10 — weak-to-narrow, eroding
Justification: A handful of genuinely strong brands (Heinz above all, Philadelphia) sit inside a broad portfolio that has been losing volume and share to private label for a decade; the $9.3B of 2025 impairments are the filer's own admission that much of the brand equity was worth less than carried. Pricing power survives only in select categories and is bought back with volume losses.
- FOR: Heinz and Philadelphia "win-big" brands gaining or holding share across regions and categories (management reports Heinz gaining/holding on over 70% of its revenue combinations in 2026); global distribution scale and shelf presence built over decades; demonstrated pricing in select categories (Q2 2026 price contributed +1.3pp); cash-generative core — OCF positive in every year of the filed history, $4.62B TTM.
- AGAINST: private-label share of the market up from ~11% to ~17% since 2019, a structural attack on national-brand pricing power; volume/mix declining (−2.6pp in Q2 2026; meats and spoonables weakest); repeated goodwill/intangible impairments ($9.3B in 2025, following the 2019 write-downs) — the brands keep failing their own carrying-value tests; only 21% of revenue was gaining or holding share in 2025 (improving to 36% year-to-date 2026 — still a minority of the portfolio); low returns on capital through the cycle and a dividend frozen at $0.40 since 2019.
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection. The 2.5% terminal rate is kept at default — for a pricing-led staples portfolio it is roughly inflation, i.e. flat in real terms; no --gterm reason was strong enough to override it.

## DCF — v5 final run (2026-10-14)
Growth inputs: the engine's blend is g_base −0.16% (rev CAGR 5y −0.97%, 3y −1.99%, latest YoY −3.50%, OE/share CAGR 2y +14.72% off the depressed base, share-count adjustment +1.32pp from the −1.32%/yr buyback shrink). The +14.72% OE/share CAGR is a recovery artifact off the 2022–23 trough, not a growth rate — no scenario uses it.
**Sanity check against actual prints:** Q2 2026 revenue $6,262M, −1.4% YoY (organic −1.3%; price +1.3pp, volume/mix −2.6pp), adjusted EPS $0.56 vs $0.69 a year earlier; FY2026 guidance is organic sales −0.5% to −2% and adjusted EPS $2.03–2.09 with adjusted operating income guided down 16–18% on the brand-investment program. Scenario starts are OE/share growth, which can outrun revenue via the buyback shrink and post-investment margin recovery — but the default bull/super-bull offsets (+5/+12pp → starts of +4.84%/+11.84%) still sat far above anything the company is printing, so offsets were recalibrated to −10/−4/0/+3/+6pp and probabilities skewed bear-heavy (15/30/30/15/10) for the volume trend and the guided profit decline. OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $22.70.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −10.00% | 0.75 | Private label keeps taking share; investment fails, volumes slide mid-single digits | $11.83 | 8.57% |
| Bear | 30% | −4.16% | 0.90 | Guided decline persists; pricing offsets only part of volume loss | $17.88 | 12.21% |
| Base | 30% | −0.16% | 1.00 | Sales stabilize near guide; OE/share flat with buyback support | $23.22 | 15.29% |
| Bull | 15% | +2.84% | 1.10 | Brand investment works; Heinz-led share gains broaden, margins recover | $28.67 | 18.28% |
| Super bull | 10% | +5.84% | 1.25 | Turnaround year — volume growth returns, operating leverage on a leaner base | $36.55 | 22.34% |

- **Probability-weighted: IV@15% $22.06 (−2.83% vs price), IV@12% $28.83, IV@10% $36.34, weighted IRR 14.64%, base-case IRR 15.29%**
- **Tier by numbers: C.** Diagnostics (key_numbers.md): OE yield 13.82%, terminal value 17.19% of IV@15%, scenario spread 3.09x, 9.56 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.56 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026 (period ended 2026-06-27), with all four legs quoted above.
- **OE_VOLATILE** (OE/share range over the last 5 years spans >3x): real and identified — the span is the 2022 OCF trough (FY2022 OCF $2,469,000,000, conservative OE $1,405,000,000, from financials_history.csv) against the 2020–21 and 2025 recovery years; it is working-capital/cycle volatility in a flat business, not growth. Handled with the normalized-vs-TTM comparison, bear-heavy probabilities (45% on bear-or-worse), and confidence held at medium.
- **NI_OCF_DIVERGENCE** (2025, >40%): identified — FY2025 net income −$5,846,000,000 vs OCF +$4,462,000,000. The gap is non-cash goodwill and intangible asset impairments totaling $9,301M taken during 2025 (per the company's 10-Q reporting, citing the sustained decline in its stock price), which drove the FY2025 operating loss of −$4,669,000,000. Non-cash: the OCF-based conservative OE used throughout is unaffected, and the NI-based maintenance OE (−$5,345,000,000) is rejected for this year for exactly this reason.
- The preliminary run also flagged **WIDE_SCENARIO_SPREAD** (4.14x); the recalibrated final run's spread is 3.09x and the flag cleared, but the range is still wide — confidence is medium, not high, and the verdict is sized to the conservative end.

## My thoughts / overlay
- The method range is narrow for once: the preliminary median-base run ($2.51/share, default scenarios) gave weighted IRR 13.42% and IV@15% $19.83; the final TTM-base run gives 14.64% and $22.06. Both are Tier C. The honest headline is "high-13s to mid-14s weighted IRR on filing-derived bases" — just under the hurdle, not a mispriced bargain and not a value trap on cash numbers alone.
- Quality of the cash is decent, quality of the growth is not: TTM OE $3,721,000,000 on $4,621,000,000 of OCF is real cash generation, SBC is trivial ($95,000,000), and capex ($805,000,000 TTM) runs near D&A ($968,000,000 FY2025) — this is a harvesting asset, not a starved one. The problem is the top line: revenue has shrunk for three straight years on the filed history and is guided down again in 2026 while management spends ~$700M trying to reverse it.
- Balance-sheet overlay: the engine could not read the debt legs (net debt not in computed outputs), so no leverage adjustment is baked into the tier — with a staples issuer carrying a large debt stack and a $0.40/quarter dividend that has not grown since 2019, the equity's margin for error is thinner than the OE yield (13.82%) alone suggests. Berkshire Hathaway's exit from its ~27% stake, reported in early 2026, is a sentiment data point in the same direction, not a valuation input.
- Hurdle math: the stock clears a 15% weighted IRR at **$22.06** (the weighted IV@15%) — the $22.70 price sits just above it. For a margin of safety against the bear case (IV@15% $17.88), a conservative entry is in the high-teens; at today's price you are paid roughly the base case and nothing for the bear case.
- What would change the verdict: two consecutive quarters of volume/mix at or above zero with the share-gain breadth (36% YTD) still rising — that is the bull path (+2.84% start, 18.28% IRR) becoming the base path.

## Final verdict
- **Final tier: C** (weighted IRR 14.64% on the v5 final inputs; method range 13.42–14.64%, all Tier C)
- Confidence: **Medium** (high on the TTM cash base, low-medium on any growth path — OE is volatile and the top line is still shrinking)
- One-liner: Cash-generative packaged-food giant with an eroding narrow moat (4/10) — the OE is real but growth is negative, so at $22.70 it just misses the 15% hurdle (14.6% weighted, IV@15% $22.06); it clears 15% only below ~$22.
