# BIIB — Biogen Inc.
v5 run, 2026-10-14. Market cap $33.67B at $228.91 (nasdaq_quote_api) — in scope under $40B.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed.

## What it is
Neurology-focused biotech in a forced transition. The legacy multiple-sclerosis franchise (Tecfidera, Tysabri, Vumerity) is eroding under generics and biosimilars, and a newer growth portfolio — Spinraza (SMA), Leqembi (Alzheimer's, 50/50 collaboration with Eisai), Skyclarys (Friedreich's ataxia), Zurzuvae (postpartum depression), Qalsody (ALS) — plus the Apellis acquisition (Syfovre, Empaveli; closed May 14, 2026) now has to carry the company. Q2 2026 was the crossover quarter: growth-portfolio revenue of $1.06B (+24% YoY) exceeded legacy MS revenue of $767M for the first time, on total revenue of $2.74B (+3% YoY). Management raised FY2026 revenue guidance to mid-single-digit growth, from a previously guided mid-single-digit decline. The longer arc is still a shrink-then-stabilize story: revenue fell from $14,377,900,000 in FY2019 to $9,675,900,000 in FY2024 before recovering to $9,890,600,000 in FY2025 (rev CAGR 5y −5.96%, 3y −0.94%, latest YoY +2.22%, all from dcf_numbers.json).

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $2,204,600,000; capex $153,800,000; SBC $290,800,000 (always a real cost — roughly a sixth of conservative OE here, not a rounding item).
- **Conservative owner's earnings FY2025: $1,760,000,000 = $11.96/share** (base_oe_latest_per_share $11.964649898028552).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): **−$29,100,000** for FY2025 — negative, driven by the $1,948,100,000 increase in net working capital recorded in the history file. The two definitions do NOT corroborate each other for the latest year; the OCF-based conservative figure is the usable one, and the maintenance figure is a warning that FY2025 cash conversion absorbed a large working-capital build. No TTM maintenance figure is produced by the tooling, so none is quoted.
- OE positive 5 of the last 5 fiscal years, but volatile (see FLAGS). Net debt $6,286,800,000. Diluted shares have drifted slightly up (share CAGR +0.25%/yr) — no buyback tailwind to credit.

**Base used = TTM owner's earnings through Q1 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $2,204,600,000 − prior YTD $259,300,000 + current YTD $645,500,000 = **TTM $2,590,800,000**
- Capex: FY $153,800,000 − prior YTD $37,100,000 + current YTD $51,200,000 = **TTM $167,900,000**
- SBC: FY $290,800,000 − prior YTD $81,000,000 + current YTD $84,000,000 = **TTM $293,800,000**
- Shares (current-YTD weighted diluted): **148,400,000**
- **TTM OE total $2,129,100,000 → base OE/share $14.35** (ttm_oe_per_share $14.347035040431267; base_source: ttm_json)
- The engine's normalized base (3-yr median) is $11.96/share. The TTM base was used because FY2025 OCF was depressed relative to the quarters around it and the TTM window is the more current filing-derived figure; the method range below shows the verdict does not depend on this choice.
- **Caveat that matters:** ttm.json's window ends 2026-03-31 — before the Apellis acquisition closed (May 14, 2026) and before Q2 2026's deal-related IPR&D/upfront charges (~$164M in the quarter per the earnings reports). The TTM base is therefore a pre-Apellis base: it carries none of Syfovre/Empaveli's contribution and none of the acquisition financing cost. That cuts both ways and is one reason confidence is low, not medium.

## Moat: 4/10 — weak-to-moderate, and narrowing where it used to be wide
Justification: Biogen's historical moat was patent-protected MS blockbusters; that moat has already been breached (Tecfidera generics globally, Tysabri biosimilars in Europe with US entry following). What remains is real but narrower — orphan-drug exclusivity in rare diseases, a first-mover Alzheimer's position shared with a partner, and a royalty stream it does not control — against binary pipeline risk and payer pressure. That is a 4, not a 5: the durable, self-renewing pillars are the minority of the revenue base.
- FOR: Orphan/rare-disease franchises (Spinraza, Skyclarys, Qalsody) with regulatory exclusivity and small, hard-to-reach patient populations; Leqembi first-mover position in disease-modifying Alzheimer's therapy with Eisai, strengthened by the at-home Iqlik initiation formulation; anti-CD20 royalty/profit-share stream (Ocrevus royalties, Rituxan/Gazyva profit share — anti-CD20 revenues +10% in Q2 2026); decades of neuroscience R&D, manufacturing, and specialist commercial infrastructure.
- AGAINST: MS patent cliff already realized — Tecfidera generic globally, Tysabri biosimilar competition in Europe and entering the US, legacy MS guided down mid-teens ex-Vumerity; Leqembi uptake has been slow, carries ARIA safety/monitoring burden, and faces Lilly competition; Spinraza competes with Novartis' Zolgensma gene therapy and Roche/PTC's Evrysdi; growth from here depends on binary registrational readouts (litifilimab in lupus, felzartamab, zorevunersen) and on M&A integration (Apellis, pending RayThera) rather than on an owned, compounding franchise; high-cost neurology drugs face persistent payer/pricing pressure.
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Growth recalibration (written reason): the engine's blended growth is 0.39% (g_base), a blend of a −5.96% 5-yr revenue CAGR, +2.22% latest revenue YoY, and a +31.57% OE/share 2-yr CAGR that is an artifact of the depressed FY2023 OE base — it is not a growth rate this company is printing. Actual recent prints: revenue +2.22% (FY2025), +3% YoY (Q2 2026), FY2026 guided to mid-single-digit growth. Scenario starts were therefore re-centered on ~3% for the base case via offsets −0.084 / −0.034 / +0.026 / +0.066 / +0.116 vs g_base. The super-bull start (11.99%) sits above anything Biogen is currently printing — that is deliberate and is why it carries only 8%: it is the case where Leqembi inflects after the Iqlik launch, the Apellis products compound at the guided mid-to-high teens, and late-stage readouts land. The bear starts are negative because the legacy MS book is guided down mid-teens and has repeatedly eroded faster than the growth portfolio added. Probabilities 15/30/30/17/8 skew bearish vs the 10/25/30/25/10 defaults per the OE_VOLATILE instruction to widen bear weight. OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $228.91.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −8.01% | 0.75 | MS erosion accelerates, Leqembi stalls, pipeline misses, Apellis dilutes | $58.56 | 5.41% |
| Bear | 30% | −3.01% | 0.90 | Legacy decline outweighs growth portfolio; deal charges recur | $85.52 | 7.00% |
| Base | 30% | 2.99% | 1.00 | Guided path: growth portfolio offsets MS, revenue +~3% | $119.89 | 9.06% |
| Bull | 17% | 6.99% | 1.10 | Leqembi Iqlik + Skyclarys/Zurzuvae momentum, Apellis synergies arrive | $153.65 | 11.00% |
| Super bull | 8% | 11.99% | 1.25 | Pipeline readouts land, Leqembi inflects, Apellis compounds | $210.82 | 14.08% |

