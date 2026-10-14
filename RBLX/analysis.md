# RBLX — Roblox Corporation
v5 run, 2026-10-14 (supersedes the v4 analysis of 2026-10-13; conclusions unchanged). In scope: market cap $34.053B at $49.38 (key_numbers.md, nasdaq_quote_api) — under $40B.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.json, or financials_history.csv — none are recomputed.

## What it is
A user-generated-content gaming platform, not a game studio: millions of creator-built experiences played inside one client, monetized mainly through Robux (virtual currency bought with cash = "bookings," recognized as revenue over the life of virtual items / user engagement). Q2 2026 scale from search results: 123M daily active users (+10% YoY), 29B hours engaged (+5%), revenue $1.5B (+36%), bookings $1.6B (+8% at the low end of guidance). Management attributed the bookings softness to a mix shift away from last year's high-monetizing viral experiences and to discovery-algorithm changes prioritizing long-term retention over near-term monetization, plus rising AI infrastructure spend. Q3 2026 bookings were guided to $1.58–$1.65B, a 14–18% YoY decline, and full-year guidance was not updated / was withdrawn on elevated variability.

## Owner's earnings
History (conservative OE = OCF − capex − SBC, from financials_history.csv): FY2023 −$730,454,000, FY2024 −$373,124,000, FY2025 +$226,376,000. OE positive in 2 of the last 5 fiscal years (key_numbers.md).
- FY2025 detail: OCF $1,796,358,000 − capex $440,978,000 − SBC $1,129,004,000 = conservative OE $226,376,000 = latest FY OE/share $0.33 (key_numbers.md).
- Maintenance version FY2025: −$278,232,000 (financials_history.csv) — negative even in the first positive conservative year, because GAAP net income (−$1,065,057,000) already carries the full SBC expense and the working-capital term is dominated by the deferred-revenue book. The two definitions disagree on the sign in FY2025; the OCF-based conservative figure is the cleaner one for a bookings/deferred-revenue business, and it is the one the engine uses.
- **Normalized base (3-yr median OE/share): −$0.58/share → the preliminary v5 engine run was Tier F.** That median is a lagging artifact, not current earning power (see BASE_DIVERGENCE resolution under Flags).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math; ttm.json):**
- OCF: FY $1,796,358,000 − prior YTD $643,000,000 + current YTD $947,000,000 = **TTM $2,100,358,000**
- Capex: FY $440,978,000 − prior YTD $40,000,000 + current YTD $55,000,000 = **TTM $455,978,000**
- SBC: FY $1,129,004,000 − prior YTD $544,000,000 + current YTD $557,000,000 = **TTM $1,142,004,000**
- Shares (current-YTD weighted diluted): **714,246,000**
- **TTM OE total $502,376,000 → base OE/share $0.70** (key_numbers.md: base OE/share $0.70, source: ttm_json; ttm.json ttm_oe_per_share 0.703365507122196)
- The inflection is filing-real: OCF scaled while SBC growth flattened (SBC $867,967,000 in FY2023 → $1,015,794,000 in FY2024 → $1,129,004,000 in FY2025 → $1,142,004,000 TTM, all from financials_history.csv / ttm.json). SBC remains the single largest cost in the OE bridge.

## Moat: 6/10 — moderate-strong network, unproven pricing power
Justification: Two-sided network effects at 123M DAU scale, a creator ecosystem and content library rivals cannot copy quickly, and social-graph/identity lock-in for a cohort growing up on the platform — but no owned IP or content exclusivity (creators multi-home), pricing power unproven and currently backwards, a structural child-safety regulatory/litigation tax, and no proven returns on capital (GAAP losses in every year of history).
- FOR: Two-sided network effects at 123M DAU scale — creators follow users, users follow creator content; Creator ecosystem and content library that rivals cannot copy quickly; content concentration falling; Social-graph and identity lock-in — friendships, avatars, inventories and Robux balances live inside Roblox; Infrastructure and safety/ML stack built over a decade for real-time 3D at scale on cheap devices.
- AGAINST: No owned IP or content exclusivity — creators multi-home to Fortnite Creative, Minecraft and standalone engines; Pricing power unproven and backwards — bookings per DAU/payer fell in Q2 2026, DevEx rate raised to creators; Structural child-safety tax — global age checks in Jan 2026 cut communication density, plus active litigation and COPPA 2.0 / EU DSA scrutiny; No proven returns on capital — GAAP losses in every year of history.
- A 6 gives CAP = 9.8 years (key_numbers.md): growth holds 2 years, then converges linearly to the 2.5% terminal rate over 9.8 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Price: **$49.38** (key_numbers.md). Base: TTM OE **$0.70/share** — OE yield 1.42% (key_numbers.md). The price is ~70× TTM owner's earnings; everything depends on growth.

