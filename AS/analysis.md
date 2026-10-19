# AS — Amer Sports, Inc.
Pass-1 v5 / engine 5.4 run, 2026-10-16. In scope (market cap $16.904B at $30.02, nasdaq_quote_api). IFRS filer on Form 20-F (FY2025 filed 2026-02-26).

All figures below are copied from key_numbers.md, dcf_numbers.json, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
Premium sporting-goods portfolio: Arc'teryx (Technical Apparel), Salomon and Atomic (Outdoor Performance), Wilson (Ball & Racquet Sports), plus Peak Performance. Cayman-incorporated, Finnish-rooted, owned under an Anta-led consortium structure; the NYSE security is the ordinary share itself (see ADS flag below). Growth is currently led by Arc'teryx, Salomon softgoods/footwear, Greater China, and a rising direct-to-consumer mix.

## Owner's earnings
**FY2025 (20-F via EDGAR, from financials_history.csv):** operating cash flow $729,800,000; capex $216,500,000; SBC $37,200,000 (always a real cost).
- **Conservative owner's earnings FY2025: $476,100,000 = $0.85/share** (key_numbers.md: latest FY OE/share $0.85, latest FY OE total $476.1M)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $665,100,000 — above the conservative figure; the OCF-based conservative series is the one used throughout.
- OE positive 4 of the last 5 fiscal years (FY2022 was negative on the old leveraged structure). Net debt $282.8M (key_numbers.md), plus lease liabilities $818,000,000 in financials_history.csv; net debt / normalized OE 1.43x.
- History: OE/share was -$0.44 (FY2022), $0.17 (FY2023), $0.35 (FY2024), $0.85 (FY2025) — a genuine inflection as IPO proceeds (Feb 2024) repaid the pre-IPO debt stack (total debt $6,612,400,000 at end-FY2023 → $927,300,000 at end-FY2024, financials_history.csv) and margins expanded.

**Base used = normalized (median of last 3 FY OE/share) $0.35/share** (base_source: median_of_last_3_fy_oe_per_share).
- Amer Sports files under IFRS; ttm.py reads us-gaap only and exited non-zero for AS ("no annual (FY) fact" on its us-gaap legs) — so no TTM pin exists and the median base stands, per the worker spec's IFRS rule.
- The median is the conservative choice here (see BASE_DIVERGENCE below). The verdict does not depend on it: a sensitivity run of the same engine pinned to the latest-FY base ($0.85/share, all other preliminary inputs unchanged) printed weighted IRR 9.29% and weighted IV@15 $14.91 — still Tier D, still roughly half the $30.02 price.

