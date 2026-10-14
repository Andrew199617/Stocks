# SNAP — Snap Inc.
Run date: 2026-10-13 (engine v5 re-run). In scope: market cap ~$11.0B < $40B.

## What it is
Snapchat: a visual-messaging / camera social platform — 493M daily active users and 971M monthly actives at Q2 2026 (company Q2 2026 release, via search). Revenue is mostly advertising (Q2 2026 ad revenue $1.28B, +9% YoY) plus a fast-growing direct-revenue leg (Snapchat+, Memories Storage, Lens+ — "other" revenue $316M in Q2 2026, +85% YoY). Also developing Specs AR glasses — a call option, not a current earnings driver. Asset-light in PPE terms (FY2025 capex $219.0M) but with a very heavy stock-comp cost structure, which is the whole story below.

## Owner's earnings (SEC EDGAR, filing-direct)
- FY2025: OCF $656.170M − capex $218.981M − SBC $1,016.825M = **conservative OE −$579.636M = −$0.342/share** (engine: base_oe_latest_per_share −0.3420). Normalized base (median of last 3 FY OE/share) = **−$0.496/share**. Conservative OE has been positive in **0 of the last 5 fiscal years** (0 of 10 in the full history) — but it is improving monotonically: the latest FY (−$0.342) is the least negative of the three years in the median window.
- The blocker is one line: **SBC**. SBC was $1,016.825M in FY2025 — larger than the entire $656.170M of operating cash flow. Snap generates real cash before SBC (FCF = OCF − capex was +$437.189M in FY2025, per financials_history.csv); after paying employees in stock, owners are underwater. Per this sweep's standing rule, SBC is a real cost, not an add-back.
- Maintenance version FY2025: −$111.385M — less negative than the conservative figure, but the gap is a working-capital artifact (the formula's ΔNWC was a $349.104M release, and Snap's current assets include its marketable-securities portfolio, so portfolio drawdowns masquerade as operating NWC releases). The OCF-based conservative figure is the cleaner one.
- **STALE_FY resolution — TTM base through Q2 2026, computed by ttm.py from EDGAR 10-Q YTD facts (inputs quoted verbatim):**
  - OCF: FY2025 $656,170,000 − H1 2025 YTD $240,104,000 + H1 2026 YTD $502,993,000 = **TTM $919,059,000**
  - Capex: FY2025 $218,981,000 − H1 2025 YTD $101,915,000 + H1 2026 YTD $96,448,000 = **TTM $213,514,000**
  - SBC: FY2025 $1,016,825,000 − H1 2025 YTD $499,224,000 + H1 2026 YTD $513,229,000 = **TTM $1,030,830,000**
  - Shares: H1 2026 weighted diluted **1,675,483,000** (ttm.py basis: current YTD weighted average)
  - **TTM conservative OE = −$325,285,000 = −$0.1941/share** — this is the base used in the final engine pass (`--base-oe-ps -0.19414401697898456`; dcf_numbers.json base_source = agent_supplied_ttm_override). Still negative, so the verdict below is unchanged: every defensible conservative base — latest FY, 3-yr median, TTM — is negative. Sensitivity, not an adjustment: Q2 2026 included a $128.5M restructuring charge (Q2 2026 earnings coverage); even if it were added back in full, TTM OE would remain negative.

## Moat score: 4/10 — weak-to-moderate
FOR:
- Differentiated close-friends ephemeral-messaging graph with a loyal younger North America/Europe cohort
- AR/camera platform depth (Lenses, creator AR ecosystem, Specs optionality)
- Emerging direct-revenue leg with demonstrated willingness to pay (other revenue +85% YoY in Q2 2026; direct revenue past $1B annualized per company commentary) with <3% of monthly users paying — headroom if conversion grows
AGAINST:
- Scale and ad-targeting disadvantage vs Meta/Google/TikTok — ad revenue only +9% in Q2 2026 while subscriptions carried total growth
- Growth from the wrong geography: Q2 2026 DAU +5% globally but North America −7% YoY and Europe −2%; all net growth is Rest of World at $1.00 ARPU vs $10.26 in North America (Q2 2026 release figures via search)
- No real switching costs: users multi-home and features are copied within quarters; ~15 years without GAAP profitability — pricing power asserted, not proven
- Platform dependence: Apple/Google privacy and app-store rules sit between Snap and its advertisers and subscribers

