# KR — The Kroger Co.
v5 run, 2026-10-14 (supersedes the v4 run of 2026-10-13, which also landed Tier D on the same TTM base). In scope: engine market cap $39.791B at $60.75 (nasdaq_quote_api) — just under the $40B line on the fiscal-year share count.

All figures below are copied from dcf_numbers.json, ttm.py output (ttm.json), or financials_history.csv — none are recomputed.

## What it is
The largest pure-play US supermarket operator: ~$147.6B revenue (FY ended 2026-01-31), grocery stores under Kroger, Ralphs, Fry's, King Soopers and other banners, plus pharmacies, fuel centers, the Our Brands private-label portfolio, e-commerce (>$16B sales in fiscal 2025, +20% in Q2 fiscal 2026), and alternative profit businesses (Kroger Precision Marketing retail media, personal finance, data) that delivered $1.5B of operating profit in fiscal 2025. The Albertsons merger is dead; the two are litigating the termination fee. This is a defensive, low-margin volume business — net income has run at roughly 1–2% of revenue across the filed history.

## Owner's earnings
**Latest FY (ended 2026-01-31, from financials_history.csv):** operating cash flow $7,311M; capex $3,855M (tag: PaymentsToAcquireProductiveAssets); SBC $157M (tag: ShareBasedCompensation — trivially small for this business, ~2% of OCF; dilution is not Kroger's problem, buybacks are the story).
- **Conservative owner's earnings latest FY: $3,299M = $5.04/share** (latest-FY OE/share in dcf_numbers.json).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $2,065M — LOWER than the conservative figure this year, and the reason is instructive: fiscal 2025 net income ($1,016M) carries the $2,497M non-cash automated-fulfillment-network impairment (see NI_OCF_DIVERGENCE below), which the maintenance formula does not add back, while the OCF-based conservative figure is unaffected. The conservative definition is the cleaner one for Kroger this year.
- OE positive 5 of the last 5 fiscal years, but volatile in level: conservative OE totals of $3,373M / $1,230M / $2,712M / $1,602M / $3,299M across FY2022–FY2026 in the filed history. Capex runs persistently above D&A (FY2026 capex $3,855M vs D&A $3,332M), so this screen's all-capex-is-a-cost stance bites Kroger harder than it bites asset-light names — some of that capex is growth (new stores, store-based fulfillment after the Ocado exit), which is the main reason the method range below matters.
- Net debt $12,541M (dcf_numbers.json) — see HIGH_NET_DEBT. This excludes operating-lease liabilities, which for a grocer are material on top of it.

**Base used = TTM owner's earnings through Q2 fiscal 2026 (period ended 2026-08-15), from ttm.py — no hand math:**
- OCF: FY $7,311M − prior YTD $3,688M + current YTD $3,085M = **TTM $6,708M**
- Capex: FY $3,855M − prior YTD $1,968M + current YTD $2,437M = **TTM $4,324M**
- SBC: FY $157M − prior YTD $83M + current YTD $101M = **TTM $175M**
- Shares (current-YTD weighted diluted): **612,000,000**
- **TTM OE total $2,209M → base OE/share $3.61** (base_source: ttm_json)
- The engine's normalized base (median of last 3 FY OE/share) is $3.74/share — close to the TTM figure, which raises confidence in the base. The latest-FY $5.04/share was rejected as the base: its OCF was flattered by working-capital timing, and TTM capex has stepped up (current-year capex guidance is $3.8–4.0B against the $3,855M filed for last FY, and the TTM build annualizes the heavier H1 spend). TTM $3.61 is the freshest and the most conservative of the three candidate bases.

## Moat: 5/10 — moderate / narrow
Justification: genuine scale, loyalty data, private label and a growing retail-media profit pool — but the product is a commodity, customer switching costs are near zero, and Kroger is currently LOSING share to Walmart, Costco and Amazon (Numerator, 12 months ended June 30, 2026). Pricing power is pass-through of food inflation, not rent extraction.
- FOR: #2 US grocer with ~$147.6B revenue and dense local store networks (fresh, pharmacy, fuel) that are hard to replicate market by market
- FOR: loyalty program data driving personalization and Kroger Precision Marketing — retail-media profit +24% in Q2 fiscal 2026; alternative profit businesses delivered $1.5B operating profit in fiscal 2025
- FOR: Our Brands private label — high-margin, expanding (900+ new items launched in fiscal 2025), benefits directly from value-seeking shoppers
- FOR: e-commerce scale (>$16B fiscal 2025 sales, +20% growth) now pivoting to store-based fulfillment after the Ocado write-down
- AGAINST: Walmart's structural cost/scale advantage (~23.6% US grocery share) and Amazon/Costco taking the share Kroger is losing
- AGAINST: near-zero switching costs — shoppers multi-home across grocers, warehouse clubs and discounters (Aldi at 2,600+ US stores)
- AGAINST: structurally thin margins (~1–2% net) leave no buffer against shrink, labor (largely unionized) and price investment
- AGAINST: food-at-home disinflation removes the inflation pass-through that flattered nominal growth in 2021–23
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Growth inputs: the engine's blend is 1.27% (rev CAGR 5y 2.19%, rev CAGR 3y −0.14%, latest rev YoY +0.35%, OE/share CAGR 2y 16.10%) plus the +3.41pp buyback adjustment = g_base 4.68%. Sanity check against actual prints: Q2 fiscal 2026 identical sales ex fuel +0.2%; full-year identical-sales guidance was CUT to 0.2–0.8% (from 1–2%), while adjusted EPS guidance was held at $5.10–$5.30 vs $4.85 adjusted in fiscal 2025 — i.e., management's own EPS growth is mid-to-high single digits and is buyback/mix-driven, not sales-driven. The base start of 4.68% is consistent with that. Two adjustments, with reasons:
- **Bull/super-bull offsets trimmed** (+5/+12pp → +4/+9pp): the default super-bull start of 16.7% exceeds every current print and the top of EPS guidance; its only support is the 16.10% OE/share CAGR, which is an artifact of compounding off the depressed FY2025 OE base ($1,602M). Grocery OE/share growth is buyback-plus-mix arithmetic, and 13.7% is already generous for it.
- **Probabilities skewed defensive** (10/30/35/20/5 vs default 10/25/30/25/10): identical-sales guidance cut, measured share loss, 5.3x net debt to normalized OE, and TTM capex running above the last fiscal year.
OE multipliers left at defaults 0.75/0.90/1.00/1.10/1.25. Price $60.75.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | −7.3% | 0.75 | Price war with Walmart/Aldi; shrink and labor squeeze the thin margin | $14.71 | 5.20% |
| Bear | 30% | −0.3% | 0.90 | Identical sales stall at the low end of guidance; capex stays heavy | $23.68 | 7.26% |
| Base | 35% | 4.7% | 1.00 | EPS-guide path: flat sales, buybacks + media/private-label mix carry OE/share | $32.40 | 9.25% |
| Bull | 20% | 8.7% | 1.10 | Identical sales recover toward 2%; e-commerce turns profitable per the strategic review | $42.06 | 11.33% |
| Super bull | 5% | 13.7% | 1.25 | Share stabilization plus alternative profits compounding at media rates | $58.68 | 14.62% |

- **Probability-weighted: IV@15% $31.26 (−48.5% vs price), IV@12% $41.38, IV@10% $52.65, weighted IRR 9.02%, base-case IRR 9.25%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 5.94%, terminal value 18.4% of IV@15%, scenario spread 3.99x, net debt 5.30x normalized OE, 8.4 months since FY end.
- The starkest line in the table: **even the super-bull scenario does not clear 15% at $60.75** (IRR 14.62%, IV@15 $58.68 — below the price). At this price the market is paying for the bull case as the base case.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 8.4 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 fiscal 2026 (inputs quoted above), passed to the final run via --ttm.
- **BUYBACK_TAILWIND** (share count shrinking 3.4%/yr): real and already credited via the +3.41pp growth adjustment — not double-counted in the verdict. Kroger completed a $7.5B repurchase authorization in fiscal 2025 (including a $5B accelerated share repurchase) and the board approved a further $2B; diluted shares fell from 725M (FY2024) to 655M (latest FY) to 612M (current YTD). Note the corollary: per-share growth is doing heavy lifting while total OE is flat-to-down (TTM OE total $2,209M vs $3,299M in the latest FY).
- **NI_OCF_DIVERGENCE** (2024, 2026): both years identified. FY2026 (ended 2026-01-31): the $2,497M fulfillment-network impairment and related charges in the fiscal 2025 cash-flow statement — non-cash, crushes net income ($1,016M) without touching OCF ($7,311M). FY2024 (ended 2024-02-03): the $1.4B charge for the nationwide opioid settlement framework recorded in Q2 of that fiscal year, payable over 11 years — again an NI hit well ahead of the cash. Both are one-offs against NI, not OCF, so the OCF-based conservative OE used throughout is not contaminated by them; if anything the maintenance definition is the distorted one this year (see Owner's earnings).
- **HIGH_NET_DEBT** (net debt 5.30x normalized OE in the final run): folded into the verdict. Net debt is $12,541M, and the engine's figure excludes operating leases, so true fixed obligations are higher. OE here is levered equity cash flow (OCF is after interest), so the DCF is internally consistent — but with margins at 1–2% of sales, a modest sales or gross-margin shock compresses equity OE fast. This is a core reason for the 30% bear weight and for sizing the verdict to the conservative end.
- **WIDE_SCENARIO_SPREAD** (preliminary run, 4.51x): the trimmed bull offsets and defensive probabilities narrowed the final spread to 3.99x — still wide for a grocer, reflecting genuine OE volatility in the filed history (FY totals above). Confidence is set to medium, not high.

## My thoughts / overlay
- Method range: the preliminary run (median base $3.74, default probabilities/offsets) gave weighted IRR 10.05%, Tier C, IV@15% $35.96. The final run (TTM base $3.61, defensive skew, trimmed bull offsets) gives 9.02%, Tier D, and the superseded v4 run (2026-10-13, same TTM base via --base-oe-ps, moat 4) also landed Tier D. The honest range is **C–D — and both ends are far below the 15% hurdle**. Unlike APP, there is no defensible input set found here that gets Kroger near 15% at $60.75: the super-bull scenario itself doesn't clear it.
- Quality is not the issue: Kroger is a durable, defensive cash generator with a real (if narrow) moat, tiny SBC, disciplined buybacks and a growing high-margin media/data profit pool. The issue is purely price versus this screen's OE math: TTM capex of $4,324M against OCF of $6,708M leaves a 5.94% OE yield, and low-single-digit underlying growth cannot compound that into 15% from $60.75.
- The main way this screen could be too harsh: it charges ALL capex against OE. Kroger guides capex of $3.8–4.0B while D&A runs ~$3.3B; if a meaningful slice is genuinely growth capex (new stores, fulfillment re-platforming), a maintenance-capex view would lift OE — but the maintenance definition printed $2,065M for the latest FY (impairment-distorted, see above), so the filings do not currently support a kinder base. The October 20, 2026 investor update (longer-term targets) is the next catalyst that could change the growth inputs.
- Hurdle math: the weighted IV@15% is $31.26 — Kroger clears Andrew's 15% hurdle only at roughly half the current price, and a margin of safety against the bear cases ($23.68 IV@15) argues for lower still. At ~$31 the buyer would also be getting the dividend and buyback yield of a defensive staple at a distressed multiple; nothing about the current $60.75 price offers that.

## Final verdict
- **Final tier: D** (weighted IRR 9.02% on the v5 final inputs; method range C–D, no tier override — the range is disclosed, and the verdict is sized to the conservative end per the spread)
- Confidence: **Medium** (high on the base — TTM and median agree within ~4%; medium on growth, which is buyback arithmetic more than business growth)
- One-liner: Durable #2 US grocer, narrow moat 5/10, tiny SBC and heavy buybacks — but at $60.75 the weighted IRR is 9.0% and even the super-bull case misses 15%; it only clears the hurdle near $31.
