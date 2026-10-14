# CTSH — Cognizant Technology Solutions Corporation
v5 run, 2026-10-14. In scope (market cap $30.734B at $62.85, nasdaq_quote_api) — see key_numbers.md.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed.

## What it is
Large global IT services and consulting firm: it builds and runs systems for large enterprises, paid time-and-materials or on managed-services terms, delivered predominantly from India and billed at Western rates. Segments span Financial Services, Health Sciences, Products and Resources, and Communications/Media/Technology. Management now brands it an "AI builder" and technology services provider. Q2 2026 (reported July 29, 2026, via search of the company's release): revenue $5.5 billion, up 4.5% year-over-year (4.1% constant currency), Financial Services up 12%, GAAP EPS $1.36 / adjusted EPS $1.37, trailing 12-month bookings $29.1 billion up 5% (book-to-bill ~1.3x) although Q2 bookings themselves fell 6% year-over-year; full-year 2026 constant-currency revenue growth guidance revised to 4.0% to 5.5%, adjusted operating margin guidance 16.0% to 16.2%, adjusted diluted EPS guidance raised to $5.70 to $5.82.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $2,883,000,000; capex $288,000,000; SBC $181,000,000 (always a real cost).
- **Conservative owner's earnings FY2025: $2,414,000,000 = $4.94/share** (key_numbers.md: latest FY OE/share $4.94, latest FY OE total $2.414B)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC, from financials_history.csv): $1,922,000,000 for FY2025 — below the conservative figure, which is a caution: the OCF rebound in FY2025 was stronger than the earnings-based measure. The conservative OCF-based series is the one used throughout.
- OE positive 5 of the last 5 fiscal years. Net debt (latest, key_numbers.md): $-1.358B — i.e. net cash on the FY2025 balance sheet; net debt / normalized OE -0.58x. Balance-sheet caveat post-FY end: the Astreya acquisition closed in Q2 2026 for $634 million, funded in part by a $1.0 billion revolver draw (per Q2 2026 search results) — so the FY2025 net-cash position overstates today's cushion; the company also deployed $1.153 billion on Q2 2026 buybacks ($1.6 billion in H1 2026, $2.3 billion authorization remaining). This is folded into the verdict: no balance-sheet premium is credited.

**Base used = TTM owner's earnings through Q1 2026, from ttm.py (filing-direct, no hand math; ttm.json's latest YTD leg is Q1 2026):**
- OCF: FY $2,883,000,000 − prior YTD $400,000,000 + current YTD $274,000,000 = **TTM $2,757,000,000**
- Capex: FY $288,000,000 − prior YTD $77,000,000 + current YTD $76,000,000 = **TTM $287,000,000**
- SBC: FY $181,000,000 − prior YTD $42,000,000 + current YTD $46,000,000 = **TTM $185,000,000**
- Shares (current-YTD weighted diluted): **477,000,000**
- **TTM OE total $2,285,000,000 → base OE/share $4.79** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $3.64/share — rejected as the base: the median year is FY2023, whose OCF ($2,330,000,000 in financials_history.csv) and FY2024's ($2,124,000,000) were the weak trough years, while FY2025 ($2,883,000,000) and the TTM figure ($2,757,000,000) corroborate each other at the higher level. The median is still reported in key_numbers.md. Caution retained: FY2025's OCF jump is a rebound off a trough, not proof of a new growth rate — handled in the growth recalibration below, not by reverting to the trough median.

## Moat: 5/10 — moderate / narrow
Justification: embeddedness in client estates creates real switching costs and scale/global delivery sustains ~16% operating margins, but the core product is replicable labour services with weak contractual lock-in and an AI threat to the headcount model itself.
- FOR: Embeddedness in client estates — institutional knowledge of a payer's claims platform or a bank's core operations is expensive to rebuild; proprietary TriZetto healthcare software inside client revenue cycles, not just services; scale and global delivery — predominantly India-based workforce billed at Western rates, vertical expertise in Financial Services and Health Sciences; proven cash generation through a cycle — OE positive 5 of last 5 FY, ~16% operating margin, net cash on the FY2025 balance sheet.
- AGAINST: Labour-arbitrage model is replicable — Accenture, TCS, Infosys and Wipro match scale and delivery; no structural cost moat; weak contractual lock-in — many contracts are short-term and terminable on short notice, visibility comes from bookings, not lock-in; AI automation threat — AI-led productivity deflates the headcount pyramid the model is built on, and the Project Leap restructuring (expected to cost $230 million to $320 million in 2026, per Q2 2026 search results) is the admission; wage inflation, attrition (13.0% voluntary Tech Services TTM at Q2 2026) and pricing pressure cap pricing power.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Growth recalibration (written reason): the engine's g_base is 7.87% (growth blend 5.90% — rev CAGR 5y 4.86%, rev CAGR 3y 2.80%, latest rev YoY 6.95%, OE/share CAGR 2y 16.48% — plus the share-count adjustment). The OE/share CAGR component is a rebound artifact off the FY2023-24 OCF trough, and 7.87% sits above every revenue print and above management's own 4.0% to 5.5% constant-currency guidance for 2026 (Q2 2026 printed +4.5% / +4.1% CC). Scenario starts were therefore set via offsets (−0.15 / −0.08 / −0.03 / +0.02 / +0.07 vs g_base) to −7.1% / −0.1% / **4.9%** / 9.9% / 14.9% — the base start sits inside guidance, the bull start requires sustained share gains / AI-services acceleration beyond guidance, and super bull requires a step-change no recent print supports (hence only 10%). Probabilities 10/30/30/20/10 were skewed one notch bearish vs the 10/25/30/25/10 defaults on the Q2 bookings decline (−6% YoY), the Project Leap restructuring load, and growth concentration in Financial Services (the other three segments grew only ~1-2% in Q2 2026 per search results). OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $62.85.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -7.1% | 0.75 | AI deflation hits the headcount model; bookings slide turns into revenue decline | $19.68 | 6.04% |
| Bear | 30% | -0.1% | 0.90 | Growth stalls near zero; restructuring and wage pressure squeeze OE | $31.68 | 8.70% |
| Base | 30% | 4.9% | 1.00 | Guided 4-5.5% growth decays normally over the CAP | $43.35 | 11.19% |
| Bull | 20% | 9.9% | 1.10 | AI-services demand and Financial Services momentum broaden to other segments | $58.63 | 14.22% |
| Super bull | 10% | 14.9% | 1.25 | Durable double-digit compounder path — not in any recent print | $81.76 | 18.29% |

