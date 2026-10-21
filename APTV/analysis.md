# APTV — Aptiv PLC
Engine 5.5 run, 2026-10-20. Price $45.11 (nasdaq_quote_api), market cap $9.958B (basis: diluted_latest; price × shares) — in scope under $40B.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json or fundamentals.json — none are recomputed.

## What it is
Global automotive technology supplier (SIC 3714, Motor Vehicle Parts & Accessories) — electrical architecture / interconnect, advanced safety and user experience (now Intelligent Systems), and engineered components, plus Wind River software. **The company changed shape in 2026:** on April 1, 2026 Aptiv completed the tax-free spin-off of its Electrical Distribution Systems (EDS) segment into Versigent PLC (VGNT) — shareholders of record March 17, 2026 received one Versigent share for every three Aptiv shares, EDS is presented as discontinued operations for all periods presented in the 2026 filings, and Aptiv received a dividend of approximately $1.9 billion from Versigent, used to redeem debt. EDS was $8.8B of FY2025 revenue in the carve-out reporting cited in the spin-off materials, against consolidated FY2025 revenue of $20.398B in financials_history.csv. The remaining "New Aptiv" guided FY2026 (Q2 2026 release, pro forma ex-EDS) to net sales $12,600–$12,800M, cash flow from continuing operations $1,270–$1,370M and free cash flow $625–$725M, with adjusted revenue growth of 2% at the midpoint. Q2 2026 continuing revenue was $3.3B, adjusted growth 2%, adjusted EBITDA $613M, and free cash flow was an outflow of $33M including approximately $70M of cash separation costs for the Versigent spin-off.

## Owner's earnings
Two definitions, from financials_history.csv / key_numbers.md:
- **Conservative (OCF − capex − SBC), latest FY2025:** OE total $1.390B, OE/share $6.30. Capex FY2025 $656.0M (components: PaymentsToAcquireProductiveAssets), SBC is filed under ShareBasedCompensation.
- **Normalized (3-yr median OE/share): $5.83** — FY2023 $3.09, FY2024 $5.83, FY2025 $6.30 per the history (median is the FY2024 figure).
- OE positive 5 of the last 5 fiscal years.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $2,185,000,000 − prior YTD $783,000,000 + current YTD −$51,000,000 = **TTM $1,351,000,000**
- Capex: FY $656,000,000 − prior YTD $267,000,000 + current YTD $278,000,000 = **TTM $667,000,000**
- SBC: FY $139,000,000 − prior YTD $64,000,000 + current YTD $50,000,000 = **TTM $125,000,000**
- Shares (current-YTD weighted diluted): **212,530,000**
- **TTM OE total $559,000,000 → base OE/share $2.63** (base_source: ttm_json)

**Why the TTM base, not the $5.83 median — the basis break is the whole call.** The median and latest-FY figures are consolidated Aptiv *including* EDS, a business APTV shareholders no longer own through APTV (they own it separately as VGNT, 1 share per 3 APTV). Scoring the $45.11 post-spin price on the pre-spin median printed Tier A at a 22.47% weighted IRR in the preliminary run — a tier for a company that no longer exists in that form. The TTM window still straddles the spin (H2 2025 was pre-spin, H1 2026 includes separation costs and a weak H1 OCF print: current-YTD OCF −$51,000,000 vs prior YTD $783,000,000), so it is not a clean New Aptiv figure either — but it is corroborated by the company's own New Aptiv guidance above: guided continuing OCF of $1,270–$1,370M less guided free cash flow of $625–$725M leaves a guided OE after capex and SBC in the same range as the TTM OE total of $559,000,000. No cleaner filing-direct New Aptiv OE base exists in this run's outputs; the pro forma statement of operations in the April 2026 8-K exhibit is an operations statement, not a cash-flow statement. Confidence is therefore low, and the method range (below) is part of the verdict.

