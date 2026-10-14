# ODFL — Old Dominion Freight Line, Inc.
v5 run, 2026-10-14 (supersedes the v4 analysis of 2026-10-13). In scope: market cap $38.758B at $183.17 (nasdaq_quote_api) — under the $40B cutoff.

All DCF figures below are copied from key_numbers.md / dcf_numbers.json / financials_history.csv — none are recomputed. Quarterly operating figures are from cited search results on the Q2 2026 8-K/10-Q and the September 3, 2026 Q3 update 8-K.

## What it is
The largest U.S. less-than-truckload (LTL) carrier by revenue: a nationwide single-network model running regional, inter-regional and national LTL plus smaller container-drayage/logistics offerings, through ~260 service centers. A pure freight-cycle play on U.S. industrial/retail volumes, run with uncommon discipline: it invests through the cycle, holds spare capacity, and competes on service — 99% on-time, claims ratio 0.1% (Q2 2026 reports, search results) — rather than price.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,370,133,000; capex $415,034,000 (tag: PaymentsToAcquireProductiveAssets); SBC $12,854,000 (tag: ShareBasedCompensation — a real cost, but trivial at this scale; share count is shrinking on buybacks, not diluting).
- **Conservative owner's earnings FY2025: $942,245,000 = $4.45/share** (latest FY OE/share, key_numbers.md)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,004,345,000 (financials_history.csv) — modestly above the conservative figure; the conservative figure is the anchor used for the base.
- OE positive 5 of the last 5 fiscal years (key_numbers.md). Net debt (latest): $-100.1M — i.e. net cash (key_numbers.md: cash $120,091,000, debt_current $20,000,000 in financials_history.csv FY2025).
- **Base used = normalized base, median of last 3 FY OE/share: $4.05/share** (base_source: median_of_last_3_fy_oe_per_share, key_numbers.md). Latest FY is $4.45/share; there is no BASE_DIVERGENCE flag — the median and the latest year are in the same range, and the median is the non-distorted, through-cycle anchor for a cyclical carrier whose FY2025 capex ($415,034,000) ran well below FY2023–24 ($757,309,000 / $771,318,000, financials_history.csv).

**TTM attempt (STALE_FY resolution):** `ttm.py ODFL` exited non-zero with: "ttm.py: cannot compute TTM for ODFL (CIK 878927): sbc: no post-FY YTD fact (no 10-Q since the 2025-12-31 fiscal year end)". Per the sweep instructions, when ttm.py exits non-zero its message is recorded here and the engine's median base is used instead, with the reason stated: no TTM base is pinned in this run, and no TTM figures are hand-computed. What the post-FY quarters show qualitatively (search results, not used as a base): Q2 2026 revenue $1.554B, up 10.4% YoY, with operating ratio 70.1% and diluted EPS $1.68, up 32.3% — a yield-led print (LTL revenue per hundredweight +5.5% excluding fuel) with LTL tons per day still down 4.1%; August 2026 revenue per day was up 12.4% with tons per day down 0.9% and quarter-to-date revenue per hundredweight excluding fuel up 4.8%. The recovery so far is pricing, not volume.

## Moat: 7/10 — strong
Justification: Structural cost advantage (operating ratio 70.1% in Q2 2026 vs industry mid-80s) from network density, owned service centers and a non-union low-turnover workforce; service quality (99% on-time, 0.1% claims) converts to pricing power (rev/cwt +5.5% ex-fuel in Q2 2026 with volumes down, 4.9% general rate increase effective Oct 2026); spare capacity and a net-cash balance sheet let it take share through cycles — against low switching costs/annual bids, no network effects, capable rivals (XPO, Saia, FedEx Freight, Estes) investing to close the service gap, and freight cyclicality (revenue -5.5% in FY2025, tons/day still -4.1% in Q2 2026 and -0.9% in Aug 2026).
- FOR:
  - Structural cost advantage — operating ratio 70.1% in Q2 2026 vs industry mid-80s
  - Service quality converts to pricing power — 99% on-time, 0.1% claims, rev/cwt +5.5% ex-fuel in Q2 2026
  - Network density and owned service centers with spare capacity to take share through cycles
  - Non-union, low-turnover workforce and through-cycle investment discipline
  - Net-cash balance sheet funds investment without dilution
