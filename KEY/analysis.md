# KEY — KeyCorp
v5 run, 2026-10-15. In scope (market cap $22.07B at $19.92, nasdaq_quote_api).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, financials_history.csv, or a cited search result — none are recomputed.

## What it is
Cleveland-based super-regional bank holding company (~$191B assets at Q2 2026 per search results), operating across 16 states with Ohio, New York and Washington its largest deposit markets. Mix of middle-market commercial banking (C&I is the growth book), consumer banking, and fee businesses: investment banking and debt placement (KeyBanc), payments/cards, trust and wealth, and commercial mortgage servicing. Earnings are overwhelmingly a net-interest-margin story: Q2 2026 NIM was 2.89%, NII rose 9.4% YoY, and management targets a core NIM of 3.00–3.05% in 2026 and 3.25%+ in 2027, with a >15% core ROTCE target by end-2027 (search results: Q2 2026 earnings release and September 2026 investor presentation).

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $2,208,000,000; capex $107,000,000 (tag PaymentsToAcquireProductiveAssets); SBC $132,000,000 (tag ShareBasedCompensation — always a real cost, but small for a bank).
- **Conservative owner's earnings FY2025: $1,969,000,000** (OCF − capex − SBC).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,829,000,000 — same ballpark, which helps.
- OE positive 5 of the last 5 fiscal years, but the path is violent: conservative OE was $2,640,000,000 in FY2023, $495,000,000 in FY2024, $1,969,000,000 in FY2025 (all from financials_history.csv). FY2024 net income was −$161,000,000 — see NI_OCF_DIVERGENCE below.
- Net debt per the engine: $9,917,000,000 (long-term debt; see HIGH_NET_DEBT — for a bank this is not the leverage that matters).

**Base used = the engine's normalized base, median of the last 3 FY OE/share: $1.78/share** (dcf_numbers.json: base_oe_per_share / base_oe_normalized_per_share $1.7770854354806975, base_source median_of_last_3_fy_oe_per_share). The median year is FY2025 itself, so the normalized and latest-FY bases coincide.

**TTM was run and NOT used as the base — written reason.** ttm.py (filing-direct, saved to ttm.json) through Q2 2026:
- OCF: FY $2,208,000,000 − prior YTD $1,094,000,000 + current YTD $197,000,000 = **TTM $1,311,000,000**
- Capex: FY $107,000,000 − prior YTD $33,000,000 + current YTD $38,000,000 = **TTM $112,000,000**
- SBC: FY $132,000,000 − prior YTD $63,000,000 + current YTD $64,000,000 = **TTM $133,000,000**
- Shares (current-YTD weighted diluted): **1,087,412,000**
- **TTM OE total $1,066,000,000 → TTM OE/share $0.98**

That TTM figure is rejected as the base because for a bank the OCF leg is a balance-sheet flow, not earnings: H1 2026 OCF of $197M against H1 net income that produced diluted EPS of $0.88, up 28% from $0.69 in H1 2025, and Q2 2026 EPS of $0.44, up 25.7% YoY (search results: Q2 2026 earnings release / investor presentation). Earnings power is rising while the OCF leg collapses — pinning the base to $0.98 would price a loan/deposit-flow swing as if it were lost earnings. The 3-year median ($1.78) sits on the recovered FY2025 year and is the defensible base; the TTM print is retained here as the conservative bound of the method range.

