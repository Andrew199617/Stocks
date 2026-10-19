# FROG — JFrog Ltd.
v5 run, 2026-10-18. In scope (market cap $9.797B at $84.31, nasdaq_quote_api — under the $40B cutoff).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv / fundamentals.json — none are recomputed.

## What it is
Software supply-chain platform built on Artifactory, the enterprise system of record for software binaries/artifacts: artifact management across 30+ package formats, distribution, and the Xray security line (binary scanning, SBOM, supply-chain security), sold self-managed and as SaaS to mid-sized and large organizations. Research (Q2 2026, quarter ended 2026-06-30, via search): revenue $163.8M, +28.7% YoY; cloud revenue $87.5M, +53% YoY and 53% of total; net revenue retention 121%; 1,291 customers above $100,000 ARR and 97 above $1M; full-year 2026 revenue guidance raised to $648M–$652M. The growth and the platform position are real — the problem in this screen is, as with Rubrik, the stock-based compensation line between operating cash flow and the owner.

## Owner's earnings
**FY2025 (10-K via EDGAR):** revenue $531,840,000; operating cash flow $145,729,000; capex $3,460,000; SBC $156,657,000 (always a real cost in this sweep).
- **Conservative owner's earnings FY2025: −$14,388,000 = −$0.12/share** (latest FY OE/share, key_numbers.md).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): −$158,582,000 (financials_history.csv) — also negative, and worse; the two definitions agree on the sign.
- **Normalized base (engine): median of last 3 FY OE/share = −$0.21/share.** History: FY2023 −$0.22/share, FY2024 −$0.21/share, FY2025 −$0.12/share. OE positive in 0 of the last 5 fiscal years on the normalized view (key_numbers.md: 0/5).
- Preliminary run therefore fired the F branch, sub-type `sbc_exceeds_cash`: over the last 3 fiscal years OCF − capex is positive but SBC consumes it. The F was investigated, not accepted blindly — see the TTM check, which is the one basis on which OE has crossed zero.

**TTM check via ttm.py (filing-direct, through Q2 2026 — quoted inputs):**
- OCF: FY $145,729,000 − prior YTD $64,877,000 + current YTD $95,412,000 = **TTM $176,264,000**
- Capex: FY $3,460,000 − prior YTD $1,274,000 + current YTD $4,377,000 = **TTM $6,563,000**
- SBC: FY $156,657,000 − prior YTD $74,854,000 + current YTD $79,204,000 = **TTM $161,007,000**
- Shares (current-YTD weighted diluted): **120,992,123**
- **TTM OE total $8,694,000 → TTM OE/share $0.07**

The TTM base was pinned via `--ttm` in the final run (base_source: ttm_json), following the STALE_FY procedure and the precedent of comparable SBC-heavy names whose OE inflected only in the TTM window. It is positive — barely. TTM SBC ($161,007,000) still consumes nearly all of TTM operating cash flow ($176,264,000) before capex; what flipped the sign is OCF growth, not SBC discipline (TTM SBC is above the FY2025 figure). The resulting OE yield at $84.31 is 0.09% (key_numbers.md), so the DCF below rests almost entirely on growth compounding off a $0.07 base — and even the super-bull path cannot lift the return off the model's floor.

