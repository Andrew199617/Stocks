# ACGL — Arch Capital Group Ltd.
v5 run, 2026-10-14. Price $96.035 (nasdaq_quote_api), market cap $36,099,556,500 (dcf_numbers.json) — in scope under $40B.

All figures below are copied from dcf_numbers.json, ttm.py output (ttm.json), financials_history.csv, or the company's Q2 2026 earnings release as returned by search — none are recomputed.

## What it is
Bermuda-based diversified insurer with three segments: specialty (primary) insurance, reinsurance, and mortgage insurance (a U.S. mortgage-insurance leadership position). Earnings come from underwriting plus investment income on the float — Q2 2026 pre-tax net investment income was $417 million and the release put book value per common share at $68.04 at June 30, 2026. This is a Finance-sector name: the standardized owner's-earnings/capex DCF fits it poorly (see SECTOR_MODEL_MISMATCH below), so the tier is softened and confidence is low.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** revenue $19,929,000,000; net income $4,399,000,000; operating cash flow $6,172,000,000; capex $44,000,000 (tag PaymentsToAcquireProductiveAssets); SBC $148,000,000.
- **Conservative owner's earnings FY2025: $5,980,000,000 = $15.91/share** (base_oe_latest_per_share 15.908486299547752 in dcf_numbers.json).
- Maintenance version: not produced — the engine's D&A tag is null for this filer (used_tags.da: null in dcf_numbers.json) and the maintenance column is blank in financials_history.csv, so no second definition is available to quote. That is stated in words rather than calculated, per the sweep's hard rule.
- OE positive 5 of the last 5 fiscal years (oe_positive_years_of_last_5: 5/5). Net debt is null in dcf_numbers.json (an insurer's balance sheet does not reduce to the engine's cash-minus-debt fields) — balance-sheet risk is handled through the verdict, not a net-debt figure.
- **The structural caveat that drives this whole verdict:** for a growing insurer, OCF collects premiums and builds loss reserves/unearned premiums — cash that belongs to future claimants. FY2025 OCF of $6,172,000,000 against net income of $4,399,000,000 (both from financials_history.csv) is that float effect, not a one-off. The OCF-based OE base is therefore an upper bound on distributable owner's earnings, exactly as in the HIG pass.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $6,172,000,000 − prior YTD $2,582,000,000 + current YTD $2,510,000,000 = **TTM $6,100,000,000**
- Capex: FY $44,000,000 − prior YTD $21,000,000 + current YTD $22,000,000 = **TTM $45,000,000**
- SBC: FY $148,000,000 − prior YTD $99,000,000 + current YTD $97,000,000 = **TTM $146,000,000**
- Shares (current-YTD weighted diluted): **354,200,000** (FY2025: 375,900,000 — the count fell on heavy buybacks, $1.2 billion repurchased in Q2 2026 alone and $1.95 billion in H1 2026 per the Q2 release)
- **TTM OE total $5,909,000,000 → base OE/share $16.68** (16.68266516092603, base_source: ttm_json)
- The engine's normalized base (median of last 3 FY) is $15.91/share. The TTM base is used per the STALE_FY rule; the two are close, so the base choice is not the swing factor here — the growth rate and the float caveat are.

**Latest quarter (Q2 2026 release, via search):** net income available to common shareholders $1.0 billion, or $3.00/share (18.0% annualized net income ROE); after-tax operating income $893 million, or $2.56/share (15.3% annualized operating ROE), vs $2.58/share a year earlier. Gross premiums written $6,126 million (−1.1% YoY), net premiums written $4,049 million (−6.9%), net premiums earned $3,985 million (−8.1%), underwriting income $657 million (−19.7%). Combined ratio 83.5% vs 81.2% a year earlier; excluding catastrophe activity and prior-year development, 82.5% vs 80.9%. Pre-tax catastrophe losses were $201 million, partly offset by $165 million of favorable prior-year reserve development. Segment color: insurance combined ratio deteriorated to 98.5% (catastrophe losses tied in part to the Iran conflict / political-violence and marine war lines), reinsurance combined ratio 77.5%, mortgage underwriting income $220 million. Management described the market as in the early stages of softening, with property reinsurance pricing under pressure at renewals, and said it is walking away from under-priced business rather than chasing share.

