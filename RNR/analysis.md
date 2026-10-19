# RNR — RenaissanceRe Holdings Ltd.

Finance / Property & Casualty Reinsurance · Price $351.06 · Market cap (est) $16.318B · Engine 5.4.0, 2026-10-17
**Final tier: A (agent override of S) · confidence low · weighted IRR 27.31% · weighted IV@15% $720.19**

## What it is

Bermuda-based global reinsurer founded in 1993 after Hurricane Andrew. Two underwriting segments — Property (led by property catastrophe) and Casualty & Specialty — plus RenaissanceRe Capital Partners, which manages third-party capital through joint ventures and ILS funds (DaVinci, Vermeer, Fontana, Medici, Upsilon). Management frames the business as three drivers of profit: underwriting, fee income, and net investment income. On November 1, 2023 it closed the acquisition of Validus Re from AIG (treaty reinsurance, the AlphaCat ILS manager, and Talbot treaty renewal rights) for total consideration of about $3.3B; the FY2023 10-K cash-flow statement shows a net Validus purchase outflow of $2,433,746,000 in investing activities plus $285,168,000 of non-cash consideration.

Current form is strong but the cycle is turning: Q2 2026 combined ratio 72.8%, operating income available to common shareholders $547.8M, annualized operating ROE 20.1%, book value per common share $264.77 (+24.8% YoY), fee income $83.0M, net investment income $432.5M — while gross premiums written fell 12.5% YoY as U.S. property-catastrophe rates dropped high-teens at the mid-year renewals and the company bought more retrocession rather than chase softening prices. Casualty & Specialty is the weak leg: a 103.3% combined ratio and an underwriting loss in Q2 2026, with $58.0M of adverse prior-year development in the quarter. Capital return is aggressive: $350.0M repurchased in Q2 2026, ~11.5M shares (~22% of the starting count) for ~$3B over the two years to Q2 2026.

## Owner's earnings

Conservative OE = OCF − capex − SBC; maintenance OE = NI + D&A − min(capex, D&A) − ΔNWC (engine definitions). Filed history (financials_history.csv):

| FY | Revenue | Net income (attrib.) | OCF | SBC | OE/share (conservative) |
|---|---|---|---|---|---|
| 2021 | $5,277,709,000 | -$40,155,000 | $1,234,815,000 | $40,000,000 | $25.33 |
| 2022 | $5,060,412,000 | -$1,061,203,000 | $1,603,683,000 | $45,200,000 | $36.21 |
| 2023 | $9,134,608,000 | $2,561,132,000 | $1,911,634,000 | $60,300,000 | $38.89 |
| 2024 | $11,695,148,000 | $1,870,360,000 | $4,164,822,000 | $71,400,000 | $79.73 |
| 2025 | $12,848,074,000 | $2,682,334,000 | $3,693,107,000 | $77,500,000 | $77.78 |

Base used: **$77.78/share — median of the last 3 FY OE/share** (base_source: median_of_last_3_fy_oe_per_share), which here equals the latest FY figure; latest-FY OE total $3.616B on 46,483,000 diluted shares. OE-positive years 5/5 over the last five.

Two honesty limits on that base, both structural for a reinsurer:

1. **The base capitalizes float and other people's capital.** FY2025 OCF of $3,693,107,000 is consolidated: it includes a $998,854,000 increase in the reserve for claims and claim expenses (premiums collected, claims not yet paid) and the cash earnings of the Capital Partners vehicles, of which $935,409,000 of FY2025 net income is attributable to redeemable noncontrolling interests, not to RNR common shareholders (both FY2025 10-K). The same filing's diluted EPS available to common shareholders is $56.03 — the $77.78 OE/share base sits well above what common shareholders actually earned per share.
2. **The median window is three benign-cat hard-market years.** 2023–2025 had no franchise-breaking catastrophe year; 2021–2022 printed attributable net losses (-$40,155,000 and -$1,061,203,000) while OCF-based OE/share stayed positive ($25.33 / $36.21) precisely because OCF does not charge for reserve inadequacy the way earnings eventually do. OE/share range over the last 5 years spans >3x (OE_VOLATILE).

TTM: `ttm.py` refuses for RNR — ShareBasedCompensation is tagged only annually in this filer's companyfacts (the only SBC fact is the FY2025 full-year figure), so there is no post-FY YTD SBC fact to build a TTM OE pin from, and no --ttm base was used. The filed H1 legs that do exist argue against any TTM uplift anyway: H1 2026 OCF of $1,539,924,000 vs H1 2025 OCF of $1,627,334,000, and H1 2026 net income (attributable) of $956,457,000 vs H1 2025 of $1,005,342,000 (EDGAR companyfacts, 10-Q YTD facts) — flat-to-down, so the median base stands unadjusted.

