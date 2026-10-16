# RS — Reliance, Inc.
v5 run, 2026-10-15. In scope (market cap $21.503B at $406.67, nasdaq_quote_api — under the $40B cutoff).

All figures below are copied from key_numbers.md / dcf_numbers.json, ttm.py output (ttm.json), or financials_history.csv — none are recomputed. Quarterly earnings figures cited for context are from the company's Q2 2026 earnings release as returned by web search, and are labeled as such.

## What it is
The largest metals service center company in North America: a diversified distributor and value-added processor of carbon steel, stainless steel, aluminum, copper, brass, titanium and specialty metals, through roughly 310 locations, distributing over 100,000 metal products to more than 125,000 customers across aerospace, construction, energy, general manufacturing, infrastructure and transportation. The model is small orders with quick turnaround — about 49% of orders include value-added processing (cutting, leveling, slitting, sawing, machining, forming, coating) and about 40% are delivered within 24 hours (company description in its 2026 releases, via search). Growth is volume + metals price + a long roll-up (76 acquisitions since its 1994 IPO, per search summaries). This is a cyclical commodity-distribution business, not a compounder with contracted revenue: earnings track metals prices and industrial volumes.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $831,400,000; capex $328,900,000 (tag PaymentsToAcquirePropertyPlantAndEquipment); SBC $55,600,000 (tag ShareBasedCompensation — always a real cost).
- **Conservative owner's earnings FY2025: $446,900,000 = $8.45/share** (base_oe_latest_per_share in dcf_numbers.json).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $426,400,000 for FY2025 — same ballpark as the conservative figure, which raises confidence in the level.
- OE positive 5 of the last 5 fiscal years, but the level is violently cyclical in totals from financials_history.csv: $492,000,000 (2021), $1,711,500,000 (2022), $1,137,500,000 (2023), $942,400,000 (2024), $446,900,000 (2025) — the 2022 metals-price peak has been normalizing for three straight years. FY2025 revenue was $14,294,300,000, latest revenue YoY +3.32%.
- Net debt latest: $1,204,300,000 (dcf_numbers.json). Diagnostics put net debt at 2.13x normalized OE on the final (TTM-base) run — modest leverage for a distributor, not a balance-sheet story either way.

**Base used = TTM owner's earnings from ttm.py (filing-direct, no hand math), through 2026-03-31 — ttm.py's latest aligned YTD period:**
- OCF: FY $831,400,000 − prior YTD $64,500,000 + current YTD $151,400,000 = **TTM $918,300,000**
- Capex: FY $328,900,000 − prior YTD $86,900,000 + current YTD $64,200,000 = **TTM $306,200,000**
- SBC: FY $55,600,000 − prior YTD $12,200,000 + current YTD $13,300,000 = **TTM $56,700,000**
- Shares (current-YTD weighted diluted): **51,974,000**
- **TTM OE total $555,400,000 → base OE/share $10.69** (ttm_oe_per_share $10.686112286912687; base_source: ttm_json)
- The engine's normalized base (3-yr median FY OE/share) is $16.75/share — rejected as the headline base: it is the median of a peak-to-decline sequence (2023–2025), so it capitalizes 2023–24 price-peak economics that FY2025 ($8.45/share) and the TTM ($10.69/share) show have already normalized away. It is retained below as the method-range check.
- Caveat on the TTM window: ttm.py's aligned YTD legs end at 2026-03-31. The company has since reported Q2 2026 (earnings release via search: net sales $4.63B, up 26.5% YoY; diluted EPS $6.29, up 42% YoY; Q3 2026 diluted EPS guided to $6.40–$6.60). Those are earnings, not owner's earnings — Q2 benefited from higher carbon steel and aluminum prices, record tons, and a U.S. border wall project that contributed 5.2 percentage points of the tons-sold growth and $0.41 of diluted EPS in the quarter (release via search) — and rising prices/ volumes build working capital, which is exactly what separates EPS from OCF-based OE in this business. The TTM OE base is therefore the conservative, filing-computed anchor; the method-range check below shows the verdict does not depend on it.

