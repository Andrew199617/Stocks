# DECK — Deckers Outdoor Corporation
Pass-1 run, 2026-10-18 (engine 5.4.0). In scope (market cap $12.497B at $85.71, nasdaq_quote_api).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, fundamentals.json or financials_history.csv — none are recomputed. Quarter and guidance facts are from the company's Q1 FY2027 reporting (quarter ended 2026-06-30, reported 2026-07-23) as returned in search results.

## What it is
Premium footwear built on two brands: HOKA (performance running / maximalist cushioning) and UGG (premium casual / sheepskin). The other-brands segment is being wound down (Koolaburra phase-out; other-brands sales fell 18.1% in Q1 FY2027). Asset-light, third-party manufactured (concentrated in Vietnam / Southeast Asia), sold through selective wholesale plus a growing direct-to-consumer channel. Fiscal year ends March 31.

## Owner's earnings
**FY2026 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,181,955,000; capex $84,623,000; SBC $44,835,000 (always a real cost).
- **Conservative owner's earnings FY2026 (OCF − capex − SBC): $1,052,497,000 = $7.22/share** (key_numbers.md: latest FY OE/share $7.22, latest FY OE total $1.052B)
- Maintenance version (from financials_history.csv): $1,086,320,000 — same ballpark as the conservative figure, which raises confidence.
- OE positive 5 of the last 5 fiscal years. No dividend. The capital return is the buyback: $338.2M repurchased in Q1 FY2027 alone at an average $103.79, with ~$4.7B remaining under authorization at 2026-06-30.
- Balance sheet (resolves DEBT_TAGS_BLANK, below): cash $1,907,249,000 at FY2026 year-end (financials_history.csv), $1.6B at 2026-06-30 per the Q1 FY2027 report, and **no outstanding borrowings** — the Q1 call states it directly, which is why no debt tag files. Operating lease liabilities are $375,194,000 (dcf_numbers.json). This is a net-cash company; the engine's blank net debt means "no debt to measure," verified from the filing, not assumed.

**Base used = TTM owner's earnings through Q1 FY2027, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,181,955,000 − prior YTD $36,146,000 + current YTD $47,904,000 = **TTM $1,193,713,000**
- Capex: FY $84,623,000 − prior YTD $23,940,000 + current YTD $15,222,000 = **TTM $75,905,000**
- SBC: FY $44,835,000 − prior YTD $8,739,000 + current YTD $10,741,000 = **TTM $46,837,000**
- Shares (current-YTD weighted diluted): **138,559,000**
- **TTM OE total $1,070,971,000 → base OE/share $7.73** (base_source: ttm_json)
- Why TTM over the normalized base: the 3-yr median ($6.03/share) is the distorted figure — its median year is FY2025 and the set includes FY2024 at $5.80, from the lower-margin, pre-scale era, while the latest FY printed $7.22 and the share count has since shrunk further (Q1 FY2027 weighted diluted 138,559,000 vs FY2026 average 145,805,000). The TTM base is the current run-rate.
- Basis note on the TTM denominator: ttm.py divides by the current-YTD share count (138,559,000); fundamentals.json's TTM block instead uses a duration-weighted average of the four quarterly counts (143,055,893) and prints OE/share $7.49 on the same TTM OE total. The $7.73 used here is the sanctioned ttm.py figure; the $7.49 variant is the conservative cross-check and would trim the weighted IRR modestly. Noted, not hidden.
- History caveat: there was a 6-for-1 split in September 2024 (fundamentals.json split_adjustments). Share counts and OE/share in the filed history before FY2023 sit partly on the pre-split basis, so pre-FY2023 per-share history is not comparable. The base (FY2024–26 median, latest FY, TTM) and the growth components that matter here are all on the post-split basis and are unaffected.

