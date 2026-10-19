# NVR — NVR, Inc.
Engine 5.4.0 run, 2026-10-16. In scope (market cap $18.169B at $5,919.82, nasdaq_quote_api — key_numbers.md).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed. Earnings-release figures are from NVR's Q2 2026 release (PR Newswire, 2026-07-23); balance-sheet detail is from the FY2025 10-K.

## What it is
One of the largest US homebuilders: single-family detached homes, townhomes and condos under Ryan Homes, NVHomes and Heartland Homes across 37 metropolitan areas in 16 states plus Washington, DC, plus an attached mortgage banking operation (NVR Mortgage). The defining feature is the asset-light lot-option model: NVR generally does not develop or own land — it controls finished lots through fixed-price lot purchase agreements (LPAs) with third-party developers, forfeiting only its deposit (~10% of lot value) if it walks away. Capex is structurally trivial: FY2025 capex was $24,508,000 against revenue of $10,323,959,000 (financials_history.csv).

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,121,320,000; SBC $69,213,000 (always a real cost); capex $24,508,000.
- **Conservative owner's earnings FY2025: $1,027,599,000 = $334.82/share** (key_numbers.md: latest FY OE/share $334.82, latest FY OE total $1.028B)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,339,818,000 total — above the conservative figure because FY2025 working capital (inventory build) dragged OCF below net income; the OCF-based conservative figure is the cleaner base for a builder mid-cycle.
- OE positive 5 of the last 5 fiscal years. OE/share history is openly cyclical: $504.24 (FY2022) → $399.85 (FY2023) → $382.99 (FY2024) → $334.82 (FY2025) — the current base sits on a down-leg, not a peak.
- Buybacks are the capital-return engine: $1,818,595,000 repurchased in FY2025 per the 10-K; fundamentals.json puts TTM buybacks at $1,784,065,000. No dividend.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,121,320,000 − prior YTD $242,886,000 + current YTD $188,156,000 = **TTM $1,066,590,000**
- Capex: FY $24,508,000 − prior YTD $15,362,000 + current YTD $11,023,000 = **TTM $20,169,000**
- SBC: FY $69,213,000 − prior YTD $36,339,000 + current YTD $32,580,000 = **TTM $65,454,000**
- Shares (current-YTD weighted diluted): **2,872,444**
- **TTM OE total $980,967,000 → base OE/share $341.51** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $382.99/share — rejected as the base because it is the FY2024 figure and straddles the downturn: FY2025 printed $334.82 and H1 2026 diluted EPS fell 26% YoY per the Q2 release, so the median overstates the current run-rate. It is retained in the method-range discussion below.

**Balance sheet (FY2025 10-K, resolving DEBT_TAGS_BLANK / CASH_INCLUDES_RESTRICTED):** the only debt is $900,000,000 of senior notes maturing May 2030; the $300,000,000 revolving credit agreement and the mortgage subsidiary's $150,000,000 repurchase facility both had **no borrowings outstanding** at December 31, 2025. The combined cash + restricted-cash tag totals $1,956,881,000 (financials_history.csv); total assets $5,856,930,000, total liabilities $1,992,061,000, equity $3,864,869,000. The engine's debt tags came back blank because the senior notes are not filed under the debt tags the engine reads — debt is NOT zero, it is the $900M notes; against the combined cash figure the company is in a net-cash position before separating the restricted portion (escrow/collateral balances inside the combined tag are not broken out in the tags the engine reads, so the exact unrestricted net cash is stated here as a range in words, not a number).