## Moat: 5/10 — moderate / narrow
Justification: real scale and network advantages in a commodity distribution business — the largest North American footprint, purchasing leverage, local availability and value-added processing that regional rivals cannot match everywhere — but the product itself is a commodity, switching costs are low, and pricing power is mostly the metals market's, not Reliance's.
- FOR: largest metals service center network in North America (~310 locations) — scale purchasing power and geographic breadth no single regional rival matches; value-added processing on ~49% of orders (customers buy a finished part, not just metal, which adds service stickiness); extreme diversification — 125,000+ customers, 100,000+ products, many end markets — so no customer-concentration cliff; proven roll-up operator (76 acquisitions since 1994 IPO) with the balance sheet to keep consolidating a fragmented industry; disciplined capital returns — share count shrinking 4.91%/yr (engine share_cagr) and a long dividend record.
- AGAINST: the underlying product is a commodity — no IP, no brand pricing power, customers can dual-source from regional service centers and mills; earnings are a leveraged pass-through of metals prices (LIFO expense rises with prices; the Q2 2026 release recorded $1.64/share of LIFO expense vs $0.54 expected, via search) and industrial volumes; tariff/Section 232 support for domestic metals pricing is a policy variable, not a company asset, and can reverse; the current volume tailwind includes a finite U.S. border wall project; historical returns on capital collapse in downcycles (OE total fell from $1,711,500,000 in 2022 to $446,900,000 in 2025 on the filed history).
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Engine blended growth: g_blend −1.17% (components: revenue CAGR 5y +10.16%, revenue CAGR 3y −5.66%, latest revenue YoY +3.32%, OE/share CAGR 2y −33.76%), plus the +4.91pp share-count adjustment = **g_base +3.74%**. Default scenario offsets (−12/−5/0/+5/+12pp) and OE multipliers (0.75/0.90/1.00/1.10/1.25) were kept; probabilities are the defaults 10/25/30/25/10.

**Sanity check vs recent prints (required):** the scenario growth starts (−8.26% to +15.74% OE/share) sit well below the Q2 2026 earnings print (sales +26.5% YoY, diluted EPS +42% YoY, per the release via search). Written reason: those prints are a price-and-project spike, not a sustainable OE/share growth rate — average selling price and volumes were lifted by rising carbon steel/aluminum prices and the border wall project (5.2pp of tons growth), while the filed OE history shows the opposite long-run behavior after price peaks (OE/share CAGR 2y −33.76%; OE total down three straight years from the 2022 peak). A multi-year growth start at the Q2 print level would capitalize a spot metals price. The super-bull start (+15.74% with a 1.25x OE multiplier) is the recovery case, and it still does not clear the price — see the table.

Price $406.67. Base OE/share $10.69 (TTM, above).

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -8.26% | 0.75 | Metals prices normalize hard; volumes follow the 2023-25 OE slide | $41.87 | 3.60% |
| Bear | 25% | -1.26% | 0.90 | Post-peak plateau: OE/share flat-to-down from the TTM base | $67.40 | 4.48% |
| Base | 30% | 3.74% | 1.00 | Blended growth (buyback-credited) fades over the 8.5-yr CAP | $92.26 | 5.37% |
| Bull | 25% | 8.74% | 1.10 | Price/volume recovery holds; roll-up and buybacks compound | $124.83 | 6.54% |
| Super bull | 10% | 15.74% | 1.25 | Durable price upcycle + share gains vs the industry | $188.95 | 8.74% |

