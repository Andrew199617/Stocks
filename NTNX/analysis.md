# NTNX — Nutanix, Inc.
v5 run, 2026-10-15. Market cap ~$20.4B at $69.98 (nasdaq_quote_api) — in scope (<$40B). This run carries a declared `base_override` that corrects a filer share-count unit error — see OVERRIDE.

All figures below are copied from key_numbers.md, dcf_numbers.json, financials_history.csv, or this run's EDGAR companyfacts pull — none are recomputed, except the unit correction in OVERRIDE, whose full construction is quoted there.

## What it is
Hybrid-multicloud infrastructure software: the Nutanix Cloud Platform (AHV hypervisor, storage, cloud management) sold as subscriptions to 27,000+ enterprise customers. FY2026 (ended 2026-07-31): revenue $2,853,545,000 (+12.4% YoY), ARR $2.55B (+16% YoY), net dollar-based retention 106%. FY2027 guidance: revenue $3.18–3.23B, free cash flow $850–950M. The demand story is VMware displacement after Broadcom's pricing changes, plus external-storage partnerships (Dell PowerStore, Pure, NetApp) and AI-infrastructure positioning.

## Owner's earnings
**FY2026 (10-K via EDGAR, from financials_history.csv):** operating cash flow $916,688,000; capex $76,013,000; SBC $357,667,000 (always a real cost — and here it is the single largest cost line in the OE bridge, ~39% of OCF).
- **Conservative owner's earnings FY2026: $483,008,000 = $1.65/share** (latest-FY OE/share, unit-corrected — see OVERRIDE).
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $1,345,849,000 — NOT comparable this year: FY2026 net income of $1,506,837,000 contains a ~$1.21B non-cash deferred-tax valuation-allowance release (the CSV tax line is −$1,179,729,000; the balance sheet now carries a $1,215,823 thousand deferred tax asset). The OCF-based conservative figure is the clean one; the maintenance figure is a tax artifact.
- OE positive 3 of the last 5 fiscal years (FY2024 $263,846,000; FY2025 $398,583,000; FY2026 $483,008,000) — a recent, still-ramping cash generator, not a long-compounding one.
- Balance sheet: the engine's debt tags came back null (net_debt_latest: null in dcf_numbers.json), so no net-debt figure is computed. The FY2026 10-K balance sheet (in thousands, as filed) shows cash $777,308, short-term investments $1,584,155, and convertible senior notes $1,348,711 — liquid assets comfortably cover the converts; deferred revenue ($1,246,575 current + $1,176,794 non-current, in thousands) is subscription float that supports OCF.

**Base used = the engine's normalized base (median of last 3 FY OE/share), unit-corrected: $1.3553/share** (base_source: agent_supplied_ttm_override via the declared base_override below). No STALE_FY flag (FY ended 2.5 months ago), so no TTM pin was needed. The median sits below the latest FY ($1.65) because FY2024 OE was still ramping — that conservatism is accepted: even the latest-FY base is only ~22% above the median, and the verdict (below) does not change on either base.

