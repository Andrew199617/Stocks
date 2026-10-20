# KLAR — Klarna Group plc

Pass-1 run, 2026-10-19 (engine 5.5.0). Price $13.08 (nasdaq_quote_api), market cap $4,848,155,406 — in scope under $40B. UK-incorporated, Swedish-bank-led digital bank and flexible-payments group, listed directly on the NYSE (ordinary shares, IPO 10 Sep 2025 at $40.00/share).

All engine figures below are copied from dcf_numbers.json / financials_history.csv / fundamentals.json — none are recomputed. Company-release and research figures are labelled as such.

## What it is

Klarna sells checkout credit and is becoming a consumer bank: interest-free Pay in 30 / Pay in 4 (merchant pays a fee), interest-bearing Fair Financing loans up to 36 months, the Klarna Card, memberships, and deposit/savings accounts through Klarna Bank AB (Swedish banking licence). Q2 2026 release (company): revenue $1,042M (+27% YoY), GMV $36.6B, 120M active consumers, 1.2M+ merchants (+54%), transaction margin dollars $446M (+42%). Distribution is increasingly default-on inside Stripe, Nexi, Worldpay and JPMorgan Payments, plus Walmart via OnePay and the Apple Upgrade programme. The FY2025 mix shift into Fair Financing is the story of the filed numbers: GMV +22% and revenue +24.8% in FY2025, but credit provisions rose ~60% (company reporting, via research summary) and the P&L flipped back to a loss.

Filed history (financials_history.csv):

| FY | Revenue | Net income | Operating income | OCF | Capex | SBC | OE conservative | OE/share |
|---|---|---|---|---|---|---|---|---|
| 2023 | $2,276,000,000 | -$244,000,000 | -$323,000,000 | $808,000,000 | $85,000,000 | $43,000,000 | $680,000,000 | $1.88 |
| 2024 | $2,811,000,000 | $21,000,000 | -$121,000,000 | $587,000,000 | $45,000,000 | $92,000,000 | $450,000,000 | $1.23 |
| 2025 | $3,509,000,000 | -$273,000,000 | -$230,000,000 | -$1,032,000,000 | $30,000,000 | $157,000,000 | -$1,219,000,000 | -$3.29 |

Capex is almost entirely capitalised intangible assets ($84,000,000 / $44,000,000 / $27,000,000 per capex_provenance) plus $1–3M of PP&E per year — an asset-light platform; the two filed tags in capex_provenance are the whole investing capex the engine reads, and no CAPEX_COVERAGE_LOW flag fired (no D&A tag is filed, so the test cannot run — stated here rather than assumed clean). SBC is rising fast — $43M → $92M → $157M — and diluted shares grew 362,090,644 → 364,412,068 → 370,654,083 (share CAGR 1.17% in dcf_numbers.json).

## Owner's earnings

Two definitions, and at a lender they disagree violently:

- **Conservative (OCF − capex − SBC):** $680,000,000 / $450,000,000 / -$1,219,000,000. For a deposit-funded bank, consolidated OCF is a balance-sheet flow — deposit inflows, consumer-lending book growth and funding movements run through it — not earnings available to common shareholders. FY2023's +$808M OCF beside a -$244M net loss and FY2025's -$1,032M OCF beside a -$273M net loss are the same artifact in opposite directions.
- **Payable earnings (what common shareholders actually earned):** profit attributable to ordinary equity holders -$249,000,000 / $3,000,000 / -$294,000,000 (statements.json `net_income_to_common`; consolidated net income before non-controlling interests was -$244,000,000 / $21,000,000 / -$273,000,000); adjusted operating profit $65M in FY2025 (company release, via research). H1 2026 net income was $1M (Q1) and $9M (Q2) per the company's quarterly releases — the earnings base is currently near zero, not $450M.

