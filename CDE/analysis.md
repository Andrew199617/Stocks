# CDE — Coeur Mining, Inc.
v5 run, 2026-10-16. All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed. Market cap (engine, on FY2025 share count): $9.555B at $15.545 (nasdaq_quote_api) — in scope under $40B; see the DILUTION flag for why the engine's share count is stale and why the company remains in scope anyway.

## What it is
U.S.-based precious-metals producer. After two all-stock acquisitions it operates seven wholly-owned mines: New Afton (gold-copper, British Columbia) and Rainy River (gold-silver, Ontario) from New Gold; Las Chispas (silver-gold, Sonora, Mexico) from SilverCrest; plus the legacy Palmarejo (gold-silver, Mexico), Rochester (silver-gold, Nevada), Kensington (gold, Alaska) and Wharf (gold, South Dakota) mines, and the Silvertip polymetallic exploration project in British Columbia. Revenue is gold first, silver second (~30% of Q2 2026 revenue), with copper now added from New Afton. It is a pure price-taker: earnings are set by gold/silver prices, grades, and costs — not by anything Coeur controls on the revenue line.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $886,879,000; capex $221,162,000 (tag PaymentsToAcquireProductiveAssets); SBC $19,209,000 (always a real cost, and here genuinely small next to OCF).
- **Conservative owner's earnings FY2025: $646,508,000 = $1.0518/share** (base_oe_latest_per_share).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $491,449,000 — same order of magnitude; the conservative OCF-based figure is used throughout.
- The history is brutal before FY2025: conservative OE was −$308,690,000 (2023, on a capex peak of $364,617,000 for the Rochester expansion) and −$20,976,000 (2024). OE positive in only **1 of the last 5 fiscal years**, and the engine's normalized base (3-yr median) is **−$0.0528/share** — on the median base alone this is a Tier F. Net debt at FY2025 end: −$536,601,000, i.e. net cash (key_numbers.md / dcf_numbers.json), and Q2 2026 reporting had cash more than doubling since year-end alongside a newly initiated capital-return program — the balance sheet is not the problem; the through-cycle earnings base is.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $886,879,000 − prior YTD $274,586,000 + current YTD $854,068,000 = **TTM $1,466,361,000**
- Capex: FY $221,162,000 − prior YTD $110,809,000 + current YTD $199,788,000 = **TTM $310,141,000**
- SBC: FY $19,209,000 − prior YTD $7,515,000 + current YTD $16,033,000 = **TTM $27,727,000**
- Shares (current-YTD weighted diluted): **867,417,000**
- **TTM OE total $1,128,493,000 → base OE/share $1.3010** (base_source: ttm_json)
- Why the TTM base and not the median: the median is the distorted figure here — it averages two pre-acquisition, pre-price-rally years in which the company was smaller and capex-peaked. The TTM base is still not clean, and that is handled in the scenarios, not hidden: it (a) consolidates Las Chispas for a full TTM but New Gold only from its March 20, 2026 closing (Q2 2026 was the first full quarter with New Afton and Rainy River), (b) is struck at historically high realized metal prices (Q2 2026 realized $4,140/oz gold and $71.18/oz silver, already declining within the quarter), and (c) uses a weighted share count (867,417,000) below the post-New Gold shares outstanding, because the new shares were only outstanding for part of the YTD period. Full-weighting the enlarged share count would lower OE/share; the bear-side OE multipliers and the low confidence grade carry that.

## Moat: 3/10 — weak; miners are price-takers
Justification: Coeur has no pricing power and no customer lock-in — it sells a commodity at spot. What passes for a moat in mining is cost-curve position, reserve quality/life, and jurisdiction; Coeur is mid-pack there, helped by one genuinely high-grade, low-cost asset (Las Chispas) and hurt by depletion, ramp risk at the newly acquired Canadian mines, and a history of buying growth with its own shares.
- FOR: Las Chispas is one of the world's highest-grade, lowest-cost silver-gold operations — a real cost-curve asset; seven-mine diversification across the U.S., Mexico and Canada reduces single-mine blow-up risk; scale after New Gold makes it a leading silver producer with a copper kicker; net-cash balance sheet plus record free cash flow funds a record exploration budget and buybacks without leverage.
- AGAINST: zero pricing power — revenue is the gold/silver spot price, which also inflated the current base; reserves deplete every year and must be replaced with capex or dilutive M&A; the two Canadian assets are still ramping (2026 guidance was trimmed in Q2 for slower ramps and lower prices) and carry purchase-accounting noise (a $140M non-cash stockpile-inventory impact hit Q2 net income); cost inflation (diesel cited by management); Mexico permitting/jurisdiction exposure at Palmarejo and Las Chispas.
- A 3 gives CAP = 5.9 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 5.9 years, 15-year projection. The 2.5% terminal rate is generous for a depleting-asset business and is kept only for sweep comparability — the verdict is sized accordingly.

