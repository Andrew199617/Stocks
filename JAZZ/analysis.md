# JAZZ — Jazz Pharmaceuticals plc
Engine 5.4.0 pass-1 run, 2026-10-17. Market cap (est) $12.820B at $210.23 (nasdaq_quote_api) — in scope under $40B.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
Irish-domiciled specialty pharma. Neuroscience: Xywav/Xyrem (oxybate for narcolepsy and idiopathic hypersomnia, REMS controlled distribution) and Epidiolex/Epidyolex (cannabidiol for rare epilepsies, ex-GW Pharmaceuticals). Oncology: Zepzelca, Rylaze, Vyxeos, Defitelio, plus the two growth launches — Ziihera (zanidatamab, HER2+; first-line GEA approval Aug 2026) and Modeyso (dordaviprone, from the 2025 Chimerix acquisition). Q2 2026 (10-Q filed 2026-08-03; press release): record revenue $1.21B, +16% YoY — Xywav $471M (+13%), Epidiolex $292M (+16%), oncology +32% — and management raised 2026 revenue guidance to $4.60–4.75B vs FY2025 revenue $4,267,586,000 (+4.88% YoY, financials_history.csv).

## Owner's earnings
**FY2025 (10-K via EDGAR, financials_history.csv):** operating cash flow $1,355,773,000; SBC $291,133,000 (always a real cost); capex $58,752,000.
- **Conservative owner's earnings FY2025: $1,005,888,000 = $16.50/share** (latest FY OE/share, key_numbers.md)
- Maintenance version FY2025: $289,820,000 — far below the conservative figure because it charges the full intangible-amortization-heavy D&A/NWC swing of an acquisition-built balance sheet; the OCF-based conservative figure is the cleaner one here (see NI_OCF_DIVERGENCE below).
- OE positive 5 of the last 5 fiscal years. Net debt $3,966,358,000 (key_numbers.md: $3.966B) plus lease liabilities $65,170,000 (dcf_numbers.json).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,355,773,000 − prior YTD $518,600,000 + current YTD $823,900,000 = **TTM $1,661,073,000**
- SBC: FY $291,133,000 − prior YTD $132,200,000 + current YTD $147,800,000 = **TTM $306,733,000**
- Capex: FY $58,752,000 − prior YTD $26,800,000 + current YTD $37,800,000 = **TTM $69,752,000**
- Shares (current-YTD weighted diluted): **67,800,000**
- **TTM OE total $1,284,588,000 → base OE/share $18.95** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $16.50/share. The TTM base is preferred: it is more current (STALE_FY), and the FY2025 diluted count of 60,981,000 was depressed because FY2025 was a GAAP loss year (dilutive securities excluded); the TTM's 67,800,000 diluted count is the more honest denominator. Even so, the gap matters — see method range under Thoughts.
- **Caveat that cuts the other way:** Jazz buys its pipeline. Acquired IPR&D was $947,862,000 in FY2025 (10-K cash-flow reconciliation: the Chimerix charge, $905.4M of it in Q2 2025) and the cash sat in investing ($858,053,000 asset acquisition), so none of it touches OCF or capex — owner's earnings as defined here excludes a cost this company incurs repeatedly (Actio Biosciences closed 2026-09-15 for $820M upfront, after the TTM window). The bear scenarios' 0.75–0.90 OE multipliers are partly a charge for this.

## Moat: 5/10 — moderate/narrow
Justification: patent-protected niche franchises with real friction, but returns on the acquisition-inflated capital base have been poor for five years and the largest franchise is entering its generic-pressure window.
- Evidence (fundamentals.json): roic_proxy was 12.5% / 10.7% / 12.9% / 10.3% in 2016–19, then 7.1% (2020), 1.4% (2021, GW acquisition year), −0.7% (2022), 5.8% (2023), 7.3% (2024), −4.1% (2025, IPR&D-depressed). Gross margin is not filed in a form fundamentals.json captures (cogs null); company guidance puts GAAP gross margin at ~88% (non-GAAP ~92%) — pricing power at the product level is real, it is the capital base that earns poorly.
- FOR: oxybate REMS controlled-distribution platform creates switching friction for Xywav/Xyrem; Epidiolex patent protection into the late 2030s (ANDA litigations resolved); high product gross margins on orphan/rare-disease pricing; diversifying oncology launches (Ziihera peak sales estimate raised to $3–5B after the GEA approval; Modeyso).
- AGAINST: ROIC collapse post-GW (above); Xywav concentration (~39% of Q2 2026 revenue) facing generic high-sodium oxybate payer pressure from H2 2026 and once-nightly Lumryz; orexin agonists in development (Takeda, Axsome) threaten narcolepsy longer term; growth is bought — recurring acquisition IPR&D sits outside owner's earnings; leverage (net debt 3.4x normalized OE).
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — final run (engine 5.4.0, 2026-10-17)
Growth sanity check: the engine's blended start is 9.74% (components: rev CAGR 5y 12.55%, rev CAGR 3y 5.26%, latest rev YoY 4.88%, OE/share CAGR 2y 18.86%). Against actual prints: TTM revenue $4,601,233,000 is +12.59% YoY (fundamentals.json TTM), Q2 2026 printed +16%, and the raised FY2026 guide of $4.60–4.75B implies roughly +8–11% on FY2025. The base start of 9.7% sits inside the guidance range and below the latest quarter — the written reason it is not higher is that Q2's +16% was flattered by launch-period oncology (Modeyso/Ziihera first periods, oncology +32% off a small base). Bull at 14.7% is approximately the Q2 print sustained as Ziihera's GEA launch ramps — below the latest print, so no inflation. Super-bull offset was trimmed from the default +12pp to +8pp (start 17.7%): the default 21.7% start exceeds every print the company has made and is not defensible for a $4.6B-revenue pharma whose largest franchise faces new generic pressure; 17.7% is just above the Q2 print and requires Ziihera to become the HER2 standard of care while Xywav holds double-digit growth. Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25 (defaults). Price $210.23.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -2.3% | 0.75 | Generic oxybate payer squeeze hits Xywav; orexin/launch disappointments; another IPR&D charge | $95.51 | 7.98% |
| Bear | 25% | 4.7% | 0.9 | Oxybate erosion offsets Epidiolex/oncology growth; leverage bites | $153.47 | 11.69% |
| Base | 30% | 9.7% | 1.0 | Guidance-range growth decays over the CAP | $209.68 | 14.97% |
| Bull | 25% | 14.7% | 1.1 | Q2 pace sustained; Ziihera GEA ramps | $283.07 | 18.78% |
| Super bull | 10% | 17.7% | 1.25 | Ziihera becomes HER2 standard ($3–5B peak); Modeyso scales; Xywav holds | $363.34 | 22.52% |

