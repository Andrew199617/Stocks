# VRSN — VeriSign, Inc.
v5 run, 2026-10-14. In scope (market cap $27.707B at $295.38, nasdaq_quote_api).

All figures below are copied from key_numbers.md, dcf_numbers.json, ttm.py output, or financials_history.csv — none are recomputed. Business facts are from the Q2 2026 earnings release and registry-contract reporting found in this run's web research, cited in words where used.

## What it is
The exclusive registry operator for .com and .net: every registrar (GoDaddy, Cloudflare, etc.) pays Verisign a wholesale fee for each .com/.net registration and renewal, and Verisign operates the DNS resolution infrastructure behind those TLDs (plus two of the 13 root servers). Q2 2026: combined .com/.net base 179.1 million names (+5.1% YoY), 12.7 million new registrations in the quarter, Q1 2026 final renewal rate 76.3%, revenue +6% YoY (per the Q2 2026 earnings release). It also guides the .web TLD launch later in 2026 — immaterial to this model.

## Owner's earnings
**FY2025 (10-K via EDGAR, from financials_history.csv):** operating cash flow $1,091,100,000; capex $22,800,000 (tag PaymentsToAcquirePropertyPlantAndEquipment); SBC $69,700,000 (always a real cost).
- **Conservative owner's earnings FY2025: $998,600,000 = $10.65/share** (key_numbers.md: latest FY OE total $998.6M, latest FY OE/share $10.65)
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $748,600,000 (financials_history.csv) — lower than the conservative figure mainly because it starts from net income rather than OCF; the OCF-based conservative series is the standard base here and is the one the engine models. The gap between the two definitions is a stated uncertainty, not hidden — it is one reason confidence is medium, and even the higher (conservative) definition produces the Tier D verdict below, so the choice does not drive the conclusion.
- OE positive 5 of the last 5 fiscal years (key_numbers.md). Revenue history is metronomic: FY2021 $1,327.6M → FY2025 $1,656.6M, rev CAGR 5y 5.54% / 3y 5.15%, latest rev YoY 6.37% (financials_history.csv / key_numbers.md).
- Balance sheet: key_numbers.md reports net debt as unavailable (the engine's debt tags returned no values for this filer, so no net-debt figure is quoted and none was hand-computed, per the hard rule). Qualitatively, book equity is negative (−$2,154.2M at FY2025, financials_history.csv) — an artifact of decades of buybacks against a capital-light registry, not a solvency signal against ~$1.1B of annual OCF; the Q2 2026 release reports the company issued $550M of 5.10% senior notes due 2031 and redeemed its $550M 2027 notes in July 2026. No balance-sheet adjustment was made to the verdict; the DCF is on per-share OE, which already nets interest through OCF.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,091,100,000 − prior YTD $493,800,000 + current YTD $504,000,000 = **TTM $1,101,300,000**
- Capex: FY $22,800,000 − prior YTD $13,600,000 + current YTD $26,000,000 = **TTM $35,200,000**
- SBC: FY $69,700,000 − prior YTD $33,400,000 + current YTD $38,500,000 = **TTM $74,800,000**
- Shares (current-YTD weighted diluted): **91,400,000**
- **TTM OE total $991,300,000 → base OE/share $10.85** (base_source: ttm_json)
- The engine's normalized base (3-yr median) is $8.28/share — rejected as the base: it is the FY2024 figure, and both FY2025 ($10.65) and the TTM ($10.85) sit above it because OCF stepped up in FY2025 and the share count keeps shrinking. The median is still reported in key_numbers.md. Note the honesty check in the other direction: TTM OE total ($991.3M) is essentially flat vs FY2025 ($998.6M) — the TTM per-share gain over FY2025 is buyback arithmetic, not OCF growth. That is priced into the recalibrated growth starts below.

## Moat: 9/10 — wide and durable, but granted not owned
Justification: exclusive ICANN registry rights for .com/.net with presumptive renewal, .com's default-TLD network status and registrant switching costs, contractual 7% pricing power repeatedly exercised, and ~68% operating margins on minimal capex. Scored 9 not 10 because the moat is granted by contract and politics — NTIA/antitrust pressure on .com pricing is a live, binary erosion force at each renewal.
- FOR: Exclusive .com/.net registry operator under ICANN agreements with presumptive renewal — no competitor can legally take the registry without a contract change; .com is the default commercial TLD: brand identity, email, and links are embedded in 179.1M registrations — switching costs are borne by registrants, not Verisign, and renewal rates run ~76% despite repeated price hikes; proven contractual pricing power: wholesale .com price taken from $7.85 to $10.26 since 2021, next +7% to $10.97 effective Nov 1, 2026, with up to three more 7% steps to 2030; .net allows up to 10%/yr; structural cost advantage: ~68% operating margins, capex of only $22.8M on $1,656.6M FY2025 revenue — registry scale economics no entrant can replicate; 29 years of 100% .com/.net DNS availability — operational record is itself a barrier to any re-bid argument.
- AGAINST: Moat is granted by ICANN/NTIA contracts, not owned — .com agreement runs to Nov 2030 and pricing terms are a political/antitrust target (NTIA publicly wanted lower .com prices at the 2024 renewal; antitrust suit filed over .com pricing); mature .com base — long-run volume growth depends on new-business formation; alternative TLDs (.ai, ccTLDs), brand TLDs from ICANN's 2026 round, and platform/social presence substitute at the margin; wholesale price hikes are capped (7% in only 4 of each 6 years for .com) and each hike risks registrar/registrant pushback and volume elasticity; single-product concentration — essentially all economics are .com/.net registry fees; a DNS security/availability failure would be existential for the contract.
- A 9 gives CAP = 13.7 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 13.7 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Growth recalibration (written reason): the engine's g_base is 10.54% — a 5.96% blend plus a 4.59pp share-count adjustment. The blend's median is honest on revenue (5-yr 5.54%, 3-yr 5.15%, latest YoY 6.37%) but the 21.33% OE/share CAGR 2y component reflects the FY2025 OCF step-up, and TTM OCF has since gone flat ($1,101.3M TTM vs $1,091.1M FY2025). A durable OE/share start of ~8.5% — guided revenue growth (~6% print in Q2 2026, .com price hikes resuming Nov 2026) plus buyback shrinkage — is the defensible base, so the base-scenario offset was set to −0.02 and the spread tightened for a utility-stable name (offsets −0.10 / −0.05 / −0.02 / 0.00 / +0.03). Sanity check against prints: bear start 5.5% ≈ the historical revenue CAGRs; base start 8.5% sits above Q2's EPS growth print on the strength of the contracted Nov 2026 price hike and continued buybacks — stated, not hidden; super-bull start 13.5% requires all four 7% .com hikes, sustained ~5% domain-base growth, and undiminished buybacks — a genuine bull story, not a recent print (FY2025's OE/share jump was the OCF step-up, which TTM shows has not repeated). Probabilities 10/20/40/20/10 — heavier base weight than default because this is one of the most predictable revenue streams in the market; OE multipliers default 0.75/0.90/1.00/1.10/1.25 (the 0.75 super-bear multiplier is where a pricing-regime loss lives). Price $295.38.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | 0.5% | 0.75 | Pricing regime cut at/before 2030 renewal; volume stalls | $60.31 | 4.94% |
| Bear | 20% | 5.5% | 0.90 | Domain growth reverts to mature ~2-3%; hikes partly offset by elasticity | $93.81 | 6.67% |
| Base | 40% | 8.5% | 1.00 | ~6% revenue growth + contracted hikes + buybacks, fading over 13.7-yr CAP | $122.11 | 8.08% |
| Bull | 20% | 10.5% | 1.10 | Domain-base growth holds near the guided 5-6%; all hikes taken cleanly | $149.41 | 9.34% |
| Super bull | 10% | 13.5% | 1.25 | Four 7% .com hikes compound on a growing base; buybacks accelerate | $199.41 | 11.47% |

