# TFII — TFI International Inc.
Engine 5.5 run, 2026-10-20; **bridged-TTM re-score the same day** under Andrew's Q4 ruling (2026-10-19), directed by Andrew 2026-10-20 (supersession note in Owner's earnings below). Canadian 40-F (IFRS) filer; SIC 4210 Trucking & Courier Services. Price $111.59 (pinned manually to the original run's nasdaq_quote_api price so the two bases are comparable), market cap $9.308B — in scope (<$40B).

All figures below are copied from key_numbers.md, dcf_numbers.json, dcf_numbers_ttm_bridge.json, financials_history.csv, fundamentals.json, the filed FY2025 consolidated statements of cash flows (40-F) or the cited Q2 2026 interim statements (6-K Exhibit 99.3) — none are recomputed.

## What it is
North American transportation and logistics group built by acquisition, in the three operating segments the FY2025 40-F segment note reports (segments.json): Less-Than-Truckload (anchored by TForce Freight, the former UPS Freight), Truckload (including Daseke, North America's largest flatbed/specialized carrier), and Logistics. Package and Courier is not among the filed segments — it is no longer a separately reported segment. Headquartered in Saint-Laurent, Québec; common shares listed directly on NYSE and TSX under TFII (no ADS). Management has announced an intention to redomicile to the U.S. and has discussed a possible separation of the Daseke/truckload business — neither is in the numbers.

## Owner's earnings
**FY2025 (40-F via EDGAR, from financials_history.csv):** operating cash flow $977,788,000; capex $282,923,000 (rollup: PP&E $273.2M + intangibles $9.7M); SBC $15,148,000 (always a real cost, though small here).
- **Conservative owner's earnings FY2025: $679,717,000 = $8.15/share** (latest FY OE/share $8.15 in key_numbers.md; latest FY OE total $679.7M).
- Maintenance version (from financials_history.csv): $699,015,000 — same ballpark as the conservative figure.
- OE/share for the median window: FY2023 $7.31, FY2024 $7.65, FY2025 $8.15 → median **$7.65/share**. OE positive 5 of the last 5 fiscal years.
- Balance sheet (latest FY, financials_history.csv / dcf_numbers.json): cash $210,186,000; debt current $222,498,000; debt long-term $2,355,477,000; **net debt $2.368B**, i.e. 3.67x normalized OE (key_numbers.md). Lease liabilities of $637,764,000 sit on top of that and are not in the engine's net debt.

### Bridged-TTM base — the scored base (Q4 re-score, 2026-10-20)
The original pass scored the median base because ttm.py reads us-gaap facts only and cannot run on this IFRS filer. Andrew's Q4 ruling (2026-10-19) says: when an interim filing prints the TTM legs, an IFRS name scores on the bridged TTM. TFII's Q2 2026 interim statements do print every leg, so Andrew ordered this directed re-run on 2026-10-20 and the record now scores on the bridged base.

Source: Form 6-K furnished 2026-07-27 (accession 0001193125-26-318068), Exhibit 99.3, Condensed Consolidated Interim Financial Statements for the second quarter ended June 30, 2026 — the condensed consolidated statements of cash flows print six-month legs for both 2026 and 2025, and Note 16 (Earnings per share) prints the diluted share counts. The capex leg is the same two-line rollup as the scored chain (purchases of property and equipment + purchases of intangible assets); the SBC leg is the statements' share-based payment transactions line. Construction, per leg (TTM = FY2025 + H1 2026 − H1 2025):

| Leg | FY2025 (40-F) | H1 2026 (6-K) | H1 2025 (6-K) | TTM |
|---|---|---|---|---|
| Operating cash flow | $977,788,000 | $377,110,000 | $440,238,000 | **$914,660,000** |
| Purchases of property and equipment | $273,220,000 | $100,686,000 | $118,331,000 | **$255,575,000** |
| Purchases of intangible assets | $9,703,000 | $2,125,000 | $7,334,000 | **$4,494,000** |
| Share-based payment transactions | $15,148,000 | $8,526,000 | $7,257,000 | **$16,417,000** |

- **Bridged TTM owner's earnings: $914,660,000 − $260,069,000 (total capex) − $16,417,000 = $638,174,000.**
- Denominator: the latest filed diluted count — **82,413,114**, the H1 2026 weighted average number of diluted common shares (Note 16) — the ttm.py denominator convention (the score values future per-share cash flow on the current count). **Bridged TTM base: $7.7436/share**, declared as a `base_override` (kind filing) and pinned via `--base-oe-ps`; the pinned engine run is recorded in `dcf_numbers_ttm_bridge.json` (base_source: agent_supplied_ttm_override).
- Denominator sensitivity: on the FY2025 diluted count (83,414,310) the same TTM OE is $7.6507/share; on a duration-bridged weighted-average count (81,725,467) it is $7.8088/share. The base moves ±1% across the three; no variant changes the tier.

### Both bases side by side
| Base | OE/share | Weighted IRR | IV@15% | Tier |
|---|---|---|---|---|
| Median of last 3 FY (original pass, 2026-10-20) | $7.6544 | 10.01% | $66.54 | C |
| **Bridged TTM (scored, this re-run)** | **$7.7436** | **10.10%** | **$67.32** | **C** |

The bridge barely moves the verdict, and the reason is visible in the legs: TTM operating cash flow fell $63.1M against FY2025 (H1 2026 OCF of $377.1M ran well below H1 2025's $440.2M even as operating income recovered), but capex fell further — TTM capex of $260.1M vs $282.9M in FY2025, because H1 equipment purchases dropped to $100.7M from $118.3M — and the smaller current share count lifts the per-share figure. The two effects nearly cancel: the bridged base is 1.2% above the median. The tier is C on both bases; what the re-score settles is that the knife-edge 10.01% print was not a stale-FY artifact — the current-year cash legs, fully bridged, land in the same place.

## Moat: 4/10 — weak-to-narrow
Justification: scale and a proven decentralized acquisition platform in a fragmented industry, but freight is a commodity with low switching costs, and returns have compressed straight through the cycle.
- FOR: one of North America's largest trucking groups and the largest flatbed/specialized carrier via Daseke, with LTL terminal-network density from TForce Freight (ex-UPS Freight); the decentralized acquisition platform under Alain Bédard — decades of buying fragmented carriers, keeping local operators, improving operating ratios; diversification across LTL, Truckload and Logistics and across industrial end markets.
- AGAINST: commodity freight with low shipper switching costs and a deep rival set (Old Dominion, XPO, ArcBest, FedEx Freight); returns compression — see ROIC below; cyclical and cost-exposed (unionized U.S. LTL workforce, driver/purchased-transportation cost pressure flagged into Q3 2026); acquisition-led model carries leverage (3.67x) and execution risk (Daseke integration/separation, planned redomiciliation).
- Evidence (fundamentals.json): ROIC proxy (after-tax operating income over equity + debt − cash) by FY: 2019 11.7%, 2020 11.9%, 2021 20.9%, 2022 24.4%, 2023 13.7%, 2024 10.7%, **2025 8.6%** — a clear downtrend from the freight-cycle peak to roughly the cost of capital. Operating margin: 13.6% (2021), 13.0% (2022), 10.1% (2023), 8.6% (2024), 7.2% (2025). Gross margin is not separable in this IFRS presentation (fundamentals.json files no COGS/gross-profit split), so operating margin is the margin evidence. A 4/10 sits on that record: no pricing power that survives a freight recession.
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection. (Unchanged in the re-score — the bridge changes the base, not the moat.)

## DCF — final run (bridged-TTM base, 2026-10-20)
Growth sanity check (mandatory): the engine blend is 2.46% (rev CAGR 5y 15.84% — rejected as a basis-break artifact, see BASIS_BREAK below; rev CAGR 3y -3.64%; latest rev YoY -6.10%; OE/share CAGR 2y 5.60%; share-count adjustment +2.95pp applied to revenue components only). Recent prints: FY2025 revenue fell 6.10%; Q2 2026 total revenue rose 12.4% YoY to $2,289.9M but revenue **before fuel surcharge** rose only ~6% ($1,900.0M vs $1,794.0M, Q2 2026 release), and management guided Q3 2026 EPS ($1.70–1.80) below Q2's $1.85 print. The base start of 2.5% sits **below** the latest ex-fuel print for a written reason: the recovery is one quarter old, FY2025 was still down, and H1 2026 operating cash flow fell YoY. The bull start (7.5%) is in line with the ex-fuel Q2 print; the super-bull start (14.5%) exceeds any recent organic print and is carried only at 10% probability as a full freight-recov
...[truncated 6927 chars]