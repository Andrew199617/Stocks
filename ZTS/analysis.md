# ZTS — Zoetis Inc.
v5 run, 2026-10-14. In scope (market cap $33.587B at $75.675, nasdaq_quote_api).

All figures below are copied from dcf_numbers.json, ttm.py output (ttm.json), or financials_history.csv — none are recomputed.

## What it is
The world's largest pure-play animal health company (spun out of Pfizer in 2013): prescription medicines, vaccines, parasiticides, dermatology and osteoarthritis pain products, plus diagnostics, for companion animals (~two-thirds of revenue) and livestock. Key franchises: Simparica (parasiticides), Apoquel/Cytopoint (dermatology), Librela/Solensia (monoclonal-antibody OA pain). FY2025 revenue $9,467,000,000, net income $2,673,000,000.

The story in 2026 is a reset, not a collapse: Q2 2026 revenue was flat year on year ($2.47B per the earnings release summary), with global Companion Animal down 6% organically and U.S. Companion Animal down 11%; Key Dermatology fell 16% as Elanco's Zenrelia takes Apoquel share, Simparica was flat globally (international growth offsetting U.S. weakness against a lower-priced, broader-label competitor), and FDA safety-label warnings on Librela have suppressed prescribing, with securities litigation now alleging the headwinds were downplayed. Management cut FY2026 guidance in August 2026 to revenue $9.120–$9.320B (organic operational growth −3% to −1%) and adjusted EPS $6.15–$6.25, from $9.68–$9.96B / $6.85–$7.00 previously, citing falling veterinary clinic visits, pet-owner price sensitivity, and no assumed near-term market stabilization. Livestock and Diagnostics and the international business remain resilient offsets. The stock is down roughly half from its 52-week high ($148.30 per Finnhub data in search results) — the question is whether $75.675 already pays for the reset. On owner's earnings, it does not yet.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $2,904,000,000; capex $621,000,000 (tag PaymentsToAcquirePropertyPlantAndEquipment); SBC $83,000,000 (always a real cost, though small here — ~3% of OCF, no dilution problem; share count is shrinking).
- **Conservative owner's earnings FY2025: $2,200,000,000 = $4.96/share** (latest FY OE/share in dcf_numbers.json).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $2,064,000,000 — same ballpark, which raises confidence in the base.
- OE positive 5 of the last 5 fiscal years. Net debt $9,042,000,000 (see HIGH_NET_DEBT below). Shares have fallen steadily (498,225,000 in 2016 to 443,835,000 in FY2025, −1.92%/yr share CAGR) on persistent buybacks.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $2,904,000,000 − prior YTD $1,120,000,000 + current YTD $1,056,000,000 = **TTM $2,840,000,000**
- Capex: FY $621,000,000 − prior YTD $324,000,000 + current YTD $227,000,000 = **TTM $524,000,000**
- SBC: FY $83,000,000 − prior YTD $39,000,000 + current YTD $51,000,000 = **TTM $95,000,000**
- Shares (current-YTD weighted diluted, per ttm.py's stated basis): **420,100,000**
- **TTM OE total $2,221,000,000 → base OE/share $5.29** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $4.89/share and the latest FY is $4.96/share; the TTM base was used because FY2025 ended 9.4 months ago (STALE_FY) and the TTM is the most current filing-derived figure.
- Honesty caveat on the TTM base: TTM OE *total* ($2,221,000,000) is essentially flat vs FY2025 ($2,200,000,000) — the per-share step-up to $5.29 is buyback arithmetic (the TTM denominator is the H1 2026 YTD share count of 420,100,000, sharply below FY2025's 443,835,000 after heavy repurchases), not operating growth. The scenarios below therefore start growth from a near-zero operating base, not from the per-share optics.

## Moat: 7/10 — strong, but visibly eroding
Justification: Still the scaled global leader at roughly double its nearest competitor's companion-animal share, with brands, vet-channel lock-in and a first-mover monoclonal-antibody platform — but 2026 is the first year the erosion forces are taking measurable share in two core franchises at once, which caps the score below the 8–9 this business would have earned three years ago.
- FOR: Global scale and distribution — ~20%+ global animal-health share, roughly double the nearest rival in companion animal; portfolio breadth no single-product rival matches
- FOR: Prescription brands with vet habit and switching friction (Simparica Trio, Apoquel/Cytopoint, Librela/Solensia); Zoetis mAbs held ~73% of the 2024 veterinary mAb market per search-sourced market research
- FOR: Diversification as a hedge — livestock + diagnostics + international kept growing while U.S. companion fell 11% in Q2 2026
- FOR: Proven economics through the cycle — OE positive 5/5 years, high operating margins (~37% in Q2 2026 per earnings coverage), R&D pipeline management guides to 12+ potential blockbusters
- AGAINST: Dermatology share loss is happening now — Apoquel/Cytopoint facing Elanco Zenrelia and promotional competition (Key Dermatology −16% in Q2 2026)
- AGAINST: Parasiticides under price attack — a lower-priced competitor with broader indications is eroding Simparica Trio in a shrinking market; growth is being redistributed, not expanded
- AGAINST: Librela safety overhang — FDA label warnings and a "Dear Veterinarian" letter suppressed the OA franchise that was supposed to be the next growth leg; related securities litigation is pending
- AGAINST: Demand-side erosion — U.S. vet visits in a multi-year decline after years of price increases outpacing inflation; pet owners are now price-sensitive, which directly attacks the pricing-power pillar
- AGAINST: Generic erosion of legacy livestock/companion products (Draxxin, Rimadyl and others already hit in prior years)
- A 7 gives CAP = 11.1 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 11.1 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Growth recalibration (written reason): the engine's g_base is 8.25% (blend 6.33% + 1.92pp buyback adjustment), but its components are backward-looking — 5-yr revenue CAGR 7.24%, 3-yr 5.42%, and an OE/share CAGR (2y) of 21.14% that is an artifact of the depressed 2023 OE year plus buybacks. Actual current prints are far lower: latest FY revenue YoY +2.28%, Q2 2026 revenue flat (−1% organic), and FY2026 guidance is *negative* (organic −3% to −1%). Starting scenarios at the engine defaults (base 8.25%, bull 13.25%, super bull 20.25%) would price a recovery that has not started. Offsets were therefore recalibrated to starts of −5 / 0 / **4** / 9 / 14%: the 4% base start is revenue recovering to roughly the ~5% long-run animal-health market growth rate, expressed per share with buyback help, after the 2026 reset year; even that requires stabilization management says it is not yet seeing. Probabilities were skewed bearish vs defaults (15/30/30/15/10, 45% on bear-or-worse) because the guidance cut was driven by share loss, not just macro. OE multipliers kept at defaults 0.75/0.90/1.00/1.10/1.25 (rebate/promotion pressure is the bear-case margin mechanism). Price $75.675, TTM base $5.29/share.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −5.0% | 0.75 | Zenrelia + parasiticide rival keep taking share; Librela fallout deepens; vet visits keep falling | $22.89 | 5.87% |
| Bear | 30% | 0.0% | 0.90 | 2026 reset becomes the run-rate: flat OE, rebates defend share at margin cost | $34.68 | 8.09% |
| Base | 30% | 4.0% | 1.00 | Reset year, then recovery to market growth; intl/livestock/diagnostics carry the mix | $46.53 | 10.26% |
| Bull | 15% | 9.0% | 1.10 | Share stabilizes, clinic traffic normalizes, pipeline blockbusters land | $64.86 | 13.35% |
| Super bull | 10% | 14.0% | 1.25 | Full moat reassertion — historical outperformance vs the market resumes | $93.48 | 17.49% |

- **Probability-weighted: IV@15% $46.87 (−38.1% vs price), IV@12% $62.33, IV@10% $79.60, weighted IRR 10.38%, base-case IRR 10.26%**
- **Tier by numbers: C.** Diagnostics (dcf_numbers.json): OE yield 6.99%, terminal value 18.90% of IV@15%, scenario spread 4.08x, net debt 3.85x normalized OE, 9.43 months since FY end.
- Sanity check vs prints: every scenario start was set *from* the prints (guided −3% to −1% organic for 2026, flat Q2) rather than from the engine blend — no start, including super bull at 14%, assumes more than the company's pre-2025 delivery (revenue CAGR 7.24% over 5 years with faster OE/share growth on buybacks). The preliminary default run (median base $4.89, default offsets) gave weighted IRR 11.70% / IV@15% $54.45 — also Tier C; the final run is lower because the growth recalibration outweighs the higher TTM base.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.43 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, with all inputs quoted above. The TTM confirms stagnation, not growth: TTM OE total $2,221,000,000 vs FY2025 $2,200,000,000.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.08x super-bear IV): real — the range between "share loss is permanent" and "moat reasserts" is genuinely wide after a guidance reset. Confidence is medium, never high, and the verdict is sized to the weighted/conservative end: even the *bull* case (IV@15% $64.86) sits below the current price.
- **HIGH_NET_DEBT** (net debt 3.85x normalized OE; net debt $9,042,000,000): folded into the verdict explicitly. The leverage is serviceable against OCF of $2,840,000,000 TTM and the business is investment-grade quality, but it removes the safety net: buybacks at the recent pace plus the dividend run ahead of free cash flow in H1 2026 per earnings coverage, so if OE slides to the bear path ($34.68 IV) there is no balance-sheet cushion story — equity holders eat the full operating decline first. This is one reason probabilities put 45% on bear-or-worse rather than the default 35%.

## My thoughts / overlay
- Quality is not the debate: 5/5 positive OE years, two OE definitions within ~6% of each other in FY2025, SBC trivial, share count shrinking. The debate is purely growth durability — whether 2026 is a cyclical reset (vet visits, price sensitivity) or the start of structural share loss in dermatology and parasiticides. The filings and guidance cannot distinguish those yet; the scenario weights (45% bear-or-worse) reflect that honestly.
- Method range: defensible runs span IV@15% $46.87 (final) to $54.45 (preliminary defaults) — Tier C either way. Only the super-bull scenario clears 15% at the current price; a buyer at $75.675 is paying for bull-case delivery in advance.
- Hurdle math: the price that clears Andrew's 15% on the weighted case is the weighted IV@15% itself, **$46.87**. With a margin of safety against the bear case (IV@15% $34.68), an entry in the mid-$30s to mid-$40s is where this starts to pay for its risks; at $75.675 there is no margin of safety at all.
- Watch items that would change the call: two consecutive quarters of U.S. companion-animal stabilization, dermatology share holding, Librela prescribing recovering post-label-change, and buyback pace vs free cash flow.

## Final verdict
- **Final tier: C** (weighted IRR 10.38% on the v5 final inputs; Tier C under the preliminary default run as well)
- Confidence: **Medium** (high on OE quality and the TTM base; low-medium on the growth path — scenario spread 4.08x and an unresolved share-loss question)
- One-liner: High-quality animal-health leader, moat 7/10 but eroding — does not clear 15% at $75.68 (weighted IRR 10.4%, IV@15 $46.87 vs $75.68 price); it clears 15% only at ~$46.87, so wait for that price or for proof U.S. companion share has stabilized.
