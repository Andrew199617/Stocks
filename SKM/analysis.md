# SKM — SK Telecom Co., Ltd.
Engine 5.4.0 run, 2026-10-17. All figures below are copied from dcf_numbers.json, key_numbers.md, fundamentals.json or the cited company releases — none are recomputed.

## What it is
South Korea's largest mobile carrier (NYSE ADS: SKM; KRX common stock), plus SK Broadband fixed-line/IPTV, enterprise ICT and a growing AI data-center (AIDC) business. IFRS (K-IFRS) filer on Form 20-F, reporting in KRW; the engine converts to USD at period-end ECB rates. In scope: under $40B on any basis (engine market-cap estimate $6.82B on its mismatched share×ADS-price basis; ~$12.3B implied by the ADS price and the 5/9 ratio).

## Owner's earnings
**FY2024 (latest FY in EDGAR companyfacts, USD-converted in financials_history.csv):** operating cash flow $3,459,353,800; capex $1,691,404,800; SBC $4,553,280 (negligible — always charged as a real cost, it is just tiny for this filer).
- **Conservative owner's earnings FY2024: $1,763,395,720 = $8.26 per ordinary share = $4.59 per ADS** (after the 5/9 ADS scaling in dcf_numbers.json).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC) FY2024: $2,897,456,440 — above the conservative figure because ΔNWC was strongly negative in FY2024; the conservative OCF-based figure is the one used.
- OE positive 5 of the last 5 fiscal years. Net cash: net debt −$1,375,922,880 (net_debt_to_normalized_oe −1.48x) on the TOTAL:Borrowings basis, with lease liabilities of $1,113,806,680 on top.

**Base used = normalized median of the last 3 fiscal years' OE/share: $7.85 per ordinary share → $4.36 per ADS** (base_source: median_of_last_3_fy_oe_per_share; FY2022 $7.85, FY2023 $6.92, FY2024 $8.26 per ordinary share). No TTM base: ttm.py reads us-gaap only and exits non-zero for this IFRS filer, and the FY2025 20-F (filed 2026-04-29) is not yet in EDGAR companyfacts (fundamentals.json warning), so the base stops at FY2024 — it is a **pre-breach** base. For reference, the company reported FY2025 (K-IFRS, press release): revenue KRW 17.0992 trillion (−4.7% YoY), operating income KRW 1.0732 trillion (−41.1%), net income KRW 375.1 billion (−73.0%), hit by the April 2025 cybersecurity incident (USIM replacements, fee waivers, Customer Appreciation Package; Q3 2025 operating income −90.9% YoY). AIDC revenue grew +34.9% to KRW 519.9 billion. The FY2025 collapse is handled through scenario weights, not the base.

## ADS RATIO — the preliminary run's fake Tier S
The preliminary run (no ads_ratio) printed Tier S, weighted IRR 28.1%, IV@15% $66.16 — by comparing per-ordinary-share OE with the per-ADS price. judgment.json carries `ads_ratio = {ratio: 0.5555555555555556 (5/9), kind: stated in the filer's own 20-F, source: "SK Telecom Form 20-F for the fiscal year ended December 31, 2025 (filed 2026-04-29), cover page: the registered American Depositary Shares are 'each representing five-ninths of one share of Common Stock' (NYSE: SKM) — the ratio in place since the October 2021 5-for-1 stock split"}` under step 8(d) bounded authority. Applied, it scales the base to $4.36/ADS and IV@15% down ~1.8x. This is the whole story of this run: the corrected verdict is Tier C, not S.

