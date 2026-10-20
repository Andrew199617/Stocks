# HSIC — Henry Schein, Inc.
v5 run, 2026-10-20. All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json or financials_history.csv — none are recomputed.

## What it is
The world's largest provider of health-care solutions to office-based dental and medical practitioners (SIC 5047, wholesale distribution): global dental and medical merchandise distribution, specialty products (implants, orthodontics), and the Henry Schein One / Dentrix practice-management technology platform. Q2 2026 (quarter ended 2026-06-27) sales were $3.46B, +6.7% YoY (internal +4.6%, acquisitions +0.7%, FX +1.4%); management raised FY2026 guidance to sales growth of 4.5–5.5% and non-GAAP diluted EPS of $5.29–5.39. KKR took a 12% anchor stake in May 2025 with two board seats (since granted the right to go to 19.9%) and is co-driving a value-creation program targeting >$200M of operating-income improvement over the next few years; a new CEO (Fred Lowery) is executing it.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $712M; capex $139M (PaymentsToAcquireProductiveAssets, PP&E only, no intangible leg filed); SBC $39M.
- **Conservative owner's earnings FY2025: $534.0M = $4.39/share** (key_numbers.md: latest FY OE/share $4.39; latest FY OE total $534.0M)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $548M for FY2025 (financials_history.csv) — same ballpark as the conservative figure.
- OE positive 5 of the last 5 fiscal years. Net debt $2.951B (key_numbers.md), plus $329M of lease liabilities (dcf_numbers.json).
- History shape: FY2023 OE/share was $2.38 — the October 2023 cyber incident disrupted the North American and European distribution businesses and depressed that year's OCF ($500M). FY2024 OE/share of $5.17 is flattered the other way by a working-capital release (see NI_OCF_DIVERGENCE). The 3-yr median and the TTM both land between those two distorted years.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $712M − prior YTD $157M + current YTD $145M = **TTM $700M**
- Capex: FY $139M − prior YTD $63M + current YTD $55M = **TTM $131M**
- SBC: FY $39M − prior YTD $16M + current YTD $16M = **TTM $39M**
- Shares (current-YTD weighted diluted): **115,238,506**
- **TTM OE total $530M → base OE/share $4.60** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $4.39/share — reported in key_numbers.md; the preliminary run on that median base printed a weighted IRR of 10.15% and IV@15 of $49.95 (dcf run of 2026-10-20 before the TTM pin), so the base choice barely moves the verdict: Tier C either way.

## Moat: 5/10 — moderate/narrow
Justification: scale and software switching friction are real, but measured returns have faded to the cost of capital.
- FOR: #1 scale in dental distribution — world's largest provider to office-based dental/medical practitioners, dense logistics network; Henry Schein One / Dentrix practice-management software installed base creates switching friction beyond merchandise; mix shift to specialty products (implants), own brand and technology lifting gross margin from 27.8% (FY2020) to 31.1% (FY2025) and 31.8% in Q2 2026; KKR anchor stake and board seats driving a >$200M operating-income value-creation program.
- AGAINST: merchandise distribution is contestable (Patterson and Benco regionally, Amazon and direct manufacturer sales) with a thin ~5% operating margin; ROIC has faded (below); leverage is real (net debt 5.27x normalized OE) and buybacks/acquisitions were debt-funded while OCF weakened; small-practice customers have no contractual lock-in on supplies, and the Oct 2023 cyber incident showed operational fragility.
- ROIC evidence (fundamentals.json roic_proxy): 12.0% (FY2020), 15.5% (FY2021), 12.7% (FY2022), 8.2% (FY2023), 8.0% (FY2024), 8.0% (FY2025) — well above the cost of capital early in the window, at it since the cyber incident. Gross margin rose over the same span (27.8% → 31.1%) on specialty/technology mix, but SG&A absorbed it: operating margin ~5.0% in FY2025. A moat of 7+ would need ROIC sustainably above the cost of capital; the last three years do not show it.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-20)
Growth sanity check: the engine blend is 8.79% (key_numbers.md components: rev CAGR 5y 5.43%, rev CAGR 3y 1.40%, latest rev YoY 4.03%, OE/share CAGR 2y 35.82%, share-count adjustment +4.06pp). The 35.82% OE/share CAGR is an artifact — it is measured off the cyber-depressed FY2023 base ($2.38/share) — but it is only one of four blend components and the median lands on the share-adjusted revenue blend. That 8.8% base start checks against the actual prints: FY2026 guidance is sales +4.5–5.5% with non-GAAP EPS of $5.29–5.39, Q2 2026 sales grew 6.7% and non-GAAP EPS 15.5% YoY, and the share count is shrinking ~4–5%/yr, so guided revenue growth plus buyback shrink plus early value-creation margin gains supports a high-single-digit OE/share start. Bull offsets were trimmed from the default +5/+12pp to +4/+9pp: a super-bull start of 20.8% would exceed every EPS print the company has made, while 17.8% sits just above Q2 2026's +15.5% non-GAAP EPS print with the 1.25 OE multiplier carrying the rest of the upside case. Probabilities are the defaults 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25. Price $84.58.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -3.2% | 0.75 | Value-creation program fails, distribution share leaks to direct/Amazon, leverage bites | $22.28 | 5.60% |
| Bear | 25% | 3.8% | 0.90 | Revenue grows at the low end, margins stay ~5%, buyback slows under debt load | $35.81 | 7.84% |
| Base | 30% | 8.8% | 1.00 | Guided growth + buyback shrink + partial savings delivery | $48.94 | 9.94% |
| Bull | 25% | 12.8% | 1.10 | $200M+ operating-income program lands, specialty/tech mix keeps lifting gross margin | $63.45 | 12.11% |
| Super bull | 10% | 17.8% | 1.25 | Full program plus re-accelerating internal growth; ROIC back to low-teens | $88.37 | 15.49% |

