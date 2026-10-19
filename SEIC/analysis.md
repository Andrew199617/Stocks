# SEIC — SEI Investments Company
Engine 5.4.0 run, 2026-10-18. Price $104.40 (nasdaq_quote_api), market cap (est) $13.267B — in scope under $40B.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, or fundamentals.json — none are recomputed.

## What it is
Technology, investment-management and outsourcing platform for banks, wealth managers, advisors and investment managers: the SEI Wealth Platform (end-to-end processing/custody/reporting infrastructure), investment-manager fund administration, and manager-of-managers investment products. Q2 2026 release: ~$2.1 trillion managed, advised or administered; AUM $606.7B. Revenue is largely recurring asset-based and processing fees. The Stratos Wealth Holdings acquisition closed in December 2025 (FY2025 acquisitions $302.048M in fundamentals.json; goodwill rose from $170.287M in FY2024 to $354.989M in FY2025 and intangibles from $77.370M to $368.272M).

## Owner's earnings
**FY2025 (10-K via EDGAR):** operating cash flow $607,662,000; capex $22,644,000; SBC $53,555,000.
- **Conservative owner's earnings FY2025: $531,463,000 = $4.18/share** (latest FY OE/share, key_numbers.md)
- Normalized base (median of last 3 FY OE/share): $4.03/share — the FY2023 dip year ($2.92/share on the filed history) drags it.
- OE positive 5 of the last 5 fiscal years.
- Maintenance definition is not quoted separately here: the conservative OCF-based figure is the series used throughout, and TTM net income ($706,850,000, fundamentals.json) sits essentially on top of TTM OCF ($712,024,000), so there is no float/reserve wedge between earnings and cash — unlike a bank or insurer, this OE is distributable cash.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $607,662,000 − prior YTD $243,005,000 + current YTD $347,367,000 = **TTM $712,024,000**
- Capex: FY $22,644,000 − prior YTD $12,451,000 + current YTD $15,029,000 = **TTM $25,222,000**
- SBC: FY $53,555,000 − prior YTD $28,029,000 + current YTD $30,809,000 = **TTM $56,335,000** (always a real cost; ~8-9% of OCF)
- Shares (current-YTD weighted diluted): **123,914,000**
- **TTM OE total $630,467,000 → base OE/share $5.09** (base_source: ttm_json)
- The TTM base is 26% above the normalized $4.03 — it reflects real H1 2026 operating leverage (Q2 2026 revenue $641.6M, +14.7% YoY; adjusted operating margin 32% vs 27% a year earlier, per the Q2 2026 earnings release) plus the first Stratos contribution. It is used, with the method range below stated plainly.

## Moat: 6/10 — moderate-strong, narrow
Justification: Moderate-strong narrow moat: the SEI Wealth Platform and investment-manager outsourcing are mission-critical, deeply embedded systems with high switching costs and a largely recurring, asset-based fee base, evidenced by a ROIC proxy that stayed between 24% and 43% over FY2016-25 (30.4% in FY2024, 24.0% in FY2025) and gross margin expanding from 29.0% in FY2023 to 35.2% in FY2025 / 36.0% TTM. Capped at 6, not 7+: ROIC is trending down as Stratos goodwill/intangibles swell invested capital, revenue growth averaged only 6.4% over five years, fees carry full equity-market beta, and custody-bank/SS&C scale competitors contest every mandate — pricing power is real but not structural.
- FOR: SEI Wealth Platform is deeply embedded back/middle-office infrastructure — migration cost and operational risk make switching rare; recurring revenue base — asset-based and processing fees on ~$2.1T managed/advised/administered assets (Q2 2026); returns through a cycle — ROIC proxy 24-43% over FY2016-25, never below 24%, gross margin rising to 35.2% in FY2025 and 36.0% TTM; asset-light, net-cash model — capex ~1% of revenue, SBC only ~8-9% of OCF, buybacks shrinking diluted shares 2.6%/yr.
- AGAINST: Asset-based fees are hostage to market levels — a bear market cuts AUM/AUA revenue with no action by SEIC; fee pressure across asset management and administration, with larger custody banks (BNY, State Street) and SS&C competing on scale; ROIC proxy falling — 42.4% in FY2021 to 24.0% in FY2025 — as Stratos swells goodwill/intangibles; growth historically modest (5-yr revenue CAGR 6.4%) and the recent acceleration is partly inorganic (Stratos) and market appreciation; large platform mandates can unwind on a client's own strategic change.
- ROIC / margin evidence (fundamentals.json, roic_proxy series): FY2021 42.4%, FY2022 33.7%, FY2023 25.4%, FY2024 30.4%, FY2025 24.0%. Gross margin: FY2021 33.6%, FY2022 32.3%, FY2023 29.0%, FY2024 32.9%, FY2025 35.2%, TTM 36.0%. Returns stayed well above any plausible cost of capital through the 2022-23 drawdown — that supports 6 — but the downtrend in ROIC is why it is not 7.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — engine 5.4.0 final run (2026-10-18)
Growth sanity check: the engine blend is 9.83% (rev CAGR 5y 6.41%, rev CAGR 3y 4.88%, latest rev YoY 8.10%, OE/share CAGR 2y 19.60%, plus the +2.57pp buyback adjustment on revenue components). Recent prints run HOTTER than the blend — TTM revenue +11.1% (fundamentals.json), Q2 2026 revenue +14.7% YoY, H1 2026 +14% — so no scenario start is below the latest print without reason: the base start (9.8%) sits below the Q2 print deliberately, because part of the +14-15% is inorganic Stratos consolidation (closed Dec 2025, so H1 2026 is compared against a Stratos-free H1 2025) and part is equity-market appreciation in AUM fees, neither of which is a permanent organic growth rate. The bull start (14.8%) essentially equals the Q2 print; the super-bull start (21.8%) is an OE/share path, not a revenue path — OE/share CAGR 2y printed 19.60% on margin expansion plus buybacks, so 21.8% is aggressive but not detached from prints. Default offsets (−12/−5/0/+5/+12pp) and OE multipliers (0.75/0.90/1.00/1.10/1.25) and probabilities (10/25/30/25/10) were kept — the evidence supports the standard fan around a conservative base.

