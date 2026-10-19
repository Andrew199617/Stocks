# SWKS — Skyworks Solutions, Inc.
Engine 5.4.0 run, 2026-10-18. Price $79.70 (nasdaq_quote_api), market cap est $12.36B on the pre-merger share count (see POST-PERIOD EVENT — the Qorvo combination closed 2026-10-05 and the combined share count is larger).

All figures below are copied from dcf_numbers.json, ttm.json, fundamentals.json or financials_history.csv — none are recomputed.

## What it is
Analog / mixed-signal and RF front-end semiconductors: power amplifiers, filters and integrated modules for smartphones (Mobile), plus Broad Markets — automotive, data center, edge IoT, industrial and infrastructure. Its largest customer accounted for ~67% of FY2025 revenue (MarketBeat) and ~57% of Q3 FY2026 revenue (Semiconductor Today); Broad Markets was ~43% of Q3 FY2026 revenue, up 8% year over year, led by automotive and data center.

## POST-PERIOD EVENT — Qorvo combination closed 2026-10-05
Every filing in this run's history is standalone Skyworks: FY2025 ended 2025-10-03 and the latest 10-Q period ended 2026-07-03. On 2026-10-05 the Qorvo combination closed (announced 2025-10-28): each Qorvo share converted into $32.50 cash plus 0.960 Skyworks shares, former Qorvo holders own ~37% of the combined company on a fully diluted basis, and Skyworks issued ~$2B of senior notes in August 2026 ($800M due 2028 at 5.000%, $600M due 2032 at 5.750%, $600M due 2036 at 6.250%, per the closing coverage). The company claims $500M+ of annualized cost synergies within 24–36 months and immediate non-GAAP EPS accretion — unproven, and none of it (Qorvo earnings, synergies, new shares, new debt) is in the engine's inputs. **The per-share figures below are therefore standalone-basis: the $79.70 price is a claim on the combined company, while the OE base and the 155.1M share count are the old company's.** The verdict is sized conservatively for that reason and confidence is low; a combined-basis re-score has to wait for combined filings (first: Q1 FY2027 10-Q).

## Owner's earnings
**FY2025 (10-K via EDGAR, financials_history.csv):** OCF $1,300,800,000; capex $195,000,000; SBC $232,400,000 (always a real cost).
- **Conservative owner's earnings FY2025: $873,400,000 = $5.63/share** (dcf_numbers.json base_oe_latest_per_share)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $838,600,000 — close to the conservative figure.
- OE positive 5 of the last 5 fiscal years. Net debt −$664,900,000 (net cash; basis TOTAL:LongTermDebt) plus lease liabilities $207,300,000 — the standalone balance sheet at FY2025 end; it does not include the ~$2B of merger notes issued in August 2026.
- The earnings trend is down hard: operating income $1,612,700,000 (FY2021) → $1,527,000,000 → $1,125,000,000 → $637,400,000 → $500,000,000 (FY2025), and $305,400,000 TTM (fundamentals.json). Revenue fell three straight fiscal years: $5,485,500,000 (FY2022) → $4,772,400,000 → $4,178,000,000 → $4,086,900,000 (FY2025).

**TTM through Q3 FY2026, from ttm.py (filing-direct):**
- OCF: FY $1,300,800,000 − prior YTD $1,100,800,000 + current YTD $516,200,000 = **TTM $716,200,000**
- Capex: FY $195,000,000 − prior YTD $139,000,000 + current YTD $226,000,000 = **TTM $282,000,000**
- SBC: FY $232,400,000 − prior YTD $168,900,000 + current YTD $168,900,000 = **TTM $232,400,000**
- Shares (current-YTD weighted diluted): **150,800,000**
- **TTM OE total $201,800,000 → $1.34/share.** Quarterly OCF fell to $50,300,000 (quarter ended 2026-04-03) and $70,400,000 (2026-07-03) against $409,400,000 and $314,200,000 in the year-ago quarters (fundamentals.json) — a working-capital build reversing the release years, on top of real margin compression (TTM gross margin 40.73%, operating margin 7.61%).