## OVERRIDE — base_override (share-count unit correction)
- **The error:** Nutanix presents weighted-average shares **in thousands** in its financial statements, and its XBRL facts carry that scale: companyfacts shows FY2026 diluted shares of 292,183 — i.e. 292,183 thousand. The engine read them as units, producing a normalized base of $1,355.34/share against a $69.98 price, a fake Tier S with IRR capped at the 200% solver limit. Proof inside this run's own outputs: financials_history.csv carries FY2017–19 diluted shares in full units (188,595,000 for FY2019) and FY2020 onward in thousands (194,719 for FY2020) — a scale break in the same series; the FY2026 8-K/10-K reconciliation prints basic shares 268,691 and diluted 292,183 (in thousands) with diluted EPS of $5.17 on net income of $1,506,837 thousand, and the 10-K cover reports 270,570,179 shares outstanding in units.
- **Why not a shares_override:** the override mechanism fills only periods where a tag is *absent*; it never replaces a filed value. These values are filed — at the wrong scale for the engine — so the bounded route is a base_override built exclusively from this run's code outputs.
- **Construction (quoted in full):** base_override = base_oe_normalized_per_share from this run's dcf_numbers.json ($1,355.341859271022) ÷ 1,000 = **$1.355341859271022/share**. Every OE total leg (OCF, capex, SBC) is in dollars as filed; only the share denominator carried the thousands scale, and all three median years (FY2024–26) carry it uniformly, so the single ÷1,000 corrects the median exactly. Cross-check: the corrected latest-FY figure is $1.6531/share on OE of $483,008,000 — consistent with 292,183 thousand diluted shares.
- **Measured impact:** without the correction the run is a fake Tier S at the 200% IRR cap; with it, Tier D at 5.71% weighted IRR. This override does not unblock a data gap (data_gap is empty) — it corrects a unit error, it is registered in overrides_registry.json, and it is the judgment call to review hardest in this folder.
- **Second filer data error found (no override taken):** the FY2026 10-K's comparative tagging puts net income of $1,506,837,000 on the period ending 2023-07-31 as well as on FY2026 (verified in this run's companyfacts pull: the FY2023 10-K filed −$254,560,000 for that period). financials_history.csv therefore shows FY2023 net income as $1,506,837,000. This corrupts only the maintenance OE definition and the divergence diagnostics for FY2023 — the OCF-based conservative base is untouched — so it is documented here rather than overridden.

## Moat: 5/10 — moderate / narrow
Justification: a genuine platform position in enterprise hybrid-cloud infrastructure with real switching costs and software-like gross margins, but expansion is modest (NDB 106%), the largest competitors bundle the same layer for free or cheap, and Nutanix owns no distribution channel of its own.
- FOR: Gartner Leader in distributed hybrid infrastructure; platform embedded in enterprise data centers — migrating hypervisor + storage + management plane is a multi-quarter project (real switching friction)
- FOR: Subscription model with $2.55B ARR (+16%) and 86–88% gross margins — pricing power evidenced by margin expansion while scaling
- FOR: Broadcom/VMware disruption is pushing customers to qualify an alternative, and Nutanix is the default independent candidate; OEM/external-storage partnerships (Dell, Pure, NetApp, Lenovo) widen reach without owning hardware
- AGAINST: Net dollar-based retention only 106% — customers are not expanding spend the way wide-moat platforms' customers do
- AGAINST: Broadcom (VMware), Microsoft, AWS and HPE all compete for the same layer with bundle economics Nutanix cannot match; the moat is "best independent alternative," not a lock
- AGAINST: SBC of $357,667,000 in FY2026 (~39% of OCF) — a comp culture that taxes owners every year and keeps basic share count climbing
- AGAINST: Guided FY2027 headwinds are operational, not theoretical — server supply constraints and elevated hardware prices delaying customer projects, plus a ~5% workforce restructuring
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-15)
Growth sanity check: the engine's blend is 15.34% (rev CAGR 5y 15.40%, 3y 15.27%, latest YoY 12.44%, OE/share CAGR 2y 23.85%), adjusted −5pp for the share-count trend to g_base 10.34%. That base start sits right on the evidence: FY2026 revenue +12.4%, FY2027 guided revenue growth ~+12–13%, ARR +16%. Scenario starts (default offsets −12/−5/0/+5/+12pp): −1.7 / 5.3 / **10.3** / 15.3 / 22.3%. The super-bull start of 22.3% is above any current print — it is a 10%-probability tail (VMware displacement accelerates ARR well past +16% while FCF margin expands), not a forecast; all other starts are at or below recent prints. Probabilities default 10/25/30/25/10; OE multipliers default 0.75/0.90/1.00/1.10/1.25. Price $69.98.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | −1.7% | 0.75 | VMware stabilizes, hyperscalers bundle Nutanix out; OE contracts | $7.00 | 3.68% |
| Bear | 25% | 5.3% | 0.90 | Growth decays to mid-single digits; SBC stays heavy | $11.25 | 4.57% |
| Base | 30% | 10.3% | 1.00 | Guidance-like ~12% revenue growth decaying over the CAP | $15.37 | 5.46% |
| Bull | 25% | 15.3% | 1.10 | ARR growth holds mid-teens on VMware displacement | $20.75 | 6.59% |
| Super bull | 10% | 22.3% | 1.25 | Category-winner path: sustained 20%+ growth, FCF margin expands | $31.27 | 8.69% |

