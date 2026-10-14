# DUOL — Second pass (2026-10-13)

Verdict: **NO MATERIAL FINDING — score stands.** Tier D, weighted IRR 9.1%, IV@15% $72.59 at $147.74, moat 5/10, TTM base OE $5.26/share. score.json not touched.

Pass 1 (2026-10-12, engine v4): TTM base $5.26 (OCF $430.548M − SBC $144.684M − capex $22.617M = $263.247M / 50.080M shares), scenario starts −2/7/15/23/32% (written recalibration below the 35% cap against guided deceleration), probs 15/30/30/17/8, CAP 8.5y.

## Filing freshness + forensic battery (forensic_pull.py, 2026-10-13)

```
# Forensic battery — DUOL (CIK 1562088)
Tags used: revenue=RevenueFromContractWithCustomerExcludingAssessedTax, gross_profit=GrossProfit, cogs=CostOfRevenue, sga=SellingAndMarketingExpense+GeneralAndAdministrativeExpense, ni=NetIncomeLoss, oi=OperatingIncomeLoss, disc_ops=None, nonop=NonoperatingIncomeExpense, prepaids=PrepaidExpenseAndOtherAssetsCurrent, assets=Assets

| FY end | Revenue | Gross margin | COGS %rev | SG&A %rev | (COGS+SG&A) %rev | NI vs OI gap | Disc ops | Nonop inc |
|---|---|---|---|---|---|---|---|---|
| 2020-12-31 | $162M | +71.6% | +28.4% | +48.7% | +77.1% | +1.5% | n/a | $72,000 |
| 2021-12-31 | $251M | +72.4% | +27.6% | +54.9% | +82.5% | -0.2% | n/a | $30,000 |
| 2022-12-31 | $369M | +73.1% | +26.9% | +50.0% | +76.9% | +8.6% | n/a | $-676,000 |
| 2023-12-31 | $531M | +73.2% | +26.8% | +39.1% | +65.9% | +221.2% | n/a | $-55,000 |
| 2024-12-31 | $748M | +72.8% | +27.2% | +33.0% | +60.2% | +41.5% | n/a | $-3M |
| 2025-12-31 | $1.04B | +72.2% | +27.8% | +29.6% | +57.4% | +205.4% | n/a | $2M |

## Prepaid battery
- 2024-09-30: prepaids $16M = 1.3% of assets
- 2024-12-31: prepaids $15M = 1.1% of assets
- 2025-03-31: prepaids $17M = 1.2% of assets
- 2025-06-30: prepaids $19M = 1.3% of assets
- 2025-09-30: prepaids $17M = 0.9% of assets
- 2025-12-31: prepaids $17M = 0.8% of assets
- 2026-03-31: prepaids $20M = 1.0% of assets
- 2026-06-30: prepaids $21M = 1.0% of assets
- YoY change at 2026-06-30: +7.6%
- Prepaids / latest FY SG&A: 7%

## Battery flags
- NI_OI_GAP 2023-12-31: net income differs from operating income by +221.2%
- NI_OI_GAP 2024-12-31: net income differs from operating income by +41.5%
- NI_OI_GAP 2025-12-31: net income differs from operating income by +205.4%

## Filing freshness
- Pass 1 analysis date: 2026-10-12; latest period pass 1 used: 2025-12-31
- Newer periodic filing since pass 1: NONE — pass 1 data is filing-current.
- Material 8-Ks since pass 1: none
```

