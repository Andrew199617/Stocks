# FISV — Fiserv, Inc.
v5 run, 2026-10-15. Price $46.19 (nasdaq_quote_api), market cap $25.358B — in scope under $40B. All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, or financials_history.csv — none are recomputed.

## What it is
Payments and financial-technology infrastructure: Merchant Solutions (including the Clover point-of-sale platform) and Financial Solutions (core banking processing, digital payments, issuing) for merchants and for more than 10,000 financial institutions. Largely recurring, processing-based revenue. The stock has collapsed after repeated guidance resets: it fell roughly 67–68% in 2025 after an October 2025 earnings reset and CEO change, and in Q2 2026 management cut FY2026 guidance again — organic revenue growth to −1% to flat (from +1% to +3%) and adjusted EPS to $7.20–$7.40 (from $8.00–$8.30) — after Q2 2026 GAAP revenue fell 4% year over year, Merchant Solutions organic revenue fell 1% and Financial Solutions fell 8% (Reuters / Morningstar reporting of the Q2 2026 release). Management's May 2026 Investor Day medium-term frame is a 4%–6% adjusted revenue CAGR through 2029 with adjusted EPS above $12 by 2029. Activist Jana Partners is pressing for a portfolio review and board refresh, and shareholder litigation over prior Clover growth claims is a live overhang.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $21,193M (latest YoY +3.60%), net income $3,480M, operating cash flow $6,062M, capex $1,763M, SBC $357M (always a real cost).
- **Conservative owner's earnings FY2025: $3,942M = $7.18/share** (latest FY OE/share, key_numbers.md).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $3,469M in FY2025 — below the conservative figure, so the OCF-based base is not flattered relative to the NI-based version. In FY2024 the maintenance figure was $2,747M vs conservative $4,695M, a wider gap (see NI_OCF_DIVERGENCE under Flags).
- OE positive 5 of the last 5 fiscal years. Net debt $441M (key_numbers.md); net debt is 0.12× normalized OE (diagnostics) — the balance sheet is not the problem here.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $6,062,000,000 − prior YTD $2,313,000,000 + current YTD $2,082,000,000 = **TTM $5,831,000,000**
- Capex: FY $1,763,000,000 − prior YTD $814,000,000 + current YTD $956,000,000 = **TTM $1,905,000,000**
- SBC: FY $357,000,000 − prior YTD $215,000,000 + current YTD $235,000,000 = **TTM $377,000,000**
- Shares (current-YTD weighted diluted): **534,500,000**
- **TTM OE total $3,549,000,000 → base OE/share $6.64** (base_source: ttm_json)
- The TTM base ($6.64) sits below both the latest-FY figure ($7.18) and the engine's normalized 3-yr median ($7.18) because TTM OCF fell while TTM capex rose — that deterioration is real and current, so the TTM base is the right, more conservative base. No BASE_DIVERGENCE flag fired (latest and median agree at $7.18).

## Moat: 6/10 — moderate-strong core, eroding growth engine
Justification: core bank processing is high-switching-cost infrastructure with scale and recurring revenue, but Clover faces structural competition, pricing power is visibly eroding (fee concessions, margin compression), and two years of guidance resets show the moat did not protect growth or margins.
- FOR: Core banking / payment processing embedded in 10,000+ financial institutions — mission-critical, high switching costs, long contracts; recurring revenue was 84% of adjusted revenue in Q2 2026 (per Q2 reporting); scale as one of the largest merchant acquirers / processors, with Clover holding a leading small-merchant POS position (~20% share per analyst reporting); Clover gross payment volume still growing (Q2 2026 GPV +9% reported, Clover revenue +13% excluding Argentina and prior-year one-offs per management); trivial net debt (0.12× normalized OE) funds buybacks through the reset — share count shrinking 5.4%/yr.
- AGAINST: Clover competition from Toast (restaurants and expanding verticals) and Block is structural, not cyclical; pricing power eroding — strategic fee eliminations and concessions already dragged revenue and Merchant Solutions margins; large clients can renegotiate, in-source, or leave at renewal, and government contracts can be terminated for convenience (10-K risk factors); Financial Solutions shrinking (organic −8% in Q2 2026: digital payments −6%, issuing −10%, banking −10%); management credibility damaged — repeated "miss and reset" quarters, CEO turnover, shareholder litigation alleging prior Clover growth was flattered by forced Payeezy-to-Clover migrations, and activist pressure for a break-up review; stepped-up technology / resiliency spending is pressuring margins (adjusted operating margin 31.8% in Q2 2026 vs 39.6% a year earlier, per the release reporting).
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Growth recalibration (written reason): the engine's blended g_base is 11.74% — a blend of historical revenue CAGRs (5-yr 7.37%, 3-yr 6.11%), latest FY revenue YoY (+3.60%) and OE/share CAGR 2y (13.51%), plus the maximum +5pp buyback adjustment. That start is far above what the company is actually printing now: Q2 2026 revenue −4% YoY, organic revenue −5% in the quarter, and FY2026 organic guidance of −1% to flat. Scenario starts were therefore recalibrated downward (offsets −0.1374 / −0.1074 / −0.0724 / −0.0374 / +0.0026 vs g_base) to −2% / +1% / **+4.5%** / +8% / +12%. The base start (4.5%) anchors on management's own medium-term 4%–6% adjusted revenue CAGR through 2029 (OE/share can grow faster than revenue on buybacks, which is why bull/super-bull sit above the revenue frame; super-bull 12% additionally assumes margin recovery toward the Investor Day path and Clover re-acceleration — it is deliberately given only 7%). Probabilities were skewed bearish vs the defaults (15/30/30/18/7 vs 10/25/30/25/10) because two consecutive guidance resets, a second CEO transition and broad-based segment declines make bear-or-worse the single largest block. OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $46.19, TTM base $6.64/share.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −2.0% | 0.75 | Decline persists; client losses / pricing cuts compound; turnaround fails | $33.43 | 11.38% |
| Bear | 30% | 1.0% | 0.90 | Flat-to-low growth sticks; margins stay compressed near the reset level | $45.84 | 14.90% |
| Base | 30% | 4.5% | 1.00 | Medium-term 4–6% revenue frame delivered from the reset base; buybacks support OE/share | $59.52 | 18.50% |
| Bull | 18% | 8.0% | 1.10 | Clover re-accelerates, implementations land, margins recover toward plan | $76.50 | 22.51% |
| Super bull | 7% | 12.0% | 1.25 | Full Investor Day path: double-digit EPS growth, margin expansion, multiple-worthy execution | $103.83 | 28.15% |

