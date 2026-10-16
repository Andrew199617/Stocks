# RGLD — Royal Gold, Inc.
v5 run, 2026-10-15. In scope (engine market cap $16,207,692,263 at $233.00 on the FY2025 weighted share count; ~$19.7B on the current post-acquisition count — under $40B either way).

All figures below are copied from dcf_numbers.json, ttm.py output (ttm.json), or financials_history.csv — none are recomputed.

## What it is
Precious-metals royalty and stream company: it acquires and manages stream interests (the right to buy a share of a mine's metal at a fixed, low price) and royalty interests (a percentage of mine revenue/production) — it does not operate mines. Two segments (stream interests ~69% of Q2 2026 revenue, royalty interests ~31%). As of December 31, 2025 the company names five material properties: Andacollo, Cortez, Kansanshi, Mount Milligan and Pueblo Viejo. Gold was 76% of Q2 2026 revenue (silver 12%, copper 8%). In late 2025 it closed the Sandstorm Gold and Horizon Copper acquisitions plus the Kansanshi gold stream, materially expanding the portfolio to 393+ interests.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $1,030,471,000; net income $466,281,000; operating cash flow $704,846,000; D&A (depletion) $177,082,000; SBC $11,805,000 (always a real cost); capex $0 — by filing-sourced override, see OVERRIDE.
- **Conservative owner's earnings FY2025: $693,041,000 = $9.96/share** (base_oe_latest_per_share $9.963081133310633)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $615,190,000 — lower than the conservative figure because it charges the ΔNWC swing; same ballpark, no contradiction.
- OE positive 5 of the last 5 fiscal years. Net debt $661,717,000 at FY2025 (0.78x normalized OE); Q2 2026 reporting says $500M of revolver debt was repaid in H1 2026, leaving $400M drawn and $1.0B undrawn, plus a new $500M buyback program — the balance sheet is not the risk here.
- **Definition caveat (material):** conservative OE deducts PPE capex, which is genuinely $0 — but a royalty company's economic "capex" is buying new stream/royalty interests to replace depleting ones, and that sits in investing, outside the standardized OE definition. The company's own free-cash-flow definition (OCF minus acquisition of stream and royalty interests, per its FY2025 results release) was deeply negative in FY2025 because it spent $1,164,753,000 on stream/royalty acquisitions plus the Sandstorm/Horizon cash consideration. Most of that is growth, not maintenance — the portfolio grew — but a buyer should know this OE stream is pre-replacement-cost. The depletion charge that proxies replacement ($177,082,000 of DD&A in FY2025) appears only in the maintenance definition.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $704,846,000 − prior YTD $289,171,000 + current YTD $628,715,000 = **TTM $1,044,390,000**
- SBC: FY $11,805,000 − prior YTD $5,911,000 + current YTD $6,886,000 = **TTM $12,780,000**
- Capex: **TTM $0** — all three legs filled by the override (see OVERRIDE)
- Shares (current-YTD weighted diluted): **85,068,765** — the post-Sandstorm/Horizon count (H1 2025 YTD was 65,806,160)
- **TTM OE total $1,031,610,000 → base OE/share $12.13** (base_oe_per_share $12.126777672157342, base_source: ttm_json)
- The engine's normalized base (3-yr median) is $7.87/share (base_oe_normalized_per_share $7.869199055704019) — rejected as the base: FY2023–FY2024 are pre-acquisition scale and FY2025 is only a part-year of the enlarged portfolio, so the median straddles the Sandstorm/Horizon basis break and understates the company that exists now. It is retained below as the method-range floor.
- TTM prints behind the base (Q2 2026 release): revenue $450.5M, +115% YoY; record quarterly OCF of $335.2M; sales volume 100,000 GEOs, +56.5% YoY; adjusted EBITDA margin 83%. Those growth prints are acquisition- and gold-price-driven (average gold price +37% YoY in the quarter), which is exactly why scenario growth starts below were recalibrated down.

## OVERRIDE — capex $0 (filing)
- **The gap:** the preliminary engine run exited 4 with `DATA_GAP:capex` — Royal Gold files no PPE-capex fact under any candidate tag in any year (financials_history.csv carries capex as assumed-zero with a blank capex_tag throughout). Under v5's gate, no tier is emitted on that.
- **The decision (bounded worker authority, kind "filing"):** judgment.json carries `capex_override = {value: 0, kind: "filing", ack_reason: <out-of-band is mechanical — no filed value exists to band against>}` sourced to the FY2025 10-K (filed 2026-02-19), Consolidated Statements of Cash Flows: the investing section lists every investing line for 2025/2024/2023 — Sandstorm & Horizon acquisition $(411,342)k (2025 only), acquisition of stream and royalty interests $(1,164,753)k / $(102,564)k / $(2,678)k, Versamet proceeds $158,886k, Hod Maden cash calls $(9,330)k, Khoemacau proceeds $25,000k, restricted-inventory proceeds $7,681k, Other $299k / $(116)k / $(151)k, netting to $(1,418,559)k / $(77,680)k / $(2,829)k — with no purchases-of-property-and-equipment line anywhere, and no PPE asset line on the balance sheet.
- **Measured impact:** nil on OE — the engine's history already carried capex as assumed-zero, so the override converts a silent zero-fill into a sourced, registered decision (dcf_numbers.json override_impact: median-basis base $7.8692/share with and without; the difference between the block's 7.58% zero-fill weighted IRR and the final 10.16% is the TTM base pin, not the override). Its binary effect: without it there is no tier at all (unblocks_tier).

