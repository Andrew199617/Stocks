# SUI — Sun Communities, Inc.
Pass-1 run, 2026-10-17, engine 5.4.0. Price $118.08 (nasdaq_quote_api), market cap $14.748B, diluted shares 124.9M. In scope (<$40B).

All figures below are copied from dcf_numbers.json, financials_history.csv, fundamentals.json, or the cited company releases — none are recomputed.

## What it is
A REIT that owns the land under manufactured homes and RV communities: residents typically own their homes and pay Sun monthly lot rent, so turnover is very low. After two exits it is now a pure-play North American MH/RV operator: Safe Harbor Marinas (123 marinas) sold to Blackstone Infrastructure in April 2025 for ~$5.25B pre-tax cash (estimated book gain ~$1.4B, company Q1 2025 release), and the UK Park Holidays business sold Sept 22, 2026 for ~$1.03B net cash (GlobeNewswire). Portfolio at June 30, 2026: 455 developed properties, 156,130 developed sites in the US and Canada.

## Owner's earnings
From financials_history.csv (10-K via EDGAR). Conservative = OCF − capex − SBC; maintenance = NI + D&A − min(capex, D&A) − ΔNWC.

| FY | Revenue | OCF | Capex | SBC | Conservative OE | OE/share | Maintenance OE |
|---|---|---|---|---|---|---|---|
| 2023 | $2,284.1M | $790.5M | $7.1M | $35.1M | $748.3M | $6.04 | $280.1M |
| 2024 | $2,260.5M | $861.0M | $30.2M | $33.1M | $797.7M | $6.27 | $563.9M |
| 2025 | $2,306.1M | $864.2M | $457.0M | $37.4M | $369.8M | $2.96 | $1,464.8M |

- OE positive 5 of the last 5 fiscal years. **Base used = the engine's normalized base, the 3-yr median $6.0444/share** (base_source: median_of_last_3_fy_oe_per_share) — see BASE_DIVERGENCE below.
- The maintenance definition is the distorted one in 2025: it starts from net income, which contains the Safe Harbor gain (fundamentals.json: discontinued operations $1,429.6M in FY2025 against total net income of $1,413.9M — continuing operations were roughly breakeven on a GAAP basis). The OCF-based conservative series is the cleaner one and is used throughout.
- **TTM:** ttm.py cannot compute a TTM OE for SUI — capex is filed annually only, so there is no post-FY YTD capex fact (ttm.py exit 3). Filing-direct TTM through 2026-03-31 (fundamentals.json; EDGAR companyfacts has not yet ingested the Q2 2026 10-Q): revenue $2,343.8M (+3.64% YoY), OCF $889.6M (+3.15% YoY), SBC $45.0M, diluted shares 123.8M — OCF is stable-to-up versus FY2025's $864.2M, so the median base is not stale in substance. Q2 2026 (release, July 27, 2026): Core FFO $1.84/share vs $1.76 a year earlier; 2026 Core FFO guidance raised to $6.94–7.10/share.
- Capital returns: dividends paid $1,044.3M in FY2025 (includes the $4.00/share special distribution from the Safe Harbor proceeds) and buybacks of $539.1M in FY2025 (fundamentals.json); a further ~3.5M shares for ~$425M repurchased year-to-date through Sept 21, 2026 (company release). Declared DPS TTM $4.24 (fundamentals.json); Q3 2026 distribution declared at $1.12/share.
- **Balance sheet (DEBT_TAGS_BLANK — stated from filings/releases, not the engine):** the FY2025 debt tag is blank in EDGAR companyfacts, so the engine's net debt is unknown, not zero. Filed FY2024: total debt $7,387.8M, net debt $7,339.9M. Company-reported after the Safe Harbor sale: total debt ~$4.3B at Sept 30, 2025 with net debt / recurring EBITDA ~3.6x (proceeds included ~$1.6B of debt repayment); Q2 2026 release summaries put total debt at $4.1B at a 3.3% weighted average rate, net debt/EBITDA 3.9x, with a 3.5–4.5x target range. FY2025 cash $569.6M plus $66.5M restricted cash (financials_history.csv).