## Moat: 4/10 — weak-to-moderate
Evidence first (fundamentals.json): **roic_proxy** was 11.4% in FY2021, 8.0% in FY2022, 7.6% in FY2023, 10.3% in FY2024 and 6.2% in FY2025 — falling, and at/below a plausible cost of capital in the last three years. **Gross margin** over the last five fiscal years: 15.6% (FY2021), 15.1% (FY2022), 17.2% (FY2023), 18.8% (FY2024), 19.1% (FY2025) — improving but thin for a claimed technology leader. A moat above 4 would need ROIC sustained well above the cost of capital; the measured history says the opposite.
- FOR: OEM design integration — engineers embedded in vehicle programs years before production, the architecture baked into the platform, high switching costs once specified; global scale in electrical architecture/interconnect with leading ADAS and domain-controller positions; Smart Vehicle Architecture plus Wind River software for software-defined vehicles; non-automotive diversification growing 12% in Q2 2026 (industrials, aerospace/defense).
- AGAINST: ROIC proxy falling to 6.2% in FY2025; 19.1% gross margin and structural OEM price-downs, with the top-10 OEM customers a majority of sales in the FY2025 reporting; larger rivals — Bosch held an estimated 16% of the smart-vehicle-architecture market in 2025 vs Aptiv at 7.4% (industry survey cited in research) — plus OEM vertical integration of compute; the $648M FY2025 non-cash goodwill impairment on Wind River, i.e. software-defined-vehicle adoption slower than the acquisition price assumed; cyclical vehicle production and ongoing Motional autonomous-driving equity losses.
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — final run (2026-10-20)
**Growth sanity check and recalibration (written reason):** the engine's blended growth is 12.29% (components, key_numbers.md: rev CAGR 5y 9.32%, rev CAGR 3y 5.26%, latest rev YoY 3.47%, OE/share CAGR 2y 42.64%, share-count adjustment +5.00%). That blend straddles the basis break — the OE/share CAGR is measured on the pre-spin consolidated business and the revenue CAGRs include EDS — and it contradicts every current print: FY2025 consolidated revenue grew 3.47%, Q2 2026 continuing revenue grew 2% adjusted, and New Aptiv's FY2026 guidance implies adjusted growth of 2% at the midpoint. Scenario starts were therefore set via offsets (−0.1529 / −0.1229 / −0.0929 / −0.0629 / −0.0229 vs the 12.29% blend) to −3 / 0 / **3** / 6 / 10%. Even the super-bull start (10%) sits above guidance — it is the case where non-auto growth and software content outrun the auto cycle, not a forecast. Probabilities 15/30/30/17/8 — bear-weighted per OE_VOLATILE and HIGH_NET_DEBT; OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $45.11.

| Scenario | Prob | Growth start | OE mult | IV@15 | IRR |
|---|---|---|---|---|---|
| Super bear | 15% | -3.0% | 0.75 | $13.07 | 5.97% |
| Bear | 30% | 0.0% | 0.9 | $17.63 | 7.31% |
| Base | 30% | 3.0% | 1.0 | $21.99 | 8.61% |
| Bull | 17% | 6.0% | 1.1 | $27.13 | 10.11% |
| Super bull | 8% | 10.0% | 1.25 | $35.87 | 12.56% |

