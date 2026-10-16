# NDSN — Nordson Corporation
v5 run, 2026-10-16. Price $328.80 (nasdaq_quote_api), market cap $18.714B — in scope under $40B.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed.

## What it is
Precision dispensing and fluid-management industrial technology, in three segments: Industrial Precision Solutions (adhesives, coatings, sealants dispensing for packaging, consumer, automotive, general industrial), Medical and Fluid Solutions (proprietary medical fluid components — tubing, balloons, catheters, connectors — expanded by the Atrion acquisition in August 2024), and Advanced Technology Solutions (electronics dispensing and test-and-inspection, expanded by CyberOptics). The model is engineered systems specified into customer production lines, plus recurring parts, service and consumables on the installed base.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $719,175,000; capex $58,060,000 (tag PaymentsToAcquirePropertyPlantAndEquipment); SBC $18,944,000 (tag ShareBasedCompensation, always a real cost).
- **Conservative owner's earnings FY2025: $642,171,000 = $11.28/share** (base_oe_latest_per_share $11.2828)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $549,060,000 — below the conservative figure, mainly working-capital movement; the OCF-based figure is the cleaner base series.
- OE positive 5 of the last 5 fiscal years. SBC is small relative to OCF ($18,944,000 vs $719,175,000 in FY2025) — no dilution/SBC-load red flag; diluted shares fell from 58,249,000 (FY2022) to 56,916,000 (FY2025) in the filed history, a mild buyback tailwind already credited in the growth blend (share_cagr −0.77%/yr, share_count_adj +0.77pp).
- Net debt latest: $1,887,812,000 (dcf_numbers.json) — see HIGH_NET_DEBT under Flags.

**Base used = TTM owner's earnings through Q3 FY2026 (period ended 2026-07-31), from ttm.py (filing-direct, no hand math):**
- OCF: FY $719,175,000 − prior YTD $516,264,000 + current YTD $570,473,000 = **TTM $773,384,000**
- Capex: FY $58,060,000 − prior YTD $49,002,000 + current YTD $40,313,000 = **TTM $49,371,000**
- SBC: FY $18,944,000 − prior YTD $13,255,000 + current YTD $17,512,000 = **TTM $23,201,000**
- Shares (current-YTD weighted diluted): **56,084,000**
- **TTM OE total $700,812,000 → base OE/share $12.4958** (base_source: ttm_json)
- The engine's normalized base (median of last 3 FY OE/share) is $10.1332/share — not used as the base because the TTM figure is more current and filing-derived; the median is retained in the reporting. The TTM base is also above the latest FY ($11.2828), consistent with the FY2026 acceleration below, so it is not a conservative-low choice — the Tier D verdict survives on the *highest* defensible base.

**Recent prints (search, Zacks / company release via search results):** fiscal Q3 2026 revenue $817.67M, +10.3% YoY, with Advanced Technology Solutions +28.4%, Medical and Fluid Solutions +5.0%, Industrial Precision Solutions +5%; adjusted EPS $3.25, +19% YoY. Full-year FY2026 guidance was raised to sales $3,035–$3,075M (+9–10% vs FY2025 revenue $2,791,687,000) and adjusted EPS $11.80–$12.00. Management expects Advanced Technology Solutions growth to moderate in fiscal 2027 after a peak cycle.

## Moat: 7/10 — strong, not wide
Justification: proprietary precision-dispensing process technology that is specified and validated into customer production lines — in regulated medical and in electronics processes, swapping a dispenser or inspection system risks revalidation and downtime, which makes the installed base sticky and supports recurring parts/service/consumables and durable segment margins. It is not a 9–10: there are no network effects, end demand is customer-capex cyclical, and larger diversified industrials and niche specialists compete in every segment.
- FOR: Proprietary dispensing/process technology specified into customer lines; Validation and requalification switching costs, especially medical and electronics; Recurring parts, service and consumables on the installed base; Proven pricing power — high segment margins held through cycles; Global service footprint across diversified end markets (packaging, medical, electronics, automotive, industrial)
- AGAINST: Customer-capex cyclicality — electronics/ATS is a peak-cycle business, guided to moderate in FY2027; Latest growth concentrated in ATS — Q3 FY2026 incremental EBITDA came essentially from ATS while the other two segments were flat; Acquisition-dependent growth (Atrion, ARAG, CyberOptics) with integration risk and acquisition debt; No network effects or owned platform — the technology lead must be re-earned against larger industrials and niche specialists; Interest expense rose in FY2025 on higher average debt from funding acquisitions (10-K, via search summary)
- A 7 gives CAP = 11.1 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 11.1 years, 15-year projection.

