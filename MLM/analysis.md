# MLM — Martin Marietta Materials, Inc.
v5 run, 2026-10-14 (supersedes the v4 analysis of 2026-10-13; same conclusion, re-verified under the v5 data gate). Price $472.39 (nasdaq_quote_api), market cap $28.63B — in scope (<$40B).

All figures below are copied from dcf_numbers.json, ttm.py output (ttm.json), or financials_history.csv — none are recomputed.

## What it is
One of the two largest US aggregates producers (crushed stone, sand and gravel quarries across the East and West groups), plus asphalt/paving, ready-mixed concrete remnants being exited, and a Magnesia Specialties segment. The model business is local quarries: aggregates are heavy and cheap per ton, so transport cost confines each quarry to a ~30–50 mile market, and permitted reserves are scarce. Portfolio is rotating to pure aggregates: South Texas cement sold to CRH in Feb 2024 for $2.1B; the QUIKRETE asset exchange closed in 2026 (Midlothian cement + Texas ready-mix out; aggregates assets in VA/MO/KS/Vancouver + $450M cash in); Premier Magnesia acquired Jul 2025; New Frontier Materials acquired; and in Aug 2026 the company agreed to acquire Lhoist North America (lime) for $13.5B — pending per Q2 2026 10-Q reporting and subsequent 8-Ks (one secondary source claims an Aug 21, 2026 closing; the filing-based record describes it as pending, and the FY2025 balance sheet used here predates it either way). Q2 2026: record revenue $1,947M (+21%, largely acquired volume), gross profit flat at $495M, earnings from operations −10%, continuing diluted EPS $4.26 (−12%; adjusted $5.00, +3%); aggregates shipments 61.6M tons (+17%), organic shipments +2.3%, headline ASP −2% on mix, mix-adjusted organic pricing +3.7%. Management raised FY2026 revenue guidance to $7.2–7.4B and reaffirmed adjusted EBITDA guidance of $2.36–2.5B; SOAR 2030 efficiency program targets ~$350M of run-rate pre-tax cash flow benefits.

## Owner's earnings
SEC EDGAR filing-direct history (conservative = OCF − capex − SBC; SBC is small, $46M in FY2025, tag ShareBasedCompensation; capex tag PaymentsToAcquirePropertyPlantAndEquipment):
- FY2023: OCF $1,528M − capex $650M − SBC $50M = $828M = $13.33/sh
- FY2024: OCF $1,459M − capex $855M − SBC $58M = $546M = $8.86/sh
- FY2025: OCF $1,785M − capex $807M − SBC $46M = $932M = $15.38/sh (latest FY OE/share in dcf_numbers.json)
- 3-yr median (engine normalized base): $13.33/sh. OE positive 5/5 of the last 5 years, but lumpy — a cyclical, capex-heavy quarry business, not a compounder glide path. Net debt $5,256M at FY2025.
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC) is NOT usable here: it prints $2,970M for FY2024 and −$222M for FY2025. Two distortions explain it: FY2024 net income ($1,995M) contains the pretax gain on the South Texas cement divestiture, and the ΔNWC line swings −$975M / +$1,359M across 2024–25 on held-for-sale reclassifications for the QUIKRETE exchange (both from financials_history.csv). The OCF-based conservative definition is clean of both, so it is the base definition.

**Base used = TTM owner's earnings through Q2 2026, from ttm.py (filing-direct, no hand math):**
- OCF: FY $1,785M − prior YTD (H1 2025) $605M + current YTD (H1 2026) $339M = **TTM $1,519M**
- Capex: FY $807M − prior YTD $412M + current YTD $314M = **TTM $709M**
- SBC: FY $46M − prior YTD $37M + current YTD $41M = **TTM $50M**
- Shares (current-YTD weighted diluted): **60.3M**
- **TTM OE total $760M → base OE/share $12.60** (base_source: ttm_json)
- The TTM base sits below both the median ($13.33) and FY2025 ($15.38) because H1 2026 OCF ($339M) ran far below H1 2025 ($605M); the TTM formula is a full 12 months, so this is current reality, not seasonality, and using it is the conservative choice. Cross-check from the v4 pass: TTM net income is useless as a check — H1'26 net income includes the ~$1.4B after-tax gain on the Midlothian divestiture in discontinued operations; it never touches OCF, so the OE base is not flattered by it.

