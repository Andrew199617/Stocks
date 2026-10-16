# ZBRA — Zebra Technologies Corporation
v5 run, 2026-10-16. Market cap $19.486B at $380.50 (nasdaq_quote_api) — in scope (<$40B).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed.

## What it is
The leading enterprise automatic-identification and data-capture (AIDC) vendor: rugged mobile computers, barcode scanners and printers, RFID, machine vision, and the Zebra DNA software platform, sold into retail, logistics/warehousing, manufacturing, and healthcare. Two segments: Connected Frontline and Asset Visibility & Automation. Zebra closed the $1.3B cash acquisition of Elo Touch Solutions on 2025-10-01, which now contributes acquired revenue to reported growth.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $5,396M; net income $419M; operating cash flow $917M; capex $86M (tag: PaymentsToAcquirePropertyPlantAndEquipment); SBC $163M (tag: ShareBasedCompensation — always a real cost).
- **Conservative owner's earnings FY2025: $668M = $13.04/share** (base_oe_latest_per_share in dcf_numbers.json).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $472M — below the conservative figure; the gap is working-capital and non-cash noise (see NI_OCF_DIVERGENCE below), not a capex problem: Zebra is asset-light, capex runs ~1.6% of revenue.
- OE positive 4 of the last 5 fiscal years — the exception is FY2023, when conservative OE was −$146M on an OCF collapse to −$4M (demand downturn: FY2023 revenue $4,584M vs $5,781M in FY2022).
- Net debt $2,377M (dcf_numbers.json) — debt current $141M + long-term debt $2,361M vs cash $125M at FY2025 end; the Elo cash deal added leverage. Net debt is 3.1x normalized OE (diagnostics).

**Base used = TTM owner's earnings through Q2 2026 (period end 2026-07-04), from ttm.py (filing-direct, no hand math):**
- OCF: FY $917,000,000 − prior YTD $325,000,000 + current YTD $387,000,000 = **TTM $979,000,000**
- Capex: FY $86,000,000 − prior YTD $37,000,000 + current YTD $26,000,000 = **TTM $75,000,000**
- SBC: FY $163,000,000 − prior YTD $83,000,000 + current YTD $94,000,000 = **TTM $174,000,000**
- Shares (current-YTD weighted diluted): **48,776,549** (buybacks are shrinking the count — $568M repurchased in H1 2026 per earnings coverage)
- **TTM OE total $730,000,000 → base OE/share $14.97** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $13.04/share — the TTM base is used instead because FY2023's negative-OE year and the post-downturn recovery make the median stale; the TTM figure is the more current, filing-derived one and it is *higher*, so this choice does not flatter the verdict (the stock fails the hurdle on either base).

## Moat: 6/10 — moderate-strong, not wide
Justification: Zebra is the clear share leader in enterprise mobile computing and barcode printing with an installed base, software layer, and service network that create real switching friction — but the products are hardware, the cycle is tied to customers' capex budgets, and credible rivals (Honeywell, low-cost Android device makers) contest every refresh.
- FOR: market leadership in rugged mobile computing, scanning, and printing with a large installed base; Zebra DNA software platform and device-management integration raise switching costs; global sales/service channel and support network entrants can't quickly replicate; demonstrated pricing power — Q2 2026 gross margin 53.0%.
- AGAINST: hardware cyclicality — revenue fell ~21% in the FY2023 downturn; competition from Honeywell and lower-cost device makers on refresh cycles; component/memory (DRAM) supply constraints flagged by management coverage as a cost headwind; growth currently flattered by the Elo acquisition rather than purely organic demand.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-16)
Growth recalibration (written reason): the engine's blended growth is 4.80% — anchored on the 5-yr revenue CAGR (3.94%) and a negative 3-yr CAGR (−2.27%) that straddles the FY2023 downturn. Current prints are stronger: FY2025 revenue +8.33% YoY; Q2 2026 net sales +20.4% YoY with +9.2% organic (the rest acquisitions/FX, mainly Elo); FY2026 guidance is 14–16% sales growth including ~8pp from acquisitions/dispositions/FX. Scenario starts were therefore set via offsets (−0.10 / −0.04 / +0.03 / +0.09 / +0.16 vs g_base) to −5.2 / 0.8 / **7.8** / 13.8 / 20.8%: the base start (7.8%) approximates guided organic growth, and the super-bull start (20.8%) matches the Q2 2026 headline print rather than exceeding it. The super-bear start (−5.2%) is milder than the actual FY2023 revenue decline — the scenario spread is carried by the OE multipliers as well. Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25. Price $380.50.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -5.2% | 0.75 | 2023-style downturn repeats; levered OE compresses | $65.37 | 4.40% |
| Bear | 25% | 0.8% | 0.90 | Post-Elo digestion; organic growth stalls near zero | $102.41 | 5.80% |
| Base | 30% | 7.8% | 1.00 | Guided organic trajectory decays over the CAP | $155.38 | 7.83% |
| Bull | 25% | 13.8% | 1.10 | Headline growth holds as Elo synergies land | $223.05 | 10.25% |
| Super bull | 10% | 20.8% | 1.25 | Q2 2026 headline pace persists; margin expansion | $345.04 | 14.02% |

