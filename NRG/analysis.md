# NRG — NRG Energy, Inc.
v5 run, 2026-10-15. All figures below are copied from dcf_numbers.json, ttm.py output (ttm.json), or financials_history.csv — none are recomputed.

## What it is
The largest US competitive power company: ~25 GW of generation (doubled by the LS Power portfolio acquisition, closed February 2026 — 18 natural-gas plants plus the CPower commercial/industrial virtual-power-plant platform) paired with the largest US retail electricity business (Reliant, Green Mountain, Direct Energy, and the Vivint smart-home base). Segments: Texas, East, West/Services/Other. Merchant generation plus retail supply — earnings ride power prices, capacity prices, weather, and hedge mark-to-market, not regulated rate base.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,913,000,000; capex $1,147,000,000; SBC $134,000,000 (always a real cost).
- **Conservative owner's earnings FY2025: $632,000,000 = $3.18/share** on 199,000,000 diluted shares.
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): **−$102,000,000** for FY2025 — the working-capital build ($1,225,000,000 increase in net working capital per the CSV) swamps it. The two definitions disagree violently for NRG in most years because GAAP OCF carries derivative mark-to-market and collateral swings; the OCF-based conservative figure is the series used throughout.
- OE history (conservative, from the CSV): FY2021 $203,000,000; FY2022 −$35,000,000; FY2023 −$920,000,000; FY2024 $1,732,000,000; FY2025 $632,000,000. OE positive 3 of the last 5 fiscal years. This is a deeply cyclical, hedge-distorted series — no single year means much.
- **Base used = the engine's normalized base, median of last 3 FY OE/share = $3.1759/share** (the three years are −$4.04, +$8.17, +$3.18 per share as filed; the median is the FY2025 value). Net debt: the engine returned null (the FY2025 debt tags did not come through in the filed facts it read), so no net-debt figure is quoted — see the balance-sheet note under Flags/Thoughts instead of a computed number.

**TTM check (ttm.py, filing-direct, FY2025 − H1 2025 + H1 2026):**
- OCF: FY $1,913,000,000 − prior YTD $1,306,000,000 + current YTD $948,000,000 = **TTM $1,555,000,000**
- Capex: FY $1,147,000,000 − prior YTD $595,000,000 + current YTD $655,000,000 = **TTM $1,207,000,000**
- SBC: FY $134,000,000 − prior YTD $62,000,000 + current YTD $72,000,000 = **TTM $144,000,000**
- Shares (current-YTD weighted diluted): **210,000,000** — up from 199,000,000 in FY2025 because of the shares issued to LS Power at closing
- **TTM OE total $204,000,000 → $0.97/share**
- **The TTM base was NOT used.** It is the distorted one here: (1) TTM capex of $1,207,000,000 is loaded with growth capex for new-build generation (the 415 MW T.H. Wharton plant entered commercial operation in May 2026, with two more Texas Energy Fund projects under construction) — the standardized OE definition charges all capex, so a build-out year mechanically crushes it; (2) H1 2026 OCF ($948,000,000 vs $1,306,000,000 in H1 2025) absorbed Winter Storm Fern costs, mild weather, and Texas softness that management described as first-half-weighted when reaffirming full-year 2026 guidance. Against that, the median-of-3 base is the designed normalization for exactly this OE_VOLATILE profile. The honest caveat runs the other way too: even the median base ($3.18/share) sits far below the company's own cash-earnings framing (2026 guidance: Adjusted EBITDA $5,325–5,825M, FCFbG $2,800–3,300M, Adjusted EPS $7.90–$9.90, all reaffirmed at Q2 2026) — GAAP OCF for a merchant generator is simply a noisy anchor, which is why confidence is low and the verdict leans on the spread, not a point estimate.