Justification: a real, differentiated social graph and AR capability, but no demonstrated pricing power or profitability, a structural scale disadvantage in the ad auction, and growth concentrated in the lowest-ARPU region. CAP from moat 4: clamp(2 + 1.3×4, 2, 15) = **7.2 years** — moot for the DCF (no positive OE to fade), but it records a fade window well short of the leaders'.

## Five scenarios — FINAL v5 run (2026-10-13)
Price: **$6.49** (Nasdaq quote API, engine run); market cap est. $10,997,941,020 on 1,694,598,000 diluted shares (dcf_numbers.json). The engine cannot project scenarios on a negative base, and forcing one would be inventing numbers — so there are no scenario IVs or IRRs, by design (no positive normalized OE = Tier F, flagged not forced). Likelihoods are the defaults, assigned for the record:

| Scenario | Prob | Growth start | OE mult | Story | IV@15% | IRR |
|---|---|---|---|---|---|---|
| Super bear | 10% | n/a — no OE base | n/a | Ad growth stalls (NA DAU already −7%), SBC stays ~$1.05B/yr, Specs burns cash; OE stays negative indefinitely and dilution compounds | n/a (OE < 0) | n/a |
| Bear | 25% | n/a | n/a | Revenue grows low-double-digits but SBC is guided ~$1.05B for 2026 and buybacks only partly offset grants; OE breakeven keeps slipping | n/a (OE < 0) | n/a |
| Base | 30% | n/a | n/a | Management's own path: SBC flat in dollars and falling as % of revenue, share count stabilized via the dilution-management program — first positive OE late this decade, but nothing to discount today | n/a (OE < 0) | n/a |
| Bull | 25% | n/a | n/a | Direct revenue keeps compounding, ad growth re-accelerates on AI targeting, OCF growth outruns a flat SBC line and OE flips solidly positive within ~2 years — value sits beyond the OE screen's current window | n/a (OE < 0) | n/a |
| Super bull | 10% | n/a | n/a | Snapchat+ conversion scales, Specs becomes a real platform, SBC/revenue collapses toward peer levels — a monetization story, not a current owner's-earnings story | n/a (OE < 0) | n/a |

- **Probability-weighted IV@15% / IRR: not computable — no positive owner's earnings in any conservative base period.**
- **Tier by numbers: F.** Sanity check per the standing rule — revenue growth starts can't rescue a negative base, but for the record the trajectory is real: FY2025 revenue +10.6% YoY (engine rev_yoy_latest), Q2 2026 revenue $1,599M +19% YoY, Q3 2026 guided to $1.70–1.74B with Adjusted EBITDA $300–350M (company guidance via search). None of that changes the OE sign while SBC ≈ $1.03–1.05B/yr absorbs more than all of OCF.
- Diagnostics: TTM OE yield on price is negative (−$0.1941 against a $6.49 price). 100% of the price is payment for a future SBC-discipline outcome that has not yet appeared in any filing. Engine net debt (FY2025 basis) is $2,459,425,000, but that figure counts only cash against debt; the company reported ~$2.7B of cash plus marketable securities at Q2 2026 (Q2 2026 coverage), so balance-sheet leverage is modest and is not a verdict driver — stated in words because the corrected figure is not in the computed outputs.