**Base used = latest complete FY, $5.631205673758865/share, pinned via base_override** (see OVERRIDE). The engine's normalized base (3-yr median) is $9.11/share; the TTM base is $1.34/share. The FY2025 base still contains a $277,800,000 working-capital release (ΔNWC, financials_history.csv), so it is generous relative to the TTM print — deliberately: it is the most recent *complete* fiscal year, with a full seasonal cycle, rather than a nine-month WC-build trough or two WC-release years.

## OVERRIDE — base (bounded authority (c))
- judgment.json carries `base_override = {value: 5.631205673758865, source: "dcf_numbers.json base_oe_latest_per_share, built from financials_history.csv FY2025 row (10-K, period ended 2025-10-03): OCF $1,300,800,000 − capex $195,000,000 − SBC $232,400,000 = conservative OE $873,400,000 over 155,100,000 diluted shares"}` — a figure printed by this run's engine outputs, no outside numbers.
- **Measured impact:** on the median base the preliminary run gave weighted IRR 12.07%, weighted IV@15% $61.71, Tier C. On the pinned base the final run gives weighted IRR 8.41%, IV@15% $38.55, Tier D. On the TTM base ($1.34/sh) the same model would print near Tier F. The method range is the finding (see Thoughts).

## Moat: 4/10 — weak, eroding
Justification: real design-win franchise and RF scale, but measured returns have fallen through the cost of capital — ROIC proxy 22.7% (FY2020 and FY2021) → 20.0% → 16.1% → 10.0% → 8.9% (FY2025), gross margin 49.2% (FY2021) → 47.5% → 44.2% → 41.2% → 41.2% (FY2025), 40.73% TTM (fundamentals.json roic_proxy and gross-margin series). A moat of 7+ needs ROIC held well above the cost of capital through a cycle; Skyworks shows the opposite trajectory.
- FOR: RF front-end oligopoly with deep design-win integration in flagship Apple and Android phones and in-house GaAs manufacturing; patent estate (~5,200 patents standalone per the company IR page; 12,000+ issued and pending combined after the Qorvo close); Broad Markets diversification working (~43% of Q3 FY2026 revenue, +8% YoY); the Qorvo combination adds RF/analog/power scale and removes a direct rival.
- AGAINST: largest customer ~67% of FY2025 revenue (~57% in Q3 FY2026) and that customer dual-sourced a premier RF socket for the iPhone 17 — a 20–25% content loss at that socket (Semiconductor Today, 2026-08-06); sockets are re-competed every phone generation; Qualcomm bundles RF with Snapdragon and Broadcom holds premium filter slots; revenue fell three straight fiscal years; Qorvo integration risk with ~$2B of new debt and $500M+ of claimed, unproven synergies.
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — final run (2026-10-18)
Growth sanity check (written reasons): the engine blend is −4.05%. Scenario starts use the default offsets (−12/−5/0/+5/+12pp; the super-bear start floors at −10%). The anchor prints are revenue, not the WC-distorted OE prints: FY2025 revenue −2.18% YoY (dcf_numbers.json), TTM revenue +0.06% YoY (fundamentals.json), Q3 FY2026 revenue $934.8M, −3.1% YoY. Base −4.05% OE/share growth sits on those prints with continued margin pressure; bull +0.95% is roughly the flat TTM revenue print plus Broad Markets growth — it is *not* below the latest revenue print, and no scenario is anchored on the TTM OE print (−82% YoY OE in fundamentals.json), which is a working-capital swing, not a growth rate. Super bull +7.95% requires mobile stabilization plus Broad Markets compounding; weighted only 10%. Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25. Price $79.70.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | −10.0% | 0.75 | Further Apple content loss; handset downturn; merger indigestion | $21.24 | 5.47% |
| Bear | 25% | −9.05% | 0.90 | Content losses stick, margins keep sliding toward TTM levels | $26.47 | 6.28% |
| Base | 30% | −4.05% | 1.00 | Revenue roughly flat-to-down, slow margin bleed, Broad Markets offsets mobile | $35.81 | 7.90% |
| Bull | 25% | +0.95% | 1.10 | Mobile stabilizes, Broad Markets growth carries the mix | $47.84 | 9.96% |
| Super bull | 10% | +7.95% | 1.25 | Content regained, synergies land, Broad Markets compounds | $71.06 | 13.70% |

