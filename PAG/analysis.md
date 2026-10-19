# PAG — Penske Automotive Group, Inc.
Engine 5.4.0 run, 2026-10-17. All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json or fundamentals.json — none are recomputed.

## What it is
Diversified international transportation services company and one of the world's premier automotive and commercial truck retailers (10-K / Q2 2026 release): franchised dealerships in the US and UK (Sytner), heavy premium/luxury brand mix, Premier Truck Group (commercial trucks), commercial vehicle distribution in Australia, and an equity stake in Penske Transportation Solutions (full-service leasing). Revenue FY2025 $31.81B (financials_history.csv). Market cap $14.062B at $212.42 (nasdaq_quote_api) — in scope under $40B.

**Live deal overhang:** in Q2 2026 the board formed a special committee to evaluate a non-binding proposal from Penske Corporation and Mitsui & Co. to acquire the shares they do not already own at **$210 per share in cash**. The $212.42 market price sits essentially on that proposal — it is a control/deal price, not a standalone DCF price. That context explains, but does not change, the valuation gap below.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $975,100,000; capex $324,600,000; SBC $30,200,000 (always a real cost).
- **Conservative owner's earnings FY2025 (OCF − capex − SBC): $620,300,000 = $9.37/share** (key_numbers.md: latest FY OE/share $9.37, latest FY OE total $620.3M)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $468,700,000 (financials_history.csv) — below the conservative figure; the OCF-based figure is the cleaner one and is used throughout.
- OE positive 5 of the last 5 fiscal years. Net debt $2.101B (key_numbers.md), plus lease liabilities of $2,563,000,000 (dcf_numbers.json).
- OE/share history is cyclical, not a growth line: $12.35 (2020), $12.79 (2021), $15.46 (2022), $10.76 (2023), $12.31 (2024), $9.37 (2025) — the pandemic-era GPU windfall has been normalizing for three years.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $975,100,000 − prior YTD $500,200,000 + current YTD $419,100,000 = **TTM $894,000,000**
- Capex: FY $324,600,000 − prior YTD $157,600,000 + current YTD $134,900,000 = **TTM $301,900,000**
- SBC: FY $30,200,000 − prior YTD $16,900,000 + current YTD $15,800,000 = **TTM $29,100,000**
- Shares (current-YTD weighted diluted): **65,770,606**
- **TTM OE total $563,000,000 → base OE/share $8.56** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $10.76/share — rejected as the base: it averages in the stronger 2023–24 years while the current trajectory is down (TTM OE/share in fundamentals.json is $8.40 on its quarterly construction, revenue TTM +0.64% YoY, OE TTM −18.36% YoY). The median is the distorted base here; the TTM figure is current and conservative. The method range is reported under Thoughts — both bases land in Tier D.

**Q2 2026 print (company release, via search):** revenue $8.5B, +6% YoY; same-store retail automotive revenue +6%; adjusted EPS $3.62 excluding a $30.5M gain on dealership sales (GAAP EPS $3.96); new-vehicle retail GPU $4,782 (−10.4% YoY per Zacks summary), used GPU $2,095; service & parts same-store revenue +2% with gross margin +80bp to 59.5%; Class 8 orders +170% YoY; long-term debt reduced $141M in the quarter; dividend raised to $1.44 — the 23rd consecutive quarterly increase. Six-month revenue $16.4B vs $16.0B a year earlier; six-month net income down year over year.

