# Corpay, Inc. (CPAY) — Owner's Earnings DCF

**Price:** $393.02 · **Market cap (engine est.):** $27,927,215,160 · **Sector:** Business payments / transaction processing (formerly FLEETCOR, rebranded 2024)

## What it is

Corpay runs B2B payment infrastructure in three segments: **Vehicle Payments** (fuel cards, tolls, parking, fleet maintenance controls), **Corporate Payments** (AP automation, virtual cards, cross-border payments/FX), and **Lodging Payments** (workforce housing, airline crew, insurance displacement). Revenue is recurring transaction/service fees on spend volume. Q2 2026 (search results): revenue $1.34B, +21.5% YoY reported and +10% organic; Corporate Payments revenue +42% reported; management raised FY2026 guidance to ~$5.31B revenue and $27.35 adjusted EPS at the midpoint. Portfolio is being simplified — PayByPhone was sold in March 2026 and the UK epyx/r2c vehicle-payments units are being divested, with proceeds earmarked for buybacks.

## Owner's earnings

- **Conservative definition (OCF − capex − SBC), FY2025:** $1,196,508,000 total, $16.8385/share.
- **Maintenance definition (NI + D&A − min(capex, D&A) − ΔNWC), FY2025:** $1,842,697,000 — materially higher because FY2025 OCF was depressed by working-capital/float timing (see NI_OCF_DIVERGENCE below), while the maintenance version starts from net income.
- **Base used: TTM OE/share of $22.6108** (ttm.py, `--ttm` pin), vs the engine's 3-yr median normalized base of $22.9466/share. The two independent bases agree within ~1.5%, which is the main comfort given the OCF volatility below.

TTM inputs quoted from ttm.json (FY = 2025-01-01→2025-12-31; prior YTD = H1 2025; current YTD = H1 2026):

| Leg | FY | Prior YTD | Current YTD | TTM |
|---|---|---|---|---|
| OCF | 1,499,901,000 | 1,066,096,000 | 1,413,479,000 | 1,847,284,000 |
| Capex | 200,756,000 | 97,407,000 | 105,529,000 | 208,878,000 |
| SBC | 102,637,000 | 47,234,000 | 59,509,000 | 114,912,000 |
| Diluted shares | 71,058,000 | 71,494,000 | 67,379,000 | 67,379,000 (current YTD basis) |

TTM OE total: $1,523,494,000 → $22.6108/share. SBC is a real but modest cost (~$115M TTM vs ~$1.85B TTM OCF); capex is light (asset-light payments model), so the conservative and maintenance definitions differ mainly through OCF timing, not capex judgment.

## MOAT — 6/10 (CAP 9.8 years)

**FOR:**
- Embedded workflows: AP automation, fleet controls and lodging booking sit inside customers' operating processes — ripping them out means re-plumbing payables/fleet policy, not just swapping a card (customer retention ~93% per Q2 2026 reporting).
- Acceptance/network scale in fleet payments and a cross-border platform (Mastercard partnership, bank-channel pipeline) that sub-scale rivals can't cheaply replicate.
- Cross-sell across three segments on one platform (fleet + commercial card + AP), plus a large stated addressable market (~$600B per management).
- Proven through-cycle economics: OE positive 5/5 of the last 5 years, revenue CAGR 13.6% over 5 years.

**AGAINST:**
- Yield compression on mix shift: Corporate Payments revenue per spend dollar fell from 0.70% to 0.58% as larger enterprise clients (lower yield) mix in — scale is bought with price.
- Credible attackers on every flank: fintech AP/expense platforms (Ramp/Brex-class), bank-owned processors, and the card networks selling direct B2B payment products.
- Vehicle Payments is tied to fuel/fleet volumes — long-run EV transition shrinks the fuel-card use case.
- Regulatory overhang is real, not theoretical: Q2 2026 GAAP net income absorbed a $100M charge for a preliminary FTC Bureau of Consumer Protection settlement (search results), a legacy of the FLEETCOR-era fee-practice scrutiny.
- Leverage (see HIGH_NET_DEBT) means the equity story depends on continued capital-market access and disciplined buybacks.

Net: a genuine but narrow-to-moderate moat — switching costs and scale are real, but pricing power is visibly eroding at the enterprise end and the fastest-growing segment (Corporate Payments) is also the most contested. 6/10.

## Five scenarios (base OE $22.6108/sh, TTM; g_base 14.27%)

Growth sanity check: engine blended growth 14.27% (rev CAGR 5y 13.65%, 3y 9.73%, latest YoY 13.93%, OE/share CAGR 2y −17.28% off the volatile OCF years, +2.58pp buyback adjustment). Recent prints: FY2025 revenue +13.9%, Q2 2026 +21.5% reported / +10% organic, FY2026 revenue guided to ~+17% reported. Bull (19.3%) and super-bull (26.3%) starts sit above organic growth but below reported growth and in line with the acquisition-plus-buyback trajectory — no start is below what the company just printed, so no recalibration was needed. Default probabilities/offsets/multipliers kept: leverage and OCF volatility argue against skewing bullish; guided momentum argues against skewing bearish.

