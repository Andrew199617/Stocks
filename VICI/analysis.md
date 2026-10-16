# VICI — VICI Properties Inc.
v5 run, 2026-10-15. In scope (market cap $24.548B at $23.10, nasdaq_quote_api).

All figures below are copied from dcf_numbers.json, ttm.py output (ttm.json), financials_history.csv, or cited Q2 2026 reporting — none are recomputed.

## What it is
An experiential real estate investment trust spun out of Caesars in 2017. It owns marquee gaming and leisure real estate — Caesars Palace Las Vegas, MGM Grand, The Venetian Resort Las Vegas among them — and leases it back to operators under long-term triple-net leases: the tenant pays rent plus taxes, insurance, and maintenance. VICI does not operate casinos; it collects contractual rent with built-in escalators (fixed 1–2% bumps or CPI-linked, per its supplemental reporting). Reported portfolio markers from Q2 2026 coverage: ~100% occupancy and a weighted-average lease term of roughly 39–40 years including renewal options.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $2,509,991,000; capex $1,335,000 (triple-net tenants bear property costs, so landlord capex is structurally tiny); SBC $16,195,000 (always a real cost, but immaterial here).
- **Conservative owner's earnings FY2025: $2,492,461,000 = $2.35/share** (base_oe_latest_per_share $2.3454)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $2,777,795,000 — above the conservative figure, so the OCF-based number is the conservative anchor, as intended.
- OE positive 5 of the last 5 fiscal years. Net debt $16,209,762,000 (dcf_numbers.json).
- Caveat inherent to the model: for a REIT the "owner's earnings" here is effectively an AFFO-like cash figure — rent collected minus minimal landlord capex and SBC — and it ignores the equity issuance VICI needs to fund growth (see DILUTION below). That is why confidence is low even though the cash stream itself is contractual.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $2,509,991,000 − prior YTD $1,231,758,000 + current YTD $1,360,042,000 = **TTM $2,638,275,000**
- Capex: FY $1,335,000 − prior YTD $828,000 + current YTD $794,000 = **TTM $1,301,000**
- SBC: FY $16,195,000 − prior YTD $7,343,000 + current YTD $8,734,000 = **TTM $17,586,000**
- Shares (current-YTD weighted diluted): **1,079,442,313**
- **TTM OE total $2,619,388,000 → base OE/share $2.43** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $2.2492/share. The TTM base was used because the FY ended 9.5 months ago (STALE_FY) and the TTM figure is filing-derived and higher on contractual rent growth, not on a one-off: Q2 2026 reporting showed revenue up ~5.7% YoY and AFFO per share up 4.6% YoY, with FY2026 AFFO guidance raised to $2.45–$2.47 per share — the TTM OE/share of $2.43 sits right against that guided range, which cross-checks it. (Q2 2026 GAAP net income fell sharply on a large non-cash CECL allowance change; the OCF-based OE series is unaffected by that reserve accounting, which is one reason the conservative OCF definition is the right series here.)

