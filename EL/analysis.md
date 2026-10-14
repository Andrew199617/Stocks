# EL — The Estée Lauder Companies Inc.
v5 run, 2026-10-14 (supersedes the v4 analysis of 2026-10-13; conclusions unchanged, price updated). In scope (market cap $37.316B at $102.2912, nasdaq_quote_api — under the $40B cutoff). Fiscal year ends June 30.

All figures below are copied from dcf_numbers.json, financials_history.csv, or key_numbers.md — none are recomputed.

## What it is
The largest US pure-play prestige beauty company: skin care (Estée Lauder, La Mer, Clinique, The Ordinary), makeup (MAC, Tom Ford Beauty, Too Faced), fragrance (Jo Malone London, Le Labo, Tom Ford), hair care (Aveda, Bumble and bumble). FY2026 (ended 2026-06-30) net sales $15,049M, +5.0% reported / +3% organic — the first growth year after three straight annual declines (FY2023 $15,910M → FY2024 $15,608M → FY2025 $14,326M). The February 2025 "Beauty Reimagined" strategy plus the Profit Recovery and Growth Plan (PRGP) is the turnaround vehicle: ~10,000 net job cuts (high end of guidance), cumulative restructuring program cost ~$1.75B pre-tax, program described as completed on 2026-06-30. FY2026 adjusted operating margin 11.2% (+320bp), adjusted diluted EPS $2.51 (+66%), Q4 FY2026 sales +6.3% with every geography and category except hair care growing organically and mainland China +9% for the full year. FY2027 guidance: organic sales +3–5%, adjusted operating margin 12.7–13.5%, adjusted EPS $3.10–3.35 — but operating cash flow guided DOWN to $1.3–1.4B on higher restructuring payments and working-capital needs, and management says transformational M&A is off the table while it deleverages.

## Owner's earnings
**FY2026 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,773M; capex $457M (tag: PaymentsToAcquirePropertyPlantAndEquipment); SBC $310M (tag: ShareBasedCompensation — always a real cost; material, not abusive).
- **Conservative owner's earnings FY2026: $1,006M = $2.76/share** on 364,800,000 diluted shares (base_oe_per_share $2.7577 in dcf_numbers.json).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $274M from financials_history.csv. It is NOT the cleaner number here — it is built on reported net income of $182M, which is depressed by non-cash and accrued restructuring/litigation charges (see NI_OCF_DIVERGENCE below), so it double-punishes. The OCF-based conservative figure is the trustworthy one: impairments never touched OCF.
- **Base used: $2.76/share = median of the last 3 fiscal years' OE/share** (base_source: median_of_last_3_fy_oe_per_share; the latest year and the median coincide — FY2024 $3.09, FY2025 $1.02, FY2026 $2.76 per the filed history). No TTM override: the latest FY ended only 3.48 months ago (2026-06-30, diagnostics months_since_fy_end) and Q1 FY2027 (September quarter) has not been filed yet — earnings are scheduled 2026-11-02 — so the FY2026 figure IS the trailing-twelve-month figure. No STALE_FY flag fired.
- OE positive 5 of the last 5 years (oe_positive_years_of_last_5: 5/5), but the path is violent: OE/share FY2022 $4.57 → FY2023 $1.28 → FY2024 $3.09 → FY2025 $1.02 → FY2026 $2.76 (from financials_history.csv).
- OE yield at $102.2912 is 2.70% (diagnostics oe_yield 0.02696). The market is paying for the recovery in advance, at a prestige multiple on adjusted EPS — not on cash owner's earnings.

## Moat: 5/10 — moderate, real but narrowing
Justification: A prestige brand portfolio built over decades with genuine premium pricing power and global distribution, but visibly eroding — three years of revenue decline while L'Oréal kept growing, repeated nine-figure impairments on acquired brands, structural channel decay in department stores and Asia travel retail, and faster local/digital-native rivals.
- FOR: Prestige brand portfolio built over decades (La Mer, Estée Lauder, MAC, Le Labo, Jo Malone London) with genuine premium pricing power
- FOR: Global prestige distribution plus a record 34% of sales online in FY2026
- FOR: Mainland China prestige share gains in FY2026 (China sales +9% for the year) and fragrance +10% — a structurally attractive category where EL is strong
- FOR: Scale in R&D and marketing that sub-scale rivals cannot match
- AGAINST: Three straight years of revenue decline (FY2023–25) while L'Oréal kept growing — share and relevance leaked
- AGAINST: Repeated nine-figure impairments on acquired brands (Dr.Jart+, Too Faced, Tom Ford) — management's own admission that bought brand equity decays
- AGAINST: Structural channel decay in US department stores and Asia travel retail (daigou crackdown, weaker Chinese tourist spend; travel retail fell from ~30% of sales at peak to ~15%)
- AGAINST: Rising local Chinese brands and digital-native indies move at TikTok speed; EL's legacy launch process is slower
- AGAINST: Lauder-family dual-class control limits outside discipline on capital allocation; beauty is discretionary and tariff-exposed
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection. Long enough to respect the brands, short enough to admit the lead is contestable.