## Moat: 5/10 — moderate/narrow
Justification: a top-tier underwriting franchise — disciplined cycle management, three diversified segments, leadership in specialty lines and U.S. mortgage insurance, and mid-to-high-teens operating ROE held through the cycle — capped at moderate because the product is commodity risk capital repriced annually: no structural pricing power, no customer lock-in, and returns are set by the industry cycle and catastrophe luck as much as by the franchise.
- FOR: Disciplined cycle management — shrinking premiums into the softening market (net written −6.9% YoY in Q2 2026) instead of chasing share; compensation tied to long-term underwriting profitability per management.
- FOR: Diversified three-segment platform (specialty insurance, reinsurance, mortgage) — segments offset each other (Q2 2026: reinsurance and mortgage carried a weak insurance segment).
- FOR: Leadership positions in specialty insurance and U.S. mortgage insurance; clients buy underwriting expertise and claims capability, not just capacity (Q2 2026 release).
- FOR: Proven returns through a cycle — Q2 2026 annualized operating ROE 15.3% even in a deteriorating combined-ratio quarter; OE positive 5 of the last 5 fiscal years.
- FOR: Capital return as a real per-share engine — $1.95 billion of buybacks in H1 2026, diluted share count down to 354,200,000 (ttm.json) from 375,900,000 in FY2025.
- AGAINST: Commodity product — insurance/reinsurance capacity is fungible, contracts reprice annually, brokers can move business; no structural pricing power.
- AGAINST: Price-taker in a softening cycle — property reinsurance rates already falling at renewals, competition and third-party capital set the price, not Arch.
- AGAINST: Catastrophe and geopolitical tail — $201 million of pre-tax cat losses in one quarter (including conflict-related lines); a single large event year can erase a year of underwriting profit and hit book value.
- AGAINST: Reserve risk — earnings lean on favorable prior-year development ($165 million in Q2 2026); adverse development would reverse the same way.
- AGAINST: Mortgage insurance concentration in U.S. housing credit and GSE/housing-policy risk — a housing downturn hits that segment's loss ratio first.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
**Growth sanity check (mandatory):** the engine's g_base is 16.57% (g_blend 16.42%), built from revenue CAGRs of 18.56% (5y) and 27.50% (3y) and latest revenue YoY of +14.27% — all hard-market history (the 2023–24 premium surge). The OE/share CAGR 2y component is only 3.70%. Against actual current prints the blend is not credible as a forward start: Q2 2026 gross premiums written −1.1% YoY, net premiums written −6.9%, net premiums earned −8.1%, operating EPS $2.56 vs $2.58 (−0.8% area, as reported), combined ratio worsening, and management explicitly in the early stages of a softening market, shrinking writings on purpose. Scenario starts were therefore recalibrated via offsets (−0.2657 / −0.2057 / −0.1457 / −0.1057 / −0.0657 vs g_base) to −10% / −4% / +2% / +6% / +10%. The base start of +2% is per-share OE growth — roughly flat total OE plus buyback accretion — not premium growth. Even the super-bull start (+10%) sits below the engine blend and below the FY2025 revenue print, with the written reason being the guided/observed softening cycle; the bull cases require the cycle to re-harden, not merely continue. Probabilities were skewed bearish for the same reason (15/30/30/15/10 vs the 10/25/30/25/10 default): 45% on bear-or-worse in an early soft market. OE multipliers kept at the defaults 0.75/0.90/1.00/1.10/1.25 — the super-bear multiplier is where a major catastrophe/reserve year lands. Moat 5, TTM base $16.68/share, price $96.035.

| Scenario | Prob | Growth start | OE mult | Story | IV@15% | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −10.0% | 0.75 | Major cat/reserve year lands in a soft market; premiums and OE contract | $60.76 | 9.89% |
| Bear | 30% | −4.0% | 0.90 | Soft cycle deepens; writings shrink, combined ratio keeps deteriorating | $93.80 | 14.69% |
| Base | 30% | +2.0% | 1.00 | Flat total OE, buybacks carry per-share growth; soft but disciplined | $133.95 | 19.97% |
| Bull | 15% | +6.0% | 1.10 | Softening stays shallow; casualty/specialty rates hold, buybacks compound | $174.00 | 24.64% |
| Super bull | 10% | +10.0% | 1.25 | Cycle re-hardens early; Arch deploys capital at hard-market returns again | $233.23 | 30.79% |

