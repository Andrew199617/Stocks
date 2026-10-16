# FOX — Fox Corporation
v5 run, 2026-10-15. In scope (market cap $24.958B at $56.85, nasdaq_quote_api). All figures below are copied from dcf_numbers.json, key_numbers.md (after make_score), or financials_history.csv — none are recomputed. Deal terms are from cited web search results on the proposed Roku transaction.

## What it is
US media focused on live content since the 2019 Disney separation: Cable Network Programming (FOX News — the top-rated US cable news network — FOX Business, FS1/FS2), Television (FOX broadcast network and owned stations), Tubi (leading free ad-supported streaming service), FOX Sports (NFL and MLB rights, NFL deal running through 2033 per search results), and the recently launched FOX One direct-to-consumer service. Revenue is distribution/affiliate fees plus advertising — the two categories most exposed to cord-cutting and to the ad/political cycle, respectively. A transformational proposed acquisition of Roku (see Thoughts) is pending: DOJ issued a Second Request on 2026-09-08, the companies expect a close in the first half of 2027 subject to approvals, and the consideration reported in search results is $96.00 in cash plus 0.9693 FOX Class A shares per Roku share, at about $22.0B enterprise value.

## Owner's earnings
**FY2026 (10-K via EDGAR, period ended 2026-06-30, from financials_history.csv):** operating cash flow $1,970,000,000; capex $502,000,000 (tag PaymentsToAcquirePropertyPlantAndEquipment); SBC $132,000,000 (tag ShareBasedCompensation, always a real cost).
- **Conservative owner's earnings FY2026: $1,336,000,000** (financials_history.csv oe_conservative; base_oe_total_latest_fy in dcf_numbers.json).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,473,000,000 — same ballpark as the conservative figure, which raises confidence in the level, if not in its stability.
- OE positive 5 of the last 5 fiscal years.
- **Volatility is the story in the base:** conservative OE totals in financials_history.csv were $1,405,000,000 in FY2024, $2,858,000,000 in FY2025, and $1,336,000,000 in FY2026. The FY2025 OCF spike ($3,324,000,000 vs $1,840,000,000 in FY2024 and $1,970,000,000 in FY2026) reflects sports-rights payment timing and event mix, not a step-change in earning power.
- **Base used = normalized base, median of last 3 FY OE/share = $3.04/share** (base_oe_normalized_per_share $3.0432801822323463, base_source median_of_last_3_fy_oe_per_share). It equals the latest-FY figure only because the latest year is the median of the three; it is deliberately NOT the FY2025 spike year. No STALE_FY flag (3.5 months since FY end), so no TTM override was needed or used.
- Net debt (engine, dcf_numbers.json): $6,606,000,000 — see HIGH_NET_DEBT under Flags. Note the engine's cash tag was null in this pull, so this figure is treated as the engine's reported net debt and not restated here.

## Moat: 5/10 — moderate/narrow, real but structurally eroding
Justification: FOX News' loyal, #1-rated cable-news audience and long-dated live sports rights give genuine pricing power in affiliate and advertising negotiations, and Tubi is a scaled free-streaming asset; against that, the distribution base (the cable bundle) shrinks secularly, sports rights are rented at auction against far deeper-pocketed tech bidders, and Fox owns no scaled subscription streaming surface — the moat is a strong position inside a declining channel.
- FOR: FOX News is the top-rated cable network with a loyal audience that supports affiliate-fee and ad pricing power
- FOR: Long-dated live sports rights (NFL through 2033) — appointment viewing advertisers cannot replicate elsewhere
- FOR: Tubi — scaled free ad-supported streaming that monetizes cord-cutters instead of only losing them
- FOR: Owned broadcast stations capture political-cycle advertising windfalls in election years
- AGAINST: Cord-cutting shrinks the cable bundle and the affiliate-fee base every year
- AGAINST: Sports rights are rented, not owned — renewal inflation against Amazon/Apple/Google-scale bidders compresses margins
- AGAINST: Advertising cyclicality plus political-cycle lumpiness (even-year spikes, odd-year air pockets)
- AGAINST: No scaled subscription streaming business; FOX One is new and unproven
- AGAINST: Pending Roku acquisition adds leverage and share issuance and carries antitrust (DOJ Second Request) and integration risk
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Growth recalibration (written reason): the engine's g_base is 9.89%, built from a blended growth of 4.89% (rev CAGR 5y 5.82%, rev CAGR 3y 4.72%, latest rev YoY 5.07%, OE/share CAGR 2y 1.97%) plus the maximum +5.00pp share-count adjustment for a share count shrinking 6.14%/yr. That buyback pace is not a safe forward assumption: (1) the recent prints — revenue growth of about 5% even in a FIFA Men's World Cup year (Q4 FY2026 revenue rose 28% YoY on the World Cup broadcast and Tubi growth, per the earnings release; full-year revenue rose 5.07%) and OE/share CAGR of only 1.97% — do not support a 9.89% OE/share growth start; (2) the pending Roku consideration is partly in FOX shares, which reverses the shrinkage the +5pp credits. Scenario starts were therefore set via offsets (−0.12 / −0.09 / −0.05 / −0.02 / +0.01 vs g_base) to −2.11% / 0.89% / 4.89% / 7.89% / 10.89% — the base case start equals the engine's blended growth with no buyback credit. Even the super-bull start (10.89%) sits near, not below, the observed ~5% revenue prints once the World Cup one-off is noted: it requires Tubi/FOX One growth plus a political-cycle year, and it is weighted at only 10%. Probabilities were skewed bearish (15/30/30/15/10 vs the 10/25/30/25/10 default) for the leverage, the Roku binary, and the FY2027 comparison against a World Cup-boosted FY2026. OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $56.85.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -2.11% | 0.75 | Cord-cutting accelerates, sports costs bite, Roku deal adds debt then disappoints | $15.44 | 5.74% |
| Bear | 30% | 0.89% | 0.90 | Affiliate erosion roughly offsets Tubi/political gains; OE stays depressed | $21.00 | 7.06% |
| Base | 30% | 4.89% | 1.00 | Blended historical growth, no buyback credit, news/sports pricing holds | $27.57 | 8.65% |
| Bull | 15% | 7.89% | 1.10 | Tubi and FOX One scale, political cycle delivers, affiliate pricing holds | $34.33 | 10.23% |
| Super bull | 10% | 10.89% | 1.25 | Roku closes cleanly and synergizes; digital growth re-rates the mix | $44.15 | 12.39% |