## Moat: 4/10 — weak-to-moderate regional-bank franchise
Justification: a real deposit and relationship franchise with genuine fee businesses and a credible NIM-rebuild path, but a commodity product with no structural pricing power, full credit- and rate-cycle exposure, and returns that are guided (ROTCE >15% by 2027) rather than proven through a cycle.
- FOR: Deposit/relationship franchise at scale across 16 states (Ohio, New York, Washington the largest deposit markets); middle-market C&I relationships — average C&I loans up 11.7% YoY in Q2 2026 (search results).
- FOR: Diversified fee engines inside the bank — investment banking and debt placement, cards and payments, trust/wealth (record AUM per the September 2026 presentation), commercial mortgage servicing.
- FOR: NIM rebuild is actually printing — 2.89% in Q2 2026, up 23 bps YoY, with ~$9B of fixed-rate assets repricing in H2 2026 and ~$21B in 2027 (search results); deposit costs fell 36 bps YoY.
- FOR: Capital bolstered by Scotiabank's strategic minority investment (~163M shares at $17.17 for ~$2.8B, second tranche closed Q1 2025); CET1 ratio 11.2% at Q2 2026 and buybacks resumed — $341M repurchased in Q2 2026, at least $1.3B expected for 2026 (search results).
- AGAINST: Commodity product — deposits and loans are fungible; the NIM is earned through repricing and mix, not owned, and deposit repricing pressure is outside management's control.
- AGAINST: Credit-cycle exposure — non-performing assets rose in Q2 2026, concentrated in commercial real estate, agriculture and consumer goods; net charge-offs were 42 bps of loans (search results). Provisions are the swing factor in any downturn.
- AGAINST: Capital-constrained growth — loan growth, the dividend (~$0.20/quarter) and the buyback all compete for the same CET1; Basel III endgame requirements are still evolving.
- AGAINST: Scale/efficiency disadvantage vs the money-center banks' technology and compliance budgets; management is guiding ~$1B of technology investment just to keep pace.
- AGAINST: Per-share dilution to re-earn — the Scotiabank issuance lifted diluted shares from 949,561,000 (FY2024) to 1,107,994,000 (FY2025) in the filed history; the resumed buyback has to retire that before per-share compounding restarts.
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Growth recalibration (written reason): the engine's g_base of −1.36% is not usable as printed. Its revenue series is the contract-revenue tag (RevenueFromContractWithCustomerExcludingAssessedTax), which for a bank excludes interest income — the CSV revenue line is $1,749,000,000 for FY2025 and the series breaks at FY2018 ($6,308,000,000 in FY2017 to $1,316,000,000 in FY2018) purely on the tag — and the blend is then dragged by a −5pp share-count adjustment for a share CAGR (+5.9%/yr) that is really the one-off Scotiabank capital raise, not ongoing dilution, plus an OE/share CAGR 2y of −20.75% measured off the repositioning-wrecked FY2024. Scenario starts were therefore set via offsets (−0.0864 / −0.0264 / +0.0436 / +0.0936 / +0.1436 vs g_base) to −10 / −4 / **+3** / +8 / +13%: a low-single-digit through-cycle base (earnings power grows with mid-single-digit loan growth, fee growth and resumed buybacks, minus through-cycle credit costs), bears carrying a real provision cycle, bull/super-bull anchored on the NIM-to-3.25% / ROTCE-15% path. Probabilities 10/30/30/20/10 (bear overweighted for OE_VOLATILE); OE multipliers 0.75/0.90/1.00/1.10/1.25. Price $19.92.

Sanity check against actual prints: Q2 2026 revenue grew 6.7% YoY and H1 2026 revenue 8% YoY, with diluted EPS up 25.7% (Q2) and 28% (H1) — recovery prints off the FY2024 repositioning trough, flattered by falling deposit costs and asset repricing that fade by construction. The base start (+3%) sits below those prints with that reason; the bull start (+8%) matches the current revenue print; even the super-bull start (+13%) sits well below the EPS rebound rate, deliberately — a rebound rate is not a 15-year start rate.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -10.0% | 0.75 | Credit cycle turns: provisions spike, NIM rebuild stalls, buybacks halt | $6.70 | 6.30% |
| Bear | 30% | -4.0% | 0.90 | Recession-lite: charge-offs normalize up, CRE/agri stress spreads, earnings shrink first | $10.19 | 8.68% |
| Base | 30% | 3.0% | 1.00 | NIM grinds toward ~3%, mid-single-digit loan/fee growth, buybacks offset SBC drip | $14.85 | 11.83% |
| Bull | 20% | 8.0% | 1.10 | NIM reaches 3.25% in 2027, ROTCE approaches 15%, capital return compounds per-share OE | $19.77 | 14.91% |
| Super bull | 10% | 13.0% | 1.25 | ROTCE target hit and held, fee businesses compound, no credit cycle in the window | $27.12 | 19.09% |

