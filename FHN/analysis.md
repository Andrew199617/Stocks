# FHN — First Horizon Corporation
Engine 5.4.0 run, 2026-10-18. All figures copied from dcf_numbers.json, ttm.json, or financials_history.csv — none recomputed.

## What it is
Memphis-based regional bank holding company (~$83.9B assets, FY2025): commercial and consumer banking, wealth management, and specialty finance (including mortgage warehouse lending) across the Southeast and Mid-Atlantic, plus the FHN Financial fixed-income business. Q2 2026: EPS $0.54 (beat $0.52 consensus), net income available to common $260M (+12% YoY), ROTCE 15.2%, NIM 3.49%, CET1 10.5%, tangible book value/share $14.53, $100M of buybacks in the quarter. On Oct 15, 2026 (Q3 call) management announced a ~$4.5B sale of lower-yielding mortgage loans at ~a 10% all-in discount, guided to ~+4% 2027 EPS accretion and ~+150bp ROTCE from it, buybacks resuming in Q4, loan-to-deposit ~88%, NIM expected into the 3.50s.

## Owner's earnings
**FY2025 (10-K via EDGAR, financials_history.csv):** operating cash flow $628,000,000; capex $33,000,000; SBC $61,000,000.
- **Conservative owner's earnings FY2025: $534,000,000 = $1.04/share** (dcf_numbers.json base_oe_latest_per_share)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,013,000,000 — for a bank neither definition is clean: bank OCF swings with loan/deposit balance-sheet flows, not earnings power (see NI_OCF_DIVERGENCE below).
- OE positive 5 of the last 5 fiscal years on the conservative definition, but the series is extremely volatile: OE/share ran $3.87 (FY2022), $2.18 (FY2023), $2.14 (FY2024), $1.04 (FY2025) — and was negative in FY2020 on the same definition.
- Balance sheet (FY2025, financials_history.csv): assets $83,876,000,000; liabilities $74,734,000,000; equity $8,847,000,000. Engine net debt $1,659,000,000 is on a CURRENT_ONLY:ShortTermBorrowings basis — for a bank, "net debt" is not a meaningful leverage measure; deposits and wholesale funding are the balance sheet. Do not read the 1.63x net-debt-to-normalized-OE diagnostic as corporate leverage.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct):**
- OCF: FY $628,000,000 − prior YTD $432,000,000 + current YTD $863,000,000 = **TTM $1,059,000,000**
- Capex: FY $33,000,000 − prior YTD $18,000,000 + current YTD $27,000,000 = **TTM $42,000,000**
- SBC: FY $61,000,000 − prior YTD $33,000,000 + current YTD $27,000,000 = **TTM $55,000,000**
- Shares (current-YTD weighted diluted): **483,334,000**
- **TTM OE total $962,000,000 → base OE/share $1.99** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $2.14/share. The TTM base was used instead: it is more current (through Q2 2026), it sits between the distorted FY2025 print ($1.04) and the median, and it already reflects the H1 2026 OCF recovery. Using the median would raise the weighted IRR by roughly 1pp (preliminary median-base run: 15.37% weighted IRR, Tier B) — that gap is the method range, stated below.

## Moat: 4/10 — weak-to-moderate regional-bank franchise
Justification: a real Southeast deposit and relationship franchise with mid-teens ROTCE in 2025–26, but banking is a commodity product set, the efficiency ratio (~59–60%) is mediocre, there are no network effects or structural cost advantages, and returns through a full credit cycle have been well below the current run-rate.
- FOR: established Southeast/Mid-Atlantic deposit franchise and long client relationships (roots to 1864); diversified fee businesses (FHN Financial fixed income, wealth/trust, mortgage warehouse); ROTCE reached 15.0–15.3% in 2025 through Q2 2026 with disciplined deposit-cost management; CET1 10.5% and consistent buybacks (share count −3.34%/yr) support per-share compounding.
- AGAINST: no network effects, low switching costs, commodity lending/deposit products priced against money-center and larger regional competitors; efficiency ratio 59.88% in Q2 2026 (worse YoY) — no cost advantage; 5-yr EPS growth ~2%/yr and revenue growth lagged peers (the 2020 IberiaBank merger flatters the longer history, see BASIS_BREAK); credit is cyclical — charge-offs and provisions can erase a year of earnings power quickly; the roic_proxy series in fundamentals.json is null for FHN (banks do not file the operating-income tag it needs) and there is no meaningful gross-margin series for a bank, so the return evidence used is ROTCE: ~15% recently, materially lower through prior cycles — not the sustained well-above-cost-of-capital record a 7+ moat requires.
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — final run (2026-10-18)
Growth recalibration (written reason): the engine's blended start is 8.01%, but it is built on distorted inputs — the 5-yr revenue CAGR (8.46%) straddles the 2020 IberiaBank merger, the +3.34pp buyback adjustment is applied on top of revenue components, and the OE/share 2-yr CAGR is −30.79%. The cleaner signals: 3-yr revenue CAGR 2.16%, latest FY revenue YoY +7.18%, Q2 2026 revenue +7% YoY with NII +5% and fee income +12%. Scenario starts were therefore set via offsets (−0.10 / −0.06 / −0.02 / +0.015 / +0.05 vs g_base) to −2.0 / 2.0 / **6.0** / 9.5 / 13.0% — the base start sits at the current revenue print, not above it; the bull start (9.5%) is above recent prints on the strength of the mortgage-sale accretion guide (~+4% 2027 EPS, +150bp ROTCE) plus buyback-driven per-share growth, and the super-bull start (13.0%) additionally assumes sustained mid-teens ROTCE. Probabilities 15/30/30/15/10 (bear weight widened per OE_VOLATILE); OE multipliers 0.75/0.90/1.00/1.10/1.25. Price $22.88 (nasdaq_quote_api); market cap $11.694B.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −2.0% | 0.75 | Credit cycle turns; provisions spike, NIM compresses | $10.29 | 7.98% |
| Bear | 30% | 2.0% | 0.90 | Deposit costs stay high, loan growth stalls, expenses keep rising | $14.41 | 10.36% |
| Base | 30% | 6.0% | 1.00 | Current trajectory: mid-single-digit revenue growth, ~15% ROTCE, steady buybacks | $18.67 | 12.76% |
| Bull | 15% | 9.5% | 1.10 | Mortgage-sale accretion lands, NIM into the 3.50s, efficiency improves | $23.45 | 15.29% |
| Super bull | 10% | 13.0% | 1.25 | Durable mid-teens ROTCE with above-peer growth and heavy buybacks | $30.38 | 18.72% |