## Moat: 5/10 — moderate
Justification: the royalty/stream model itself is the moat — contractual interests on producing mines at an 83% adjusted EBITDA margin with no mine cost exposure, now genuinely diversified and at competitive scale — but the company has no pricing power, no operating control, and depleting assets that must be re-bought against deep-pocketed rivals.
- FOR: contractual, long-life stream/royalty interests on producing mines — revenue with no operating or capital-cost exposure at the mine; post-Sandstorm/Horizon diversification (393+ interests, no asset above 13% of Q2 2026 revenue, only two above 10%); scale and deal access in a consolidating sector; capital-allocation record (25 consecutive annual dividend increases, 2026 dividend $1.90; $500M of debt repaid in H1 2026).
- AGAINST: no pricing power and no control — a price-taker on gold (76% of Q2 2026 revenue), operators set mine plans and closures; depletion is real and uncharged in conservative OE — interests waste and replacement means winning auctions against Franco-Nevada, Wheaton, Triple Flag and Osisko; growth is bought, dilutively (diluted shares 65,806,160 H1 2025 YTD → 85,068,765 H1 2026 YTD; FY2025 stream acquisitions of $1,164,753,000 against OCF of $704,846,000); principal-property and jurisdiction concentration across counterparties and countries it does not control.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Growth recalibration (written reason): the engine's blended growth is 23.26% (rev CAGR 5y 12.11%, 3y 19.54%, latest YoY +43.24%, OE/share CAGR 2y 26.98%, share-count adjustment −1.94pp → g_base 21.32%). That blend straddles the Sandstorm/Horizon basis break and a step-change in the gold price — the acquired portfolio is already inside the TTM base, and metal prices do not compound. Scenario starts were therefore set via offsets (−0.26 / −0.19 / −0.12 / −0.07 / −0.01) to −4.7 / +2.3 / **+9.3** / +14.3 / +20.3%. Sanity check against prints: even the super-bull start (20.3%) sits below the latest prints (FY2025 revenue +43.24%, Q2 2026 revenue +115% YoY) deliberately — those prints are the acquisition closing and a +37% YoY gold price, not a repeatable growth rate; the base start of 9.3% rests on portfolio volume ramps (Platreef, Back River, Greenstone per company guidance coverage) and the full-year effect of assets owned for only part of the TTM window. Probabilities 10/25/30/25/10; OE multipliers 0.75/0.90/1.00/1.10/1.25. Price $233.00.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | −4.7% | 0.75 | Gold retraces hard; TTM base marked down to ~FY2025 level and shrinking | $55.22 | 5.23% |
| Bear | 25% | +2.3% | 0.90 | Gold flat-to-down; volumes carry a smaller OE base | $88.81 | 7.26% |
| Base | 30% | +9.3% | 1.00 | Full-year acquired portfolio + volume ramps, gold holds | $131.89 | 9.81% |
| Bull | 25% | +14.3% | 1.10 | Gold grinds higher; ramps deliver; disciplined new deals | $178.08 | 12.31% |
| Super bull | 10% | +20.3% | 1.25 | Gold bull extends and the enlarged portfolio compounds | $258.04 | 16.14% |