## Moat: 5/10 — moderate/narrow
Justification: South Korea's largest mobile carrier with spectrum/network scale, the leading brand, SK Broadband fixed-line/IPTV and a fast-growing AI data-center business, and ROIC proxy that recovered to 11.9%/12.6%/13.6% in FY2022-24 after the SK Square spin-off shrank the equity base. Against: a saturated, three-player market (KT, LG U+) with government tariff pressure and no real pricing power, KRW revenue CAGR negative over 5 and 3 years, the April 2025 cybersecurity breach showing trust is fragile, and a chaebol governance / Korea discount.
- FOR: Korea's #1 mobile carrier — spectrum, network scale and brand in a concentrated three-player market; ROIC proxy recovered to 13.6% by FY2024 (11.9% FY2022, 12.6% FY2023) after the SK Square spin-off; SK Broadband fixed-line/IPTV bundle plus enterprise ICT — recurring, contracted revenue; AIDC growth engine: AI data-center revenue +34.9% YoY in FY2025, Ulsan AIDC with AWS under construction.
- AGAINST: saturated market, government tariff pressure — no demonstrated pricing power; KRW revenue CAGR negative over 3 and 5 years; April 2025 cybersecurity breach — FY2025 operating income −41.1% YoY, net income −73.0%, trust and remediation costs are live; KT and LG U+ contest every segment; chaebol governance and KRW depreciation — USD revenue fell ~10% in FY2024 on FX alone in the engine's converted series.
- ROIC / margin evidence (fundamentals.json, KRW as filed): roic_proxy 7.1% / 5.2% / 3.0% / 2.7% / 2.5% / 7.8% / 11.9% / 12.6% / 13.6% for FY2016-24 — a decade mostly at or below the cost of capital, with the recent recovery flattered by the post-spin-off equity base; that is why this is a 5, not a 7. Gross margin is not presented in its IFRS filings (no cost-of-revenue tag; gross_margin is null in fundamentals.json); FY2024 operating margin was ~9.4% on the KRW figures in fundamentals.json.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — 5.4 final run (2026-10-17)
**Growth recalibration (written reason):** the engine's blended start is +1.48%, but it includes the maximum +5pp share-count adjustment driven by a −13.8%/yr share CAGR that is a basis artifact (diluted count 332.9M in FY2021 → 218.1M in FY2022 on the SK Square spin-off and split restatement), not buybacks — the actual FY2022-24 diluted count fell only ~1%/yr (218.1M → 217.5M → 213.4M). KRW revenue CAGR is −1.9% (5y) / −4.6% (3y) and FY2025 revenue fell 4.7%. Scenario starts were therefore recentered via offsets (−0.1348 / −0.0648 / −0.0148 / +0.0352 / +0.0852) to −10 / −5 / **0** / +5 / +10%: a 0% base start on the pre-breach median base, recovery-plus-AIDC in the bull cases, breach aftermath in the bear cases. Sanity check vs prints: the bull start (+5%) sits above every recent revenue print — justified only as OE/share recovery toward pre-breach economics plus AIDC growth, and weighted at only 17%; the super-bull start (+10%, 8%) is a tail, not a forecast. Probabilities shifted downside (15/30/30/17/8 vs default 10/25/30/25/10) because the breach-hit FY2025 is the current reality and is not in the base. OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $31.96 (nasdaq_quote_api).

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −10.0% | 0.75 | Breach churn sticks, tariff cuts, KRW slides | $15.88 | 8.14% |
| Bear | 30% | −5.0% | 0.90 | Slow trust rebuild; flat-to-down KRW revenue | $23.51 | 11.46% |
| Base | 30% | 0.0% | 1.00 | Pre-breach OE base holds, no real growth | $32.21 | 15.10% |
| Bull | 17% | +5.0% | 1.10 | Breach costs reverse; AIDC/enterprise compounds | $43.64 | 19.43% |
| Super bull | 8% | +10.0% | 1.25 | AIDC becomes a second engine; buybacks accelerate | $60.97 | 25.18% |

