# PAYX — Paychex, Inc.
Sweep run, 2026-10-13. In scope (market cap ~$37.0B < $40B). Sector: Industrials / HCM & payroll services (Nasdaq universe file).

## What it is
US payroll, HR, benefits, retirement and PEO (professional employer organization) provider for small and mid-sized businesses: Paychex Flex HCM platform, Management Solutions (~$4.9B of FY2026 revenue), PEO & Insurance Solutions (~$1.4B), plus interest earned on funds held for clients ($210.9M in FY2026). In April 2025 it acquired Paycor HCM for ~$4.1B cash ($22.50/share), pushing it upmarket into larger mid-market clients. Recurring, employment-linked revenue; adjusted operating margin guided ~44% for FY2027.

## Owner's earnings (SEC EDGAR, engine v4)
- FY2026 (ended 2026-05-31): OCF $2,556.7M − capex $234.9M − SBC $96.1M = **conservative OE $2,225.7M = $6.1825/share** on 360.0M diluted shares.
- Maintenance version FY2026 (NI + D&A − min(capex, D&A) − ΔNWC): $2,014.7M = ~$5.60/share — below the conservative figure, so $6.18 is not understated; no reason to use a higher base.
- OE positive 5 of the last 5 fiscal years. SBC is modest (3.8% of FY2026 OCF) and treated as a real cost.
- **Base used: latest FY2026 OE/share, $6.1825 (via `--base-oe-ps`), NOT the engine's normalized median of $4.626.** Reason: the 3-yr median spans FY2024–FY2026, and FY2024–FY2025 are pre-Paycor / stub-period years (Paycor closed April 2025, ~6 weeks in FY2025). FY2026 is the first full combined year, so the median mechanically understates current earning power by ~25%. This is the BASE_DIVERGENCE / BASIS_BREAK resolution (see Flags).
- **TTM cross-check (computed, not used as the base):** TTM through Q1 FY2027 (ended 2026-08-31) from EDGAR 10-Q YTD figures — OCF TTM = FY26 $2,556.7M − Q1 FY26 $718.4M + Q1 FY27 $413.5M = $2,251.8M; capex TTM = $234.9M − $55.9M + $56.1M = $235.1M; SBC TTM = $96.1M − $26.8M + $19.3M = $88.6M; TTM OE = $2,251.8M − $235.1M − $88.6M = **$1,928.1M = $5.41/share** on 356.6M Q1 diluted shares. The TTM is *lower* than FY2026 because Q1 OCF fell $304.9M YoY — a client-funds / working-capital timing swing, not lost earning power (Q1 FY2027 net income actually rose 12% YoY to $429.7M and operating income rose 14%). A TTM-base run on $5.41 gives weighted IRR 9.1% (Tier D) — same verdict, so the base choice is not what drives the conclusion; the FY2026 base is the more generous and more representative one, and it is used.
- Balance sheet: net debt $3,467.9M at FY2026 end (long-term debt $4,556.1M, issued to fund Paycor, vs $798.6M pre-deal) = 1.56× the FY2026-base OE. Q1 FY2027 interest expense was $65.1M (~$260M annualized run-rate) vs a near-unlevered balance sheet before the deal. Client payroll funds are held for client obligations and are not available to repay this debt. Dividend is $1.19/quarter ($4.76/yr); FY2026 shareholder returns were ~$2.2B, roughly the whole year's OE — little surplus left for deleveraging if growth disappoints.

## MOAT: 6/10 — moderate / narrow, durable but not wide
- **FOR:** Payroll is a cannot-fail function — tax filing across thousands of US jurisdictions with penalties for error creates real switching friction; once payroll, benefits, retirement and PEO are bundled on one platform, ripping it out risks missed pay runs. Decades of SMB incumbency, high recurring revenue and retention, ~40%+ operating margins held through cycles, broker/CPA referral channels (a third national broker partnership signed in six months; broker referrals +43% YoY in Q1 FY2027), and the Paycor base adds upmarket cross-sell (ASO-to-PEO conversions running ~2× plan).
- **AGAINST:** ADP is larger, global and harder to displace upmarket; the SMB end is attacked on price and UX by Gusto, Rippling, QuickBooks Payroll and Justworks; seat-based (per-employee) pricing is structurally exposed to AI automation and to SMB employment levels — Morningstar downgraded Paychex (and ADP) from wide to narrow moat in its post-AI payroll review, fair value $90. Paycor's promised cross-sell/retention is still being proven (Q1 FY2027 Management Solutions grew only 4%), and there is no owned consumer surface or data network effect rivals cannot replicate.
- **CAP:** moat 6 → CAP = 2 + 1.3×6 = **9.8 years** (growth holds 2 years, then converges to the 2.5% terminal rate over 9.8 years, 15-yr projection).

## Five scenarios — growth recalibrated to guidance, with the reason written
**Sanity check / recalibration (mandatory):** the engine's blended growth is 12.78%, built from a latest revenue YoY of +16.5% and a 3-yr OE/share CAGR of +15.6% — both are Paycor-consolidation artifacts, not organic growth (Paycor contributed ~12pp of FY2026's +17% revenue growth; pre-deal organic growth was +4.6% FY2024, +5.4% FY2025). Actual current prints: Q1 FY2027 revenue +6% YoY, FY2027 guidance revenue +5–6% and adjusted EPS +7–9% (reaffirmed 2026-09-23). Using the engine's default starts (base 12.8%, bull 17.8%, super bull 24.8%) would price in a second acquisition that has not happened. Scenario starts are therefore set via offsets to 0% / 3% / 6% / 9% / 12% — base sits on guidance, super bull at 12% is still 2× guided growth and needs sustained Paycor cross-sell plus PEO mix shift, which is why it only gets 10%.
Price: **$104.64** — 16.9× FY2026 owner's earnings (OE yield 5.9% on the base used).

