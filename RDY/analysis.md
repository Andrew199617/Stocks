# RDY — Dr. Reddy's Laboratories Limited

**Tier D — weighted IRR 4.58% · IV@15% $2.19 vs price $12.87 · moat 4/10 · confidence low**
Engine 5.4.0, run 2026-10-19. All figures below are copied from `key_numbers.md` / `dcf_numbers.json` / `financials_history.csv`; post-FY25 results are cited press/broker reports of the company's own IFRS releases, used only to calibrate scenarios (see STALE_FY).

## What it is

Hyderabad-based pharmaceutical company (NYSE ADSs, 1 ADS = 1 equity share): Global Generics — North America generics, India branded generics, emerging markets, and Europe (including the nicotine-replacement portfolio acquired from Haleon in September 2024) — plus Pharmaceutical Services & Active Ingredients (PSAI). Fiscal year ends March 31. It reports under IFRS in INR and files Form 20-F; the engine used the issuer's own filed USD convenience translations where present.

## Owner's earnings

Scored definition (conservative): OE = operating cash flow − capex − SBC, per share on diluted shares.

| FY (ended Mar) | OCF | Capex | SBC | OE | OE/share |
|---|---|---|---|---|---|
| 2023 | $716M | $138M | $5M | $573M | $0.69 |
| 2024 | $545M | $197M | $5M | $343M | $0.41 |
| 2025 | $545M | $322M | $5M | $218M | $0.26 |

Base OE/share is **$0.41**, the median of the last 3 fiscal years (`median_of_last_3_fy_oe_per_share`); latest FY is $0.26 and latest-FY OE total is $218.0M on 834,179,134 diluted shares. SBC is genuinely tiny ($5M/yr) — this is not an SBC story. The FY25 drop is a capex story plus flat OCF: capex rose to $322M while OCF stayed at $545M despite revenue up 13.76% YoY.

**Capex completeness (method note):** the engine's capex leg reads one filed line — purchases of property, plant and equipment. `statements.json` shows a second recurring investing line it does not read: purchases of intangible assets (`PurchaseOfIntangibleAssetsClassifiedAsInvestingActivities`) of ₹7,543M / ₹11,032M / ₹6,894M in FY23/24/25 — $91.7M / $132.3M / $80.7M at the period-end rates recorded in `dcf_numbers.json`. Charging them as capex would cut OE/share to $0.58 / $0.25 / $0.16 and the median base to $0.25 (−39%), so the scored base and IRR are upper bounds on this account too. The verdict does not move — Tier D on every variant (even the as-scored super-bull IRR is 7.50% against a $12.87 price). This is the tracked additive-capex-tag engine item (same family as AR/TXRH/MICC); redefining the capex leg is a code/spec decision, not a company-folder change.

The second (maintenance) lens points the same way: earnings power fell through FY25 and kept falling after it — FY26 (ended Mar 2026, reported May 2026 under IFRS) revenue ₹335,933M (+3.2% YoY) with PAT ₹42,850M, down roughly a quarter year on year; Q1 FY27 PAT fell ~69% YoY with EBITDA margin 12.5% vs 26.7%. The median base is therefore a *pre-cliff* base. Rather than a base_override (not permitted: FY26 figures are not in this run's engine outputs, and EDGAR companyfacts has not yet ingested the FY26 20-F's annual facts), the reset is carried in the scenario multipliers (base case 0.80× the median base) and bear-weighted probabilities. Treat the headline IRR as an upper bound on a stale base, not a precise estimate.

Balance sheet: net debt $375.0M (latest), 1.09× normalized OE — leverage is not the issue. Market cap $10.736B at $12.87 — in scope under $40B.

## Moat: 4/10 — weak-to-moderate (CAP 7.2 yrs)

Filing-direct evidence (fundamentals.json `roic_proxy`, gross margin): ROIC 17.9% (FY23), 17.9% (FY24), 14.5% (FY25); gross margin 56.7% / 58.6% / 58.5%. That history is respectable but it is the *old* regime: FY26 gross margin compressed (Q4 FY26 44.8%) and Q1 FY27 EBITDA margin printed 12.5%, so returns are resetting below the level a 7+ moat would require, with no through-cycle evidence at the new level.

