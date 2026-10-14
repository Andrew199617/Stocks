# ALNY — Alnylam Pharmaceuticals, Inc.
v5 run, 2026-10-14. Price $224.41 (nasdaq_quote_api), market cap $30.224B — in scope under $40B.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output (ttm.json), or financials_history.csv — none are recomputed. Q2 2026 print figures are from the company's Q2 2026 results release as returned by web search and are cited as search results, not filing-computed figures.

## What it is
The RNA-interference platform company: Amvuttra (vutrisiran) and Onpattro (patisiran) for transthyretin amyloidosis (TTR), plus the rare-disease products Givlaari and Oxlumo, collaboration/royalty revenue, and a pipeline extending the platform (including zilebesiran for hypertension with Roche, and CNS candidates). The investment case in 2026 is the Amvuttra launch in ATTR cardiomyopathy (ATTR-CM) following the HELIOS-B trial.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $524,080,000; capex $58,697,000; SBC $348,235,000 (always a real cost).
- **Conservative owner's earnings FY2025: $117,148,000 = $0.87/share** (latest FY OE/share, key_numbers.md)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $529,269,000 for FY2025 (financials_history.csv) — higher than the conservative figure mainly because it does not deduct the full SBC load the conservative definition deducts; the conservative figure is the one used throughout.
- OE positive in only **1 of the last 5 fiscal years** on the conservative definition. The normalized base (3-yr median) is **$-1.44/share** — the preliminary engine run on that base was Tier F, correctly, because the median averages in the pre-profit years.
- Net debt: not stated — the engine's computed outputs report net debt as unavailable for this name (debt tags null in dcf_numbers.json, "—" in key_numbers.md), so no balance-sheet figure is quoted here rather than a hand-computed one.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $524,080,000 − prior YTD $9,495,000 + current YTD $397,228,000 = **TTM $911,813,000**
- Capex: FY $58,697,000 − prior YTD $23,263,000 + current YTD $56,513,000 = **TTM $91,947,000**
- SBC: FY $348,235,000 − prior YTD $168,392,000 + current YTD $156,779,000 = **TTM $336,622,000**
- Shares (current-YTD weighted diluted): **138,249,000**
- **TTM OE total $483,244,000 → base OE/share $3.50** (key_numbers.md: $3.50; dcf_numbers.json: 3.4954610883261363, base_source: ttm_json)
- Why the TTM base and not the median: the median is the distorted base here — it is built from years before Amvuttra's ATTR-CM launch turned OCF positive. The TTM base is filing-derived, uses the same conservative definition (full SBC deducted), and is still only a $3.50/share base against a $224.41 price (OE yield 1.56%).

## Moat: 7/10 — strong, not wide
Justification: RNAi platform leader with patent-protected GalNAc delivery, first-mover Amvuttra in ATTR cardiomyopathy backed by HELIOS-B mortality data, and quarterly subcutaneous dosing versus daily oral rivals; offset by three-front competition (Pfizer, BridgeBio, Ionis), heavy TTR franchise concentration, high SBC load, and payer/pricing pressure — strong moat, not wide.
- FOR:
  - Patent-protected RNAi/GalNAc delivery platform, repeatable across targets
  - Amvuttra first-mover in ATTR-CM with HELIOS-B mortality/CV-event data
  - Quarterly subcutaneous dosing vs daily oral competitors
  - Proven pricing power in rare disease (Givlaari, Oxlumo) plus TTR scale
  - Deep pipeline and Roche zilebesiran partnership extending the platform
- AGAINST:
  - TTR franchise concentration — most growth rides on Amvuttra
  - Three-front competition: Pfizer Vyndaqel, BridgeBio acoramidis, Ionis
  - Patent expiry and payer pricing pressure on high-cost rare-disease drugs
  - Heavy SBC load and 3.4%/yr share dilution
  - Pipeline/binary trial risk beyond the liver franchise
- A 7 gives CAP = 11.1 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 11.1 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Growth sanity check (mandatory): the engine's blended growth is 52.96% (rev CAGR 5y 49.78%, rev CAGR 3y 52.96%, latest rev YoY 65.19%) and g_base hit the 35% cap. Scenario starts with the default offsets are therefore 23.0% / 30.0% / **35.0%** / 40.0% / 47.0%. Every start — including super bull at 47.0% — sits below the company's latest prints (latest FY revenue YoY 65.19% in the computed outputs; Q2 2026 search-reported total revenue growth +67% YoY and TTR growth +89% YoY). That gap has a written reason, and it is deliberate: those prints are a launch-phase spike off the ATTR-CM approval, the revenue base is scaling rapidly so the same dollar growth is a falling percentage, and in Q2 2026 the company trimmed its 2026 TTR net product revenue guidance range to $4,200–$4,500 million (search-reported) with a modest net-price reduction noted in the quarter. Extrapolating a launch spike as a 15-year fade start would be the opposite error. Probabilities are the defaults 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 23.0% | 0.75 | Competitors take ATTR-CM share fast; pricing pressure; growth collapses | $56.86 | 6.43% |
| Bear | 25% | 30.0% | 0.90 | Launch decelerates hard; SBC load stays heavy | $94.90 | 8.86% |
| Base | 30% | 35.0% | 1.00 | Amvuttra keeps growing, fading normally over the CAP | $133.17 | 10.97% |
| Bull | 25% | 40.0% | 1.10 | TTR share gains continue; operating leverage drops through | $184.59 | 13.38% |
| Super bull | 10% | 47.0% | 1.25 | Category-defining TTR franchise plus pipeline wins (e.g. zilebesiran) | $288.68 | 17.28% |