| Scenario | Prob | Growth start | OE mult | Story | IV@15% | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 0% | 0.75 | SMB recession / AI seat compression; growth stalls, margins give back | $34.02 | 6.5% |
| Bear | 25% | 3% | 0.90 | Growth undershoots guidance; Paycor synergies disappoint | $46.66 | 8.1% |
| Base | 30% | 6% | 1.00 | Guidance delivered (rev +5–6%, adj EPS +7–9%), steady PEO mix shift | $59.25 | 9.7% |
| Bull | 25% | 9% | 1.10 | Paycor cross-sell + PEO conversions compound above guidance | $74.48 | 11.6% |
| Super bull | 10% | 12% | 1.25 | Upmarket share gains + synergy beat ($90M+ annualized already claimed) sustain double digits | $96.69 | 14.1% |

- **Probability-weighted: IV@15% $61.13 (−41.6% vs price), IV@12% $81.56, weighted IRR 10.0%.**
- **Tier by numbers: D** (weighted IRR <10% boundary — 9.98%, effectively on the C/D line; even the super-bull scenario, 14.1%, does not clear the 15% hurdle at this price).
- Diagnostics (final run): OE yield 5.9%, terminal value 19.2% of IV@15% (low — verdict is not a terminal-value artifact), scenario spread 2.84×, net debt 1.56× base OE, 4.4 months since FY end.

## FLAGS — every fragility flag resolved
- **WIDE_SCENARIO_SPREAD (fired on the preliminary run, 4.4×):** the 4.4× spread was an artifact of the acquisition-inflated growth blend (super-bull start 24.8% on a $4.63 pre-deal base). After the base and growth recalibration above, the final-run spread is 2.84× and the flag no longer fires — but the underlying range is still wide ($34–$97 IV@15%), so **confidence is capped at medium**, never high.
- **BASE_DIVERGENCE / BASIS_BREAK_SUSPECT (did not fire as engine flags; resolved manually because the inputs demanded it):** normalized median $4.626 vs latest FY $6.1825 is a +34% gap caused by the Paycor basis break (closed April 2025; FY2024–25 are pre/stub bases, debt $0.80B → $4.56B). Resolution: use the first full combined year (FY2026) as the base, recalibrate growth off organic/guided rates rather than consolidation prints, and cross-check with the TTM ($5.41, Tier D at 9.1%) — all three defensible bases land in C/D, so the break does not change the verdict, only its precision.
- **STALE_FY: did not fire** (FY end 2026-05-31, 4.4 months ago). The Q1 FY2027 10-Q was still pulled and the TTM built (above) as the cross-check.
- **HIGH_NET_DEBT: did not fire, addressed anyway:** net debt $3.47B / 1.56× base OE is new, acquisition debt (pre-deal Paychex was effectively unlevered). It is folded into the verdict via the bear/super-bear OE multipliers and the payout observation: ~all of FY2026 OE was returned to shareholders, so deleveraging depends on continued cash generation, not surplus cash.
- **NI_OCF_DIVERGENCE / OE_VOLATILE / THIN_HISTORY / SECTOR_MODEL_MISMATCH / DILUTION: none fired, none present on inspection.** NI vs OCF gaps are D&A/client-funds explained; OE positive 5/5 years; 10 years of history; not a bank/insurer/REIT; share count essentially flat (−0.2%/yr CAGR — neither dilution nor a buyback tailwind worth crediting).

## Thoughts / overlay
- Quality is not the problem: this is a durable, high-margin, recurring-revenue compounder. The problem is arithmetic — at $104.64 you pay 16.9× owner's earnings for a business guiding to 5–6% growth with new leverage. Even the super-bull path (12% start, OE ×1.25) returns only 14.1%.
- **Method range:** engine defaults (median base, unadjusted blend) give 10.3% / Tier C; the corrected FY2026-base run gives 10.0% / Tier D; the TTM-base run gives 9.1% / Tier D. Every defensible method is below the 15% hurdle — the range is narrow in verdict terms (C/D boundary), wide only in IV terms.
- The September 2026 selloff (stock −8.8% on Q1 report day, from ~$114.53) was about exactly this: a guidance-reaffirming quarter at a premium multiple. The de-rating helps but has not finished the job.
- **Hurdle-clearing price:** the weighted IV@15% is **$61.13** — that is the price that clears 15% on the weighted path with no margin of safety. With a ~20% margin of safety, ~**$49**. Even Morningstar's post-downgrade fair value ($90) sits well above this DCF's weighted IV because it uses a lower discount rate — at Andrew's 15% hurdle, PAYX needs to be roughly 40% cheaper.
- Watch items that could change the answer: sustained double-digit organic growth from Paycor cross-sell (would lift the base start), rapid deleveraging restoring the old balance-sheet quality, or a further de-rating toward the $60s.

## Final verdict
- **Final tier: D** (same as tier by numbers — weighted IRR 10.0%, on the C/D boundary; no override, and the TTM cross-check at 9.1% argues against rounding up to C)
- Confidence: **Medium** (high on the financial history and base arithmetic; the scenario spread and the unproven Paycor growth story cap it)
- One-liner: High-quality narrow-moat (6/10) payroll/HCM compounder, but at $104.64 it prices in growth it is not guiding to — weighted IRR 10.0%, IV@15% $61 vs $105 price; it clears Andrew's 15% hurdle only at ~$61 (~$49 with a margin of safety).
