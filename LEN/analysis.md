# LEN — Lennar Corporation
v5 run, 2026-10-16. In scope (market cap $20.215B at $78.43, nasdaq_quote_api).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, or financials_history.csv — none are recomputed.

## What it is
The second-largest U.S. homebuilder by deliveries, plus Financial Services (mortgage/title, ~83% mortgage capture), Multifamily, and land banking through Lennar's land-light structure. It sells volume into affordability pressure with incentives and rate buydowns rather than defending price. Q3 FY2026 (ended 2026-08-31, reported 2026-09-16): total revenue $8.05B (-8.7% YoY), net earnings attributable to Lennar $284M / $1.19 diluted EPS vs $591M / $2.29 a year earlier, new orders -9% to 20,879, deliveries -3% to 20,840 at a $372,000 average price, home-sales gross margin 15.8% vs 17.5% a year earlier, backlog 16,857 homes at ~$6.3B. Management cut the FY2026 delivery target to 80,000-81,000 homes from 82,000-83,000.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $34,186,934,000; net income $2,078,179,000; operating cash flow $216,812,000; capex $188,629,000; SBC $163,494,000 (always a real cost).
- **Conservative owner's earnings FY2025: -$135,311,000 = -$0.52/share** (key_numbers.md: latest FY OE/share $-0.52) — negative because OCF collapsed on the inventory/land cash build (see NI_OCF_DIVERGENCE), not because the P&L lost money.
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $2,078,179,000 for FY2025 — it equals net income here; for a homebuilder that definition is not the headline, because inventory *is* the working capital and the engine captures no ΔNWC for this filer. The OCF-based conservative series is the honest one: inventory and land spend is a real, recurring cash cost of this business.
- OE positive 4 of the last 5 fiscal years. Net debt $2.119B (key_numbers.md), 2.96x normalized OE. SBC is not the story ($163.5M on $34.2B of revenue); the cycle is.

**Base used = TTM owner's earnings through Q3 FY2026, from ttm.py (filing-direct, no hand math; resolves STALE_FY):**
- OCF: FY $216,812,000 − prior YTD $-1,542,675,000 + current YTD $-822,184,000 = **TTM $937,303,000** (both YTD legs are negative — homebuilders build cash inventory ahead of Q4 closings; the TTM window spans a full Q4, so the seasonality washes)
- Capex: FY $188,629,000 − prior YTD $103,424,000 + current YTD $40,829,000 = **TTM $126,034,000**
- SBC: FY $163,494,000 − prior YTD $138,363,000 + current YTD $117,907,000 = **TTM $143,038,000**
- Shares (current-YTD weighted diluted): **240,990,000**
- **TTM OE total $668,231,000 → base OE/share $2.77** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $7.56/share — that median *is* the FY2024 figure, earned at margins that no longer exist (home-sales gross margin was 15.8% in Q3 FY2026 and falling). It is reported, not used; see BASE_DIVERGENCE.

## OVERRIDE — shares (filing-sourced, bounded authority)
- **The gap:** the preliminary engine run exited 4 with `DATA_GAP:shares` — EDGAR companyfacts carries only the basic tag for FY2025, and v5 does not silently swap basic for diluted.
- **The cure:** Lennar reports a single combined basic-and-diluted denominator. judgment.json carries `shares_override = {value: 257746000, kind: "filing", source: "Form 10-K for fiscal year ended November 30, 2025, Earnings Per Share note: 'Denominator for basic and diluted earnings per share — weighted average common shares outstanding 257,746' (in thousands) for FY2025 (FY2024 272,019, FY2023 283,319 in the same table); the same combined basic-and-diluted denominator is reported in the Q4/FY2025 earnings release. Lennar reports a single basic-and-diluted denominator (no dilutive securities outstanding; the filing states there were no antidilutive options for FY2023-2025)."}`. In band (0.95x the last filed diluted count) and never replaces a filed value — it fills only 2025-11-30.
- **Measured impact (key_numbers.md, on the TTM base actually used):** base OE/share $2.77 without → $2.77 with (+0.00%), weighted IRR 6.74% → 6.74% — the TTM denominator comes from the current-YTD diluted tag in the 10-Qs regardless. `unblocks_tier: true`: without the override the annual gate blocks scoring entirely.