- **Probability-weighted: IV@15% $38.55 (−51.6% vs price), IV@12% $50.25, IV@10% $63.20, weighted IRR 8.41%, base-case IRR 7.90%**
- **Tier by numbers: D** — and bear and bull cases are also D, so no tier band. Diagnostics (dcf_numbers.json): OE yield 7.07%, terminal value 16.9% of IV@15%, scenario spread 3.35x, net debt −0.76x normalized OE (net cash), 12.5 months since FY end.
- Hurdle prices: clears 15% at $38.55, 20% at $27.91, 25% at $21.95.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 12.5 months ago): ttm.py run and its legs quoted above. The TTM base ($1.34/sh) was NOT used: its OCF leg is a working-capital-build trough (quarterly OCF $50.3M/$70.4M in the last two quarters vs $409.4M/$314.2M year-ago) in the pre-close merger period. Base pinned to the latest complete FY instead; the TTM collapse is carried as downside evidence and in the method range.
- **NI_OCF_DIVERGENCE** (NI vs OCF differ by >40% in 2023, 2024, 2025): the gap runs OCF *above* NI — FY2023 NI $982,800,000 vs OCF $1,856,400,000; FY2024 NI $596,000,000 vs OCF $1,824,700,000; FY2025 NI $477,100,000 vs OCF $1,300,800,000 (financials_history.csv). It is non-cash addbacks (D&A $387,800,000/$264,800,000/$278,700,000 and SBC $185,100,000/$180,300,000/$232,400,000) plus working-capital release as revenue contracted (ΔNWC −$131,800,000/−$434,700,000/−$277,800,000). No single tax-deposit or impairment one-off is tagged in the computed outputs; the risk is the reverse of the usual one — OCF-based OE *overstates* run-rate earnings in release years — and it is handled by the base pin and confirmed by the FY2026 reversal, when the WC build dragged TTM OCF to $716,200,000.
- **BASE_DIVERGENCE** (latest FY $5.63 vs 3-yr median $9.11): the median is the distorted one — its anchor years FY2023 ($9.11/sh) and FY2024 ($9.21/sh) capitalize the WC-release OCF above. Latest FY pinned as the base (see OVERRIDE, with the tier on each base stated there); even it retains a $277,800,000 release, so the pin errs on the generous side.
- **TIER_BAND** (preliminary run: bear D 8.5% vs bull C 14.6%): on the final pinned base, bear and bull are both D — the band is gone and the verdict is sized to the bear end anyway.

## My thoughts / overlay
- The honest headline is the method range: Tier C on the engine's median base (weighted IRR 12.07%), Tier D on the latest-FY base (8.41%), near F on the TTM base. Every base is defensible from the filings; they disagree because FY2023–25 cash flow was flattered by liquidating working capital from a shrinking revenue base and FY2026 TTM is depressed by rebuilding it. The pinned FY2025 base is the middle, most complete-year choice.
- Quality check: this was a genuinely good business — ROIC above 20% and ~49% gross margins in FY2020–21. The measured franchise now earns 8.9% ROIC at 41% gross margins with revenue down three straight years and its dominant customer actively dual-sourcing. That is erosion, not a cycle print.
- The Qorvo combination could change the answer in either direction (scale + $500M+ claimed synergies vs ~$2B of new debt, a ~59% larger share count, and integration risk), but none of it is scoreable from filings yet: no combined financial statements exist. Treat this score as the standalone floor case and re-run on the first combined 10-Q.
- Dividend: DPS TTM $2.84 declared, 12 growth years, no cut on record in fundamentals.json — the payout is real, but on the pinned base it is a large share of owner's earnings, which limits self-funded merger deleveraging.

## Final verdict
- **Final tier: D** (weighted IRR 8.41% on the pinned latest-FY base; method range C on the median base to near-F on TTM)
- Confidence: **Low** (base divergence across a 7x OE range, a working-capital swing dominating recent cash flow, and a transformative merger closed after every filing in the model)
- One-liner: RF front-end franchise in structural erosion, moat 4/10 — does not clear 15% on the latest-FY base (8.4% weighted, IV $38.55 vs $79.70); clears 15% only below ~$39, and the Qorvo combination that closed 2026-10-05 makes even that a standalone-basis figure pending combined filings.
