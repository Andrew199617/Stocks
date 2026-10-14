# CBOE — Cboe Global Markets, Inc.
First-pass run, 2026-10-13 (engine v4). In scope: market cap ~$30.7B (< $40B).

## What it is
The largest US options exchange operator. Core franchises: proprietary index options (SPX and VIX options are listed only on Cboe), multi-listed options (~30% industry share), North American equities, futures, global FX, the Cboe Clear Europe central counterparty, and Data Vantage (access, capacity and market-data fees — the recurring-revenue layer). Asset-light, ~72% adjusted EBITDA margin (Q2 2026). Earnings are volume-driven: FY2025 was a record year (net revenue $2.4B, +17%; Q4 net revenue +28%), and 2026 is running hotter — Q2 2026 net revenue $731.6M (+25% YoY), adjusted EPS $3.56 (+45%), options net revenue a record $473.9M on ADV +26%. Management raised 2026 organic net revenue growth guidance twice, from mid-single-digit at the FY25 print to mid-to-high teens after Q2 2026.

## Owner's earnings — the headline numbers are float, not earnings
Raw engine output (SEC EDGAR): FY2025 OCF $1,752.6M − capex $71.0M − SBC $50.4M = **conservative OE $1,631.2M = $15.52/share**; maintenance version (NI + D&A − min(capex, D&A) − ΔNWC) $1,472.4M = $14.01/share. Both are built on raw OCF, and for Cboe raw OCF is not shareholder cash flow:

- Cboe's cash flow statement runs **Cboe Clear Europe clearing-member balances through operating activities**: the line "restricted cash and customer bank deposits (included in margin deposits, clearing funds, and interoperability funds)" contributed **+$528.5M in FY2025** (+$76.0M FY2024, +$282.6M FY2023). These are participants' segregated deposits with an equal offsetting liability ($1,617.0M at FY25-end) — float, not earnings. The FY2025 10-K MD&A says the OCF-vs-net-income variance is "primarily attributable" to this line. The H1 2026 10-Q is starker: the same line is +$943.2M of H1 OCF.
- **Section 31 fees payable** (SEC pass-through fees collected from members and remitted) swung −$181.8M in FY2025 (+$130.1M FY2024, −$95.2M FY2023) — also not earnings.
- FY2025 NI→OCF bridge, fully explained: NI $1,100.0M + clearing float $528.5M + D&A $122.4M + SBC $50.4M + impairments $46.7M − Section 31 paydown $181.8M − equity earnings on investments $84.2M (non-cash) + small WC = OCF $1,752.6M.

**Float-cleaned shareholder OE** (OCF − clearing line − Section 31 line − capex − SBC, all from the audited statements of cash flows):
- FY2023: $1,075.6 − $282.6 + $95.2 − $45.0 − $41.3 = $801.9M = **$7.55/share**
- FY2024: $1,100.6 − $76.0 − $130.1 − $60.9 − $41.8 = $791.8M = **$7.51/share**
- FY2025: $1,752.6 − $528.5 + $181.8 − $71.0 − $50.4 = $1,284.5M = **$12.22/share**

The FY2025 step-up is real earnings, not float: GAAP EPS $7.25 → $10.47, adjusted EPS ~$8.60 → $10.67, operating income +34% on record index-options volume (0DTE SPX was >61% of SPX volume in Q4 2025). The spread income Cboe earns *on* the float stays in net income — only the balance changes are removed, which is the correct treatment.

**TTM through Q2 2026 (10-Q YTD math):** OCF TTM = $1,752.6 − $1,246.6 (H1'25) + $1,456.8 (H1'26) = $1,962.8M; clearing line TTM = $528.5 − $555.6 + $943.2 = $916.1M; Section 31 TTM = −$181.8 − $56.4 + $155.3 = −$82.9M; clean OCF TTM = $1,962.8 − $916.1 + $82.9 = $1,129.6M; capex TTM = $71.0 − $35.0 + $52.3 = $88.3M (statement line: PPE + data-processing software + leasehold improvements); SBC TTM = $50.4 − $25.7 + $28.5 = $53.2M; **clean OE TTM = $988.1M = $9.41/share**. That TTM figure is mechanically depressed by the June window: H1'26 caught the year-end accrual paydown (AP/accrued −$282.0M in H1 vs +$6.5M across FY2025) and a receivables build on the June volume spike (−$195.7M vs +$79.4M across FY2025), while H1'26 earnings themselves were strong (NI $738.8M, +52% YoY).