- **Probability-weighted: IV@15% $113.39 (−50.5% vs price), IV@12% $149.30, IV@10% $189.22, weighted IRR 8.70%, base-case IRR 9.06%**
- **Tier by numbers: D.** Diagnostics: OE yield 6.27%, terminal value 17.87% of IV@15%, scenario spread 3.60x, net debt 2.98x normalized OE, 9.4 months since FY end.
- Even the super-bull scenario (14.08% IRR, IV@15% $210.82) does not clear the 15% hurdle at $228.91 — the market price already pays for more than the bull case.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.4 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q1 2026, quoted above, and the final run used `--ttm`. Limit stated in the OE section: the TTM window predates the Apellis close, so post-deal quarters are not in the base.
- **OE_VOLATILE** (OE/share range over the last 5 years spans >3x): real and structural, not a data error — conservative OE/share ran from the FY2022–23 trough years (OCF of $1,384,300,000 and $1,547,200,000 in the history file) to FY2024's $2,875,500,000 OCF year, reflecting MS erosion, restructuring-era charges, and working-capital swings. Handled by using the TTM base rather than any single year, and by widening bear weight to 45% combined (15% super bear + 30% bear).
- **NI_OCF_DIVERGENCE** (net income vs OCF differ by >40% in 2024, 2025): the direction is OCF well above net income in both years (2024: NI $1,632,200,000 vs OCF $2,875,500,000; 2025: NI $1,292,900,000 vs OCF $2,204,600,000, both from financials_history.csv). The gap is principally the non-cash addbacks visible in the same history — D&A of $673,200,000 (2024) and $779,900,000 (2025) plus SBC of $291,200,000 and $290,800,000 — not a tax-deposit-style one-off inflating OCF. The conservative OE used throughout already subtracts SBC and capex, so this divergence does not inflate the base; if anything it says reported net income understates cash generation while overstating nothing. No adjustment made.
- The preliminary run also flagged HIGH_NET_DEBT (3.57x on the median base) and WIDE_SCENARIO_SPREAD (4.24x); on the final TTM base these read 2.98x and 3.60x and no longer trip the flags, but neither has gone away in substance: $6,286,800,000 of net debt against a volatile OE base is real leverage, and a 3.60x scenario spread is wide. Both are reflected in the low confidence and the bear-skewed probabilities rather than waved off.

## My thoughts / overlay
- The method range does not save this one. On the engine's normalized median base ($11.96/share) with default probabilities, the preliminary run gave weighted IV@15% $96.59 and weighted IRR 7.78% — also Tier D. On the more generous TTM base with re-centered growth, the final run gives $113.39 and 8.70% — still Tier D. Defensible inputs span D either way; there is no C-to-A ambiguity here.
- The stock's 2026 run (to a 52-week high at this price) is the market pricing the turnaround — growth portfolio crossover, raised guidance, Apellis — as if it were already durable. The DCF says the turnaround, even if it works at the guided pace, is worth roughly half the price at a 15% discount rate. A buyer at $228.91 needs the super-bull world and then some.
- Balance sheet: net debt $6,286,800,000 was measured at FY2025, before Apellis acquisition financing — the current leverage is higher than the figure in this run, which makes the bear cases more dangerous than modeled, not less.
- Quality notes: SBC is contained ($293,800,000 TTM vs OCF of $2,590,800,000), capex is light ($167,900,000 TTM), and the anti-CD20 royalty stream is genuinely high-quality cash. The problem is not OE quality; it is that the OE base is shrinking-to-flat while the price assumes growth.
- **Hurdle price:** the weighted IV@15% is $113.39 — that is the price that clears 15% on these inputs, before any additional margin of safety. At roughly half the current price, the bear cases ($58.56–$85.52) would still argue for sizing small.

## Final verdict
- **Final tier: D** (weighted IRR 8.70% on the v5 final inputs; Tier D on every defensible base tried)
- Confidence: **Low** (OE volatility, a pre-Apellis TTM base, binary pipeline dependence, and leverage the run understates)
- One-liner: Transitioning biotech, moat 4/10 — real growth portfolio but a shrinking legacy base; at $228.91 it does not clear 15% (weighted IRR 8.70%, IV@15% $113.39 vs $228.91); it clears 15% only at or below $113.39.
