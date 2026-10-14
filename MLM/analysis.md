# MLM — Martin Marietta Materials, Inc.
Run date: 2026-10-13. Engine v4. Price $472.40 (Nasdaq quote API), market cap ~$28.6B (60.6M diluted shares) — in scope (<$40B).

## What it is
One of the two largest US aggregates producers (crushed stone, sand and gravel quarries across the East and West groups), plus asphalt/paving, ready-mixed concrete remnants being exited, and a Magnesia Specialties segment (chemical and high-purity magnesia). The model business is local quarries: aggregates are heavy and cheap per ton, so transport cost confines each quarry to a ~30–50 mile market, and permitted reserves are scarce. Portfolio is rotating to pure aggregates: South Texas cement sold to CRH in Feb 2024 for $2.1B; the QUIKRETE asset exchange closed in 2026 (Midlothian cement + Texas ready-mix out; aggregates assets in VA/MO/KS/Vancouver + $450M cash in); Premier Magnesia acquired Jul 2025; and in Aug 2026 the company agreed to acquire Lhoist North America for $13.5B (pending, per Q2 2026 10-Q reporting and subsequent 8-Ks).

## Owner's earnings
SEC EDGAR filing-direct history (conservative = OCF − capex − SBC; SBC is small, ~$46–50M/yr):
- FY2023: OCF $1,528M − capex $650M − SBC $50M = $828M = $13.33/sh
- FY2024: OCF $1,459M − capex $855M − SBC $58M = $546M = $8.86/sh
- FY2025: OCF $1,785M − capex $807M − SBC $46M = $932M = $15.38/sh
- 3-yr median (engine normalized base): $13.33/sh. OE positive 5/5 of the last 5 years, but lumpy ($7.46–$15.38/sh over 2021–25) — a cyclical, capex-heavy quarry business, not a compounder glide path.
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC) is NOT usable here: it prints $2,970M for FY2024 and −$222M for FY2025. Two distortions explain it: FY2024 net income ($1,995M) contains the $1.3B pretax gain on the South Texas cement divestiture, and the ΔNWC line swings −$975M / +$1,359M across 2024–25 on held-for-sale reclassifications for the QUIKRETE exchange. The OCF-based conservative definition is clean of both (the divestiture gains are investing/non-cash items), so it is the base definition.

**Base used: TTM owner's earnings through Q2 2026 = $12.60/sh** (STALE_FY resolution, arithmetic below). This is below both the median ($13.33) and FY2025 ($15.38) because H1 2026 operating cash flow fell hard — that is current reality, not a trough to normalize away, and using it is the conservative choice.