- **Probability-weighted: IV@15% $169.02 (−55.6% vs price), IV@12% $227.96, IV@10% $294.15, weighted IRR 8.39%, base-case IRR 7.83%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 3.93%, terminal value 20.3% of IV@15%, scenario spread 5.28x, net debt 3.10x normalized OE, 9.5 months since FY end.
- Even the super-bull IV@15% ($345.04) sits below the $380.50 price — no scenario in the set clears a 15% return at this price.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026 (period end 2026-07-04), inputs quoted above.
- **NI_OCF_DIVERGENCE** (2023, 2024, 2025): working-capital swings plus structural non-cash addbacks, not an earnings-quality red flag. FY2023: net income $296M vs OCF −$4M — the CSV shows a +$450M ΔNWC swing (inventory/receivables built into the demand downturn). FY2024: net income $528M vs OCF $1,013M — ΔNWC released −$196M, plus D&A $172M and SBC $89M added back. FY2025: net income $419M vs OCF $917M — D&A $185M and SBC $163M non-cash addbacks account for most of the gap. The OE base is built on OCF throughout, so the divergence does not contaminate it; the FY2023 episode is handled via the super-bear scenario, not by adjusting the base.
- **WIDE_SCENARIO_SPREAD** (5.28x): real — outcomes range from a cyclical downturn on a levered balance sheet to sustained acquisition-fed growth. Confidence is capped at medium, and the verdict needs no sizing-down: even the top of the range fails the hurdle.
- **HIGH_NET_DEBT** (3.1x normalized OE): folded into the verdict explicitly — net debt $2,377M after the $1.3B cash Elo acquisition, against TTM OE of $730M. Leverage is serviceable at current OE but leaves little cushion if a 2023-style OCF collapse repeats; this is why the super-bear OE multiplier (0.75) and a 10% weight are retained despite the current momentum.

## My thoughts / overlay
- This is a valuation failure, not a business failure. The franchise is real (moat 6/10), the TTM base ($14.97/share) is current and filing-derived, and management is buying back stock — but at $380.50 the OE yield is 3.93%, and no defensible scenario set gets the weighted IRR near 15%.
- Method range: on the engine's preliminary configuration (median base $13.04/share, default offsets) the weighted IRR was 6.80%; on the final configuration (TTM base, recalibrated growth) it is 8.39%. Both are Tier D — the verdict is not assumption-sensitive.
- One watch item inside the bull case: Q2 2026 margins included $73M of IEEPA tariff recoveries (per earnings coverage) — a one-off tailwind that should not be extrapolated; it sits inside the TTM OCF only via the quarters already filed and is one reason the base OE multiplier stays at 1.00 rather than higher.
- Hurdle-clearing price: the weighted IV@15% is $169.02 — that is the price at which the weighted case clears 15% before any margin of safety. With a margin of safety for the leverage and spread, ~$145–155 is the level where this becomes interesting.

## Final verdict
- **Final tier: D** (weighted IRR 8.39%; tier by numbers D, no override)
- Confidence: **Medium** (capped by WIDE_SCENARIO_SPREAD; the base itself is filing-solid)
- One-liner: Solid AIDC franchise, moat 6/10, but at $380.50 the weighted IRR is only 8.4% — it clears 15% only near $169, and even the super-bull IV@15 ($345) is below today's price.
