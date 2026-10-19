# EHC — Encompass Health Corporation
Pass-1 run, 2026-10-18. Engine 5.4.0. Price $127.87 (nasdaq_quote_api), market cap $13.068B — in scope under $40B.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, or fundamentals.json — none are recomputed.

## What it is
The largest owner and operator of inpatient rehabilitation hospitals (IRFs) in the United States: 173 hospitals and 11,465 licensed beds at FY2025-end (10-K, via research), roughly 22% of Medicare IRF discharges, 66 joint ventures with acute-care health systems. Pure-play IRF since the Enhabit home-health/hospice spin-off (July 2022). Revenue is reimbursement-driven: Medicare fee-for-service is the anchor payer, Medicare Advantage and managed care the rest. Q2 2026 (10-Q through 2026-06-30): revenue +9.6% YoY, discharges +5.6%, net revenue per discharge +3.9%; management raised FY2026 guidance to revenue $6.41–6.49B and adjusted EPS $6.02–6.25, and CMS's FY2027 IRF final rule adds an estimated ~2.3% to Medicare net revenue per discharge from 2026-10-01.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow (continuing operations) $1,175.6M; capex $736.4M; SBC $56.5M.
- **Conservative owner's earnings FY2025: $382.7M = $3.74/share** (latest FY OE/share, dcf_numbers.json)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $529.4M — HIGHER than the conservative figure, and rejected: it caps capex at D&A ($327.9M) while actual capex ran $736.4M, i.e. the de novo hospital buildout is real cash out the door, not an accounting choice. The OCF-based conservative figure is the honest one for a hospital builder.
- OE positive 5 of the last 5 fiscal years. Net debt $2,418.6M (total debt $2,490.8M less cash $72.2M, dcf_numbers.json basis), plus operating lease liabilities of $223.1M.
- The 2021–22 trough is visible in the history: OE/share fell to $1.62 / $1.11 as capex climbed ($524.6M → $564.8M) while OCF stalled (~$706–716M) through the COVID / premium-labor crisis, then recovered to $2.14 / $3.05 / $3.74 (FY2023–25) as premium labor normalized and OCF rose to $1,175.6M.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,175,600,000 − prior YTD $558,800,000 + current YTD $595,700,000 = **TTM $1,212,500,000**
- Capex: FY $736,400,000 − prior YTD $320,000,000 + current YTD $382,700,000 = **TTM $799,100,000**
- SBC: FY $56,500,000 − prior YTD $23,800,000 + current YTD $25,300,000 = **TTM $58,000,000**
- Shares (current-YTD weighted diluted): **100,300,000**
- **TTM OE total $355,400,000 → base OE/share $3.5434** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $3.0528/share and the latest FY is $3.7446/share; the TTM base sits between them. TTM OE is below FY2025 despite revenue growth because TTM capex ($799.1M) is running above the FY2025 level — the buildout is accelerating (8 hospitals planned for 2026), and that cash cost lands in OE immediately while the new beds ramp over years.

## Moat: 5/10 — moderate / narrow
Justification: genuine scale, CON and referral-network advantages in a supply-constrained niche, but CMS sets the price, labor is ~52% of revenue, and measured returns on capital have historically sat around the cost of capital — scale converts into volume, not into wide-moat economics.
- FOR: Largest US IRF operator (~22% of Medicare IRF discharges; 173 hospitals) — scale in recruiting, purchasing, clinical protocols and payor contracting that sub-scale rivals cannot match; certificate-of-need regimes in many states cap new competing supply while national IRF bed supply has been roughly flat for a decade against an aging Medicare population; 66 joint ventures with acute-care systems hard-wire the referral pipeline; clinical outcomes above industry averages (Q2 2026 discharge-to-community 84.7%) reinforce referral preference.
- AGAINST: No real pricing power — Medicare rates are set by CMS annual rule (~+2.3% estimated for FY2027) and managed-care rates follow; ROIC proxy (fundamentals.json) ran only 8.7–11.3% across 2016–2022, around the cost of capital, and the company files no COGS split (gross margin is not filed; operating margin ran 12.4–16.1% in the filed years 2016–2022); labor is the business — salaries and benefits ~52% of revenue with guided wage inflation of 3.5–4% for 2026, at or above the pricing update; payer concentration and administrative denial risk (Medicare RCD reviews, Medicare Advantage utilization management, the TEAM episodic model from 2026); local competition for referrals and staff from Select Medical, PAM Health, ScionHealth and hospital-owned units; growth itself consumes the cash — $799.1M TTM capex against $1,212.5M TTM OCF.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — final run (2026-10-18)
Growth sanity check (mandatory): the engine blend is 10.23%, built from revenue CAGRs of 10.73% (5y) / 10.92% (3y), latest FY YoY +10.46%, and a 32.16% OE/share CAGR that is a trough-recovery artifact off 2022. Current prints: Q2 2026 revenue +9.6%, TTM revenue +9.47% YoY (fundamentals.json), FY2026 guidance $6.41–6.49B = roughly +8–9% over FY2025. The base start was therefore recalibrated slightly down to 9.23% (offset −0.01), and the default super-bull start of 22.23% — more than double any revenue print in the company's history — was cut to 17.23%, still generous (capacity ramp + North Carolina CON repeal + FY2027 rate rule). Offsets used: −0.10 / −0.05 / −0.01 / +0.03 / +0.07. Probabilities 10/30/30/20/10 — bear weight raised from the 25% default per the OE_VOLATILE flag. OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Base OE/share $3.5434 (TTM). Price $127.87.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 0.2% | 0.75 | CMS rate squeeze + wage inflation above pricing; buildout capex keeps eating OE | $19.82 | 4.39% |
| Bear | 30% | 5.2% | 0.90 | Growth halves; labor pressure and MA denials compress conversion | $29.29 | 5.44% |
| Base | 30% | 9.2% | 1.00 | Guidance-level growth decays over the CAP; capex intensity persists | $38.40 | 6.47% |
| Bull | 20% | 13.2% | 1.10 | New beds ramp fast, NC/CON openings add a second leg | $49.78 | 7.73% |
| Super bull | 10% | 17.2% | 1.25 | Sustained mid-teens growth the company has never printed | $66.56 | 9.47% |

