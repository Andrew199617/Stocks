# AA — Alcoa Corp
Engine 5.4.0 run, 2026-10-18. Price $41.45 (nasdaq_quote_api), market cap $10.818B, in scope under $40B. All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv or fundamentals.json — none are recomputed.

## What it is
Pure-play upstream aluminum: bauxite mining, alumina refining and primary aluminum smelting, fully integrated since the August 1, 2024 all-stock acquisition of Alumina Limited ended the AWAC joint venture (Alcoa previously held 60%; Alumina holders received 0.02854 Alcoa shares per share, ~$2.8B implied equity value). Two segments: Alumina and Aluminum. Earnings are the LME aluminum price and the alumina index minus energy-heavy conversion costs — Q2 2026 showed the split in one quarter: record revenue of $3.97B and adjusted EBITDA $901M, with Aluminum segment EBITDA $1.07B while Alumina swung to a $96M EBITDA loss on Pinjarra refinery disruptions in Western Australia (2026 alumina production guidance cut to 9.5–9.6 Mt).

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,185,000,000; capex $618,000,000; SBC $41,000,000 (always a real cost, and here genuinely small).
- **Conservative owner's earnings FY2025: $526,000,000 = $2.02/share** (base_oe_latest_per_share in dcf_numbers.json).
- Maintenance version FY2025 (NI + D&A − min(capex, D&A) − ΔNWC, from financials_history.csv): $1,472,000,000 — rejected as the cleaner figure: FY2025 net income of $1,157,000,000 includes the ~$786M gain on the July 1, 2025 sale of the 25.1% Ma'aden joint venture (consideration $1,350M: Ma'aden shares valued $1,200M plus $150M cash) and a $267M mark-to-market gain on those Ma'aden shares, neither of which is operating cash generation. The OCF-based conservative figure is the clean one.
- OE positive 4 of the last 5 fiscal years. Net debt $851,000,000 (basis: LongTermDebtNoncurrent + LongTermDebtAndCapitalLeaseObligationsCurrent + ShortTermBorrowings), plus lease liabilities $308,000,000 — modest against the filed balance sheet today, but see the South32 deal under Thoughts: the leverage picture is about to change.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,185,000,000 − prior YTD $563,000,000 + current YTD $429,000,000 = **TTM $1,051,000,000**
- Capex: FY $618,000,000 − prior YTD $224,000,000 + current YTD $305,000,000 = **TTM $699,000,000**
- SBC: FY $41,000,000 − prior YTD $23,000,000 + current YTD $30,000,000 = **TTM $48,000,000**
- Shares (current-YTD weighted diluted): **266,000,000**
- **TTM OE total $304,000,000 → base OE/share $1.14** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $0.03/share — rejected as the base: it is the median of a trough year (FY2023 OE/share −$2.67), a near-zero year (FY2024 $0.03) and the FY2025 recovery ($2.02), so it prices Alcoa as if the trough were the normal year. It is still reported in dcf_numbers.json and drives the method range under Thoughts. The TTM base is itself conservative in one respect: TTM capex of $699M runs above FY2025's $618M and above D&A, reflecting the Australian mine-relocation and residue-storage capital program.

## Moat: 3/10 — weak
Justification: a vertically integrated, scaled upstream producer, but a pure commodity price-taker. Evidence first: fundamentals.json carries **no roic_proxy series and no gross-margin series** — operating income and COGS are not tagged in the companyfacts extraction, so both print null for every fiscal year; there is no filing-direct ROIC history to quote. The return series that is printed, ROE, swings from −15.3% (2023) to +1.2% (2024) to +18.9% (2025), and was negative in 2022 (−2.4%) as well — returns through the cycle do not sit above the cost of capital, so no moat above the weak band is defensible.
- FOR: vertically integrated bauxite → alumina → aluminum chain with full AWAC control since Aug 2024; scale as one of the world's largest bauxite and alumina producers with long-life Western Australian bauxite; low-carbon product line positioned for carbon-border premiums; smelter portfolio selling into structurally short North American / European markets.
- AGAINST: commodity price-taker — the LME price and alumina index set earnings, not Alcoa; ROE history above shows no durable through-cycle return; energy is a bought, market-priced input and Canadian metal carries tariff exposure; alumina sits in surplus into 2026–27 with Chinese supply capping upside; the pending South32 upstream acquisition adds debt and shares before its synergies are proven.
- A 3 gives CAP = 5.9 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 5.9 years, 15-year projection.

## DCF — final run (2026-10-18)
Probabilities skewed to the bear side of the 10/25/30/25/10 defaults (15/30/25/20/10) per the OE_VOLATILE flag — this is a cyclical at a strong point in its price cycle. Offsets and multipliers are the defaults (−12/−5/0/+5/+12pp; 0.75/0.90/1.00/1.10/1.25). Growth-start sanity check: the base start of 1.68% sits below the recent revenue prints (latest FY revenue YoY +7.87%, TTM revenue YoY +6.46% in fundamentals.json, and Q2 2026 revenue +31% YoY) for two written reasons: (1) the blend's revenue components already carry the engine's −5pp share-count adjustment for the Alumina Ltd issuance, and (2) the recent prints are aluminum-price prints (LME near $3,150–3,200/t vs ~$2,600/t a year earlier), not volume or OE growth that a 15-year fade can extrapolate. The bull start of 6.68% matches the FY/TTM revenue prints; the super-bull start of 13.68% sits well below Q2's price-spike quarter, which is a price level, not a growth rate.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −10.0% | 0.75 | Aluminum price gives back the 2025–26 run; alumina surplus deepens | $4.49 | 3.72% |
| Bear | 30% | −3.3% | 0.90 | Price normalizes toward mid-cycle; Pinjarra / tariff costs stick | $6.86 | 4.48% |
| Base | 25% | 1.7% | 1.00 | TTM cash generation persists with low nominal growth | $9.11 | 5.23% |
| Bull | 20% | 6.7% | 1.10 | Tight supply outside China holds prices; restarts deliver | $11.92 | 6.17% |
| Super bull | 10% | 13.7% | 1.25 | Structural deficit pricing plus South32 synergies land | $17.17 | 7.91% |