**Growth recalibration (written reason, per the standing rule):** the engine's growth blend is 35.77% → g_base 30.77% (key_numbers.md; components: rev CAGR 5y 39.56%, rev CAGR 3y 30.01%, latest rev YoY 35.77%). Those are *revenue* signals, and revenue here is a lagging indicator — it recognizes bookings collected in earlier periods. The forward cash indicator is bookings, and bookings have broken: +8% in Q2 2026 (low end of guidance), Q3 2026 guided to a 14–18% YoY decline, full-year guidance not updated. OE is collected cash minus SBC and capex, so OE growth must be set off bookings, not off the +36% revenue print. Scenario starts were therefore recalibrated down via offsets (−0.308 / −0.228 / −0.158 / −0.088 / −0.008 vs g_base) to −0.0% / 8.0% / 15.0% / 22.0% / 30.0% (key_numbers.md scenario table). Even the super-bull start (30.0%) sits below the latest revenue YoY (35.77%) — the written reason is the bookings guide above; a super-bull above the bookings trajectory would be inventing a reacceleration no filing or guide shows. Probabilities skewed bearish (15/25/30/20/10 vs default 10/25/30/25/10) for the guidance withdrawal and the safety-litigation overhang. Multipliers left at defaults (0.75/0.90/1.00/1.10/1.25).

| Scenario | Prob | Growth start | OE mult | Story | IV@15% | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | -0.0% | 0.75 | Bookings decline persists, safety costs and AI infra spend rise, SBC stays elevated; OE flat at a haircut level | $3.87 | 3.44% |
| Bear | 25% | 8.0% | 0.90 | Bookings recover only to high-single digits; monetization per user keeps slipping | $6.62 | 4.31% |
| Base | 30% | 15.0% | 1.00 | Bookings stabilize after Q3, SBC discipline continues; OE compounds mid-teens | $10.04 | 5.42% |
| Bull | 20% | 22.0% | 1.10 | Retention-first discovery pays off, aging-up monetization lifts bookings/DAU, OE leverage returns | $15.02 | 6.97% |
| Super bull | 10% | 30.0% | 1.25 | Bookings reaccelerate toward revenue growth in 2027+, platform takes share of global gaming spend | $24.16 | 9.52% |

- **Probability-weighted: IV@15% $10.67, IV@12% $14.68, IV@10% $19.22, weighted IRR 5.67%, base-case IRR 5.42%** (key_numbers.md)
- **Tier by numbers: D.** Upside at 15%: −78.4% (key_numbers.md).
- Diagnostics (key_numbers.md): OE yield 1.42%, terminal value 22.4% of IV@15%, scenario spread 6.25x, net debt / normalized OE −0.44x, 9.4 months since FY end.
- Sanity check: no scenario — not even super bull at a 30.0% start and a 1.25× OE multiplier (IRR 9.52%) — clears even a 10% IRR at $49.38. The binding constraint is the $0.70 base against a $49.38 price, not the growth debate.

