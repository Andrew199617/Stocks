# NXT — Nextpower Inc. (formerly Nextracker Inc.)
Pass-1 run, 2026-10-17, engine 5.4.0. Price $80.04 (nasdaq_quote_api), market cap est. $12.22B — in scope under $40B.

All figures below are copied from dcf_numbers.json, ttm.json, financials_history.csv, or fundamentals.json — none are recomputed.

## What it is
The global leader in utility-scale solar trackers (NX Horizon, Hail Pro, TrueCapture software), rebranded Nextpower as it expands into an integrated clean-power platform: eBOS, NX Earth Truss foundations, power conversion (Zigor acquisition closed July 30, 2026) and battery storage (Prevalon acquisition, >$300M incremental backlog). ~26% global tracker share in 2025 prints, operations in 40+ countries, but revenue is U.S.-concentrated (83% of Q1 FY27 revenue). Backlog exceeded $5.5B at Q1 FY27 (ended 2026-07-03), up from $5.25B at FY26 end. No dividend.

## Owner's earnings
**FY2026 (10-K, period ended 2026-03-31, from financials_history.csv):** operating cash flow $562,911,000; capex $49,277,000; SBC $120,298,000 (always a real cost).
- **Conservative owner's earnings FY2026: $393,336,000 = $2.5757/share** (latest FY OE/share in dcf_numbers.json)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $356,536,000 — same ballpark, which raises confidence in the conservative figure.
- OE positive 4 of the last 5 fiscal years (FY2022 was −$156,078,000 total in the supply-chain trough). OE/share history: FY2023 $0.4970, FY2024 $2.4852, FY2025 $3.3696, FY2026 $2.5757 — volatile (see FLAGS).
- Engine normalized base (median of last 3 FY OE/share): $2.5757/share. FY2026 OE fell vs FY2025 despite revenue +20.28% because OCF fell ($562.9M vs $655.8M) on working capital (ΔNWC leg) while SBC rose to $120.3M.
- SBC trajectory is a real headwind: $31,994,000 (FY23) → $56,783,000 (FY24) → $118,880,000 (FY25) → $120,298,000 (FY26) → $127,626,000 TTM. Share count is rising, not shrinking: diluted shares CAGR +1.54%/yr (growth blend already charges −1.54pp for it).

**Base used = TTM owner's earnings through Q1 FY27, from ttm.py (filing-direct):**
- OCF: FY $562,911,000 − prior YTD $81,324,000 + current YTD $121,059,000 = **TTM $602,646,000**
- Capex: FY $49,277,000 − prior YTD $11,258,000 + current YTD $15,899,000 = **TTM $53,918,000**
- SBC: FY $120,298,000 − prior YTD $22,310,000 + current YTD $29,638,000 = **TTM $127,626,000**
- Shares (current-YTD weighted diluted): **155,141,856**
- **TTM OE total $421,102,000 → base OE/share $2.7143** (base_source: ttm_json)
- The TTM base ($2.7143) sits close to the normalized median ($2.5757), so the base is not the fight here — growth and the price are. TTM revenue (fundamentals.json) $3,630,307,000, TTM gross margin 33.4%, TTM operating margin 19.3%.

**Balance sheet (resolves DEBT_TAGS_BLANK):** cash $1,094,976,000 at FY26 end (financials_history.csv). The company reports no debt outstanding — stated in its Q3 FY26 and Q4 FY26 releases (over $1.1B cash, no debt, investment-grade Fitch rating, $500M buyback authorized over three years). The filed history agrees: total debt was $147,717,000 in FY2024 and $0 in FY2025; FY2026 files no debt tag because there is no debt balance to tag. Net cash, not leverage, is the position — the engine's net_debt is null only because the tag is blank.