- **Probability-weighted: IV@15% $123.46 (−58.2% vs price), IV@12% $167.56 (−43.3%), IV@10% $217.38, weighted IRR 8.16%, base-case IRR 8.08%**
- **Tier by numbers: D.** Diagnostics (key_numbers.md): OE yield 3.67%, terminal value 21.2% of IV@15%, scenario spread 3.31x, 9.4 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.4 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, quoted above with all four legs (OCF/capex/SBC/shares).
- **BUYBACK_TAILWIND** (share count −4.59%/yr): already credited via the +4.59pp growth adjustment in g_base; the recalibrated scenario starts were set with that credit in view (base start 8.5% includes expected buyback shrinkage) — not double-counted as a separate verdict boost.
- The preliminary run also carried WIDE_SCENARIO_SPREAD (4.46x on default ±12pp offsets); the final run's tightened, company-specific offsets bring the spread to 3.31x and the flag no longer fires. Confidence is still held at medium: the spread that remains is real (the super-bear case is a political event, not a forecast error), and no tier conclusion here depends on resolving it — even the super-bull IRR (11.47%) does not clear 15%.

## My thoughts / overlay
- This is a quality-vs-price result, not a quality debate. The business is arguably the cleanest toll road in the sweep so far: 5/5 OE-positive years, capex of $22.8M against $1,091.1M of OCF, SBC a modest $69.7M, and a contracted price-hike schedule. None of that is in dispute — and none of it clears Andrew's hurdle at $295.38.
- Method range: on the engine's normalized median base ($8.28/share) with default settings, the preliminary run gave weighted IRR 7.12% and IV@15% $101.33; on the TTM base with recalibrated growth, 8.16% / $123.46. Every defensible input set lands in Tier D — there is no C→A spread here, which is itself the finding. The market price ($295.38) sits above even this run's super-bull IV@15% ($199.41) and above the weighted IV@10% ($217.38): a buyer at $295 is paying for a discount rate well under 10% or for growth beyond the contracted pricing schedule.
- The one number that would change the verdict is price, not operations: the stock clears 15% at the weighted IV@15% of $123.46, and clears it with a margin of safety only below that. At ~$168 (the weighted IV@12%) it would clear 12%, still not the 15% hurdle.
- Live risks to monitor rather than model: the Nov 1, 2026 .com hike to $10.97 (first of up to four), the antitrust suit over .com pricing, NTIA posture into the 2030 renewal, and whether the 2026 domain-base growth spike (guided 5.2-6%) persists or reverts to mature low-single digits.

## Final verdict
- **Final tier: D** (weighted IRR 8.16% on the v5 final inputs; Tier D under every defensible base — median or TTM)
- Confidence: **Medium** (high on OE quality and the TTM base; the residual uncertainty is a binary regulatory event at the 2030 renewal that no scenario spread captures, and the two OE definitions diverge by a wide margin)
- One-liner: Elite wide-moat registry monopoly (9/10) with contractual pricing power — but at $295.38 the price assumes far more than the model gives: weighted IRR 8.16%, weighted IV@15% $123.46; it clears 15% only below ~$123.