- **Probability-weighted: IV@15% $38.90 (−69.6% vs price), IV@12% $52.19, IV@10% $67.08, weighted IRR 6.55%, base-case IRR 6.47%**
- **Tier by numbers: D — and D in the bear AND bull cases alike; even the super-bull scenario IRR (9.47%) does not reach Tier C's 10% floor.**
- Diagnostics (dcf_numbers.json): OE yield 2.77%, terminal value 19.7% of IV@15%, scenario spread 3.36x, net debt 6.68x normalized OE, 9.6 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.6 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, legs quoted above.
- **OE_VOLATILE** (OE/share spans >3x over 5 years: $1.11 → $3.74): real and explained — the 2021–22 premium-labor/COVID trough plus a rising capex curve, then recovery. Handled with the normalized-vs-TTM cross-check (TTM $3.54 sits between the $3.05 median and $3.74 latest FY) and by raising the bear probability to 30%.
- **NI_OCF_DIVERGENCE** (>40% in 2023, 2024, 2025): structural, not a one-off. The largest single reconciling item each year is D&A on the hospital asset base ($273.9M / $299.6M / $327.9M in 2023/24/25 against gaps of $498.8M / $547.0M / $609.4M), with SBC ($50.6M / $48.3M / $56.5M) and working-capital/other non-cash items making up most of the rest; the OCF series is also tagged on a continuing-operations basis. Because the base is built from OCF directly, the divergence does not contaminate it — and the NI-based maintenance OE is the flattering one here (see Owner's earnings), so the conservative series is the right side to err on.
- **HIGH_NET_DEBT** (net debt 6.7x normalized OE in the final run; 7.8x in the preliminary): balance sheet from the filing (dcf_numbers.json): total debt $2,490.8M, cash $72.2M, net debt $2,418.6M, plus $223.1M operating lease liabilities. The OE multiple overstates the strain — OE is measured after full growth capex — but the leverage is real: the de novo program is debt-funded, and a reimbursement or labor shock would hit a levered, capex-committed P&L. Reflected in the 30% bear weight and the super-bear OE multiplier.
- **WIDE_SCENARIO_SPREAD** (preliminary run, 4.47x): after recalibrating the scenario starts to the company's actual prints the spread is 3.36x (dcf_numbers.json). Still wide — confidence is capped at medium, and the verdict is sized to the conservative end. Note the spread does not threaten the verdict: every scenario, super bull included, lands in Tier D.

## My thoughts / overlay
- This is a valuation verdict, not a quality verdict. The operating business is executing: discharges +5.6%, revenue per discharge +3.9%, guidance raised twice, buybacks cut the diluted count to 100.3M, premium labor fading. The problem is arithmetic: at $127.87 the market is paying ~36x TTM owner's earnings (OE yield 2.77%) for a business whose owner earnings are structurally capex-hungry — TTM capex consumed 66% of TTM OCF.
- Method range: the preliminary default run (median base $3.05, default scenarios) gave weighted IRR 6.41% / IV@15% $36.87; the final TTM-base run gives 6.55% / $38.90. Every defensible variation lands in the same place — Tier D — because even a 17.2% growth start at a 1.25x OE multiplier only produces a 9.47% IRR. The price, not the assumptions, is the outlier.
- What would have to be true: sustained mid-teens OE/share growth for a decade with capex intensity falling sharply as the buildout matures — possible if the 2025–26 hospital cohort ramps and build pace slows, but it is not in any print to date, and CMS pricing (~+2–3%/yr) caps the revenue side.
- Watch items: FY2027 CMS pricing realization, wage inflation vs the 3.5–4% guide, RCD affirmation rates broadening beyond Alabama, TEAM-model referral effects, and whether capex intensity (capex/OCF) ever steps down.

## Final verdict
- **Final tier: D** (weighted IRR 6.55%; bear and bull tiers are also D; hurdle prices from dcf_numbers.json: clears 15% only at or below $38.90, 20% at $27.03, 25% at $20.56 — vs the $127.87 price)
- Confidence: **Medium** (high that the tier is D — it holds in all five scenarios; medium on the exact IV, given the 3.36x scenario spread and the leverage)
- One-liner: Durable IRF leader, moat 5/10 — good business, impossible price: weighted IRR 6.5% and IV@15% $38.90 vs $127.87; it only clears the 15% hurdle below ~$39.