TTM arithmetic (EDGAR 10-Q YTD, six months ended Jun 30):
- OCF TTM = FY25 $1,785M − H1'25 $605M + H1'26 $339M = $1,519M
- Capex TTM = FY25 $807M − H1'25 $412M + H1'26 $314M = $709M
- SBC TTM = FY25 $46M − H1'25 $37M + H1'26 $41M = $50M
- OE TTM = $1,519M − $709M − $50M = **$760M ÷ 60.3M diluted shares (H1'26 weighted) = $12.60/sh**
- Cross-checks: TTM revenue = $6,150M − $2,771M + $3,309M = $6,688M (+8.7% vs FY25). TTM net income is useless as a check — H1'26 net income of $1,764M includes the ~$1.4B after-tax gain on the Midlothian divestiture, booked in discontinued operations; it never touches OCF, so the OE base is not flattered by it.

## Moat score: 7/10 — strong, local, and real, but cyclical
CAP = 2 + 1.3 × 7 = 11.1 years.
FOR:
- Permitting scarcity: a new greenfield quarry takes years-to-decades of zoning/environmental approval; existing permitted reserves near growing metros are effectively irreplaceable assets.
- Transport economics: aggregates lose competitiveness beyond ~30–50 truck miles, so each deposit is a local oligopoly/monopoly, not a national commodity market.
- Proven pricing power: FY2025 aggregates pricing +6.9% with volumes +3.8% (aggregates revenue +11%, gross margin +143bp to 34%); a multi-year record of mid-to-high single-digit price increases through inflation and soft housing.
- Demand floor: public infrastructure (highway/state DOT work) is the largest end market and is funded multi-year; specialties magnesia adds a niche, higher-margin (record FY25 revenue/gross profit) diversifier.
AGAINST:
- The product itself is an undifferentiated commodity — the moat is location and reserves, not brand, network, or switching costs; a rival quarry inside the same radius competes on price.
- Volumes are hostage to construction cycles: residential weakness already shows in downstream lines, and revenue CAGR is only ~5.4% over 5 yrs and ~0% over 3 yrs on the restated continuing basis.
- Reserves deplete; growth has to be bought back via M&A at rising per-ton prices (Premier, New Frontier, now Lhoist at $13.5B).
- Q2 2026 showed the limit of pricing power near-term: revenue +21% to a record $1,947M (largely acquired volume) but gross profit flat at $495M, earnings from operations −10%, continuing diluted EPS $4.26 (−12%; adjusted $5.00, +3%) — West Group margins compressed faster than price could offset.

## DCF — final v4 run
Inputs: base OE $12.60/sh (TTM override), moat 7 (CAP 11.1y), g_base 7.42% (blend: rev CAGR 5y +5.4%, rev CAGR 3y −0.1%, latest rev YoY +8.6%, OE/sh CAGR 3y +7.4%, +1.0pp buyback adjustment — shares shrinking ~1.0%/yr). Probabilities skewed bearish vs default (15/30/30/20/5 vs 10/25/30/25/10): H1'26 OCF −44% YoY, Q2 margin compression, and the pending $13.5B Lhoist deal argue against paying for the bull tail at this price. Offsets/multipliers at defaults (−12/−5/0/+5/+12pp; 0.75/0.90/1.00/1.10/1.25).

Sanity check vs recent prints: base start 7.4% sits between TTM revenue growth (+8.7%) and organic continuing growth (FY25 aggregates +11% helped by price; Q2 adjusted EPS only +3%) — defensible. Bull 12.4% exceeds organic prints and needs acquired volume + margin recovery; super-bull 19.4% exceeds everything the continuing business has printed organically (Q2's +21% revenue headline is acquisition-driven with flat gross profit) — that is why super-bull is cut to 5% weight, not because the start is a cap artifact.

| Scenario | Prob | Growth start | OE mult | Story | IV@15% | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −4.6% | 0.75 | Construction downturn + Lhoist leverage bite | $55.62 | 3.8% |
| Bear | 30% | 2.4% | 0.90 | Soft housing, pricing only offsets cost inflation | $92.62 | 4.9% |
| Base | 30% | 7.4% | 1.00 | Pricing + mid-single volume, margins stabilize | $130.37 | 6.2% |
| Bull | 20% | 12.4% | 1.10 | SOAR efficiencies + infra volumes + margin recovery | $181.85 | 7.8% |
| Super bull | 5% | 19.4% | 1.25 | Acquisitions all accrete, pricing compounds double-digit | $288.23 | 10.8% |

**Probability-weighted: IV@15% $126.02, IV@12% $169.29, weighted IRR 6.1%** (base-case IRR 6.2%). Price $472.40 = 37.5× TTM owner's earnings; OE yield 2.7%. Upside at 15% = −73.3%. Diagnostics: terminal value only 20% of IV@15% (this is not a terminal-assumption artifact — the explicit 15 years don't clear the price either), scenario spread 5.2×, net debt 6.9× TTM-normalized OE.

## FLAGS — every fragility flag resolved
- **STALE_FY** (FY ended 9 months ago): Resolved with the TTM override above — FY25 base replaced by TTM through Q2 2026 ($12.60/sh), built from 10-Q YTD OCF/capex/SBC. The TTM is *lower* than the FY base because H1'26 OCF fell to $339M from $605M; seasonality is not an excuse — the TTM formula (FY − prior H1 + current H1) is a full 12 months.
- **WIDE_SCENARIO_SPREAD** (super-bull IV 5.2× super-bear): Real and structural — at 37.5× OE the price capitalizes the bull path, so small changes in the growth/margin path swing value hugely. Confidence is capped at medium (not high) per the rule; the *tier conclusion* is nonetheless robust because even the super-bull scenario (IV $288, IRR 10.8%) sits far below the price.
- **HIGH_NET_DEBT** (net debt $5,256M = 6.9× normalized/TTM OE): Folded into the verdict explicitly. Against EBITDA (~$2.1–2.2B) leverage is a moderate ~2.4× and the credit is investment-grade, so this is not distress — but on the owner's-earnings definition that this sweep prices (after ~$700–800M/yr of quarry capex), debt service capacity is thin, and the announced $13.5B Lhoist North America acquisition, if debt-funded as the Aug–Sep 2026 8-K financing items suggest, will push leverage up sharply before its OE contribution is proven. Bear/super-bear weights were raised (45% combined) partly for this.

## Thoughts / overlay
- Quality is not the problem; price is. This is a genuinely good franchise (moat 7) whose TTM owner's earnings yield 2.7% at $472. No defensible input set clears 15%: the preliminary run (median base $13.33, moat 5, default probs) gave 6.5% weighted IRR / IV $143; the final TTM-base run gives 6.1% / $126. Method range across defensible runs: ~6.1–6.5% weighted IRR — Tier D throughout, and even a 100%-super-bull world only reaches 10.8%.
- The 2024–26 portfolio churn (CRH sale, QUIKRETE exchange, Premier, New Frontier, Lhoist) means historical CAGRs straddle a basis break the engine didn't flag (>60% revenue jump test not tripped): continuing-operations restatements make the revenue series usable, but per-ton economics of the *new* asset base are unproven through a cycle. Another reason not to pay a bull multiple for the blend.
- Hurdle math: the stock clears a 15% hurdle only at or below the weighted IV@15% of **~$126**; with a 25% margin of safety, **~$95**. That is ~73–80% below the current price — this is a watchlist-at-a-crash name, not a near-miss.
- What would change the answer: Lhoist closing on accretive terms with rapid deleveraging, or a construction-cycle selloff taking the price toward the low $100s. Neither is today's fact pattern.

## Final verdict
- **Final tier: D** (tier by numbers D; weighted IRR 6.1% — no overlay adjustment, the numbers and the story agree)
- Confidence: **Medium** (capped by WIDE_SCENARIO_SPREAD and the pending Lhoist transformation; the D conclusion itself holds in every scenario)
- One-liner: High-quality local-monopoly aggregates franchise, moat 7/10, but at $472 (37.5× TTM owner's earnings) it doesn't come close to the 15% hurdle — weighted IRR 6.1%, IV@15% $126; it clears 15% only at ~$126, ~$95 with a margin of safety.