| Scenario | Prob | Growth start | OE mult | Story | IV@15% | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 2.3% | 0.75 | Credit losses bite, yield compression accelerates, leverage forces a buyback halt | $137.65 | 6.9% |
| Bear | 25% | 9.3% | 0.90 | Organic growth fades to high-single digits; float/WC stays a headwind | $225.54 | 9.9% |
| Base | 30% | 14.3% | 1.00 | Guided trajectory: double-digit organic growth + buybacks, gradual deleveraging | $312.79 | 12.7% |
| Bull | 25% | 19.3% | 1.10 | Corporate Payments compounds, cross-border scales, divestiture proceeds shrink the share count | $428.94 | 16.0% |
| Super bull | 10% | 26.3% | 1.25 | Full platform story: spend-management attach + sustained 20%+ OE/share growth | $661.78 | 21.3% |

**Weighted result:** IV@15% **$337.40**, IV@12% $462.69, **weighted IRR 13.45%** → **Tier C**. Price $393.02 is above the weighted IV@15% (upside_at_15 −14.2%). Diagnostics: OE yield 5.75%, terminal-value share at 15% 22.1%, scenario spread 4.8×, net debt 6.8× normalized OE.

## FLAGS — resolutions

- **STALE_FY** (FY ended 9.5 months ago): Resolved with ttm.py — base pinned to TTM OE/share $22.6108 from H1 2026 10-Q YTD math (inputs quoted above). TTM base is within ~1.5% of the 3-yr median ($22.9466), so staleness is not distorting the verdict.
- **BUYBACK_TAILWIND**: Share count shrinking 2.6%/yr, already credited via the +2.58pp growth adjustment. Confirmed live in the TTM legs: diluted shares fell from 71,058,000 (FY2025) to 67,379,000 (H1 2026 YTD). Caveat: buybacks are partly debt-funded — see HIGH_NET_DEBT.
- **OE_VOLATILE**: OE/share range >3× over 5 years is an OCF-timing artifact, not business cyclicality of that magnitude: conservative OE was $481,953,000 in 2022 vs $1,831,224,000 in 2023 (financials_history.csv), tracking OCF swings ($754,797,000 → $2,101,132,000) while revenue grew smoothly ($3,427,129,000 → $3,757,719,000). The normalized/TTM base smooths this; bear + super-bear carry a combined 35% weight as the widening the flag asks for.
- **NI_OCF_DIVERGENCE (2023, 2024)**: OCF $2,101,132,000 vs NI $981,890,000 in 2023; OCF $1,940,565,000 vs NI $1,003,746,000 in 2024. D&A ($336,604,000 / $351,088,000) and SBC ($116,086,000 / $116,724,000) explain part of the gap; the engine's ΔNWC is small ($54,023,000 in 2023, $188,707,000 in 2024), so the remainder sits in operating items the computed outputs don't break out (customer-funds/float and other operating asset/liability swings typical of a payments balance sheet) — I am not hand-computing a figure the outputs don't provide. The 2022 mirror image (OCF $754,797,000 < NI $954,327,000) confirms timing, not one-directional inflation. Resolution: trust the cross-check — TTM base $22.6108 vs median $22.9466 agree closely despite being built from different windows.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.8× super-bear): Genuine uncertainty (leverage × yield compression × OCF noise). Confidence capped at medium; verdict sized to the conservative end.
- **HIGH_NET_DEBT**: Engine net debt $10,939,120,000 = 6.8× normalized OE. That multiple overstates fragility vs. the company's own frame (2.55× leverage on adjusted EBITDA at Q2 2026 per search results, debt stack refinanced, revolver expanded to $3.7B), because OE is after capex/SBC and the engine counts gross balance-sheet debt against cash only. Still: the equity is levered, bear cases carry 0.75/0.90 OE multipliers, and this is a stated reason the verdict demands a margin of safety rather than treating $337 as a buy price.

## Thoughts / overlay

Method range: on the median base instead of TTM the preliminary run gave weighted IRR 13.11% — same tier. The defensible range is narrow (C either way); what moves this stock a tier is price, not method. The Q2 2026 $100M FTC charge is a GAAP-NI one-off (preliminary settlement) — it doesn't change OCF-based OE materially today, but it's a reminder the legacy fee model carries regulatory tail risk. Divestitures (PayByPhone closed Mar 2026; epyx pending) are small basis changes, not a BASIS_BREAK — segment mix shifts toward Corporate Payments, which the growth blend already reflects.

**Hurdle math:** the price that clears 15% on the weighted path is the weighted IV@15% itself, **$337.40**. Given 6.8× net-debt/OE and the 4.8× scenario spread, a margin of safety puts an interesting entry nearer **$285–305**. At $393.02 the market is pricing something between base and bull as the central case.

## Verdict

**Tier C — weighted IRR 13.45%, IV@15% $337.40 vs price $393.02.** A good business (moat 6/10, real buyback tailwind, guided double-digit organic growth) at a price that already pays for the good outcome. Below the 15% hurdle; revisit under ~$305.
