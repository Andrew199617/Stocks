# BBY — Best Buy Co., Inc.
v5 run, 2026-10-16. In scope: market cap $19.976B at $94.18 (nasdaq_quote_api), under the $40B cutoff.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed.

## What it is
The largest US specialty consumer-electronics retailer (~1,068 stores at end of FY2026, Domestic + International): computing, appliances, home theater, mobile, gaming, plus Geek Squad services/installation, paid memberships, the Best Buy Ads retail-media network, and a third-party Marketplace launched in 2025. It sells identical manufacturer-branded products against Amazon (which passed it in 2025 with ~31% of US consumer-electronics spending vs Best Buy's ~27%, per Numerator figures reported in trade press), Walmart, Costco, Target, and Home Depot/Lowe's in appliances.

## Owner's earnings
**FY2026 (10-K via EDGAR, period ended 2026-01-31, from financials_history.csv):** revenue $41,691M; net income $1,069M; operating cash flow $1,962M; capex $704M; D&A $831M; SBC $139M (always a real cost).
- **Conservative owner's earnings FY2026: $1,119M = $5.28/share** (OCF − capex − SBC).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $749M — lower than the conservative figure, driven by the ΔNWC drag of $447M in FY2026 in the CSV. The two definitions bracket the base rather than agreeing, which is one reason the verdict is sized conservatively.
- OE positive 5 of the last 5 fiscal years, but the path is cyclical: OE/share troughed in FY2024 and recovered through FY2025–26 (see OE_VOLATILE below).
- Balance sheet: the engine's net_debt_latest is null (FY2026 debt fields are blank in the extracted CSV), so no net-debt figure is quoted from the engine. Q2 FY27 reporting (10-Q coverage) put cash and equivalents at ~$2.26B at 2026-08-01 with long-term debt of ~$1.17B — modest funded debt, with the real fixed load sitting in operating leases, which this model does not capitalize. No HIGH_NET_DEBT or BIG_NET_CASH flag fired.

**Base used = TTM owner's earnings through Q2 FY27 (2026-08-01), from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,962M − prior YTD $783M + current YTD $1,296M = **TTM $2,475M**
- Capex: FY $704M − prior YTD $341M + current YTD $344M = **TTM $707M**
- SBC: FY $139M − prior YTD $75M + current YTD $74M = **TTM $138M**
- Shares (current-YTD weighted diluted): **212,100,000**
- **TTM OE total $1,630M → base OE/share $7.69** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $5.28/share. Caution on the TTM base, stated plainly: the entire uplift vs the median comes from one half-year — H1 FY27 OCF of $1,296M vs $783M in H1 FY26 — and H1 retailer cash flow is working-capital timing (inventory was reported up 8.3% YoY at Q2). The TTM base is used per the STALE_FY procedure, but the scenario weights below are skewed bear-side (45% on bear-or-worse) precisely because part of that H1 swing can reverse in H2. The median-base method range is documented under Thoughts.

## Moat: 4/10 — weak-to-moderate, durable position, no pricing power
Justification: Best Buy has held the #1 specialty position for over a decade and its store/service network is genuinely hard to replicate, but it sells commodity products whose prices manufacturers and Amazon effectively set — ~4% operating margins (Q2 FY27 adjusted operating margin 4.3%) are the structural ceiling, and it slipped to #2 in category spending share in 2025.
- FOR: Geek Squad installation/service and in-store expertise rivals cannot match online; ~1,000-store showroom + same-day pickup network nobody would fund building today; vendor partnerships and store-within-store concepts with exclusive launches/demos; membership program driving repeat purchase; growing high-margin adjuncts — Best Buy Ads (management guided ~10% growth) and Marketplace (Q2 GMV ~$300M, FY27 forecast raised to $1.3B).
- AGAINST: identical SKUs sold by Amazon/Walmart/Costco with full price transparency and price-matching — no pricing power; manufacturers set product economics and can go direct; category is replacement-driven, not growth — revenue CAGR is negative over 3 and 5 years (−3.42% / −2.47% per the engine); Amazon already took the #1 spending share in 2025; appliances contested by Home Depot/Lowe's; thin ~4% operating margin leaves no buffer in a downturn.
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — v5 final run (2026-10-16)
Growth sanity check: the engine's g_base is 1.00% (blend −1.04% from rev CAGR 5y −2.47%, rev CAGR 3y −3.42%, latest rev YoY +0.39%, and an OE/share CAGR 2y of +47.68% that is a trough artifact off FY2024 — plus the +2.04pp buyback adjustment). A 1% base start sits right on the evidence: FY2026 revenue +0.4% YoY, Q2 FY27 comparable sales +4.1%, and FY27 guidance (raised 2026-08-27) for comparable sales +1.9% to +3.0% and revenue $42.3–42.8B. Default offsets were kept (−12/−5/0/+5/+12pp). The super-bull start of 13% is deliberately NOT benchmarked to the TTM OE/share jump — that jump is a working-capital swing off a weak prior H1, not a repeatable growth rate; against revenue-side prints (guided comps ≤3%), 13% OE growth already assumes comps at/above guide plus ads/marketplace margin mix and buybacks, so it gets only 8% probability. Probabilities were skewed bear-side (15/30/30/17/8 vs the 10/25/30/25/10 default) for the TTM-base reason above and OE_VOLATILE. OE multipliers are the defaults. Price $94.18.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −10.0% | 0.75 | CE replacement cycle rolls over; TTM cash swing reverses; price war with Amazon/Walmart | $28.99 | 5.96% |
| Bear | 30% | −4.0% | 0.90 | Comps go flat-to-negative after the AI-PC/Windows refresh fades; margins stay ~4% | $44.07 | 8.13% |
| Base | 30% | 1.0% | 1.00 | Guided path: low-single-digit comps, services/ads/marketplace mix offsets product pressure | $59.48 | 10.35% |
| Bull | 17% | 6.0% | 1.10 | Refresh cycle extends, emerging categories (AI glasses etc.) keep compounding, ads scale | $79.27 | 13.07% |
| Super bull | 8% | 13.0% | 1.25 | Sustained share recapture + margin expansion beyond the historical ~4% ceiling | $117.27 | 17.79% |

- **Probability-weighted: IV@15% $58.27 (−38.13% vs price), IV@12% $76.56, IV@10% $96.88, weighted IRR 10.22%, base-case IRR 10.35%**
- **Tier by numbers: C.** Diagnostics: OE yield 8.16%, terminal value 17.67% of IV@15%, scenario spread 4.05x, 8.5 months since FY end.
- Only the super-bull scenario (8% probability) values the shares above the $94.18 price at a 15% discount rate; even the bull case IV@15% ($79.27) sits below price.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 8.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 FY27 (2026-08-01), quoted above, with the working-capital caveat handled via bear-skewed probabilities.
- **BUYBACK_TAILWIND** (share count shrinking 2.0%/yr): already credited via the +2.04pp growth adjustment in the blend; not double-counted. Note the tailwind is currently small in cash terms — management expects only ~$300M of FY27 repurchases and the TTM diluted count is flat at 212.1M — which is already reflected in using the engine's adjustment as-is.
- **OE_VOLATILE** (OE/share range over the last 5 yrs spans >3x): real cyclicality — pandemic-era boom, FY2024 trough, recovery since. Handled by the normalized-median cross-check (method range below) and by putting 45% probability on bear-or-worse.
- **NI_OCF_DIVERGENCE** (2025, 2026): benign and identified — in both years net income sits BELOW operating cash flow (FY2025: NI $927M vs OCF $2,098M; FY2026: NI $1,069M vs OCF $1,962M), and the gap is the size of the non-cash addbacks the filings report (D&A $866M / $831M and SBC $139M / $139M in FY2025 / FY2026). There is no one-off gain inflating net income; if anything the NI-based maintenance OE ($749M in FY2026) is the more conservative series, and it is reported alongside the base above. No tax-deposit or impairment one-off was found in the named years.
- **WIDE_SCENARIO_SPREAD** (4.05x): real — the range is the TTM-base question (does the H1 cash level hold?) plus cycle timing. Confidence is capped at medium, and the verdict is sized to the conservative end.

## My thoughts / overlay
- **Method range is the honest headline:** on the engine's normalized median base ($5.28/share, preliminary run), the weighted IRR was 8.32% with IV@15% $43.64 — Tier D. On the TTM base actually used ($7.69/share), it is 10.22% / $58.27 — Tier C. Both methods agree on the decision-relevant point: at $94.18 the stock does not clear a 15% hurdle under any defensible base; the disagreement is only about how far short it falls.
- Quality is fine, price is the problem: positive OE in 5/5 years, modest funded debt, a 22-year dividend-raising record and guided FY27 adjusted EPS of $6.70–$6.90 (raised 2026-08-27) describe a well-run, mature retailer — being paid for at a price that needs the refresh cycle, ads, and marketplace all to deliver at once.
- Watch items: the CEO transition (Corie Barry's final quarter was Q2 FY27; Jason Bonfig takes over 2026-10-31) lands right into the holiday quarter; computing ASPs are being lifted by memory costs while units fall (noted on the Q2 call), which can borrow demand forward; the $34M of Q2 tariff refunds flattered gross margin and is non-recurring in nature.
- Margin of safety: the weighted IV@15% of $58.27 is the price that clears exactly 15% on the weighted path — the current $94.18 price sits far above it, and even the bull-case IV@15% ($79.27) is below the price. There is no margin of safety here at any scenario except super bull.

## Final verdict
- **Final tier: C** (weighted IRR 10.22% on the TTM base; method range D–C across the median and TTM bases — either way, well short of the 15% hurdle)
- Confidence: **Medium** (clean filing data, no data gaps; capped by the 4.05x scenario spread and the TTM base's working-capital content)
- One-liner: Durable #1 specialty CE retailer, moat 4/10, quality cash generation — but at $94.18 it prices in a recovery the numbers don't pay for: weighted IRR 10.2%, IV@15% $58.27; it clears 15% only at ~$58 or below.
