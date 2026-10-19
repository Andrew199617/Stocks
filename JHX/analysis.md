# JHX — James Hardie Industries plc
Pass-1 run, 2026-10-17 (engine 5.4.0). In scope: market cap $14.08B at $25.82 (nasdaq_quote_api), under the $40B cutoff.

All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
The dominant North American fiber-cement maker (Hardie® siding/trim, ~90% category share) plus Australia/NZ and Europe fiber cement/gypsum — transformed on 1 July 2025 by the $8.75B acquisition of The AZEK Company (TimberTech composite decking, Versatex trim), which added a Deck, Rail & Accessories segment and a $500M revenue-synergy / $125M cost-synergy program. Repair & remodel is ~60-65% of demand, new construction the rest — so it is housing-exposed but not a pure homebuilder beta. Legacy asbestos claims are funded through the AICF, a permanent cash drag.

## Owner's earnings
**FY2026 (10-K, period ended 2026-03-31, from financials_history.csv):** revenue $4,835.8M (+24.7% YoY — almost entirely AZEK's nine months; legacy organic sales were flat-to-down through FY26); operating cash flow $589.8M; capex $383.9M; SBC $38.0M.
- **Conservative owner's earnings FY2026: $167.9M = $0.31/share** — a trough: net income fell to $104.0M (from $424.0M in FY2025) on AZEK acquisition/integration costs, a D&A jump to $493.5M (from $216.2M) as AZEK intangibles amortize, and interest on the acquisition debt (Q3 FY26 net interest $65.6M in one quarter vs $3.8M a year earlier).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $142.3M — same trough ballpark.
- OE positive 5 of the last 5 fiscal years, but the per-share series spans $0.001 (FY2023, a capex-peak year) to $1.48 (FY2021) — genuinely cyclical.
- Net debt $4,265.8M at FY2026 end (total debt $4,535.0M), vs $556.8M pre-deal — the AZEK financing. Lease liabilities $147.2M. Goodwill jumped to $4,780.4M and intangibles to $3,340.1M (fundamentals.json).

**Base used = TTM owner's earnings through Q1 FY27, from ttm.py (filing-direct, no hand math):**
- OCF: FY $589.8M − prior YTD $206.9M + current YTD $344.0M = **TTM $726.9M**
- Capex: FY $383.9M − prior YTD $103.2M + current YTD $89.8M = **TTM $370.5M**
- SBC: FY $38.0M − prior YTD $6.9M + current YTD $12.0M = **TTM $43.1M**
- Shares (current-YTD weighted diluted): **584,300,000**
- **TTM OE total $313.3M → base OE/share $0.5362** (base_source: ttm_json)
- Why not the engine's normalized base ($0.8276, median of last 3 FY OE/share)? That median is the FY2025 per-share figure — a pre-AZEK company on ~432M shares. A per-share median straddling a +35% share-count break and a business-mix break is not a coherent quantity. The TTM base is the only one that pairs a full twelve months of the combined company with the post-deal share count. It is still a trough base: it carries nine months of deal-era costs, and management's raised FY27 free-cash-flow target of $600M (Sept 15, 2026 Investor Day) sits well above TTM OE of $313.3M — that gap is handled in the scenario multipliers and growth, not by inflating the base.

## Moat: 6/10 — strong category dominance, cyclical and now levered
Evidence first (fundamentals.json): ROIC proxy 23.4% FY22 → 20.5% FY23 → 19.8% FY24 → 15.9% FY25 → 2.1% FY26. The FY26 collapse is acquisition accounting (goodwill/intangibles swelling invested capital, deal costs in operating income), but the pre-deal fade from 23% to 16% is real and is why this is not a 7. Gross margin: 36.3% FY22, 34.7% FY23, 40.4% FY24, 38.8% FY25, 35.8% FY26 (AZEK mix plus plant underutilization in a weak housing market).
- FOR: ~90% share of North American fiber cement — the Hardie brand is the category; national multi-year builder agreements and deep channel partnerships; proven pricing power (ASP +2% in a weak market, Q2 FY26); repair & remodel ~60-65% of demand, less cyclical than new construction; material-conversion runway (fiber cement on only ~8% of existing US homes; a $23B conversion opportunity cited at the Sept 2026 Investor Day); AZEK adds the leading composite deck/rail brand and exterior cross-sell, with the $125M cost-synergy target tracking a year ahead of schedule.
- AGAINST: housing-cycle volumes and plant utilization (FY26 Siding & Trim EBITDA margin compressed ~400bp on underutilization); cheaper substitutes (vinyl ~25-30% of siding, wood, stucco) cap pricing in downturns; fading pre-deal ROIC and gross margin; AZEK leverage ($4.27B net debt) and Trex competition in decking; the legacy asbestos funding obligation; capital intensity (capex $258-591M/yr over the last five fiscal years).
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — final run (2026-10-17)
Growth recalibration (written reason): the engine's blended start of 4.64% blends a +24.7% revenue YoY that is AZEK-inorganic with an OE/share CAGR of −44.4% that is a share-count/trough artifact, then docks revenue components a further 5pp for the AZEK share issuance. Neither artifact describes forward OE/share growth. The usable signals are management's FY27 guide — pro forma sales growth of 5.9-9.0% and pro forma adjusted EBITDA growth of 7.4-13.7% (raised Aug 6, 2026 after Q1 FY27 pro forma sales printed +12% and North American fiber cement grew +20% organically) — and the Sept 15, 2026 Investor Day long-term organic ambition of 4-7% above market. Scenario starts were therefore set via offsets (−0.11 / −0.05 / +0.02 / +0.07 / +0.12 vs the blended start) to −6.4 / −0.4 / **+6.6** / +11.6 / +16.6%. The base start (+6.6%) sits inside the FY27 pro forma sales guide and below the Q1 FY27 pro forma print (+12%) because OE/share also carries the new interest burden; the super-bull start (+16.6%) sits above the sales print on operating leverage in a housing recovery plus synergy drop-through — that is the reason it is weighted only 8%. Probabilities were shifted bear-ward (15/30/30/17/8 vs the 10/25/30/25/10 default) for leverage, cyclicality, and integration risk. OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $25.82.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −6.4% | 0.75 | Housing leg down; levered OE squeezes toward the debt | $2.22 | 3.42% |
| Bear | 30% | −0.4% | 0.90 | Weak housing persists; synergies offset volume drag only | $3.48 | 4.11% |
| Base | 30% | +6.6% | 1.00 | FY27 guide delivered; mid-single-digit pro forma growth, slow deleveraging | $5.29 | 5.19% |
| Bull | 17% | +11.6% | 1.10 | Material conversion + revenue synergies land; housing stabilizes | $7.26 | 6.35% |
| Super bull | 8% | +16.6% | 1.25 | Housing recovery operating leverage on the combined platform | $10.30 | 8.04% |

- **Probability-weighted: IV@15% $5.02 (−80.5% vs price), IV@12% $6.70, IV@10% $8.58, weighted IRR 5.07%, base-case IRR 5.19%**
- **Tier by numbers: D** (bear D, bull D — even the super-bull scenario IRR of 8.04% is a D). Diagnostics (dcf_numbers.json): OE yield 2.08%, terminal value 19.2% of IV@15%, scenario spread 4.63x, net debt 14.58x normalized OE (on the TTM base), 6.6 months since FY end.

## Flags — every fragility flag resolved
- **DILUTION** (share count +7.0%/yr): this is the AZEK consideration, not SBC creep — diluted shares went 432.1M (FY2025) → 545.5M (FY2026) → 584.3M (Q1 FY27 YTD) because AZEK holders were paid substantially in Hardie stock for the $8.75B deal. SBC itself is small: $43.1M TTM, ~5.9% of TTM OCF. The −5pp growth adjustment the engine applied for the share trend double-counts a one-time deal issuance; the scenario recalibration above replaces the distorted blend rather than stacking on it. Remaining small issuances are mechanical settlements of converted AZEK equity awards.
- **OE_VOLATILE** (OE/share spans >3x over 5 years): real cyclicality plus one capex-peak year (FY2023 OE/share $0.001 on $591.3M capex) and the FY26 deal trough. Handled with the TTM base, bear-shifted probabilities (45% on bear-or-worse), and a verdict sized to the conservative end — the tier is D in every scenario, so the volatility does not change the answer.
- **NI_OCF_DIVERGENCE** (>40% in 2024, 2025): direction is OCF well above net income (FY24: OCF $914.2M vs NI $510.2M; FY25: $802.8M vs $424.0M), i.e. earnings are cash-backed, not accrual-flattered. The largest identified leg in the filed history is non-cash D&A ($185.0M FY24, $216.2M FY25); the remainder is non-cash provisions (including asbestos) and working-capital timing in the 10-K cash-flow statements. The base used throughout is the OCF-based conservative OE, so the divergence does not contaminate it.
- **BASE_DIVERGENCE** (latest FY $0.31 vs 3-yr median $0.83): both are distorted, in opposite directions — the latest FY is the AZEK trough (deal costs, nine months of AZEK, full interest burden), and the median is a pre-AZEK per-share figure on ~432M shares. Resolved by using the TTM base ($0.5362/share on the post-deal 584.3M share count, full twelve months of the combined company); see Owner's earnings. Method check: the preliminary run on the median base printed a weighted IRR of 6.49% — also Tier D — so the base choice does not drive the verdict.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.63x super-bear): real — a levered cyclical's outcome range is wide. Confidence is low, and the tier is D at both ends of the band, so the spread is disclosed rather than decision-relevant.
- **HIGH_NET_DEBT** (net debt 14.58x normalized OE on the TTM base; 9.45x on the median base in the preliminary run): the balance sheet was reshaped by AZEK — total debt $4,535.0M and net debt $4,265.8M at FY2026 end vs $556.8M net debt pre-deal; reported net leverage was 2.87x adjusted EBITDA at Dec 31, 2025 (Q3 FY26 presentation). The multiple against trough OE overstates steady-state leverage but the direction is right: interest is now a first-order cost (~$65.6M net in Q3 FY26 alone), free cash flow is earmarked for deleveraging (FY27 FCF target raised to $600M), and the bear cases are weighted accordingly (45%).

## My thoughts / overlay
- The honest headline is the gap between price and any filing-derived OE path: at $25.82 the market is paying ~48x TTM owner's earnings per share ($0.54) and ~31x the pre-deal median ($0.83) for a cyclical building-products company. Even the super-bull scenario — 16.6% OE/share growth start, 1.25x OE multiplier — returns only 8.04%. There is no defensible method in this system that gets JHX near the 15% hurdle at this price; the method range across the two bases run today is D to D.
- What the market is actually buying: the AZEK synergy case ($125M cost synergies a year early, $500M revenue synergies), Q1 FY27's +12% pro forma print, and housing-recovery operating leverage. Those may all be real — they are just already in the price, with the debt ($4.27B net) senior to the equity story.
- Quality is not the debate: ~90% category share, pricing power through a weak housing tape, and R&R ballast are a genuine franchise (moat 6). The pre-deal ROIC fade (23% → 16% over FY22-25) and the FY26 margin compression are the things pass 2 should press on if the price ever makes the name interesting.
- Hurdle math: the stock clears a 15% IRR only below ~$5.02 (the weighted IV@15%), 20% below ~$3.52, 25% below ~$2.70 — i.e. roughly an 80% drawdown from $25.82. That is not a "wait for a dip" name at anything like current levels.

## Final verdict
- **Final tier: D** (weighted IRR 5.07% on the TTM base; D in every scenario from super bear to super bull, and D on the median base as well)
- Confidence: **Low** (trough base, 4.63x scenario spread, 14.6x net-debt-to-normalized-OE, AZEK integration unproven through a cycle — but the D verdict itself is robust: no scenario or base tried clears even 10%)
- One-liner: Dominant fiber-cement franchise, moat 6/10, transformed and levered by the $8.75B AZEK deal — at $25.82 the market is paying for synergies and a housing recovery, but TTM owner's earnings of $0.54/share support only a 5.1% weighted IRR (weighted IV@15% $5.02); it clears the 15% hurdle only below ~$5.