## FLAGS — resolving every fragility flag from the final v5 run
- **STALE_FY** — Fires: latest fiscal year ended 2025-12-31, 9 months before this run. Resolved with the ttm.py TTM base quoted above: TTM OE −$0.1941/share, an improvement on FY2025's −$0.3420 but still negative. Verdict unchanged.
- **BASIS_BREAK_SUSPECT** — Checked against financials_history.csv and resolved as a false alarm for the recent window: annual revenue growth over the last 5 fiscal years was +11.8% (2022), +0.1% (2023), +16.4% (2024), +10.6% (2025) — no >60% jump or drop, no material divestiture/M&A/restatement. The >60% move the flag sees is 2020 → 2021 revenue ($2,506.626M → $4,117.048M), organic hypergrowth in the pandemic ad boom, not a basis break. It does mean the 5-yr revenue CAGR (18.8%) flatters the long window vs the 3-yr CAGR (8.8%) — one more reason no growth input was trusted with a negative base.
- **NI_OCF_DIVERGENCE** — Fires for 2023, 2024, 2025 and is resolved: the gap is structural, not a one-off. FY2025 net income −$460.489M vs OCF +$656.170M; FY2024 NI −$697.856M vs OCF +$413.480M; FY2023 NI −$1,322.485M vs OCF +$246.521M (all financials_history.csv). In each year the dominant reconciling item is the non-cash SBC add-back (SBC $1,324.004M / $1,041.023M / $1,016.825M in 2023/2024/2025), dwarfing D&A. OE is built on OCF and then subtracts SBC explicitly, so it is clean of this — and it is precisely this divergence that makes Snap's GAAP loss look worse than its cash burn while its Adjusted EBITDA looks better than its owner's earnings.
- Flags checked that did **not** fire in the v5 output: BASE_DIVERGENCE does not drive the verdict (latest FY −$0.3420 vs median −$0.4957 differ, but every base is negative — the TTM base was used because it is freshest, not because it flatters); DILUTION is borderline — diluted share CAGR +1.76%/yr (engine share_cagr) and the Q2 2026 release reported common shares outstanding of 1,682M at June 30, 2026, flat vs June 30, 2025, i.e. buybacks are currently running to stand still against SBC; HIGH_NET_DEBT does not reflect the marketable-securities portfolio (see Diagnostics); SECTOR_MODEL_MISMATCH does not fire (Technology) — the OE/capex model fits Snap's asset-light cost structure well, which is exactly why the F is informative: the model isn't missing capex, it's counting SBC.

## Thoughts / overlay
- Unlike a pre-revenue name, SNAP's F is narrow and closing: the TTM OE gap is −$325.285M on a growing revenue base, and the OE/share trajectory (−$0.496 median → −$0.342 FY2025 → −$0.194 TTM) crosses zero within ~1–2 years IF SBC stays flat in dollars (guided ~$1.05B for 2026) while OCF keeps compounding. Management is explicitly managing to FCF/share and a stable share count. Those are the right promises; they are also unproven — SBC has been ~$1.0–1.4B every year since 2021 per the filing history.
- What the buyer at $6.49 is actually paying for: TTM free cash flow *before* SBC (the company reported TTM FCF of $706M through Q2 2026), for a business whose highest-value users are shrinking (NA DAU −7%) and whose growth engine is currently subscriptions and storage sold to <3% of users, plus a World Cup ad bump in Q2. That can work — but it is a monetization-and-discipline bet, not an owner's-earnings stream, and on this sweep's rules there is **no price at which a negative-OE company clears a 15% hurdle** and no margin-of-safety price to quote.
- Method range: on the conservative definition there is none — latest-FY, 3-yr-median, and ttm.py TTM bases are all negative, and even a full restructuring add-back stays negative. The maintenance definition is less negative (FY2025 −$111.385M) but still negative on an FY basis, so no defensible base supports a DCF.
- What would change the tier: two consecutive filings showing TTM conservative OE > 0 — OCF growth doing the work while SBC stays at ~$1.05B — plus a diluted share count that is actually flat. At that point SNAP gets a real DCF; until then it stays F regardless of revenue headlines.

## Final verdict
- **Final tier: F** (= tier by numbers; no override — there is no positive conservative owner's earnings to underwrite any hurdle)
- Confidence: **Medium** — high confidence in the arithmetic (OE is negative under every conservative base and both the FY and TTM windows, and the TTM inputs tie to the company's reported TTM FCF), but the gap is closing fast enough that this F has a shorter shelf life than most: one to two years of guided SBC discipline would flip it.