## Flags — every fragility flag resolved
Final-run flags from dcf_numbers.json / key_numbers.md:
- **STALE_FY** (latest fiscal year ended 9 months ago; 9.4 months since FY end in key_numbers.md): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above with its FY / prior-YTD / current-YTD inputs.
- **DILUTION** (share count growing 5.0%/yr; share count CAGR 5.01%, growth adj −5.00% in key_numbers.md): driver is SBC (TTM $1,142,004,000 from ttm.json). The engine already deducted the maximum −5pp in its blend; the recalibrated scenario starts are OE/share growth targets set below revenue growth for the same reason.
- **BASIS_BREAK_SUSPECT** (>60% revenue jump/drop in last 5 yrs): the >60% jumps are 2020 (+82% on the filed history: $508,393,000 → $923,885,000) and 2021 ($923,885,000 → $1,919,181,000) — the pandemic surge, not a divestiture, acquisition, or restatement in the recent window (2023–2025 revenue growth was sequential and filing-consistent in financials_history.csv). Consequence: the 5-yr revenue CAGR (39.56%) straddles the pandemic step-up and overstates the forward run-rate — one more reason scenario starts were set off bookings, not the blend.
- **NI_OCF_DIVERGENCE** (2023, 2024, 2025): resolved — the gap is SBC, not a one-off cash item. From financials_history.csv: net income vs OCF was −$1,151,946,000 vs +$458,180,000 in 2023, −$935,384,000 vs +$822,316,000 in 2024, and −$1,065,057,000 vs +$1,796,358,000 in 2025. The non-cash SBC added back ($867,967,000 / $1,015,794,000 / $1,129,004,000) plus D&A explains the divergence in every named year; no tax deposit, impairment, or WC one-off is distorting the OCF-based OE — and OE subtracts SBC explicitly, so the base is not flattered by the add-back.
- **LOW_OE_YIELD** (base OE yield 1.4%; 1.42% in key_numbers.md): resolved by acknowledgment, not adjustment — at ~70× TTM OE the valuation rests almost entirely on future growth, which is exactly what the recalibrated scenarios and the low confidence grade reflect.
- **WIDE_SCENARIO_SPREAD** (super-bull IV is 6.2x super-bear IV; 6.25x in key_numbers.md): real uncertainty (bookings are guided negative next quarter), and it caps confidence below high by rule — confidence is low here for additional base-history reasons below.
- **BASE_DIVERGENCE (manual — noted in the preliminary run):** latest FY $0.33 vs 3-yr median −$0.58 vs TTM $0.70 (all key_numbers.md). The median is the distorted one: two of its three years (2023, 2024) predate the OE inflection, when OCF was $458,180,000 / $822,316,000 against SBC of $867,967,000 / $1,015,794,000. OCF has since scaled while SBC flattened, so the median measures a cost structure that no longer exists. The TTM base is used, with this reasoning — the most generous defensible base, and the tier is still D.

## Thoughts / overlay
- The business inflected; the stock price already paid for the next several inflections. Roblox finally prints positive owner's earnings — $0.70/share TTM — and at $49.38 that is a 1.42% OE yield with bookings guided down 14–18% next quarter. The bull debate (does retention-first discovery + aging-up reaccelerate bookings in 2027?) is a debate about whether the weighted IRR is ~6% or ~9%, not about clearing 15%.
- Method range, documented: median base → **F** (no DCF at all, preliminary run); TTM base with bookings-calibrated growth (final) → 5.67% weighted IRR, **D**. Every filing-defensible method lands at D or below on the TTM base; there is no defensible route to B/A here without assuming both a much larger OE base than any filing shows and a bookings reacceleration no guide supports.
- Balance sheet: net debt (latest) −$212.2M (key_numbers.md) — i.e. net cash on the engine's cash-only definition, a cushion, not a thesis. Current liabilities are dominated by deferred revenue / creator obligations in this business model — an obligation to deliver service, not financial debt — which is why the fuller liquid-asset picture is not quoted here: the figures needed are not in the computed outputs for this v5 run.
- Risks: child-safety litigation and regulation (global age checks rolled out January 2026, only about half of global DAUs age-checked by end-Q1 2026 per search results, with management citing friction in sign-ups; a securities class action followed the disclosures), monetization per user falling while AI infrastructure spend rises, and creator-economics pressure (DevEx).

## Final verdict
- **Final tier: D** (= tier by numbers; no override — the TTM base already gives the company its most generous defensible base, and it still lands in D)
- Confidence: **Low** — the arithmetic is filing-exact, but the base rests on the first positive OE periods in company history, the scenario spread is 6.25x, and the forward bookings guide contradicts the backward revenue signals the engine blends.
- Hurdle math: the price that clears 15% on the weighted case is the weighted IV@15% itself — **$10.67**, ~78% below $49.38; even the super-bull IV@15% ($24.16) is well below the price, so there is no margin-of-safety price near current levels to quote.
- One-liner: Real UGC gaming platform, moat 6/10, finally inflected to positive owner's earnings ($0.70/share TTM) — but at $49.38 (~70x TTM OE, 1.4% yield) with Q3 2026 bookings guided down 14-18%, it clears only a 5.7% weighted IRR (IV@15% $10.67); it would need to trade near $11 to clear the 15% hurdle.
