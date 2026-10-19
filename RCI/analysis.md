# RCI — Rogers Communications Inc.

Engine 5.4.0 run, 2026-10-16. In scope (market cap $17.305B at $31.99, nasdaq_quote_api). Price $31.99 is the NYSE line.

All figures below are copied from key_numbers.md, dcf_numbers.json, financials_history.csv, or fundamentals.json — none are recomputed. Filing figures are in CAD as filed unless marked USD (the engine converts CAD→USD at period-end ECB rates; see FX_CONVERTED).

## What it is

Canada's largest communications and entertainment company: Wireless (the #1 national subscriber base), Cable (internet/video, made national by the April 2023 Shaw acquisition), and Media (Sportsnet, the Toronto Blue Jays, and Maple Leaf Sports & Entertainment — 75% owned since July 1, 2025, with an agreement to buy the remaining 25% in Q4 2026, after which Rogers plans to sell a minority stake in its combined sports/media holdings). Dual-class: Class A Voting shares (family control) and Class B Non-Voting shares — the Class B share is itself the NYSE security (see ADS_RATIO). IFRS filer reporting in CAD on Form 40-F; it files no 10-Qs, so there are no quarterly XBRL facts — interim results arrive as 6-K earnings releases.

## Owner's earnings

**FY2025 (40-F via EDGAR, from financials_history.csv, USD-converted):** operating cash flow $4,425,251,240; capex $2,821,380,680; SBC $71,575,280.

- **Conservative owner's earnings FY2025: $1,532,295,280 = $2.83/share** (latest FY OE/share, key_numbers.md).
- Maintenance version (NI-based, from financials_history.csv): $7,645,035,740 — unusable for 2025: net income carries a non-cash, non-taxable gain of roughly CAD $5.0B from revaluing Rogers' pre-existing MLSE stake to fair value when the July 1, 2025 consolidation closed (the Q3 2025 release books it in "Other (income) expense" of −$5,038M CAD for the quarter and its tax reconciliation names the non-taxable MLSE revaluation gain). The gain is non-cash, so the OCF-based conservative figure is the clean one.
- OE positive 5 of the last 5 fiscal years. Net debt $29.006B (key_numbers.md); lease liabilities a further $2,277,262,480 (dcf_numbers.json).
- **Base used = normalized owner's earnings, $1.98/share** (median of the last 3 FY OE/share: $1.60 / $1.98 / $2.83, base_source: median_of_last_3_fy_oe_per_share). No TTM base: ttm.py was run and cannot compute TTM for this IFRS 40-F filer (it reads us-gaap facts only and there are no quarterly filings), so per the worker spec the median base stands and is the subject of BASE_DIVERGENCE below.
- CAD history (fundamentals.json, as filed): revenue CAD 13,916M (2020) → CAD 15,396M (2022) → CAD 19,308M (2023, Shaw) → CAD 21,712M (2025, +half a year of MLSE). Capex was CAD 4,042M / 4,100M / 3,863M in 2023/24/25; 2026 guidance cuts it to CAD 2.5–2.7B (Q2 2026 release), which mechanically lifts forward OE — a tailwind carried in the scenario growth starts and bull multipliers, not in the base.
- Telecom capex caveat (for pass 2): the engine's capex leg is PP&E purchases only. Spectrum licence payments — lumpy, multi-billion CAD auction outlays — sit outside it, as does lease principal. Through a full spectrum cycle, true economic capex is higher than the leg used and OE is correspondingly flattered.

## Moat: 6/10 — moderate-strong oligopoly, shared with two equals

Justification: Canadian telecom oligopoly member with the #1 wireless base, a national cable footprint after Shaw, deep spectrum holdings and unique sports/media assets; ROIC proxy stayed 10.2–16.2% over 2020–2025 (13.9% in 2025) and gross margin expanded from 42.1% to 45.2%, but the moat is shared with Bell/Telus, the regulator keeps prying at wholesale access, and population-driven subscriber growth is fading.

