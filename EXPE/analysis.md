# EXPE — Expedia Group, Inc.
v5 run, 2026-10-14. In scope (market cap $35.90B at $272.06, nasdaq_quote_api).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed.

## What it is
The #2/#3 global online travel agency: consumer brands Expedia.com, Hotels.com and Vrbo (alternative accommodations), plus a fast-growing B2B segment (Expedia Partner Solutions — white-label travel tech and hotel supply sold to airlines, offline agencies, banks and other partners) and trivago. Predominantly a merchant/agent booking model: travelers usually pay Expedia upfront and suppliers are paid later, so the balance sheet carries a large traveler-prepayment float. US-led, competing against Booking Holdings (global leader, higher margins), Airbnb (alt-accommodation leader) and Google at the top of the search funnel.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $14,733M; net income $1,294M; operating cash flow $3,880M; capex $770M (PaymentsToAcquirePropertyPlantAndEquipment); SBC $398M (ShareBasedCompensation — always a real cost).
- **Conservative owner's earnings FY2025: $2,712M = $20.55/share** (latest FY OE/share in dcf_numbers.json).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $2,654M — same ballpark as the conservative figure, which raises confidence.
- OE positive 5 of the last 5 fiscal years (engine: 5/5). The FY totals show a steep recovery path: $1,431M (2023) → $1,871M (2024) → $2,712M (2025), on a diluted share count shrinking from 150,228k (2023) to 131,943k (2025).
- Net debt (latest): $748M — small against these OE levels (final-run diagnostics: net debt 0.17x the base OE used).

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $3,880M − prior YTD (H1 2025) $4,073M + current YTD (H1 2026) $5,409M = **TTM $5,216M**
- Capex: FY $770M − prior YTD $396M + current YTD $383M = **TTM $757M**
- SBC: FY $398M − prior YTD $203M + current YTD $217M = **TTM $412M**
- Shares (current-YTD weighted diluted, ttm.py's documented basis): **123,763k**
- **TTM OE total $4,047M → base OE/share $32.70** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $13.57/share — rejected as the base: it is the FY2024 figure and averages in the depressed post-replatforming FY2023 (see BASE_DIVERGENCE below). It is still reported in key_numbers.md and anchors the conservative end of the method range.

## Moat: 5/10 — moderate / narrow
Justification: a real B2B platform and loyalty-driven direct traffic, but Expedia is the #2/#3 player in a market where the leader (Booking) is bigger and more profitable, the alt-accommodation leader (Airbnb) owns the stronger brand, and the top of the funnel belongs to Google and, increasingly, AI agents.
- FOR: B2B platform (Expedia Partner Solutions) — partner integrations are sticky and hard to replicate; B2B gross bookings grew +21% YoY in Q2 2026 (B2C +8%), and B2B revenue grew +23%.
- FOR: One Key unified loyalty program (reported 168M+ members) across Expedia/Hotels.com/Vrbo drives direct and app traffic, reducing dependence on paid search.
- FOR: Scale supply network and US market leadership in a two-sided marketplace; unified post-replatforming tech stack now compounding (Q2 2026 adjusted EBITDA +23%, margin expansion guided to continue).
- FOR: Merchant-model float is a structural, interest-free funding source while bookings grow.
- AGAINST: Booking Holdings is larger, more profitable (~37% EBITDA margins cited in coverage vs Expedia's mid-20s) and growing engagement faster — Morgan Stanley (Sept 2026) put Expedia MAU growth at 0% in Q2 2026 vs +6% Booking and +10% Airbnb, and rates the stock Underweight.
- AGAINST: Vrbo is #2 to Airbnb in alternative accommodations, where Airbnb's brand is the category default.
- AGAINST: Google controls the top of the travel search funnel; agentic-AI booking is a live disintermediation threat, and Expedia's supply skews to commoditized chain hotels and air.
- AGAINST: Suppliers keep pushing direct booking to bypass OTA commissions; short-term-rental regulation tightens in key European cities.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Growth recalibration (written reason): the engine's blended growth is 15.63% and g_base 20.63% after the +5pp buyback adjustment, but two blend components are artifacts — the 5-yr revenue CAGR (23.16%) spans the COVID collapse/rebound and the OE/share 2-yr CAGR (46.86%) is a recovery print off the depressed FY2023 base. The signals that mean something: latest revenue YoY +7.61% (FY2025), Q2 2026 revenue +14% YoY, and raised FY2026 guidance of +9–10% revenue and +8–9% gross bookings (Q3 2026 guided +5–8%). Per-share OE growth runs above revenue growth on guided EBITDA-margin expansion (+150–175bp for FY2026) and a share count shrinking ~6.6%/yr. Scenario starts were therefore set via offsets (−0.17 / −0.10 / −0.05 / 0.00 / +0.07 vs g_base) to 3.6 / 10.6 / **15.6** / 20.6 / 27.6%. Sanity check vs actual prints: the base start (15.6%) sits between guided revenue growth (~10%) and Q2's per-share earnings print (adjusted EPS +36% YoY) — defensible given margin expansion plus buybacks; the super-bull start (27.6%) is below that +36% print, with the written reason that Q2's print rides recovery dynamics and float growth that cannot compound indefinitely; the super-bear start (3.6%) is deliberately below every recent print — it is the travel-downturn / AI-disintermediation case, not a forecast. Probabilities kept at defaults 10/25/30/25/10 (momentum vs valuation/engagement concerns roughly offset); OE multipliers at defaults 0.75/0.90/1.00/1.10/1.25. Price $272.06.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 3.6% | 0.75 | Travel downturn + AI agents/Google squeeze OTA take; float inflow reverses | $210.75 | 12.21% |
| Bear | 25% | 10.6% | 0.90 | Growth decays to high-single digits; Booking/Airbnb take share; margins stall | $337.78 | 17.76% |
| Base | 30% | 15.6% | 1.00 | Guided revenue growth + margin expansion + buybacks compound per-share OE | $460.44 | 22.33% |
| Bull | 25% | 20.6% | 1.10 | B2B keeps growing ~20%+ and becomes the mix driver; One Key lifts direct mix | $619.95 | 27.39% |
| Super bull | 10% | 27.6% | 1.25 | B2B platform dominance + sustained margin expansion; float keeps compounding | $931.00 | 35.34% |

- **Probability-weighted: IV@15% $491.74 (+80.75% vs price), IV@12% $671.32, IV@10% $873.68, weighted IRR 23.30%, base-case IRR 22.33%**
- **Tier by numbers: A.** Diagnostics (final dcf_numbers.json): OE yield 12.02%, terminal value 21.46% of IV@15%, scenario spread 4.42x, net debt 0.17x base OE, 9.43 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.43 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, inputs quoted above.
- **BASE_DIVERGENCE** (latest FY $20.55 vs 3-yr median $13.57): the median is the distorted figure — the OE series rises steeply through it ($1,431M → $1,871M → $2,712M → TTM $4,047M in totals) on post-replatforming recovery, margin expansion and buybacks, so a 3-yr median anchored on FY2023–24 understates the current run-rate. The latest FY and TTM continue the same trend and Q2 2026 corroborates (quarterly OCF +32% YoY per the earnings release). The honest counterweight: TTM OCF includes the merchant-float working-capital inflow, which scales with bookings growth — if growth stalls, OCF normalizes down toward earnings-plus-D&A levels. That is why the verdict is sized below the numbers tier (see Thoughts).
- **NI_OCF_DIVERGENCE** (2023, 2024, 2025): structural, not a one-off. OCF exceeds net income every year because (i) D&A ($807M / $838M / $887M across 2023–25) and SBC ($413M / $458M / $398M) are non-cash add-backs, and (ii) the merchant model collects traveler cash before paying suppliers, so growing deferred bookings are a working-capital cash source (ΔNWC is a cash source in all three years in financials_history.csv). The OCF-based conservative OE already subtracts SBC and capex, so the divergence does not inflate the base beyond the float effect flagged under BASE_DIVERGENCE.
- **BASIS_BREAK_SUSPECT**: the >60% revenue move in the last 5 years is COVID, not M&A or a divestiture — revenue fell to $5,199M in 2020 (from $12,067M in 2019) and rebounded +65% (2021) and +36% (2022). No recent basis break in the OE series itself; the fix is in the growth inputs, which ignore the 5-yr CAGR (23.16%) as a rebound artifact and anchor on guidance and current prints instead.
- **BUYBACK_TAILWIND** (share count −6.6%/yr): already credited via the +5pp growth adjustment in the blend and via the lower TTM share count in the base; not double-counted in the verdict. Buybacks continued in Q2 2026 (~880k shares for $200M per the earnings release).
- **WIDE_SCENARIO_SPREAD** (4.42x): real — the outcome range hinges on whether the float-assisted TTM run-rate holds. Confidence is medium (never high with this flag), and the final tier is sized to the conservative end of the method range.

## My thoughts / overlay
- The honest headline is the *range* across defensible bases: the preliminary run on the 3-yr median base ($13.57/share, default scenarios) gave weighted IRR 14.11% and IV@15% $249.37 — Tier C, below the $272.06 price. The final run on the TTM base ($32.70/share, recalibrated growth) gives 23.30% and $491.74 — Tier A. The latest audited FY base ($20.55/share) sits between the two. Anyone quoting one number for EXPE without its base is hiding the ball.
- What separates the runs is mostly one question: how much of the TTM OCF jump (TTM OCF $5,216M vs FY2025 $3,880M) is durable earnings power vs bookings-growth float? The earnings evidence (Q2 2026 revenue +14%, adjusted EBITDA +23%, guidance raised) says a large part is real operating improvement; the float mechanics say not all of it survives a flat-bookings year.
- Quality is decent, not elite: asset-light, SBC a modest share of OCF ($412M TTM), net debt only $748M, disciplined buybacks — against a #2/#3 competitive position, an engagement stall flagged by Morgan Stanley, and reported unresolved IRS transfer-pricing exposure as a contingent overhang.
- Margin of safety: at $272.06 the weighted IV@15% sits 80.75% above the price on TTM inputs (upside_at_15, final run); against the median base the price is *above* IV@15% ($249.37). The price that clears 15% with a margin of safety is the conservative end — at or below the median-base IV of ~$249 the 15% hurdle is cleared even if the float benefit fully normalizes. **Tier override to B** (from A by numbers): the method range spans C to A on one unresolved question (float durability), the spread flag is present, and the standing rule is to size the verdict to the conservative end when the spread is wide.

## Final verdict
- **Final tier: B** (tier_override from A by numbers — weighted IRR 23.30% on TTM inputs, 14.11% on the median base; method range C to A)
- Confidence: **Medium** (high on the filing-derived TTM arithmetic, medium-low on float durability and the AI/engagement overhang)
- One-liner: Quality OTA with a sticky B2B platform, moat 5/10 — clears 15% easily on TTM numbers (23.3% weighted, IV $492 vs $272) but the TTM base rides merchant-float growth; on the conservative median base it doesn't clear (IV $249), so size it as a B, not an A.