- **Probability-weighted: IV@15% $16.44 (−76.5% vs price), IV@12% $22.18, IV@10% $28.63, weighted IRR 5.71%, base-case IRR 5.46%**
- **Tier by numbers: D.** Diagnostics (dcf_numbers.json): OE yield 1.94%, terminal value 20.3% of IV@15%, scenario spread 4.46x, 2.5 months since FY end. Even the super-bull scenario (8.69% IRR, IV@15% $31.27) does not reach half the current price — the D is not a close call on any scenario.

## Flags — every fragility flag resolved
- **DILUTION** (share count growing 7.8%/yr): two parts. The diluted series jumps partly because convertible-note dilutive shares entered the count in FY2025 (26,604 thousand incremental contingently issuable shares in EDGAR for FY2025) — accounting dilution, not issuance. But the economic core is real: SBC ran $311,745,000 / $333,833,000 / $351,590,000 / $357,667,000 across FY2023–26 and basic shares rose from 233,247 thousand (FY2023) to 268,691 thousand (FY2026). SBC is deducted in full in the conservative OE, and the −5pp growth adjustment is already applied — the flag is honored, not waved off.
- **NI_OCF_DIVERGENCE** (2024, 2025, 2026): identified year by year. FY2024–25: net income near/below zero (−$124,775,000 in FY2024, +$188,366,000 in FY2025) against OCF of $672,931,000 / $821,456,000 — the gap is the non-cash SBC addback (~$334–352M/yr) plus deferred-revenue float. FY2026: net income of $1,506,837,000 *exceeds* OCF of $916,688,000 because of the ~$1.21B non-cash deferred-tax valuation-allowance release (tax line −$1,179,729,000). Neither direction touches the OCF-based base; the FY2026 maintenance-OE figure is the distorted one and is not used.
- **IRR_CAPPED** (preliminary run only): an artifact of the share-scale error — at a fake $1,355 base every scenario's IRR blew through the 200% cap. Resolved by the OVERRIDE unit correction; the final run's irr_capped is false and every scenario IRR is inside the solver's range.
- **LOW_OE_YIELD** (base OE yield 1.9%): real and decisive. At $69.98 the market is paying ~52x the normalized OE base; the valuation rests almost entirely on growth the fade does not grant a moat-5 company. This flag is the verdict, in one line.
- **WIDE_SCENARIO_SPREAD** (4.46x): real — outcomes range from platform decay to category winner. Confidence is held to low (below the medium cap the spread alone would impose) because the run also carries a declared base_override.

## My thoughts / overlay
- Quality is not the problem: +16% ARR growth, 29% FY2026 free-cash-flow margin on the company's own FCF definition, net liquid assets covering the converts, and a genuine industry tailwind from Broadcom's VMware pricing. The problem is purely the price: $69.98 capitalizes a super-bull decade at a moat-5 fade.
- Method range: narrow for once. Median base ($1.36) → D at 5.71%; latest-FY base ($1.65) lifts every IV by roughly a fifth and still lands nowhere near the price; super-bull scenario alone → 8.69%. Every defensible input set tiers D.
- What would change the answer: ARR growth re-accelerating above 20% for several years (making the super-bull the base case), or the price falling to the weighted IV@15% of **$16.44** — the level that clears Andrew's 15% hurdle on the weighted path. A margin-of-safety buy point sits below that, in the low teens.
- Watch items: FY2027 delivery against the $3.18–3.23B revenue guide under server-supply constraints; whether NDB climbs above 106%; SBC as a share of OCF (39% in FY2026 — any drift up directly cuts OE).

## Final verdict
- **Final tier: D** (weighted IRR 5.71% on the v5 final inputs; no tier override — the numbers and the overlay agree)
- Confidence: **Low** (wide scenario spread + a declared base_override carrying the run, even though the D conclusion is robust across bases and scenarios)
- One-liner: Quality hybrid-cloud platform, moat 5/10 — but at $69.98 the price pre-pays a super-bull decade: weighted IRR 5.7%, IV@15% $16.44; it clears 15% only below ~$16.