**Base used: FY2025 float-cleaned OE of $12.22/share** (passed via `--base-oe-ps`) — the full-annual-cycle figure, current enough that H1 2026 prints sit above it. Price $292.25 = 23.9× this base (18.8× the float-inflated raw figure). OE positive 5 of the last 5 years on every definition.

## Moat score: 7/10 — strong, not wide
FOR — (1) Exclusive proprietary index products: SPX and VIX options trade only on Cboe — a licensing-based monopoly on the highest-RPC flow in US options (index RPC ~$0.91 vs ~$0.07 multi-listed). (2) Liquidity network effects at scale: ~30% options share; liquidity begets liquidity, and the installed market-maker/broker connectivity is sticky. (3) Data Vantage: recurring access/market-data revenue growing to low-teens guidance, high switching friction. (4) Proven economics across cycles: ~20%+ ROE, 72% adj. EBITDA margin, net cash balance sheet. (5) Exchange/CCP licenses are genuine regulatory barriers.
AGAINST — (1) Roughly half the flow (multi-listed options, equities) is fungible across 16 competing options exchanges; share and revenue-per-contract are contested every day — Cboe Japan lost share in 2025 and took a $17.1M intangible impairment, a live demonstration that share can walk. (2) Volumes are volatility-cyclical: calm regimes cut ADV (net revenue grew only ~0–9% across 2023–24). (3) 0DTE mix shift structurally dilutes RPC. (4) Political/regulatory exposure: transaction-tax proposals, market-structure rule changes, and the index exclusivity is contractual, not statutory — CME and others contest the index complex. (5) Customer base is a handful of large market makers with real bargaining power.
A 7 gives CAP = 2 + 1.3×7 = **11.1 years** (growth holds 2 years, then converges to 2.5% terminal over the CAP, 15-yr projection).

## DCF — final v4 run
Base OE $12.22/share (float-cleaned FY2025, above). Growth starts set against actual prints: engine blend was 11.4% (rev CAGRs ~6%, latest gross-revenue YoY +15.1%, OE/share CAGR 29% off the float-distorted series). Recent prints: FY2025 net revenue +17%, H1 2026 gross revenue +14.7% YoY, Q2 2026 net revenue +25%, 2026 guidance raised to mid-to-high teens. Base start kept at the engine's 11.4% — below the current print pace on purpose: the current regime is a high-volatility one and volumes mean-revert; bull/super-bull starts (18.4% / 25.4%) bracket what the company is actually printing now, so no scenario start sits below the latest print without that written reason. Super-bear start −2.6% is a vol drought. Probabilities tilted slightly to the bear side for OE volatility: 12/26/30/22/10. Multipliers at defaults 0.75/0.90/1.00/1.10/1.25.
Price: **$292.25** (Nasdaq quote at run time).

| Scenario | Prob | Growth start | OE mult | IV@15% | IRR |
|---|---|---|---|---|---|
| Super bear | 12% | −2.6% | 0.75 | $59 | 4.8% |
| Bear | 26% | +4.4% | 0.90 | $98 | 6.8% |
| **Base** | **30%** | **+11.4%** | **1.00** | **$152** | **9.4%** |
| Bull | 22% | +18.4% | 1.10 | $234 | 12.9% |
| Super bull | 10% | +25.4% | 1.25 | $370 | 17.5% |

