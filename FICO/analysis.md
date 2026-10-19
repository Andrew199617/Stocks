# FICO — Fair Isaac Corporation
Pass-1 run, 2026-10-17 (engine 5.4.0). In scope: market cap $18.941B at $771.19 (nasdaq_quote_api).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, financials_history.csv or fundamentals.json — none are recomputed. Post-filing events and balance-sheet updates after the FY2025 10-K are from cited press coverage of the FY2026 10-Qs, named where used.

## What it is
The FICO Score company: two segments. **Scores** — royalties on the consumer credit score embedded in US lending, historically the mandated score for GSE (Fannie/Freddie) mortgages; Q3 FY26 revenue $458.9M, +41% YoY, of which mortgage origination revenue was +97% YoY on low-single-digit volumes (price-led, not volume-led) and 62% of Scores revenue. **Software** — the FICO Platform (decisioning, fraud, customer management); Q3 FY26 revenue $215.3M, +2% YoY, but Platform ARR +62% to $413M, 51% of total ARR of $816M (+10%). Asset-light to an extreme: FY2025 capex was $8.9M on $1,990.9M of revenue.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $778,807,000; SBC $156,667,000 (always a real cost); capex $8,922,000.
- **Conservative owner's earnings FY2025: $613,218,000 = $24.97/share** (key_numbers.md: latest FY OE/share $24.97; latest FY OE total $613.2M)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,037,623,000 — above the conservative figure, flattered by a −$379,647,000 ΔNWC swing; the OCF-based conservative figure is the cleaner series and is used throughout.
- OE positive 5 of the last 5 fiscal years. Net debt at FY25 end $2,921,555,000 (key_numbers.md: $2.922B); stockholders' equity is −$1,745,784,000 — negative by design after a decade of buybacks, not a solvency signal by itself.
- **Balance-sheet update (post-FY25, from press coverage of the FY2026 10-Qs):** the company repurchased $3.1B of stock in the first nine months of FY26 — 4.0x the $777,880,000 of YTD operating cash flow — funded partly by a new $1.5B term loan; total debt rose to $5.58B by June 2026 from $3,055,691,000 at FY25 end. The leverage the engine sees ($2.922B net debt) has roughly doubled since.

**Base used = TTM owner's earnings through Q3 FY26 (June 30, 2026), from ttm.py (filing-direct, no hand math):**
- OCF: FY $778,807,000 − prior YTD $555,138,000 + current YTD $777,880,000 = **TTM $1,001,549,000**
- Capex: FY $8,922,000 − prior YTD $4,751,000 + current YTD $1,355,000 = **TTM $5,526,000**
- SBC: FY $156,667,000 − prior YTD $124,288,000 + current YTD $141,910,000 = **TTM $174,289,000**
- Shares (current-YTD weighted diluted): **23,470,000**
- **TTM OE total $821,734,000 → base OE/share $35.01** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $18.93/share and the latest FY is $24.97/share. The median is the stale one: it spans FY23–FY25, before the steepest per-score price increases flowed through, and the share count has since fallen to 23,470,000. The TTM base is used per the STALE_FY rule. **Caveat that matters:** the TTM window closes June 30, 2026 — it is a *pre-regime-change peak*. It capitalizes mortgage pricing earned under the old FHFA rules. That is handled in the scenario design (multipliers down to 0.60, 45% of probability on bear-or-worse), not by haircutting the filing-derived base — and the verdict is the same on either base (see method range).

