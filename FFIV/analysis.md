# FFIV — F5, Inc.
v5 run, 2026-10-14. In scope: market cap $27.1648B at $462.90 (nasdaq_quote_api), under the $40B cutoff. All figures below are copied from dcf_numbers.json, ttm.py output (ttm.json), financials_history.csv, or key_numbers.md — none are recomputed.

## What it is
The incumbent in application delivery and security: BIG-IP application delivery controllers, NGINX, and a growing security stack (WAAP, API security, bot/DDoS defense, and new AI application security — AI Guardrails / AI Red Team). Q3 FY26 (ended 2026-06-30, reported 2026-07-27): revenue $865.1M, +10.9% YoY, with systems revenue +32% and product revenue +19%, software revenue +7% (subscriptions 90% of software revenue), services +3%. Management raised the FY26 revenue-growth outlook to 9–10% (its third raise of the year) and non-GAAP EPS guidance to $17.21–$17.33.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $949,666,000; capex $43,260,000; SBC $231,491,000 (always a real cost); net income $692,380,000.
- **Conservative owner's earnings FY2025: $674,915,000 = $11.50/share** (latest FY OE/share, dcf_numbers.json)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $724,888,000 — same ballpark as the conservative figure, which raises confidence.
- OE positive 5 of the last 5 fiscal years. Balance sheet: the history file shows cash $1,344,273,000 at FY2025 with no debt figures tagged for that period, and the engine reports net_debt_latest as null — no HIGH_NET_DEBT or BIG_NET_CASH flag fired.
- SBC load is material: $231,491,000 in FY2025 and $250,783,000 TTM against TTM OCF of $1,049,441,000 — a real, ongoing dilution cost, partly offset by buybacks (share count CAGR −1.33%/yr, credited in the growth blend).

**Base used = TTM owner's earnings through Q3 FY2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $949,666,000 − prior YTD $741,598,000 + current YTD $841,373,000 = **TTM $1,049,441,000**
- Capex: FY $43,260,000 − prior YTD $27,119,000 + current YTD $63,705,000 = **TTM $79,846,000**
- SBC: FY $231,491,000 − prior YTD $174,243,000 + current YTD $193,535,000 = **TTM $250,783,000**
- Shares (current-YTD weighted diluted): **57,674,000**
- **TTM OE total $718,812,000 → base OE/share $12.4634** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $9.1460/share — rejected as the base because it averages in the soft FY2022–23 years; the latest FY ($11.5008/share) and the filing-derived TTM ($12.4634/share) are the current run-rate. The median is still reported in key_numbers.md.

## Moat: 6/10 — moderate-strong, not wide
Justification: BIG-IP installed-base switching costs, WAAP leadership and an early AI-security position, on a mature, low-growth core that hyperscaler bundling and the cloud shift steadily erode.
- FOR: BIG-IP installed base in mission-critical traffic paths — high switching costs; Leader in application delivery / WAAP and one of only two Gartner Market Shapers in AI application security (Sept 2026); recurring base — services ~46% of Q3 FY26 revenue, subscriptions 90% of software revenue; gross margins above 82% and owner's earnings positive 5 of the last 5 years — pricing power held through a cycle; hybrid multicloud, on-prem and air-gapped reach that hyperscaler-native tools do not match.
- AGAINST: hyperscaler-bundled load balancing and security (AWS / Azure / Google) plus Cloudflare at the edge; secular shift from on-prem ADC hardware toward cloud / SaaS delivery; mature core — 5-yr revenue CAGR 5.61%, Q3 FY26 software revenue only +7% YoY; 40+ vendors contesting AI application security, so the growth-layer lead must be re-earned; systems / component-cost cyclicality (FY2022 operating cash flow dipped to $442,631,000).
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
The engine's blended growth is 7.63% (components: rev CAGR 5y 5.61%, rev CAGR 3y 4.63%, latest rev YoY 9.66%, OE/share CAGR 2y 38.24% — the last is an artifact of the soft FY2023 base and is not taken at face value), plus a +1.33pp share-count adjustment, for g_base 8.97%. Sanity check against actual prints: the base start of 8.97% sits right against the real run-rate — FY26 revenue growth guided to 9–10% and Q3 FY26 revenue +10.9% YoY. The bull (13.97%) and super-bull (20.97%) starts sit above anything F5 currently prints; they are deliberately optimistic cases (sustained systems refresh + AI-security acceleration), and even they do not clear the hurdle — see the table. Default probabilities 10/25/30/25/10 and default OE multipliers were kept: the evidence does not justify skewing either way. Price $462.90.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -3.03% | 0.75 | Cloud shift bites the ADC base; systems cycle reverses | $59.93 | 3.98% |
| Bear | 25% | 3.97% | 0.90 | Growth fades back to the historical ~4-5% revenue trend | $98.18 | 5.20% |
| Base | 30% | 8.97% | 1.00 | Guided 9-10% growth decays normally over the CAP | $136.27 | 6.43% |
| Bull | 25% | 13.97% | 1.10 | Systems refresh + AI security sustain low-teens growth | $187.11 | 8.02% |
| Super bull | 10% | 20.97% | 1.25 | AI-security category win; growth re-accelerates durably | $289.43 | 10.91% |

