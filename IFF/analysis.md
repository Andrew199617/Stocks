# IFF — International Flavors & Fragrances Inc.
v5 run, 2026-10-15. Market cap $23.114B at $90.29 (nasdaq_quote_api) — in scope under $40B. All figures below are copied from dcf_numbers.json, ttm.py output (ttm.json), financials_history.csv, or key_numbers.md — none are recomputed.

## What it is
One of the big-four flavor & fragrance houses (with Givaudan, dsm-firmenich and Symrise — the top four hold over half the global market), selling taste, scent and health/biosciences ingredients to food, beverage, personal-care and pharma customers. It is mid-way through a portfolio breakup of the business built by the February 2021 DuPont Nutrition & Biosciences merger: Pharma Solutions was sold in 2025, the Soy Crush/Concentrates/Lecithin business has been sold, and Food Ingredients has a definitive sale agreement (reported ~$3.8B net, closing targeted by end of Q2 2027), after which IFF is a continuing business guided for FY2026 sales of $7.4–7.6B (+2–4%) and adjusted operating EBITDA of $1.53–1.6B (+4–8%). Q2 2026 continuing sales grew ~6% currency-neutral with adjusted operating EBITDA of $408M, and management announced a $2.5B buyback program funded in part by divestiture proceeds.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $850,000,000; capex $594,000,000; SBC $88,000,000 (always a real cost).
- **Conservative owner's earnings FY2025: $168,000,000 = $0.66/share** (base_oe_latest_per_share).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $2,244,000,000 in FY2025 — far above the conservative figure and NOT trusted here: its ΔNWC leg is a large negative in financials_history.csv driven by divestiture / held-for-sale reclassifications in a breakup year, not by a repeatable working-capital release. The OCF-based conservative series is the base throughout.
- OE positive 4 of the last 5 fiscal years (FY2022 conservative OE was negative). Net debt $5,404,000,000 (dcf_numbers.json).
- SBC is small ($88M FY2025, $88M TTM) — dilution is not the problem; capex ($594M FY2025, $621M TTM) and weak OCF conversion are.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $850,000,000 − prior YTD $368,000,000 + current YTD $679,000,000 = **TTM $1,161,000,000**
- Capex: FY $594,000,000 − prior YTD $274,000,000 + current YTD $301,000,000 = **TTM $621,000,000**
- SBC: FY $88,000,000 − prior YTD $51,000,000 + current YTD $51,000,000 = **TTM $88,000,000**
- Shares (current-YTD weighted diluted): **257,000,000**
- **TTM OE total $452,000,000 → base OE/share $1.7588** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $2.0703125/share and the latest FY is $0.65625/share. The TTM figure was chosen: it sits between the two, reflects the OCF recovery already printed in H1 2026, and does not carry the median's pre-breakup, higher-OCF years at full weight (see BASE_DIVERGENCE below).

## Moat: 5/10 — moderate / narrow
Justification: a top-four oligopoly seat with real formulation stickiness, but IFF itself has not converted that seat into durable returns — a decade of goodwill impairments on acquired businesses (including the FY2025 Food Ingredients impairment) is the evidence that the moat is narrower in IFF's hands than the industry structure suggests, and its earnings power is currently consumed by capex, interest-era OCF drag and restructuring.
- FOR: Top-four global F&F oligopoly — Givaudan, dsm-firmenich, IFF and Symrise together hold over 50% of the market; proprietary formulation libraries and confidential co-development embed IFF inside customers' finished products, creating real switching friction; global scale across taste, scent and biosciences that smaller houses cannot match; continuing business still growing (Q2 2026 continuing sales ~+6% currency-neutral, FY2026 EBITDA guided +4–8%).
- AGAINST: Givaudan is the clear market leader and dsm-firmenich was strengthened by its 2023 merger — IFF is not the share-gainer of the group; customers are large FMCG manufacturers with real bargaining power and pricing has largely been cost pass-through; repeated goodwill impairments (FY2022–FY2025, including Food Ingredients in FY2025) prove acquired earnings power was overpaid for and has decayed; fragrance-business antitrust investigations add legal cost and headline risk (named in the FY2025 10-K adjustments); the underlying category grows only mid-single digits, capping what even a good operator can compound.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Growth recalibration (written reason): the engine's blended growth is −4.89% (g_base), but every component is a breakup artifact — reported revenue fell −5.17% in FY2025 and the 3-yr revenue CAGR is −4.34% because businesses were being sold, not because the continuing business is shrinking; OE/share CAGR (2y) of −56.54% measures the impairment-era OCF trough. On a continuing basis the company just printed ~+6% currency-neutral sales growth in Q2 2026 and guides FY2026 sales +2–4% and EBITDA +4–8%. Scenario starts were therefore set via offsets (−0.0011 / +0.0489 / +0.0789 / +0.1189 / +0.1589 vs g_base) to −5 / 0 / **+3** / +7 / +11% — the base start sits inside the company's own guidance range, and even the super-bull start (+11%) is a stretch target, not a print. Probabilities were skewed bear-ward (15/25/30/20/10 vs the 10/25/30/25/10 default) for the leverage and OE volatility below; OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $90.29.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −5.0% | 0.75 | Food Ingredients sale slips, stranded costs stick, OCF stays at trough | $7.91 | 3.48% |
| Bear | 25% | 0.0% | 0.90 | Continuing business flat; capex stays heavy; deleveraging eats the cash | $11.70 | 4.07% |
| Base | 30% | 3.0% | 1.00 | Guided continuing growth; TTM OE base holds | $14.73 | 4.55% |
| Bull | 20% | 7.0% | 1.10 | EBITDA guide top end delivered; buybacks shrink the count | $19.13 | 5.27% |
| Super bull | 10% | 11.0% | 1.25 | Full post-breakup re-rating story: margins and OE conversion both recover | $25.63 | 6.31% |

