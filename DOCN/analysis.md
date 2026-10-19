# DOCN — DigitalOcean Holdings, Inc.
Pass-1 run, 2026-10-16 (engine 5.4.0). Price $97.50 (nasdaq_quote_api), market cap (est) $10.271B — in scope under $40B. All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
Developer-focused cloud infrastructure (Droplets, managed Kubernetes, managed databases, Spaces storage) sold self-serve to developers, SMBs and digital-native companies, now pivoting hard into AI inference: AI-customer ARR reached $234M in Q2 2026 (+212% YoY), 85% of it from inference services and core cloud rather than bare metal. Q2 2026 revenue was $281.2M, +28.6% YoY, with a record $93M of incremental ARR; FY2026 guidance was raised to $1.17B–$1.18B of revenue. Competition is the hyperscalers (AWS, Azure, GCP) above and Vultr / Akamai-Linode at the same tier.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $309,604,000; capex $129,086,000; SBC $80,315,000 (always a real cost).
- **Conservative owner's earnings FY2025: $100,203,000 = $0.95/share** (key_numbers.md: latest FY OE/share $0.95; latest FY OE total $100.2M)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $606,900,000 — **not usable**: it is built on net income, which carries FY2025's −$52,600,000 tax benefit (tax line, financials_history.csv; quarterly net income spiked to $158,371,000 in Q3 2025 in fundamentals.json), and on a −$339,275,000 ΔNWC swing. The OCF-based conservative figure is the clean one.
- OE positive in only 3 of the last 5 fiscal years. OE/share history (financials_history.csv): −$0.27 (2021), −$0.17 (2022), $0.28 (2023), $0.15 (2024), $0.95 (2025) — an inflection series, not a stable one.
- Balance sheet at FY2025 (dcf_numbers.json): net debt $1,041,287,000 (debt total $1,295,762,000 less cash $254,475,000), lease liabilities $274,932,000. Post-FY delevering is material — see HIGH_NET_DEBT below.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $309,604,000 − prior YTD $156,537,000 + current YTD $156,889,000 = **TTM $309,956,000**
- Capex: FY $129,086,000 − prior YTD $95,160,000 + current YTD $81,576,000 = **TTM $115,502,000**
- SBC: FY $80,315,000 − prior YTD $40,513,000 + current YTD $55,231,000 = **TTM $95,033,000**
- Shares (current-YTD weighted diluted): **118,708,000**
- **TTM OE total $99,421,000 → base OE/share $0.84** (key_numbers.md; $0.8375 in dcf_numbers.json, base_source: ttm_json)
- The TTM total ($99,421,000) essentially matches FY2025's total ($100,203,000) — the business did not shrink. The per-share drop from $0.95 to $0.84 is dilution: the share count rose from 105,343,000 diluted (FY2025) to the 118,708,000 TTM basis after the 2026 secondary offering (share_issuance TTM $891,465,000 in fundamentals.json; shares outstanding 117,579,550 per the 10-Q filed 2026-08-04). That dilution is permanent and the TTM base correctly charges it.
- The engine's normalized base (3-yr median) is $0.28/share — rejected as the base; see BASE_DIVERGENCE.

