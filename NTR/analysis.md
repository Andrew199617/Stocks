# NTR — Nutrien Ltd.
v5 run, 2026-10-14. All figures below are copied from dcf_numbers.json, financials_history.csv, ttm.py output, or key_numbers.md — none are recomputed.

## What it is
World's largest fertilizer company and largest agricultural-input retailer (Canadian, USD-reporting, IFRS/40-F filer, common shares directly listed on TSX and NYSE — not an ADS). Segments: Retail, Potash, Nitrogen, Phosphate. Price $70.49 (nasdaq_quote_api), market cap $34.29B — in scope under $40B.

## Owner's earnings
From financials_history.csv (SEC EDGAR, ifrs-full tags):
- FY2025: OCF $4,007,000,000; capex $1,882,000,000 (tag PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities); SBC $163,000,000 (tag AdjustmentsForSharebasedPayments — always a real cost).
- **Conservative owner's earnings FY2025: $1,962,000,000 = $4.03/share** (dcf_numbers.json: base_oe_total_latest_fy and base_oe_latest_per_share).
- Maintenance version FY2025 (NI + D&A − min(capex, D&A) − ΔNWC): $1,195,000,000 — materially below the conservative figure, mainly because ΔNWC was $1,589,000,000 in FY2025 (working-capital build). The OCF-based conservative figure is the cleaner base; the gap is a warning that FY2025 cash conversion absorbed working capital.
- OE positive 5 of the last 5 fiscal years, but violently cyclical: OE/share printed $10.73 in FY2022, $5.36 in FY2023, $2.98 in FY2024, $4.03 in FY2025 (per financials_history.csv OE totals and diluted shares).
- Net debt $9,162,000,000 = 4.67x normalized OE (diagnostics) — levered for a commodity cyclical.

**Base used = engine normalized base, median of last 3 FY OE/share = $4.03/share** (base_source: median_of_last_3_fy_oe_per_share; here the median and the latest year coincide at $4.0327). No TTM pin: see STALE_FY flag resolution below. This is a mid-to-low-cycle base, not the 2022 spike — that is the right anchor for a fertilizer cyclical, and no base_override is declared.

## MOAT: 5/10 — moderate/narrow
Justification: irreplaceable low-cost Saskatchewan potash mines with long-life reserves, North American low-cost nitrogen (cheap gas feedstock), scale as the world's largest fertilizer producer, and the largest ag-retail distribution network give a real cost and distribution advantage — but Nutrien is fundamentally a commodity price-taker in potash/nitrogen/phosphate, earnings swing with global fertilizer benchmarks it does not control, and returns collapse in down-cycles, so pricing power is not proven through a cycle.
- FOR: Low-cost, long-life Saskatchewan potash mines — among the world's largest reserves, not replicable on any investable timeline; scale as world's largest fertilizer company and largest crop-input retailer, with purchasing and logistics advantages; low-cost North American nitrogen plants on cheap natural gas feedstock (H1 2026 controllable potash cash cost below $60/tonne, per the Q2 2026 release); retail distribution network provides a steadier service/proprietary-products margin stream that dampens pure commodity exposure.
- AGAINST: Commodity price-taker — potash/nitrogen/phosphate prices are set globally; cyclicality proven in its own history (OE/share $10.73 in 2022 to $2.98 in 2024; revenue 3-yr CAGR -10.80%); new global potash supply (e.g. BHP Jansen) and Russian/Belarusian supply normalization can pressure prices; capital-intensive assets (capex ~$1.9–2.4B/yr in the filed history) with net debt 4.7x normalized OE; retail is low-margin distribution exposed to farm incomes, weather, and acreage.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Engine blended growth: rev CAGR 5y +5.16%, rev CAGR 3y -10.80%, latest rev YoY +3.52%, OE/share CAGR 2y -13.27% → g_blend -3.64%, plus +3.42pp buyback adjustment → **g_base -0.23%**. Default offsets and multipliers were kept — for a mid-cycle commodity name the standardized spread is the honest one, and no company-specific evidence justifies skewing it.
Sanity check vs actual prints: the base start (-0.2%) sits below the latest revenue YoY print (+3.52%) for a written reason — that revenue print is volume/price stabilization after the post-2022 normalization, while OE/share is still falling on a 2-yr view (-13.27% CAGR) and the 3-yr revenue CAGR is -10.80%; Q2 2026 (search result, BusinessWire release) showed sales $10.81B, up ~4% YoY, with net earnings $1.22B roughly flat YoY and adjusted EPS $2.61 — stabilization, not OE growth. The bull (+4.8%) and super-bull (+11.8%) starts bracket a genuine fertilizer up-cycle; neither is set below what an up-cycle actually prints (FY2022 OE/share was $10.73, ~2.7x the base).

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -10.0% | 0.75 | Fertilizer prices revisit trough; new potash supply lands into weak demand | $14.69 | 4.72% |
| Bear | 25% | -5.2% | 0.90 | Post-2022 normalization continues; retail margins squeezed | $21.54 | 6.03% |
| Base | 30% | -0.2% | 1.00 | Mid-cycle stasis: volumes grow, prices flat, buybacks offset drift | $29.51 | 7.63% |
| Bull | 25% | +4.8% | 1.10 | Benchmark prices recover; record potash volumes hold | $39.98 | 9.67% |
| Super bull | 10% | +11.8% | 1.25 | Supply shock (geopolitics/export curbs) reprices fertilizer up | $60.65 | 13.39% |

