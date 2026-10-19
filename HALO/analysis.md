# HALO — Halozyme Therapeutics, Inc.
Engine 5.4.0 run, 2026-10-18. In scope (market cap $15.097B at $121.84, nasdaq_quote_api).

All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv or fundamentals.json — none are recomputed.

## What it is
Asset-light drug-delivery platform. Its ENHANZE technology (recombinant human hyaluronidase PH20) lets partners convert IV biologics into subcutaneous injections; Halozyme collects royalties on commercialized partner products — DARZALEX SC (Janssen), VYVGART Hytrulo (argenx), Phesgo, Ocrevus Zunovo, Opdivo Qvantig, Rybrevant Faspro — plus product sales and collaboration/milestone revenue. Q2 2026: total revenue $481M (+48% YoY), royalty revenue $307.7M (+50% YoY); management raised FY2026 guidance to total revenue $1.835B–$1.91B and royalty revenue $1.22B–$1.245B. In late 2025 it bought Elektrofi (Hypercon) and Surf Bio to build a second, longer-dated royalty platform.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $651,558,000; capex $6,970,000; SBC $51,565,000 (always a real cost).
- **Conservative owner's earnings FY2025: $593,023,000 = $4.79/share** (base_oe_latest_per_share $4.7861).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $637,403,000 — same ballpark, raises confidence.
- OE positive 5 of the last 5 fiscal years. Net debt $2,008,810,000 on the FY2025 filing basis (debt $2,142,630,000 vs cash $133,820,000; LongTermDebtNoncurrent+LongTermDebtCurrent). Post-period: in September 2026 the company closed a $1.5B 1.50% convertible offering due 2033 and repurchased portions of its 2027/2028 notes, so the live debt stack differs from the FY2025 basis the engine nets.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $651,558,000 − prior YTD $253,932,000 + current YTD $420,969,000 = **TTM $818,595,000**
- Capex: FY $6,970,000 − prior YTD $2,513,000 + current YTD $7,914,000 = **TTM $12,371,000**
- SBC: FY $51,565,000 − prior YTD $22,834,000 + current YTD $34,335,000 = **TTM $63,066,000**
- Shares (current-YTD weighted diluted): **122,092,000**
- **TTM OE total $743,158,000 → base OE/share $6.0869** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $3.2836/share — rejected as the base: it averages in the pre-inflection royalty years (FY2023 OE/share $2.5087, FY2024 $3.2836) before the post-2020 launch cohort (Vyvgart, Ocrevus, Opdivo, Rybrevant SC versions) ramped. The median-base run is retained as the method-range low end below.

## Moat: 7/10 — strong, with a dated cliff
Justification: contractual royalties on already-approved blockbusters with clinical/regulatory/commercial switching costs once a co-formulated SC version wins share (DARZALEX SC at ~96% US conversion), gross margins of 76.8–84.3% over the last five fiscal years (fundamentals.json: 2021 81.6%, 2022 78.9%, 2023 76.8%, 2024 84.3%, 2025 83.6%), and roic_proxy above the cost of capital through the cycle (2021 22.8%, 2022 15.1%, 2023 18.6%, 2024 25.1%, 2025 15.5%). The ROIC proxy's denominator is flattered/distorted by convertible-funded buybacks and acquisitions that shrank book equity to $48,814,000, so the level should be read as "comfortably above WACC," not as precise. Capped at 7, not higher, because the core ENHANZE composition patent expires around 2027–2029, a large share of ENHANZE royalties rolls off by 2035, and Alteogen's competing hyaluronidase already powers Merck's Keytruda SC.
- FOR: royalties are contractual and run past the core patent date on the big products (e.g. DARZALEX SC royalties contractually through ~2032); switching a co-formulated, approved SC product back out is a clinical, regulatory and commercial cost, not just a technical one; six material royalty contributors and broadening — five new collaboration agreements signed through July 2026, including first deals in ADCs and nucleic acids; near-zero capex royalty economics (TTM capex $12,371,000 on TTM OCF $818,595,000); Hypercon/SurfBio add a second platform with IP guided into the mid-2040s.
- AGAINST: single-platform concentration — ENHANZE is the business until Hypercon produces royalties in the 2030s; core patent expiry 2027–2029 weakens pricing power on NEW deals even where existing contracts hold; Alteogen/Merck competition is live (Keytruda Qlex approved in the US and Europe) and Halozyme is spending on multi-country Mdase patent litigation against Merck; partner concentration in a handful of blockbusters whose own patent cycles and competition Halozyme does not control; acquisition appetite (Elektrofi $750M upfront, Surf Bio) is converting a pure royalty stream into balance-sheet and integration risk.
- A 7 gives CAP = 11.1 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 11.1 years, 15-year projection.

