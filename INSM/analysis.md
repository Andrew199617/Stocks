# INSM — Insmed Incorporated
v5 run, 2026-10-15. Price $98.50 (nasdaq_quote_api), market cap $19.602B — in scope under $40B.

All filing figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output (ttm.json), or financials_history.csv — none are recomputed. Q2 2026 print figures are from web-search reporting of the company's Q2 2026 results and are cited as search results, not filing-computed figures.

## What it is
A pulmonary/rare-disease biotech with two commercial products: ARIKAYCE (amikacin liposome inhalation suspension), the inhaled therapy for refractory Mycobacterium avium complex (MAC) lung disease, and BRINSUPRI (brensocatib), a once-daily oral DPP1 inhibitor approved by the FDA in August 2025 as the first and only treatment for non-cystic fibrosis bronchiectasis (NCFB) — since approved in Europe and Japan as well (search-cited). The pipeline is led by TPIP (treprostinil palmitil inhalation powder) in Phase 3 for pulmonary arterial hypertension and other lung indications. The 2026 investment case is the BRINSUPRI launch ramp; the owner's-earnings case does not exist yet.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $-935,014,000; capex $32,561,000; SBC $152,710,000 (always a real cost).
- **Conservative owner's earnings FY2025: $-1,120,285,000 = $-5.63/share** (key_numbers.md: latest FY OE/share $-5.63, latest FY OE total $-1.120B)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $-1,322,561,000 for FY2025 (financials_history.csv) — worse than the conservative figure, so there is no definition-shopping escape here.
- OE positive in **0 of the last 5 fiscal years** (key_numbers.md). The normalized base (3-yr median) is **$-4.89/share**. This is not a one-bad-year story: the filed history shows negative conservative OE every year back to 2016, on a rising revenue line (FY2025 revenue $606,423,000).
- Net debt (latest, key_numbers.md): $30.5M — small on the FY2025 filed basis (cash $510,445,000 in financials_history.csv). Search-cited Q2 2026 reporting puts cash, cash equivalents and marketable securities at roughly $1.2 billion at June 30, 2026 — the balance sheet funds the burn for now; it does not create owner's earnings.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $-935,014,000 − prior YTD $-467,657,000 + current YTD $-311,566,000 = **TTM $-778,923,000**
- Capex: FY $32,561,000 − prior YTD $13,554,000 + current YTD $9,739,000 = **TTM $28,746,000**
- SBC: FY $152,710,000 − prior YTD $82,238,000 + current YTD $87,008,000 = **TTM $157,480,000**
- Shares (current-YTD weighted diluted): **216,415,000**
- **TTM OE total $-965,149,000 → base OE/share $-4.46** (key_numbers.md: base OE/share $-4.46, base_source: ttm_json)
- Why the TTM base: STALE_FY requires checking it, and it is the least-bad base — the launch quarters are already in it (TTM OCF burn $-778,923,000 vs FY2025 $-935,014,000). It changes nothing: TTM, latest-FY ($-5.63), and median ($-4.89) bases are all deeply negative. Unlike an inflection name where TTM rescues the median, here every defensible base is Tier F.

## Moat: 6/10 — moderate, launch-proven but never yet profitable
Justification: BRINSUPRI is the first and only FDA-approved treatment for non-cystic fibrosis bronchiectasis (patent-protected DPP1 inhibitor, ASPEN Phase 3 data, now also approved in Europe and Japan per search reports) and ARIKAYCE is the only approved inhaled therapy for refractory MAC lung disease, giving Insmed a specialized pulmonary commercial platform and rare-disease pricing power; offset by zero positive owner's-earnings years in its history, growth concentrated in one launch, a binary Phase 3 TPIP pipeline, payer pressure, and 17.4%/yr share dilution funding the burn.
- FOR:
  - BRINSUPRI first-and-only approved treatment for non-CF bronchiectasis — patent-protected DPP1 inhibitor, ASPEN data
  - ARIKAYCE only approved inhaled therapy for refractory MAC lung disease (liposomal delivery)
  - Specialized pulmonary/rare-disease commercial platform reused across products and geographies (US/EU/Japan)
  - Rare-disease pricing power — FY2026 BRINSUPRI guidance raised to $1.25–$1.40B within a year of launch (search-cited)
- AGAINST:
  - No positive owner's earnings in any of the last 5 fiscal years — moat has never converted to cash profit
  - Growth concentration: the story now rides on one launch (BRINSUPRI) plus a niche base product (ARIKAYCE)
  - TPIP and other pipeline value is binary Phase 3 risk, not an earnings stream
  - Payer / gross-to-net pressure on high-cost specialty drugs, and eventual patent expiry
  - Dilution funding the burn: share count growing 17.4%/yr, SBC $157,480,000 TTM
- A 6 would give CAP = 9.8 years (growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection) — moot here, because there is no positive base for the fade to act on.

## DCF — v5 final run (2026-10-15)
Price: **$98.50** (key_numbers.md). The engine cannot project scenarios on a negative base, and forcing one would be inventing numbers — so there are no scenario IVs or IRRs, by design (no positive normalized OE = Tier F, flagged not forced). The five scenario slots were assigned the default likelihoods 10/25/30/25/10 for the record, each with its story:

