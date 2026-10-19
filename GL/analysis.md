# GL — Globe Life Inc.
Engine 5.4 run, 2026-10-17. In scope (market cap $13.928B at $168.77, nasdaq_quote_api).

All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv or fundamentals.json — none are recomputed.

## What it is
Life and supplemental health insurer (founded as Torchmark, renamed 2019) selling to underserved middle-income households through exclusive/captive agency channels — American Income Life (largest life channel), Liberty National, Family Heritage (supplemental health) — plus a direct-to-consumer channel and United American (Medicare Supplement). Q2 2026 (per search results summarizing the company's release): revenue $1.60B, up 6.7% year over year; net operating income $3.61/share, up 10%; net income $288M, $3.65/share, up 20%; total premiums up 7% (life +3%, health +16%); management raised 2026 net operating EPS guidance to $15.55–$15.95 and planned 2026 repurchases to $670–$700M.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,396,391,000; capex $142,484,000; SBC $53,355,000 (always a real cost); net income $1,161,238,000; revenue $5,994,318,000.
- **Conservative owner's earnings FY2025: $1,200,552,000 = $14.55/share** (base_oe_latest_per_share $14.547738459641414).
- Maintenance version FY2025 (NI + D&A − min(capex, D&A) − ΔNWC, from financials_history.csv): $1,161,238,000 — only ~3% below the conservative figure in FY2025, but the gap was much wider in FY2023–24 (see NI/OCF note under Thoughts): FY2023 OCF $1,482,425,000 vs net income $970,755,000; FY2024 OCF $1,402,440,000 vs net income $1,070,762,000. Reserve/float growth adds to insurer OCF in the annual history; the gap has narrowed as capex rose.
- OE positive 5 of the last 5 fiscal years. Net debt $2,480,745,000 (dcf_numbers.json, basis LongTermDebtNoncurrent+ShortTermBorrowings) — for an insurer this is a holding-company sliver: the real balance sheet is assets $30,813,692,000 against liabilities $24,839,113,000 (financials_history.csv FY2025), i.e. the investment portfolio against policy liabilities, not the corporate debt load.
- Capex has stepped up hard: $49,553,000 (FY2023) → $71,045,000 (FY2024) → $142,484,000 (FY2025), and TTM capex is $159,203,000 (ttm.json). The computed outputs do not identify the cause; if the step-up is permanent it is a real drag on OE, if it normalizes the TTM base below is conservative. The scenario multipliers span this rather than a hand adjustment.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,396,391,000 − prior YTD $739,813,000 + current YTD $735,000,000 = **TTM $1,391,578,000**
- Capex: FY $142,484,000 − prior YTD $24,687,000 + current YTD $41,406,000 = **TTM $159,203,000**
- SBC: FY $53,355,000 − prior YTD $26,062,000 + current YTD $30,577,000 = **TTM $57,870,000**
- Shares (current-YTD weighted diluted): **79,333,337**
- **TTM OE total $1,174,505,000 → base OE/share $14.80** (base_source: ttm_json; ttm.json ttm_oe_per_share $14.80468418969947)
- The engine's normalized base (median of last 3 FY OE/share) is $14.547738459641414/share — nearly identical to the TTM base, so the base choice is not the swing factor here (unlike most insurer runs). Cross-checks on earnings power: TTM net income is $1,212,199,000 (fundamentals.json TTM) — above TTM conservative OE, because TTM capex now exceeds the reserve/OCF uplift — and management's raised 2026 operating-EPS guidance ($15.55–$15.95, per search results) sits above both engine bases. The engine base is not obviously flattering; the softening below rests on the sector model fit, the annual-history float component, and how marginal the B is, not on the TTM base being above net income.

## Moat: 5/10 — moderate / narrow
Justification: a scaled, exclusive-agent distribution machine aimed at an underserved niche, with a recurring renewal-premium base and through-cycle ROE of 19.4% (FY2025), 20.2% (FY2024) and 21.6% (FY2023) per fundamentals.json — returns well above the cost of capital sustained over a cycle — against commodity life/supplemental-health products with no structural pricing power, a recruiting-dependent agent model under regulatory and short-seller attack, and earnings hostage to mortality/morbidity, rates and regulators' willingness to approve premium-rate increases.
- Evidence on returns: the `roic_proxy` series in fundamentals.json reads 15.8% (FY2022) and 15.8% (FY2023), with FY2021's 24.3% and FY2020's 7.0% distorted by AOCI swings in the equity denominator (equity fell to $2,003,808,000 in FY2021) — for an insurer the cleaner series is ROE, 19–22% for FY2023–25 above. Gross margin (fundamentals.json) ran 19.0% (FY2020), 23.8% (FY2021), 22.6% (FY2022), 23.1% (FY2023); FY2024–25 gross margin is not in the computed outputs (operating income not tagged for those years), so no level/trend is claimed for them.
- FOR: Exclusive distribution scale — American Income, Liberty National and Family Heritage agents sell only Globe Life products into an underserved middle-income niche larger rivals underserve; specialized policy design and underwriting experience in that niche.
- FOR: Recurring renewal-premium base — in-force policies persist and compound premium revenue (revenue CAGR 4.8% over 5 years on filed history) with disciplined underwriting margins.
- FOR: Through-cycle profitability and capital return — OE positive 5 of last 5 FY; ROE ~19–22% FY2023–25; DPS TTM $1.20 with 16 consecutive growth years and no cut since 2009, buybacks TTM $881,315,000 (fundamentals.json), diluted shares shrinking 5.9%/yr.
- AGAINST: Commodity products, no structural pricing power — life and supplemental health cover is price-competed and rate increases (e.g. Medicare Supplement) need regulatory approval.
- AGAINST: Agent-model conduct and regulatory overhang — the 2024 Fuzzy Panda short report alleged widespread fraud and a kickback scheme at American Income Life, and the company disclosed a DOJ probe into AIL sales practices (per search results); recruiting-led growth is the model's engine and its biggest fragility.
- AGAINST: Distribution disruption — management said in Q2 2026 that AI-driven search is eroding the paid-search leads the direct-to-consumer channel depends on; agent counts at American Income fell year over year in Q2 2026 even as premiums grew.
- AGAINST: Hostage to assumptions and markets — mortality/morbidity experience, the yield curve and reserve assumption updates move earnings outside management control; capital rules cap growth and returns.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — engine 5.4 final run (2026-10-17, --moat 5 --ttm, probs 0.10/0.25/0.30/0.25/0.10, default offsets/mults)
**Growth sanity check (mandatory):** the engine's blended growth is 9.21% — built from revenue components (5-yr CAGR 4.82%, 3-yr CAGR 4.67%, latest YoY 3.74%) each credited +5.00pp for the buyback (share CAGR −5.88%/yr, capped adjustment), with OE/share CAGR 2y at −0.01% entering unadjusted. So the 9.21% start is a *per-share* number: ~4–5% business growth plus a ~5% shrinking denominator. Against actual prints: TTM revenue grew 5.24% year over year (fundamentals.json TTM) and Q2 2026 revenue grew 6.7% with net operating EPS up 10% and guidance raised (search results) — the base start of 9.21% sits between the revenue prints and the per-share operating-EPS print, which is where a buyback-credited per-share start should sit; it is not below the latest per-share print by enough to need a separate written reason beyond this composition. Bear 4.21% = business growth stalls and the buyback credit fades. Bull 14.21% requires premium growth at the top of the recent range plus the full buyback pace sustained — above any recent revenue print, justified only as a per-share figure at 25% weight. Super-bull 21.21% is the stretch case (health-premium momentum +16% in Q2 compounding group-wide plus maximum repurchases) at 10% weight. Super-bear −2.79% is the conduct/regulatory accident case. No offsets were recalibrated: the blend's composition is transparent and the starts bracket the prints honestly.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -2.8% | 0.75 | Regulatory/conduct accident at AIL; lapses rise, growth stops | $72.99 | 7.69% |
| Bear | 25% | 4.2% | 0.90 | Premium growth at filed-history pace, buyback credit fades, capex step-up sticks | $117.30 | 11.24% |
| Base | 30% | 9.2% | 1.00 | ~4–5% premium growth plus ~5%/yr share shrink, fading over the CAP | $160.29 | 14.41% |
| Bull | 25% | 14.2% | 1.10 | Health momentum spreads, agent counts recover, full buyback pace | $216.44 | 18.11% |
| Super bull | 10% | 21.2% | 1.25 | Category compounding at Q2 health pace group-wide | $326.50 | 24.19% |

- **Probability-weighted: IV@15% $171.47 (+1.6% vs price $168.77), IV@12% $230.78, IV@10% $297.27, weighted IRR 15.18%, base-case IRR 14.41%**
- **Tier by numbers: B.** Diagnostics (dcf_numbers.json): OE yield 8.77%, terminal value 20.0% of IV@15%, scenario spread 4.47x, net debt 2.03x normalized OE, 9.5 months since FY end.
- Hurdle prices (dcf_numbers.json): clears 15% at $171.47, 20% at $118.63, 25% at $89.88.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above; the TTM and median bases nearly coincide ($14.80 vs $14.55), so staleness is not driving the verdict.
- **BUYBACK_TAILWIND** (share count shrinking 5.9%/yr): already credited via the +5.00pp growth adjustment in the blend (capped); not double-counted. It is also the single biggest support under the growth start — if repurchases slow (planned $670–$700M for 2026, per search results, is roughly the recent pace), per-share growth falls toward the ~4–5% revenue pace and the bear case is the right anchor.
- **CASH_INCLUDES_RESTRICTED**: the only cash tag filed for FY2025 is the combined cash + restricted-cash total ($144,704,000, financials_history.csv) with no separate restricted tag, so the engine's $2,480,745,000 net debt is understated by the restricted amount. Checked against the balance sheet: cash is small next to both the debt figure and the $30.8B asset base, so the understatement cannot change the net-debt picture; and for an insurer the corporate net-debt figure is a holding-company sliver anyway (see Owner's earnings). No HIGH_NET_DEBT conclusion is relied on.
- **SECTOR_MODEL_MISMATCH**: Finance/life insurance — the OE/capex DCF fits insurers poorly; confidence is low, and the final tier is softened one notch (see verdict), per Andrew's standing insurer rule (2026-10-15; same treatment as PFG/HIG/ACGL/WRB/AIZ).
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.47x super-bear): real — the range runs from a conduct accident to a compounding case. Confidence is capped at low, and the verdict is sized to the bear end.
- **TIER_BAND** (bear tier C at 11.24% vs bull tier B at 18.11%): the verdict spans tiers; sized to the bear end — one of the two reasons (with the sector mismatch) the final tier is C, not the marginal B the weighted number prints.