| Scenario | Prob | Growth start | OE mult | IV@15 | IRR |
|---|---|---|---|---|---|
| Super bear | 10% | -2.2% | 0.75 | $25.42 | 5.36% |
| Bear | 25% | 4.8% | 0.90 | $41.66 | 7.59% |
| Base | 30% | 9.8% | 1.00 | $57.81 | 9.72% |
| Bull | 25% | 14.8% | 1.10 | $79.37 | 12.32% |
| Super bull | 10% | 21.8% | 1.25 | $122.72 | 16.77% |

- **Probability-weighted: IV@15% $62.41 (−40.2% vs price), IV@12% $84.57 (−19.0%), IV@10% $109.51, weighted IRR 10.34%, base-case IRR 9.72%**
- **Tier by numbers: C.** Diagnostics (key_numbers.md): OE yield 4.87%, terminal value 20.8% of IV@15%, scenario spread 4.83x, months since FY end 9.6.
- Hurdle-clearing prices (weighted path): 15% at $62.41 · 20% at $42.79 · 25% at $32.19.

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 10 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above (TTM OE/share $5.09 vs latest FY $4.18).
- **BUYBACK_TAILWIND** (share count shrinking 2.6%/yr): already credited via the +2.57pp growth adjustment in the blend; not double-counted in the verdict. Fundamentals TTM: buybacks $565,485,000 against issuance $147,317,000 and dividends paid $127,169,000.
- **DEBT_TAGS_BLANK** (no debt tag for the latest fiscal year — net debt UNKNOWN, not zero): stated from the filing — in FY2025 SEIC carried no tagged debt because it had essentially none: cash was $399,804,000 at 2025-12-31 (Q2 2026 earnings release balance sheet) against zero long-term debt on that date. Debt appeared only in 2026 alongside Stratos: at 2026-06-30 cash and equivalents were $395,664,000 against long-term debt $29,483,000 plus current portion $3,487,000, total liabilities $477,439,000 and operating lease liabilities $28,562,000 (FY2025). This is a net-cash balance sheet; the engine's null net debt understates nothing material, and no leverage verdict is needed beyond that.
- **SECTOR_MODEL_MISMATCH** (Finance sector — OE/capex DCF fits finance names poorly): confidence graded low, as required. Substantively, SEIC is the benign end of this flag: it is not a bank or insurer — TTM net income ($706,850,000) ≈ TTM OCF ($712,024,000), there is no float or reserve growth inside OCF, and capex/SBC are fully tagged — so no tier override is applied (contrast the insurer float-softening cases). The flag still caps confidence at low and score.json records model_fit "misfit" with alerts suppressed for that reason.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.83x super-bear IV): real — the range is driven by market beta on fees plus operating leverage, in both directions. Confidence is low and the verdict is sized to the bear end.
- **TIER_BAND** (bear tier D at 7.59% vs bull tier C at 12.32%): the verdict spans D-C; even the bull case does not clear 15% — only the 10%-weighted super bull (16.77%) does. Sized to the bear end: D-C, final C only on the weighted number.

## My thoughts / overlay
- Method range: on the normalized median base ($4.03/share) instead of TTM, the preliminary engine run printed weighted IRR 8.57% and weighted IV@15% $47.94 — Tier D. On the TTM base actually used: weighted IRR 10.34%, IV@15% $62.41 — Tier C. The honest headline is that range, D to C; no defensible base gets this price anywhere near a 15% return. Even the super-bull scenario's IV@15% ($122.72) is only 18% above the $104.40 price.
- Quality is not the debate: OE positive 5/5 years, ROIC never below 24% in a decade, net cash, semi-annual dividend raised for 24 straight years (fundamentals: DPS TTM $1.04, 5-yr DPS CAGR 7.0%, no cut since 2013), and buybacks comfortably exceeding SBC + issuance drag.
- Watch items: Q2 2026 GAAP EPS fell 11% YoY ($1.59 vs $1.78) while adjusted EPS rose 38% — the gap is non-operating items in the prior-year quarter, but it is a reminder to read the GAAP line, not the adjusted headline. Stratos integration and its goodwill/intangibles load bear on the falling ROIC trend. Next earnings are expected 2026-10-28 per market calendars — not a filing fact, treat as indicative only.
- Margin of safety: none at this price on these numbers — the price sits 67% above the weighted IV@15% ($62.41). A buyer at $104.40 is paying for the bull/super-bull path at full weight.

## Final verdict
- **Final tier: C** (weighted IRR 10.34% on the TTM base; method range D on the normalized base to C on TTM — sized to the conservative end, the name is a low-C)
- Confidence: **Low** (SECTOR_MODEL_MISMATCH grading rule plus a 4.83x scenario spread; high confidence in the OE figures themselves, low in any single growth path)
- One-liner: High-quality asset-light platform compounder, moat 6/10 — does not clear 15% at $104.40 (weighted IRR 10.3%, weighted IV@15% $62.41); it clears 15% only at ~$62, so the quality is not the debate, the price is.