## Moat: 5/10 — moderate / narrow
Justification: Developer brand, simplicity and predictable pricing win SMB/digital-native workloads from hyperscalers, and the managed platform layer is getting stickier (85% of AI-customer ARR from inference + core cloud, not bare metal) — but compute is commodity with low switching costs, AWS/Azure/GCP outscale it, gross margin is compressing on GPU mix, and ROIC has no through-cycle proof.
- FOR: developer brand, simplicity and predictable pricing vs hyperscaler complexity and egress fees; managed platform layer (Kubernetes, databases, inference engine) — 85% of AI-customer ARR from inference + core cloud rather than bare metal; large-cohort growth and stickiness ($1M+ customer ARR +214% YoY in Q2 2026, record $93M incremental ARR in the quarter); self-serve acquisition economics (CAC payback 9.3 months reported in Q1 2026 coverage).
- AGAINST: hyperscalers outscale on price, custom silicon and bundled credits, and Vultr / Akamai-Linode sell the same commodity compute; low switching costs on core compute and a price-sensitive SMB/developer base; weak ROIC history; gross-margin compression; no proprietary silicon, network scale or owned consumer distribution.
- **ROIC / margin evidence (fundamentals.json `roic_proxy` and gross margins):** roic_proxy was −14.3% (2020), −2.7% (2021), −1.5% (2022), 1.0% (2023), 9.2% (2024), 12.2% (2025) — the first double-digit print is the most recent year, so a moat above the moderate band is not earned. Gross margin ran 60.2% / 63.2% / 57.4% / 59.7% / 59.9% across FY2021–25 and is falling on AI/GPU mix in the quarterly series: 61.4% (Q1 2025) → 59.9% → 59.6% → 58.7% → 56.1% → 55.0% (Q2 2026); TTM gross margin 57.2%.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — final run (2026-10-16)
**Growth recalibration (written reason, mandatory sanity check):** the engine's blended growth is 18.13% (components: rev CAGR 5y 23.14%, rev CAGR 3y 16.08%, latest rev YoY 15.48%, OE/share CAGR 2y 83.22%). That blend is built on stale FY prints — the "latest YoY" is FY2025's — while the company just printed Q2 2026 revenue +28.6% YoY and guided FY2026 to ~30% growth and a 35%+ Q4 exit rate. A base start at 18.13% would sit *below* what the company just printed, which the method forbids without a reason; equally, the 83.22% OE/share CAGR component is an inflection artifact off the $0.15/share 2024 base and was **not** used to justify starts above the revenue evidence. Scenario starts were therefore set via offsets (−0.08 / +0.02 / +0.10 / +0.20 / +0.30 vs g_base 18.13%) to 10.1 / 20.1 / **28.1** / 38.1 / 48.1%: base ≈ the Q2 2026 print (28.6%), bull ≈ the ~38% next-twelve-month growth sell-side expectation reported with Q2 results, super bull just under management's >50% 2027 growth objective, bear a fallback toward the FY2023–25 trend if the AI acceleration fades, super bear below the slowest recent fiscal year (FY2024, +12.7% on the filed history). Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25. Price $97.50.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 10.1% | 0.75 | AI acceleration collapses; hyperscalers retake share; capex already spent | $7.06 | 3.49% |
| Bear | 25% | 20.1% | 0.9 | Growth falls back to the pre-AI trend; GPU margins keep sliding | $12.74 | 4.44% |
| Base | 30% | 28.1% | 1.0 | Current trajectory (Q2 print, FY guide) decays normally over the CAP | $19.46 | 5.55% |
| Bull | 25% | 38.1% | 1.1 | Inference ARR compounds; larger cohorts keep expanding | $31.57 | 7.43% |
| Super bull | 10% | 48.1% | 1.25 | Management's >50% 2027 path lands and holds for years | $52.28 | 10.22% |