## Moat: 6/10 — moderate-strong brand moat, no switching costs
Justification: Two premium brands (HOKA, UGG) with proven pricing power — gross margin expanded from 50.3% in FY2023 to 57.7–57.9% in FY2025-26 on full-price selling and disciplined distribution — and returns on invested capital far above the cost of capital for five years, but footwear has no switching costs, both brands are fashion-exposed, and HOKA faces On, Nike and Brooks in its own category.
- Evidence (fundamentals.json): gross margin FY2022 51.0% · FY2023 50.3% · FY2024 55.6% · FY2025 57.9% · FY2026 57.7% · TTM 57.8%. The roic_proxy series runs 64.2% (FY2022), 65.8% (FY2023), 121.0% (FY2024), 149.3% (FY2025), 168.4% (FY2026) — the level is flattered by the tiny asset-light capital base (equity + debt − cash is small because the company holds $1.91B of cash against essentially no debt), but returns have sat far above any plausible cost of capital through the whole five-year window, including the tariff-hit years. That supports 6; it does not support 7+, because the return stream rests on brand heat, not on lock-in.
- FOR: HOKA and UGG brand strength with proven pricing power (gross-margin path above, full-price selling); distribution discipline — selective wholesale, controlled inventory (Q1 FY2027 inventory down 5% YoY) and DTC +13% in Q1 FY2027 protecting realization; asset-light model and net-cash balance sheet funding a buyback shrinking the count 3.1%/yr; international runway — 41.7% of FY2026 sales, growing +8.4% vs domestic +3.2% in Q1 FY2027.
- AGAINST: no switching costs — loyalty is fashion-driven and revocable, and UGG has faded before (FY2017 operating income was negative in the filed history); HOKA competition intensifying (On growing far faster in premium running, Nike retaking shelf space, Brooks in stability); two-brand concentration with the rest of the portfolio shrinking; Vietnam sourcing concentration — the unmitigated tariff impact was guided at roughly $150M for FY2026, and FY2027 gross-margin guidance of ~56.5% already embeds tariff and freight pressure; growth has decelerated hard (below).
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — final run (2026-10-18)
**Growth recalibration (written reason, mandatory sanity check):** the engine's blend is 15.30% (key_numbers.md components: rev CAGR 5y 16.54% · rev CAGR 3y 14.69% · latest rev YoY 9.76% · OE/share CAGR 2y 11.56%, plus the +3.07pp buyback adjustment on the revenue legs). That blend is a backward-looking average of the HOKA hypergrowth era and is contradicted by every current print: FY2026 revenue +9.76%, Q1 FY2027 revenue +5.7% (HOKA +7.7% to $703.5M, UGG +4.9% to $278.0M, DTC +13.0%), diluted EPS $0.94 vs $0.93 as SG&A rose 13% on international/DTC investment, and FY2027 guidance of $5.86–5.91B in sales (high-single-digit growth; HOKA low-double-digit, UGG mid-single-digit) with diluted EPS guided at $7.35–$7.50. Management's framework through FY2030 is high-single-digit revenue growth and low-double-digit EPS growth. Scenario starts were therefore set via offsets (−0.153 / −0.103 / −0.053 / −0.013 / +0.037 vs g_base) to 0 / 5 / **10** / 14 / 19%: the base start sits between the EPS guide and the FY2030 EPS framework, crediting buyback accretion and the FY2028+ SG&A leverage management guides to, without crediting a return to mid-teens growth that no current print supports. Even the super-bull start (19%) is a re-acceleration case, not a continuation case. Probabilities shifted bearish vs default (15/25/30/20/10) on the deceleration, the tariff load, and SG&A deleverage in FY2027. OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $85.71.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -0.0% | 0.75 | Brand heat fades, On/Nike take the category, tariffs bite unmitigated — OE/share stagnates | $42.52 | 8.58% |
| Bear | 25% | 5.0% | 0.90 | Guidance-level revenue, no SG&A leverage, margin drifts toward the ~56.5% guide and below | $63.74 | 11.87% |
| Base | 30% | 10.0% | 1.00 | HSD revenue, buyback accretion, SG&A leverage returns from FY2028 as guided | $88.46 | 15.37% |
| Bull | 20% | 14.0% | 1.10 | HOKA holds low-double-digit growth internationally, UGG 365/men's lines extend the cycle | $116.19 | 18.82% |
| Super bull | 10% | 19.0% | 1.25 | Re-acceleration: HOKA becomes a global top-tier athletic brand and margins re-expand | $164.62 | 23.95% |