- AGAINST:
  - Low switching costs — LTL sold on annual bids, shippers multi-source, no network effects
  - Capable rivals XPO, Saia, FedEx Freight and Estes investing to close the service gap
  - Freight cyclicality — revenue -5.5% in FY2025, tons/day still negative in 2026
  - Structural cost inflation (driver wages, equipment, real estate) passed through only with a lag
- A 7 gives CAP = 11.1 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 11.1 years, 15-year projection (key_numbers.md).

## DCF — v5 final run (2026-10-14)
Engine blended growth: growth blend 1.12% → g_base 3.31% (key_numbers.md). Components: rev CAGR 5y 6.48%, rev CAGR 3y -4.24%, latest rev YoY -5.48%, OE/share CAGR 2y 10.65%; share count CAGR -2.19% (growth adj 2.19%). Probabilities, offsets and multipliers are kept at the defaults (10/25/30/25/10; -12/-5/0/+5/+12pp; 0.75/0.90/1.00/1.10/1.25) — the evidence is balanced: pricing is strong and volumes are still negative, so there is no basis to skew the weights. Price: $183.17. OE yield 2.21% (key_numbers.md).

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -8.7% | 0.75 | Freight recession deepens, yield discipline breaks, capex normalizes against falling OCF | $14.79 | 3.28% |
| Bear | 25% | -1.7% | 0.90 | Volumes stay negative through 2027, rate increases only offset cost inflation, capex normalizes | $24.55 | 4.05% |
| Base | 30% | 3.3% | 1.00 | Yield grows mid-single digits, volumes flat-to-slightly-up, buybacks shrink the count ~2%/yr | $34.50 | 4.89% |
| Bull | 25% | 8.3% | 1.10 | Freight recovery: tons turn positive, operating leverage improves the operating ratio, share gains continue | $48.09 | 6.04% |
| Super bull | 10% | 15.3% | 1.25 | Full cycle snap-back with sustained sub-70% operating ratio and light capex — a stacked tail, not a forecast | $76.22 | 8.30% |

- **Probability-weighted: IV@15% $37.61 (-79.5% vs price), IV@12% $50.11, IV@10% $64.09, weighted IRR 5.20%, base-case IRR 4.89%**
- **Tier by numbers: D.** Diagnostics (key_numbers.md): OE yield 2.21%, terminal value 19.1% of IV@15%, scenario spread 5.15x, net debt / normalized OE -0.12x, 9.4 months since FY end.

