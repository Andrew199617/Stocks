# RNR — RenaissanceRe Holdings Ltd.

Finance / Property & Casualty Reinsurance · Price $351.53 · Market cap (est) $16.340B · Engine 5.5.0, 2026-10-19
**Final tier: C · confidence low · weighted IRR 10.72% · weighted IV@15% $229.39**

## What it is

Bermuda-based global reinsurer founded in 1993 after Hurricane Andrew. Two underwriting segments — Property (led by property catastrophe) and Casualty & Specialty — plus RenaissanceRe Capital Partners, which manages third-party capital through joint ventures and ILS funds (DaVinci, Vermeer, Fontana, Medici, Upsilon). Management frames the business as three drivers of profit: underwriting, fee income, and net investment income. On November 1, 2023 it closed the acquisition of Validus Re from AIG (treaty reinsurance, the AlphaCat ILS manager, and Talbot treaty renewal rights) for total consideration of about $3.3B; the FY2023 10-K cash-flow statement shows a net Validus purchase outflow of $2,433,746,000 in investing activities plus $285,168,000 of non-cash consideration.

Current form is strong but the cycle is turning: Q2 2026 combined ratio 72.8%, operating income available to common shareholders $547.8M, annualized operating ROE 20.1%, book value per common share $264.77 (+24.8% YoY), fee income $83.0M, net investment income $432.5M — while gross premiums written fell 12.5% YoY as U.S. property-catastrophe rates dropped high-teens at the mid-year renewals and the company bought more retrocession rather than chase softening prices. Casualty & Specialty is the weak leg: a 103.3% combined ratio and an underwriting loss in Q2 2026, with $58.0M of adverse prior-year development in the quarter. Capital return is aggressive: $350.0M repurchased in Q2 2026, ~11.5M shares (~22% of the starting count) for ~$3B over the two years to Q2 2026.

## Owner's earnings — the payable-earnings base

For a P&C reinsurer the base is **payable earnings**: the five-year average of operating income available to common shareholders (WORKER_SPEC step 4; Andrew, 2026-10-19). Construction (key_numbers.md, "Payable-earnings base"; declaration in judgment.json, registry event `base_override`):

- Operating income available to common, last 5 FY (oldest first, exact): $81,599,000 / $322,791,000 / $1,824,910,000 / $2,234,426,000 / $1,859,691,000
- Average: $1,264,683,400 · shares diluted (latest): 46,483,000
- Per ordinary share: $27.21 × ADS ratio 1.0 = pinned base **$27.2074**

Base used: **$27.2074/share** (base_source: judgment_base_override). A five-year average rather than a 3-year median because FY2023–25 are three benign-cat hard-market years and FY2021–22 are the cycle's loss years (combined ratios 102.1% / 97.7%) — the average is the through-cycle normalization this filer needs. Measured impact of the pin (registry, same engine configuration replayed both ways): base OE/share $77.7834 → $27.2074 (−65.02%), weighted IRR 25.52% → 10.72% (−14.80pp), tier by numbers S → C.

The engine's OCF-based figures are kept as context for why they are **not** the base. Conservative OE = OCF − capex − SBC (filed history, financials_history.csv):

| FY | Revenue | Net income (attrib.) | OCF | SBC | OE/share (conservative) |
|---|---|---|---|---|---|
| 2021 | $5,277,709,000 | -$40,155,000 | $1,234,815,000 | $40,000,000 | $25.33 |
| 2022 | $5,060,412,000 | -$1,061,203,000 | $1,603,683,000 | $45,200,000 | $36.21 |
| 2023 | $9,134,608,000 | $2,561,132,000 | $1,911,634,000 | $60,300,000 | $38.89 |
| 2024 | $11,695,148,000 | $1,870,360,000 | $4,164,822,000 | $71,400,000 | $79.73 |
| 2025 | $12,848,074,000 | $2,682,334,000 | $3,693,107,000 | $77,500,000 | $77.78 |

On that basis the engine's normalized (3-yr median) OE/share is $77.78 and the latest-FY OE total is $3.616B on 46,483,000 diluted shares (OE-positive years 5/5 over the last five). Two structural reasons it overstates what common shareholders earn:

1. **The OCF base capitalizes float and other people's capital.** FY2025 OCF of $3,693,107,000 is consolidated: it includes a $998,854,000 increase in the reserve for claims and claim expenses (premiums collected, claims not yet paid) and the cash earnings of the Capital Partners vehicles, of which $935,409,000 of FY2025 net income is attributable to redeemable noncontrolling interests, not to RNR common shareholders (both FY2025 10-K). The same filing's diluted EPS available to common shareholders is $56.03 — the $77.78 OE/share base sits well above what common shareholders actually earned per share even in a hard-market year.
2. **The median window is three benign-cat hard-market years.** 2023–2025 had no franchise-breaking catastrophe year; 2021–2022 printed attributable net losses (-$40,155,000 and -$1,061,203,000) while OCF-based OE/share stayed positive ($25.33 / $36.21) precisely because OCF does not charge for reserve inadequacy the way earnings eventually do. The payable base's five annual figures span $81,599,000 to $2,234,426,000 — that spread is the cycle, and the average prices it in instead of selecting the benign half.

This re-run replaces the previously published record (Tier A final, S by numbers, on the OCF base with a one-notch softening): the tier is now the numbers tier on the payable base, with no softening applied on top.

TTM: `ttm.py` refuses for RNR — ShareBasedCompensation is tagged only annually in this filer's companyfacts (the only SBC fact is the FY2025 full-year figure), so there is no post-FY YTD SBC fact to build a TTM OE pin from, and no --ttm base was used. The filed H1 legs that do exist argue against any TTM uplift anyway: H1 2026 OCF of $1,539,924,000 vs H1 2025 OCF of $1,627,334,000, and H1 2026 net income (attributable) of $956,457,000 vs H1 2025 of $1,005,342,000 (EDGAR companyfacts, 10-Q YTD facts) — flat-to-down.

Balance sheet: net debt $598.0M on the engine's TOTAL:LongTermDebt basis (debt $2,329,201,000 vs cash $1,731,181,000 at Dec 31, 2025 per the 10-K balance sheet); net debt / normalized OE 0.47x. Leverage is not the risk here — the $22,302,345,000 reserve for claims and claim expenses (Dec 31, 2025, 10-K) is: it is an estimate, and its development is the earnings story in both directions.

## Overrides

**capex_override of $0, kind "filing"** (full source and reconciliation in judgment.json / key_numbers.md): DATA_GAP:capex blocked scoring — the FY2025 10-K Consolidated Statements of Cash Flows (p. F-8) contain no purchases-of-property-and-equipment line for FY2025, FY2024 or FY2023, the balance sheet carries no property-and-equipment line, and the statement reconciles exactly without one in all three years (e.g. FY2025: $3,693,107 − $2,215,809 − $1,410,503 − $12,218 = reported $54,577 thousand net increase in cash). Measured impact on the payable-earnings base actually used (key_numbers.md): base OE/share $27.21 without the override → $27.21 with it (+0.00%), weighted IRR 10.72% → 10.72% (+0.00pp) — the override converts the engine's silent assumed-zero history into a sourced, registered decision; it does not change any OE figure. Unblocks tier: YES — without it the filing gap blocks scoring entirely.

**base_override, basis `payable_earnings_5y`, kind "filing"** — the base construction above ($27.2074/share from five Q4-release figures; sources in judgment.json). Registry-measured impact: base $77.7834 / S by numbers → $27.2074 / C (weighted IRR 25.52% → 10.72% on the same-configuration replay). This is a base *definition*, not a tier adjustment: no tier_override is declared, and none is applied on top of a payable base.

## Moat: 5/10 — moderate / narrow

CAP = 8.5 years (2 + 1.3 × 5). Evidence first: `roic_proxy` and gross margin are not computable for this filer — fundamentals.json carries no operating-income or COGS series for an insurer — so the substitute evidence is return on equity from the filing figures: attributable net income / year-end equity of $2,561,132,000 / $9,454,958,000 (2023), $1,870,360,000 / $10,574,012,000 (2024) and $2,682,334,000 / $11,608,657,000 (2025) in the hard-market years, against losses in 2021 and 2022. That is a franchise that earns well above its cost of capital at the top of the cycle and below it at the bottom — the signature of a narrow moat, not a wide one.

FOR:
- Leading global property-catastrophe reinsurance franchise — 72.8% combined ratio in Q2 2026, book value per share +24.8% YoY to $264.77.
- Capital Partners third-party capital platform: >$9B of partner/ILS capital at Dec 31, 2025 and $328.9M of FY2025 fee income — capacity and fees peers cannot easily replicate.
- Validus Re acquisition (closed Nov 1, 2023) added treaty scale and diversification into casualty & specialty.
- Disciplined cycle management — gross premiums written down 12.5% YoY in Q2 2026 into softening prices, more retrocession bought instead of chasing share.
- Aggressive, accretive buybacks: ~11.5M shares (~22% of the starting count) repurchased for ~$3B over the two years to Q2 2026.