- **Probability-weighted: IV@15% $26.45, IV@12% $35.02, IV@10% $44.56, weighted IRR 8.40%, base-case IRR 8.65%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 5.35%, terminal value 18.40% of IV@15%, scenario spread 2.86x, net debt 4.94x normalized OE, 3.5 months since FY end.
- No scenario — not even super bull at a 1.25x OE multiplier — clears the 15% hurdle at $56.85. The shortfall is a price/base problem, not a scenario-construction problem.

## Flags — every fragility flag resolved
- **BUYBACK_TAILWIND** (share count shrinking 6.1%/yr — already credited via the growth adjustment): resolved by removing the credit — the final scenario offsets strip the +5.00pp share-count adjustment out of every scenario start (see growth recalibration above), because the shrinkage is about to be reversed by share issuance for the Roku acquisition and cannot be extrapolated at 6.1%/yr alongside 4.94x leverage.
- **HIGH_NET_DEBT** (net debt is 4.9x normalized OE): net debt $6,606,000,000 is 4.94x normalized OE (diagnostics). Folded into the verdict explicitly: bearish-skewed probabilities (45% on bear-or-worse), the super-bear OE multiplier of 0.75, and confidence low. The pending Roku transaction would add substantial further debt per search-result reporting, which is a reason to size to the conservative end, not a figure restated here beyond the engine's number.
- **WIDE_SCENARIO_SPREAD** (preliminary run: super-bull IV 4.5x super-bear IV): after the growth recalibration the final spread is 2.86x. The uncertainty is still real (a binary acquisition, a World Cup-boosted comparison year, volatile OCF) — confidence is set to low, below the medium cap this flag would impose.

## My thoughts / overlay
- Quality vs price are separate questions. The assets (FOX News, NFL rights, Tubi, stations) generate positive OE every year and the maintenance OE definition corroborates the conservative one. But at $56.85 the buyer pays for a base OE of $3.04/share — a 5.35% OE yield — in a business whose revenue grows about 5%, whose OE total halved from FY2025 to FY2026 on rights-payment timing, and whose share-count tailwind is about to reverse.
- Method range: the preliminary default run (full buyback credit, default probabilities, base growth start 9.89%) printed weighted IRR 10.77% / Tier C with weighted IV@15% $36.25. The final calibrated run prints 8.40% / Tier D. The defensible range is therefore C-to-D, and the verdict is sized to the conservative (D) end because the preliminary run's two most aggressive assumptions — perpetual 6.1%/yr shrinkage and a 9.89% growth start against 5% prints — are the ones the evidence contradicts.
- The Roku deal is the dominant overlay: if it closes on the reported terms, per-share economics, leverage, and the growth mix all change at once, in either direction; if it is blocked, FOX keeps its buyback but also its declining-bundle exposure. Either branch argues against paying a growth price today.
- Hurdle-clearing price: the weighted IV@15% is $26.45 — the stock would need to trade at or below about $26.45 to clear Andrew's 15% hurdle on these inputs, less than half the $56.85 price (upside_at_15 −53.47%).

## Final verdict
- **Final tier: D** (weighted IRR 8.40% on the v5 final inputs; method range C to D, sized to the conservative end)
- Confidence: **Low** (binary pending acquisition under DOJ review, 4.94x net debt to normalized OE, OE totals that swung from $2,858,000,000 to $1,336,000,000 in a year)
- One-liner: Durable live news/sports assets, moat 5/10, but at $56.85 on a $3.04 normalized OE base it clears only 8.4% weighted — it needs ~$26.45 to clear 15%, and the Roku deal reverses the buyback tailwind the growth math was crediting.