## DCF — v5 final run (2026-10-14)
**Growth sanity check (mandatory):** the engine's blended base growth is −2.02% (g_base; components: rev CAGR 5y −1.48%, rev CAGR 3y −1.84%, latest rev YoY +5.05%, OE/share CAGR 2y −5.58%, share-count adj −0.36pp). That blend is backward-looking — it averages the collapse years. Actual recent prints: FY2026 revenue +5.05% reported (+3% organic), Q4 FY2026 +6.3%, FY2027 guided organic +3–5% with adjusted EPS +23–33% on margin recovery. Scenario starts were therefore recalibrated via offsets (−0.0598 / −0.0098 / +0.0602 / +0.1002 / +0.1502 vs g_base — written reason per the rules: the −2% base start would sit below what the company just printed and guided, with no deceleration guided):
- Super bear −8.0%: a repeat of the FY2025 revenue print (−8%) — China relapse + travel-retail slide.
- Bear −3.0%: stagnation — guidance missed, North America fails to accelerate.
- **Base +4.0%: in line with FY2026's +5.05% reported / +3% organic and the FY2027 +3–5% organic guide; OE grows with sales plus modest margin leverage, held back near-term by the guided FY2027 cash restructuring drag on OCF.**
- Bull +8.0%: China momentum (+9% FY2026) sustains, PRGP savings drop through, margins rebuild toward pre-2023 levels.
- Super bull +13.0%: full return toward FY2022 earning power — well under the engine's 50% scenario cap.
Probabilities skewed slightly bearish at 15/25/30/20/10 (defaults 10/25/30/25/10): the price already capitalizes the recovery, leverage is real (see balance-sheet caveat below), and FY2027 cash flow is guided down even as adjusted EPS rises. OE multipliers at defaults 0.75/0.90/1.00/1.10/1.25 — the trough-median base makes 1.00 already conservative.

| Scenario | Prob | Growth start | OE mult | Story | IV@15% | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −8.0% | 0.75 | China relapse, travel-retail slide repeats FY2025 | $10.93 | 3.65% |
| Bear | 25% | −3.0% | 0.90 | Guidance missed, North America stagnates | $16.17 | 4.34% |
| Base | 30% | +4.0% | 1.00 | Guided recovery: +3–5% organic, margin leverage | $24.07 | 5.49% |
| Bull | 20% | +8.0% | 1.10 | China sustains, PRGP savings drop through | $31.25 | 6.50% |
| Super bull | 10% | +13.0% | 1.25 | Full return toward FY2022 earning power | $43.61 | 8.19% |

- **Probability-weighted: IV@15% $23.52 (−77.01% upside vs $102.2912 price), IV@12% $31.10, IV@10% $39.55, weighted IRR 5.43%, base-case IRR 5.49%.**
- **Tier by numbers: D.** Diagnostics: OE yield 2.70%, terminal value 18.31% of IV@15% (the low IV is a cash-flow problem, not a terminal-value artifact), scenario spread 3.99×, net debt 0.50× normalized OE on the engine's figure (see caveat below — understated), 3.48 months since FY end.