AGAINST:
- Reinsurance capacity is close to a commodity — no network effects, low switching costs, price set by the cycle; property-cat pricing fell high-teens at mid-2026 renewals.
- Catastrophe earnings volatility: net losses in 2021 and 2022 (2022 attributable net loss $1,061,203,000) — a single severe cat year can erase several benign years of OE.
- Casualty & specialty is the weak leg: 103.3% combined ratio and an underwriting loss in Q2 2026, adverse prior-year development, social-inflation exposure.
- Reserve risk is the balance sheet: $22,302,345,000 of claim reserves at Dec 31, 2025 are estimates, and prior-year development swings earnings both ways.
- Third-party capital is rented, not owned — partner capital takes its share of the best underwriting economics ($935,409,000 of FY2025 net income attributable to redeemable noncontrolling interests) and can be returned at cycle turns.

## DCF — engine 5.5 final run (2026-10-19)

Final run: `dcf_engine.py RNR --moat 5 --probs 0.15,0.30,0.30,0.15,0.10 --offsets -0.33,-0.256,-0.226,-0.186,-0.11 --base-judgment` (OE multipliers default 0.75/0.90/1.00/1.10/1.25; terminal growth 2.50%).

**Growth sanity check (mandatory):** the engine's blended start of 25.59% (components, key_numbers.md: rev CAGR 5y 19.96%, rev CAGR 3y 36.41%, latest rev YoY 9.86%, OE/share CAGR 2y 41.39%) is a Validus artifact — every component straddles the Nov 2023 acquisition (see BASIS_BREAK_SUSPECT below) and none of it describes the current company, whose latest filed prints are FY2025 revenue +9.86% YoY and Q2 2026 gross premiums written −12.5% YoY in a softening market. The offsets above recalibrate the starts to **−7.4% / −0.0% / +3.0% / +7.0% / +14.6%**. The base start (+3.0%) sits *below* the FY2025 revenue print (+9.86%) for a written reason: 2026 prints have already turned negative (GPW −12% YoY; U.S. property-cat rates down high-teens at the 6/1/2026 renewals; the 1/1/2027 consensus is another −7.5% to −15%), and what per-share growth remains is carried mainly by buybacks (~5%/yr; diluted share count 51,339,000 in FY2024 → 46,483,000 in FY2025, financials_history.csv) net of a shrinking book, not by premium growth. Bull (+7.0%) assumes pricing stabilizes near current levels with buyback leverage intact; super bull (+14.6%) is the 10%-weight tail of a hard-market re-acceleration, still far below the engine blend. Super bear (−7.4% start, 0.75× OE) is a severe catastrophe year landing on a softening price environment. Bear weight was widened (super bear 15% / bear 30%) per OE_VOLATILE.

| Scenario | Prob | Growth start | OE mult | IV@15 | IRR |
|---|---|---|---|---|---|
| Super bear | 15% | -7.4% | 0.75 | $110.49 | 6.04% |
| Bear | 30% | -0.0% | 0.9 | $180.82 | 8.83% |
| Base | 30% | 3.0% | 1.0 | $227.69 | 10.61% |
| Bull | 15% | 7.0% | 1.1 | $295.68 | 13.09% |
| Super bull | 10% | 14.6% | 1.25 | $459.09 | 18.35% |
| **Weighted** | | | | **$229.39** | **10.72%** |

Weighted IV @12% $303.35, @10% $385.72; upside at 15% -34.7% vs the $351.53 price (@12% -13.7%). Hurdle-clearing prices on the weighted path: 15% at $229.39, 20% at $162.72, 25% at $125.87. Diagnostics: OE yield 7.74%, TV share @15% 18.3%, scenario spread (IV@15) 4.16x, net debt / normalized OE 0.47x, IRR band bear 8.83% (tier D) → bull 13.09% (tier C); scenario range 6.04% – 18.35%.

## Flags — every fragility flag resolved