## Moat: 4/10 — weak-to-moderate, scale without pricing power
Justification: Second-largest U.S. homebuilder with real scale (national procurement, ~488k controlled homesites, land-light model with 98% of homesites controlled and ~0.1 years owned, even-flow manufacturing cutting cycle time to a record 116 days, integrated Financial Services with ~83% mortgage capture) — against a commodity product with no switching costs or network effects, no through-cycle pricing power (incentives ~12% of price in Q3 FY2026, home-sales gross margin 27.5% in FY2022 -> 15.8% in Q3 FY2026), land bought in a competitive open market at rising cost, and demand hostage to mortgage rates and affordability that the company does not control.
- FOR: #2 U.S. homebuilder by deliveries — national procurement and subcontractor scale; land-light model: ~98% of homesites controlled via options/land banking, ~0.1 years of owned homesites — balance-sheet risk through troughs is structurally lower; even-flow manufacturing: cycle time cut to a record 116 days, construction cost per sq ft down 6% YoY in Q3 FY2026; integrated Financial Services (~83% mortgage capture) captures margin beyond the home sale and funds rate buydowns that defend volume; sustained buyback: share count shrinking 3.8%/yr, credited in the growth blend.
- AGAINST: commodity product — no switching costs, no network effects; buyers choose on price, location and rate buydown; no pricing power through the cycle: incentives ~12% in Q3 FY2026, home-sales gross margin fell from 27.5% (FY2022) to 15.8% (Q3 FY2026) on higher land costs; land is bought in a competitive open market — management attributes the margin gap to land cost; demand is hostage to mortgage rates and affordability, neither company-controlled; Q3 FY2026 orders -9% YoY and FY2026 delivery guidance was cut; capable, well-capitalized rivals (D.R. Horton #1, PulteGroup, NVR's structurally higher-ROE land-light model).
- A 4 gives CAP = 7.2 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 7.2 years, 15-year projection.

## DCF — v5 final run (2026-10-16)
Growth sanity check (mandatory): the engine's blended growth is 0.51% (rev CAGR 5y 8.74%, rev CAGR 3y 0.51%, latest rev YoY -3.54%, OE/share CAGR 2y not computable off the negative latest year), adjusted +3.83pp for the buyback → g_base 4.34%. Default offsets (-12/-5/0/+5/+12pp) and default probabilities 10/25/30/25/10 were kept; OE multipliers default 0.75/0.90/1.00/1.10/1.25. Against actual prints: current prints are negative (FY2025 revenue -3.54%, Q3 FY2026 revenue -8.7% YoY, orders -9%), and the bear/super-bear starts (-0.7% / -7.7%) bracket them. The base start (+4.3%) sits above the current print rate — defensible only because it is a *per-share* rate carried largely by the 3.83pp buyback adjustment against a trough-depressed TTM base. The super-bull start (+16.3%) is above anything recently printed and requires a real housing upcycle (rate relief plus volume and margin recovery) — that is why it carries only 10% probability, and even it yields just a 10.46% IRR at this price. Price $78.43, TTM base $2.77/share.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | -7.7% | 0.75 | Rates stay high, incentives widen, margins compress further | $11.48 | 4.14% |
| Bear | 25% | -0.7% | 0.90 | Affordability stalemate; volume flat at trough margins | $18.11 | 5.31% |
| Base | 30% | 4.3% | 1.00 | Slow per-share recovery on buybacks, no margin snap-back | $24.40 | 6.44% |
| Bull | 25% | 9.3% | 1.10 | Rate relief revives orders; margins rebuild partway | $32.46 | 7.87% |
| Super bull | 10% | 16.3% | 1.25 | Full housing upcycle off the trough base | $47.89 | 10.46% |

- **Probability-weighted: IV@15% $25.90 (-67.0% vs price), IV@12% $34.36, IV@10% $43.80, weighted IRR 6.74%, base-case IRR 6.44%**
- **Tier by numbers: D.** Diagnostics (key_numbers.md): OE yield 3.54%, terminal value 18.6% of IV@15%, scenario spread 4.17x, net debt 2.96x normalized OE, 10.5 months since FY end.

## Flags — every fragility flag resolved
- **DATA_GAP:shares / OVERRIDE_APPLIED:shares**: see OVERRIDE — the filer's own 10-K EPS note reports one combined basic-and-diluted denominator of 257,746,000 for FY2025; declared as a filing-kind override, measured impact +0.00% on the TTM base, `unblocks_tier: true`.
- **STALE_FY** (FY ended 2025-11-30, 10.5 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q3 FY2026 (2026-08-31), inputs quoted above.
- **BASE_DIVERGENCE** (latest FY OE/share $-0.52 vs 3-yr median $7.56): both ends are distorted, in opposite directions. The latest FY is crushed by the inventory/land cash build (OCF $216,812,000 against net income $2,078,179,000). The median is the FY2024 print, earned before the margin collapse (home-sales gross margin 15.8% in Q3 FY2026 and still falling). The TTM base ($2.77) is the most current, filing-derived middle — used, with the verdict sized to it.
- **NI_OCF_DIVERGENCE** (2024, 2025): the homebuilder working-capital cycle, not a tax deposit, impairment, or one-off gain. FY2024: net income $3,932,533,000 vs OCF $2,403,379,000. FY2025: net income $2,078,179,000 vs OCF $216,812,000 — cash went into homes under construction and land/land-banking positions ahead of closings while deliveries and margins fell. (The only named one-offs in the recent prints are small and on the NI side: Q3 FY2026 carried $53M of mark-to-market losses on technology investments and $39M of one-time Financial Services items.) Because the OE base is OCF-based, the divergence makes the base *more* conservative, not less; it reverses in harvest years (FY2023 OCF was $5,179,738,000), which is exactly why no single year is trusted.
- **BUYBACK_TAILWIND** (share count shrinking 3.8%/yr): already credited via the +3.83pp growth adjustment in the blend; not double-counted in the verdict. Q3 FY2026 alone repurchased 3M shares for $256M.
- **WIDE_SCENARIO_SPREAD** (4.17x): real — a cyclical near a trough genuinely has this outcome range. Confidence is low, and the verdict is sized to the conservative end.

## My thoughts / overlay
- The uncomfortable fact is not the tier, it is the gap: even the super-bull scenario (16.3% growth start, 1.25x OE) returns only 10.46% at $78.43. On the current cash earnings, there is no scenario in the set that clears 15% — the market price is paying for a recovery in *net-income* terms (FY2025 EPS was $7.98) that the OCF-based owner's-earnings series does not confirm, because this business must continuously re-buy its inventory with cash.
- The method range is honest to state: on the normalized median base ($7.56/share, the FY2024 print) the picture would be materially better — but that base prices in a margin regime that has since compressed from the mid-20s to 15.8%, with orders still falling. The TTM base is the defensible one today; if margins and OCF recover through FY2027, this name re-rates on a re-run, not on today's numbers.
- Quality is not zero: the land-light pivot (98% controlled, ~0.1 years owned) genuinely lowers trough balance-sheet risk vs the old Lennar, cycle time and unit construction costs are at records, and the buyback at -3.8%/yr is real per-share compounding *if* earnings stabilize. Net debt $2.119B is manageable. None of that closes a 67% gap between price and weighted IV@15%.
- Hurdle price: the weighted case clears 15% only below ~$26 (the weighted IV@15% itself); a margin of safety against the bear case ($18.11 IV@15%) requires materially less than that. At $78.43 a buyer is underwriting the recovery, not being paid to wait for it.

## Final verdict
- **Final tier: D** (weighted IRR 6.74% on the v5 final inputs, TTM base; no tier override)
- Confidence: **Low** (WIDE_SCENARIO_SPREAD, BASE_DIVERGENCE unresolved in the sense that the two candidate bases span negative-to-$7.56, and a cyclical trough)
- One-liner: Second-largest U.S. homebuilder with a real land-light/scale moat, 4/10 — but the cycle has crushed cash earnings: TTM OE is only $2.77/share (FY2025 OE was negative on an inventory-driven OCF collapse) and Q3 FY2026 orders fell 9% with home-sales gross margin at 15.8%, so at $78.43 the weighted IRR is only 6.74% (IV@15% $25.90); it clears the 15% hurdle only below ~$26.