- **Probability-weighted: IV@15% $14.85, IV@12% $19.60, IV@10% $24.88, weighted IRR 11.85%, base-case IRR 11.83%**
- **Tier by numbers: C.** Diagnostics (dcf_numbers.json): OE yield 8.92%, terminal value 18.08% of IV@15%, scenario spread 4.05x, net debt 5.04x normalized OE, 9.46 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.46 months ago): ttm.py was run and its full inputs are quoted above. The TTM base ($0.98/share) was NOT pinned, for the written reason given there — a bank's OCF leg is a balance-sheet flow and it contradicts the reported earnings trajectory (H1 EPS +28% YoY). The median base was used instead, and the TTM figure is carried as the conservative method bound.
- **DILUTION** (share count +5.9%/yr): resolved — this is not SBC drip. It is Scotiabank's strategic minority investment: ~163M newly issued shares at $17.17 (~$2.8B), first tranche August 2024, second tranche closed Q1 2025 (search results), which is why diluted shares step from 949,561,000 (FY2024) to 1,107,994,000 (FY2025) in the filed history. SBC itself is $132,000,000 in FY2025 — immaterial next to OE. The direction has already reversed: current-YTD diluted shares are 1,087,412,000 (ttm.json) and $341M was repurchased in Q2 2026 with at least $1.3B expected for 2026 (search results). The engine's −5pp growth adjustment for this "dilution" is one of the reasons g_base was recalibrated rather than used as printed.
- **OE_VOLATILE** (OE/share range >3x over 5 years): real — FY2024 conservative OE of $495,000,000 against $2,640,000,000 in FY2023 and $1,969,000,000 in FY2025. Handled by the 3-year median base and by overweighting the bear case to 30% probability with a 0.75 super-bear OE multiplier.
- **NI_OCF_DIVERGENCE** (2023, 2024): identified. FY2024 net income was −$161,000,000 against OCF of $664,000,000 because Q4 2024 carried a $915M loss on the sale of securities in the strategic repositioning of the available-for-sale portfolio that followed the Scotiabank capital raise (search results: Q4 2024 / Q4 2025 earnings releases) — a realized investing loss inside net income, not an operating cash shortfall; FY2024 conservative OE of $495,000,000 is the dent it left. The FY2023 gap (net income $967,000,000 vs OCF $2,903,000,000, financials_history.csv) is the recurring bank pattern: non-cash addbacks inside OCF (provision for credit losses, depreciation/amortization/accretion) plus balance-sheet flow. The structural point matters more than either year: the provision is a real through-cycle cost that OCF adds back, so the OCF-based OE base is systematically flattering for a bank — one more reason confidence is low and the bears carry 0.75/0.90 multipliers.
- **SECTOR_MODEL_MISMATCH** (Finance): accepted in full. A bank's "owner's earnings" are not its distributable cash — loan growth consumes regulatory capital, provisions are a through-cycle cost the OCF line only partially carries, and banking value is normally judged on ROTCE vs cost of equity and tangible book, none of which this model computes. Confidence is low and the tier is soft.
- **WIDE_SCENARIO_SPREAD** (4.05x): real — a bank's outcome range across a credit cycle IS wide (super-bear IV@15% $6.70 vs super-bull $27.12). Confidence is capped accordingly (low, also mandated by the sector flag) and the verdict is sized to the conservative end.
- **HIGH_NET_DEBT** (5.04x normalized OE): an artifact of applying an industrial leverage lens to a bank. The engine's net debt is the $9,917,000,000 long-term debt line with no cash leg in the pulled series; it excludes the deposit base that actually funds the bank and the loan/securities book that backs it. The leverage that matters is regulatory capital: CET1 11.2% at Q2 2026 (search results) — adequate, and the reason the buyback is sized in the ~$1.3B range rather than larger. The bear scenarios carry the credit stress this flag asks for.

## My thoughts / overlay
- The honest headline is the method range, and unusually it does not span tiers: the preliminary run on the engine's default scenarios printed weighted IRR 10.85% / IV@15% $13.38 (Tier C); this recalibrated final run prints 11.85% / $14.85 (Tier C); and the rejected TTM-OCF base ($0.98/share) would print materially lower still. Every defensible method says the same thing — at $19.92 the stock does not clear a 15% hurdle. What changes across methods is only how far below it sits.
- Quality is genuinely improving and the screen can see it: NIM expanding toward guided targets, charge-offs contained at 42 bps, fee businesses growing, capital rebuilt and buybacks resumed. None of that is the debate. The debate is price: even the bull case (IV@15% $19.77, IRR 14.91%) only roughly reaches the current price — a buyer at $19.92 needs the bull case just to approach 15%, and the weighted case returns 11.85%.
- Bank-specific cross-check the model cannot do: the entire bull story is NIM reaching 3.25% and ROTCE reaching >15% by 2027, and both are exactly what a shifting rate path or a credit turn postpones — management itself flagged pockets of CRE/agriculture/consumer stress in Q2 2026 (search results). If ROTCE stalls in the low teens, even the base case here is generous.
- Price that clears 15%: the weighted IV@15% is $14.85 — the stock clears Andrew's hurdle at or below that level, about a quarter below the current price, before any additional margin of safety. With a margin of safety against the bear cases (bear IV@15% $10.19), the low teens are the interesting zone.

## Final verdict
- **Final tier: C** (weighted IRR 11.85% on the v5 final inputs; no tier override — the numbers tier and the sector-soft verdict agree)
- Confidence: **Low** (sector-model mismatch plus a 4.05x scenario spread; the OE base itself is filing-solid on the median, with the TTM-OCF bound documented)
- One-liner: Improving super-regional bank, moat 4/10 — median OE $1.78/sh is an 8.92% yield at $19.92, but on through-cycle starts the weighted IRR is 11.85% (IV@15% $14.85) and even the bull case only reaches ~$19.77, so it clears 15% only below ~$14.85; bank-model mismatch, confidence low.