## Moat: 7/10 — strong, local, and real, but cyclical
Justification: permitted reserves near growing metros are genuinely scarce and effectively irreplaceable, transport economics make each deposit a local oligopoly, and pricing power is proven through cycles. The ceiling on the score is the product itself — an undifferentiated commodity whose moat is location and reserves, not brand, network, or switching costs — and volumes that are hostage to construction cycles, with growth increasingly bought via M&A.
- FOR: permitting scarcity — a new greenfield quarry takes years-to-decades of zoning/environmental approval; existing permitted reserves near growing metros are effectively irreplaceable; transport economics — aggregates lose competitiveness beyond ~30–50 truck miles, so each deposit is a local oligopoly, not a national commodity market; proven pricing power — FY2025 aggregates pricing +6.9% with volumes +3.8%, Q2 2026 mix-adjusted organic pricing +3.7%, a multi-year record of mid-to-high single-digit price increases through inflation and soft housing; demand floor — public infrastructure (highway/state DOT) is the largest end market and is funded multi-year, with data-center and power construction adding demand; Specialties (magnesia, and lime via Lhoist) adds niche, higher-margin, less-cyclical revenue.
- AGAINST: undifferentiated commodity product — no brand, network effects, or switching costs; a rival quarry inside the same radius competes on price; volumes hostage to construction cycles — residential weakness already shows, revenue CAGR only ~5.4% over 5 yrs and ~0% over 3 yrs on the restated continuing basis; reserves deplete and growth must be bought back via M&A at rising per-ton prices (Premier, New Frontier, now Lhoist at $13.5B); Q2 2026 showed pricing's near-term limit — revenue +21% to a record but gross profit flat, operating earnings −10%, aggregates gross profit per ton −17% YoY on mix/acquisition effects.
- A 7 gives CAP = 11.1 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 11.1 years, 15-year projection.

## DCF — v5 final run (2026-10-14)
Inputs: base OE $12.60/sh (TTM via --ttm), moat 7 (CAP 11.1y), g_base 7.42% (blend components: rev CAGR 5y +5.39%, rev CAGR 3y −0.06%, latest rev YoY +8.62%, OE/share CAGR 2y +7.39%; share count −1.02%/yr adds a +1.02pp buyback adjustment). Probabilities skewed bearish vs default (15/30/30/20/5 vs 10/25/30/25/10): H1'26 OCF fell hard YoY, Q2 margins compressed, and the pending $13.5B Lhoist deal argues against paying for the bull tail at this price. Offsets and multipliers at defaults (−12/−5/0/+5/+12pp; 0.75/0.90/1.00/1.10/1.25).