- **Probability-weighted: IV@15% $144.38 (−35.7% vs price), IV@12% $210.33, IV@10% $286.79, weighted IRR 11.55%, base-case IRR 10.97%**
- **Tier by numbers: C.** Diagnostics (key_numbers.md): OE yield 1.56%, terminal value 29.3% of IV@15%, scenario spread 5.08x, 9.4 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 9 months ago / 9.4 months in diagnostics): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, with all inputs quoted above.
- **DILUTION** (share count growing 3.4%/yr): real and already deducted via the −3.44% growth adjustment in the blend (share count CAGR 3.44%, key_numbers.md). The driver is SBC: TTM SBC is $336,622,000 against TTM OCF of $911,813,000 — a heavy, real cost that the conservative OE definition deducts in full in both the FY and TTM bases. Convertible-note conversion is an additional dilution overhang disclosed in the company's filings (per web search of its 10-Q risk disclosures).
- **BASIS_BREAK_SUSPECT** (>60% revenue jump in the last 5 years): investigated — no divestiture, big M&A, or restatement explains it. The jump is organic: the Amvuttra ATTR-CM launch. Latest rev YoY is 65.19% and the 3-yr/5-yr revenue CAGRs (52.96% / 49.78%) are launch-driven, not basis-driven — which is why the growth starts were sanity-checked against launch deceleration (guidance trim, scaling base) rather than taken at face value.
- **NI_OCF_DIVERGENCE** (net income vs OCF differ by >40% in 2023, 2024, 2025): the visible bridge in the filed history is non-cash compensation — SBC was $221,680,000 (2023), $272,084,000 (2024), and $348,235,000 (2025) in financials_history.csv, with D&A on top — net income is charged with SBC while OCF adds it back, so the two series diverge mechanically in exactly the flagged years. No specific tax-deposit or impairment one-off was identified in the research. The conservative OE used throughout starts from OCF and then deducts SBC in full, so the divergence does not flatter the base.
- **LOW_OE_YIELD** (base OE yield 1.6%; key_numbers.md 1.56%): real — at $224.41 the valuation rests almost entirely on growth delivery. This is a core reason the verdict is C with low confidence rather than a story-driven upgrade.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 5.08x super-bear IV): real — the outcome range for a single-franchise launch at this price IS wide. Confidence is low, and the verdict is sized to the conservative end.

## My thoughts / overlay
- The honest headline is the method range: on the normalized 3-yr median base ($-1.44/share) this is a Tier F — no positive normalized owner's earnings at all. On the filing-derived TTM base ($3.50/share) it is a Tier C at 11.55% weighted IRR. Both are defensible readings of the same filings; the TTM run is the more current one, but the spread between "no normalized OE" and "C" is itself the finding — this is an inflection story, not an established owner's-earnings compounder (OE positive 1/5 years).
- Quality is improving fast and is not the whole debate: TTM OCF of $911,813,000 vs the FY2025 figure of $524,080,000 (both ttm.py / filed inputs) shows the launch converting to cash. The debate is price: even the super-bull case (47.0% start, 1.25× OE) only reaches a 17.28% IRR, and the bull case sits below the 15% hurdle at 13.38%.
- Risks: TTR concentration, Pfizer/BridgeBio/Ionis competition in ATTR-CM, payer pressure on high-cost rare-disease pricing, patent expiry over the projection window, the heavy SBC/dilution load, and binary pipeline risk beyond the liver franchise.
- Price that clears the hurdle: the weighted IV@15% is **$144.38** — that is the price at which these inputs clear 15%, before any additional margin of safety. At $224.41 a buyer is paying for the bull-to-super-bull path, not the weighted case.

## Final verdict
- **Final tier: C** (weighted IRR 11.55% on the v5 final TTM-base inputs; the method range runs F on the normalized median base to C on the TTM base)
- Confidence: **Low** (WIDE_SCENARIO_SPREAD 5.08x, LOW_OE_YIELD 1.56%, OE positive only 1/5 years)
- One-liner: Strong RNAi platform, moat 7/10, at an inflection to positive owner's earnings — but at $224.41 it does not clear 15% (weighted IRR 11.55%, weighted IV@15 $144.38); the price that clears 15% on these inputs is $144.38.