- **Probability-weighted: IV@15% $22.85 (−76.6% vs price), IV@12% $32.12, IV@10% $42.67, weighted IRR 6.13%, base-case IRR 5.55%**
- **Tier by numbers: D** (bear tier D, bull tier D — the whole band is D). Hurdle-clearing prices on the weighted path: 15% at $22.85, 20% at $14.81, 25% at $10.60.
- Diagnostics (key_numbers.md): OE yield 0.86%, terminal value 24.6% of IV@15%, scenario spread 7.40x, net debt 11.80x normalized OE, 9.5 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above.
- **BASE_DIVERGENCE** (latest FY $0.95 vs 3-yr median $0.28): the **median is the distorted one** — it is the 2023 value, blending the pre-profit 2023 year ($0.28) and the capex-peak 2024 year ($0.15, capex $178,167,000). Latest FY ($0.95) and TTM ($0.84, total $99,421,000 vs FY total $100,203,000) corroborate each other; the per-share gap between them is the secondary-offering dilution documented above, not business deterioration. TTM base used.
- **OE_VOLATILE** (OE/share spans >3x over 5 years; only 3/5 OE-positive years): real — it is a genuine inflection (negative OE through 2022, capex-peak 2024, breakout 2025), not noise. Handled by the TTM base, 35% combined weight on bear-or-worse, and low confidence.
- **NI_OCF_DIVERGENCE** (2023, 2024): explained by the standard non-cash addbacks of a capex-heavy cloud, not a one-off — 2023 D&A $117,866,000 + SBC $88,347,000 and 2024 D&A $130,052,000 + SBC $90,545,000 (financials_history.csv) account for the NI-to-OCF gaps; no tax-deposit or impairment one-off was found. The conservative OE deducts both capex and SBC, so the divergence does not inflate the base. (Separately, FY2025 *net income* is flattered by the −$52.6M tax benefit — one more reason the maintenance OE version was rejected above.)
- **LOW_OE_YIELD** (0.86%): accepted and priced into the verdict — at $97.50 essentially all of the value is future growth; the tier is D on every scenario, so the fragility cuts against the price, not against the tier.
- **WIDE_SCENARIO_SPREAD** (7.40x): real — the AI-inference outcome range is genuinely wide. Confidence is low, and the verdict is sized to the conservative end; note even the super-bull IV@15% ($52.28) sits ~46% below the price.
- **HIGH_NET_DEBT** (net debt 11.80x normalized OE): the FY2025 filing basis is debt total $1,295,762,000, cash $254,475,000, net debt $1,041,287,000, plus lease liabilities $274,932,000 (dcf_numbers.json). Two post-FY events materially reduce it: the 2026 secondary offering raised ~$888M of proceeds with $500M applied to retire the term loan facility (Q1 2026 reporting), and $472M of convertible notes were equitized in Q2 2026, taking pro-forma net leverage to ~0.7x (Q2 2026 earnings-call reporting). The FY-based flag therefore overstates current leverage — but the AI capacity build (about 20MW of additional capacity secured in Q2) will consume capital, bear cases were kept at full weight, and no adjustment was made to the score.
- **IRR_AT_FLOOR** (present in the preliminary median-base run, cleared in the final run): with the TTM base and recalibrated starts the flag no longer fires (irr_at_floor: false in score.json), but bear-case IRRs of 4.44% and 3.49% remain barely above the 2.5% terminal rate — the price is still at the edge of what the model can express.

## My thoughts / overlay
- The honest headline is the **method range**: the preliminary run on the normalized median base gave weighted IV@15% $4.71 and weighted IRR 3.24%; this final run on the TTM base with guidance-anchored growth gives $22.85 and 6.13%; the single super-bull scenario gives $52.28 and 10.22%. Every defensible method lands on **Tier D** — the tier is robust even though the IV is assumption-dominated.
- The business improvement is real, not a mirage: TTM revenue $1,011,113,000 (+21.4% YoY on the fundamentals.json TTM basis) and accelerating quarterly, RPO up 12x YoY to $894M with the first nine-figure commitments (Q2 2026 call reporting), and SBC falling as a share of OCF over the annual history (54% in 2022 to 26% in 2025) — though TTM SBC rose to $95,033,000 and H1 2026 SBC ($55,231,000) ran well above H1 2025 ($40,513,000) in the ttm.json legs.
- The problem is purely the price. The stock's 52-week range is $37.84–$187.50 (WallStreetZen quote data) and it changed hands at $131–$141 in late September / early October before falling to $97.50 — the market is pricing DOCN as a proven AI-inference winner. On owner's earnings it is a 0.86%-yield company whose best historical ROIC print is 12.2%, with gross margin falling as the AI mix grows. Even granting management's >50% 2027 growth objective in the super-bull case, the model cannot get IV@15% above $52.28.
- Dilution is the quiet tax: shares outstanding went from the FY2025 diluted 105,343,000 to 117,579,550 outstanding (10-Q, filed 2026-08-04) in one equity raise. Growth in total OE will keep leaking into per-share terms if capacity is equity-funded.

## Final verdict
- **Final tier: D** (weighted IRR 6.13% on the final inputs; bear→bull band both D; method range D under every base tried)
- Confidence: **Low** (7.40x scenario spread, volatile OE history, inflection-dependent base — the D itself is the robust part)
- One-liner: Real AI-inference growth story with a narrow moat 5/10 — but at $97.50 the price pays for more than the super-bull case: weighted IRR 6.1%, weighted IV@15% $22.85, and it clears a 15% hurdle only below ~$22.85.

## Data / enrichment notes
- Enrichment (fundamentals, prices, segments, statements, profile, reprice) all completed after scoring per step 9. fundamentals.json was also generated before the final run to source the ROIC and gross-margin evidence quoted in the moat section. segments.json carries no dimensioned facts for DOCN on the segment / product / geography axes (the filer reports a single segment), noted here per step 9.
