# GFI — Gold Fields Limited
v5 run, 2026-10-14. This supersedes the earlier 2026-10-14 escalation note in this folder: that run blocked because the engine then read only us-gaap and GFI's history ended in 2015. Engine v5.3 reads its ifrs-full filings, the history now runs FY2015–FY2024, and the run scores — with the staleness caveat below stated plainly.

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed. Figures marked "search-cited" are from company results reporting found in web search; they are narrative context only and were NOT used in the scoring, because they are not in this run's code outputs.

## What it is
South African gold miner (NYSE/JSE: GFI), 20-F filer reporting under IFRS in USD. Mines across Australia, South Africa, Ghana, Peru and Chile, plus the Windfall project in Canada. It sells a commodity at a price it does not set: attributable gold-equivalent production was 2.438 Moz in 2025 and 2026 guidance is 2.40–2.60 Moz (search-cited) — volume is essentially flat, so earnings growth is a gold-price story, not a volume story.

## Owner's earnings
**FY2024 (latest FY in the engine's history, from financials_history.csv):** revenue $5,201,600,000; net income $1,290,500,000; operating cash flow $1,607,000,000; capex $1,183,400,000; SBC $4,400,000 (immaterial — this is not an SBC story); diluted shares 895,503,589.
- **Conservative owner's earnings FY2024: $419,200,000 = $0.47/share** (key_numbers.md: latest FY OE/share $0.47; latest FY OE total $419.2M)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,290,500,000 — far above the conservative figure because total capex at a miner includes waste-stripping and project capital well above D&A. The conservative definition is the right base here: at a depleting mine, most capex is the cost of staying in business.
- OE positive 5 of the last 5 fiscal years (key_numbers.md). Net debt (latest, FY2024) $1.635B (key_numbers.md).
- **Base used = normalized base: median of last 3 FY OE/share = $0.34/share** (base_source: median_of_last_3_fy_oe_per_share). No TTM base was available — see STALE_FY below.

## Moat: 3/10 — weak
Justification: a gold miner is a pure price taker — no pricing power, no switching costs, no network effects. What it has is cost-curve position and asset life, which earn it a 3 rather than a 0-2.
- FOR: Cost-curve position at Salares Norte (low AISC, steady state reached 2025); Portfolio of long-life mines across five countries; Scale: ~2.4-2.6 Moz/yr attributable production guidance for 2026; Reserve replacement track record incl. Gold Road acquisition (2025)
- AGAINST: Pure commodity price taker — no pricing power; Reserves deplete; must be replaced via capex/exploration/M&A; Rising all-in sustaining costs (H1 2026 AISC +13% YoY per company reports); Jurisdictional risk — Tarkwa (Ghana) leases expire April 2027, renewal terms unresolved; Windfall project permitting delays
- A 3 gives CAP = 5.9 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 5.9 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Probabilities were skewed bear-ward from the 10/25/30/25/10 defaults to 15/30/25/20/10, per the OE_VOLATILE flag's instruction to widen bear weight on a cyclical. Offsets and multipliers are the defaults (−12/−5/0/+5/+12pp; 0.75/0.90/1.00/1.10/1.25). Price $35.59.

Growth sanity check (mandatory): the base start of 13.7% sits just under the latest engine-observed revenue print (latest rev YoY 15.57%, FY2024). The bull (18.6%) and super-bull (25.7%) starts sit BELOW the FY2025 revenue growth the company actually reported (+68%, search-cited) — written reason: that print is a gold-price step (realised price +45%, search-cited), not a repeatable growth rate. Production guidance is flat (2.40–2.60 Moz for 2026 vs 2.438 Moz in 2025, search-cited), and cost inflation runs the other way (H1 2026 AISC +13% YoY, search-cited). Compounding a one-year price spike for a decade would be the inflection-artifact error in reverse.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | 1.7% | 0.75 | Gold price retraces; OE compresses toward the low end of its 5-yr range | $2.02 | 3.21% |
| Bear | 30% | 8.6% | 0.90 | Gold flat-to-down, AISC inflation eats volume gains | $3.09 | 3.63% |
| Base | 25% | 13.7% | 1.00 | Engine blend decays over the 5.9-yr CAP | $4.07 | 4.04% |
| Bull | 20% | 18.6% | 1.10 | Gold holds highs; Salares Norte outperforms | $5.28 | 4.54% |
| Super bull | 10% | 25.7% | 1.25 | Gold supercycle persists; full operating leverage | $7.52 | 5.46% |

- **Probability-weighted: IV@15% $4.06 (−88.6% vs price), IV@12% $5.44, IV@10% $6.98, weighted IRR 4.04%, base-case IRR 4.04%**
- **Tier by numbers: D.** Diagnostics (key_numbers.md): OE yield 0.95%, terminal value 19.5% of IV@15%, scenario spread 3.72x, net debt 5.39x normalized OE, 21.4 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (latest FY ended 21.4 months ago): PARTIALLY RESOLVED, and it is the dominant caveat on this score. ttm.py was run and exited 3: "cannot compute TTM for GFI (CIK 1172724): ocf: no annual (FY) fact; sbc: no annual (FY) fact; shares_diluted: no annual (FY) fact; capex: no capex facts in companyfacts under any candidate tag" — ttm.py reads us-gaap facts only, GFI is an IFRS filer, so this failure is expected per the sweep spec; the engine's median base was used, as instructed. Separately, the engine's annual history ends at FY2024 even though the company has reported FY2025 results (revenue US$8,751m, profit attributable to owners US$3,567.4m, adjusted free cash flow US$2,970m — search-cited, 19 Feb 2026 release) and H1 2026 results (revenue US$5,936.9m, headline earnings US$1,855m, adjusted free cash flow US$2,225m — search-cited, 25 Aug 2026). Those reported figures are not in this run's code outputs, so under the hard rule they cannot be scored on. Consequence, stated plainly: the $0.34 base is a pre-gold-surge base, and the Tier D below is a verdict on that base at a $35.59 price that already capitalizes the surge — not a claim that the current business earns $0.34/share.
- **OE_VOLATILE** (OE/share range over last 5 yrs spans >3x): real and structural — OE is a leveraged function of the gold price. Handled by the normalized median base and by skewing probabilities bear-ward (45% on bear-or-worse).
- **ADS_RATIO_APPLIED**: resolved under bounded authority (step 8d). judgment.json declares ads_ratio {ratio: 1.0, source: "Gold Fields FY2025 Form 20-F cover (filed 30 March 2026, fiscal year ended 31 December 2025): the registered security is American Depositary Shares, each representing one ordinary share", reason: per-share figures are per ordinary share and the NYSE price is per ADS; at 1:1 no figure changes}. The engine applied it (×1.0) and make_score accepted it.
- **BASE_DIVERGENCE** (latest FY $0.47 vs 3-yr median $0.34): neither is a one-off distortion — the median is dragged by the weaker FY2022–23 years (lower realised gold price, Salares Norte still ramping), and FY2024 is simply a better price year. The median is retained deliberately: for a cyclical, normalizing through the cycle is the conservative choice, and the direction of the gap is disclosed rather than arbitraged.
- **LOW_OE_YIELD** (base OE yield 1.0%): stands on the engine base — at $35.59 the price capitalizes current gold-price earnings, not the normalized base. This is exactly why the tier is fragile in both directions and confidence is low.
- **HIGH_NET_DEBT** (net debt 5.39x normalized OE): true on engine (FY2024) figures — net debt $1.635B against a small normalized OE base. Context the engine cannot see: reported net debt fell to US$1,442m at end-2025 and to US$437m at H1 2026 (search-cited), because current OE is far above the normalized base. Leverage is not the binding risk at current gold prices; it becomes binding only in the super-bear case, which is weighted 15%.

## My thoughts / overlay
- The honest headline is the method limitation, not the D: the standardized engine scores GFI on a FY2022–24 median base while the market prices it on FY2025–26 gold-price earnings. A defensible method range cannot be computed in this run — building a current base would require figures outside this run's code outputs, which the bounded-authority rule forbids a worker from declaring. That escalation is the finding to carry forward: GFI (and IFRS miners generally) needs either FY2025 facts in companyfacts coverage or a main-agent base decision before its tier means anything.
- What the run does establish: on through-cycle normalized owner's earnings, $35.59 is nowhere near clearing 15% — the price that clears 15% on these inputs is the weighted IV@15% of $4.06, and a margin-of-safety entry would be below that. Anyone buying at $35.59 is buying the gold price, not normalized earnings power, and should size it as a commodity position.
- Quality overlay: flat guided production, rising AISC, an unresolved Tarkwa lease renewal (leases expire April 2027, search-cited) and Windfall permitting delays are the operational watch items; balance-sheet risk has receded sharply at current prices (search-cited net debt figures above).

## Final verdict
- **Final tier: D** (weighted IRR 4.04% on the v5 final inputs; no tier override — the numbers say D on the base the method allows, and the staleness caveat is carried in words, not by fudging the tier)
- Confidence: **Low** (stale FY2024-capped base on a name whose reported earnings have since multiplied on the gold price; scenario spread 3.72x)
- One-liner: Price-taking gold miner, moat 3/10 — does not clear 15% on the engine's FY2022-24 median base (weighted IRR 4.0%, IV@15 $4.06 vs $35.59 price; clears 15% only below ~$4.06). That base predates the FY2025 gold-price surge in the engine's data, so this D is a stale-base result, not a read on current earnings power.