**Sanity check vs actual prints:** Latest FY revenue YoY is -5.48% and TTM revenue growth is low-single-digit on yield alone (Q2 2026 revenue +10.4% YoY was +5.5% rev/cwt ex-fuel against -4.1% tons/day; August revenue/day +12.4% against -0.9% tons/day — search results). The base start of 3.3% sits on the TTM/H1 yield-led prints and deliberately below the Q2 revenue/EPS spike, with the written reason that the Q2 spike is yield, fuel and operating leverage off a trough — including $17.2M of net gains on property and equipment disposals noted in the Q2 reports — not a volume run-rate. Bull 8.3% requires only a normal freight recovery. Super bull 15.3% exceeds every recent volume print and is priced as a 10% tail. Super bear/bear negative starts are below current prints by construction (recession cases; FY2023 and FY2025 delivered revenue declines of that kind).

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 9 months ago; 9.4 months since FY end, key_numbers.md): ttm.py was run as required and exited non-zero — its exact message is quoted in the Owner's earnings section above (no post-FY YTD SBC fact in the facts ttm.py reads, so it hard-blocks rather than zero-filling). No TTM base was pinned and no TTM figures were hand-computed; the final run uses the engine's normalized median base of $4.05/share, with the reason stated here. The post-FY quarterly evidence (Q2/August, above) was checked qualitatively: it shows a yield-led recovery with volumes still negative, which supports keeping the base growth at 3.3% rather than raising it — and the verdict does not turn on the base, because even the super-bull IV@15% ($76.22) sits far below the $183.17 price.
- **BUYBACK_TAILWIND** (share count shrinking 2.2%/yr — key_numbers.md: share count CAGR -2.19%): already credited once via the +2.19% growth adjustment in the blend; not double-counted in the scenario stories or the verdict. Search results confirm the pace continued in H1 2026 (share repurchases and dividends were funded from operating cash flow, with cash of $283.9M held at June 30, 2026).
- **WIDE_SCENARIO_SPREAD** (super-bull IV is 5.2x super-bear IV; key_numbers.md spread 5.15x): real but mechanical at a 2.21% OE yield — a small base cash flow against a large price fans any growth range out in IV terms. Confidence is capped at medium. Decisively, the spread does not straddle the hurdle: even the super-bull IV@15% ($76.22, IRR 8.30%) is far below the price, so there is no tier ambiguity to size around.
- **Balance sheet (no HIGH_NET_DEBT / BIG_NET_CASH flag fired — resolved explicitly):** Net debt (latest) is $-100.1M (key_numbers.md) — net cash, at -0.12x normalized OE. The OE stream is an equity cash flow, so net cash is not added to IV; it is downside protection and the reason ODFL can invest through the cycle. It does not rescue the valuation: the gap between the $183.17 price and the $37.61 weighted IV@15% dwarfs the per-share cash position implied by the filed balance sheet.

## My thoughts / overlay
- This is one of the best-run industrial carriers in the U.S. at a price that pays for a decade of flawless compounding: $183.17 against a normalized base of $4.05/share is a 2.21% OE yield, for a business whose revenue shrank in FY2025 (latest rev YoY -5.48%) and whose volumes are still negative in 2026.
- **Method range:** the preliminary v5 run (median base $4.05/share, default moat 5) gave weighted IV@15% $36.79 and weighted IRR 5.09%; the final run (same median base, moat 7) gives $37.61 and 5.20%. Both are deep in Tier D. No TTM variant is quoted in this run because ttm.py hard-blocked (see STALE_FY) and hand-computed TTM figures are prohibited — stated in words instead of calculated.
- Red flags, honestly sized: none are about integrity or the balance sheet. The risks are (1) valuation — the entire question; (2) freight-cycle duration — the recovery so far is yield and fuel, not tons; if tons keep falling, operating leverage runs in reverse and management guided the Q3 operating ratio to worsen sequentially from Q2 as the Q2 disposal gains normalize (search results); (3) capex normalization — Q2 reports put expected 2026 capex at about $380M, so forward OE should not be assumed to repeat a light-capex window; (4) buybacks at a 2.21% OE yield are expensively bought capital returns, even if affordable.
- SBC/dilution: clean — SBC $12,854,000 in FY2025 (financials_history.csv), share count shrinking ~2.2%/yr.
- **Hurdle math:** the price that clears 15% on the weighted case is the weighted IV@15% itself, **$37.61**; with a 20% margin of safety, **~$30**. The market price is roughly five times the hurdle-clearing price.

## Final verdict
- **Final tier: D** (weighted IRR 5.20% on the v5 final inputs; tier_final = tier_by_numbers, no override)
- Confidence: **Medium** (high on the OE base and the direction — no scenario, including the super-bull tail at 8.30%, clears even 10%; capped at medium by WIDE_SCENARIO_SPREAD and by the unresolved TTM pin, which is recorded, not worked around)
- One-liner: Strong-moat (7/10) best-in-class LTL carrier with real pricing power and a net-cash balance sheet, but at $183.17 on a normalized base of $4.05/share (2.2% OE yield) it yields a 5.2% weighted IRR — clears the 15% hurdle only at ~$38 (~$30 with a margin of safety); even the super-bull case ($76.22) is far below today's price.