## Moat: 6/10 — moderate-strong, not wide
Justification: clear #1 share, bankability and software, with ROIC well above the cost of capital in the clean post-IPO years — but trackers are bid project-by-project, margins are partly policy-made (45X credits), and there is no recurring-revenue lock-in.
- FOR: Global tracker leader (~26% share, 28.5 GW shipped in 2025 prints) — scale, bankability and field record EPCs/developers pay for; TrueCapture / Hail Pro software and integrated bundles (tracker + eBOS + Earth Truss + TrueCapture, e.g. the 552 MW Cold Creek project) raise switching friction beyond commodity steel; proven pricing power — gross margin (fundamentals.json) rose from 15.1% (FY23) to 32.5% (FY24), 34.1% (FY25), 32.6% (FY26), 33.4% TTM; ROIC proxy (fundamentals.json) 72.0% (FY24), 59.2% (FY25), 46.2% (FY26) — far above any plausible cost of capital, on an asset-light model (FY26 capex $49.3M on $3.56B revenue).
- AGAINST: ROIC history before FY24 is not usable evidence — the pre-IPO Flex capital structure left FY23 equity at −$3,075,767,000 and the ROIC proxy meaningless (−4.0% FY23, distorted earlier years), so the high-ROIC record is only three years long; gross margin is flattered by IRA 45X credits and tariff recoveries (~$99M in Q1 FY27 alone, ~$82M in Q1 FY26) which management expects to normalize; per-project bidding against Array Technologies, GameChange, Arctech and PV Hardware — no contract lock-in beyond the $5.5B backlog; 83% U.S. revenue concentration exposes the whole P&L to U.S. tax-credit, tariff and permitting policy; SBC is rising fast (see above) and dilutes the OE/share compounding the moat is supposed to produce.
- A 6 gives CAP = 9.8 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — final run (2026-10-17)
Growth sanity check (mandatory): the engine blend is 20.21% (rev CAGR 5y 24.39%, 3y 23.22%, latest YoY +20.28%, OE/share CAGR 2y only 1.81% — the blend is a revenue blend, and OE/share has NOT kept pace, which is why the OE multipliers and bear weight matter). Against actual prints: FY26 revenue +20.28%; Q1 FY27 revenue +8.2% YoY ($935M) — well below the base start, written reason: management RAISED FY27 guidance after that print to $4.10–$4.40B revenue (vs FY26 $3,559,390,000), i.e. +15% to +24% growth for the full year, on a >$5.5B backlog — the base start sits inside the company's own guided range, and the super-bear start (8.21%) is set exactly at the Q1 print in case Q1, not guidance, is the truth. Bull (25.21%) sits just above the guidance top end and needs a guidance beat plus storage/power-conversion conversion; super bull (32.21%) exceeds every recent full-year print — it gets only 8% probability for that reason. Probabilities were shifted bear-ward from the 10/25/30/25/10 defaults to 15/30/30/17/08 per the OE_VOLATILE flag instruction. OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $80.04.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | 8.2% | 0.75 | Q1 FY27 pace is the real pace; 45X/tariff benefits normalize, platform opex (+56% YoY in Q1) sticks | $21.52 | 6.08% |
| Bear | 30% | 15.2% | 0.90 | Growth at the low end of guidance; OE/share keeps lagging revenue on SBC/WC | $35.22 | 8.51% |
| Base | 30% | 20.2% | 1.00 | Guidance mid-range delivers; backlog converts | $48.78 | 10.70% |
| Bull | 17% | 25.2% | 1.10 | Guidance beaten; non-tracker mix (14% of Q1 revenue) scales | $66.76 | 13.29% |
| Super bull | 8% | 32.2% | 1.25 | Platform story fully lands — storage + power conversion re-rate growth | $102.63 | 17.59% |

- **Probability-weighted: IV@15% $47.99 (−40.0% vs price), IV@12% $66.57, IV@10% $87.67, weighted IRR 10.61%, base-case IRR 10.70%**
- **Tier by numbers: C.** Diagnostics (dcf_numbers.json): OE yield 3.39%, terminal value 23.3% of IV@15%, scenario spread 4.77x, 6.6 months since FY end. Hurdle-clearing price at 15%: $47.99; at 20%: $31.79; at 25%: $23.23.

## Flags — every fragility flag resolved
- **OE_VOLATILE** (OE/share spans >3x over 5 years: $0.4970 → $3.3696 → $2.5757): real cyclicality, not a data error — FY22 OCF was negative in the supply-chain trough and FY25 was a peak. Handled as instructed: bear weight widened (super bear + bear = 45% vs 35% default) and the TTM base was checked against the median ($2.7143 vs $2.5757 — close, neither is an outlier pick).
- **DEBT_TAGS_BLANK** (no debt tag for the latest FY): resolved from the filing/company reporting above — no debt outstanding, cash $1,094,976,000 at FY26 end. Net debt is not unknown in substance; the tag is blank because the balance is zero. No leverage risk; the DCF's null net_debt is conservative (it credits no net cash).
- **WIDE_SCENARIO_SPREAD** (super-bull IV 4.77x super-bear IV): real — the range between "Q1 pace + credit normalization" and "platform re-rate" IS this wide. Confidence is capped at medium, and the verdict is sized to the conservative (bear) end.
- **TIER_BAND** (bear tier D at 8.51% vs bull tier C at 13.29%): the verdict spans tiers; any position must be sized to the bear end (Tier D economics, IV@15 $35.22), not the weighted C.

## My thoughts / overlay
- Quality is not the debate: net cash, investment-grade, #1 share, 46–72% ROIC proxy in the clean years, backlog >$5.5B against $3.63B TTM revenue. The debate is price and OE/share conversion: revenue compounded ~24% over 5 years while OE/share CAGR (2y) is 1.81% — SBC, working capital and 45X-dependent margins eat the growth before it reaches the share.
- The 45X question cuts both ways in the OE base: TTM OE includes roughly $99M of 45X/tariff benefit in a single quarter's gross profit. If those credits normalize faster than volume grows, even the bear OE multiplier (0.90) may be kind; if they persist, the base is understated. That asymmetry is priced into the 45% bear-or-worse weight, not into a base_override — no override was used or needed.
- Method range: on the preliminary default run (median base, moat 5, default probs) the weighted IRR was 10.33% / IV@15 $46.57; on this final TTM-base run it is 10.61% / $47.99. Both are Tier C — the verdict is not assumption-sensitive at this price. Even the bull case (13.29%) does not clear 15%.
- What would change the verdict: a price near $48 (the 15% hurdle price), or evidence OE/share — not just revenue — is compounding (SBC flattening as a share of OCF, OCF conversion recovering to FY25 levels).

## Final verdict
- **Final tier: C** (weighted IRR 10.61% on the final TTM-base inputs; bear D / bull C band, sized to the bear end)
- Confidence: **Medium** (clean filing data and a stable base, capped by the 4.77x scenario spread and 45X/policy dependence)
- One-liner: High-quality solar-tracker leader, moat 6/10 — but at $80.04 it does not clear 15% (10.6% weighted IRR, IV@15 $47.99); it clears 15% only at ~$48.