## Moat: 7/10 — strong, capped by concentration
Justification: the assets are effectively irreplaceable (scarce Las Vegas Strip frontage, extreme replacement cost, gaming-license regulatory barriers) and the cash flows are locked in by ~39–40-year triple-net leases with contractual escalators and a perfect recent rent-collection record, including through COVID. That durability is offset by extreme tenant and geography concentration, zero operating control, and a growth model that must be bought with external capital.
- FOR: Irreplaceable Strip assets — scarce frontage, tens of billions in replacement cost, no developable Strip land left; ~39–40-year weighted-average lease term (incl. renewals) with 1–2% fixed or CPI-linked escalators; triple-net structure pushes taxes, insurance, and maintenance onto tenants; 100% occupancy and rent collected in full through COVID; tenants are largely publicly traded operators (77% of rent per supplemental reporting).
- AGAINST: Tenant concentration — Caesars and MGM together account for roughly 70%+ of rent, Las Vegas roughly half; a single master-lease restructuring hits cash flow directly; no operating business or pricing control — rent growth is capped by the escalators; growth is externally funded (debt + equity issuance), so per-share growth structurally lags portfolio growth; rate-sensitive — a long-duration contractual rent stream trades like a bond when real yields rise.
- A 7 gives CAP = 11.1 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 11.1 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Growth calibration (written reason): the engine's blended growth is 10.24% before the −5pp share-count adjustment, giving g_base 5.24%. Two blend components are acquisition artifacts, not organic growth (revenue CAGR 5y 26.73% and 3y 15.49% both straddle the 2022 MGM Growth Properties acquisition, the Venetian purchase, and the Jan 2023 MGM Grand/Mandalay Bay JV buyout — see BASIS_BREAK_SUSPECT). The signals that mean something — latest revenue YoY +4.08%, OE/share CAGR 2y +4.98%, Q2 2026 AFFO/share +4.6% YoY — center on ~5%, so the base start was left at g_base (offset 0). The default bull/super-bull offsets (+5/+12pp → 10.24%/17.24% starts) were recalibrated down to +3/+6pp (8.24%/11.24% starts): a triple-net landlord whose rents escalate 1–2% contractually cannot print 17% per-share OE growth without transformational M&A, and pencilling that in as a 10% scenario would repeat the basis-break error. Bear/super-bear offsets were likewise narrowed (−4/−7pp) because contractual rent does not fall off a cliff absent tenant distress. Probabilities 10/30/30/20/10 — bear weighted above default for the leverage and concentration (HIGH_NET_DEBT), bull below default because upside is escalator-plus-deals, not operating leverage. OE multipliers kept at defaults 0.75/0.90/1.00/1.10/1.25. Price $23.10.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -1.76% | 0.75 | A top tenant (Caesars/MGM) restructures a master lease; rent cut, growth negative | $12.21 | 8.86% |
| Bear | 30% | 1.24% | 0.90 | Escalators only, no accretive deals; higher-for-longer rates pressure the multiple | $16.87 | 11.58% |
| Base | 30% | 5.24% | 1.00 | Escalators plus steady sale-leaseback accretion at recent pace (Golden Entertainment-type deals) | $22.64 | 14.76% |
| Bull | 20% | 8.24% | 1.10 | Sustained accretive deal flow into non-gaming experiential assets without heavy dilution | $28.71 | 17.78% |
| Super bull | 10% | 11.24% | 1.25 | Transformational accretive M&A plus CPI escalators running hot | $37.62 | 21.74% |