## Moat: 5/10 — moderate/narrow
Justification: Artifactory is the dominant enterprise artifact repository and the system of record for binaries, with real switching costs, 121% net revenue retention in Q2 2026 and 1,291 customers above $100k ARR. It is not 7+: the `roic_proxy` series in fundamentals.json is negative in every year from 2020 to 2025 (FY2020 −2.9%, FY2021 −9.5%, FY2022 −12.3%, FY2023 −10.0%, FY2024 −9.9%, FY2025 −8.9%) because GAAP operating income is negative after SBC — there is no filed evidence of returns well above the cost of capital through a cycle. Gross margin tells the same cautionary story: 83.1% in 2018, sliding to 76.8% in FY2025 (77–78% in the recent quarters in fundamentals.json) as cloud hosting costs grow with the SaaS mix. A 7+ on this ROIC and margin record would be a narrative, not a measurement.
- FOR: Artifactory dominance — the enterprise system of record for binaries/artifacts across 30+ package formats, with deep CI/CD integrations
- FOR: Switching costs once artifact storage, replication, retention and release workflows sit on the platform; mission-critical and rarely ripped out
- FOR: Expansion inside the base — net revenue retention 121% in Q2 2026, 1,291 customers >$100k ARR, 97 >$1M, Enterprise+ 59% of revenue
- FOR: Security attach — Xray/supply-chain security is landing with new logos (>40% of Q2 2026 new wins included security) and the $1M+ cohort (>80%)
- AGAINST: Bundled 'good enough' rivals — GitHub Packages and GitLab, plus Sonatype Nexus, Harbor and hyperscaler registries (ECR/GCR/ACR) attack from inside platforms customers already pay for
- AGAINST: No ROIC proof — roic_proxy negative every year 2020-2025 (FY2025 -8.9%); GAAP operating losses persist after SBC, so pricing power is unproven in filed numbers
- AGAINST: Gross margin erosion — 83.1% in 2018 to 76.8% in FY2025 as cloud hosting costs grow with the SaaS mix (53% of Q2 2026 revenue)
- AGAINST: SBC-funded talent model — SBC $156.7M in FY2025 exceeds all of OCF growth headroom and dilutes holders 5.4%/yr; the moat is re-bought annually in stock
- A moat of 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-18)
Final engine pass: `--moat 5 --probs 0.10,0.25,0.30,0.25,0.10 --ttm` (default probabilities, offsets, and multipliers). Base OE/share $0.07 (ttm_json), price $84.31.
Growth sanity check (standing rule): the scenario starts are OE/share growth, not revenue growth. The revenue prints are strong — latest FY revenue YoY +24.12%, Q2 2026 revenue +28.7% YoY, FY2026 guidance $648M–$652M against FY2025 revenue $531,840,000 — but the engine's blend (19.12%) is the median of the adjusted components (rev CAGR 5y 28.67%, rev CAGR 3y 23.83%, latest YoY 24.12%, each reduced by the −5.00pp share-count adjustment for 5.40%/yr dilution; key_numbers.md). A bull start of 24.1% OE/share growth therefore corresponds to roughly the current revenue print sustained *after* dilution, and the super-bull start of 31.1% sits above every recent revenue print — no start is understated relative to the evidence once the dilution adjustment is accounted for, and none was recalibrated.

| Scenario | Prob | Growth start | OE mult | Story | IV@15% | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 7.1% | 0.75 | Bundled rivals take share, cloud mix keeps pressuring gross margin, SBC stays at TTM run-rate; OE slips back below zero in spirit — the model floors the return | $0.54 | 2.58% |
| Bear | 25% | 14.1% | 0.90 | Revenue decelerates toward guidance-implied low-20s and below; OCF growth only just outruns SBC | $0.86 | 2.65% |
| Base | 30% | 19.1% | 1.00 | Current trajectory: OCF compounding outgrows a flat-to-rising SBC line off the $0.07 TTM base | $1.17 | 2.71% |
| Bull | 25% | 24.1% | 1.10 | Cloud +53% momentum and security attach hold; Enterprise+ mix keeps expanding | $1.57 | 2.80% |
| Super bull | 10% | 31.1% | 1.25 | JFrog becomes the default control plane for AI-era software delivery with real SBC discipline | $2.35 | 2.96% |

- **Probability-weighted: IV@15% $1.24 (−98.5% vs price), IV@12% $1.71, weighted IRR 2.73%, base-case IRR 2.71%** — and every IRR, including the weighted figure, is flagged IRR_AT_FLOOR: read the expected return as **at most ~3.0%**, not as the recorded figure (key_numbers.md).
- **Tier by numbers: D** (tier_bear D, tier_bull D — no band ambiguity). Diagnostics (key_numbers.md): OE yield 0.09%, terminal value 22.2% of IV@15%, scenario spread 4.38x, 9.6 months since FY end.
- **Hurdle-clearing prices (weighted path): 15% at $1.24, 20% at $0.83, 25% at $0.61.** At $84.31 the market is paying roughly 68x the price at which this OE stream would clear Andrew's 15% hurdle — the entire valuation is a forecast of SBC normalization and OE compounding that the filings have only just begun to show.