FOR:
- Scale diversified generics platform across North America, India, emerging markets and Europe, plus PSAI/API.
- India branded-generics franchise compounding at mid-teens (FY26 India revenue +16%).
- Haleon nicotine-replacement portfolio (Sep 2024) added owned consumer brands; Europe revenue +55% in FY26.
- Filing-direct ROIC 14.5–17.9% and ~58% gross margins through FY25.
- Pipeline: 73 ANDAs pending at Q1 FY26 (43 Paragraph IV, 22 possible first-to-file); semaglutide and abatacept optionality.

AGAINST:
- No pricing power in commodity US generics; lenalidomide's protected volume window ended 31 Jan 2026 — North America revenue −22% in FY26, NA generics −41% YoY in Q1 FY27.
- The reset is in the prints: FY26 PAT down ~24%, Q4 FY26 PAT −86% YoY, Q1 FY27 PAT ~−69% YoY.
- Concentration was real: the lenalidomide shelf-stock adjustment alone cut FY26 revenue by ₹4,530M.
- USFDA compliance overhang (Form 483, seven observations, CTO-2 API facility, Nov 2024).
- ROIC falling, not through-cycle stable.

## DCF — final run (engine 5.4.0)

Growth sanity check (mandatory): the engine's blended start (g_base 5.48%; components rev CAGR 5y 10.48%, 3y 10.48%, latest YoY 13.76%, OE/share CAGR 2y −38.38%) is a backward FY23–25 blend. Actual recent prints are far weaker: FY26 revenue +3.2%, Q4 FY26 revenue −11.6% YoY, Q1 FY27 revenue −5.6% YoY. Scenario starts were therefore recalibrated *downward* with offsets — base starts at 0.0%, bear at −6.0% — and OE multipliers were cut below 1.0 because the median base predates the lenalidomide cliff (see BASE_DIVERGENCE). Super-bear start is −10.0% (the engine floors the start there).

| Scenario | Prob | Growth start | OE mult | IV@15 | IRR |
|---|---|---|---|---|---|
| Super bear | 20% | −10.0% | 0.50 | $1.03 | 3.37% |
| Bear | 30% | −6.0% | 0.65 | $1.58 | 3.90% |
| Base | 30% | −0.0% | 0.80 | $2.45 | 4.83% |
| Bull | 15% | 5.0% | 0.95 | $3.53 | 5.99% |
| Super bull | 5% | 10.0% | 1.10 | $4.94 | 7.50% |

**Weighted: IRR 4.58%, IV@15% $2.19** (@12% $2.87, @10% $3.61). Bear→bull IRR band 3.90% → 5.99%, both Tier D. Hurdle-clearing prices: 15% at $2.19, 20% at $1.58, 25% at $1.24. Diagnostics: OE yield 3.20%, terminal-value share @15% 17.3%, scenario spread 4.77×.

Probabilities are bear-shifted (20/30/30/15/5 vs the 10/25/30/25/10 default) because the bear case is not hypothetical — it is the last three reported quarters.

## Flags — every fragility flag resolved