- **Probability-weighted: IV@15% $22.58 (−2.2% vs price), IV@12% $30.06 (+30.1%), IV@10% $38.43, weighted IRR 14.73%, base-case IRR 14.76%**
- **Tier by numbers: C.** Diagnostics (dcf_numbers.json): OE yield 10.50%, terminal value 19.0% of IV@15%, scenario spread 3.08x, net debt 6.29x normalized OE, 9.5 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above, and it cross-checks against the raised FY2026 AFFO guidance of $2.45–$2.47/share from Q2 2026 reporting.
- **DILUTION** (share count +6.5%/yr): real and structural, not SBC-driven — SBC is only $17,586,000 TTM. VICI funds acquisitions with equity (e.g. shares issued to Golden Entertainment holders in the 2026 Nevada sale-leaseback, per Q2 2026 call reporting; the count rose from 1,056,852,269 weighted diluted in prior-YTD to 1,079,442,313 in current-YTD per ttm.json). The engine already deducted the maximum −5pp via the share-count adjustment; the scenario calibration above additionally refuses to credit acquisition-driven revenue CAGRs as organic growth. Per-share, not portfolio, growth is what this DCF prices.
- **BASIS_BREAK_SUSPECT** (>60% revenue jump in last 5 yrs): identified — 2022 was a transformation year: the MGM Growth Properties acquisition closed Apr 2022, the Venetian land/real-estate purchase closed Feb 2022, and the remaining 49.9% of the MGM Grand/Mandalay Bay JV closed Jan 2023. Revenue went from $1,509,568,000 (FY2021) to $2,600,697,000 (FY2022) to $3,611,988,000 (FY2023) on consolidation, not organic growth. Growth inputs were therefore anchored on latest YoY (+4.08%), OE/share CAGR (+4.98%), and current AFFO/share prints (+4.6%), not on the 5y/3y revenue CAGRs.
- **SECTOR_MODEL_MISMATCH** (Real Estate): stands — an OE/capex DCF fits REITs poorly (it ignores NAV, cap-rate marks, and the dividend-payout structure, and VICI's near-zero capex makes the conservative OE look better than a maintenance-capex business's would). Confidence graded **low** and the tier treated as soft, per spec.
- **HIGH_NET_DEBT** (net debt $16,209,762,000, 6.29x normalized OE): folded into the verdict — leverage is why bear carries 30% weight and why the super-bear case assumes a lease restructuring rather than a soft patch. Mitigants from Q2 2026 reporting (cited, not engine figures): debt is overwhelmingly fixed-rate, weighted-average rate 4.45%, liquidity $2.5B, and net debt/EBITDA was reported at 4.9x, inside the company's 5.0–5.5x target range. Leverage is manageable for a landlord with 40-year leases; it is the equity cushion that is thin if rent is ever renegotiated.
- **WIDE_SCENARIO_SPREAD** (preliminary run 4.50x): the recalibrated final run narrows the IV@15 spread to 3.08x and the flag no longer fires; uncertainty is still material (super-bear IV $12.21 is roughly half the price), so confidence stays low on the sector flag alone and the verdict is sized to the conservative end.

## My thoughts / overlay
- The honest headline: this is a high-quality contractual rent stream priced to deliver just under the 15% hurdle on filing-derived numbers. The preliminary default run (median base $2.2492/share, default offsets) gave weighted IRR 14.50% / IV@15 $22.13; the final TTM run gives 14.73% / $22.58. Both are Tier C — the method range here is narrow (C either way), unlike an inflection name, because the cash flows are contractual and the argument is only about the price of the stream.
- The OE yield of 10.50% on the TTM base is the story: at $23.10 the market is already paying for the escalators and a normal deal pace. Nothing in the recent prints (revenue +4.08% latest FY YoY, AFFO/share +4.6% in Q2 2026) supports underwriting more than ~5% per-share growth, and the two things that could break the stream — a Caesars or MGM master-lease event and a sustained high-real-yield regime — are both live, named risks, not tail hypotheticals.
- Balance sheet: net debt $16,209,762,000 is 6.29x normalized OE. For a triple-net landlord with ~40-year leases and mostly fixed-rate debt that is serviceable, but it leaves no room for a rent renegotiation to be painless.
- Hurdle math: the weighted IV@15% is $22.58 — the price at which the weighted case clears exactly 15%. At $23.10 the stock sits just above it, returning 14.73% weighted — a near-miss, not a bargain. A margin of safety against the bear case ($16.87) would require a price well below the weighted IV; nothing here clears 15% with room to spare.

## Final verdict
- **Final tier: C** (weighted IRR 14.73% on the v5 final inputs; Tier C on both the preliminary and final defensible runs)
- Confidence: **Low** (SECTOR_MODEL_MISMATCH — OE/capex DCF fits a REIT poorly; cash-flow inputs themselves are high-quality and contractual, the model fit is the weak link)
- One-liner: Strong-moat (7/10) triple-net landlord with irreplaceable Strip assets and ~40-year leases, but at $23.10 it returns 14.7% weighted — just under the 15% hurdle; it clears 15% at or below its weighted IV@15% of $22.58, with tenant concentration and 6.3x net debt/OE as the standing risks.