- **Probability-weighted: IV@15% $50.56 (-40.2% vs price), IV@12% $67.82, IV@10% $87.14, weighted IRR 10.22%, base-case IRR 9.94%**
- **Tier by numbers: C.** Diagnostics (key_numbers.md): OE yield 5.44%, terminal value 19.7% of IV@15%, scenario spread 3.97x, net debt 5.27x normalized OE, 9.8 months since FY end.
- Hurdle-clearing prices (weighted path): 15% at $50.56 · 20% at $35.15 · 25% at $26.74.

## Flags — every fragility flag resolved
- **STALE_FY** (latest FY ended 2025-12-27, 9.8 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026 (legs quoted above), not the FY figure.
- **BUYBACK_TAILWIND** (share count shrinking 4.1%/yr): credited once, via the +4.06pp growth adjustment in the blend; not double-counted in the verdict. The pace is continuing — TTM buybacks were $728M (fundamentals.json) and the cover-page count was down to 111,446,542 by 2026-07-27 vs 121,717,876 FY weighted diluted — but it is partly debt-funded (see HIGH_NET_DEBT), which is why the bear cases assume it slows.
- **NI_OCF_DIVERGENCE** (2024, 2025): explained, not a one-off hiding in the base. FY2025: net income $398M + D&A $311M = $709M vs OCF $712M (financials_history.csv) — D&A bridges essentially the whole gap. FY2024: net income $390M + D&A $297M = $687M vs OCF $848M, with the remainder a working-capital release (delta_nwc −$576M in the CSV) partly offset by other non-cash items. The base is OCF-based throughout, and the WC-flattered FY2024 year ($5.17/share) is not the base on either the median or the TTM.
- **CASH_INCLUDES_RESTRICTED**: the latest cash figure ($156M, financials_history.csv) is filed only as the combined cash + restricted-cash total. The restricted portion sits inside that $156M, so net debt of $2.951B is understated by at most $156M — the 5.27x net-debt ratio would rise to roughly 5.6x at the extreme. HIGH_NET_DEBT stands either way; no conclusion changes.
- **HIGH_NET_DEBT** (net debt 5.27x normalized OE): real. Total debt $3.107B against TTM OE of $530M, built up through acquisitions and buybacks while FY2023 OCF was cyber-depressed; the revolver was expanded from $1.0B to $1.25B in September 2026 (company filing via press coverage). Cash flows are staple-like and OE has been positive 5/5 years, but the bear and super-bear cases carry the stress (0.90 / 0.75 OE multipliers, IRRs 7.84% / 5.60%).
- **TIER_BAND** (bear tier D at 7.84% vs bull tier C at 12.11%): the verdict spans tiers, so it is sized to the bear end — the final C is the weighted figure, and any position case should be argued off the bear IV@15 of $35.81, not the weighted $50.56.

## My thoughts / overlay
- The method range is narrow for once: median base ($4.39) → weighted IRR 10.15%, IV@15 $49.95; TTM base ($4.60) → 10.22%, $50.56. Tier C on both. The argument about HSIC is not the base year, it is the price: at $84.58 the market is already paying for the KKR value-creation program to deliver. The super-bull case — full delivery, ROIC back to low-teens — only just reaches the current price at a 15% discount rate (IV@15 $88.37).
- The equity story (activist + KKR anchor, >$200M of targeted operating-income improvement, $125M annualized savings run-rate targeted by end-2026, accelerating buybacks) is credible but it is an execution story on a ~5% operating-margin distributor with 5.3x leverage, not a moat story: ROIC has been ~8% for three straight years.
- What would change the tier: a print showing the savings converting to operating margin (not just gross margin), or a price below ~$51, where the weighted path clears 15%.

## Final verdict
- **Final tier: C** (weighted IRR 10.22% on the TTM base; bear D 7.84% → bull C 12.11%)
- Confidence: **Medium** (clean filing data, no overrides, narrow method range — held back from high by the leverage and the tier band)
- One-liner: Durable #1 dental/medical distributor, moat 5/10 — does not clear 15% at $84.58 (weighted IRR 10.2%, IV@15 $50.56); it clears the 15% hurdle only below ~$51, and the bear case (7.8%) sizes the verdict.