- **Probability-weighted: IV@15% $9.11 (−78.0% vs price), IV@12% $11.99, IV@10% $15.20, IV@20% $6.50, IV@25% $5.05, weighted IRR 5.25%, base-case IRR 5.23%**
- **Tier by numbers: D.** Bear and bull cases are also Tier D — there is no tier band to size to; every scenario sits far below the price. Diagnostics (dcf_numbers.json): OE yield 2.76%, terminal value 17.9% of IV@15%, scenario spread 3.83x, net debt 2.85x normalized OE, 9.6 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.6 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above.
- **BASE_DIVERGENCE** (latest FY $2.02 vs 3-yr median $0.03): the median is the distorted one — it medians a trough year, a near-zero year and a recovery year (see Owner's earnings). TTM base used; the median is retained in the method range below.
- **OE_VOLATILE** (OE/share spans >3x over 5 years): real cyclicality, not an artifact — OE/share ran $2.58 / $1.67 / −$2.67 / $0.03 / $2.02 over FY2021–25. Handled by the TTM base plus bear-skewed probabilities (45% on bear-or-worse).
- **DILUTION** (share count +13.0%/yr): resolved — this is not SBC creep. SBC is $35–48M/yr, immaterial against OCF. The count stepped from 178M (FY2023) to 214M (FY2024) to 261M (FY2025) because of the all-stock Alumina Limited acquisition of August 1, 2024 (Alumina holders took ~31% of the combined company); the FY2024 weighted count is part-year, FY2025 is the first full year. The engine's −5pp growth adjustment therefore over-penalizes forward growth — noted, and it is one reason the verdict does not lean on the blend beyond the written sanity check above. A second, smaller step is already announced: the South32 deal includes ~17M new Alcoa shares (~$1.0B of the consideration, per deal reporting).
- **NI_OCF_DIVERGENCE** (2023): FY2023 net income −$651,000,000 vs OCF +$91,000,000. The gap is mostly non-cash: D&A alone was $632,000,000 in FY2023 (financials_history.csv), and the year carried the Kwinana refinery's ~$130M pre-tax loss ahead of its January 2024 curtailment decision. The OCF-based conservative OE used throughout is not contaminated by the non-cash charges; FY2023 OE was still genuinely negative (−$475,000,000) on weak prices and costs — a trough, not an accounting illusion.
- Preliminary-run flags that disappeared on the TTM base and are recorded here so they are not lost: **IRR_AT_FLOOR, LOW_OE_YIELD, HIGH_NET_DEBT (116.3x) and WIDE_SCENARIO_SPREAD** were all artifacts of the $0.03 median base in the preliminary run (weighted IV@15% $0.24, weighted IRR 2.57% at the floor). On the TTM base the IRR solves cleanly at 5.25% and net debt is $851M against a real cash-generating business — but the leverage warning returns in forward form via the South32 financing, below.

## My thoughts / overlay
- The honest headline is the method range, and it is wide: the preliminary median-base run printed weighted IV@15% $0.24 and a floored IRR of 2.57%; the TTM base prints $9.11 and 5.25%; the latest-FY base ($2.02/share) would print higher still. Every one of those is a defensible base for a cyclical at a different point of the cycle — and every one is far below the $41.45 price. The conclusion (Tier D, does not clear 15%) is robust to the base choice even though no single number is.
- What the price is actually paying for: spot aluminum. Q2 2026 adjusted EPS was $2.12 in a single quarter on LME prices near their highs; annualize a peak quarter and the stock looks cheap, run the filed TTM owner's earnings ($1.14/share after $699M of capex) and it does not. The DCF's job here is to refuse the annualization.
- Balance-sheet event after the TTM period: the agreed acquisition of South32's upstream (AliGroup) assets — ~$4.1B headline, ~$3.1B cash, ~17M new shares, ~$750M assumed debt/leases, up to ~$750M contingent, with $2.6B of senior notes already issued in September 2026 and a claimed ~$900M NPV of synergies; completion expected H1 of South32's FY2027. Pro forma leverage steps up materially from today's $851M net debt. None of that is in the base; it is a reason the bear weight is heavy, not a reason to raise the base.
- Operations watch items: Pinjarra stabilization (alumina guidance already cut once), San Ciprián restart cash burn into 2027, Section 232 tariff cost on Canadian metal (partly offset by Midwest premiums), and the Massena / idled-site asset sales.

## Final verdict
- **Final tier: D** (weighted IRR 5.25% on the TTM base; Tier D under the median and TTM bases alike, and in every scenario including super bull at 7.91%)
- Confidence: **Low** (the base itself is the argument for a cyclical — but the tier conclusion survives every base tried)
- One-liner: Cyclical commodity price-taker, moat 3/10 — on the current TTM base it does not clear 15% (weighted IRR 5.25%, weighted IV@15% $9.11 vs $41.45 price); it would need a price near $9.11 to clear the 15% hurdle on these cash flows.