Sanity check vs recent prints: the base start of 7.4% sits between TTM revenue growth and organic continuing growth (Q2 2026 organic shipments +2.3% with +3.7% mix-adjusted pricing; Q2 adjusted EPS only +3%) — defensible. Bull 12.4% exceeds organic prints and needs acquired volume plus margin recovery and SOAR savings; super-bull 19.4% exceeds everything the continuing business has printed organically (Q2's +21% revenue headline is acquisition-driven with flat gross profit) — that is why super-bull is cut to 5% weight, not because the start is a cap artifact.

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −4.6% | 0.75 | Construction downturn + Lhoist leverage bite | $55.63 | 3.78% |
| Bear | 30% | 2.4% | 0.90 | Soft housing; pricing only offsets cost inflation | $92.65 | 4.95% |
| Base | 30% | 7.4% | 1.00 | Pricing + mid-single-digit volume; margins stabilize | $130.41 | 6.18% |
| Bull | 20% | 12.4% | 1.10 | SOAR efficiencies + infra volumes + margin recovery | $181.91 | 7.79% |
| Super bull | 5% | 19.4% | 1.25 | Acquisitions all accrete; pricing compounds double-digit | $288.32 | 10.79% |

- **Probability-weighted: IV@15% $126.06 (−73.3% vs price), IV@12% $169.34, IV@10% $217.91, weighted IRR 6.09%, base-case IRR 6.18%**
- **Tier by numbers: D.** Diagnostics: OE yield 2.67% (price = ~37.5x TTM owner's earnings), terminal value 20.0% of IV@15% (not a terminal-assumption artifact — the explicit 15 years don't clear the price either), scenario spread 5.18x, net debt 6.88x normalized OE, 9.4 months since FY end.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.4 months ago): resolved by construction — the base is the TTM figure from ttm.py through Q2 2026, inputs quoted above. The TTM base is *lower* than the FY bases, so staleness was flattering the stock, not penalizing it.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 5.2x super-bear IV): real and structural — at ~37.5x TTM OE the price capitalizes the bull path, so small changes in the growth/margin path swing value hugely. Confidence is capped at medium. The tier conclusion is nonetheless robust: even the super-bull scenario (IV $288.32, IRR 10.79%) sits far below the price and below the 15% hurdle.
- **HIGH_NET_DEBT** (net debt $5,256M = 6.88x normalized OE): folded into the verdict explicitly. Against EBITDA the leverage is moderate and the credit is investment-grade, so this is not distress — but on the owner's-earnings definition this sweep prices (after ~$700–800M/yr of quarry capex), debt-service capacity is thinner, and the announced $13.5B Lhoist North America acquisition, if debt-funded, will push leverage up sharply before its OE contribution is proven (management has guided to deleveraging to target within 24 months of closing). Bear/super-bear weights were raised (45% combined) partly for this. The FY2025 balance sheet predates the deal either way.

## Thoughts / overlay
- Quality is not the problem; price is. This is a genuinely good franchise (moat 7) whose TTM owner's earnings yield 2.67% at $472.39. No defensible input set clears 15%: the preliminary v5 run (median base $13.33, moat 5, default probs) gave 6.53% weighted IRR / IV@15% $143.49; an intermediate TTM-base run (moat 6, probs 10/30/30/20/10) gave 6.33% / $134.73; the final run gives 6.09% / $126.06. Method range across defensible runs: ~6.1–6.5% weighted IRR — Tier D throughout, and even a 100%-super-bull world only reaches ~10.8%.
- The 2024–26 portfolio churn (CRH sale, QUIKRETE exchange, Premier, New Frontier, Lhoist) means historical CAGRs straddle a basis break the engine didn't flag: continuing-operations restatements keep the revenue series usable, but per-ton economics of the new asset base are unproven through a cycle. Another reason not to pay a bull multiple for the blend.
- Hurdle math: the stock clears a 15% hurdle only at or below the weighted IV@15% of **~$126**; with a margin of safety, lower still (~$95 at a 25% discount to that value). That is ~73–80% below the current price — a watchlist-at-a-crash name, not a near-miss.
- What would change the answer: Lhoist closing on accretive terms with rapid deleveraging, or a construction-cycle selloff taking the price toward the low $100s. Neither is today's fact pattern.

## Verdict
**Tier D** (tier by numbers D, no override; weighted IRR 6.09%, weighted IV@15% $126.06 vs $472.39). High-quality local-monopoly aggregates franchise, but at ~37.5x TTM owner's earnings it doesn't come close to the 15% hurdle — it clears 15% only at ~$126, ~$95 with a margin of safety. Confidence: medium (capped by WIDE_SCENARIO_SPREAD and the pending Lhoist transformation; the D conclusion itself holds in every scenario).