- Evidence (fundamentals.json, CAD as filed): roic_proxy 16.2% (2020), 14.0% (2021), 10.6% (2022), 10.2% (2023, Shaw integration trough), 13.3% (2024), 13.9% (2025) — above the cost of capital through the cycle, which supports a 6; gross margin 42.1% → 40.2% → 41.5% → 44.4% → 46.7% → 45.2% over the same years. Not a 7+: returns are oligopoly-typical, not franchise-exceptional, and two rivals hold comparable positions.
- FOR: regulated three-player oligopoly with foreign-ownership limits and spectrum scarcity; #1 wireless subscriber base with 66–67% wireless EBITDA margins and best-in-class postpaid churn (0.94–0.99% in 2026 prints); national cable/internet footprint from Shaw plus deep spectrum holdings; ROIC and gross-margin record above; sports/media assets no rival can replicate (Blue Jays, MLSE).
- AGAINST: the moat is shared — Bell and Telus hold comparable scale, spectrum and margins; CRTC wholesale/MVNO mandates and political pressure on consumer prices cap pricing power; federal immigration cuts remove the population-growth tailwind behind subscriber adds; Quebecor/Freedom (the Shaw-deal remedy buyer) competes on price nationally; net debt of $29.0B (3.9x EBITDA) limits flexibility and cord-cutting erodes cable video.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — engine 5.4.0 final run (2026-10-16)

Growth recalibration (written reason): the engine's blended growth is 8.97%, and every component is acquisition arithmetic, not organic growth — rev CAGR 3y 11.72% spans the April 2023 Shaw close (revenue stepped up ~25% in one year), latest rev YoY 10.74% includes MLSE consolidating from July 1, 2025, and OE/share CAGR 2y 32.84% runs off the 2023 integration trough. The organic prints are far lower: Q2 2026 wireless service revenue was flat and cable +1% (reported total +8% is the MLSE anniversary), and FY2026 guidance is service revenue +3–5% (still MLSE-flattered) with adjusted EBITDA +1–3%. Scenario starts were therefore set via offsets (−0.12 / −0.09 / −0.05 / −0.02 / +0.01 vs the blend) to −3.0 / −0.0 / **4.0** / 7.0 / 10.0%. The 4.0% base start sits inside the 3–5% guidance range because the guided capex step-down (CAD 2.5–2.7B vs CAD 3,863M filed for 2025) mechanically raises OE even at flat revenue; the bull and super-bull starts require that step-down to stick plus sports/media monetization. Probabilities 10/30/30/20/10 — bear weight raised from the 25% default for the leverage and OE volatility (flags below); OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -3.0% | 0.75 | Price war + wholesale mandates bite; capex creeps back up | $9.53 | 5.98% |
| Bear | 30% | -0.0% | 0.9 | Organic telecom flat; population tailwind gone | $13.07 | 7.49% |
| Base | 30% | 4.0% | 1.0 | Guidance path: modest service growth, capex step-down holds | $17.36 | 9.35% |
| Bull | 20% | 7.0% | 1.1 | Capex discipline + sports monetization + deleveraging | $21.82 | 11.18% |
| Super bull | 10% | 10.0% | 1.25 | Sports/media sell-down re-rates the asset base; OE steps up | $28.33 | 13.68% |

- **Probability-weighted: IV@15% $17.28 (−46.0% vs price), IV@12% $22.87 (−28.5%), IV@10% $29.10, weighted IRR 9.33%, base-case IRR 9.35%.**
- **Tier by numbers: D.** No tier override. Diagnostics (key_numbers.md): OE yield 6.20%, terminal value 18.4% of IV@15%, scenario spread 2.97x, net debt 27.05x normalized OE, 9.5 months since FY end.
- Hurdle-clearing prices on the weighted path: 15% at $17.28, 20% at $12.24, 25% at $9.46. Even the super-bull case (13.68%) does not clear 15% at $31.99.