## DCF — v5 final run (2026-10-16)
Growth recalibration (written reason): the engine's blended growth is 38.11% (g_base 33.11% after the −5pp share-count adjustment) because its components straddle two acquisitions and a metal-price spike — latest revenue YoY +96.41%, 3-yr revenue CAGR 38.11%. None of that is organic, repeatable OE/share growth: Q2 2026 revenue +126% YoY is New Gold consolidation, not compounding. Scenario starts were therefore set via offsets (−0.461 / −0.381 / −0.301 / −0.231 / −0.161 vs the blend) to −10.0 / −5.0 / +3.0 / +10.0 / +17.0%. The base start of +3.0% credits the mechanical full-year effect of New Gold (only ~9 months in 2026 guidance) and Rochester's ramp, partly offset by metal prices already rolling over in Q2; it sits far below the printed growth rates for the acquisition/price reasons above — this is the APP lesson applied in reverse, the prints are the artifact. Probabilities are bear-weighted (15/30/30/17/8) because the TTM base is struck at high metal prices; OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $15.545.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −10.0% | 0.75 | Gold/silver correct hard from highs; Canadian ramps disappoint | $5.11 | 6.30% |
| Bear | 30% | −5.0% | 0.90 | Prices normalize, costs inflate, full share count bites | $7.36 | 8.23% |
| Base | 30% | +3.0% | 1.00 | Full-year New Gold + Rochester ramp offset softer prices | $10.86 | 11.24% |
| Bull | 17% | +10.0% | 1.10 | Prices hold near highs; New Afton/Rainy River hit plan | $15.20 | 14.74% |
| Super bull | 8% | +17.0% | 1.25 | Metal bull market persists; Silvertip/exploration adds a leg | $21.83 | 19.55% |

- **Probability-weighted: IV@15% $10.56, IV@12% $13.93, IV@10% $17.67, weighted IRR 11.02%, base-case IRR 11.24%**
- **Tier by numbers: C.** Diagnostics (key_numbers.md): OE yield 8.37%, terminal value 18.0% of IV@15%, scenario spread 4.27x, net debt −0.67x normalized OE (net cash), 9.5 months since FY end.
- Even the super-bull case (8%) only reaches a 19.55% IRR at this price — there is no plausible path here to Andrew's 20%+ tiers without a much lower entry.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted in full above.
- **DILUTION** (share count +30.7%/yr): this is acquisition issuance, not SBC leakage — SBC is only $19,209,000 (FY2025) / $27,727,000 (TTM) — a few percent of operating cash flow. SilverCrest closed February 2025 (SilverCrest holders took ~37% of the combined company) and New Gold closed March 20, 2026 for 392,682,578 newly issued Coeur shares, leaving ~1,034,524,520 shares outstanding (company closing release) vs the engine's FY2025 count of 614,666,000. Consequences handled, not waved: (a) the engine's $9.555B market cap understates the true cap on the enlarged count — in words, the company is still comfortably under the $40B scope line; (b) the TTM base uses the 867,417,000 weighted count, and the residual full-weighting drag is carried in the bear weighting and low confidence.
- **BASIS_BREAK_SUSPECT**: confirmed, twice. (1) SilverCrest/Las Chispas (Feb 2025) is the main driver of FY2025 revenue +96.41% YoY (Las Chispas contributed $286.8M of the 9M-2025 revenue increase per the 10-Q, alongside $280.2M from higher realized prices). (2) New Gold (Mar 2026) breaks the basis again — pro forma 2025 combined revenue was $3,618,301,000 vs the standalone $2,070,126,000 in the filed history. No CAGR that straddles either break is trusted; scenario growth was set from the post-deal production/price picture instead (see the recalibration note).
- **NI_OCF_DIVERGENCE** (2023): in 2023 net income was −$103,612,000 vs OCF of $67,288,000, with D&A of $99,822,000 — the gap is the classic miner pattern of large non-cash depletion/depreciation (and a working-capital drag, ΔNWC −$105,541,000 in the filed history) sitting on top of a capex peak. The OCF-based conservative OE used throughout is unaffected by the non-cash side; the year matters only as evidence of how negative OE gets when capex peaks.
- **WIDE_SCENARIO_SPREAD** (4.27x): real — a miner's outcome range IS the metal price. Confidence is low, and the verdict is sized to the conservative end.

## My thoughts / overlay
- The honest headline is the method range: on the normalized median base (−$0.0528/share) this is a Tier F — no positive through-cycle OE. On the TTM base struck at high metal prices with two acquisitions consolidated, it is a Tier C at 11.02% weighted. The truth is that Coeur's OE is real now but unproven through a price cycle: 1 positive year in 5.
- Quality notes in its favor: SBC is negligible, the balance sheet is net cash (−$536,601,000 net debt), TTM capex of $310,141,000 against TTM OCF of $1,466,361,000 is a moderate reinvestment load for a miner, and management has started returning capital ($750M buyback authorization and a first dividend were announced with the New Gold close, per company releases).
- The price already pays for the transformation: at $15.545 the market is capitalizing peak-price TTM earnings. The stock clears the 15% hurdle only at or below the weighted IV@15% of $10.56 — and a margin of safety against the bear cases ($7.36 / $5.11 IV@15%) would demand an entry meaningfully below even that.
- Watch items: realized gold/silver prices (already fading within Q2 2026), New Afton/Rainy River ramp vs the trimmed guidance, and whether buybacks actually shrink the post-deal share count from here.

## Final verdict
- **Final tier: C** (weighted IRR 11.02% on the TTM base; Tier F on the normalized median base — the method range is F to C, sized to C only because the TTM base is filing-derived and current)
- Confidence: **Low** (WIDE_SCENARIO_SPREAD 4.27x, cyclical price-taker, hybrid TTM base mid-consolidation)
- One-liner: Price-taking precious-metals miner, moat 3/10 — TTM OE inflected on the SilverCrest and New Gold deals plus high metal prices, but at $15.55 the weighted IRR is only 11.0% (IV@15 $10.56); it clears 15% only below ~$10.56.