- **Probability-weighted: IV@15% $44.38 (−29.4% vs price), IV@12% $58.97 (−6.2%), IV@10% $75.24, weighted IRR 11.43%, base-case IRR 11.19%**
- **Tier by numbers: C.** Diagnostics (key_numbers.md): OE yield 7.62%, terminal value 18.8% of IV@15%, scenario spread 4.15x, net debt −0.58x normalized OE, 9.4 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.4 months ago): resolved by construction — the base is the TTM figure from ttm.py, quoted above with all its inputs. Note ttm.py's latest YTD leg is Q1 2026; Q2 2026 evidence (revenue +4.5%, EPS guidance raised) was used for the growth sanity check and scenario calibration, not to hand-build a newer TTM base.
- **BASE_DIVERGENCE** (latest FY $4.94 vs 3-yr median $3.64): the median is the distorted one — it is the FY2023 trough year (OCF $2,330,000,000; FY2024 was lower still at $2,124,000,000, both from financials_history.csv). FY2025 OCF $2,883,000,000 and the TTM OCF $2,757,000,000 corroborate the higher level, so the TTM base ($4.79) is used. The residual caution — that FY2025 is a rebound and the maintenance OE ($1,922,000,000) is lower — is carried in the growth recalibration and the 40% weight on bear-or-worse, not ignored.
- **WIDE_SCENARIO_SPREAD** (4.15x): real for a business mid-AI-transition — outcomes range from headcount-model deflation to an AI-services re-acceleration. Confidence is medium (never high with this flag), and the verdict is sized to the conservative end.

## My thoughts / overlay
- Method range: on the preliminary run (median base $3.64, default offsets/probabilities) the weighted IRR was 10.67% (Tier C); on the final TTM base with guidance-calibrated growth it is 11.43% (Tier C). The tier is stable across the defensible inputs — the finding is a solid C, not a borderline B: even the bull case (14.22% IRR, IV@15% $58.63) sits below the $62.85 price, and only the 10%-weighted super bull clears the price.
- Quality is not the debate: OE positive 5/5 years, SBC is small ($185,000,000 TTM) relative to OCF, capex is light ($287,000,000 TTM), buybacks shrink the count (share count CAGR −1.96%, already credited via the growth adjustment in the blend; Q1 2026 TTM share leg 477,000,000 vs 489,000,000 latest FY). The debate is purely growth: a ~5% grower cannot clear a 15% hurdle at an OE yield of 7.62% unless the price falls or growth re-accelerates durably.
- Red flags / watch items: Q2 2026 bookings −6% YoY against a +5% TTM line; growth concentration in Financial Services; Project Leap restructuring costs of $230 million to $320 million expected in 2026; Astreya debt-funded acquisition post-FY end; voluntary attrition rising to 13.0%.
- Price that clears 15%: the weighted IV@15% itself, $44.38. With a margin of safety against the bear case (IV@15% $31.68), a buyer needs roughly $35 — the ~$44 level only pays for the weighted case, not insurance against the bear case.

## Final verdict
- **Final tier: C** (weighted IRR 11.43% on the v5 final inputs; Tier C on both the preliminary median-base run and the final TTM-base run)
- Confidence: **Medium** (high on OE quality and the filing-derived TTM base, medium-low on the growth path — scenario spread is 4.15x)
- One-liner: Solid, cash-generative IT-services franchise, moat 5/10 — but slow guided growth (4.0-5.5% CC for 2026) does not clear 15% at $62.85 (weighted IRR 11.43%, IV@15% $44.38); clears 15% only at or below $44.38, ~$35 with a margin of safety.