- **Probability-weighted: IV@15% $167 (−43% vs price), IV@12% $229, weighted IRR 10.2%**
- **Tier by numbers: C.** Diagnostics: OE yield on the clean base 4.2%, terminal value 22% of IV@15%, net cash 0.60× normalized OE (engine basis).

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.4 months ago): Resolved with the full TTM build above — raw TTM OE $17.47/share is float-inflated, float-cleaned TTM is $9.41/share and June-timing-depressed; the FY2025 clean base ($12.22) was used instead, with H1 2026 earnings (+52% NI YoY) confirming it is not stale-high.
- **BASE_DIVERGENCE** (latest $15.52 vs 3-yr median $9.46): Both ends are distorted. The latest year is inflated by +$528.5M of clearing float in OCF. The median is built from raw OCF for 2023–24, years whose float lines were smaller (+$282.6M/+$76.0M) but whose *clean* OE was genuinely ~$7.5/share — so the median mixes a real pre-2025 earnings level with float noise. Resolution: float-cleaned series ($7.55 / $7.51 / $12.22); the step-up is documented in audited adjusted EPS, and the base is the latest clean year.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 6.3× super-bear): Real — it is the volume cycle plus base uncertainty, not a modeling artifact. Confidence is low and bear weight was raised (super bear 12%, bear 26%).
- **OE_VOLATILE** (raw OE/share spans >3× over 5 yrs): Mostly manufactured by the float lines (raw range $4.84–$15.52); the clean series is a step ($7.5 → $12.2), not chaos. The underlying business is still volume-cyclical, which is why the super-bear case carries a negative growth start and a 0.75 multiplier.
- **SECTOR_MODEL_MISMATCH** (Finance): Partially applicable. Cboe is an exchange/CCP, not a bank or insurer — no loan book, no underwriting float of its own; capex is real but small ($88M TTM, mostly technology) and SBC is a real cost, so the OE framework fits far better than for a lender. The genuine mismatch is the one fixed above: consolidated OCF contains clearing-participant balances. Confidence graded **low** per the rule, and the verdict is sized accordingly.

Balance sheet (not a flag, folded into the verdict): corporate net cash $773.6M (own cash $2,216.5M vs debt $1,442.9M) ≈ $7.36/share, which the engine's IV does **not** add — a small conservatism in the IVs above. The $1,617.0M of restricted clearing balances on the balance sheet is participants' money and is excluded everywhere in this analysis.

## My thoughts / overlay
- The verdict is base-dominated, and the range is the honest headline: on the June-timing-depressed TTM-clean base ($9.41) the weighted IRR is 8.6% (Tier D, IV@15% $129); on the chosen FY2025 clean base ($12.22) it is 10.2% (Tier C, $167); even on the float-inflated raw base ($15.52) it is only 12.0% (Tier C, $212). **No defensible base clears 15% at $292** — the disagreement is between C and D, not between cheap and expensive. The stock's de-rating from its $371 high to the $271–297 range has not changed that math; consensus targets (~$300–307) are pricing the same sustained mid-teens growth the bull case needs.
- Quality is not the debate: exclusive index franchise, 72% EBITDA margins, net cash, buybacks shrinking the count ~0.5%/yr, and a secular (0DTE/retail/index) volume tailwind that has survived several vol regimes. What the price demands is that a *record-volatility* earnings level becomes the new base and compounds at double digits — possible, but it is paying upfront for the bull path.
- Watch items: the Canada/Australia disposals and CEDX wind-down from the 2025 strategic realignment (small basis break — excluded businesses are minor vs the index core; consolidated growth inputs above are not materially distorted by them); RPC dilution if 0DTE mix keeps rising; any transaction-tax or exclusivity challenge; Q3 2026 print on Oct 30, 2026.
- Hurdle math: the weighted path clears 15% at **≤ ~$167**; on the base case alone at ≤ ~$152. With a margin of safety against the wide spread, a buyer is paid at **~$130–150**, not at $292.

## Final verdict
- **Final tier: C** (weighted IRR 10.2% on the float-cleaned FY2025 base; method range D→C, and even the float-inflated base only reaches 12.0%)
- Confidence: **Low** (sector-model flag + 6.3× scenario spread + base is a judgment call between two defensible cleans)
- One-liner: Top-tier exchange franchise, moat 7/10, with real (float-cleaned) owner's earnings of $12.22/share — but at $292 (23.9× that base) the weighted IRR is 10.2%, well short of the 15% hurdle; it clears 15% only at ≤ ~$167, and with a margin of safety nearer $130–150.