## Moat: 5/10 — moderate / narrow
Justification: franchise-protected local dealership territories, scale as the second-largest US franchised dealer group, premium/luxury brand mix and a high-margin recurring service & parts business give a moderate moat; ROIC was 17.0–19.6% in 2022–23 but has fallen to 12.4% in FY2025 and gross margin has eased from 17.4% to 16.4%, while powerful OEMs control allocations and brand standards, margins are thin (~4% operating) and the business is deeply cyclical — so 5/10, not higher.
- FOR: State franchise laws create protected local dealership territories; scale — second-largest US franchised dealer group, leverage in OEM allocations and acquisitions; premium/luxury brand mix with better margins than volume peers; service & parts — recurring, ~55–60% gross-margin revenue that cushions vehicle-sale cyclicality (Q2 2026 same-store service & parts revenue +2%, gross margin +80bp to 59.5%); diversification beyond US retail autos — Premier Truck Group, Australia/UK operations and the Penske Transportation Solutions equity stake.
- AGAINST: OEMs hold the power — they control production, allocations, franchise size/location and brand standards; thin economics — blended gross margin 16.4% in FY2025 (17.4% in 2021–22), operating margin only 4.03%; ROIC falling through the cycle — 19.6% (2022) → 17.0% → 14.4% → 12.4% (2025) per fundamentals.json roic_proxy; cyclical vehicle demand, affordability and interest-rate exposure — new-vehicle GPU fell 10.4% YoY in Q2 2026; direct-to-consumer OEM models threaten the franchise model long term, with intense rivalry from AutoNation, Lithia and private dealers.
- **ROIC / margin evidence (fundamentals.json, roic_proxy series):** 11.0% (2020), 18.5% (2021), 19.6% (2022), 17.0% (2023), 14.4% (2024), 12.4% (2025) — still above a typical cost of capital, but falling for three straight years. Gross margin: 15.58% (2020), 17.38% (2021), 17.40% (2022), 16.65% (2023), 16.37% (2024), 16.40% (2025); TTM gross margin 16.15%. A moat above 6 would need ROIC holding in the high teens; the trend says the opposite.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — final run (2026-10-17)
**Growth sanity check (written reason for recalibration):** the engine's blended growth is 6.01%, built from rev CAGR 5y 9.24% (inflated by the post-COVID recovery), rev CAGR 3y 4.57%, latest rev YoY −0.18% and OE/share CAGR 2y −6.66%. The actual current prints are far below the blend: FY2025 revenue −0.18% YoY, TTM revenue +0.64% YoY and TTM OE −18.36% YoY (fundamentals.json), with Q2 2026 revenue +6% YoY the strongest recent print. The preliminary run's default starts (−4.0% / +1.0% / +6.0% / +11.0% / +18.0%) put the super-bull start at nearly 3x the best recent revenue print — indefensible. Scenario starts were therefore set via offsets (−0.10 / −0.06 / −0.03 / 0.00 / +0.04 vs g_base) to **−4.0% / 0.0% / 3.0% / 6.0% / 10.0%**: the bull start equals the Q2 2026 revenue print, and the super-bull start (10.0%) requires a genuine cycle upturn plus acquisition contribution. Probabilities were skewed down (15/30/30/20/5 vs the 10/25/30/25/10 defaults) because OE is falling, ROIC is compressing, and the $210 take-private proposal caps the standalone upside case for public holders. OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Base = TTM $8.56/share (--ttm). Price $212.42.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -4.0% | 0.75 | Vehicle cycle downturn; GPUs keep compressing; levered OE falls fast | $40.14 | 4.68% |
| Bear | 30% | 0.0% | 0.90 | Flat revenue, continued OE normalization from pandemic-era levels | $56.95 | 5.77% |
| Base | 30% | 3.0% | 1.00 | Low-single-digit growth; service & parts offsets vehicle-margin drift | $71.71 | 6.74% |
| Bull | 20% | 6.0% | 1.10 | Q2 2026 revenue pace holds; truck cycle (Class 8 orders +170%) delivers | $89.34 | 7.89% |
| Super bull | 5% | 10.0% | 1.25 | Full cycle upturn plus accretive acquisitions at recent pace | $119.76 | 9.80% |