- **Probability-weighted: IV@15% $18.02 (−21.2% vs price), IV@12% $23.90 (+4.4%), IV@10% $30.44, weighted IRR 12.41%, base-case IRR 12.76%**
- **Tier by numbers: C.** Diagnostics (dcf_numbers.json): OE yield 8.70%, terminal value 18.5% of IV@15%, scenario spread 2.95x, net debt 1.63x normalized OE (bank — not meaningful, see above), 9.6 months since FY end.
- Hurdle prices: clears 15% only at or below $18.02; 20% at $12.74; 25% at $9.82.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.6 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above.
- **BUYBACK_TAILWIND** (share count −3.34%/yr): already credited via the growth adjustment in the blend; the recalibrated scenario starts do not double-count it — per-share growth from buybacks is inside the base/bull stories, not added on top.
- **BASIS_BREAK_SUSPECT**: the 2020 IberiaBank Corporation merger — total assets jumped from $43.3B (FY2019) to $84.2B (FY2020) in financials_history.csv and revenue history straddles the deal; the TD Bank merger agreed in 2022 was terminated in May 2023. Growth inputs were chosen off post-merger signals (3-yr CAGR, latest YoY, current-quarter prints), not the 5-yr CAGR.
- **OE_VOLATILE** (OE/share spans >3x over 5 years): real and structural for a bank — OCF-based OE swings with balance-sheet flows (FY2020 was negative on this definition). Handled by the TTM base, a widened bear weight (45% on bear-or-worse), and low confidence.
- **NI_OCF_DIVERGENCE** (2025: net income $982M vs OCF $628M): bank OCF is driven by loan origination/sale flows and deposit movements, not by an earnings one-off; FY2025 net income was solid (Q4 2025 NIAC $259M, FY2025 ROTCE 15%) while OCF was depressed by balance-sheet growth. This is exactly why the latest-FY OE/share ($1.04) understates earnings power and why neither single-year figure is trusted alone.
- **CASH_INCLUDES_RESTRICTED**: the filed cash tag is the combined cash + restricted-cash total with no separating restricted-cash tag, so engine net debt is understated by the restricted amount. Noted; for a bank the net-debt figure is not used in the verdict (see Owner's earnings).
- **SECTOR_MODEL_MISMATCH** (Finance): accepted — the OE/capex DCF fits banks poorly (capex is trivial, OCF is balance-sheet noise, value lives in ROTCE vs cost of equity and tangible book). Confidence is low and the verdict is sized to the bear end, per spec.
- **BASE_DIVERGENCE** (latest FY $1.04 vs 3-yr median $2.14): the latest FY is the distorted one (OCF collapse against $982M of net income, above). The TTM base ($1.99) was used — close to the median but current through Q2 2026.
- **TIER_BAND** (bear C at 10.36% vs bull B at 15.29%): the verdict spans tiers; sized to the bear end — final tier C, not B.

## My thoughts / overlay
- The honest headline is the method range: on the engine's median base the preliminary run printed Tier B (weighted IRR 15.37%, IV@15% $23.60); on the TTM base with recalibrated bank-appropriate growth it prints Tier C (12.41%, IV@15% $18.02). For a bank trading at ~1.57x tangible book ($14.53 TBVPS at Q2 2026) with ~15% ROTCE, a low-teens IRR is the believable center — the price already capitalizes the current ROTCE holding.
- Quality is adequate, not elite: disciplined credit (Q2 2026 net charge-offs 0.20% of loans, ACL 1.24%), CET1 10.5%, real buybacks — offset by a ~60% efficiency ratio, rising expenses (+8% YoY in Q2 2026), and deposit-cost pressure.
- The Q3 2026 mortgage-loan sale is a genuine positive for returns mix (+150bp guided ROTCE) but is a one-time portfolio trade, not a growth engine; it is in the bull case, not the base.
- Margin of safety: none at $22.88 on these numbers — the weighted IV@15% sits 21.2% below the price. The stock clears Andrew's 15% hurdle only at or below $18.02.

## Final verdict
- **Final tier: C** (weighted IRR 12.41% on the TTM base; method range C to B across the median-base preliminary run)
- Confidence: **Low** (SECTOR_MODEL_MISMATCH for a bank, OE_VOLATILE, TIER_BAND — per spec a finance name is graded low)
- One-liner: Adequate regional bank, moat 4/10 — does not clear 15% at $22.88 (weighted IRR 12.4%, IV@15% $18.02); it clears 15% only at or below $18.02, and the bank model fit is poor so size any interest to the bear case.