- **Probability-weighted: IV@15% $126.86 (+32.1% vs price), IV@12% $166.65, IV@10% $210.84, weighted IRR 19.05%, base-case IRR 19.97%**
- **Tier by numbers: B.** Diagnostics (dcf_numbers.json): OE yield 17.37%, terminal value 17.65% of IV@15%, scenario spread 3.84x, 9.43 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (latest fiscal year ended 9.43 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, inputs quoted above. TTM total OE ($5,909,000,000) is slightly below FY2025 ($5,980,000,000); the per-share base rose only because buybacks cut the share count.
- **SECTOR_MODEL_MISMATCH** (Finance — OE/capex DCF fits finance names poorly): real and binding. An insurer's OCF capitalizes float/reserve growth (FY2025 OCF $6,172,000,000 vs net income $4,399,000,000), capex ($44–45 million) is a rounding error against underwriting risk, and the maintenance-OE definition is not even produced (D&A tag null). Handled the same way as HIG: confidence low, and the final tier softened one notch from tier-by-numbers (see verdict). The engine numbers are an upper bound, not a point estimate.
- **WIDE_SCENARIO_SPREAD** (preliminary run: super-bull IV 4.41x super-bear IV): on the final recalibrated run the spread is 3.84x (dcf_numbers.json diagnostics) and the flag no longer fires, but the range is still wide in substance — a catastrophe year vs a re-hardening cycle genuinely spans IV@15% from $60.76 to $233.23. Confidence is low (also capped by the sector mismatch) and the verdict is sized to the conservative end.

## My thoughts / overlay
- The honest headline is the method range: on the engine's unadjusted hard-market growth blend the preliminary run printed Tier S (weighted IRR 30.44%, IV@15% $248.49); on current prints with recalibrated growth it is Tier B by numbers (19.05%); on an earnings (not float-capitalizing OCF) view of an insurer it is a notch lower still. Defensible methods span S→C, which is itself the finding — no single number for ACGL should be quoted without its method.
- Quality is not the debate: this is one of the best-run P&C franchises — disciplined enough to shrink into a soft market, diversified enough that two segments carried Q2 2026, and returning capital aggressively ($1.95 billion of H1 2026 buybacks). The debate is what a softening cycle does to earnings from here, and how much of the OCF "owner's earnings" is actually the owners'.
- Cross-check on reported figures only: book value per share was $68.04 at June 30, 2026 (Q2 release) against a $96.035 price, and Q2 annualized operating ROE was 15.3% — a good franchise at a full-ish price for a softening market, not an obvious bargain on earnings/book metrics the way the float-inflated OE yield (17.37%) makes it look.
- Hurdle math on engine numbers: the stock clears 15% at the weighted IV@15% of $126.86, but the bear case IV@15% is $93.80 — just below the current price. With a margin of safety against the bear case rather than the weighted case, a buyer wants a price in the low-$90s or below; at $96.035 the margin rests on the base/bull cases and on treating float-driven OCF as owner's earnings.

## Final verdict
- **Final tier: C** (tier_override from tier-by-numbers B — reason: SECTOR_MODEL_MISMATCH insurer artifact; the OCF-based OE base capitalizes float/reserve growth, so the engine's B overstates distributable owner's earnings; softened one notch, confidence low — same treatment as HIG)
- Confidence: **Low** (sector model mismatch; wide scenario range in substance)
- One-liner: High-quality diversified P&C/reinsurance/mortgage insurer, moat 5/10 — engine prints Tier B (weighted IRR 19.05%, IV@15% $126.86 vs $96.04) on a float-capitalizing OCF base, so the final tier is softened to C at low confidence; on engine numbers it clears 15% at ~$127, ~$94 (bear IV) with a margin of safety.