- **Probability-weighted: IV@15% $147.14, IV@12% $198.90, IV@10% $257.08, weighted IRR 6.82%, base-case IRR 6.43%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 2.69%, terminal value 20.5% of IV@15%, scenario spread 4.83x, 12.5 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (latest FY ended 12.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q3 FY2026, quoted in full above, and the final engine pass ran with `--ttm`.
- **OE_VOLATILE** (OE/share range over the last 5 years spans >3x): real and identified — the trough is FY2022, when operating cash flow fell to $442,631,000 (financials_history.csv) before recovering to $949,666,000 by FY2025. It is cash-flow cyclicality (systems / component-cost driven), not a broken business: OE stayed positive 5 of the last 5 years. Handled by the TTM base (which uses the recovered run-rate, not the trough or the peak) and by keeping the full default bear weight (35% on bear-or-worse).
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.83x super-bear IV): real — the range is driven by the growth-duration question, not by base quality. Confidence is capped at medium, and the verdict is sized to the conservative end. Note the spread does not straddle the hurdle: every scenario, super bull included, prices below the current price at a 15% discount.

## My thoughts / overlay
- Quality is not the debate; price is. This is a profitable, cash-generative incumbent with 82%+ gross margins, a recurring base, and growth that has genuinely re-accelerated (revenue +10.9% in Q3 FY26, guidance raised three times). The problem is the 2.69% base OE yield at $462.90: the stock trades near the top of analyst targets (consensus ~$438 per search results) and the DCF cannot get near the price under any scenario — even the super bull (20.97% growth start, 1.25x OE) yields only a 10.91% IRR.
- The method range is narrow here, which is itself informative: on the rejected 3-yr-median base ($9.1460/share) the preliminary run gave a weighted IRR of 5.57% and weighted IV@15% of $104.89 — Tier D as well. Defensible inputs span D to D.
- Price that clears the hurdle: the weighted IV@15% of **$147.14** is the price at which the weighted case earns 15%; with any margin of safety the entry would need to be below that. At $462.90 the price is more than 3x that level — this is not a close call that better moat arguments can rescue.
- Risks to this (bearish) verdict: a sustained AI-infrastructure spending cycle could keep systems growth elevated longer than the fade assumes, and buybacks (share count −1.33%/yr) add a modest per-share tailwind already credited in the blend. Neither closes a gap of this size.

## Final verdict
- **Final tier: D** (weighted IRR 6.82% on the v5 final inputs; no tier override)
- Confidence: **Medium** (capped by the wide scenario spread; high on the base's filing quality, low on any single growth path)
- One-liner: High-quality app-delivery/security incumbent, moat 6/10 — but at $462.90 it does not come close to the 15% hurdle: weighted IRR 6.82%, weighted IV@15% $147.14; it would need to fall to roughly $147.14 to clear 15%.
