# USFD — US Foods Holding Corp.
v5 run, 2026-10-15. In scope: market cap $23.338B at $101.47 (nasdaq_quote_api, key_numbers.md).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed. Business/guidance facts are from web search results cited in words.

## What it is
The second-largest U.S. broadline foodservice distributor (~10% national share vs Sysco at ~17-18% per search results), delivering food and supplies to independent restaurants, chains, healthcare, hospitality and other institutions. Thin-margin, volume-and-route-density business: Q2 2026 net sales rose 4.5% to $10.5 billion, total case volume grew 1.9%, independent restaurant cases grew 5.1%, chain cases fell 1.5%, and adjusted EBITDA margin was 5.7% (search results, Q2 2026 earnings reports).

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,369,000,000; capex $410,000,000; SBC $83,000,000 (always a real cost).
- **Conservative owner's earnings FY2025: $876,000,000 = $3.81/share** (key_numbers.md: latest FY OE/share $3.81, latest FY OE total $876.0M)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $815,000,000 for FY2025 (financials_history.csv) — same ballpark as the conservative figure.
- OE positive 5 of the last 5 fiscal years (key_numbers.md).
- Balance sheet: key_numbers.md shows net debt as — (the engine's net_debt_latest is null, so no computed net-debt figure is quoted here). Search results from the Q2 2026 call report net leverage of 2.6x at quarter-end, within the company's stated 2x-3x target range, with no long-term maturities until 2028 — manageable, not a verdict driver either way.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,369,000,000 − prior YTD $725,000,000 + current YTD $725,000,000 = **TTM $1,369,000,000**
- Capex: FY $410,000,000 − prior YTD $161,000,000 + current YTD $174,000,000 = **TTM $423,000,000**
- SBC: FY $83,000,000 − prior YTD $45,000,000 + current YTD $54,000,000 = **TTM $92,000,000**
- Shares (current-YTD weighted diluted): **222,000,000**
- **TTM OE total $854,000,000 → base OE/share $3.85** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $3.16/share. The TTM base was used because FY ended 9.6 months ago (STALE_FY) and the TTM figure sits close to the latest FY figure ($3.81/share), so it updates the base without importing a distorted year. The preliminary run on the median base gave weighted IRR 6.91% and weighted IV@15% $33.88 — also Tier D, so the base choice does not change the verdict.

## Moat: 4/10 — weak to moderate
Justification: scale and route density as the #2 national distributor give real but limited advantages; the larger leader holds the cost edge, switching costs are low, and margins are thin.
- FOR: #2 U.S. broadline distributor, ~10% national share; dense national distribution and route network; diversified mix across independents, healthcare, hospitality and chains; private label and value-added services (Pronto, MenuIQ); scale purchasing and per-case operating leverage.
- AGAINST: Sysco is larger (~17-18% share) with a cost advantage; no demonstrated moat vs peers; low switching costs — customers multi-source; thin margins — Q2 2026 adjusted EBITDA margin 5.7%; labor, fuel and food-inflation pass-through risk; restaurant cyclicality — chain case volume fell 1.5% in Q2 2026.
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Growth sanity check (required): the engine's blended growth is 7.95% → g_base 7.36%. Components (key_numbers.md): rev CAGR 5y 11.53%, rev CAGR 3y 5.02%, latest rev YoY 4.08%, OE/share CAGR 2y 10.88%, share count CAGR 0.59% (growth adj -0.59%). The base start of 7.4% sits above revenue growth (~4-5% in FY2025, Q2 2026, and the reaffirmed FY2026 sales guidance of 4-6% from search results) because OE/share has grown faster than revenue on margin expansion and buybacks (OE/share CAGR 2y 10.88%). Bull start 12.4% is above that CAGR but below the guided adjusted EPS growth range; super-bull start 19.4% is justified only as a 10%-probability upside case because FY2026 adjusted EPS guidance is +18% to +24% (search results, reaffirmed at Q2) — it is not a central expectation. Default offsets (-12/-5/0/+5/+12pp) and OE multipliers (0.75/0.90/1.00/1.10/1.25) and default probabilities 10/25/30/25/10 were kept. Price $101.47.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -4.6% | 0.75 | Restaurant downturn, chain weakness spreads, fuel/labor squeeze thin margins | $17.93 | 4.56% |
| Bear | 25% | 2.4% | 0.90 | Low-single-digit sales growth, no further margin expansion | $28.24 | 5.97% |
| Base | 30% | 7.4% | 1.00 | Guided sales growth plus margin/buyback-driven OE/share growth decays over the CAP | $37.98 | 7.32% |
| Bull | 25% | 12.4% | 1.10 | Share gains in independents/healthcare and per-case leverage continue | $50.44 | 8.98% |
| Super bull | 10% | 19.4% | 1.25 | Guided adjusted EPS growth range is delivered and sustained | $74.23 | 11.95% |

- **Probability-weighted: IV@15% $40.28 (-60.3% vs price), IV@12% $53.76, IV@10% $68.82, weighted IRR 7.66%, base-case IRR 7.32%**
- **Tier by numbers: D.** Diagnostics (key_numbers.md): OE yield 3.79%, terminal value 19.2% of IV@15%, scenario spread 4.14x, 9.6 months since FY end.
- Even the super-bull scenario (IV@15% $74.23, IRR 11.95%) sits below the $101.47 price — no scenario clears the 15% hurdle at this price.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.6 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above.
- **OE_VOLATILE** (OE/share range over the last 5 years spans >3x): real and historical — the early years in the filed history are COVID-depressed (foodservice shutdowns), and the span is a recovery arc, not current instability. Recent bases cluster tightly: normalized median $3.16, latest FY $3.81, TTM $3.85. Handled by using the TTM base and keeping 35% probability on bear-or-worse.
- **NI_OCF_DIVERGENCE** (2023, 2024, 2025): explained by non-cash addbacks, not a one-off gain. In FY2025, D&A was $462,000,000 and SBC was $83,000,000 (financials_history.csv) against net income of $676,000,000 and OCF of $1,369,000,000 — a capital-intensive distributor's OCF structurally runs well above net income because depreciation on its fleet/facilities is added back. The OCF-based conservative OE deducts full capex ($410,000,000 in FY2025), so the divergence does not inflate the base.
- **WIDE_SCENARIO_SPREAD** (4.14x): real — thin margins make OE sensitive to small volume/margin moves. Confidence is capped at medium, and the verdict is sized to the conservative end; note even the super-bull case fails the hurdle, so the spread does not rescue the price.

## My thoughts / overlay
- The method range does not span tiers: median-base preliminary run 6.91% weighted IRR (IV@15% $33.88) and TTM-base final run 7.66% (IV@15% $40.28) are both Tier D. The finding is valuation, not data: the market price embeds the guided high-teens adjusted EPS growth as a durable path, while this owner's-earnings screen — full capex and SBC deducted — values the same business at roughly $34-40 at a 15% discount.
- Quality is middling, not poor: OE positive 5/5 years, buybacks are active (search results: ~$500M repurchased year-to-date through Q2 2026), leverage reported at 2.6x, and independent-restaurant momentum is genuine. None of that closes a gap this wide.
- Risks to the short/underweight read: sustained margin expansion toward Sysco-like economics, accretive tuck-in M&A, or a re-rating on continued EPS beats could keep the premium in place for a long time.
- Margin of safety: there is none at $101.47 on these numbers — the price is 60.3% above the weighted IV@15%. The price that clears 15% on the weighted case is $40.28.

## Final verdict
- **Final tier: D** (weighted IRR 7.66% on the v5 final inputs; Tier D under both the TTM and median bases)
- Confidence: **Medium** (capped by WIDE_SCENARIO_SPREAD; the direction of the verdict is robust because even the super-bull scenario is below price)
- One-liner: Solid #2 foodservice distributor, moat 4/10, but priced for much more than its owner's earnings deliver — weighted IRR 7.66% at $101.47, does not clear 15%; hurdle-clearing price is the weighted IV@15% of $40.28.