- **Probability-weighted: IV@15% $68.47 (−67.8% vs price), IV@12% $90.21, IV@10% $114.38, weighted IRR 6.55%, base-case IRR 6.74%**
- **Tier by numbers: D.** Bear tier D (5.77%), bull tier D (7.89%) — the whole band is D. Diagnostics (key_numbers.md): OE yield 4.03%, terminal value 17.9% of IV@15%, scenario spread 2.98x, net debt 3.71x normalized OE, 9.5 months since FY end.
- **Hurdle-clearing prices (weighted path): 15% at $68.47 · 20% at $48.83 · 25% at $37.93.**

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 10 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted leg-by-leg above, and the final run used --ttm.
- **BUYBACK_TAILWIND** (share count shrinking 3.8%/yr; key_numbers.md: share count CAGR −3.82%, growth adj 3.82%): already credited via the growth adjustment in the blend; not double-counted in the verdict. Note the shrinkage is partly Penske Corporation's control position dynamics and modest open-market buybacks alongside a rising dividend — it flatters per-share growth regardless of source, hence the downward recalibration of scenario starts.
- **HIGH_NET_DEBT** (net debt 3.71x normalized OE): balance sheet from the filing (financials_history.csv, FY2025): total debt $2,165,500,000 (current $355,000,000 + long-term $1,810,500,000), cash $64,700,000 → net debt $2,100,800,000, plus operating lease liabilities $2,563,000,000 not in the engine's net-debt figure, and floor-plan/inventory financing inherent to dealership operations sits in current liabilities ($12,016,800,000 total liabilities vs $17,597,700,000 assets; equity $5,562,400,000). This is normal leverage for a dealer group and Q2 saw $141M of long-term debt reduction, but against a falling OE base it is why the bear cases carry 45% combined probability and the super-bear OE multiplier is 0.75 — levered OE can vanish fast in a vehicle downturn.
- Preliminary-run flags that do not appear in the final run, for the record: WIDE_SCENARIO_SPREAD (4.50x on default starts) and TIER_BAND (bear D vs bull C) both disappeared after the growth recalibration — the final spread is 2.98x and every scenario tier is D, so there is no band to size to.

## My thoughts / overlay
- The honest headline is the method range: on the engine's normalized median base ($10.76/share) with default scenario starts, the preliminary run gave a weighted IRR of 9.13% and IV@15% of $109.27 — still Tier D. On the TTM base with recalibrated growth, 6.55% and $68.47 — Tier D. Every defensible method lands in D; the disagreement is only about how far below the price the value sits.
- The $212.42 price is not the market mispricing standalone cash flows — it is pinned to the $210 Penske Corporation / Mitsui take-private proposal now before a special committee. A buyer at this price is buying deal completion at ~$210 (i.e. roughly flat to the proposal), not a 15% owner's-earnings return. If the proposal fails or is withdrawn, the standalone DCF range ($68–$110 across methods) is the gravity below.
- Quality is real but cyclical: OE positive 5/5 years, service & parts is a genuine recurring anchor (59.5% gross margin in Q2 2026), the dividend has risen 23 straight quarters, and ROIC at 12.4% still clears the cost of capital. The problem is purely price versus a falling OE base: TTM OE/share $8.56 is a 4.03% OE yield at $212.42.
- What would change the verdict: a completed take-private above $210 (a deal outcome, not a DCF outcome), or a sustained OE recovery back toward the 2022–24 range ($12–15/share) — neither is in the current prints.

## Final verdict
- **Final tier: D** (weighted IRR 6.55% on the final TTM-base inputs; bear 5.77% → bull 7.89%, super-bull only 9.80%)
- Confidence: **Medium** (high on the filing-derived OE base and the direction of ROIC/OE; the take-private process is a binary overlay no DCF can price)
- One-liner: Solid franchised dealer group, moat 5/10 — does not clear 15% on current TTM numbers (6.5% weighted IRR, IV@15% $68.47 vs $212.42 price; hurdle price for 15% is $68.47); the price sits at the $210 Penske Corp/Mitsui take-private proposal, i.e. it is a control/deal price, not standalone owner's-earnings value.