## Moat: 4/10 — weak-to-moderate
Justification: real scale and a sticky retail book, but the generation half is a commodity price-taker and retail switching costs are low; nothing here earns pricing power through a cycle.
- FOR: Largest US retail electricity customer base (multi-brand: Reliant, Green Mountain, Direct Energy) plus the Vivint smart-home installed base — retail load is comparatively sticky and diversifies the merchant book
- FOR: Integrated generation-plus-retail structure is a partial natural hedge — retail load absorbs fleet output when power prices fall
- FOR: Post-LS Power fleet scale (~25 GW) concentrated in ERCOT and PJM, the two markets with the tightest capacity outlooks and the data-center load growth
- FOR: CPower virtual-power-plant / demand-response platform — a contracted, asset-light earnings stream few peers match
- FOR: Contracted data-center pipeline (Bring Your Own Power: 1.2 GW hyperscaler CCGT aligned on key terms, minimum 15-year term targeted) converts merchant exposure into contracted cash flow if it closes
- AGAINST: Merchant generation is a pure commodity — no pricing power; spark spreads and capacity prices are set by the market and by regulators
- AGAINST: Retail electricity churn is structurally high and switching costs are near zero; the customer base must be re-bought continuously with marketing spend
- AGAINST: Weather and commodity volatility dominate any single year (OE was negative in FY2022 and FY2023)
- AGAINST: Regulatory/political exposure in ERCOT (post-Uri scrutiny; Texas now requires audits before data-center interconnections advance) and in state retail-choice politics
- AGAINST: Post-acquisition leverage — the LS Power deal added cash consideration and assumed debt, and management is targeting a return to <3.0x net debt / Adjusted EBITDA over 24–36 months; the balance sheet constrains the equity story near-term
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Engine blended growth g_base = 14.37% (blend median is the latest revenue YoY of +9.37%, plus the +5.00pp share-count adjustment — see BUYBACK_TAILWIND below for why that credit is backward-looking). Default offsets and multipliers retained; probabilities at the 10/25/30/25/10 defaults. **Sanity check against actual prints:** the base-case start of 14.37% sits right on management's post-LS Power target of at least 14% Adjusted EPS CAGR through 2030 (raised from at least 10% when the deal was announced) — consistent, not heroic. Q2 2026 printed Adjusted EBITDA +33.9% YoY (LS Power contribution) but Adjusted EPS −13.9% YoY on higher interest and the enlarged share count, so per-share growth is running well below total-company growth near-term; the bear start (9.37%) covers that. The super-bull start (26.37%) is above anything NRG has printed per-share — it is a 10% tail that requires full LS Power annualization, strong PJM/ERCOT capacity pricing, and the BYOP data-center build converting on schedule; it is not a forecast. Price $101.535.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 2.37% | 0.75 | Weak power/capacity prices, another bad-weather year, deleveraging stalls | $19.43 | 4.89% |
| Bear | 25% | 9.37% | 0.90 | LS Power accretion eaten by interest and share count; Texas stays soft | $30.45 | 6.42% |
| Base | 30% | 14.37% | 1.00 | Guided ~14% EPS CAGR path delivered on a normalized OE base | $40.79 | 7.84% |
| Bull | 25% | 19.37% | 1.10 | Capacity prices stay tight; BYOP contracts close; buybacks resume at $1B/yr | $53.94 | 9.56% |
| Super bull | 10% | 26.37% | 1.25 | Power-demand supercycle: data-center load + fleet scarcity rents | $78.92 | 12.56% |