- **Probability-weighted: IV@15% $217.92 (+3.7% vs price), IV@12% $293.07 (+39.4%), IV@10% $377.29, weighted IRR 15.42%, base-case IRR 14.97%**
- **Tier by numbers: B.** Diagnostics (key_numbers.md): OE yield 9.01%, terminal value 19.9% of IV@15%, scenario spread 3.80x, net debt 3.43x normalized OE, 9.5 months since FY end.
- Hurdle-clearing prices (weighted path): 15% at $217.92 · 20% at $150.92 · 25% at $114.45. The price clears 15% by only $7.69/share.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above.
- **NI_OCF_DIVERGENCE** (2023, 2024, 2025): identified. FY2025's gap (net loss −$356,148,000 vs OCF $1,355,773,000) is the acquired IPR&D charge of $947,862,000 (Chimerix; non-cash add-back in the 10-K reconciliation, cash in investing), plus intangible amortization $654,661,000, SBC $291,133,000 and acquisition inventory step-up $147,948,000, partly offset by a deferred tax benefit of −$444,971,000 (all 10-K cash-flow reconciliation figures). 2023–24 show the same pattern at smaller scale (IPR&D $19,000,000 / $10,000,000; amortization $608,284,000 / $627,313,000; 2023 also a $61,014,000 PP&E impairment). The divergence is structural amortization + episodic IPR&D, not cash earnings quality — the OCF-based conservative OE is the right series. The IPR&D recurrence is handled as an overlay caveat above, not by adjusting the base.
- **HIGH_NET_DEBT** (3.43x normalized OE): from the filing — total debt $5,358,257,000 (debt_current $1,029,903,000 + debt_lt $4,328,354,000, financials_history.csv FY2025) less cash $1,391,899,000 = net debt $3,966,358,000; leases add $65,170,000. Against TTM OE of $1,284,588,000 the load is serviceable but leaves no room for an oxybate shock; the bear cases (0.90/0.75 multipliers, IV@15 $153.47/$95.51) are the stress test, and the verdict is sized to them.
- **TIER_BAND** (bear C 11.69% vs bull B 18.78%): the verdict spans tiers — sized to the bear end in the verdict below.
- The preliminary run also flagged **WIDE_SCENARIO_SPREAD** (4.47x on the median base with default offsets); trimming the super-bull offset brought the final spread to 3.80x and the flag cleared, but the range is still wide — confidence is medium, not high.

## My thoughts / overlay
- The honest headline is the method range: on the 3-yr median base ($16.50/share) the preliminary run printed weighted IRR 14.18% / IV@15 $195.25 — Tier C, below the price. On the TTM base ($18.95/share) the final run prints 15.42% / $217.92 — Tier B, barely above the price. The entire verdict is the base choice; the TTM base is the more current and uses the honest diluted share count, so B stands, but it is a B with a 3.7% margin of safety, not a B with room.
- Quality: genuine cash generation (TTM OCF $1,661,073,000, OE yield 9.01% at the price), no dividend, minimal buybacks TTM ($23,000 per fundamentals.json — buybacks paused while acquisitions absorb cash).
- Risks: oxybate franchise defense through the H2 2026 generic window is the single swing factor; Ziihera execution against a $3–5B peak-sales promise; serial-acquisition IPR&D ($948M in 2025, $820M Actio upfront in Sep 2026) is a recurring real cost the OE definition misses — pass 2 should test an OE variant charging average IPR&D; leverage 3.4x normalized OE.
- Data/enrichment note: fundamentals.json carries no gross margin (cogs not filed under the captured tags) — margin evidence above is from company guidance, not the filing-direct file.

## Final verdict
- **Final tier: B** (weighted IRR 15.42% on the TTM base; method range C→B across the median and TTM bases, which is itself the finding)
- Confidence: **Medium** (TIER_BAND spans C→B, leverage 3.4x, scenario spread 3.80x)
- One-liner: Cash-generative specialty pharma, moat 5/10 — clears 15% only just and only on the TTM base (weighted IRR 15.4%, IV@15 $218 vs $210 price); on the 3-yr median base it does not clear (14.2%, Tier C), so size it to the bear end, not as a full B.