- **Probability-weighted: IV@15% $88.55 (+3.3% vs price), IV@12% $119.56 (+39.5%), IV@10% $154.39, weighted IRR 15.38%, base-case IRR 15.37%**
- **Tier by numbers: B.** Hurdle-clearing prices (weighted path): clears 15% only at or below $88.55, 20% at $61.02, 25% at $46.11. Diagnostics (key_numbers.md): OE yield 9.02%, terminal value 20.4% of IV@15%, scenario spread 3.87x, 6.6 months since FY end.

## Flags — every fragility flag resolved
- **BUYBACK_TAILWIND** (share count shrinking 3.1%/yr): already credited via the +3.07pp growth adjustment in the engine blend. Not double-counted in the verdict — and note the recalibrated scenario starts are OE/share growth rates set against guided EPS growth, which already embeds the buyback, so the tailwind is if anything conservatively handled in the final run.
- **DEBT_TAGS_BLANK** (no debt tag for the latest fiscal year — net debt unknown to the engine): resolved from the filing — Deckers has **no outstanding borrowings** (stated in Q1 FY2027 reporting; $1.6B cash at 2026-06-30, $1,907,249,000 at FY2026 year-end per financials_history.csv) and operating lease liabilities of $375,194,000. The blank is the absence of debt, verified, not missing data; no leverage risk to the OE base.
- **TIER_BAND** (bear tier C at 11.87% vs bull tier B at 18.82%): real — the verdict spans tiers, so it is sized to the bear end in the verdict below. The weighted 15.38% sits only just over the 15% line.
- The preliminary default run also carried **WIDE_SCENARIO_SPREAD** (4.42x); the recalibrated final run prints 3.87x. Still wide — confidence is medium, not high.

## My thoughts / overlay
- The honest headline is how thin the clearance is. The preliminary run (median base $6.03, unadjusted 15.30% blend, default moat 5) printed a weighted IRR of 15.48% and IV@15% of $89.46 — nearly the same headline as the final run (15.38%, $88.55) but built from two offsetting errors: a stale base and a growth rate no current print supports. The final run's composition is the defensible one; the agreement of the two headlines is coincidence, not confirmation.
- Quality is not the debate: 57.8% TTM gross margin, OE yield 9.02% at this price, net cash, inventory down 5% YoY in Q1 FY2027, and a buyback executed aggressively ($338.2M in one quarter). The debate is duration — how long a two-brand fashion business holds HSD growth against On and a re-investing Nike, with a tariff load on Vietnam-made product.
- Margin of safety: essentially none against the weighted case (IV@15% is 3.3% above price) and none against the bear case (bear IV@15% $63.74 is well below the $85.71 price). A buyer here is paid if the base case delivers, and needs the price at or below $61.02 to be paid at a 20% hurdle.

## Final verdict
- **Final tier: B** (weighted IRR 15.38%; sized to the conservative end per TIER_BAND — the bear case is Tier C at 11.87%)
- Confidence: **Medium** (high on the OE base and balance sheet, medium on growth duration; scenario spread 3.87x)
- One-liner: Premium two-brand footwear compounder, moat 6/10 — just clears 15% on the TTM base (15.4% weighted, IV $88.55 vs $85.71) with the verdict sized to the bear end (Tier C at 11.9%); it clears 15% only below $88.55, so there is almost no margin of safety at the current price.
