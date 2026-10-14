# TKO — TKO Group Holdings, Inc. (NYSE: TKO)
v5 run, 2026-10-14 (supersedes the 2026-10-13 blocked analysis — the DATA_GAP that blocked that run is now resolved by a filing-sourced capex override under Andrew's 2026-10-14 bounded worker authority; see OVERRIDE). In scope: market cap $33.535B at $172.85 (nasdaq_quote_api), under the $40B scope cap.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output (ttm.json), financials_history.csv, or the filings/search results cited — none are recomputed.

## What it is
Premium sports/entertainment holding company formed in September 2023 by combining UFC and WWE. On February 28, 2025 it closed the acquisition of IMG (sports marketing/media rights), On Location (premium event hospitality) and PBR from Endeavor in an all-equity transaction. Asset-light model: venues are rented, PPE net is only $639,930,000 against FY2025 revenue of $4,735,151,000. Revenue is media rights/content, live events/hospitality, sponsorship and consumer products across UFC, WWE and IMG segments.

Latest prints (search-cited, Q2 2026 release): Q2 2026 revenue $1.547 billion, +18% YoY (UFC $535.7M, WWE $620.9M, IMG $354.7M), net income $303.9M, Adjusted EBITDA $649.9M (+23%). Full-year 2026 guidance was raised to revenue $5,775–5,825M and Adjusted EBITDA $2,275–2,305M. An analyst-estimate summary put FY2026 revenue at $5.82B, +22.91% vs FY2025 — a step-up that includes one-off FIFA World Cup 2026 hospitality at On Location, the first year of the new media-rights deals, and a full year of IMG/On Location/PBR consolidation, so it is not a clean organic growth rate.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $4,735,151,000; net income $195,403,000; operating cash flow $1,285,725,000; SBC $117,588,000 (always a real cost); capex $126,953,000 — by filing override, see OVERRIDE (the engine files no capex tag for TKO in any year).
- **Conservative owner's earnings FY2025: $1,041,184,000 = $5.37/share** (dcf_numbers.json: latest FY OE/share $5.3666)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $386,472,000 — far below the conservative figure and not the usable definition here: FY2025 net income is depressed by merger purchase-accounting amortization inside the $484,990,000 D&A line, so an NI-anchored definition double-counts the merger's non-cash cost. The OCF-based conservative figure is the cleaner series and is used throughout.
- OE positive 5 of the last 5 fiscal years (on the override-filled history). Net debt $2,931,024,000 (dcf_numbers.json), 1.90x the base OE total (diagnostics: net_debt_to_normalized_oe 1.9041).
- History caveat (basis break, below): the FY2023–FY2025 per-share series straddles the UFC/WWE combination and the February 2025 Endeavor-asset deal — share count stepped 82,808,019 (2023) → 171,874,540 (2024) → 194,011,072 (2025) — so no historical CAGR in this folder is an organic growth rate.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math; full output saved to ttm.json):**
- OCF: FY $1,285,725,000 − prior YTD (H1 2025) $559,045,000 + current YTD (H1 2026) $1,068,456,000 = **TTM $1,795,136,000**
- Capex: **TTM $126,953,000**, all three legs filled by the override, prorated by days (FY leg $126,953,000 over 365 days; both YTD legs $62,954,775.34 over 181 days; they cancel in the TTM math) — see OVERRIDE for the true filed-leg comparison
- SBC: FY $117,588,000 − prior YTD $63,267,000 + current YTD $79,982,000 = **TTM $134,303,000**
- Shares (current-YTD weighted diluted): **193,323,374**
- **TTM OE total $1,533,880,000 → base OE/share $7.9343** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $2.0693/share — rejected as the base: its median year is FY2024, a stub/combination year (OCF only $586,084,000 on a part-year combined basis) that describes a company that no longer exists in that form. It is still reported in key_numbers.md and used in the method range below.
- TTM caveat, stated plainly: H1 2026 OCF nearly doubled YoY ($1,068,456,000 vs $559,045,000) in a half that included World Cup hospitality and the first months of the new rights deals. The TTM base may therefore be flattered; that risk is carried in the bear-side OE multipliers (0.75/0.90) and in the low confidence, not by silently haircutting the filing-derived base.

