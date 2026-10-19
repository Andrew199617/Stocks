# EG — Everest Group, Ltd.
Engine 5.4 run, 2026-10-17. In scope (market cap $16.187B at $389.10, nasdaq_quote_api).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, or the filer's own 10-K text — none are recomputed.

## What it is
Bermuda-domiciled global (re)insurer (founded 1973 as Prudential Reinsurance; S&P 500). Two engines: a reinsurance treaty book that earns (FY2025 segment combined ratio 91.7%; 87.2% in Q1 2026 and 88.5% in Q2 2026 for the treaty segment, per company reporting) and a primary insurance book that blew up on U.S. casualty social inflation. Management is exiting primary retail: on October 26, 2025 it agreed to sell the renewal rights for the commercial retail insurance business in the U.S., U.K., E.U. and Asia Pacific to AIG (~$2B of gross premiums; Everest keeps the legacy liabilities in run-off), sold the Canadian retail arm to Wawanesa (closed 2026), and agreed to sell the Colombian unit to AIG (closing early 2027). The go-forward company is reinsurance plus global wholesale & specialty (specialty premiums +32.9% in Q1 2026, mid-80s attritional combined ratio).

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $3,068M; net income $1,591M; SBC $61M (always a real cost); capex $0 — by filing override, see OVERRIDE.
- **Conservative owner's earnings FY2025: $3.007B = $72.28/share** (key_numbers.md: latest FY OE/share $72.28, latest FY OE total $3.007B).
- OE positive 5 of the last 5 fiscal years.
- The engine-native normalized base (median of last 3 FY OE/share) is **$109.06/share — rejected as the base**: FY2023-24 OCF ($4,553M / $4,957M) capitalized premium growth (float) on a book that has since been put into run-off; on that base the engine prints a 33.27% zero-fill weighted IRR, a fake Tier S (dcf_numbers.json override_impact). This is the insurer-float artifact Andrew's 2026-10-15 rule targets.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $3,068M − prior YTD $2,007M + current YTD $939M = **TTM $2,000M**
- SBC: FY $61M − prior YTD $26M + current YTD $40M = **TTM $75M**
- Capex: **TTM $0**, all three legs filled by the override (see OVERRIDE)
- Shares (current-YTD weighted diluted): **39,300,000** — buybacks are shrinking the count (FY2025 average 41,600,000; shares outstanding 38,342,734 at 2026-07-27; treasury purchases $797M in FY2025 and $1,122M of buybacks TTM per fundamentals.json)
- **TTM OE total $1,925M → base OE/share $48.98** (base_source: ttm_json)
- Cross-check: TTM net income is $1,913M (fundamentals.json) — essentially equal to TTM OE. With the book shrinking, float no longer inflates OCF above earnings; the TTM base is the de-floated one. Q4 2025 OCF was negative (−$398M, fundamentals.json quarterly) as casualty loss payments and the exit hit — the TTM window is not flattered.

## OVERRIDE — capex
- **The gap:** the preliminary run exited 4 with `DATA_GAP:capex` — Everest files no capex under any candidate tag in any year (EDGAR companyfacts, CIK 1095073). Under the v5 data gate, no tier was emitted, correctly.
- **The decision (bounded authority, kind "filing"):** judgment.json carries `capex_override = {value: 0, kind: "filing"}`: the FY2025 10-K's consolidated cash-flow statement has no capex line at all — investing activities are securities/other-invested-asset flows, short-term investments, unsettled transactions and the $331M renewal-rights proceeds — and the statement fully reconciles without one (FY2025: $3,068M − $2,096M − $1,175M − $28M FX = the reported −$231M exactly; FY2024 exact; FY2023 within $1M rounding). The balance sheet carries no property-and-equipment line. Same presentation as the CMPS/DFTX precedents. The override is flagged out-of-band mechanically (band vs a null last-filed value) with an ack_reason recorded; there is no filed value to anchor an estimate to.
- **Measured impact (key_numbers.md):** on the TTM base actually used, nil — base OE/share $48.98 → $48.98, weighted IRR 16.71% → 16.71%. Its effect is binary: without it there is no tier at all. Any real premises spend aggregated inside the filed investing lines is immaterial at this scale (~$1.2/share per hypothetical $50M).