| Scenario | Prob | Growth start | OE mult | Story | IV@15% | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | n/a — no OE base | n/a | BRINSUPRI ramp stalls on payer/diagnosis limits; TPIP fails; burn and dilution continue | n/a (OE < 0) | n/a |
| Bear | 25% | n/a | n/a | Launch decelerates, ARIKAYCE expansion (PDUFA Jan 28, 2027, search-cited) disappoints; OE stays negative for years | n/a (OE < 0) | n/a |
| Base | 30% | n/a | n/a | Launch delivers the guided $1.25–$1.40B BRINSUPRI year (search-cited) but launch/R&D spend keeps OE negative near term — still no OE-DCF support today | n/a (OE < 0) | n/a |
| Bull | 25% | n/a | n/a | BRINSUPRI scales toward blockbuster peak sales and operating leverage turns OE positive late this decade — value sits beyond the OE screen's current window | n/a (OE < 0) | n/a |
| Super bull | 10% | n/a | n/a | BRINSUPRI + TPIP + ARIKAYCE deliver on the combined peak-revenue claim of over $14 billion (search-cited company claim) — a peak-sales valuation story, not an owner's-earnings story | n/a (OE < 0) | n/a |

- **Probability-weighted IV@15% / IRR: not computable — no positive owner's earnings in any base period** (dcf_numbers.json: implied_irr_weighted null, tier_by_numbers "F").
- **Tier by numbers: F.** Sanity check per the standing rule: scenario growth starts cannot be compared against OE prints because there are no positive OE prints. The revenue prints are real and extraordinary — latest rev YoY 66.73% (key_numbers.md), and search-cited Q2 2026 total revenue of $425.5M, up 296% year over year, with BRINSUPRI at $309.2M in the quarter (+49% vs Q1 2026). That growth is exactly why the equity has value as an option; it does not make an OE DCF computable, because the same launch spend that produces the revenue keeps OCF negative (TTM OCF $-778,923,000).
- Diagnostics: OE yield on price is negative on every base; 100% of any equity value here is future/terminal option value, so terminal-value share and scenario spread are not computable. One quality caution from the search-cited Q2 print: the near-breakeven Q2 2026 net loss ($13.2M) was helped by a $99.8M favorable change in contingent consideration liabilities — a non-cash mark, not operating progress; the OCF-based OE series is unaffected by it and remains negative.

## FLAGS — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 9 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026 (ytd_end 2026-06-30), with all inputs quoted in full under Owner's earnings. Verdict unchanged: TTM OE/share is $-4.46.
- **DILUTION** (share count growing 17.4%/yr; key_numbers.md share count CAGR 17.38%): fires, hard, and it is both SBC and financing dilution. SBC rose from $96,835,000 (FY2024) to $152,710,000 (FY2025) in financials_history.csv and is $157,480,000 TTM (ttm.json) — a real cost the conservative definition deducts in full. Weighted diluted shares rose from 199,014,000 in FY2025 (key_numbers.md) to 216,415,000 on the H1 2026 YTD weighted count (ttm.json). At a TTM OCF burn of $-778,923,000, expect the count to keep rising until OE breakeven; the −5.00% growth adjustment (key_numbers.md) is irrelevant on a negative base — there is no growth to adjust.
- **BASIS_BREAK_SUSPECT** (a >60% revenue jump in the last 5 years): investigated — no divestiture, big M&A, or restatement explains it. The break is the BRINSUPRI launch: FY2025 revenue grew 66.73% (latest rev YoY, key_numbers.md) in the year of its August 2025 approval, and search-cited Q2 2026 revenue grew 296% year over year. The revenue CAGRs (5y 29.83%, 3y 35.20%, key_numbers.md) are launch-phase figures, not a repeatable base rate — another reason no growth start was extrapolated from them. The OE series itself has no break to fix: it is negative on both sides of the jump.
- Checked and not firing, for the record: **HIGH_NET_DEBT / BIG_NET_CASH** — net debt (latest) is $30.5M (key_numbers.md), immaterial against a $19.602B market cap either way; the search-cited ~$1.2B cash-and-securities position at June 30, 2026 cushions the burn but is not owner's earnings. **SECTOR_MODEL_MISMATCH** — not Finance/Real Estate/Utilities, but the same caution applies in biotech form: an OE/capex DCF cannot value a launch-phase, peak-sales story. The F tier is a correct statement about owner's earnings and a deliberately incomplete statement about the equity.

## My thoughts / overlay
- This is the screen working as intended, with a sharper edge than a pre-revenue name: INSM has real, fast-growing revenue and a genuinely strong launch — and still no owner's earnings at any point in its filed history (0/5 positive years; negative every year since 2016 in financials_history.csv). With negative OE on the latest-FY, median, and TTM bases alike, there is **no price at which the OE DCF clears a 15% hurdle**, and no margin-of-safety price to quote. Method range: none — all three bases give Tier F.
- What a buyer at $98.50 is actually underwriting: BRINSUPRI reaching multi-billion peak sales in a ~500,000-patient US NCFB pool (search-cited), the ARIKAYCE label expansion (FDA Priority Review, PDUFA target January 28, 2027, search-cited), TPIP Phase 3 success, and the company's combined peak-revenue claim of over $14 billion (search-cited) — against continued dilution (17.4%/yr) and a CFO transition announced October 2026 with guidance reaffirmed (search-cited).
- What would change the tier: the first positive-OE fiscal year in the filings. Until revenue covers the launch-plus-R&D spend in actual OCF terms — not adjusted or guided terms — INSM stays F in this sweep regardless of launch headlines.

## Final verdict
- **Final tier: F** (= tier by numbers; no tier override — there is no positive owner's earnings to underwrite any hurdle)
- Confidence: **Low** (negative OE on every base is high-confidence; the equity's option value is entirely outside this method)
- One-liner: Real launch, no owner's earnings, moat 6/10 — BRINSUPRI is the first-and-only bronchiectasis drug and revenue is exploding (Q2 2026 total revenue $425.5M, search-cited), but OE is negative on every base (TTM -$4.46/share, 0/5 positive years), so it cannot clear the 15% hurdle at any price on an OE DCF; the $98.50 price is a peak-sales option, not an earnings stream.