Balance sheet: net debt $598.0M on the engine's TOTAL:LongTermDebt basis (debt $2,329,201,000 vs cash $1,731,181,000 at Dec 31, 2025 per the 10-K balance sheet); net debt / normalized OE 0.17x. Leverage is not the risk here — the $22,302,345,000 reserve for claims and claim expenses (Dec 31, 2025, 10-K) is: it is an estimate, and its development is the earnings story in both directions.

## OVERRIDE — capex

DATA_GAP:capex blocked the preliminary run (no capex tag filed in any year). Resolved with a **capex_override of $0, kind "filing"** (full source and reconciliation in judgment.json / key_numbers.md): the FY2025 10-K Consolidated Statements of Cash Flows (p. F-8) contain no purchases-of-property-and-equipment line for FY2025, FY2024 or FY2023, the balance sheet carries no property-and-equipment line, and the statement reconciles exactly without one in all three years (e.g. FY2025: $3,693,107 − $2,215,809 − $1,410,503 − $12,218 = reported $54,577 thousand net increase in cash). Measured impact is zero by construction: base OE/share $77.78 with and without the override, weighted IRR 27.31% both ways (key_numbers.md) — the override converts the engine's silent assumed-zero history into a sourced, registered decision; it does not change any OE figure. The alert gate still records "tier exists only because of a judgment override" because without it the DATA_GAP blocks scoring entirely.

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

## DCF — engine 5.4 final run (2026-10-17)

Final run: `dcf_engine.py RNR --moat 5 --probs 0.15,0.30,0.30,0.15,0.10 --offsets -0.33,-0.24,-0.20,-0.15,-0.09` (OE multipliers default 0.75/0.90/1.00/1.10/1.25; terminal growth 2.50%).

**Growth sanity check (mandatory):** the engine's blended start of 25.59% (rev CAGR 5y 19.96%, rev CAGR 3y 36.41%, latest rev YoY 9.86%, OE/share CAGR 2y 41.39%) is a Validus artifact — every component straddles the Nov 2023 acquisition (see BASIS_BREAK_SUSPECT below) and none of it describes the current company, whose latest filed prints are FY2025 revenue +9.86% YoY and Q2 2026 gross premiums written −12.5% YoY in a softening market. The offsets above recalibrate the starts to **−7.4% / +1.6% / +5.6% / +10.6% / +16.6%**. The base start (+5.6%) sits *below* the FY2025 revenue print (+9.86%) for a written reason: 2026 prints have already turned negative, and what per-share growth remains is carried mainly by buybacks (diluted share count 51,339,000 in FY2024 → 46,483,000 in FY2025, financials_history.csv), not by premium growth. Bull (+10.6%) roughly matches the FY2025 print with pricing stabilized; super bull (+16.6%) is the 10%-weight tail of a hard-market re-acceleration plus buyback leverage, still far below the engine blend. Super bear (−7.4% start, 0.75× OE) is a severe catastrophe year landing on a softening price environment. Bear weight was widened (super bear 15% / bear 30%) per OE_VOLATILE.

| Scenario | Prob | Growth start | OE mult | IV@15 | IRR |
|---|---|---|---|---|---|
| Super bear | 15% | -7.4% | 0.75 | $315.88 | 13.60% |
| Bear | 30% | 1.6% | 0.9 | $552.66 | 22.27% |
| Base | 30% | 5.6% | 1.0 | $725.19 | 27.68% |
| Bull | 15% | 10.6% | 1.1 | $980.58 | 34.46% |
| Super bull | 10% | 16.6% | 1.25 | $1,423.72 | 44.16% |
| **Weighted** | | | | **$720.19** | **27.31%** |

Weighted IV @12% $958.22, @10% $1,223.92; upside at 15% +105.1% vs the $351.06 price. Hurdle-clearing prices on the weighted path: 15% at $720.19, 20% at $506.52, 25% at $389.07. Diagnostics: OE yield 22.16%, TV share @15% 18.9%, scenario spread (IV@15) 4.51x, IRR band bear 22.27% (tier A) → bull 34.46% (tier S).

## Flags — every fragility flag resolved