## Moat: 6/10 — moderate, real but capped
Justification: zoning-protected, irreplaceable MH sites plus high resident switching costs give durable ~5% rent growth and 98.8% occupancy, but returns are capped by resident affordability/politics, RV cyclicality, and no cost advantage on new capital.
- FOR: Residents own their homes but rent Sun's land; moving a manufactured home is costly, so turnover is very low and lot-rent increases stick — same-property adjusted blended occupancy 98.8% in Q2 2026. Restrictive zoning/NIMBYism makes new MH communities nearly impossible to entitle — the site base cannot be replicated at will. Affordable-housing shortage gives durable pricing power: ~5% MH rent increases delivered for 2026, same-property NOI +6.0% in Q2 2026 (MH +8.8%), 2026 NOI guidance raised to 4.5–5.3%. Scale: 455 properties / 156,130 sites post-exits.
- AGAINST: RV/transient revenue is discretionary and rate-sensitive; MH residents are lower-income, so outsized rent hikes invite political/regulatory backlash; growth capital must be deployed at market prices with no proprietary cost advantage; REIT multiple and refinancing costs move with long rates; measured ROIC history is thin (below).
- **ROIC / margin evidence (fundamentals.json, as required):** the `roic_proxy` series is only populated for 2016 (8.61%) and 2017 (7.69%) and is null from 2018 on — operating income is not tagged on the current filing basis, so the computed outputs do not show ROIC staying well above the cost of capital through a cycle. Gross margin on the SalesRevenueNet basis ran 88.2–90.9% across 2016–2022 and is null for 2023–25 on the Revenues basis. That evidence gap is itself a reason the moat is 6, not 7+: the franchise case rests on occupancy, rent prints, and supply constraint, not on a measured ROIC record.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — final run (2026-10-17)
**Growth recalibration (written reason):** the engine's blended start is −3.57%, but every blend component straddles the portfolio breaks — 3-yr revenue CAGR −8.08% and 2-yr OE/share CAGR −29.99% measure the marina exit, the UK discontinued-operations presentation, and the FY2025 capex spike, not the continuing business. The continuing-business prints are: same-property NOI +6.0% in Q2 2026 and +6.1% for H1 2026, MH NOI +8.8%, 2026 same-property NOI guidance raised to 4.5–5.3%, MH rent notices ~+5% and RV ~+4%, Core FFO guidance $6.94–7.10 vs the $6.59–6.67 post-sale 2025 range, filing-direct TTM revenue +3.64% YoY. Scenario starts were therefore set via offsets (+0.016 / +0.046 / +0.081 / +0.101 / +0.126 vs the blended −3.57%) to −1.97 / +1.03 / **+4.53** / +6.53 / +9.03%. Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25 (defaults — the recalibration is in growth, where the distortion was).

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | −1.97% | 0.75 | Rate shock + RV downturn; rent growth stalls | $30.47 | 5.54% |
| Bear | 25% | +1.03% | 0.90 | Growth fades to inflation-minus; UK exit charges linger | $41.78 | 6.86% |
| Base | 30% | +4.53% | 1.00 | NOI guidance delivered; ~5% MH rents, ~4% RV | $54.25 | 8.34% |
| Bull | 25% | +6.53% | 1.10 | H1 2026 NOI pace (+6.1%) persists; buybacks add per-share growth | $65.23 | 9.58% |
| Super bull | 10% | +9.03% | 1.25 | MH NOI pace (+8.8%) broadens; accretive redeployment of UK proceeds | $82.84 | 11.48% |

