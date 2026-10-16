# BR — Broadridge Financial Solutions, Inc.
v5 run, 2026-10-16. In scope (market cap $20.39B at $174.11, nasdaq_quote_api).

All figures below are copied from dcf_numbers.json or financials_history.csv — none are recomputed. Earnings/guidance facts are from the company's fiscal 2026 results release (PR Newswire, Aug 2026), summarized.

## What it is
Financial-infrastructure utility: Investor Communication Solutions (proxy distribution and voting, regulatory and customer communications) and Global Technology and Operations (capital-markets trade processing, wealth and investment-management technology). Per its 10-K scale summary, in fiscal 2026 it managed proxy voting for over 1 billion equity proxy positions, processed over 8 billion investor/customer communications, and processed on average over $18 trillion in tokenized and traditional securities trades per day. Revenue is heavily recurring and tied to regulated, non-discretionary workflows.

## Owner's earnings
**FY2026 (10-K via EDGAR, from financials_history.csv):** revenue $7,476,800,000; net income $1,124,300,000; operating cash flow $1,345,600,000; capex $67,200,000 (tag PaymentsToAcquirePropertyPlantAndEquipment); SBC $93,900,000 (tag AllocatedShareBasedCompensationExpense in FY2025–26, ShareBasedCompensation earlier — always treated as a real cost).
- **Conservative owner's earnings FY2026: $1,184,500,000 = $10.12/share latest FY** (dcf_numbers.json base_oe_latest_per_share $10.11528608027327).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,158,100,000 — close to the conservative figure, which supports the base.
- OE positive 5 of the last 5 fiscal years (oe_positive_years_of_last_5: 5/5).
- Net debt $2,851,700,000 (dcf_numbers.json net_debt_latest), 2.73x normalized owner's earnings (diagnostics) — material but serviceable for a recurring-revenue utility; folded into the verdict below.
- Diluted shares 117,100,000, drifting down (share_cagr −0.53%/yr), which the blend credits with a +0.53pp share-count adjustment.

**Base used = normalized median of the last 3 fiscal years' OE/share: $8.91/share** (base_oe_normalized_per_share $8.910397295012679, base_source: median_of_last_3_fy_oe_per_share). The latest FY ($10.12) sits above the median; the median is the right base because the 5-year OE path is volatile (see OE_VOLATILE below) and FY2026 EPS also benefited from a strong print (reported diluted EPS grew 35% in FY2026 per the release, vs 12% on an adjusted basis). No TTM override: fiscal year-end was 2026-06-30, only 3.55 months ago (diagnostics), and there is no STALE_FY flag.

**Growth inputs:** blended growth 8.47% (rev CAGR 5y 8.41%, rev CAGR 3y 7.25%, latest revenue YoY 8.53%, OE/share CAGR 2y 13.94%), g_base 9.00% after the share-count adjustment.

## Moat: 7/10 — strong
Justification: dominant, regulation-embedded position in proxy/investor communications and mission-critical trade processing with high operational and regulatory switching costs and proven through-cycle compounding — but contested by in-house operations and many vendors, exposed to financial-services volumes, and facing a print-to-digital shift.
- FOR: Dominant scale in proxy processing and investor communications — the de facto standard workflow for U.S. issuers, funds and broker-dealers
- FOR: Mission-critical, regulated workflows (proxy voting, trade processing) with high operational/regulatory switching costs
- FOR: Large recurring-revenue base — fiscal 2026 recurring revenues grew 8% and closed sales rose to $305 million (company release)
- FOR: Proven durability — revenue CAGR 8.41% over 5 years and OE positive 5/5 years through cycles
- FOR: Embedded with the largest wealth providers and primary dealers (10-K scale summary: services to the 15 largest U.S. wealth providers; fixed-income processing for 22 of 26 U.S. primary dealers)
- AGAINST: Competition from clients' in-house operations, transfer agents, proxy advisory/solicitation firms and numerous trade-processing and wealth-tech vendors (10-K competition disclosure)
- AGAINST: Customer base concentrated in financial services; the largest single client has been a high-single-digit share of revenue in recent fiscal years
- AGAINST: SEC move toward electronic default for proxy delivery could erode print/distribution economics even if Broadridge leads on digital
- AGAINST: Event-driven and position-count revenues are cyclical with equity markets and trading volumes (the FY2022 OCF trough below)
- AGAINST: Net debt 2.73x normalized owner's earnings limits flexibility if volumes fall
- A 7 gives CAP = 11.1 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 11.1 years, 15-year projection.