## OVERRIDE — capex (filing-sourced, bounded authority, unblocks the tier)
- **The gap:** TKO's capex is disclosed only under its own extension tag `tko:PaymentsToAcquirePropertyPlantAndEquipmentAndOther`. EDGAR companyfacts for CIK 1973266 carries no standard capex tag in any year, so the preliminary engine run exited 4 with `DATA_GAP:capex` (dcf_numbers.json data_gap: ["capex"]) — no tier, correctly. This is the exact case the README records as "filing-instance XBRL or a filing-sourced override."
- **The decision (worker, under Andrew's 2026-10-14 bounded authority, kind "filing"):** judgment.json carries `capex_override = {value: 126953000, kind: "filing"}` — the FY2025 figure from the Consolidated Statements of Cash Flows in the FY2025 Form 10-K (filed 2026-02-25, accession 0001193125-26-071651), line "Purchases of property, buildings and equipment and other assets": $(126,953) thousand FY2025, $(118,818) thousand FY2024, $(93,753) thousand FY2023 in the same statement. **Verified directly in the filing document in this run** (cash-flow statement, p. F-9), and corroborated in the Q2 2026 Form 10-Q (accession 0001193125-26-330592), same line: $(44,444) thousand H1 2026 vs $(48,631) thousand H1 2025. The same 10-K check confirmed the engine's OCF ($1,285,725 / $586,084 / $266,159 thousand) and SBC ($117,588 / $103,466 / $64,512 thousand) for FY2025/24/23.
- **How it was applied:** the engine filled every period where the tag is absent (financials_history.csv capex_tag = "OVERRIDE" for 2021–2025 — for the last 3 FY that is the gap being covered); ttm.py filled all three capex legs prorated by days (quoted above). An override never replaces a filed value; there were no filed values to replace.
- **Out-of-band, acknowledged:** override_checks records out_of_band: true with last_filed_value: null — mechanical only, because the band is computed against a filed value that does not exist. judgment.json carries an ack_reason saying exactly that; the value is a filing figure, not an estimate without an anchor.
- **Measured impact (key_numbers.md, on the TTM base actually used, overrides toggled off in the same final configuration):** base OE/share $8.59 (no override — the zero-fill TTM) → $7.93 (with override), −7.64%; weighted IRR 9.98% → 9.45% (−0.53pp). Unblocks tier: YES — this override is the only reason this company has a tier; without it the filing gap blocks scoring entirely. The dollar size of the capex itself is small and conservative in direction: the single FY2025 value applied to FY2024 overstates that year's true filed capex ($118,818,000) and to FY2023 overstates its true filed figure ($93,753,000), i.e. it lowers historical OE; the TTM capex under the override ($126,953,000) vs the true filed legs ($122,766,000 on the 10-K/10-Q figures) differs by ~0.3% of TTM OE, as documented in the override's reason field.

## Moat: 7/10 — strong
Justification: UFC and WWE are irreplaceable category-defining sports IP with multi-year contracted media-rights step-ups already signed for 2026 onward (Paramount, ESPN, Netflix), an asset-light cost base, and brand-over-athlete fan loyalty — a strong moat. It is not a 9–10: rights pricing power is only re-proven at renewal, litigation (fighter pay, shareholder suits) is a recurring tax, the IMG/On Location segment is lower-margin and event-cyclical, and leverage plus the noncontrolling-interest structure sit ahead of Class A economics.
- FOR:
  - UFC and WWE are the category-defining properties in MMA and sports entertainment — no substitute supplier at scale
  - Long-term contracted media rights with step-ups: UFC on Paramount (7 years from 2026), WWE premium live events on ESPN (5 years from 2026), Raw on Netflix
  - Asset-light model: venues are rented, capex is ~2.7% of revenue, and ticketing/hospitality/sponsorship carry premium pricing
  - Fans follow the promotion brand over individual fighters/talent, and promoter-favorable talent economics hold through cycles
- AGAINST:
  - Media-rights pricing power is only proven at renewal; current deals are long but back-end weighted
  - Litigation overhang: fighter-pay/antitrust history and WWE shareholder litigation (settlement costs hit Q2 2026 SG&A)
  - IMG/On Location is lower-margin and event-cyclical (World Cup/Olympics years), diluting the core moat
  - Net debt $2,931,024,000 and a large noncontrolling-interest share of OpCo economics
  - Ticketing/hospitality demand is consumer-discretionary and cyclical
- A 7 gives CAP = 11.1 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 11.1 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Growth recalibration (written reason): the engine's blended growth is 53.54% and g_base hit the 35% cap, but every blend component is a merger artifact — rev CAGR 5y 46.36% and 3y 60.72% measure the UFC/WWE combination, OE/share CAGR 2y is 143.77% off the stub-period base, share CAGR is +53.02%/yr from merger issuance, and the only clean-basis revenue print, latest FY YoY, is −3.05% despite ~10 months of IMG/On Location/PBR consolidation. The sanity check against actual prints: Q2 2026 revenue +18% YoY, FY2026 guided/estimated revenue growth ~+22.9% (both flattered by one-off World Cup hospitality, first-year rights step-ups and consolidation anniversaries). Scenario starts were therefore set via offsets (−0.35 / −0.32 / −0.27 / −0.22 / −0.17 vs the capped g_base) to 0 / 3 / **8** / 13 / 18% — the super-bull start (18%) sits at the Q2 print and below the guided FY2026 step-up, with the written reason above (one-offs and consolidation in the guide) rather than above it. Probabilities default 10/25/30/25/10; OE multipliers default 0.75/0.90/1.00/1.10/1.25. Price $172.85.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 0.0% | 0.75 | TTM base was World-Cup-flattered; litigation/rights friction; OE resets a quarter lower and never grows | $43.38 | 5.52% |
| Bear | 25% | 3.0% | 0.90 | Post-World-Cup normalization; IMG drags; rights escalators only | $59.95 | 6.86% |
| Base | 30% | 8.0% | 1.00 | Contracted rights step-ups plus sponsorship/ticketing growth decay normally over the CAP | $84.40 | 8.88% |
| Bull | 25% | 13.0% | 1.10 | Paramount/ESPN/Netflix distribution broadens the funnel; hospitality stays strong post-World Cup | $117.74 | 11.41% |
| Super bull | 10% | 18.0% | 1.25 | Q2-print growth persists; next rights cycle re-rates again; buybacks compound per-share OE | $169.69 | 14.81% |

- **Probability-weighted: IV@15% $91.05 (−47.32% vs price), IV@12% $123.15, IV@10% $159.29, weighted IRR 9.45%, base-case IRR 8.88%**
- **Tier by numbers: D.** Even the super-bull case does not clear the 15% hurdle at this price (14.81%). Diagnostics (dcf_numbers.json): OE yield 4.59%, terminal value 20.69% of IV@15%, scenario spread 3.91x, net debt 1.90x base OE, 9.43 months since FY end.

## Flags — every fragility flag resolved
- **DATA_GAP:capex / OVERRIDE_APPLIED:capex**: resolved by the filing-sourced override — see OVERRIDE. The gap is covered for all of the last 3 FY (data_gap_uncovered: []); the figures were verified in the filing document itself in this run.
- **STALE_FY** (FY ended 9.43 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, with all inputs quoted above.
- **BASE_DIVERGENCE** (latest FY OE/share $5.37 vs 3-yr median $2.07): the median is the distorted one — its median year, FY2024, is a combination stub year; the latest FY is a full combined year and the TTM extends it. TTM base used; median retained in the reporting and the method range.
- **DILUTION** (share count +53.02%/yr): merger issuance, not compensation dilution — the count stepped on the WWE combination accounting and the February 2025 Endeavor-asset deal. SBC is modest (TTM $134,303,000 against TTM OCF $1,795,136,000). The engine's −5pp dilution adjustment is part of why the raw blend was discarded rather than adjusted; scenario growth is set on the post-merger combined basis, and the share count has since stabilized (TTM denominator 193,323,374 vs FY2025 194,011,072), with H1 2026 financing showing $967.6M of share repurchases in the Q2 2026 10-Q.
- **BASIS_BREAK_SUSPECT**: confirmed and structural — revenue +183%-class jumps in the combination years are M&A, not organic growth, and FY2025 revenue fell −3.05% despite consolidating the Endeavor assets for ~10 months. No historical CAGR was used as a growth input; see the recalibration above.
- **OE_VOLATILE** (OE/share spans >3x over 5 years): real, and it is the basis break plus the OCF ramp, not ordinary cyclicality. Handled by the TTM base, a 35% combined weight on bear-or-worse scenarios, and low confidence.
- **NI_OCF_DIVERGENCE** (2023, 2024, 2025): merger purchase-accounting amortization inside D&A of $224,051,000 / $457,925,000 / $484,990,000 (financials_history.csv) plus SBC explains the bulk of the NI-vs-OCF gap in each named year — net income is not understated cash earnings hiding a problem, it is amortization-depressed. The OCF-based conservative OE is the series used throughout, so the divergence does not contaminate the base; the maintenance-definition OE ($386,472,000 in FY2025) is shown for completeness and rejected for the same reason.

## My thoughts / overlay
- The method range is the honest headline. On this run's code, three defensible input sets give: (a) 3-yr median base ($2.0693) with the calibrated scenarios — weighted IRR 4.44%, IV@15% $23.75, Tier D; (b) the final run — TTM base ($7.9343) with calibrated scenarios — weighted IRR 9.45%, IV@15% $91.05, Tier D; (c) TTM base with the engine's default growth (starts 23/30/35/40/47% off the capped blend) — weighted IRR 21.91%, IV@15% $327.72, Tier A. Run (c) is rejected, not averaged in: its super-bear growth start (23%) sits above the company's own guided FY2026 revenue step-up (~+22.9%, itself one-off-flattered), which is exactly the failure the sanity-check rule exists to catch. Defensible range: D on every input set that respects the prints; A only by trusting merger-artifact CAGRs.
- Quality is not the debate: contracted rights step-ups are signed, capex is ~2.7% of revenue even after a conservative filing override, SBC is single-digits as a share of OCF, and capital returns are real ($967.6M of H1 2026 buybacks per the 10-Q). The debate is price: at $172.85 the market is already paying for the Paramount/ESPN/Netflix step-ups and a clean post-World-Cup landing.
- Balance sheet folded in: net debt $2,931,024,000 is 1.90x the base OE total — serviceable on contracted rights revenue, but it means the bear cases have no cash-pile cushion, and a large share of OpCo economics belongs to noncontrolling unitholders ahead of Class A holders.
- Hurdle-clearing price: on the weighted path, the price that clears 15% is the weighted IV@15% itself — **$91.05**. A margin of safety against the bear cases (bear IV@15% $59.95, super-bear $43.38) requires a price well below that; at $172.85 there is no margin of safety on any scenario except super-bull, and even super-bull (14.81% IRR) does not clear 15%.

## Final verdict
- **Final tier: D** (weighted IRR 9.45% on the v5 final inputs; tier by numbers D, no tier override)
- Confidence: **Low** (the tier is D on every print-respecting input set, but the base itself rests on a World-Cup-flattered TTM and an unblocks-tier override, and the method range spans D to A)
- One-liner: Elite sports-IP owner, moat 7/10 — but at $172.85 the price already pays for the new rights deals: weighted IRR 9.45% (Tier D), weighted IV@15% $91.05 vs $172.85; it clears 15% only at or below $91.05, and even the super-bull case (14.81% IRR) does not clear at today's price.