## Flags — every fragility flag resolved

- **STALE_FY** (FY2025 ended 9.5 months ago): ttm.py was attempted and cannot run for this IFRS 40-F filer (no us-gaap annual facts, no quarterly filings), so the median FY base stands per spec. Interim evidence checked instead: H1 2026 cash provided by operating activities was CAD 3,012M, +4% YoY, and adjusted net income was flat (Q2 2026 release, July 22, 2026) — nothing in the interims contradicts the filed base: H1 operating cash flow grew 4% YoY and adjusted earnings were flat, consistent with the normalized $1.98/share median rather than the MLSE-flattered $2.83 latest year. The median base stands.
- **OE_VOLATILE** (OE/share range over the last 5 years spans >3x): the swing is identified, not noise — the 2023 Shaw integration trough ($1.60) against the 2025 MLSE consolidation year ($2.83). Mitigation is the normalized median base plus the raised bear weight (30% vs the 25% default) in the scenario design; the verdict is sized on the median, not on either endpoint.
- **NI_OCF_DIVERGENCE** (net income vs OCF differ by >40% in 2023): the Shaw close year — acquisition and integration costs, transaction working-capital swings, and non-cash marks in the April 2023 consolidation year. The base is OCF-derived in every year, so net-income noise in the close year never enters it; the same presentation gap in 2025 (the ~CAD $5.0B non-cash MLSE revaluation gain) is handled in Owner's earnings above and is precisely why the maintenance (NI-based) series is rejected there.
- **FX_CONVERTED** (CAD converted at period-end ECB rates): flow facts are converted at the period-end rate rather than a period average — a stated engine approximation, with the rates used recorded in dcf_numbers.json fx_conversion. It moves individual years modestly in both directions; it does not drive the verdict, which is set by the gap between the $1.98 normalized base and a $31.99 price.
- **ADS_RATIO_APPLIED** (×1.0): the NYSE security is the Class B Non-Voting share itself, not an ADS (Form 40-F cover, filed 2026-03-06) — there is no depositary ratio to apply, and filed per-share figures and the NYSE price are on the same share basis. The flag records the confirmation, not an adjustment.
- **BASE_DIVERGENCE** (latest FY OE/share $2.83 vs 3-yr median $1.98): the latest year is the distorted one — FY2025 consolidates MLSE only from July 1, 2025 (a part-year step-up in the cash business) while capex still runs at the pre-step-down CAD $3,863M. The median is the honest through-cycle base; the full-year MLSE effect and the guided capex step-down (CAD 2.5–2.7B for 2026) are carried in the bull scenarios instead of the base. On the latest-year base the verdict would reach the C end of the recorded method range (D to C) — disclosed, not used.
- **HIGH_NET_DEBT** (net debt 27.05x normalized OE): real leverage — $29.006B of net debt (3.9x EBITDA) plus $2,277,262,480 of lease liabilities. Levered OE compresses fast if rates, capex or subscriber economics move against the company; that is priced through the raised bear weight and the cut scenario starts (−3.0% / −0.0%), not removed. It is also why confidence is not raised despite the oligopoly moat.
- **TIER_BAND** (bear D 7.5% vs bull C 11.2%): the final D is the probability-weighted result (9.33%); no scenario reaches 15% at $31.99 (super-bull 13.68%), so the band spans D–C only and any position should be sized to the bear end.

## Final verdict
**Tier D.** Weighted IRR 9.33%, weighted IV@15% $17.28 against a $31.99 price (−46.0%); clears 15% only at or below $17.28, 20% at $12.24, 25% at $9.46. A solid oligopoly cash machine (moat 6/10) whose price already pays for the recovery: on the normalized $1.98/share base the return is single-digit, the balance sheet is levered at 27x normalized OE, and even the super-bull case does not clear the 15% hurdle. Method range D to C — the C requires paying on the MLSE-flattered latest year, which this verdict declines to do.