## DCF — v5 final run (2026-10-16)
Growth inputs: engine blended growth 4.65%, g_base 5.42% after the share-count adjustment. Components: revenue CAGR 5y 5.65%, revenue CAGR 3y 2.53%, latest revenue YoY 3.78%, OE/share CAGR 2y 5.52%. Default offsets (−12/−5/0/+5/+12pp) and default OE multipliers (0.75/0.90/1.00/1.10/1.25) were kept; probabilities 10/25/30/25/10.

**Sanity check vs actual prints:** the base start (5.42%) sits below the current prints (Q3 FY2026 revenue +10.3% YoY; FY2026 guidance +9–10%) — written reason: the TTM base already captures the FY2026 acceleration through Q3, management guides ATS to moderate in FY2027 after a peak cycle, and the long-run filed growth signals (3-yr revenue CAGR 2.53%, 5-yr 5.65%) center on mid-single digits. The bull start (10.42%) matches the current print and the super-bull start (17.42%) sits well above it, so the upside cases are not capped below observed reality.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -6.58% | 0.75 | Electronics capex rolls over hard; IPS/MFS stay flat; leverage bites | $50.28 | 4.10% |
| Bear | 25% | 0.42% | 0.90 | ATS peak passes, no offsetting recovery in industrial lines | $83.61 | 5.58% |
| Base | 30% | 5.42% | 1.00 | Mid-single-digit compounding on the TTM base over the CAP | $117.61 | 7.12% |
| Bull | 25% | 10.42% | 1.10 | Current ~10% growth pace persists longer; margins hold | $164.00 | 9.12% |
| Super bull | 10% | 17.42% | 1.25 | Durable electronics supercycle plus flawless acquisition compounding | $259.96 | 12.76% |

- **Probability-weighted: IV@15% $128.21 (−61.01% vs price), IV@12% $172.12, IV@10% $221.39, weighted IRR 7.65%, base-case IRR 7.12%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 3.80%, terminal value 19.90% of IV@15%, scenario spread 5.17x, net debt 2.65x normalized OE, 11.5 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 11.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q3 FY2026 (2026-07-31), quoted in full above.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 5.17x super-bear IV): real — the range is driven by the electronics cycle and the starting price, not by model noise. Confidence is capped at medium, and the verdict is sized to the conservative end. Note the spread does not rescue the price: even the super-bull IV@15% ($259.96) and super-bull IRR (12.76%) sit below the $328.80 price and the 15% hurdle.
- **HIGH_NET_DEBT** (preliminary run: net debt 3.27x normalized OE; final-run diagnostics: 2.65x on the TTM base): net debt is $1,887,812,000, acquisition-funded (Atrion closed August 2024). Mitigants from search results (Zacks Q3 FY2026 summary): the company repaid a net $258.03M of debt in the first nine months of FY2026, long-term debt fell to $1.53B from $1.68B at FY2025 end, and reported net debt leverage improved to 1.7x trailing EBITDA from 2.1x at FY2025 end. Leverage is being reduced, not spiralling — but at this price the equity has no cushion if the bear cases land, which is why the bear/super-bear weights total 35%.

## My thoughts / overlay
- Quality is not the debate: OE positive 5/5 years, tiny SBC load, buybacks shrinking the count, a 7/10 moat, and a TTM base that is *above* both the latest FY and the 3-yr median. The debate is price: $328.80 against a weighted IV@15% of $128.21.
- There is no defensible method range that reaches the hurdle here. On the median base the preliminary run gave a weighted IRR of 6.49%; on the TTM base the final run gives 7.65%; even the super-bull scenario alone returns 12.76%. Every defensible input set lands in Tier D.
- The price that clears 15% on the weighted case is the weighted IV@15% itself: **$128.21**. Even clearing 15% only in the super-bull case would require a price at or below $259.96. A buyer at $328.80 is paying for a super-bull outcome and still not getting a 15% return from it.
- Balance sheet folded into the verdict: $1,887,812,000 of net debt is serviceable and shrinking (see Flags), so this is a valuation verdict, not a solvency verdict — no tier softening for sector model (Industrials fits the OE model) and no tier override.

## Final verdict
- **Final tier: D** (weighted IRR 7.65% on the TTM base; tier by numbers D, no override)
- Confidence: **Medium** (high on OE quality and the TTM base; capped at medium by the 5.17x scenario spread)
- One-liner: High-quality precision-dispensing compounder, moat 7/10 — but at $328.80 it does not clear 15% in any scenario (weighted IRR 7.65%, weighted IV@15% $128.21; clears 15% only at ~$128).