- **Probability-weighted: IV@15% $43.17 (−57.5% vs price), IV@12% $58.36, IV@10% $75.40, weighted IRR 8.18%, base-case IRR 7.84%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 3.13%, terminal value 20.4% of IV@15%, scenario spread 4.06x, 9.5 months since FY end. Even the super-bull scenario (12.56% IRR) does not clear the 15% hurdle at $101.535 — on standardized owner's earnings, the price already pays for the bull case.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): ttm.py was run and its inputs are quoted in full above. The TTM base ($0.97/share) was rejected with reasons stated (growth-capex load, H1-weighted OCF weakness); the normalized median base was used. This is a judgment call documented here, not a silent default — if H2 2026 does not recover as guided, the TTM figure is the honest base and the stock is worse than a D on these numbers.
- **BUYBACK_TAILWIND** (share count shrinking 5.5%/yr, +5pp credited in the blend): the credit is real history (317M diluted shares in 2017 down to 199M in FY2025) but it has **reversed near-term** — the LS Power closing issued 24.25M shares to the seller and H1 2026 diluted shares printed 210,000,000. Management plans ~$1B/yr of buybacks until leverage is back under 3.0x, so the tailwind should resume, but the +5pp blend credit is backward-looking today; one more reason the offsets were not raised.
- **BASIS_BREAK_SUSPECT** (>60% revenue jump in the last 5 years): identified — revenue went from $8,691,000,000 (FY2020) to $26,777,000,000 (FY2021) on the Direct Energy acquisition (closed January 2021); Vivint Smart Home (closed March 2023) is the second break, and the 5-yr revenue CAGR of 28.42% is an acquisition artifact, not organic growth. The blend's median correctly ignored it (it used the latest YoY, +9.37%); no growth input in this run straddles the breaks blindly. A third break (LS Power, Feb 2026) is already in the TTM share count and will enter the annual history next fiscal year.
- **OE_VOLATILE** (OE/share range >3x over 5 years): real and structural — conservative OE totals ran −$920,000,000 to +$1,732,000,000 across FY2023–FY2025 on hedge mark-to-market, collateral, and weather. Handled by the normalized median base and by keeping 35% of probability on bear-or-worse; it is also a core reason confidence is low rather than medium.
- **SECTOR_MODEL_MISMATCH** (Utilities): NRG is a merchant/retail power company classified in Utilities. The OE/capex DCF fits it poorly in both directions — GAAP OCF is hedge-noise-dominated (understates cash earnings vs the company's FCFbG framing) while total capex mixes maintenance with new-build growth (overstates the maintenance burden in build years). Confidence graded **low** per the rule; the tier is a screen result, not a valuation opinion.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.06x super-bear IV): real — the outcome range for a levered merchant generator genuinely is this wide. Confidence capped accordingly; the verdict below is sized to the conservative end.

## My thoughts / overlay
- The method range is the story. On the TTM base ($0.97/share) this screens as a deep F/D with no scenario near the hurdle; on the median base it is a D (8.18% weighted); on the company's own Adjusted EPS guidance ($7.90–$9.90 for 2026) the stock would look optically cheap — but adjusted EPS excludes the very items (hedge MTM, growth capex, deal interest) that decide what owners actually keep. The standardized-OE answer sits between: a real, cash-generative franchise whose per-share economics are currently diluted by a levered, fleet-doubling acquisition.
- Balance sheet: the engine could not compute net debt from the filed tags it read (returned null), so no leverage multiple is quoted from the model. What is sourced: the LS Power transaction was ~$12.0B enterprise value — $6.4B cash, $2.8B in stock, $3.2B of net debt assumed — and management is targeting <3.0x net debt / Adjusted EBITDA within 24–36 months of the February 2026 close, with ~$1B/yr buybacks in the meantime. Q2 2026 quarterly interest expense rose to $310M from $148M a year earlier. Leverage, not operations, is the near-term equity risk.
- The bull case is not imaginary: East Adjusted EBITDA jumped to $469M in Q2 2026 from $99M a year earlier on LS Power assets and capacity pricing, and the BYOP hyperscaler project (1.2 GW, ~$500M targeted annual Adjusted EBITDA at full operation, late-2029) is the kind of contracted growth that would re-rate the equity story. But at $101.535 the market is already paying for a good chunk of it — every scenario in this run, including super bull, prices below the current quote at a 15% discount rate.
- Price that clears 15%: the weighted IV@15% is **$43.17** — that is the level at which the weighted case itself earns 15%. With a margin of safety against the OE volatility documented above, a buyer using this method needs the low-$40s or better; there is no plausible reading of the standardized numbers that clears 15% anywhere near $101.535.

## Final verdict
- **Final tier: D** (weighted IRR 8.18% on the normalized median base; no tier override — the numbers tier and the evidence agree, and even the super-bull tail does not clear 15%)
- Confidence: **Low** (sector-model mismatch, OE volatility, and a TTM-vs-median base dispute that spans the whole verdict)
- One-liner: Real cash-generative power franchise but a weak 4/10 moat and hedge-noise OE; on the normalized base it does not clear 15% (weighted IRR 8.2%, IV@15 $43.17 vs $101.54 price) — even the super-bull tail falls short; it would need the low-$40s to clear 15% on standardized owner's earnings.