## Moat: 7/10 — strong, structural, but not a pricing-power moat
Justification: the lot-option (LPA) model is a structural capital advantage proven through full housing cycles — invested capital stays minimal, downturn risk is capped at forfeited deposits, and returns on capital run far above land-owning peers. Note on evidence: the `roic_proxy` series in fundamentals.json is null for every year because NVR files no operating-income tag, so per the mechanics rule the returns evidence is stated in words: the FY2025 10-K figures imply returns on equity well above 30% (net income $1,339,816,000 on equity of $3,864,869,000 — both from financials_history.csv), and secondary reporting of the 10-K puts FY2025 ROE at ~34.7%, roughly double the builder industry average. Gross margin level and trend come from the earnings releases (the filing tags carry no gross-profit series): homebuilding gross margin was 21.5% in Q2 2025, 21.0% in Q3 2025 and 19.2% in Q2 2026 — a falling trend that is the main argument against a higher score.
- FOR: Lot-option (LPA) model — finished lots controlled via fixed-price agreements, ~10% deposits; land risk and capital intensity structurally removed. Returns on capital far above peers through full cycles on the small capital base. Build-to-order model with pre-sold backlog (10,998 units / $4.99 billion at June 30, 2026) limits speculative inventory. Mortgage banking capture rate 85% in Q2 2026 — attached, capital-light ancillary earnings. Decades of disciplined buybacks: share count shrinking 4.4%/yr (dcf_numbers.json share CAGR -4.36%). Leading share in Mid-Atlantic markets (Washington DC / Baltimore corridors).
- AGAINST: Peers (Lennar, D.R. Horton) are copying the asset-light lot-option model, narrowing the structural edge. No buyer switching costs or pricing power in a downturn: Q2 2026 gross margin 19.2% vs 21.5%, new-order ASP -5%, incentives rising, plus $21.7M of contract land deposit impairments in the quarter. Lot supply depends on third-party developers — no owned land bank if developers fail or reprice. Geographic concentration: 16 states + DC, East-Coast heavy. Hostage to mortgage rates and affordability; earnings are cyclical even if the balance sheet is not.
- A 7 gives CAP = 11.1 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 11.1 years, 15-year projection.