## Moat: 4/10 — weak-to-moderate
Justification: a real reinsurance treaty franchise and scale, but (re)insurance capacity is close to a commodity — no network effects, low switching costs, price set by the cycle — and the returns record confirms it. Evidence: `roic_proxy` and gross margin are not computable for this filer (fundamentals.json carries no operating income or COGS for an insurer), so the substitute is return on equity from filing figures: net income $2,517M on equity $13,202M in the clean year 2023 (~19%), but only $1,373M on $13,875M in 2024 and $1,591M on $15,461M in 2025 (~10% both years) after casualty reserve charges of ~$1.7B in 2024 and $478M more in Q3 2025. Returns through the recent cycle sit near the cost of capital, not well above it — a 7+ moat is not supportable.
- FOR: top-tier global reinsurance treaty franchise (combined ratio 91.7% FY2025; 87.2%/88.5% in Q1/Q2 2026); scale — $45,429M of total investments and cash and $15,461M of equity at FY2025 (10-K), S&P 500 member, investment-grade debt ratings (BBB+/Baa1 senior); Mt. Logan Re sidecar adds fee income and third-party capital leverage on cat business; the wholesale & specialty pivot is working (specialty premiums +32.9% in Q1 2026, mid-80s attritional combined ratio).
- AGAINST: reserve credibility damaged — ~$1.7B casualty charge in 2024 and $478M more in Q3 2025, and the $34,312M of loss and LAE reserves still carries the exited retail book's tail; reinsurance pricing is cyclical and capacity-driven with property-cat pricing softening in 2026 renewals; social inflation on U.S. casualty is industry-wide and was under-reserved here for years; through-cycle ROE ~10% is at, not above, the cost of capital.
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — engine 5.4 final run (2026-10-17)
Growth: the engine blend is 4.65% (rev CAGR 5y 12.76%, 3y 13.20%, latest rev YoY 1.24%, OE/share CAGR 2y −18.58%; share-count CAGR +2.35% applied to the revenue components only). **Sanity check against prints:** revenue itself is shrinking by design (TTM revenue $16,771M vs FY2025 $17,496M, fundamentals.json — the retail exit), so the scenario starts are OE/share figures, not revenue: the base start of 4.7% is carried by reinsurance/specialty growth plus a share count falling ~5%/yr on buybacks, not by premium growth — defensible. The super-bull start of 16.7% needs both underwriting margin expansion and the full buyback pace sustained; it is the 10% tail and is weighted as such. Probabilities shifted to the bear side vs defaults (15/25/30/20/10) because the verdict hinges on reserve adequacy of a run-off book that has already surprised twice; OE multipliers at the defaults 0.75/0.90/1.00/1.10/1.25. Price $389.10.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -7.3% | 0.75 | Run-off book develops adversely again; cat year on top | $205.22 | 8.75% |
| Bear | 25% | -0.4% | 0.9 | Reserves hold but soft pricing caps OE/share; buybacks only offset shrink | $323.85 | 12.86% |
| Base | 30% | 4.7% | 1.0 | Clean reinsurance + specialty growth, buybacks shrink the count | $436.24 | 16.49% |
| Bull | 20% | 9.7% | 1.1 | Hard-market discipline holds; capital return accelerates | $580.16 | 20.70% |
| Super bull | 10% | 16.7% | 1.25 | Reserve releases + premium growth + full buyback pace | $855.79 | 27.64% |

- **Probability-weighted: IV@15% $444.23 (+14.2% vs price), IV@12% $589.11 (+51.4%), IV@10% $750.56, weighted IRR 16.71%, base-case IRR 16.49%**
- **Tier by numbers: B.** Diagnostics (key_numbers.md): OE yield 12.59%, terminal value 18.5% of IV@15%, scenario spread 4.17x, 9.5 months since FY end.
- Hurdle-clearing prices (weighted path): clears 15% below $444.23, 20% below $313.80, 25% below $241.86.