- **Probability-weighted: IV@15% $31.40 (−1.8% vs price), IV@12% $41.10, IV@10% $51.86, weighted IRR 14.78%, base-case IRR 15.10%**
- **Tier by numbers: C.** Diagnostics (dcf_numbers.json): OE yield 13.64%, terminal value 17.3% of IV@15%, scenario spread 3.84x, net debt −1.48x normalized OE, 21.5 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (latest FY ended 21.5 months ago): cannot be resolved with a TTM base — ttm.py is us-gaap-only and exits non-zero for this IFRS filer, and EDGAR companyfacts does not yet carry the FY2025 20-F (fundamentals.json warning). The median FY2022-24 base stands, with the breach-hit FY2025 (company-reported: operating income −41.1%, net income −73.0%) handled via downside-shifted probabilities; confidence is low for exactly this reason.
- **BUYBACK_TAILWIND** (share count −13.8%/yr): the −13.8% is a spin-off/split basis artifact (FY2021 332.9M → FY2022 218.1M), not buybacks; the real FY2022-24 decline is ~1%/yr. The +5pp growth credit it produced was removed by the recalibration above — not double-counted in the verdict.
- **NI_OCF_DIVERGENCE** (2022, 2023, 2024): D&A-explained, not a one-off. FY2024 net income $943,224,600 vs OCF $3,459,353,800, with D&A of $2,515,925,200 (financials_history.csv) — a capital-intensive carrier's depreciation accounts for the gap; the OCF-based conservative OE is unaffected.
- **FX_CONVERTED** (KRW → USD at period-end ECB rates): noted — flow facts use period-end, not average, rates; the KRW fell from 0.00077 (2023) to 0.00068 (2024) USD in the recorded rates, which alone cuts USD revenue ~10% YoY in FY2024. KRW weakness is a structural headwind to every USD figure here.
- **ADS_RATIO_APPLIED** (x5/9): see ADS RATIO above — sourced from the filer's own FY2025 20-F cover.
- **SHARES_FALLBACK** (2016-2019): those years use the basic/outstanding count (70,609,160, pre-split par-W500 basis) — per-share history there is approximate and is not used in the base (median of FY2022-24, all on the post-split diluted basis).
- **TIER_BAND** (bear C 11.5% vs bull B 19.4%): the verdict is sized to the bear end — Tier C, and the bear IV@15% ($23.51) sits well below the price.

## My thoughts / overlay
- The method range is the honest headline: no-ADS-correction the same engine run prints Tier S at 28.1% weighted IRR; with the filing's own 5/9 ratio and prints-based growth it prints Tier C at 14.8%. Every SKM number quoted without its ADS basis is wrong by 1.8x.
- Quality is real but mature: OE positive 5/5 years, net cash before leases, SBC negligible, DPS KRW 3,540 (FY2024, fundamentals.json) — a bond-like carrier cash machine whose growth options (AIDC +34.9% off KRW 519.9B of KRW 17.1T revenue) are still small.
- The open question the next filing answers: whether FY2026 operating income recovers toward the FY2024 base (KRW 1.69T operating income) or the breach permanently reset the cost/churn structure. The FY2025 20-F landing in companyfacts is the refresh trigger.
- Margin of safety: none at $31.96 on the weighted case (IV@15% $31.40); the price already pays for the base case. It clears the 15% hurdle only below ~$31.40, 20% only below ~$22.59.

## Final verdict
- **Final tier: C** (weighted IRR 14.78% on the ADS-corrected, recalibrated run; bear case 11.46%)
- Confidence: **Low** (stale FY2024 base with the breach year not yet in companyfacts, 3.84x scenario spread, FX-converted flows)
- One-liner: Korea's #1 carrier, moat 5/10 — at $31.96 the ADS sits essentially at the 15% hurdle on the pre-breach FY2022-24 median base ($4.36/ADS): weighted IRR 14.8%, weighted IV@15% $31.40 vs $31.96 price, Tier C sized to the bear end (bear IRR 11.5%); clears 15% only below ~$31.40, and the breach-hit FY2025 is not yet in the engine's base.