## Flags — every fragility flag resolved
- **STALE_FY** (latest FY ended 2025-12-31, 9.6 months ago): resolved with ttm.py — TTM OE through Q2 2026 is +$0.07/share with the full legs quoted above, and the final run used the `--ttm` pin. Staleness changes the sign of the base (median −$0.21 → TTM +$0.07) but not the verdict: on either base the name fails the 15% hurdle by an enormous margin at $84.31 (F on the median basis, D on the TTM basis — the method range is F→D).
- **DILUTION** (share count growing 5.40%/yr): real and structural, not an artifact. SBC was $95,171,000 in FY2023, $131,106,000 in FY2024 and $156,657,000 in FY2025, and $161,007,000 TTM (financials_history.csv / ttm.py) — rising in dollars every year, with no buyback offset of any size in the filed history. The engine already deducts the trend via the −5.00pp share-count adjustment in the growth blend; the deeper point is the same as the OE story: SBC *is* the dilution, and it is paid in shares.
- **NI_OCF_DIVERGENCE** (2023, 2024, 2025): explained by the SBC mechanics, not by a one-off. Net income is stated after the non-cash SBC charge; OCF adds it back. FY2025: net income −$71,819,000 vs OCF +$145,729,000, with SBC of $156,657,000 — the SBC line alone more than covers the gap. FY2024 (net income −$69,236,000 vs OCF $110,924,000, SBC $131,106,000) and FY2023 (net income −$61,256,000 vs OCF $74,155,000, SBC $95,171,000) show the identical pattern. No tax deposit, impairment, or working-capital one-off is needed to explain it. The OCF-based conservative OE deducts SBC in full in every year, so the divergence does not contaminate the base — it *is* the base story.
- **SHARES_FALLBACK** (no diluted share count filed for 2019): noted — the 2019 history year uses the outstanding count recorded in the shares_tag column of financials_history.csv, so per-share history there is approximate. It does not touch the base: the median window (FY2023–FY2025) and the TTM pin both use filed diluted counts.
- **DEBT_TAGS_BLANK** (no debt tag reports for the latest fiscal year): balance sheet stated from the filing data in fundamentals.json — JFrog files no debt in any year of its history (total_debt null throughout), and FY2025 shows cash $75,840,000 and short-term investments $628,574,000 against liabilities $453,930,000 and equity $887,447,000, with operating lease liabilities of $12,456,000 (dcf_numbers.json). This is an unlevered, liquid balance sheet; the engine's net debt is null because there is no debt tag to subtract, not because leverage is hidden. Leverage is not the verdict driver — the SBC line is.
- **IRR_AT_FLOOR** (all scenarios and the weighted figure within 0.5pp of terminal growth 2.5%): the price is beyond the model's range. The recorded weighted IRR of 2.73% is reported as **at most ~3.0%** throughout this analysis, per the flag's own instruction.
- **LOW_OE_YIELD** (base OE yield 0.1%): real — the TTM base of $0.07/share against an $84.31 price means the valuation rests almost entirely on growth. Handled by sizing the verdict to the conservative end and setting confidence to low.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.38x super-bear IV): real — a $0.07 base makes any growth path produce a wide IV range in relative terms (though every path lands between $0.54 and $2.35, i.e. 97–99% below the price). Confidence is capped below high; it is set to low for this flag combined with IRR_AT_FLOOR and LOW_OE_YIELD.

## My thoughts / overlay
- Quality vs. score: this is a genuinely strong growth franchise (revenue +24.12% in FY2025, +28.7% in Q2 2026, cloud +53%, NRR 121%, guidance raised) that screens D only because the TTM window finally produced a positive OE base — on the normalized median basis it is an F, sub-type `sbc_exceeds_cash`. On a pre-SBC free-cash-flow basis the company is cash-generative (FY2025 FCF $142,269,000 in the filed history); after paying its people in stock, owners got −$0.21/share on the median basis and +$0.07/share TTM.
- The crossover is closing but fragile: OE/share improved from −$0.22 (FY2023) to −$0.12 (FY2025) to +$0.07 TTM, driven entirely by OCF growth — TTM SBC ($161,007,000) is *above* the FY2025 figure ($156,657,000). The bull case therefore rests on OCF continuing to compound faster than a rising SBC line, at a price that already capitalizes decades of that compounding: even the super-bull IV@15% ($2.35) is 97% below $84.31.
- Method range: F (normalized median base, preliminary run) to D (TTM pin, final run). Both ends fail every hurdle by a wide margin, so the range does not change the investment conclusion — it only changes the label. What would change the verdict: TTM OE/share growing into dollars, not cents — SBC falling as a share of OCF in filed quarters and the diluted count flattening — at which point FROG gets a DCF whose base can actually carry a valuation.

## Final verdict
- **Final tier: D** (tier_by_numbers D on the TTM base; F on the normalized median base — sized to the conservative end, the honest headline is "at most ~3% expected return at $84.31")
- Confidence: **Low** (high that current OE is negligible on every filing basis; low on any single growth path off a $0.07 base — WIDE_SCENARIO_SPREAD, IRR_AT_FLOOR and LOW_OE_YIELD all present)
- One-liner: Real DevOps franchise, moat 5/10, revenue +28.7% in Q2 2026 — but owner's earnings only just crossed zero in the TTM window ($0.07/share; 3-yr median -$0.21) because SBC ($161.0M TTM) consumes nearly all operating cash flow, so at $84.31 the weighted IRR sits at the ~3% floor and IV@15% is $1.24; clears 15% only near ~$1.24, Tier D.