- **Probability-weighted: IV@15% $21.32 (−52.7% vs price), IV@12% $28.10, IV@10% $35.64, weighted IRR 8.43%, base-case IRR 8.61%**
- **Tier by numbers: D.** Bear→bull band: bear 7.31% (tier D) → bull 10.11% (tier C); scenario range 5.97% – 12.56%.
- Diagnostics (key_numbers.md): OE yield 5.83%, terminal value 17.9% of IV@15%, scenario spread 2.74x, net debt / normalized OE 9.96x, 9.6 months since FY end.
- Hurdle-clearing prices (weighted path): 15% at $21.32 · 20% at $15.20 · 25% at $11.80.

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 10 months ago, 9.6 months since FY end): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above.
- **BUYBACK_TAILWIND** (share count shrinking 6.6%/yr; key_numbers.md: share count CAGR −6.63%): credited in the engine blend via the +5.00% growth adjustment, but the scenario starts were set from revenue prints and guidance, not from the blend, so the buyback tailwind is not double-counted in the verdict. Note the −6.63% CAGR is itself measured across the spin window and a heavy repurchase program ($1.8B remained under the authorization at June 30, 2026 per the Q2 release).
- **OE_VOLATILE** (OE/share range over the last 5 yrs spans >3x): real and cyclical — OE/share ran $1.93 (FY2021), $1.23 (FY2022), $3.09 (FY2023), $5.83 (FY2024), $6.30 (FY2025) on the consolidated basis. Handled by the TTM base and by putting 45% of probability on bear-or-worse scenarios.
- **NI_OCF_DIVERGENCE** (>40% in 2023, 2025): both years are non-cash tax/impairment effects, not OCF quality problems. FY2023: net income $2,938M vs OCF $1,896M in financials_history.csv, with a tax line of −$1,928M (a large deferred-tax benefit inflating net income). FY2025: net income $165M vs OCF $2,185M — the FY2025 release states net income includes a non-cash goodwill impairment charge of $648M (Wind River), and the history's FY2025 tax line is $700M. The OCF-based conservative OE used throughout is unaffected by either; the base does not rest on net income in either year.
- **HIGH_NET_DEBT** (net debt 10.0x normalized OE; key_numbers.md: net debt / normalized OE 9.96x, net debt latest $5.781B): the $5.781B is the FY2025 (pre-spin) balance sheet — debt_current from ShortTermBorrowings plus LongTermDebtAndCapitalLeaseObligationsCurrent, debt_lt LongTermDebtNoncurrent, less cash $1,851M per financials_history.csv, plus lease liabilities of $543M recorded separately in dcf_numbers.json. Post-spin the picture improved: Aptiv used the ~$1.9B Versigent dividend to redeem $1,847M of senior notes in April 2026 after redeeming $266M in Q1 2026 (Q1/Q2 2026 releases). Even so, against a TTM OE total of $559,000,000 the remaining leverage is high, which is why the bear cases are weighted at 45%.
- **TIER_BAND** (bear-case tier D, 7.3%, vs bull-case tier C, 10.1%): the verdict is sized to the bear end — both the bear and the weighted cases are Tier D, and even the super-bull case (12.56%) does not clear 15%.

## My thoughts / method range
- The honest headline is the **method range: Tier D on the post-spin TTM base (this run) to Tier A on the pre-spin median base (preliminary run, weighted IRR 22.47%, IV@15% $76.56)**. The A is not a live alternative — it values EDS cash flows the APTV price no longer claims — but anyone quoting APTV from a screener built on consolidated history will see something like it. The TTM base is the only filing-direct base in this run that reflects the smaller company, and management's own FY2026 continuing-operations guidance (OCF $1,270–$1,370M, FCF $625–$725M) brackets it.
- What would change the verdict: a clean post-spin cash-flow history (the FY2026 10-K, filed on a continuing basis) showing New Aptiv OE/share sustainably above the TTM $2.63 — e.g. if H1 2026's −$51,000,000 YTD OCF proves to be separation costs and working-capital timing rather than run rate. H2 is seasonally Aptiv's strong half, so this is a live possibility; it is a reason to re-run on the next filing, not a reason to score it now.
- Quality: the retained business is the higher-margin part (adjusted EBITDA margin guided to 18.4% for FY2026 on the New Aptiv pro forma basis, above the old consolidated operating margins in the history), buybacks continue, and the spin cleaned the balance sheet. None of that makes $45.11 cheap on $2.63 of TTM owner's earnings — the price needs the bull path just to reach a low-teens IRR.

## Final verdict
- **Final tier: D** (weighted IRR 8.43% on the TTM base; bear D → bull C)
- Confidence: **low** (basis break: the TTM base straddles the April 2026 Versigent spin-off and is corroborated by guidance rather than by a clean post-spin filing history; the method range runs D to A)
- One-liner: Cyclical auto-tech supplier, moat 4/10 — does not clear 15% on the post-spin TTM base (weighted IRR 8.4%, IV@15 $21.32 vs $45.11 price); it would clear 15% only below $21.32, and the pre-spin median base that printed Tier A is not the business the price now buys.