## Moat: 6/10 — strong franchise, one pillar was a regulation
Justification: measured economics are wide-moat, but the richest pillar — the GSE mortgage mandate — was a rule, and the rule changed in September 2026.
- FOR: FICO Score is the embedded standard across auto, card, personal-loan and mortgage underwriting; lender models, securitization and investor reporting are built around it. Proven pricing power — repeated per-score price increases with no volume loss through FY2026 (mortgage origination revenue +97% YoY in Q3 FY26 on low-single-digit volumes). **ROIC proxy (fundamentals.json): 27.0% FY20 → 44.0% → 46.8% → 48.1% → 53.5% → 63.9% FY25; gross margin 72.1% → 82.2% over the same years; TTM operating margin 51.7%.** Software platform diversifying the base: Platform ARR +62% to $413M in Q3 FY26, 51% of total ARR of $816M.
- AGAINST: the mortgage monopoly was regulatory, not structural — FHFA put VantageScore 4.0 on the same pricing grid (Sept 29–30, 2026, upfront fees aligned) and Rocket Mortgage made VantageScore its default for eligible loans from Q4 2026; FICO Score 10T is not yet eligible for loan delivery. Distribution conflict: the three bureaus that distribute FICO scores jointly own VantageScore and price it far below FICO ($4.50/score committed through 2027 vs FICO's $10 per-score option). Mortgage concentration: originations were 62% of Scores revenue in Q3 FY26, and the growth is price-led — exactly the leg now contested. Leverage is rising into the fight (debt to $5.58B by June 2026 after $3.1B of 9M FY26 buybacks). Software ex-platform is shrinking: Software revenue +2% in Q3 FY26, non-platform ARR −17%.
- Why not 7+: the rubric asks for ROIC well above the cost of capital *through a cycle*. FICO's ROIC history was earned under a mandated monopoly; the post-change cycle test started in September 2026 and is unresolved. A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — final run (2026-10-17)
Growth sanity check (mandatory): the engine blend is 16.80% (rev CAGR 5y 8.99%, 3y 13.07%, latest YoY 15.91%, OE/share CAGR 2y 36.29%, +2.31pp buyback adjustment). The latest *prints* are higher — Q3 FY26 revenue +25.7%, FY26 revenue guidance raised to $2.53B (+27% vs FY25). **Scenario starts are set below those prints, with the reason written here:** those prints predate the regime change and are mortgage-price-led (+97% mortgage origination revenue on low-single-digit volumes). The Sept 29–30, 2026 FHFA single-pricing-grid and fee alignment targets exactly that price ladder; the largest mortgage originator defaults to the rival score from Q4 2026; one bank estimate (Jefferies, per press coverage) puts the EBITDA hit at ~20% if VantageScore gains real traction. Underwriting forward growth off the peak prints would capitalize a pricing regime that no longer exists. Starts: super bear −0.2% (offsets −0.17 vs blend), bear 5.8%, **base 11.8%**, bull 17.8%, super bull 23.8% — even the super bull sits at/below the current print, deliberately: 26%+ growth requires the price ladder to survive intact, which is the bull assumption, not a given. Multipliers encode the OE-level reset (0.60 super bear = mortgage pricing largely competed away; 0.95 base = partial give-back offset by non-mortgage and platform growth). Probabilities shifted bear-ward (15/30/30/17/8 vs the 10/25/30/25/10 default) because the adverse event has already happened — this is not a tail risk, it is the current rulebook. Price $771.19.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -0.2% | 0.60 | VantageScore takes mortgage share fast; per-score pricing resets toward the rival; levered OE shrinks | $152.77 | 4.89% |
| Bear | 30% | 5.8% | 0.80 | Meaningful mortgage share/price erosion over 2-3 years; software offsets only part | $266.05 | 6.95% |
| Base | 30% | 11.8% | 0.95 | Adoption is slow (multi-year lender/securitization integration), FICO's direct-license program defends economics, non-mortgage + platform carry growth | $412.46 | 9.56% |
| Bull | 17% | 17.8% | 1.05 | Lenders pull both scores; Classic FICO + 10T retain mortgage; platform ARR keeps compounding | $594.33 | 12.49% |
| Super bull | 8% | 23.8% | 1.15 | VantageScore stalls, pricing power survives, software re-accelerates | $846.74 | 15.98% |

- **Probability-weighted: IV@15% $395.24 (−48.7% vs price), IV@12% $537.03 (−30.4%), IV@10% $696.75, weighted IRR 9.33%, base-case IRR 9.56%**
- **Tier by numbers: D.** Diagnostics (key_numbers.md): OE yield 4.54%, terminal value 21.1% of IV@15%, scenario spread 5.54x, net debt 3.40x normalized OE, 12.5 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 12.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q3 FY26 (June 30, 2026), legs quoted above.
- **BUYBACK_TAILWIND** (share count −2.31%/yr): already credited via the +2.31pp growth adjustment in the blend; not double-counted. Note the tailwind is now debt-funded ($3.1B in 9M FY26 against $777,880,000 YTD OCF), which converts an equity tailwind into the HIGH_NET_DEBT problem below.
- **WIDE_SCENARIO_SPREAD** (5.54x): real — the outcome range genuinely is this wide one month after a regime break. Confidence capped at medium; verdict sized to the bear end per TIER_BAND.
- **HIGH_NET_DEBT** (net debt 3.40x normalized OE on the FY25 balance sheet): understated by the filed snapshot — total debt reached $5.58B by June 2026 (press coverage of the 10-Qs) after the $1.5B term loan funded an accelerated repurchase. Bear cases are stressed accordingly (OE multipliers 0.60/0.80 carry 45% of the probability). The debt is termed-out investment-grade paper against an 82%-gross-margin royalty stream, so this is an equity-cushion issue, not a solvency call — but levered OE/share falls faster than revenue in the bear paths.
- **TIER_BAND** (bear tier D at 6.95% vs bull tier C at 12.49%): verdict sized to the bear end — the final tier is D, and even the bull case does not clear 15%.

## My thoughts / overlay
- The honest headline is that the *price* is the story, not the business quality. The stock is down ~60% in 2026 (from a $1,690.62 close at Dec 31, 2025, per press coverage) and it is *still* roughly twice the probability-weighted IV@15%. The market is pricing a much softer landing than even this run's bull case: at $771.19 the implied weighted IRR is 9.33%, and only the super-bull path (8% weight) clears 15%.
- Method range: on the engine's normalized median base ($18.93/share, default scenarios) the preliminary run printed weighted IRR 7.86% and weighted IV@15% $298.45 — Tier D as well. Base choice moves the number, not the verdict: D on both.
- What would change the answer: two or three quarters of post-Sept-2026 mortgage score revenue holding up (first real read: Q1 FY27, the December quarter, when Rocket's VantageScore default is live), 10T gaining GSE delivery eligibility, or the price falling toward the hurdle levels — the weighted path clears 15% at $395.24, 20% at $269.91, 25% at $202.42.
- Watch items: the announced ~15% workforce reduction (Oct 6, 2026, ~570 roles, ~$27M pretax charges, AI restructuring) — cost support for OE if mortgage revenue erodes, but also a signal management sees the same pressure; short interest ~10% of float (press coverage) says the bear case is crowded, which cuts both ways.
- Earnings quality note: SBC is $174,289,000 TTM, 17.4% of TTM OCF — real and fully charged in the base. Capex is genuinely negligible ($5,526,000 TTM). This is as clean an owner's-earnings stream as the sweep will see; the problem is purely what multiple of a possibly-peak stream the price demands against $5.58B of debt.

## Final verdict
- **Final tier: D** (weighted IRR 9.33% on the final inputs; bear D 6.95% → bull C 12.49%, super-bull best case 15.98%)
- Confidence: **Medium** (filing data complete, TTM base filing-derived; capped by the 5.54x scenario spread and a regime break whose first hard data arrives next quarter)
- One-liner: Elite scoring franchise, moat 6/10 with the mortgage pillar cracked by FHFA — even on peak pre-change TTM OE of $35.01/sh, weighted IRR is only 9.3% at $771.19 (weighted IV@15% $395.24); clears the 15% hurdle only below ~$395.