## DCF — engine 5.4.0 final run (2026-10-16)
**Growth sanity check (mandatory):** the engine blend is 3.09% (components: rev CAGR 5y 6.50%, rev CAGR 3y -0.65%, latest rev YoY -1.91%, OE/share CAGR 2y -8.49%, with a +4.36pp buyback adjustment applied to the revenue components only). Recent prints are negative — FY2025 revenue -1.91% YoY, Q2 2026 consolidated revenue $2.33 billion (-10.4% YoY), H1 2026 revenue -16%, Q2 diluted EPS $83.96 (-23% YoY) — so the base start of +3.1% sits **above** the latest prints and needs its written reason: the scenario growth is OE/**share** growth, and the share count is shrinking 4.36%/yr, which mechanically lifts OE/share even with flat total OE; on the demand side Q2 new orders rose 9% to 5,885 units and backlog rose 9% to 10,998 units, so settlements (the revenue leg) have a recovery pipeline even though Q2 settlements fell 8%. To price the risk that this reason is wrong, probabilities were tilted bearish versus the defaults: 15/30/30/15/10 puts 45% on bear-or-worse. The super-bear start (-8.9%) looks mild next to the FY2025 OE/share step-down ($382.99 → $334.82), but its 0.75 OE multiplier cuts the base level by a quarter on top, so the combined path is harsher than the FY2025 print. Bull (8.1%) and super-bull (15.1%) starts are well below the last cyclical upswing in the filed history (OE/share $302.23 in FY2021 → $504.24 in FY2022), so neither needs an optimism defense. OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $5,919.82.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -8.9% | 0.75 | Affordability crunch deepens; margins compress further; orders roll over | $1,234.44 | 4.60% |
| Bear | 30% | -1.9% | 0.90 | Grinding downturn: flat-to-down settlements, 19% gross margins stick | $2,048.57 | 6.58% |
| Base | 30% | 3.1% | 1.00 | Buyback-lifted OE/share growth; backlog converts, margins stabilize | $2,878.87 | 8.61% |
| Bull | 15% | 8.1% | 1.10 | Rate relief revives settlements; margins recover toward 21-22% | $4,012.36 | 11.20% |
| Super bull | 10% | 15.1% | 1.25 | Full cyclical upswing like FY2021-22, buybacks compounding | $6,359.24 | 15.79% |

- **Probability-weighted: IV@15% $2,901.18 (-51.0% vs price), IV@12% $3,849.04, IV@10% $4,906.98, weighted IRR 8.74%, base-case IRR 8.61%**
- **Tier by numbers: D.** Diagnostics (key_numbers.md): OE yield 5.77%, terminal value 18.7% of IV@15%, scenario spread 5.15x, 9.5 months since FY end.
- Hurdle-clearing prices (weighted path): clears 15% at $2,901.18, 20% at $2,049.85, 25% at $1,581.30 — even the super-bull IV@15% ($6,359.24) barely exceeds the current price, and it carries only 10% weight.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above; TTM OE/share $341.51 vs latest FY $334.82 confirms the FY base was not flattering the result.
- **BUYBACK_TAILWIND** (share count -4.36%/yr): already credited via the +4.36pp growth adjustment on the revenue components in the blend; not double-counted in the verdict — it is, however, the explicit written reason the base growth start can sit above the latest revenue prints (see sanity check).
- **DEBT_TAGS_BLANK** (no debt tag for the latest FY): resolved from the 10-K in the balance-sheet paragraph above — debt is $900,000,000 of senior notes due May 2030, both revolving facilities undrawn; the engine's net-debt field is null because the notes are not filed under the tags it reads, NOT because debt is zero.
- **CASH_INCLUDES_RESTRICTED** (only the combined cash + restricted-cash tag filed): acknowledged — the $1,956,881,000 combined figure overstates unrestricted cash by the restricted (escrow/collateral) amount, which the filed tags do not separate; the verdict does not depend on it, since even crediting the full combined figure as net cash against the $900M notes would not move a Tier D verdict at a $5,919.82 price.
- **WIDE_SCENARIO_SPREAD** (5.15x): real — a cyclical builder's outcome range IS wide (FY2022 OE/share $504.24 vs FY2025 $334.82 in the filed history). Confidence is capped at medium and the verdict is sized to the bear end.
- **TIER_BAND** (bear D 6.58% vs bull C 11.20%): the whole band sits below the 15% hurdle, so the band does not change the action — sized to the bear end regardless, final tier D.

## My thoughts / overlay
- The honest headline is that this is a quality/price mismatch, not a quality debate. The method range is narrow for once: the preliminary run on the normalized median base ($382.99/share, default probabilities) printed weighted IRR 9.88% and IV@15% $3,447.41 — also Tier D. Both defensible bases land in D; the TTM base is the more current one and is used.
- The market is pricing NVR as if the lot-option model's through-cycle returns deserve a software-like multiple. At $5,919.82 the buyer needs the super-bull path (15.1% OE/share growth start, 1.25x OE) just to clear 15% — and that path is a repeat of the FY2021-22 upswing, not a base case.
- Margin trajectory is the swing variable to watch: homebuilding gross margin 21.5% → 21.0% → 19.2% over the last year of prints, with lot costs and deposit impairments doing the damage. Q2 orders +9% and backlog +9% say volume is recovering before pricing does.
- Balance-sheet risk is minimal (net cash before the restricted-cash separation, no revolver borrowings, no maturities until 2030), which supports the moat score — the bear case here is an earnings/multiple bear case, not a solvency one.

## Final verdict
- **Final tier: D** (weighted IRR 8.74% on the TTM base; the median-base method also prints D — the verdict is method-robust)
- Confidence: **Medium** (high on the filing data and the balance sheet, capped by the 5.15x scenario spread and the cyclical margin path)
- One-liner: Best-in-class asset-light homebuilder, moat 7/10 — but at $5,919.82 the weighted IRR is only 8.7% (weighted IV@15% $2,901); it clears the 15% hurdle only below ~$2,901, so quality does not rescue the price.