## Flags — every fragility flag resolved
- **STALE_FY** (latest FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above.
- **NI_OCF_DIVERGENCE** (NI vs OCF differ >40% in 2023, 2024, 2025): structural for a growing-then-shrinking insurer, with named one-offs on top. 2023: NI $2,517M vs OCF $4,553M — float growth (reserves and unearned premiums up with premiums). 2024: NI $1,373M vs OCF $4,957M — the ~$1.7B casualty reserve charge is non-cash, so it crushed NI and left OCF. 2025: NI $1,591M vs OCF $3,068M — $478M of Q3 reserve strengthening (non-cash), $28M severance and $83M capitalized-software impairments from the AIG transaction (10-K), partly offset by $68M of income from the renewal-rights sale. Resolution: neither series is "wrong," but OCF in growth years is float, not distributable earnings — which is exactly why the median FY base was rejected, the TTM base (OCF $2,000M ≈ NI $1,913M) was used, and the tier was softened (below).
- **DEBT_TAGS_BLANK** (no debt tag for the latest FY; engine net debt unknown, not zero): balance sheet from the FY2025 10-K — total debt $3,589M (senior notes due 2044/2050/2052 and long-term notes due 2067; EDGAR facts carry $2,352M under LongTermNotesPayable), total investments and cash $45,429M, loss and LAE reserves $34,312M, total liabilities $47,054M, shareholders' equity $15,461M, book value per share $379.83. Leverage is modest for an insurer (debt ~0.23x equity); the balance-sheet risk is reserve adequacy, not debt. Price $389.10 is ~1.02x the $379.83 book value.
- **SECTOR_MODEL_MISMATCH** (Finance): confidence low, and the final tier is softened one notch (see verdict) — the OE/capex DCF is a rough lens on an insurer.
- **OVERRIDE_APPLIED:capex**: see OVERRIDE — gap, decision, and measured impact (nil on the used base; binary unblock) are recorded in judgment.json, dcf_numbers.json and the registry.
- **WIDE_SCENARIO_SPREAD** (4.17x): real — the outcome genuinely hinges on run-off reserve development. Confidence capped at low; verdict sized to the conservative end.
- **TIER_BAND** (bear C 12.86% vs bull A 20.70%): sized to the bear end — the final tier is the bear tier.

## My thoughts / overlay
- The honest headline is the method range: on the float-capitalizing median FY base this prints a fake Tier S (33.27% weighted IRR); on the de-floated TTM base it is B by numbers and C after the insurer softening. Any single EG number quoted without its base is hiding the ball.
- The clean-book story is real: treaty combined ratios of 87-88% in H1 2026, specialty growing double digits, $1,122M of TTM buybacks at ~book value, dividend $8/share TTM (fundamentals.json). If the run-off book merely stops surprising, OE/share compounds nicely from a $48.98 base.
- The bear case is equally concrete: this management team under-reserved U.S. casualty for years, the $1.2B adverse development cover has limits, and Everest keeps 100% of the legacy tail while AIG got the forward book. Two charges in two years is a pattern, not bad luck.
- Price context: at $389.10 the stock trades at ~1.02x book ($379.83) — the market is pricing a roughly adequately-reserved, ~10% ROE insurer. The DCF says the same thing in another language.

## Final verdict
- **Final tier: C** — tier by numbers B (weighted IRR 16.71%), softened one notch under Andrew's insurer-float rule (the OCF base capitalizes float; same treatment as PFG/HIG/ACGL/WRB), landing on the bear end of the tier band. Reason recorded in judgment.json tier_override_reason and score.json.
- Confidence: **low** (SECTOR_MODEL_MISMATCH, WIDE_SCENARIO_SPREAD 4.17x, reserve-tail binary).
- One-liner: Global reinsurer mid-cleanup: quality treaty core (91.7% FY2025 CR, 87-88% in H1 2026) but the OCF base capitalizes float and the exited U.S. casualty book still sits on $34.3B of reserves after ~$2.2B of 2024-25 charges — B by numbers (16.7% weighted IRR, IV@15% $444 vs $389 price), sized down to C per the insurer-float rule and the bear end (C) of the tier band; clears 15% only below ~$444 on these inputs.
- Not alert-eligible (final tier C; alert_eligible: false in score.json).