### Battery resolutions
- **Freshness:** No newer 10-K/10-Q and no material 8-K since pass 1. Pass 1's TTM-through-Q2-2026 base is filing-current; no TTM recompute required. Q3 report is expected in early November — a future event, not a stale-base finding.
- **Margin structure / moat:** Gross margin 71.6–73.2% every year 2020–2025, COGS 26.8–28.4% of revenue — exceptionally stable for a software/subscription business, well above the 40% durable-advantage rule of thumb. This supports pass 1's moat pillars (brand/habit/data) but does not raise the score: pass 1's AGAINST case was pricing power and AI entry barriers, not cost structure, and Q2 2026 gross margin was 72.6% with full-year guide drifting toward ~69–70% by Q4 — stable, not expanding.
- **SG&A-vs-COGS split:** No migration optics. COGS % is flat while SG&A % falls 48.7% → 29.6% and the combined (COGS+SG&A)/revenue falls 77.1% → 57.4%. That is real operating leverage as revenue scaled, not costs being reclassified between lines. Trust both series.
- **NI-vs-OI gap (all three flags):** Resolved — the gap is tax/below-the-line, not operating noncore. Nonoperating income is trivial every year ($72k to $2M, −$3M in 2024). 2023's +221% is arithmetic on near-zero operating income (−$13.3M OI vs +$16.1M NI). 2025's +205% is the one pass 1 already identified: NI $414.1M vs OI $135.6M, driven by the $256.7M deferred-tax valuation-allowance release in the FY2025 10-K. It inflates NI and the NI-based maintenance OE ($458.6M), which is exactly why pass 1 rejected that definition. The conservative OCF-based base excludes it — no base rebuild needed.
- **Prepaid battery:** No deferral pattern. Prepaids are 0.8–1.3% of assets throughout, +7.6% YoY at Q2 2026 (slower than revenue growth), 7% of FY SG&A. No spike alongside improving earnings / weakening OCF.
- **Discontinued ops / divestiture optics:** None on the books (disc_ops = None every year); no divestiture or held-for-sale line to compare pre/during/post. Check run, nothing to resolve.
- **Noncore reconstruction:** Core = reported. Nonoperating items are immaterial (<0.3% of revenue every year); the only material noncore item is the 2025 tax benefit, which sits below operating income and does not enter the OCF-based OE base. Core operating profit = operating income as reported. Noncore is not carrying the base.
- **Capitalized-cost shifting:** No WorldCom pattern. Capex is $18.1M in FY2025 (1.7% of revenue), $22.6M TTM; PPE net $36.3M. SG&A falls as a % of revenue but rises in absolute dollars (~$79M in 2020 → ~$307M in 2025), and R&D/S&M rose +25%/+35% YoY in Q2 2026 per earnings coverage — costs are not being shifted off the P&L into capex while earnings outrun OCF.
- **Honest OE definition:** The total-capex (conservative) definition, as pass 1 used. Capex is trivial either way, but the maintenance version starts from NI and inherits the $256.7M tax one-off — it is the distorted one here.

## Targeted research (3 searches, 2026-10-13)
- **(a) Segments masked by consolidated:** Q2 2026 revenue split — subscription revenue +22.5% YoY ($258.0M of $298.5M), advertising +2.2% ($21.1M), total +18.3%. The growing core (subscriptions) is the business; ads are small and slow but not a sunset drag large enough to mask anything, and subscription bookings +10% / total bookings +8% confirm the consolidated deceleration pass 1 modeled is real paid-demand deceleration, not a legacy-segment artifact. Math/music/chess are not broken out and have no disclosed material revenue — no hidden second engine with filing evidence. Sources: Q2 2026 shareholder letter (SEC, accession via sec.gov Archives 000162828026053299), Zacks/AInvest Q2 metrics coverage.
- **(b) Recurring "one-offs":** None found that pass 1 normalized away in the OE base — the base is cash (OCF − capex − SBC) and contains no add-backs. Q2 2026 R&D +25% and S&M +35% YoY (faster than revenue, NI −26%, adj. EBITDA −2%) is the guided DAU-first investment year pass 1 already bear-weighted (45% bear/super-bear, EBITDA guide ~+5%). Source: Zacks Q2 2026 review.
- **(c) Post-filing events:** No guidance change, M&A, customer loss, or product sunset after the Q2 filing that pass 1 used. Full-year 2026 guide is unchanged (revenue ~$1.21B / +16%, bookings +10–12%, adj. EBITDA ~$320M). The Oct 13, 2026 shareholder-alert notices are the same securities class action pass 1 already flagged (class period May 2, 2025–Feb 26, 2026; lead-plaintiff deadline Dec 7, 2026) — allegations unproven, no quantified liability, no change to inputs. Sources: GlobeNewswire/PR Newswire class-action notices dated Oct 11–13, 2026; Q2 shareholder letter guidance page.
- **(d) SBC / dilution:** On pass 1's trajectory. Management guides 2026 SBC ≈15% of revenue and diluted share count +3.5–4% before buybacks; Q2 letter's diluted-share table totals 50.7M vs the 50.08M in pass 1's TTM base — in line. H1 2026 buybacks ~695k shares / ~$70M under the $400M authorization partly offset grants. SBC remains ~1/3 of OCF and is deducted in full in the base. Sources: Q1/Q2 2026 shareholder letters (SEC).
- **(e) Thin flags re-checked:** BASE_DIVERGENCE and NI_OCF_DIVERGENCE resolutions hold under the battery (see above) — the median and the maintenance OE are the distorted figures, the TTM OCF base is the clean one. DILUTION resolution holds per (d).

## Why the score stands
Every load-bearing pass-1 assumption survived: filing-current TTM base, stable ~72% gross margin with no cost-shifting or deferral pattern, guided (not hidden) deceleration to ~16% revenue / ~8–11% bookings, SBC/dilution as guided, and no post-filing event that moves the numbers. No segment, forensic, or event evidence quantifies a different base, growth path, moat, or probability set. Tier D / 9.1% weighted IRR unchanged.