- **Probability-weighted: IV@15% $31.77, IV@12% $41.76, IV@10% $52.85, weighted IRR 8.12%, base-case IRR 7.63%**
- **Tier by numbers: D.** Diagnostics: OE yield 5.72%, terminal value 17.7% of IV@15%, scenario spread 4.13x, net debt 4.67x normalized OE, 9.4 months since FY end.
- Note the verdict does not hinge on the bull cases: even the super-bull scenario (13.39% IRR) does not clear 15% at $70.49.

## FLAGS — every fragility flag resolved
- **STALE_FY** (FY ended 9.4 months ago): ttm.py was run and exited non-zero, as expected for an IFRS filer (it reads us-gaap facts only): "ttm.py: cannot compute TTM for NTR (CIK 1725964): ocf: no annual (FY) fact; sbc: no annual (FY) fact; shares_diluted: no annual (FY) fact; capex: no capex facts in companyfacts under any candidate tag and no capex_override in judgment.json — refusing to zero-fill". No ttm.json was produced. Per the sweep spec, the engine's median base ($4.03/share) is used and the reason is stated here. Mitigating evidence from the Q2 2026 release (search result): H1 2026 net earnings and potash volumes were strong (record potash sales volumes, Retail and Potash H1 adjusted EBITDA each $1.24B per the release summary), so there is no sign the FY2025 base overstates the current run-rate — if anything H1 2026 ran above it, which is already reflected in keeping full bull/super-bull weight rather than skewing bearish.
- **BUYBACK_TAILWIND** (share count shrinking 3.4%/yr): already credited via the +3.42pp growth adjustment in the blend; not double-counted. A renewed NCIB for up to 5% of common shares was announced Feb 2026 (search result).
- **OE_VOLATILE** (OE/share range >3x over 5 years): real and structural — this is the fertilizer cycle (FY2022 $10.73/share at the price spike vs FY2024 $2.98). Handled by the normalized (median) base and by keeping the default 35% combined weight on bear/super-bear; it is also a core reason confidence is low.
- **NI_OCF_DIVERGENCE** (2023, 2024): explained by non-cash charges, not by cash earnings being fake. FY2023: net income $1,282,000,000 vs OCF $5,066,000,000 with D&A of $2,169,000,000 in the filed history; FY2024: net income $700,000,000 vs OCF $3,535,000,000 with D&A of $2,339,000,000 and a $530M impairment of assets in FY2024 (per Nutrien's filed FY2025 comparative statements, search result). The OCF-based conservative OE series used for the base already excludes these non-cash hits, so the divergence does not contaminate the base — but the impairments confirm asset values get written down in down-cycles.
- **ADS_RATIO_MISSING → ADS_RATIO_APPLIED** (40-F filer): resolved by declaration under bounded authority — judgment.json carries ads_ratio {ratio: 1.0, source, reason}. Nutrien's common shares are directly listed on the TSX and NYSE under NTR (Form F-10 filed 2026-03-31: "Our Common Shares are listed on the TSX and on the NYSE under the symbol NTR"); the NYSE security is the common share itself, not an ADS, so per-share figures and price are on the same basis. This matches the system README's v5.3 note listing NTR among direct-listed ordinary shares at ratio 1.0.
- **WIDE_SCENARIO_SPREAD** (4.13x): real — a commodity cyclical's outcome range is wide. Confidence is set to low (below the medium cap make_score would impose), and the verdict is sized to the conservative end.
- **HIGH_NET_DEBT** (net debt 4.67x normalized OE): folded into the verdict — at trough OE (FY2024: $2.98/share) leverage of this size is what turns a price down-cycle into equity pain; it is a reason the bear cases carry full default weight and the stock needs a much lower entry price, not a reason to override the tier.

## My thoughts / overlay
- Quality of the asset base is not the debate: the potash mines are genuinely scarce and low-cost, and H1 2026 execution (record volumes, sub-$60/tonne controllable potash cash cost) was good. The debate is price vs cycle: at $70.49 the market is paying for a sustained recovery the weighted scenarios do not deliver (weighted IV@15% $31.77 is 54.9% below the price — upside_at_15 -54.93% per dcf_numbers.json).
- Method range: the spread here is not method-fragile in the APP sense — every scenario, including super bull at 1.25x OE and +11.8% growth start, returns an IRR below 15%. Defensible inputs span roughly D to C, not D to A.
- Balance-sheet overlay: net debt $9,162,000,000 against a normalized OE base of $1,962,000,000 leaves buybacks/dividends dependent on fertilizer prices staying mid-cycle or better.
- Price that clears 15%: the weighted IV@15% itself, ~$31.77 — and with a margin of safety for a 4.13x-spread cyclical, a buyer wanting 15% with protection needs a price below even that. At $70.49 there is no margin of safety on any scenario in the table.

## Final verdict
- **Final tier: D** (weighted IRR 8.12% on the v5 final inputs; no tier override)
- Confidence: **Low** (WIDE_SCENARIO_SPREAD, OE_VOLATILE, HIGH_NET_DEBT, and an IFRS filer with no TTM pin — the median base is the filing-derived anchor available)
- One-liner: Real low-cost potash/retail franchise, moat 5/10, but a cyclical commodity price-taker with 4.7x net debt/OE — at $70.49 it does not clear 15%: weighted IRR 8.2%, weighted IV@15% $31.77; clears 15% only below ~$31.77.