- **Probability-weighted: IV@15% $98.82 (−75.70% vs price), IV@12% $131.23, IV@10% $167.39, weighted IRR 5.64%, base-case IRR 5.37%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 2.63%, terminal value 18.70% of IV@15%, scenario spread 4.51x, net debt 2.13x normalized OE, 9.46 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.46 months ago): resolved by construction — the base is the TTM figure from ttm.py through 2026-03-31, quoted in full above. ttm.py's aligned legs end at Q1 2026; the later Q2 earnings release is addressed as context in the OE section (earnings spike, not filing-computed OE; verdict is unchanged on the higher median base — see method range).
- **BASE_DIVERGENCE** (latest FY OE/share $8.45 vs 3-yr median $16.75): the median is the distorted one for a headline base — it is drawn from 2023–2025, the descent from the 2022 metals-price peak, and capitalizes peak-cycle unit economics. The TTM base ($10.69) sits between the FY2025 trough print ($8.45) and the median, on the most recent filing-computed window. Both bases were run; both give Tier D (method range below).
- **OE_VOLATILE** (OE/share range over the last 5 years spans >3x): real and structural — this is a metals-price pass-through (OE totals $492.0M → $1,711.5M → $446.9M across 2021–2025 on the filed history). Handled with the normalized/TTM base choice, the default scenario weights (35% on bear-or-worse), and confidence held below high.
- **BUYBACK_TAILWIND** (share count shrinking 4.91%/yr): already credited via the +4.91pp growth adjustment in g_base; not double-counted in the verdict. Note the offsetting read: buybacks at $406.67 are executed at a 2.63% OE yield on the TTM base — repurchases at this price destroy per-share value relative to the same buybacks at lower prices, so the tailwind is worth less than its history.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.51x super-bear IV): real — the outcome range for a cyclical distributor IS wide. Confidence is capped at medium, and the verdict is sized to the conservative end. Note the spread does not rescue the stock: even the super-bull IV@15% ($188.95) is less than half the price.

## My thoughts / overlay
- **Method range:** the preliminary run on the engine's normalized median base ($16.75/share, same moat/probabilities/offsets/multipliers, price $406.52 on that run) gave weighted IV@15% $154.94 and weighted IRR 7.39% — Tier D. Its super-bull case gave IV@15% $296.27 and IRR 11.92% — still below the 15% hurdle and below the price. So across both defensible bases (TTM $10.69 and median $16.75) and across all ten scenarios run, no case clears 15% and no case reaches the current price at a 15% discount rate. The verdict is not base-sensitive; the price is simply capitalizing peak-ish earnings at a full multiple while filing-computed OE is mid-normalization.
- Quality is not the debate: OE positive 5/5 years, maintenance OE close to conservative OE, modest net debt ($1,204,300,000), a real network moat, and disciplined buybacks. The debate is price: at $406.67 the buyer pays for the 2026 price/volume spike (Q2 EPS +42% YoY, border wall volume, tariff-supported pricing) as if it were the run rate, on a business whose filed OE fell for three straight years after the last spike.
- Risks to this (bearish-on-price) verdict: a durable metals upcycle (tariffs + infrastructure + reshoring) could hold OE/share near peak longer than the fade assumes; the roll-up could add more than the growth fade credits; buybacks at any price still shrink the count 4.91%/yr. All three are in the bull/super-bull cases — and both still land far below the price.
- **Hurdle-clearing price:** the weighted IV@15% is $98.82 on the TTM base and $154.94 on the median base. A buyer who wants 15% with a margin of safety against the wide scenario spread should be shopping at or below the weighted IV@15% — i.e. roughly $99–$155 depending on the base believed, versus $406.67 today. There is no margin of safety anywhere near the current price.

## Final verdict
- **Final tier: D** (weighted IRR 5.64% on the final TTM-base run; 7.39% on the median-base preliminary run — D on both, no tier override)
- Confidence: **Medium** (high on the filing-computed OE history and on the cross-base robustness of the verdict; the wide scenario spread and the Q1-only TTM window cap it below high)
- One-liner: Quality cyclical metals distributor, moat 5/10 — does not clear 15% at $406.67 on any defensible base (weighted IRR 5.64% TTM / 7.39% median, weighted IV@15% $98.82 / $154.94); it clears 15% only at roughly $99–$155.