- **Probability-weighted: IV@15% $14.92 (−83.5% vs price), IV@12% $19.71, IV@10% $25.04, weighted IRR 4.60%, base-case IRR 4.55%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 1.95%, terminal value 18.2% of IV@15%, scenario spread 3.24x, net debt 12.0x the TTM base OE, 9.5 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above with all four legs.
- **BASIS_BREAK_SUSPECT** (>60% revenue jump/drop in the last 5 years): identified — the February 2021 DuPont Nutrition & Biosciences merger more than doubled reported revenue (financials_history.csv: $5,084,000,000 in FY2020 → $11,656,000,000 in FY2021) and the share count roughly doubled with it; the current breakup (Pharma Solutions sold 2025, Food Ingredients sale agreed) is the same break in reverse. No CAGR straddling either break was trusted: the 5-yr revenue CAGR (16.46%) and the negative 3-yr CAGR were both discarded and scenario starts were set from continuing-operations prints and guidance instead.
- **OE_VOLATILE** (OE/share spans >3x over 5 years): real — conservative OE went negative in FY2022 and printed $0.66/share in FY2025 against the $2.07 median. Handled with the TTM base, a bear-skewed probability set (40% on bear-or-worse), and confidence capped below high.
- **NI_OCF_DIVERGENCE** (2023, 2025): identified — these are the non-cash impairment years. FY2023 net income was −$2,587,000,000 against OCF of $1,455,000,000, and FY2025 net income was −$359,000,000 against OCF of $850,000,000, with the FY2025 10-K attributing the loss primarily to a goodwill impairment in the Food Ingredients reporting unit, held-for-sale losses on the Soy disposal group and divestiture losses, partly offset by a debt-extinguishment gain. The impairments do not enter the OCF-based conservative OE, so the base is not contaminated — but they are counted as moat evidence above.
- **BASE_DIVERGENCE** (latest FY $0.66 vs 3-yr median $2.07): both are distorted in opposite directions. The latest FY is the trough (weakest OCF of the recent years plus the heaviest capex); the median carries pre-breakup years whose OCF included businesses now sold. The TTM base ($1.7588/share, OCF already recovering in H1 2026) is the least distorted of the three and was used.
- **LOW_OE_YIELD** (base OE yield 1.95%): real and decisive — at $90.29 the valuation rests almost entirely on an OE recovery that has not yet printed. This is why no scenario, including super bull at $25.63 IV@15%, comes close to the price.
- **HIGH_NET_DEBT** (net debt 12.0x the TTM base OE): folded into the verdict — net debt is $5,404,000,000. Management's own framing (net debt ~2.6x credit-adjusted EBITDA at end-2025, per its FY2025 reporting) is kinder because EBITDA ignores capex and SBC, but on an owner's-earnings basis the leverage is heavy: a bad OCF year like FY2025 leaves almost nothing after capex. The Food Ingredients proceeds (~$3.8B reported) and the announced >$1B debt reduction would ease this materially if the sale closes on schedule — that is a 2027 event, not a current fact, and the bear cases assume slippage.

## My thoughts / overlay
- The method range does not rescue this name: on the engine's median base ($2.07/share) with the same recalibrated growth, or on the TTM base used here, the weighted IV@15% stays in the teens — an order of magnitude below the $90.29 price. The market is pricing IFF on adjusted EBITDA and a successful breakup; this screen prices it on cash actually left after capex and SBC, and that cash ($452M TTM) is thin for a $23.1B market cap plus $5.4B of net debt.
- What would have to be true to clear 15%: OE/share would need to recover several-fold from the TTM base and keep growing — i.e. OCF conversion back to the FY2023 level ($1,455,000,000) at materially lower capex, sustained. Nothing in the FY2026 guidance (EBITDA +4–8%) implies that pace.
- Quality overlay: the continuing portfolio is a real business with a real oligopoly seat, H1 2026 free cash flow improved, and the balance-sheet plan (sale proceeds → debt reduction + buybacks) is coherent. The failure here is price versus owner's earnings, not business existence.
- Price that clears 15%: the weighted IV@15% is $14.92 — the stock would need to trade near that level (before any additional margin of safety) for the weighted case to clear Andrew's hurdle. At $90.29 there is no margin of safety in any scenario.

## Final verdict
- **Final tier: D** (weighted IRR 4.60% on the v5 final inputs — no tier override)
- Confidence: **Medium** (high on the filing-derived TTM base and on the direction of the verdict — every scenario and every defensible base lands far below the price; medium on the exact IV given OE volatility)
- One-liner: Real top-four F&F franchise, moat 5/10, but owner's earnings are trough-level ($1.76/share TTM) against heavy net debt — at $90.29 it does not clear 15% (weighted IRR 4.6%, weighted IV@15% $14.92); it would need to trade near $14.92 to clear the hurdle on this screen.