- **Probability-weighted: IV@15% $137.62 (−40.94% vs price), IV@12% $185.03, IV@10% $238.17, weighted IRR 10.16%, base-case IRR 9.81%**
- **Tier by numbers: C.** Diagnostics (dcf_numbers.json): OE yield 5.20%, terminal value 19.92% of IV@15%, scenario spread 4.67x, net debt 0.78x normalized OE, 9.46 months since FY end.

## Flags — every fragility flag resolved
- **DATA_GAP:capex** (preliminary run): resolved by the filing-sourced $0 override — see OVERRIDE. The 10-K cash-flow statement fully accounts for investing activities in all three gap years with no PPE line.
- **STALE_FY** (FY ended 9.46 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, inputs quoted above.
- **NI_OCF_DIVERGENCE** (2023): structural, not a one-off — FY2023 net income of $239,440,000 vs OCF of $415,792,000 is explained by the non-cash depletion addback (D&A $164,937,000 in financials_history.csv): royalty/stream interests deplete on the income statement without a cash cost. The OCF-based conservative OE is the series used throughout, so the divergence does not contaminate the base; it is the same depletion economics flagged in the definition caveat above.
- **OVERRIDE_APPLIED:capex**: see OVERRIDE — gap, decision, source and measured (nil) impact are recorded in judgment.json, dcf_numbers.json overrides_applied/override_impact, and the override registry.
- **WIDE_SCENARIO_SPREAD** (4.67x): real — the outcome range is dominated by the gold price, which no one forecasts reliably. Confidence is set to low and the verdict is sized to the conservative end.
- Basis-break note (no flag fired, addressed anyway): the Sandstorm/Horizon/Kansanshi transactions are a scale break inside the history — handled by using the post-deal TTM base and current share count, and by recalibrating growth starts off the post-deal base rather than the blended CAGR that straddles the break.

## My thoughts / overlay
- The method range is the honest headline: **Tier C on the TTM base (weighted IRR 10.16%) to Tier D on the pre-deal 3-yr median base (the engine's counterfactual prints 7.58% on that basis)**. The TTM base is the defensible one — it is the portfolio and share count that exist today — but it is struck at record gold prices and a record OCF half, so it is a generous base, and even on it the stock does not clear 15% at $233.00. Even the super-bull case (20.3% start, 1.25x OE) returns only 16.14%.
- Quality is not the debate: 83% adjusted EBITDA margins, SBC of only $12,780,000 TTM, net debt falling fast, a 25-year dividend-growth record. Price is the debate: at $233.00 the market is paying for the gold bull and the enlarged portfolio to keep compounding; the weighted IV@15% is $137.62.
- The OE-definition caveat cuts against the stock, not for it: conservative OE charges nothing for replacing depleting interests. On the company's own FCF definition (OCF minus stream/royalty acquisitions) FY2025 was deeply negative — mostly growth spending, but a reminder that standing still is not free in this model.
- Hurdle math: the name clears a 15% hurdle at ~$137.62 (the weighted IV@15%); with a margin of safety, ~$110. At $233.00 a buyer needs the super-bull path to merely clear 15%.

## Final verdict
- **Final tier: C** (weighted IRR 10.16% on the TTM base; method range D–C)
- Confidence: **Low** (WIDE_SCENARIO_SPREAD 4.67x, a base struck at peak gold prices, and a portfolio not yet owned for a full year)
- One-liner: High-margin precious-metals royalty/stream portfolio, moat 5/10 — on the post-acquisition TTM base of $12.13/share it still does not clear 15% at $233.00: weighted IRR 10.16% (Tier C), weighted IV@15% $137.62; it clears 15% only at ~$138 (~$110 with a margin of safety), and on the pre-deal median base the same scenarios print ~7.6% (Tier D).