- **DATA_GAP:capex** — resolved by the $0 filing override above; the filer reports no capex line in any year and its cash-flow statements reconcile exactly without one (10-K pp. F-5/F-8).
- **STALE_FY** — latest FY ended Dec 31, 2025, ~10 months ago. ttm.py cannot build a TTM pin (SBC is tagged only annually in this filer's companyfacts — no post-FY YTD SBC fact exists), so the median base is used and the filed H1 2026 legs (OCF $1,539,924,000 vs $1,627,334,000 H1 2025; attributable NI $956,457,000 vs $1,005,342,000) show flat-to-down, supporting no uplift. Q2 2026 (10-Q filed Jul 23, 2026) confirms the franchise is performing (CR 72.8%, operating ROE 20.1%) but shrinking premiums into the soft market.
- **BASIS_BREAK_SUSPECT** — the break is the **Validus Re acquisition from AIG, closed November 1, 2023** (~$3.3B consideration; $2,433,746,000 net cash purchase in FY2023 investing activities): revenue stepped from $5,060,412,000 (2022) to $9,134,608,000 (2023) to $11,695,148,000 (2024) as the acquired treaty book earned in. No growth input straddling that break is trusted — the scenario starts were recalibrated to post-acquisition prints only (FY2025 YoY, Q2 2026), as documented in the sanity check above.
- **OE_VOLATILE** — OE/share spans $25.33 (2021) to $79.73 (2024) over the last five years. The median base dampens but cannot remove cat-cycle volatility; bear-side probability was widened to 45% combined (15/30) in response.
- **NI_OCF_DIVERGENCE (2024)** — not a one-off: it is float mechanics. FY2024 consolidated net income of $2,960,532,000 vs OCF of $4,164,822,000 (10-K, p. F-8) is bridged mainly by the $816,622,000 increase in claim reserves and the $862,896,000 decrease in reinsurance recoverable as the Validus book earned in, partly offset by a $381,830,000 decrease in reinsurance balances payable. Against *attributable* net income ($1,870,360,000) the gap is larger still, because $1,090,172,000 of FY2024 net income belonged to redeemable noncontrolling interests while OCF is consolidated. Structural, recurring, and the core reason the OE base overstates common-share economics — handled by the tier softening, not by adjusting the base.
- **SECTOR_MODEL_MISMATCH** — Finance/reinsurance: the OE/capex DCF fits insurers poorly (no capex, float-driven OCF, reserve-estimate balance sheet). Confidence graded **low**; the name lists under sector misfits and its alert is suppressed (score.json: alert_eligible false — "sector model misfit; tier exists only because of a judgment override").
- **OVERRIDE_APPLIED:capex** — see the override section; measured impact on the base and the weighted IRR is exactly zero.
- **WIDE_SCENARIO_SPREAD** — super-bull IV@15 is 4.51x super-bear IV@15. Cat-cycle outcomes genuinely span that range; confidence is low, never high, on this name.
- **TIER_BAND** — bear tier A (22.27%) vs bull tier S (34.46%): the verdict spans tiers, and the final tier is sized to the bear end (A).

## My thoughts / overlay

The method range is the honest headline. On engine numbers this is a Tier S screen print (weighted IRR 27.31%, IV@15% $720.19 vs $351.06) — but the base it compounds is a benign-window, float-and-NCI-inflated OCF figure: charge the base down to the filing's own diluted EPS available to common ($56.03 vs $77.78) and the same machinery would print something far closer to book-value compounding. The cross-check that matters for a reinsurer is book value: BVPS $264.77 at Q2 2026, +24.8% YoY, with a $351.06 price — the market is paying ~1.3x a book that has been compounding at hard-market speed and will not compound that fast through a soft market plus a normal cat year. RenRe is arguably the best-run property-cat franchise in the sweep's insurance cohort and the Capital Partners fee stream ($328.9M in FY2025) is a genuine second engine — that is what the A (softened) rather than a deeper cut reflects, alongside the bear-case tier itself printing A.

## Final verdict

**Tier A (final, softened one notch from Tier S by numbers), confidence low.** Weighted IRR 27.31%, weighted IV@15% $720.19 vs price $351.06; bear-case IV@15% $552.66 is the conservative anchor, and the super-bear IV@15% of $315.88 sits below the current price — a severe cat year on a softening market erases the apparent discount. On engine numbers the name clears the 15% hurdle at any price up to ~$720 (~$553 bear IV with a margin of safety), but those numbers capitalize float, so size any position to the bear end and treat the verdict as a high-quality cyclical at a reasonable price, not as a screened Tier S bargain. Alert suppressed by design (sector misfit + override-filled gap); Andrew gets this in the daily ranking.