## DCF — engine 5.4 final run (2026-10-18)
Growth sanity check (written): the blend is 39.89% and g_base hit the 35% cap. Actual prints: FY2025 revenue +37.55% YoY, Q2 2026 revenue +48% YoY with royalties +50%, and raised FY2026 guidance of $1.835B–$1.91B total revenue (+31–37% vs FY2025) with royalties guided +41–43%. The base start of 35.0% sits inside the company's own guidance range and below the latest quarterly print — the Q2 print included $35.5M of upfront collaboration revenue and the newest-launch surge, so holding base at guidance rather than at the quarterly print is the written reason. The super-bull start of 47.0% is approximately the Q2 2026 print, which is what a super bull should assume persists. Probabilities shifted vs defaults (bear 25% → 30%, bull 25% → 20%) for OE volatility, the patent cliff and the Merck/Alteogen overhang; OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $121.84.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 23.0% | 0.75 | Patent cliff bites new deals early; Alteogen wins share; partner royalty roll-off | $99.01 | 13.09% |
| Bear | 30% | 30.0% | 0.90 | Growth decays to guidance low end and fades fast post-2029 | $165.25 | 18.15% |
| Base | 30% | 35.0% | 1.00 | Guidance trajectory; launch cohort keeps compounding over the CAP | $231.90 | 22.10% |
| Bull | 20% | 40.0% | 1.10 | New ENHANZE deals and indications stack on the royalty base | $321.45 | 26.34% |
| Super bull | 10% | 47.0% | 1.25 | Q2 2026 pace persists; Hypercon becomes a real second engine early | $502.70 | 32.80% |