## Data notes (enrichment, non-blocking)
- segments.py completed but returned no dimensioned segment/product/geography facts for the tracked concepts (segments.json tables empty, with that warning) — no segment breakdown is claimed anywhere in this file; the channel split cited in research comes from search results summarizing company reporting, not from segments.json. fundamentals, prices, statements, profile/street and reprice all completed; profile.json carries one warning (no employee headcount sentence found in the 10-K).

## My thoughts / overlay
- The honest headline is how marginal this is: weighted IRR 15.18% is 0.18pp over the 15% hurdle, weighted IV@15% is 1.6% over the price, and the base case alone (14.41%) does not clear. Any defensible tweak — a slower buyback, capex staying at the new level with slower premium growth, a conduct charge — puts it in C territory, which is where the bear case already sits.
- Method range: on the preliminary median-base run the weighted IRR was 14.98% (Tier C, IV@15% $168.50); on the TTM base it is 15.18% (Tier B, IV@15% $171.47). The two defensible bases straddle the hurdle almost exactly — the method range is C to B, and that straddle is itself the finding.
- Quality is real but not wide-moated: ROE ~19–22% through FY2023–25, 16 straight years of dividend growth, OE positive 5/5, and a niche distribution machine — paid for at $168.77, essentially at the weighted IV@15% of $171.47, which leaves no margin against the bear IV@15% of $117.30.
- Red flags to monitor: the DOJ probe and AIL conduct litigation overhang from the 2024 short reports; American Income agent-count trend (down year over year in Q2 2026); whether the capex step-up ($49.6M → $142.5M in two years) keeps rising; DTC lead economics as AI search displaces paid search; health-claims pressure noted in Q2 2026.

## Final verdict
- **Final tier: C — softened one notch from B by tier_override** (weighted IRR 15.18% on the final inputs; method range C to B across the median and TTM bases)
- Confidence: **Low** (SECTOR_MODEL_MISMATCH on a life insurer plus WIDE_SCENARIO_SPREAD)
- One-liner: Steady niche life/supplemental-health insurer with exclusive-agent distribution, moat 5/10 — B by numbers on a TTM base (15.2% weighted, IV@15% $171 vs $169) but that B is within noise of the hurdle, the bear case is C, and the OCF base carries the insurer float/reserve component, so softened to C at low confidence; it clears 15% at ~$171 on engine numbers and with a margin of safety only near the bear IV of ~$117.