- **STALE_FY** — latest FY ended Dec 31, 2025 (9.6 months since FY end, key_numbers.md). ttm.py cannot build a TTM pin (SBC is tagged only annually in this filer's companyfacts — no post-FY YTD SBC fact exists), and the payable base is by construction a five-year average ending FY2025, so no TTM base applies; the filed H1 2026 legs (OCF $1,539,924,000 vs $1,627,334,000 H1 2025; attributable NI $956,457,000 vs $1,005,342,000) show flat-to-down, supporting no uplift. Q2 2026 (10-Q filed Jul 23, 2026) confirms the franchise is performing (CR 72.8%, operating ROE 20.1%) but shrinking premiums into the soft market.
- **BASIS_BREAK_SUSPECT** — the break is the **Validus Re acquisition from AIG, closed November 1, 2023** (~$3.3B consideration; $2,433,746,000 net cash purchase in FY2023 investing activities): revenue stepped from $5,060,412,000 (2022) to $9,134,608,000 (2023) to $11,695,148,000 (2024) as the acquired treaty book earned in. No growth input straddling that break is trusted — the scenario starts were recalibrated to post-acquisition prints only (FY2025 YoY, Q2 2026), as documented in the sanity check above.
- **OE_VOLATILE** — OE/share spans $25.33 (2021) to $79.73 (2024) over the last five years on the OCF basis, and the payable measure's own five figures span $81,599,000 to $2,234,426,000. The five-year average is the normalization chosen for exactly this volatility; bear-side probability was widened to 45% combined (15/30) in response. Volatility is priced, not removed — confidence stays low.
- **NI_OCF_DIVERGENCE** — not a one-off: it is float mechanics. FY2024 consolidated net income of $2,960,532,000 vs OCF of $4,164,822,000 (10-K, p. F-8) is bridged mainly by the $816,622,000 increase in claim reserves and the $862,896,000 decrease in reinsurance recoverable as the Validus book earned in, partly offset by a $381,830,000 decrease in reinsurance balances payable. Against *attributable* net income ($1,870,360,000) the gap is larger still, because $1,090,172,000 of FY2024 net income belonged to redeemable noncontrolling interests while OCF is consolidated. Structural and recurring — and now handled at the root: the payable-earnings base is built from operating income *available to common*, which excludes both the reserve build and NCI cash, instead of adjusting the tier after the fact.
- **SECTOR_MODEL_MISMATCH** — Finance/reinsurance: the OE/capex DCF fits insurers poorly (no capex, float-driven OCF, reserve-estimate balance sheet). The response under the 2026-10-19 rule is the payable-earnings base above, not a tier adjustment. Confidence graded **low**; the name lists under sector misfits and its alerts are suppressed (score.json: alert_eligible false; exit gate — "sector model misfit; tier exists only because of a judgment override").
- **OVERRIDE_APPLIED:capex** — see the overrides section; measured impact on the base and the weighted IRR is exactly zero, and the override unblocks the tier.
- **WIDE_SCENARIO_SPREAD** — super-bull IV@15 is 4.16x super-bear IV@15. Cat-cycle outcomes genuinely span that range; confidence is low, never high, on this name.
- **TIER_BAND** — bear tier D (8.83%) vs bull tier C (13.09%): the verdict spans tiers; size any position to the bear end (D economics — bear IV@15 $180.82).

## My thoughts / overlay

The method change is the story, and it reverses the conclusion. The old record compounded a float-and-NCI-inflated OCF base and then negotiated the tier down one notch; the payable base asks the simpler question — what did common shareholders actually earn, averaged across a full cat cycle that includes two loss years? — and the answer ($27.2074/share) supports $229.39 at a 15% hurdle and $303.35 at 12%, against a $351.53 price. The market is paying ~1.3x a book value ($264.77/share at Q2 2026) that has been compounding at hard-market speed; the five-year payable average says through-cycle earnings power does not carry that price at a 15% required return, and the forward prints argue the cycle is moving against it (GPW −12% YoY, property-cat rates down high-teens at 6/1, 1/1/2027 consensus −7.5% to −15%). What would change the answer: buybacks continuing at ~5%/yr shrink the denominator faster than the book shrinks (already in the base start, not in the base itself), or a hard-market re-acceleration (the 10%-weight super bull). RenRe remains arguably the best-run property-cat franchise in the sweep's insurance cohort and the Capital Partners fee stream ($328.9M in FY2025) is a genuine second engine — but on payable earnings this is a quality cyclical priced for the top of its cycle, and the conservative anchor is the bear end: bear IV@15 $180.82, super-bear $110.49.

## Final verdict

**Tier C, confidence low** — the numbers tier on the payable-earnings base; no tier override, no softening. Weighted IRR 10.72%, weighted IV@15% $229.39 vs price $351.53 (-34.7%). The name clears the 15% hurdle only at a price of ~$229.39 or below (~$303.35 at a 12% hurdle). TIER_BAND spans D (bear) to C (bull), so size any position to the bear end. Alerts suppressed by design (sector misfit; the tier exists only because judgment overrides unblock it); Andrew gets this in the daily ranking.