## Moat: 5/10 — moderate/narrow, not yet proven in returns
Justification: premium brands with real pricing power, but the measured return history has not yet cleared the cost of capital through a cycle.
- FOR: Arc'teryx premium technical-apparel franchise with proven pricing power — group gross margin 49.1% (FY2021) to 57.6% (FY2025); Salomon scale in outdoor performance, with softgoods/footwear momentum driving Outdoor Performance +37% in Q2 2026; Wilson's ball & racquet franchise (Tennis 360) as a second, steadier pillar; rising direct-to-consumer mix (record 55% of revenue in Q2 2026) — controlled distribution, full-price sell-through; multi-brand platform effect in Greater China (FY2025 Greater China revenue +43.4% to $1.86B).
- AGAINST: ROIC evidence is thin — the `roic_proxy` series in fundamentals.json runs -27.9% / 0.7% / 4.0% / 6.7% / 8.1% across FY2021–25, only just reaching roughly the cost of capital in FY2025, with no through-cycle record above it (the early years are the leveraged pre-IPO structure, but the burden of proof is on the franchise); gross margin did expand every year (49.1% → 50.0% → 52.5% → 55.4% → 57.6%), which supports pricing power but not yet durable excess returns. Brand-heat/fashion risk for Arc'teryx and Salomon softgoods; Greater China is ~28% of FY2025 revenue with local competition intensifying (KAILAS, Anta, Li-Ning outdoor pushes); Wilson / Ball & Racquet is a low-margin contested category whose segment margin compressed in 2025 prints on tariffs and SG&A; controlling-shareholder overhang and repeated primary issuance.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — final run (2026-10-16)
Growth sanity check (mandatory): the engine's blended growth is 19.59% (components, key_numbers.md: rev CAGR 5y 20.97%, rev CAGR 3y 22.50%, latest rev YoY 26.68%, OE/share CAGR 2y 124.04% — the last is an inflection artifact off the tiny FY2023 base and is not used as a scenario anchor). Recent prints are hotter than the base start: FY2025 revenue +26.68%, Q2 2026 revenue +32% to $1,633M (company release), and management raised FY2026 guidance to ~24% reported revenue growth with diluted EPS of $1.27–$1.30. Written reason the base start (19.6%) sits below those prints: the prints are revenue, not OE/share — the share count keeps rising on primary issuance (see DILUTION), Q3 2026 guidance already decelerates to 18–20% revenue growth, the original FY2026 guide was 16–18%, and H1 2026 margins include a one-time net tariff refund that flattered Q2 gross margin. The bull start (24.6%) matches the raised FY2026 revenue guide; the super-bull start (31.6%) matches the Q2 2026 print — neither bull case is set below what the company just printed. Probabilities 10/30/30/20/10 (bear widened from the 25% default per OE_VOLATILE); OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $30.02.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 7.6% | 0.75 | Brand heat cools, China slows, Wilson drags | $2.67 | 3.68% |
| Bear | 30% | 14.6% | 0.90 | Growth decays to the original FY26 guide and below; issuance continues | $4.26 | 4.51% |
| Base | 30% | 19.6% | 1.00 | Blended growth decays normally over the CAP | $5.80 | 5.31% |
| Bull | 20% | 24.6% | 1.10 | Raised FY26 guide trajectory holds; margins keep expanding | $7.80 | 6.32% |
| Super bull | 10% | 31.6% | 1.25 | Q2 2026 momentum persists across all segments | $11.68 | 8.16% |