**Base used = the 3-year median, $1.2349/share** (base_source: median_of_last_3_fy_oe_per_share; FY2024's OE/share), because the spec's IFRS rule applies: ttm.py reads US-GAAP facts only and exited 3 for KLAR ("no annual (FY) fact" under its candidate tags), so no TTM pin exists and the median base stands. It is used with its distortion disclosed in both directions (see BASE_DIVERGENCE below) and the verdict is corrected for the base's overstatement via the sector tier_override — not by inventing a replacement base.

## MOAT — 4/10

CAP = 7.2 years (growth holds 2 years, then fades to the 2.5% terminal rate over the CAP).

**FOR:**
- Consumer scale: 120M active consumers and 1.2M+ merchants (Q2 2026 release), with purchase-intent data from the shopping app.
- Distribution becoming default-on inside Stripe, Nexi, Worldpay and JPMorgan Payments, plus Walmart via OnePay and the Apple Upgrade programme.
- Swedish banking licence and ~$13B consumer deposits (~91% of funding, research summary of company reporting) — cheaper, stickier funding than wholesale-funded BNPL rivals.
- AI-driven cost base: headcount cut while GMV grew +22% in FY2025.

**AGAINST:**
- No demonstrated pricing power: merchant fees are contested by card schemes, PayPal, Affirm and Afterpay, and checkout placement must be re-won.
- Credit is the product: the fast-growing Fair Financing book (36-month loans) is unseasoned — provisions rose ~60% in FY2025 and flipped the P&L to a loss.
- No through-cycle returns: operating losses in all 3 filed years, ROE -11.1% / +0.9% / -10.2% (fundamentals.json).
- Regulation cuts both ways (EU Consumer Credit Directive, UK FCA, NY BNPL Act) and larger banks / big tech can replicate the offer with cheaper capital.

**ROIC evidence (step 5):** fundamentals.json's roic_proxy series prints 131.5% / 7.8% / 16.2% — it is not meaningful here and is not used as moat evidence: its denominator is equity + debt − cash with every debt tag blank, while a bank's funding (customer deposits) sits inside total liabilities ($16,113,000,000 at FY2025), so the proxy is an artifact of the tag set. Gross margin is likewise not filed (a lender has no COGS line). The honest returns record is ROE above and three straight operating losses — a moat of 7+ on that record would be indefensible; 4/10 prices scale and distribution without pretending the franchise has yet converted them into returns on capital.

## Scenarios

Growth-start sanity check (mandatory): the engine's blended start is 22.97% (rev CAGR 24.1% over the only 3 filed years, latest rev YoY +24.8%). That blend is above what the company itself now guides: FY2026 revenue guidance was cut in August 2026 to $4.08–4.16B (company guidance, via research summary), i.e. roughly +16–19% over FY2025's $3,509,000,000, with Q3 2026 guided soft at $940–980M revenue. Offsets are therefore recalibrated down (−14/−10/−6/0/+6pp) so the base start (16.97%) sits on guidance, the bull start (22.97%) sits at the FY2025 print rather than above it, and super-bull (28.97%) sits just above the Q2 2026 print (+27%) — no scenario needs a "below the latest print" excuse except by the deceleration the guidance itself states. Probabilities are skewed down (15/30/30/20/5 vs the 10/25/30/25/10 default) for the unseasoned credit book, the guidance cut and the announced CFO/CMO departures (research summary). OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25.

| Scenario | Prob | Growth start | OE mult | IV@15 | IRR |
|---|---|---|---|---|---|
| Super bear | 15% | 8.97% | 0.75 | $9.72 | 11.92% |
| Bear | 30% | 12.97% | 0.90 | $13.55 | 15.42% |
| Base | 30% | 16.97% | 1.00 | $17.46 | 18.69% |
| Bull | 20% | 22.97% | 1.10 | $23.91 | 23.41% |
| Super bull | 5% | 28.97% | 1.25 | $33.66 | 29.50% |
| **Weighted** | | | | **$17.23** | **18.47%** |

Tier by numbers: **B** (bear B 15.42%, bull A 23.41%). Hurdle prices: IV@15 $17.23 (+31.7% vs $13.08), IV@20 $11.79, IV@25 $8.84. Diagnostics: OE yield 9.44%, terminal value 20.6% of IV@15, scenario spread 3.46×.

## FLAGS — every flag in dcf_numbers.json resolved

- **STALE_FY** (latest FY ended 10 months ago): TTM attempted — ttm.py exited 3 because it reads US-GAAP facts only and KLAR is an IFRS 20-F filer with no facts under its candidate tags. Per the worker spec's IFRS rule, the median base is used and that is stated here. Interim evidence from the company's own 2026 releases (Q1 net income $1M, Q2 net income $9M, Q2 revenue +27%) shows no TTM earnings base exists that would credibly replace the median — the interim P&L is near breakeven.
- **NI_OCF_DIVERGENCE** (NI vs OCF differ >40% in 2023, 2024, 2025): structural, not a one-off. At a deposit-funded lender, OCF carries deposit inflows/outflows and the growth of the consumer-lending book; the sign flips with balance-sheet growth (FY2023 OCF +$808M vs NI -$244M; FY2025 OCF -$1,032M vs NI -$273M, the FY2025 leg widened by the ~60% rise in IFRS 9 credit provisions on the fast-growing Fair Financing book, per company reporting via research). Resolution: neither figure is trusted as owner's earnings on its own — see the two-definition section and the tier_override.
- **ADS_RATIO_APPLIED** (was ADS_RATIO_MISSING): resolved with judgment.json ads_ratio {ratio: 1.0, kind n/a — the bounded step-8(d) declaration}: Klarna is direct-listed — the 20-F registers the ordinary share itself, the F-1 prospectus offered ordinary shares at $40.00 per ordinary share, and the ordinary shares trade on the NYSE as KLAR. There is no ADS programme, so per-ordinary-share figures compare to the $13.08 price with no scaling; market cap basis in dcf_numbers.json confirms price × shares ÷ 1.0.
- **THIN_HISTORY** (only 3 fiscal years): accepted. EDGAR carries FY2023–FY2025 only (the group listed in Sep 2025); the growth blend is a 3-year CAGR, there is no through-cycle record, and confidence is low partly for this reason.
- **DEBT_TAGS_BLANK** (no debt tag for the latest FY — net debt UNKNOWN, not zero): balance sheet from the filing (financials_history.csv / fundamentals.json, FY2025): total assets $18,797,000,000, total liabilities $16,113,000,000, equity $2,684,000,000, cash $3,803,000,000. The funding is customer deposits and other banking liabilities inside total liabilities (~$13B of consumer deposits, ~91% of funding, per research summary of company reporting), and no balance-sheet tag separates an ending debt stock from them. The financing statement does carry borrowing flows — debt issued $104,000,000 / $264,000,000 / $903,000,000 against repayments of $150,000,000 / $169,000,000 / $86,000,000 in FY2023–25 (statements.json) — so borrowings exist and FY2025 issuance was heavy, but with no tagged ending balance the flows cannot be traced to an outstanding amount, and net debt is therefore still not computed and no leverage verdict is taken from the engine; for a regulated bank the binding constraint is capital against the lending book, not corporate net debt.
- **SECTOR_MODEL_MISMATCH** (Finance): accepted in full — confidence low, and the final tier is sized one notch down (B → C) under Andrew's 2026-10-15 standing rule for financials whose OCF base capitalizes balance-sheet flows, with the quantified gap in judgment.json's tier_override_reason: the $450,000,000 median OCF base vs $3,000,000 of FY2024 profit attributable to ordinary equity holders, a -$294,000,000 FY2025 attributable loss and $65M FY2025 adjusted operating profit.
- **BASE_DIVERGENCE** (latest FY OE/share -$3.29 vs 3-yr median $1.23): both ends are distorted, in opposite directions. The swing is quantified at the level the tagged record supports: the OCF − net income gap is +$1,052,000,000 (FY2023), +$566,000,000 (FY2024) and -$759,000,000 (FY2025), and the balance sheet shows the same FY2025 expansion — total assets grew $4,993,000,000 ($13,804,000,000 → $18,797,000,000) and total liabilities $4,566,000,000 ($11,547,000,000 → $16,113,000,000) as the lending book and deposit base grew. The individual operating-section lines behind the gap (changes in lending to the public, changes in deposits) are tagged with custom elements EDGAR companyfacts does not carry (see Data notes), so the divergence is identified by its filed gap and balance-sheet deltas rather than line by line. The latest FY is distorted down by that FY2025 balance-sheet swing. The median is distorted up because FY2024's OCF likewise includes balance-sheet inflows while its payable earnings (attributable) were $3,000,000. The median is kept as the engine base per the IFRS rule (no TTM exists), the overstatement is corrected at the tier level (override to C), and the method range below states the consequence plainly.
- **TIER_BAND** (bear B 15.42% vs bull A 23.41%): sized to the bear end — and then one notch below it (final C) for the sector reason above. No position sizing should use the bull end.

## Thoughts / method range

The honest headline is the method range, not the single tier. On the engine's OCF-median method the name prints B (18.47% weighted, IV@15 $17.23 vs $13.08). On payable earnings — three filed years of net income averaging negative, $65M of FY2025 adjusted operating profit, near-zero H1 2026 net income — there is no positive owner's-earnings base to capitalize at all, which in this system is F-territory until the lending book seasons profitably. The final C sits between those, per the standing one-notch rule; it is a policy grade, not a measurement. What would change the verdict: two or three years of Fair Financing vintage data with provisions stable as a share of GMV (Q2 2026 printed 0.52% of GMV vs 0.56% a year earlier — one encouraging quarter, per the company release), sustained GAAP profitability, and SBC growth ($43M → $157M in two years) brought under control. The price has already fallen from the $40.00 IPO price to $13.08; that de-rating is the market pricing the same credit-credibility question this analysis cannot resolve from three filed years.

## Verdict

**Tier C (final; B by numbers, notched down for the sector misfit), confidence low.** Weighted IRR 18.47% on the OCF method, IV@15 $17.23 — but the base overstates payable earnings by an order of magnitude, so the name does not clear Andrew's 15% hurdle on the earnings common shareholders actually receive. Not alert-eligible: sector model misfit suppression applies.

## Data notes (enrichment, step 9)

All six enrichment steps ran. fundamentals.json / segments.json / profile.json / street.json written (segments: product and geography revenue tables from the 20-F; Street consensus Hold, target $17.77 per profile.py). statements.py warning, non-blocking: for FY2025 the filer's other operating lines are tagged with custom elements EDGAR companyfacts does not carry, so statements.json's income-statement bridge is incomplete — the engine's history comes from the tagged lines in financials_history.csv, which reconcile to the filed revenue, operating income and OCF used above. prices.json: trading only since the 10 Sep 2025 IPO (279 rows; 52-week range $12.27–$39.73).