- **Probability-weighted: IV@15% $54.36 (−54.0% vs price), IV@12% $72.03, IV@10% $91.74, weighted IRR 8.36%, base-case IRR 8.34%**
- **Tier by numbers: D** — and D in the bear, base, and bull cases alike (no TIER_BAND). Diagnostics (dcf_numbers.json): OE yield 5.12%, terminal value 18.5% of IV@15%, scenario spread 2.72x, 9.5 months since FY end.
- **Hurdle-clearing prices:** clears 15% below $54.36, 20% below $38.45, 25% below $29.67.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): no TTM OE override is possible — ttm.py exits 3 because SUI files capex annually only, so there is no post-FY YTD capex leg. Resolved by evidence instead: filing-direct TTM OCF through 2026-03-31 is $889.6M vs FY2025's $864.2M, and Q2 2026 Core FFO grew year over year with guidance raised — the median base is not stale in substance.
- **BASIS_BREAK_SUSPECT**: three named breaks, and no growth input straddles them. (1) Safe Harbor Marinas acquired Oct 2020 (revenue +62% in FY2021) and sold April 2025 for ~$5.25B — marina revenue is in the 5-yr CAGR and out of the future. (2) Park Holidays UK, presented as discontinued operations and sold Sept 22, 2026 for ~$1.03B net — Q2 2026 carried a ~$1.1B non-cash valuation-allowance charge on the exit (release summaries). (3) The FY2025 capex spike (below). All scenario growth starts are set from continuing-business prints (same-property NOI, rent notices, Core FFO guidance), not from any filed CAGR.
- **NI_OCF_DIVERGENCE** (2023, 2024, 2025): 2025 — net income $1,413.9M vs OCF $864.2M because the ~$1.43B Safe Harbor gain sits in net income/discontinued operations while the $5.25B of proceeds are investing cash flow, not OCF. 2023 — net income −$206.9M vs OCF $790.5M, and 2024 — $103.6M vs $861.0M: the gaps are dominated by non-cash D&A of $494.1M (2023) and $490.5M (2024) plus discontinued-operations presentation ($82.3M and $74.2M in fundamentals.json). The OCF-based conservative OE series used for the base contains none of these items.
- **DEBT_TAGS_BLANK**: resolved in the balance-sheet paragraph above — FY2025 debt is not tagged, so no engine leverage verdict exists; company-reported total debt fell from $7,387.8M filed at FY2024 to ~$4.3B at Sept 30, 2025 (~3.6x net debt/recurring EBITDA) and $4.1B at Q2 2026 (3.9x). Leverage is moderate and falling, not unknown in reality — unknown only to the engine.
- **SECTOR_MODEL_MISMATCH**: Real Estate — confidence is **low** by rule. Substantively: an OE/capex DCF values only the cash-flow stream and prices the underlying land bank (carried at depreciated cost) at zero, and SUI's filed capex tag captures only a slice of real recurring property capex. The REIT cross-checks (below) are the right sanity frame.
- **BASE_DIVERGENCE** (latest FY $2.96 vs 3-yr median $6.04): the **latest year is the distorted one**. FY2025 filed capex under PaymentsToAcquireProductiveAssets spiked to $457.0M from $30.2M (2024) and $7.1M (2023) in the Safe Harbor transition year; the computed outputs do not decompose that spike, and it is not treated as a recurring run-rate. The median ($6.04, the FY2023 print; FY2024 printed $6.27) is corroborated by 2026 Core FFO guidance of $6.94–7.10/share. The opposite risk is noted honestly: filed capex of $7–30M in 2023/24 almost certainly understates true recurring property capex for a REIT, which would make even the median base generous — one more reason confidence is low and the verdict is sized to the conservative end.

## My thoughts / overlay
- **Method range:** the preliminary engine run (default moat 5, un-recalibrated −3.57% blend) gave weighted IRR 6.78% and IV@15% $41.71; the final recalibrated run gives 8.36% / $54.36. Both are Tier D — the verdict does not depend on the recalibration, only its size does.
- **REIT cross-check (the model-fit caveat in numbers):** the declared dividend annualizes to $4.48/share ($1.12 × 4), a 3.79% yield at $118.08; adding the guided ~4.5–5.3% NOI growth gives a high-single-digit expected total return — essentially the DCF's 8.36% weighted IRR. The model and the market agree on the return; they disagree with Andrew's 15% hurdle. At ~17x guided Core FFO ($6.94–7.10), the market is paying for the land bank's scarcity value and rate sensitivity, neither of which an OE DCF can see.
- The balance-sheet story genuinely improved: ~$1.6B of debt repaid from Safe Harbor proceeds, a $4.00/share special distribution, $539.1M of FY2025 buybacks plus ~$425M more in 2026, and leverage guided to 3.5–4.5x after the UK exit. None of that closes a 54% gap to the weighted IV@15%.
- Risks: long rates (REIT multiples compress as the 10-year rises), RV/transient cyclicality, political pressure on MH lot rents, and redeployment risk on the ~$1.03B of UK proceeds.

## Final verdict
- **Final tier: D** (weighted IRR 8.36% on the final inputs; D in every scenario, super bull included at 11.48%)
- Confidence: **Low** (SECTOR_MODEL_MISMATCH by rule; thin measured ROIC history and an undecomposed FY2025 capex spike on top)
- One-liner: Durable MH/RV REIT, moat 6/10 — does not clear 15% on owner's earnings at $118.08 (weighted IRR 8.4%, weighted IV@15% $54.36); clears 15% only below $54.36, and the OE/capex model prices its land bank at zero, so the D is a model-fit verdict as much as a price verdict.
