# TTMI — TTM Technologies, Inc.
Pass-1 run, 2026-10-17 (engine 5.4.0). Market cap $9,899,927,640 at $93.88 (nasdaq_quote_api) — in scope under $40B.

All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
One of the world's largest printed circuit board (PCB) manufacturers, plus RF/microwave components, RF microelectronic assemblies and mission systems. End markets: AI data centers & networking (advanced N+M asymmetrical interconnect PCBs for hyperscalers), aerospace & defense (defense backlog $1.7B per Q2 2026 reporting), medical/industrial/instrumentation, automotive. Management said ~80% of net sales relate to the AI and defense megatrends (Q2 2026 call, via search coverage). Q2 2026: revenue $1.004B, +37.4% YoY; non-GAAP EPS $0.99; gross margin 21.1%; operating margin 10.9%. Guidance raised: Q3 2026 revenue $1.10–1.14B and non-GAAP EPS $1.21–1.27; FY2026 revenue ~$4.4B with non-GAAP EPS approaching $5.00 (vs FY2025 revenue $2,906,345,000 filed); management expects 15–20% organic growth in 2027 and 2028. Two post-Q2 developments: a $1.1B cash acquisition of EPIQ Design Solutions (software-defined radio / RF; ~17.4x synergy-adjusted expected 2027 EBITDA per deal coverage; expected net leverage ~2.3x post-close) and, on 2026-10-12, a further $400M capacity investment across four China facilities and Penang, Malaysia, incremental to the previously disclosed $1.2B 2025–2029 program (company press release, 8-K 2026-10-13).

## Owner's earnings
**FY2025 (10-K via EDGAR, financials_history.csv):** operating cash flow $291,882,000; capex $292,565,000; SBC $41,668,000.
- **Conservative owner's earnings FY2025: −$42,351,000 = −$0.40/share** — negative, because the capacity supercycle's capex alone consumed all of OCF before SBC.
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $79,231,000 = $0.75/share (79,231,000 / 105,453,000 diluted shares). The two definitions diverge by ~$121M because FY2025 capex ($292.6M) is 2.7x D&A ($110,274,000) — the gap is growth capex for the disclosed $1.2B 2025–2029 AI-capacity program, not upkeep of the existing base.
- OE (conservative) positive 4 of the last 5 fiscal years (dcf_numbers.json). Net debt $414,917,000; lease liabilities a further $96,433,000.

**TTM through Q2 2026 (ttm.py, filing-direct):**
- OCF: FY $291,882,000 − prior YTD $87,149,000 + current YTD $118,172,000 = **TTM $322,905,000**
- Capex: FY $292,565,000 − prior YTD $123,726,000 + current YTD $169,205,000 = **TTM $338,044,000**
- SBC: FY $41,668,000 − prior YTD $17,975,000 + current YTD $37,648,000 = **TTM $61,341,000**
- Shares (current-YTD weighted diluted): **107,334,000**
- **TTM conservative OE total −$76,480,000 → −$0.71/share.** The TTM is worse than FY2025: capex is still accelerating into the build-out while OCF lags the capacity it is buying.

**Base used = $0.3654/share, declared as a base_override (kind "filing", see OVERRIDE).** Both engine-native bases are unusable: the normalized conservative base (3-yr median) is $0.04/share and the latest FY is −$0.40/share — both charge the full growth-capex program against current earnings power and would make every downstream figure a division by ~zero.