- **Probability-weighted: IV@15% $243.61 (+99.9% vs price), IV@12% $354.56, IV@10% $483.16, weighted IRR 22.64%, base-case IRR 22.10%**
- **Tier by numbers: A.** Diagnostics (dcf_numbers.json): OE yield 5.00%, terminal value 29.2% of IV@15%, scenario spread 5.08x, net debt 2.66x normalized OE, 9.6 months since FY end.
- Hurdle prices: clears 15% up to $243.61, 20% up to $150.17, 25% up to $103.09 (below the current price — it does not clear the 25% hurdle).

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.6 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above.
- **BUYBACK_TAILWIND** (share count shrinking 4.1%/yr): already credited via the growth adjustment in the blend; Q2 2026 alone repurchased $332.8M toward a $400M 2026 target. Not double-counted in the verdict.
- **BASIS_BREAK_SUSPECT** (>60% revenue jump in the last 5 years): the jumps are the ENHANZE royalty inflection (FY2021 revenue +65.7% as DARZALEX SC and Phesgo ramped) plus the Antares acquisition (2022) and the late-2025 Elektrofi/Surf Bio deals — not a restatement of the royalty series. Growth inputs were sanity-checked against current prints and guidance rather than taken from the long CAGRs, and the base is TTM, so no scenario straddles the break for its level.
- **OE_VOLATILE** (OE/share spans >3x over 5 years): real — it is a royalty inflection (FY2021 $1.8881 → TTM $6.0869), not cyclicality. Handled by widening the bear weight to 30% and by reporting the median-base method range below.
- **NI_OCF_DIVERGENCE** (2025): found — Q4 2025 carries a $284.9M acquired IPR&D expense for the Surf Bio acquisition (a $2.42/share hit; Q4 GAAP net loss $141.6M) plus a $48.7M intangible impairment, which crush net income ($316,889,000) while operating cash flow ($651,558,000) is unaffected in kind. The OCF-based conservative OE used throughout is not contaminated by it; if anything the charge makes the NI-based maintenance version the noisy one this year.
- **BASE_DIVERGENCE** (latest FY $4.7861 vs 3-yr median $3.2836): the median is the distorted one — it averages pre-inflection years. Latest FY and TTM both step up on filed royalty growth (+37.6% FY2025 revenue, +48% Q2 2026). TTM base used; median retained in the method range.
- **WIDE_SCENARIO_SPREAD** (5.08x): real — the outcome hinges on post-patent royalty duration. Confidence is capped at medium and the verdict is sized to the bear end of the band.
- **TIER_BAND** (bear tier B at 18.15% vs bull tier S at 26.34%): the verdict spans tiers; any position should be sized to the bear end (B economics), even though the weighted tier is A.
- **HIGH_NET_DEBT** appeared on the preliminary (median-base) run at 4.9x normalized OE and dropped off the final run (2.66x on the TTM-based diagnostics): the leverage is convertible notes, not bank debt — FY2025 debt $2,142,630,000 against TTM OCF $818,595,000, and the September 2026 refinancing pushed maturities to 2033 while retiring parts of the 2027/2028 notes. It is real leverage against a royalty stream, but there is no near-term maturity wall; the bear cases carry the stress (super-bear IV@15% $99.01 is below price).

## My thoughts / overlay
- The honest headline is the method range: the preliminary run on the 3-yr median base ($3.2836) printed Tier C — weighted IRR 13.70%, weighted IV@15% $105.95 — while the TTM-base final prints Tier A at 22.64% / $243.61. The TTM base is the right one (the median demonstrably averages a smaller, pre-launch-cohort company), but the spread between them is the finding: this verdict is base-sensitive, and pass 2 should attack the TTM base first — in particular how much of TTM OCF is recurring royalty cash vs collaboration upfronts and product sales.
- Quality is high: asset-light royalty economics, gross margin ~84%, SBC $63,066,000 TTM is a real but modest cost against $818,595,000 TTM OCF, buybacks shrinking the count ~4.1%/yr (already credited).
- The dated risk is not demand — it is duration. Core ENHANZE patent expiry 2027–2029, royalty roll-off into 2035, and a credible competitor (Alteogen) already inside the biggest SC conversion in the industry (Keytruda). The 15-year projection with an 11.1-year fade assumes the contractual tail plus Hypercon bridge that duration; the super-bear case (IV@15% $99.01, below the $121.84 price) is the one where it doesn't.
- Margin of safety on the final numbers: weighted IV@15% sits 99.9% above price, but the bear-case IV@15% ($165.25) is the more honest anchor — still above price — and the super-bear sits below it. A buyer is paid on the bear case, not insured against the super bear.

## Final verdict
- **Final tier: A** (weighted IRR 22.64% on the TTM base; bear-to-bull band B → S, method range C → A — size to the bear end)
- Confidence: **Medium** (high on the royalty cash quality and the TTM legs, medium on royalty duration past the patent cliff; WIDE_SCENARIO_SPREAD caps confidence below high)
- One-liner: Contractual royalty toll-booth on approved blockbusters, moat 7/10 — clears 15% at $121.84 on TTM numbers (22.6% weighted, IV $243.61) and even on the bear case, but the duration past the 2027–29 ENHANZE patent cliff is the bet; clears 15% up to $243.61, not the 25% hurdle (up to $103.09).
