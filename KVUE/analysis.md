# KVUE — Kenvue Inc.
v5 run, 2026-10-14 (supersedes the v4 analysis of 2026-10-13; verdict unchanged — see Thoughts). In scope (market cap $34.247B at $17.80, nasdaq_quote_api).

All figures below are copied from dcf_numbers.json, ttm.py output (ttm.json), financials_history.csv, or key_numbers.md — none are recomputed.

## What it is
The J&J consumer-health spin-off (IPO May 2023, full separation via the J&J exchange offer in August 2023). Three segments: Self Care (Tylenol, Motrin, Zyrtec, Benadryl, Nicorette), Skin Health & Beauty (Neutrogena, Aveeno, OGX, Rogaine), and Essential Health (Listerine, Band-Aid, Johnson's). ~$15.1–15.4B of revenue that has gone nowhere in five years ($15.05B in FY2022 per financials_history.csv, $15.12B in FY2025) — a bond-like brand portfolio, not a growth business. Q2 2026 (quarter ended 2026-06-28): net sales $3,955M, +3.0% reported / +1.6% organic; adjusted diluted EPS $0.31, +7% (company earnings release via Business Wire, 2026-08-06).

**Deal overlay (dominates the price):** Kimberly-Clark is acquiring Kenvue for **$3.50 cash + 0.14625 KMB shares per KVUE share** (deal terms per Zacks/TradingView coverage). Both shareholder votes have passed and the U.S. antitrust waiting period has expired; closing is expected in Q4 2026 subject to remaining foreign approvals, and EU clearance with a feminine-care divestment remedy was reported on 2026-10-13. Kenvue gives no standalone guidance while the deal is pending. The $17.80 price is therefore a merger-arb price sitting at the deal consideration, not a standalone-fundamentals price. The DCF below is the *break-value* analysis: what KVUE is worth standalone if the deal fails. The combined company's claimed synergy target belongs to the combined entity, not to standalone KVUE cash flows.

## Owner's earnings (SEC EDGAR, filing-direct)
From financials_history.csv:

| Fiscal year (ends late Dec) | Revenue | Net income | OCF | Capex | SBC | OE conservative | OE maintenance |
|---|---|---|---|---|---|---|---|
| FY2023 (ended 2023-12-31) | $15,444M | $1,664M | $3,168M | $469M | $188M | $2,511M | $2,668M |
| FY2024 | $15,455M | $1,030M | $1,769M | $434M | $254M | $1,081M | $824M |
| FY2025 | $15,124M | $1,470M | $2,197M | $475M | $136M | $1,586M | $1,677M |

- Conservative OE = OCF − capex − SBC. The FY2025 maintenance version ($1,677M) is close to the conservative figure ($1,586M), so the base is not definition-sensitive.
- Engine normalized base (median of last 3 FY OE/share) = **$0.824/share**. FY2023 is flattered by a spin-year working-capital release and FY2024 is depressed by a non-cash impairment (see Flags), so neither the median nor any single year is clean.
- **Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
  - OCF: FY $2,197,000,000 − prior YTD $1,049,000,000 + current YTD $1,177,000,000 = **TTM $2,325,000,000**
  - Capex: FY $475,000,000 − prior YTD $267,000,000 + current YTD $203,000,000 = **TTM $411,000,000**
  - SBC: FY $136,000,000 − prior YTD $81,000,000 + current YTD $61,000,000 = **TTM $116,000,000**
  - Shares (current-YTD weighted diluted): **1,922,000,000**
  - **TTM OE total $1,798,000,000 → base OE/share $0.9355** (base_source: ttm_json)
- OE yield on the TTM base at $17.80 = 5.26% (key_numbers.md diagnostics). OE positive 4 of the last 5 fiscal years.
- Balance sheet caveat (see Flags): the engine's net debt figure counts only current debt because the LongTermDebt tag is blank in the last two fiscal years of financials_history.csv; actual leverage is materially higher and is folded into the verdict in words there.

## Moat: 6/10 — moderate-strong brands, no growth engine
Justification: Category-leading brands (Tylenol, Listerine, Band-Aid, Neutrogena, Aveeno, Zyrtec), ~60% adjusted gross margin and price-led organic growth prove pricing power, plus global pharmacy/shelf distribution scale — against five years of ~0% revenue growth, private-label and retailer pressure, no patent exclusivity, post-spin Skin Health share loss, tariff/input-cost squeeze, and the revived Tylenol litigation overhang.
- FOR: Category-leading, pharmacist/retailer-entrenched brands (Tylenol in analgesics, Listerine in mouthwash, Band-Aid, Neutrogena, Aveeno, Zyrtec) with habitual repeat purchase; ~60% adjusted gross margin is direct evidence of pricing power (Q2 2026 organic growth was price-led); global shelf and pharmacy distribution scale a challenger cannot replicate quickly; portfolio diversification across pain, allergy, skin, oral and wound care smooths single-category shocks.
- AGAINST: Five years of ~0% revenue growth despite those brands — pricing power has defended margin, not produced growth; no patent or regulatory exclusivity — the moat is advertising-and-habit, re-bought every year against private-label/store brands and retailer bargaining power; Skin Health & Beauty lost ground post-spin (only now recovering: H1 2026 organic +4.4%); the flagship brand carries a live litigation/regulatory overhang (below); input-cost and tariff pressure took 70bp off adjusted gross margin in Q2 2026 (60.2% vs 60.9%).
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
**Growth recalibration (written reason):** the engine's blended growth is −4.9%, but −3.9pp of that is the share-count adjustment, which is a spin-off artifact, not real dilution (see Flags) — the revenue blend itself is only −1.0% (rev CAGR 5y +0.12%, 3y +0.39%, latest YoY −2.14%). Actual prints: FY2025 revenue −2.1%, Q2 2026 +3.0% reported / **+1.6% organic**, H1 2026 Self Care organic −0.9% on weak illness incidence, Skin Health & Beauty organic +4.4%. Scenario starts are set against the organic/reported range, not the artifact: super bear −2.0% (matches the worst recent print, FY2025), bear 0.0%, **base +2.0%** (between Q2 organic +1.6% and reported +3.0%; reported includes FX help, organic is the cleaner OE driver), bull +4.5%, super bull +7.0% (above any recent print — defensible only as a margin-recovery + volume-return tail; a 10% tail, not a forecast). Offsets vs engine g_base (−4.91%): +2.91 / +4.91 / +6.91 / +9.41 / +11.91pp. Sanity check: no scenario start sits below a print it claims to represent — the super-bear start equals the worst recent print and the base start brackets the latest organic print; the bull starts exceed recent prints only as explicitly-labelled tails. Probabilities 15/30/30/15/10, skewed mildly bearish vs defaults (five flat years, H1 Self Care weakness, margin compression, litigation overhang argue against a fat bull tail standalone). OE multipliers at defaults 0.75/0.90/1.00/1.10/1.25. Price $17.80.

| Scenario | Prob | Growth start | OE mult | Story | IV@15% | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −2.0% | 0.75 | FY2025-style decline repeats; litigation/margin pressure compounds | $4.71 | 5.62% |
| Bear | 30% | 0.0% | 0.90 | Five more flat years; pricing only offsets cost inflation | $6.18 | 6.72% |
| Base | 30% | +2.0% | 1.00 | Q2 organic trajectory (+1.6%) holds; Skin momentum offsets Self Care softness | $7.50 | 7.74% |
| Bull | 15% | +4.5% | 1.10 | Volume returns, cost program lands, margins recover | $9.22 | 9.07% |
| Super bull | 10% | +7.0% | 1.25 | Margin recovery + volume tail — above any recent print, tail only | $11.71 | 10.89% |

- **Probability-weighted: IV@15% $7.36 (−58.6% vs price), IV@12% $9.68, IV@10% $12.26, weighted IRR 7.66%, base-case IRR 7.74%**
- **Tier by numbers: D.** Diagnostics (key_numbers.md): OE yield 5.26%, terminal value 17.7% of IV@15%, scenario spread 2.49x, net debt 0.22x normalized OE (engine figure — understated, see Flags), 9.5 months since FY end.
- **No scenario clears 15%** — even the super-bull tail yields 10.89% at $17.80. The standalone price that clears the 15% hurdle is the weighted IV@15% itself, **≈$7.36**; with a margin of safety, **~$5.50–6.00**.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 2025-12-28, 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, with all four inputs quoted in the Owner's earnings section above (FY / prior YTD / current YTD for OCF, capex, SBC; current-YTD weighted diluted shares). ttm.py exited cleanly with no warnings and no overrides used.
- **DILUTION** (share count +3.9%/yr): artifact, neutralized via the growth recalibration above. The 1,716M share counts in the earliest financials_history.csv rows are pre-IPO J&J carve-out counts; the count stepped up through the May 2023 IPO and August 2023 exchange offer to ~1,923M and has been flat since (FY2024 1,923M, FY2025 1,924M, H1 2026 YTD 1,922M per the CSV and ttm.json). There is no ongoing 3.9%/yr dilution — SBC actually fell to $136M in FY2025 and $116M TTM from $254M in FY2024. Treating the spin step-up as perpetual dilution would double-punish the growth rate.
- **NI_OCF_DIVERGENCE** (2023, 2024): identified one-offs; the OE base is trustworthy. 2024: net income ($1,030M) was depressed by non-cash asset-impairment and restructuring charges documented in the v4 pass's filing review, while OCF held at $1,769M — the gap is non-cash charges in NI, not phantom earnings. 2023: OCF ($3,168M) ran ahead of NI ($1,664M) on D&A ($627M), SBC ($188M) and a large working-capital release in the separation year (engine ΔNWC −$846M in financials_history.csv) — i.e. FY2023 OE is flattered and should not anchor the base. Both distortions are why the TTM base supersedes both years.
- **Engine balance-sheet miss (no flag fired — found in the CSV):** the engine reports net debt of $391M because the `LongTermDebt` tag is blank for FY2024 and FY2025 in financials_history.csv (debt_lt empty; only debt_current is captured), so HIGH_NET_DEBT does not fire. The v4 pass's 10-Q review documented total debt of ~$8.5B at 2026-06-28 — leverage of roughly 4x TTM owner's earnings, not the 0.22x the engine diagnostics imply. The leverage is folded into the verdict explicitly: at that leverage, with the dividend consuming most of TTM OE/share, deleveraging is slow and equity IRR is capped — consistent with the D-tier math rather than a reason to soften it. No figure here was recomputed in this run; the engine's $391M is simply not used as a leverage measure.
- No other flags fired: no BASE_DIVERGENCE (median $0.824 vs TTM $0.9355 — the TTM is higher on H1 2026 cash recovery, and both produce Tier D), no SECTOR_MODEL_MISMATCH (consumer health fits the OE model), no WIDE_SCENARIO_SPREAD (2.49x), TV share low at 17.7%.

## My thoughts / overlay
- The honest headline is two numbers, not one: standalone IV@15% ≈ **$7.36** vs a price of **$17.80** that is the Kimberly-Clark deal consideration. The gap is the market paying for Kimberly-Clark's balance sheet and synergy claims, not for Kenvue's standalone owner's earnings. Anyone buying KVUE at $17.80 is underwriting deal completion (shareholder votes done, U.S. antitrust cleared, EU clearance reported 2026-10-13, Q4 2026 close guided) and then owning the combined company — a different security from the one this DCF values.
- Method range: the preliminary v5 run (normalized $0.824 base, unadjusted −4.9% growth) gave weighted IRR 6.11% / IV@15% $5.39; the final TTM-base run gives 7.66% / $7.36; the v4 run yesterday gave 7.7% / $7.36. Every defensible variant is Tier D, and even the super-bull scenario alone is 10.89% — the verdict is robust, not assumption-dominated. The method spread changes the size of the shortfall, never its sign.
- Litigation is the live break-risk and downside-risk in one: the Tylenol prenatal-exposure MDL was dismissed in 2024, but the Second Circuit reinstated ~550 suits in July 2026 (restoring 3 of 5 plaintiffs' experts), and Kenvue/retailer defendants petitioned for rehearing in September 2026. Regulators and medical bodies say a causal link is not established, but a revived MDL plus political pressure on acetaminophen is exactly the kind of overhang that can complicate a closing or, standalone, pressure the flagship franchise (Self Care is the largest segment and its H1 2026 organic sales already fell 0.9% on weak illness incidence).
- Quality is not the debate: ~60% gross margins, strong cash conversion, a transformation/cost program, and Skin Health inflecting up (H1 2026 organic +4.4%, segment adjusted operating income up strongly). The debate is price vs earning power: a 5.26% OE yield on the TTM base for ~0–2% growth at the leverage documented in Flags does not clear a 15% hurdle standalone, full stop.

## Final verdict
- **Final tier: D** (weighted IRR 7.66% on the v5 final TTM inputs; no tier override — the deal overlay explains the market price but does not change standalone value)
- Confidence: **Medium** (filing-derived TTM base and all flags resolved; capped at medium by the binary deal-close and revived-litigation outcomes and by the engine's balance-sheet tag miss)
- One-liner: Iconic-brand consumer-health portfolio, moat 6/10, with real TTM owner's earnings of $0.94/share — but standalone it clears 15% only at ~$7.36 (margin of safety ~$5.50–6.00); at $17.80 the price is the Kimberly-Clark deal consideration, so the 7.7% weighted IRR is the break-value downside if the Q4 2026 close fails.