## Flags — every fragility flag resolved
- **OE_VOLATILE (OE/share range >3× over 5 yrs): RESOLVED, and it caps confidence.** OE/share swung $4.57 → $1.28 → $3.09 → $1.02 → $2.76 while revenue only ranged $14,326M–$17,737M — the volatility is a charge/cash-conversion cycle (impairments, restructuring, China/travel-retail collapse), not demand disappearing. Handled three ways: (1) normalized 3-yr-median base instead of any single year; (2) bear weight widened — super bear raised to 15% probability with a −8% start matching the actual FY2025 print; (3) confidence held at medium despite the tier itself being robust. The guided FY2027 OCF decline to $1.3–1.4B means cash OE stays depressed one more year even in the recovery case — the volatility is not finished.
- **NI_OCF_DIVERGENCE (NI vs OCF differ >40% in 2024, 2025, 2026): RESOLVED year by year — the gap is non-cash impairments and restructuring/litigation charges, and it is why the OCF-based OE base can be trusted while reported EPS cannot.**
  - FY2024: net income $409M vs OCF $2,360M (both from financials_history.csv). One-offs identified in the v4 pass from the 10-K: goodwill/other-intangible impairment (Dr.Jart+), restructuring and other charges — plus $825M of ordinary D&A that net income bears and OCF adds back.
  - FY2025: net income −$1,133M vs OCF $1,272M. The year carried large goodwill/other-intangible impairments (including Dr.Jart+ and Too Faced), restructuring and other charges, and a talcum-litigation settlement — the impairments are non-cash: they destroyed reported earnings without touching operating cash flow.
  - FY2026: net income $182M vs OCF $1,773M. No impairments this year. The gap is D&A $796M and SBC $310M (both from financials_history.csv, added back in OCF) plus restructuring charges through the year (including a securities class-action litigation settlement in the first nine months). Reported operating income of $780M vs an 11.2% adjusted operating margin tells the same story.
  - Conclusion: the divergence is explained, not sinister — but "restructuring" here is a multi-year, ~$1.75B pre-tax program with real cash costs still flowing through FY2027 OCF. It must NOT be added back to OE, and it has not been: the conservative OE base already bears the cash portion.
- **Balance-sheet data caveat (found in this run, not flagged by the engine):** the engine's net_debt_latest of $503M is understated — in financials_history.csv the cash and long-term-debt fields came back blank for EL, so only the current portion of debt was captured. Actual leverage is materially higher than the engine's 0.50× normalized OE (the v4 pass documented total debt of roughly $7B+ against a few billion in cash from the 10-K balance sheet, and management's own FY2027 stance — deleveraging first, transformational M&A off the table, FY2025 dividend cut — confirms it). Folded into the verdict: no tier change (already D on cash flows alone), but there is no "fortress balance sheet" offset to the weak OE, and leverage is a second reason the bear weight was widened. The exact balance-sheet figures are not in the computed outputs for this run, so they are stated in words rather than recalculated here.

## My thoughts / overlay
- The turnaround is real but the stock is not cheap on any owner's-earnings math. Sales are growing again, margins are recovering, China stabilized (+9% FY2026), and the restructuring program is declared complete. None of that closes a gap between $23.52 of weighted IV@15% and a $102.29 price.
- **Method range:** this verdict is unusually robust. Even the super-bull scenario alone (13% growth start, OE ×1.25) yields only $43.61 IV@15% / 8.19% IRR — still Tier D territory. There is no defensible input set on current filings that gets EL to the 15% hurdle at $102.29; the spread across scenarios is a spread within D, not across tiers.
- What the price actually capitalizes: adjusted-EPS recovery ($2.51 → guided $3.10–3.35 → presumably higher by FY2028) at a prestige multiple. That is an earnings-multiple story, not an owner's-earnings story — cash conversion lags because restructuring cash payments and working capital claim OCF first (FY2027 OCF guided down to $1.3–1.4B proves the point).
- Hurdle math: EL clears a 15% hurdle at the weighted IV@15% of **$23.52**; with a margin of safety, at roughly **$19**. The stock would need to fall about three-quarters from $102.29. Alternatively, normalized OE/share would need to roughly quadruple from $2.76 at unchanged growth — a full return to, and beyond, pre-collapse peak earning power that nobody should underwrite as normal.
- Watch items: Q1 FY2027 print (2026-11-02) — North America acceleration is the named test; whether FY2027 cash OCF really troughs and rebounds in FY2028 once restructuring payments end; further acquired-brand impairments would confirm the moat is narrower than 5.

## Final verdict
- **Final tier: D** (tier_by_numbers D — no override; weighted IRR 5.43%)
- Confidence: **Medium** (the tier is robust across every defensible input set, but OE_VOLATILE is live — the actual OE path over the next two years is genuinely uncertain, and FY2027 cash flow is guided down)
- One-liner: Real prestige-brand moat (5/10) in a genuine early turnaround, but at $102.29 the price capitalizes the recovery in advance against trough-normalized owner's earnings of $2.76/share — weighted IV@15% is $23.52 (IRR 5.43%, Tier D); it only clears the 15% hurdle at ~$23.52, or ~$19 with a margin of safety.