## DCF — v5 final run (2026-10-16)
Scenario sanity check against actual prints: fiscal 2026 recurring revenue grew 8%, total revenue grew 9% (release), latest revenue YoY is 8.53%, and fiscal 2027 guidance in the release calls for 6–8% recurring revenue growth (constant currency) and 8–12% adjusted EPS growth. The base start of 9.00% sits inside the guided EPS range — reasonable given operating leverage and buybacks. Bear (4.00%) and super bear (−3.00%) sit below guidance, as bear cases should if volumes turn. Bull (14.00%) is above the guide top and super bull (21.00%) is well above anything the company has printed on revenue — both are deliberately low-weight stretch cases (wealth/tokenization upside plus OE leverage), and even carrying them the weighted result only reaches Tier C, so they do not flatter the verdict. Default probabilities 10/25/30/25/10, default offsets −12/−5/0/+5/+12pp and default OE multipliers 0.75/0.90/1.00/1.10/1.25 were kept — the evidence (steady 8% recurring growth, guidance in line with history) does not justify skewing them. Price $174.11.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -3.00% | 0.75 | Market/volume downturn plus e-delivery erosion of print economics | $42.35 | 5.28% |
| Bear | 25% | 4.00% | 0.90 | Growth halves vs guidance; position counts stall | $70.60 | 7.65% |
| Base | 30% | 9.00% | 1.00 | Guidance-like EPS growth decaying over the CAP | $99.41 | 9.95% |
| Bull | 25% | 14.00% | 1.10 | Above-guide growth from wealth platform and tokenization wins | $138.69 | 12.76% |
| Super bull | 10% | 21.00% | 1.25 | Stretch case: sustained mid-teens-plus OE compounding | $219.78 | 17.56% |

- **Probability-weighted: IV@15% $108.36, IV@12% $147.27, IV@10% $191.16, weighted IRR 10.67%, base-case IRR 9.95%**
- **Tier by numbers: C.** Diagnostics: OE yield 5.12%, terminal value 21.21% of IV@15%, scenario spread 5.19x, net debt 2.73x normalized OE, 3.55 months since FY end.

## Flags — every fragility flag resolved
- **OE_VOLATILE** (OE/share range over the last 5 years spans >3x): the span is driven mainly by the FY2022 trough — FY2022 OCF was $443,500,000 and conservative OE $346,100,000 (financials_history.csv), vs FY2026 OCF $1,345,600,000 and OE $1,184,500,000 — plus genuine compounding since. It is volume/cycle sensitivity, not accounting noise: the business dipped hard in a weak-volume year and recovered. Resolved by using the 3-year median base ($8.91, below the latest $10.12) rather than the latest year, and by keeping the full 35% weight on bear-or-worse scenarios. No extra probability skew was added on top of those two haircuts — that would double-count.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 5.19x super-bear IV): real — the spread is mostly the growth-start range (−3% to +21%) on a long CAP. Confidence is set to medium (never high with this flag), and the verdict is sized to the conservative end: even the bull case ($138.69) sits below the $174.11 price.

## My thoughts / overlay
- Quality is not the debate: this is a strong-moat, recurring-revenue compounder with OE positive 5/5 years and an 8.41% 5-year revenue CAGR. Price is the debate: at $174.11 the market already pays for the bull path — the weighted IV@15% is $108.36, i.e. upside_at_15 is −37.76% (the IV sits 37.76% below the price).
- Method range: on the preliminary run (moat 5, screener price $165.45) the weighted IRR was 10.50%; the final run (moat 7, live price $174.11) prints 10.67%. Both are Tier C — the verdict is not assumption-sensitive at the tier level; no defensible input set gets this price near 15%.
- Balance sheet: net debt $2,851,700,000 (2.73x normalized OE) is folded in via the engine's net-debt adjustment and noted as a moat-against item; it does not change the tier but argues against paying up.
- Hurdle-clearing price: the weighted IV@15% is $108.36 — at or below that level the same cash flows clear Andrew's 15% hurdle, and a margin of safety against the bear case ($70.60) argues for demanding a price well under the weighted IV before treating it as a B.

## Final verdict
- **Final tier: C** (weighted IRR 10.67% on the v5 final inputs; tier by numbers C, no override)
- Confidence: **Medium** (capped by WIDE_SCENARIO_SPREAD; high on OE quality and the filing data, medium on any single growth path)
- One-liner: Strong-moat (7/10) financial-infrastructure compounder, but at $174.11 it prices in the bull case — weighted IRR 10.67%, IV@15% $108.36; it clears 15% only at or below ~$108.