- **Probability-weighted: IV@15% $6.01 (-80.0% vs price), IV@12% $8.27, IV@10% $10.82, weighted IRR 5.44%, base-case IRR 5.31%**
- **Tier by numbers: D.** Bear tier D, bull tier D — no tier band. Diagnostics (key_numbers.md): OE yield 1.17%, terminal value 22.2% of IV@15%, scenario spread 4.38x, net debt 1.43x normalized OE, 9.5 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): ttm.py was run and exited non-zero — it reads us-gaap only and Amer Sports is an IFRS 20-F filer, so no TTM pin is available; the normalized median base is used, per spec. Interim evidence (Q2 2026 release: revenue +32%, guidance raised) is reflected in the scenario starts, not in a hand-built base.
- **DILUTION** (share count +13.58%/yr, -5.00pp growth adjustment already in the blend): the CAGR is issuance, not SBC creep — weighted diluted shares went 384,499,607 (FY2023) → 501,745,145 (FY2024) → 563,075,693 (FY2025) on the Feb 2024 IPO primary issuance and follow-on offerings, and a further 20,604,396 shares were priced in March 2026 at $36.40 to redeem the 6.75% senior secured notes due 2031. SBC itself is small but rising: $10,700,000 (FY2023) → $19,500,000 (FY2024) → $37,200,000 (FY2025), still ~5% of FY2025 OCF, and it is deducted in full in the conservative OE.
- **OE_VOLATILE** (OE/share spans >3x over 5 years): real, but it is an inflection (deleveraging + margin expansion), not steady-state cyclicality. Handled with the normalized median base plus a widened bear weight (30%).
- **NI_OCF_DIVERGENCE** (2023, 2024): FY2023 net income -$208,800,000 vs OCF +$199,000,000; FY2024 net income $78,400,000 vs OCF $424,700,000 (financials_history.csv). The gap is the pre-IPO leveraged structure: heavy non-cash D&A ($220,900,000 in FY2023, $273,800,000 in FY2024) and finance costs on the $6.6B debt stack that sat below operating income, which was positive both years ($302,500,000 / $470,800,000). The debt was repaid from IPO proceeds in 2024. The OCF-based conservative OE used for the base is not contaminated by this.
- **ADS_RATIO_APPLIED** (x1.0): resolved in judgment.json under the bounded authority — Amer Sports is direct-listed; the NYSE security is the ordinary share itself, so per-share figures and the $30.02 price are already on the same basis. Source: Form 20-F for FY2025 (filed 2026-02-26) and its filed Description of Share Capital; the company's SEC offering filings register Ordinary Shares, not ADSs.
- **BASE_DIVERGENCE** (latest FY $0.85 vs 3-yr median $0.35): the median is the distorted one — it averages in FY2023 ($0.17) and FY2024 ($0.35), when OE was still suppressed by the leveraged pre-/early-post-IPO structure, while FY2025 ($0.85) reflects the repaid balance sheet and 57.6% gross margin. The median is nonetheless kept as the scored base (IFRS rule, no TTM available), and the latest-FY sensitivity (weighted IRR 9.29%, IV@15 $14.91, Tier D) is reported above — the tier does not change either way.
- **LOW_OE_YIELD** (base OE yield 1.17%): agreed — at $30.02 the valuation rests almost entirely on future growth; that is exactly why the verdict is sized to the conservative end and confidence is low.
- **WIDE_SCENARIO_SPREAD** (4.38x): real — the outcome range for a brand-heat growth story at this price IS wide. Confidence is capped at low, and even the super-bull case (IRR 8.16%) does not clear 10%, so the spread does not rescue the verdict.

## Data / enrichment notes
All step-9 enrichment ran clean: fundamentals.py, prices.py, segments.py, statements.py, profile.py, reprice.py all wrote their files. One structural note from segments.py: as a 20-F filer Amer Sports files no 10-Qs, so quarterly segment tables are not available (annual only). statements.py notes some cross-filing growth cells are blank where filing generations disagree (restated vs as-filed) — no scored figure depends on those cells.

## My thoughts / overlay
- The method range is the honest headline: Tier D on the normalized base (weighted IRR 5.44%, IV@15 $6.01) and still Tier D on the most generous filing-derived base, the latest FY (weighted IRR 9.29%, IV@15 $14.91). No defensible base gets the current price anywhere near a 15% hurdle — the hurdle-clearing price on the scored base is $6.01.
- Quality is not the debate: revenue +26.68% in FY2025 and +32% in Q2 2026, gross margin up ~8.5pp in four years, net debt down to $282.8M from a $6.1B net-debt position at end-FY2023 (financials_history.csv). The debate is price and proof: ROIC proxy only reached 8.1% in FY2025, and the market is capitalizing many years of flawless brand-heat compounding.
- Risks: Arc'teryx/Salomon fashion cooling, Greater China concentration and local competition, tariff exposure in Ball & Racquet and winter equipment, continued primary issuance diluting per-share economics, and the Anta-consortium control overhang.

## Final verdict
- **Final tier: D** (weighted IRR 5.44% on the scored normalized base; D on the latest-FY sensitivity too)
- Confidence: **Low** (WIDE_SCENARIO_SPREAD, OE_VOLATILE, LOW_OE_YIELD, IFRS filer with no TTM pin)
- One-liner: Real premium-brand quality, moat 5/10, but the price pays for perfection: weighted IRR 5.4% and weighted IV@15 $6.01 vs $30.02 on the normalized base — even on the latest-FY base ($0.85/sh) the weighted IRR is only 9.3% with IV@15 $14.91; clears 15% only below ~$6.01 on the scored base.