## OVERRIDE — base (bounded authority, filing-sourced construction)
- **Construction (only figures printed in this run's financials_history.csv):** maintenance OE/share by fiscal year — period 2024-01-01: $34,769,000 / 102,744,000 sh = $0.3384; period 2024-12-30: $38,036,000 / 104,098,000 sh = $0.3654; period 2025-12-29: $79,231,000 / 105,453,000 sh = $0.7513. **Median of the three: $0.3654** — the engine's own normalization convention (median of last 3 FY) applied to the maintenance definition instead of the conservative one.
- **Why this is in bounds:** the inputs are the company's filed figures for the filed periods, and the construction is quoted in full in judgment.json's base_override {value, source, reason}. No estimate, no external data.
- **Measured impact:** on the engine-native base ($0.04) the same scenario set produced weighted IV@15% $0.62; on the override base the weighted IV@15% is $5.65. The tier does not change — D on either base, and D in the bear and bull cases alike. The override exists so the shortfall is measurable (~94% below the price), not to manufacture a tier; score.json records it, and the ranking badges the name as override-based.

## Moat: 3/10 — weak
Justification: a cyclical PCB/RF manufacturer whose filed ROIC proxy (fundamentals.json, after-tax operating income over equity + debt − cash) ran 1.2–5.3% in six of the last nine fiscal years — FY2017 5.8%, FY2018-label 12.0%, then 3.8%, 4.3%, 1.2%, 5.3%, 5.3%, 1.7%, 3.9%, FY2025 10.3% — i.e. at or below the cost of capital through most of the cycle. Gross margin lived at 16.2–19.5% over FY2017–FY2024 before the AI mix shift lifted it to 20.7% (FY2025) and 21.2% (TTM, fundamentals.json). That history earns no wide-moat credit; the current strength is a technology-and-capacity lead, not a structural barrier.
- FOR: advanced N+M asymmetrical PCB technology for AI data centers — one of few scaled suppliers, adding capacity brownfield at speed; aerospace & defense franchise (mission systems, RF/microwave assemblies, $1.7B defense backlog, long program qualifications that are sticky once designed in); scale as one of the world's largest PCB makers; mix shift visibly lifting gross margin and ROIC.
- AGAINST: through-cycle ROIC at/below the cost of capital; PCB fabrication is capital-intensive and contestable — Asian rivals can add the same capacity, so the edge is timing, not structure; demand concentrated in the hyperscaler AI capex cycle that is also driving $1.6B of committed capacity spend — if AI spend digests, the new capacity is stranded cost; new capacity concentrated in China and Penang (tariff / export-control / geopolitical exposure); SBC climbing ($22,887,000 FY2024-label → $41,668,000 FY2025 → $61,341,000 TTM) with the share count creeping up ~0.5%/yr.
- A 3 gives CAP = 5.9 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 5.9 years, 15-year projection.

## DCF — final run (2026-10-17)
Growth recalibration (written reason): the engine's blended start is 6.15%, built from the pre-AI trough (revenue CAGR 5y 6.66%, 3y 5.24%). That blend is a backward average across an inflection and is below every current print: FY2025 revenue +19.0% YoY (dcf_numbers.json growth components), TTM revenue +27.6% YoY (fundamentals.json), Q2 2026 +37.4% YoY, FY2026 guided to ~$4.4B vs $2.91B filed for FY2025, and 15–20% organic growth guided for 2027–28. Scenario starts were therefore set via offsets (−0.01 / +0.06 / +0.16 / +0.24 / +0.34 vs the 6.15% blend) to 5.15% / 12.15% / **22.15%** / 30.15% / 40.15%. The base start (22.15%) sits below the TTM and Q2 prints because OE/share growth off a $0.37 maintenance base cannot compound at revenue-ramp rates for long, and because H2-weighted FY26 guidance implies the steepest growth is the current year. Probabilities shifted bear-ward from the 10/25/30/25/10 default to **15/30/30/17/8** per the OE_VOLATILE flag and the binary AI-capex exposure. OE multipliers stay at the defaults 0.75/0.90/1.00/1.10/1.25. Price $93.88.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | 5.15% | 0.75 | AI capex digests in 2027; new capacity underutilized; defense cushions, doesn't save | $2.46 | 2.84% |
| Bear | 30% | 12.15% | 0.90 | Growth halves vs guide; margins stall near 20%; EPIQ leverage bites | $3.75 | 3.04% |
| Base | 30% | 22.15% | 1.00 | Guided trajectory roughly delivered, then fades over the 5.9y CAP | $5.80 | 3.37% |
| Bull | 17% | 30.15% | 1.10 | N+M ramp + Syracuse/Europe capacity fills; operating leverage compounds | $8.22 | 3.78% |
| Super bull | 8% | 40.15% | 1.25 | AI build-out runs hot through 2028; TTMI holds share and pricing | $12.67 | 4.52% |

- **Probability-weighted: IV@15% $5.65 (−94.0% vs price), IV@12% $7.65, IV@10% $9.90, weighted IRR 3.36%, base-case IRR 3.37%**
- **Tier by numbers: D** (bear D, bull D — no band ambiguity). Diagnostics (dcf_numbers.json): OE yield 0.39%, terminal value 20.6% of IV@15%, scenario spread 5.14x, net debt 10.77x the normalized (override) OE base — and 97.3x the engine-native conservative base — 9.6 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (latest FY ended ~10 months ago): resolved by running ttm.py — TTM legs quoted above. The TTM conservative OE (−$0.71/share) is worse than FY2025, not better; the base does not use it, and the reason is the same capex supercycle, now also visible in the current-YTD capex leg ($169,205,000 in H1 2026 alone).
- **BASE_DIVERGENCE** (latest FY −$0.40 vs 3-yr median $0.04): both are distorted the same way — the conservative definition charges $292.6M of growth capex (2.7x D&A) as maintenance. The maintenance-definition median ($0.3654) is the base, via the declared override.
- **OE_VOLATILE** (OE/share spans >3x over 5 years): real cyclicality — conservative OE/share went $1.58 (FY2020-label) → $0.71 → $1.45 → $0.04 → $0.21 → −$0.40. Handled with the normalized median base (not the peak, not the trough) and bear-ward probabilities (45% on bear-or-worse).
- **NI_OCF_DIVERGENCE** (2024, both fiscal years ending in calendar 2024): in the year ended 2024-01-01, net income was −$18,718,000 vs OCF $187,284,000; the gap is mostly non-cash — D&A alone was $99,155,000 that year, plus SBC $22,887,000 (financials_history.csv) — not a cash-quality red flag. In the year ended 2024-12-30, net income $56,299,000 vs OCF $236,894,000, again D&A $105,233,000 plus SBC $29,780,000. The OE base is OCF-derived, so the divergence does not contaminate it either way.
- **IRR_AT_FLOOR** (super bear only in the final run): the super-bear IRR of 2.84% sits within 0.5pp of the 2.5% terminal growth rate — read it as "at most ~3%", not a precise figure. The weighted IRR (3.36%) is above the floor but the message is the same: at $93.88 the model cannot find a return worth naming in any scenario (best case, super bull, is 4.52%).
- **LOW_OE_YIELD** (0.39% on the override base; 0.04% on the engine-native base): conceded in full. The valuation rests almost entirely on growth that has not yet converted to owner's earnings — exactly why the tier is D and confidence is low.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 5.14x super-bear): real uncertainty, driven off a near-zero base. Confidence capped at low; verdict sized to the conservative end.
- **HIGH_NET_DEBT** (net debt 10.77x normalized OE on the override base; 97.3x on the engine-native base): the balance sheet itself is not stretched today — net debt $414,917,000 on $9.9B market cap, plus $96,433,000 lease liabilities — but the OE denominator is tiny, and the pending $1.1B cash EPIQ acquisition takes net leverage to ~2.3x per deal coverage. The multiple is a statement about earnings power, not about today's leverage; the EPIQ debt load is the forward risk if the cycle turns mid-build.

## My thoughts / overlay
- The honest headline is the *distance*, not the tier letter: the weighted IV@15% of $5.65 sits 94.0% below the $93.88 price (key_numbers.md upside @15%). Even the super-bull case (40% OE growth start, 1.25x OE multiplier) values the share at $12.67. No defensible owner's-earnings method gets within an order of magnitude of $93.88, because the market is not paying for owner's earnings — it is paying ~19x guided non-GAAP EPS approaching $5.00, a figure that excludes SBC ($61.3M TTM and climbing) and treats a $1.6B capacity program as free.
- Method range: engine-native conservative base → weighted IV@15% $0.62; maintenance-median override base → $5.65; even pinning the base to the *latest* FY maintenance figure ($0.75/share, the friendliest filed year) would only roughly double the override IV — still ~92% below the price. The conclusion is method-insensitive: D on every defensible base.
- What would have to be true: the new capacity must convert to sustained OCF at a rate TTMI has never filed — ROIC stayed in single digits through the last full cycle — and stay there long enough to grow OE/share ~50-fold. Possible in an AI supercycle; it is a speculation on capacity economics, not an investment at a 15% hurdle.
- Watch items for pass 2: H2 2026 capex pace vs the $400M increment; whether OCF inflects as N+M capacity ships; EPIQ close terms and leverage; SBC trajectory (the quiet dilution funding part of the story); any ROIC print above ~12% sustained, which would be the first evidence the moat score is too low.

## Final verdict
- **Final tier: D** (weighted IRR 3.36% on the final inputs; bear and bull both D; D on every defensible base — method range $0.62–$5.65 weighted IV@15% vs the $93.88 price)
- Confidence: **Low** (high that the price embeds far more than filed owner's earnings support; low on any single growth path — scenario spread 5.14x)
- One-liner: Real AI/defense growth story with a weak moat (3/10) and a capex supercycle that swallows owner's earnings — even on a maintenance-capex base and guided growth it does not clear 15% at $93.88 (weighted IRR 3.36%, weighted IV@15% $5.65; clears 15% only below ~$5.65); the price capitalizes the bull case and then some, it does not discount it.