- **Probability-weighted: IV@15% $57.66 (+24.8% vs price), IV@12% $76.43, IV@10% $97.35, weighted IRR 18.01%, base-case IRR 18.50%**
- **Tier by numbers: B.** Diagnostics (key_numbers.md): OE yield 14.38%, terminal value 18.53% of IV@15%, scenario spread 3.11×, net debt 0.12× normalized OE, 9.5 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above, and it is lower than the FY base, so staleness was flattering the FY numbers, not hiding strength.
- **BUYBACK_TAILWIND** (share count shrinking 5.4%/yr): already credited via the +5pp share-count adjustment inside g_base (and the scenario starts were then recalibrated down for current prints, see above); not double-counted in the verdict. Note the TTM share count (534.5M) continues the shrink vs FY2025's 549M.
- **NI_OCF_DIVERGENCE** (net income vs OCF differ by >40% in 2024 and 2025): the gap is persistent across both years, not a single named one-off — FY2025 NI $3,480M vs OCF $6,062M; FY2024 NI $3,131M vs OCF $6,631M (financials_history.csv). It reflects the business's large non-cash add-backs (D&A and SBC of $357M in FY2025) and working-capital movement between the NI and OCF lines. Resolution: the base used throughout is the OCF-based conservative OE (OCF − capex − SBC), never NI, so the divergence does not inflate the base; and the NI-based maintenance version is actually lower in both years ($3,469M FY2025; $2,747M FY2024), which caps how much credit the OCF figure deserves — one reason probabilities were skewed bearish rather than taking the 14.38% OE yield at face value.
- The preliminary run also fired **WIDE_SCENARIO_SPREAD** (4.45× on default inputs); on the final recalibrated inputs the spread is 3.11× and the flag no longer fires. Confidence is still held at medium, not high — the outcome range (super-bear IV@15% $33.43 to super-bull $103.83) remains wide in absolute terms.

## My thoughts / overlay
- The honest tension: the filing-based cash machine is intact (TTM OE $3,549M, OE yield 14.38% at this price, net debt 0.12× normalized OE, buybacks shrinking the count), while the growth/margin story management sold for years has been reset twice and is currently negative. The price ($46.19, down from a ~$239 peak per press reporting) already capitalizes a lot of failure — even the bear case ($45.84 IV@15%) sits essentially at the price, and only the super-bear case is materially below it.
- Method range: on the preliminary default inputs (median base $7.18, engine growth) the weighted IRR printed 25.60% (Tier S) — that run is not defensible, because its 11.74% growth start contradicts the company's own current prints and guidance. On the final defensible inputs (TTM base, recalibrated growth, bear-skewed probabilities) the result is Tier B at 18.01%. Quoting FISV without the method attached would hide exactly this.
- Hurdle-clearing price: the weighted IV@15% of $57.66 is the highest price that still clears the 15% hurdle on the weighted path; the weighted IV sits 24.8% above the current $46.19 price (upside_at_15), which is the margin of safety on the weighted case — but there is no margin of safety against the super-bear case ($33.43).
- Risks that could move this down a tier: another guidance reset (the pattern is now two years long), a large client/partner loss at renewal, Clover share loss to Toast/Block becoming visible in GPV, litigation/activist outcomes forcing a value-destructive break-up, and Argentina / hardware-cycle noise in Merchant Solutions. What could move it up: delivery of the Q4-weighted recovery management guided to, and the medium-term frame holding for two consecutive quarters.

## Final verdict
- **Final tier: B** (weighted IRR 18.01% on the v5 final inputs; the indefensible default-input run printed S, the documented method range is the finding)
- Confidence: **Medium** (high on the TTM cash base and balance sheet, low-medium on management's forward path after repeated resets; scenario spread 3.11×)
- One-liner: see judgment.json.