- **STALE_FY** — Latest engine FY ended 2025-03-31 (18.6 months ago). The FY26 Form 20-F (period ended 2026-03-31) was filed 2026-05-29, but EDGAR companyfacts has not yet ingested its annual facts (fundamentals.py notes the same), so no FY26 OCF/capex/shares exist in the engine's inputs. `ttm.py` was run and cannot compute a TTM for this IFRS filer (it reads us-gaap facts only; it refused rather than zero-filling) — per spec, the median base is used and the staleness is handled in scenarios: FY26/Q1 FY27 reported results (revenue +3.2% FY26 then −5.6% YoY in Q1 FY27; PAT −24% FY26, ~−69% in Q1 FY27) set the growth starts and the sub-1.0 OE multipliers. Confidence is low for this reason.
- **DILUTION** — The 71.15% share-count CAGR is a split artifact, not dilution. Dr. Reddy's sub-divided each ₹5 share into five ₹1 shares effective 28 Oct 2024; each ADS continues to represent one equity share, so ADS holders received proportionately more ADSs. Earlier filings in the engine's history were not restated, so the CSV jumps from ~166M shares (FY22) to ~832M (FY23) — but the last three fiscal years (the base window) are all on the same post-split basis (831.9M / 833.5M / 834.2M, +~0.1%/yr), and SBC is only $5M/yr. The base is not inflated by this defect (contrast the NTNX/VIV units cases); the only damage is the spurious −5.00% growth adjustment inside g_base, which is immaterial next to the deliberate downward scenario recalibration. Named here per the share-scale rule: the 5× jump is the 5-for-1 split of 28 Oct 2024.
- **OE_VOLATILE** — OE/share spans >3× over five years ($0.26–$2.09 on mixed split bases; $0.26–$0.69 on the consistent post-split window). The normalized median base plus widened bear weight (50% combined super-bear + bear) is the response; confidence capped at low.
- **FX_CONVERTED** — Reporting currency INR converted at period-end ECB reference rates (frankfurter.app); rates per period end are recorded in `dcf_numbers.json` (e.g. 0.0117 USD/INR at 2025-03-31). Flow facts use period-end, not period-average, rates — a known approximation, noted.
- **USD_TRANSLATIONS_USED** — The issuer files its own USD convenience translations alongside INR figures; the engine used the filed USD figures where present. Noted as the basis.
- **ADS_RATIO_APPLIED** — Ratio 1.0 ordinary share per ADS, stated in the filer's own Form 20-F (FY2024: "One ADS represents one equity share") and unchanged by the Oct 2024 split per the company's share-capital disclosure; declared in `judgment.json` and applied by the engine. Per-ADS figures therefore equal per-ordinary-share figures; market cap $10.736B = $12.87 × 834,179,134 is on the correct basis.
- **BASE_DIVERGENCE** — Latest FY OE/share $0.26 vs 3-yr median $0.41. The *latest* year is the more honest direction but still not the distorted one to discard: FY25's fall is explained by filed lines — capex jumped to $322M (from $197M) while OCF was flat at $545M — and FY23's $0.69 was flattered by an unusually strong $716M OCF in the protected lenalidomide window. Neither end is clean; the median is kept as the engine base and the post-cliff reset is expressed through multipliers (base 0.80×) rather than by picking either year.
- **WIDE_SCENARIO_SPREAD** — Super-bull IV is 4.77× super-bear IV. Uncertainty is genuinely huge (post-cliff earnings power is unproven); confidence is **low**, as required.

## My thoughts / overlay

The market is pricing RDY ($12.87, ~31× the median base OE/share, OE yield 3.20%) for a recovery the filings have not yet shown: semaglutide (Canada/India, with an API-inventory provision already taken in Q1 FY27) and abatacept must replace a lenalidomide profit pool that has already evaporated, while India/Emerging Markets/Europe growth (+16% / +23% / +55% in FY26) carries the story. Method range: even the super-bull case (1.10× the pre-cliff median base, 10% growth start) yields only 7.50% IRR — no defensible method run today clears 10%, let alone 15%. If FY26's cash-flow facts land in companyfacts and show OE/share materially above the FY25 $0.26, the name deserves a refresh; on current evidence the gap to the hurdle price ($2.19) is too large for method choice to matter.

## Final verdict

**Tier D.** Weighted IRR 4.58% at $12.87; IV@15% $2.19 is 83.0% below the price. Sized to the conservative end as required: the bear and base cases cluster at 3.90–4.83% IRR, and the bull end (5.99%) is also Tier D, so there is no band ambiguity. A good business in a bad earnings regime — revisit only on a much lower price or on FY26 cash-flow facts proving the reset base wrong.
