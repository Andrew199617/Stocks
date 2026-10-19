# VIV — TELEFONICA BRASIL S.A. (Telefônica Brasil / Vivo)
v5 run, 2026-10-16. All figures below are copied from dcf_numbers.json, financials_history.csv, or ttm.py output — none are recomputed. Interim-print figures are from the company's filed 6-K earnings releases as summarized in search results, cited where used.

## What it is
Brazil's incumbent-scale telecom operator, trading as Vivo: the country's largest wireless carrier (about 33% market share, postpaid leadership at about 37% of postpaid), plus FTTH broadband, fixed voice and corporate data/ICT across Brazil. Controlled by Telefónica S.A. (77.13% direct/indirect interest at March 31, 2026, per the Q1 2026 6-K). Files on Form 20-F under IFRS, reports in BRL. NYSE ADS (ticker VIV); B3 listing VIVT3.

## Owner's earnings
**FY2025 (20-F via EDGAR, from financials_history.csv, USD after FX conversion):** operating cash flow $3,782,168,909.12; capex $1,726,571,605.92 (tag: PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities); SBC $9,820,267.52 (tag: ExpenseFromSharebasedPaymentTransactionsWithEmployees — SBC is always a real cost; here it is negligible either way); net income $1,127,772,250.08; D&A $2,728,250,394.24.
- **Conservative owner's earnings FY2025: $2,045,777,035.68** (OCF − capex − SBC). OE positive 5 of the last 5 fiscal years.
- Maintenance version (NI + D&A − min(capex, D&A) − ΔNWC): $2,102,693,492.58 for FY2025 — same ballpark as the conservative figure.
- OE totals are stable in total terms: FY2023 $2,043,840,075.89, FY2024 $1,699,459,237.38, FY2025 $2,045,777,035.68. FY2024 is the soft year of the three.
- **The per-share history is broken — see BASE_DIVERGENCE under Flags.** The engine's normalized base (3-yr median) is $2,068.56 per ADS, a share-unit artifact, and is rejected. **Base used = FY2025 owner's earnings per share, pinned via a declared base_override:** $0.6401843063053217 per ordinary share from the preliminary run's dcf_numbers.json (FY2025 is the only recent year filed on the post-transaction share count of 3,195,606,352), scaled by the FY2025 20-F ADS ratio of 2 ordinary shares per ADS = **$1.2803686126106435 per ADS** (base_source: agent_supplied_ttm_override). FY2025 total OE is in line with FY2023's, so the latest year is not an outlier being cherry-picked; it is the only clean per-share year.
- **Balance sheet:** the engine returned net_debt_latest: null — it read no borrowings tags for this filer (debt_current / debt_lt tags are null), so no net-debt figure exists in the computed outputs and none is folded into the verdict numerically. Qualitatively, the Q2 2026 release's own debt presentation excludes FISTEL TFF regulatory fees of R$7.3B for 2020–2026 — a real overhang a buyer should not ignore.
- **Revenue series:** the engine read no revenue for any year (used_tags revenue: null — this filer's IFRS revenue concept is not in the engine's map), so there are no engine revenue CAGRs. Growth evidence below comes from the company's filed interim releases instead.

## OVERRIDES / JUDGMENT CALLS (both registered and badged by make_score.py)
- **ads_ratio = 2** (kind: filing-sourced judgment field). Source: Form 20-F for fiscal year ended December 31, 2025 (filed February 23, 2026), notes to the consolidated financial statements on the 2025 share transaction (40-for-1 reverse split followed by a split under which 1 grouped share became 80 shares — a net doubling of the share count), stating 1 ADR now represents 2 ordinary shares, with the total number of ADRs unchanged. Before that transaction the ratio was 1.
- **base_override = $1.2803686126106435 per ADS.** Construction (quoted in judgment.json): this run's preliminary dcf_numbers.json figure base_oe_latest_per_share $0.6401843063053217 × the 20-F ADS ratio of 2. A shares_override cannot cure the underlying problem — overrides fill missing periods only and never replace filed values — and ttm.py cannot run on this IFRS filer (see STALE_FY). Escalation was considered and not used: every input to the pin is either a figure printed by this run's engine output or the filing-sourced ADS ratio the sweep's bounded authority separately authorizes, and the declaration is registered with its measured impact for main-agent review.

## Moat: 5/10 — moderate / narrow
Justification: Brazil's largest wireless carrier (about 33% market share, postpaid leadership) with scale, spectrum, the Vivo brand and a large FTTH footprint enabling converged cross-sell, backed by the Telefónica group — against strong Claro/TIM competition, low prepaid switching costs, heavy 5G/FTTH capex intensity, Anatel regulation including the FISTEL fee overhang, BRL/USD exposure on a USD-priced ADS, and minority holders subordinate to the controlling parent.
- FOR: largest Brazilian wireless carrier — about 33% market share with postpaid leadership (about 37% of postpaid); scale, spectrum holdings and the Vivo brand, with record mobile ARPU in the Q2 2026 prints; extensive FTTH network enabling converged fixed-mobile cross-sell into its mobile base; Telefónica group parentage — technology, procurement and balance-sheet backing.
- AGAINST: Claro (América Móvil) and TIM compete hard on price and network, and prepaid switching costs are low; capex intensity is structural (capex was 16.4% of revenue in Q2 2026, per the filed release) — the 5G and FTTH build never stops; regulatory overhang — Anatel oversight and FISTEL TFF fees (R$7.3B for 2020–2026 excluded from the company's own debt figure in the Q2 2026 release); BRL earnings priced in USD — real depreciation directly cuts per-ADS owner's earnings; controlled company (Telefónica 77.13%) — minorities are subordinate to group strategy and a distribution commitment of no less than 100% of annual net income for 2024–2026.
- A 5 gives CAP = 8.5 years: growth holds 2 years, then converges linearly to the 2.5% terminal rate over 8.5 years, 15-year projection.

## DCF — v5 final run (2026-10-16)
Growth recalibration (written reason): the engine's blended growth is −97.71% and g_base floored at −5% because its only non-null component is oe_ps_cagr_2y (−97.71%), which is computed across the broken share-count series (see Flags), and every revenue component is null. That blend contains no usable economic signal. Scenario starts were therefore set via offsets (+0.03 / +0.06 / +0.10 / +0.14 / +0.19 vs the floored g_base) to −2 / +1 / **+5** / +9 / +14%, anchored on the company's actual recent BRL prints: Q2 2026 revenue +7.6% YoY, EBITDA +10.9%, net income +17.0% (filed 6-K release). The base start of +5% sits below the BRL revenue print on purpose: the DCF is in USD, and BRL depreciation is a recurring drag on per-ADS growth. Probabilities were widened to the bear side (15/25/30/20/10) for Brazil/FX risk; OE multipliers are the defaults 0.75/0.90/1.00/1.10/1.25. Price $12.26 (nasdaq_quote_api).

| Scenario | Prob | Growth start | OE mult | Story | IV@15 | IRR |
|---|---|---|---|---|---|---|
| Super bear | 15% | −2.0% | 0.75 | BRL slide + price war; capex cannot flex down | $6.53 | 8.97% |
| Bear | 25% | +1.0% | 0.90 | BRL growth eaten by FX translation; FISTEL/regulatory drag | $8.88 | 11.51% |
| Base | 30% | +5.0% | 1.00 | Mid-single-digit USD OE growth, fading over the 8.5-yr CAP | $11.65 | 14.39% |
| Bull | 20% | +9.0% | 1.10 | BRL prints hold in USD; converged/FTTH mix lifts ARPU | $15.12 | 17.71% |
| Super bull | 10% | +14.0% | 1.25 | Strong real, buyback shrink, margin expansion together | $21.09 | 22.75% |

- **Probability-weighted: IV@15% $11.83 (−3.5% vs the $12.26 price), IV@12% $15.71, IV@10% $20.04, weighted IRR 14.57%, base-case IRR 14.39%**
- **Tier by numbers: C.** Diagnostics: OE yield 10.44%, terminal value 18.73% of IV@15%, scenario spread 3.23x, 9.5 months since FY end, IRR not capped on the corrected base.
- Scope note: the engine's market_cap_est is $39,178,133,875.52, which multiplies the per-ADS price by the ordinary share count, so it overstates the true capitalization; the name is under the $40B scope limit on either basis.

## Flags — every fragility flag resolved
- **STALE_FY** (FY ended 9.5 months ago): ttm.py was run and exited 3 — it reads us-gaap facts only, so for this IFRS filer it reported no annual OCF/SBC/shares/capex facts and refused to zero-fill; there is no ttm.json and no TTM pin. Per the sweep rules for IFRS names, the engine's annual base is used instead — here, the pinned FY2025 base above. Interim evidence since FY end comes from the filed 6-K releases: Q2 2026 revenue R$15,757M, +7.6% YoY; net income R$1,573M, +17.0% YoY; capex R$2,589M (16.4% of revenue); shareholder remuneration paid in 7M26 of R$6,990M with a buyback of up to R$1.0B authorized through February 2027.
- **BASE_DIVERGENCE** (latest FY OE/share $1.28 vs 3-yr median $2,068.56 per ADS): the median is the distorted figure. In financials_history.csv the filed diluted share counts are 1,663,556,731,000 for FY2022, 1,658,604 for FY2023 and 1,643,132 for FY2024 — the FY2023/24 facts are in thousands and on the pre-transaction basis — while FY2025's 3,195,606,352 is on the post-transaction basis (the filer's Q1 2026 6-K reports weighted average shares in thousands of 3,195,606, with comparatives restated for the reverse split / split). OE/share for FY2023/24 therefore prints in the thousands of dollars and poisons any median or CAGR that touches it. Resolution: pin the base to the one clean year (FY2025) via the declared base_override, and recalibrate growth from filed prints rather than the blend.
- **BUYBACK_TAILWIND** ("share count shrinking 87.6%/yr"): an artifact of the same share-series break, not a buyback — the −87.56% share_cagr spans the thousand-unit and pre/post-transaction facts. A real but modest buyback exists (up to R$1.0B authorized through February 2027; 34,740,770 treasury shares were cancelled in 2025 per the filer's 6-K). The +5pp share-count adjustment the engine already credited inside g_base is not relied on: scenario growth was set from prints, not from the blend.
- **OE_VOLATILE** (OE/share range over 5 years spans >3x): an artifact of the share-unit break in per-share terms. In total terms the last three years' conservative OE is $2,043,840,075.89 / $1,699,459,237.38 / $2,045,777,035.68 — a stable, not volatile, series. Bear-side weight was still widened (15% super bear) for Brazil/FX risk.
- **NI_OCF_DIVERGENCE** (2023, 2024): structural, not a one-off. This is a network carrier: net income is stated after very large non-cash depreciation (D&A was $2,759,457,099.57 in FY2023 and $2,296,367,461.65 in FY2024, from financials_history.csv), which operating cash flow adds back, so OCF ($3,871,591,489.34 in FY2023; $3,213,842,279.92 in FY2024) runs far above net income ($1,038,688,859.93; $898,565,011.08) in a normal year. The OE base is not flattered by the gap: the conservative definition deducts the full capex that replaces the depreciated network.
- **FX_CONVERTED**: BRL reporting converted to USD at period-end ECB reference rates (frankfurter.app); flow facts use the period-end rate, not a period average. Rates recorded in dcf_numbers.json include 0.16169 for 2024-12-31 and 0.18256 for 2025-12-31 — that swing alone moves USD-reported results materially year to year, and is a standing risk to any USD verdict on this name.
- **ADS_RATIO_APPLIED** (supersedes the preliminary run's ADS_RATIO_MISSING): per-share figures scaled ×2.0 ordinary shares per ADS from the FY2025 20-F — see OVERRIDES. The preliminary run's fake Tier S (weighted IRR capped at 200%, IV@15% $6,745.06 on the $1,034.28 corrupted median base) is rejected in full; on the corrected base the IRR is not capped.

## My thoughts / overlay
- The honest headline is that the preliminary Tier S was a data artifact — wrong share units in two of the three median years — and the corrected picture is a fairly priced, high-payout Brazilian incumbent: a 10.44% OE yield on the pinned base at $12.26, with mid-single-digit USD growth if BRL behaves.
- Method range: the defensible bases cluster on FY2025 (the only clean per-share year), so the range is narrower than the flags suggest — the verdict is C on the pinned base, and only the bull/super-bull scenarios (30% combined weight) clear the 15% hurdle. It does not clear 15% on the weighted case at $12.26.
- What the standardized model misses, in both directions: it deducts all capex including growth capex for FTTH/5G (maintenance OE is likely higher than the conservative figure), but it also deducts no IFRS 16 lease payments and carries no net-debt adjustment because the engine read no borrowings — and the FISTEL TFF exposure sits outside the company's own debt presentation.
- Hurdle math: the stock clears the 15% hurdle at or below the weighted IV@15% of $11.83; a buyer wanting the bear case covered needs a price at or below the bear IV@15% of $8.88. At $12.26 neither is on offer — the distribution (the company committed to distributing no less than 100% of net income for 2024–2026, and paid R$6,990M in 7M26) is the return, not multiple expansion.

## Final verdict
- **Final tier: C** (weighted IRR 14.57% on the corrected, pinned per-ADS base; preliminary Tier S rejected as a share-unit artifact)
- Confidence: **Low** (declared base_override pin, no engine revenue or debt series for this filer, BRL period-end FX translation, scenario spread 3.23x)
- One-liner: Brazil's telecom incumbent, moat 5/10 — a 10.44% OE yield and +7.6% BRL revenue prints, but at $12.26 the weighted IRR is only 14.57% (IV@15% $11.83/ADS on a pinned FY2025 base of $1.28/ADS); it clears the 15% hurdle only below ~$11.83.

## Engine 5.5 re-score (2026-10-19)
This is a dated addendum. The text above is the 2026-10-16 record and stays as written. Every figure in this section is copied from the final run's key_numbers.md or dcf_numbers.json (engine_release 5.5.0, as of 2026-10-19) unless the line names another source. The other sources are:
- the 2026-10-16 record and the saved output of the preliminary runs;
- the SEC enrichment files (statements.json, fundamentals.json) and the cited filings;
- sensitivity replays, each labelled "replay". A replay runs the engine's own scenario math (`dcf_engine.project_path` / `solve_irr`) with this run's inputs (probabilities, offsets, multipliers, moat, g_base, price) on an alternative base. Replays are not published figures, and the score rests only on key_numbers.md.

**Old vs new**

| | 2026-10-16 record (pre-5.4 engine output) | 2026-10-19 (engine 5.5.0, final) |
|---|---|---|
| Base OE/share | $1.2804 per ADS (declared pin 1.2803686126106435: FY2025 OE ÷ the year-end cover-page count × 2) | $1.27 (source: agent_supplied_ttm_override); 1.2692270927499132 in dcf_numbers.json. This is the re-declared pin and equals the engine's "Latest FY OE/share: $1.27" |
| Weighted IRR | 14.57% | 14.34% (base-case 14.16%) |
| Tier | C (no override) | C by numbers, C final (no tier override) |
| Price | $12.26 | $12.40 (nasdaq_quote_api) |
| Market cap (est) | $39.178B: the ADS price × the ordinary count | $19.987B (basis: diluted_latest; price × shares ÷ ads_ratio). In scope (market cap under $40B) |

The tier did not move. The weighted IRR fell from 14.57% to 14.34% for two reasons. The price rose from $12.26 to $12.40. The pin was also re-declared slightly lower, from 1.2803686126106435 to 1.2692270927499132, after the audit described below. The FY2025 owner's earnings total is unchanged (Latest FY OE total: $2.046B); only the share denominator changed.
- Scenario IV@15% is now $6.47 / $8.80 / $11.55 / $14.99 / $20.91.
- Weighted IV is $11.72 @15%, $15.57 @12% and $19.87 @10%.
- Upside at 15% is -5.5%.

**Runs (2026-10-19)**
1. **Preliminary, unpinned, before the shares override** (`dcf_engine.py VIV`). Exit 4, `data_gap` [shares, share_scale], no tier. Two gaps fired; the quotes are from that run's output:
   - `DATA_GAP:shares`. Diluted shares are missing for FY2025: "only a non-diluted count is filed (2025: 3,223,658,000 (WeightedAverageShares))".
   - `DATA_GAP:shares — SHARE_SCALE`. "base OE/share 2,068.56 is 165x the price 12.53 (limit 20x)". The scale breaks were FY2022 1,670,851,000 -> FY2023 1,658,604 and FY2024 1,643,132 -> FY2025 3,223,658,000.
   - Ruling 2 expects exactly this for VIV: the guard fires before the override is applied.
2. **Preliminary, unpinned, with the FY2025 shares_override declared.** Exit 4. `data_gap_uncovered` held only share_scale. The override covered the diluted-count gap in band (`override_checks.shares.out_of_band` false).
3. **`ttm.py VIV`** (for STALE_FY). Exit 3: "ocf: no annual (FY) fact; sbc: no annual (FY) fact; capex: no capex facts in companyfacts under any candidate tag". ttm.py reads us-gaap facts only and VIV files IFRS, so there is no ttm.json.
4. **Acceptance run with the carried 2026-10-16 pin** (`--base-oe-ps 1.2803686126106435`). Exit 0, Tier C, `SHARE_SCALE_SUSPECT`. make_score accepted it. This was ruling 2's acceptance check for VIV: the guard fires before the override, and the existing pin reproduces Tier C. The independent audit then asked for the declaration to be corrected, and run 5 superseded this one.
5. **Final run**: `dcf_engine.py VIV --moat 5 --probs 0.15,0.25,0.3,0.2,0.1 --offsets -0.05,-0.02,0.02,0.06,0.11 --mults 0.75,0.9,1.0,1.1,1.25 --base-oe-ps 1.2692270927499132`.
   - Exit 0, Tier C, `SHARE_SCALE_SUSPECT`, `data_gap_uncovered` empty.
   - `make_score.py VIV` accepted it.
   - `reprice.py VIV` wrote live.json with the tier unchanged.
   - `test_engine_math.py` replays the folder bit-for-bit.

**Audit follow-up (2026-10-19): the base_override re-declared**

The independent audit found four problems with the carried declaration.
- Its source quoted `base_oe_latest_per_share 0.6401843063053217` × 2. That figure came from the 2026-10-16 run, and this run does not print it: its `base_oe_latest_per_share` is 1.2692270927499132, already per ADS.
- Its reason quoted share counts this run's CSV no longer carries.
- It had no `kind`.
- It called FY2025 "the only clean per-share year". This PR's own statements.json shows that is not so: the restated post-transaction counts for FY2023/24 exist (see the alternatives below).

The carried pin also divided a full-year flow by a year-end count: FY2025 OE ÷ the cover-page count `shares_outstanding_dei_latest` 3,195,606,352. The CSV's FY2025 `shares_diluted`, the per-share history and the market cap all use the weighted-average 3,223,658,000.

The new declaration in judgment.json:
- **Value**: 1.2692270927499132, which is dcf_numbers.json `base_oe_latest_per_share` copied verbatim.
- **Construction** (exact in Python): `base_oe_total_latest_fy` 2,045,777,035.68 ÷ the CSV's FY2025 `shares_diluted` 3,223,658,000 × ads_ratio 2 = 1.2692270927499132.
- **Kind** "estimate". The anchor is that engine-printed figure itself, at a ratio of 1.0. NTNX and TEM declare their share-scale pins the same way.
- **Reason**: names the denominator choice and the alternatives, and drops the "only clean year" wording.
- **Result**: base and latest-FY OE/share now agree in key_numbers.md ("Base OE/share: $1.27", "Latest FY OE/share: $1.27"). The OE yield of 10.24% is now on the same share count as the $19.987B cap.

Alternatives. Only the first row is a published figure; the others are replays, not published figures.

| Base construction | Base per ADS | Weighted IRR | Bear IRR | Tier |
|---|---|---|---|---|
| Final pin: FY2025 OE ÷ FY2025 weighted diluted count × 2 | $1.27 (1.2692270927499132) | 14.34% | 11.32% | C |
| 2026-10-16 pin: FY2025 OE ÷ year-end cover-page count 3,195,606,352 × 2 | 1.2803686126106435 | replay 14.44% | replay 11.40% | C |
| 3-yr median on statements.json's restated basic counts: FY2023 3,317,207,000, FY2024 3,286,264,000, FY2025 3,223,658,000 | about 1.2323 | replay 14.01% | replay 11.06% | C |
| TTM to 2026-06-30 from the 2Q26 ITR 6-K, at the 2026-06-30 ECB rate (see STALE_FY) | about 1.2917 | replay 14.54% | replay 11.48% | C |
| Base at which the weighted IRR reaches 15.00% | about 1.3426 | replay 15.00% | — | B line |

Every construction is Tier C, and none comes within about 3.9% of the B line.

The median row would be the method-standard base if the filed FY2023/24 counts were on the right scale. Its denominators come from the enrichment file, not from this run's outputs, so bounded authority (c) does not allow it as a pin. It is lower than the final pin, so the published base is not the conservative end of the range. The bear end is still C on every row.

**Registry (make_score, final run)**
- The `base_override` event now records `kind` "estimate" and the share-scale rescue impact. Without the pin, `base_oe_without_override` is 2068.5608 (the engine's median on the defective count) and no IRR exists, because the run gaps. With the pin, `base_oe_with_override` is 1.2692 and `weighted_irr_with_override` is 0.1434. `unblocks_tier` is true.
- Its date, 2026-10-19, is correct, because the declaration changed today.
- The `shares` event is dated 2026-10-19 (new today). Its measured impact is base_used declared_pin, $1.27 → $1.27, 14.34% → 14.34%, and unblocks_tier true.
- The `ads_ratio` event also reads 2026-10-19, but its declaration (ratio 2, same source and reason) dates from 2026-10-16. The make_score that ran this morning replaced the ticker's entries before `keep_first_dates` existed, so the 2026-10-16 entry is no longer in the registry and a re-run cannot recover it. Restoring the date needs a registry edit, which a worker may not make. It is escalated to the main agent, together with the same re-dating at the other names re-scored before that fix.

**What engine 5.5 changed for this filer**
- **Share-scale guard (ruling 2). This is the change that matters for VIV.**
  - Test (a) fires: base OE/share 2,068.56 is 167x the price 12.40, against a 20x limit.
  - Test (b) does not fire. The cover-page (dei) count of 3,195,606,352 (dei_date=2025-12-31) agrees with the latest count of 3,223,658,000 (dei_ratio=1.00878).
  - Engine 5.4 scored a pinned base like this with no flag. Engine 5.5 refuses the unpinned base and lets only a qualifying declared pin carry it. This pin qualifies: it has no `basis`, its value equals the `--base-oe-ps` value, and it is within 20x the price. The record reads rescued_by_pin=True and pin_over_price=False, and the flag names "the declared base_override pin 1.26923".
- **Growth inputs dropped (ruling 2).** Two adjacent counts among the last four are more than 100x apart: FY2022 3,223,658,000 -> FY2023 1,658,604, and FY2024 1,643,132 -> FY2025 3,223,658,000.
  - The share-count CAGR (+0.0%/yr) and the OE/share CAGR (-97.7%/yr) therefore leave the blend, and the share adjustment is 0 ("Share count CAGR: — (growth adj 0.00%)").
  - The engine maps no IFRS revenue tag for this filer, so no revenue component exists either. The blend falls to its default: "Growth blend: 3.00% → g_base 3.00%".
  - On 2026-10-16 the -97.71% OE/share CAGR had floored g_base at -5.00%, and the -87.56% share CAGR had added a +5.00% adjustment. Both were unit artefacts.
- **Market cap (rulings 1 and 2).** $19.987B = price × 3,223,658,000 ÷ 2 (`market_cap_basis`: shares_source diluted_latest, ads_ratio 2.0).
  - No power-of-ten factor applies (`scale_factor` null): "the cover-page count agrees with it within 25%; no power-of-ten factor found in the dei count or the pin".
  - The old $39.178B multiplied the per-ADS price by the ordinary count. VIV was in scope on either figure, but the old one sat close to the $40B line. `in_scope_under_40b` stays true and now rests on a correct cap.
- **Leverage.** `leverage_unverifiable` is false.
  - The engine now reads the IFRS total-borrowings tag (`net_debt_basis` TOTAL:Borrowings). Net debt (latest) is $2.431B and Net debt / normalized OE is 1.19x. HIGH_NET_DEBT / BIG_NET_CASH were tested and neither fires.
  - The 2026-10-16 record had no net-debt figure.
  - The tagged total includes IFRS 16 leases and the deferred 5G licence payments. The 2Q26 ITR 6-K (accession 0001292814-26-004412, filed 2026-09-02), Note 20.a, breaks down the 12.31.2025 total of R$20,346,681 thousand: leases R$15,432,854 thousand, debentures R$3,066,965 thousand, loans and financing R$1,846,862 thousand, 5G licences R$1,033,964 thousand, plus smaller items. That total is the same figure as the engine's FY2025 debt_total converted back at 0.18256.
  - The FISTEL fees (R$7,341,381 thousand at 06.30.2026 in the same ITR, Note 17, enforceability suspended by court decision) are outside the figure.
- **Capex tags (rulings 3–5): no change.** Each base year reads the IFRS roll-up `PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities` with no intangible purchases filed: FY2023 $1.816B, FY2024 $1.508B, FY2025 $1.727B (intangibles $0.00 each year). No component was summed and no zero-guard period applies. VIV does not file `PurchaseOfIntangibleAssetsClassifiedAsInvestingActivities` (`capex_provenance` intangibles empty). CAPEX_COVERAGE_LOW did not fire: FY2025 capex was $1,726,571,605.92 against D&A of $2,728,250,394.24 in financials_history.csv.
  - **Completeness check (audit item).** The cash-flow line behind that tag is "Additions to PP&E, intangible assets and others". That is how the 2Q26 ITR's consolidated cash-flow statement labels it (6M26 R$4,672,144 thousand, 6M25 R$4,664,649 thousand). One tagged line therefore carries PP&E and intangible additions together.
  - The FY2025 investing section in the 20-F XBRL facts reconciles in full: −R$9,457,557 thousand on that line; +R$436,542 thousand of PP&E sale proceeds (`ProceedsFromSalesOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities`); and −R$1,064,753 thousand of payments for acquisitions of investments, net of cash acquired (`OtherCashPaymentsToAcquireEquityOrDebtInstrumentsOfOtherEntitiesClassifiedAsInvestingActivities`; the 4Q25 release coverage names the 2025 CyberCo acquisition, and the split by deal cannot be verified from these files). Untagged lines (judicial deposits, financial investments) make up the remaining +R$68,249 thousand, for an investing total of −R$10,017,519 thousand.
  - So the R$560M gap the audit found between the capex line and investing cash flow is an acquisition partly offset by asset-sale proceeds. Neither is recurring capex under the method, so no capex_override is warranted.
  - Spectrum is not paid through investing. The 5G licences are carried as a liability (R$1,033,964 thousand at 12.31.2025, current portion R$68,932 thousand) and paid in financing cash flow, so OE does not deduct those instalments. They are immaterial against the FY2025 OE. The secondary-coverage capex figure the earlier draft of this addendum relied on is no longer needed.
- **SBC tag (ruling 6): not applicable.** VIV files the IFRS tag `ExpenseFromSharebasedPaymentTransactionsWithEmployees`, not the us-gaap ShareBasedCompensation / Allocated pair. `sbc_provenance` is empty and SBC_TAG_RECONCILED did not fire. SBC stays negligible ($9,820,267.52 in FY2025, financials_history.csv).
- **USD-override branch (ruling 7): not triggered.** The one field override is a share count (`override_checks.shares.currency_basis` "shares"), which nothing converts. `fx_conversion.overrides_usd_verbatim` is empty.
- **Split basis: nothing adjusted.** `share_basis.split` and `share_basis.divergence` are null, and no split facts were found.
  - The April 2025 transaction (40-for-1 reverse split, then 1 grouped share into 80, a net doubling) is already inside the FY2025 count and the cover-page count.
  - VIV, an IFRS filer, files no split-ratio fact, so the engine cannot rescale the FY2023/24 counts. The pin carries the base, as ruling 2 intends.
- **5.4 change new to this folder: no silent swap.** The 2026-10-16 CSV showed 3,195,606,352 as FY2025 "diluted" shares. That figure is the year-end cover-page count, not a weighted average. Today's companyfacts carry only the basic WeightedAverageShares for FY2025, so the engine raises `DATA_GAP:shares` instead of substituting it, and the filing-sourced shares_override fills the gap.

**Override check**
- **shares_override (new, kind filing)**: value 3,223,658,000.
  - Source: Form 20-F FY2025 (accession 0002070979-26-000018), Note 24.h Earnings per share, p. F-89. The weighted-average count of 3,223,658 thousand is the denominator of basic and diluted results per common share of R$1.91, and the note states there are no potentially dilutive shares.
  - It checks against the XBRL facts in statements.json: WeightedAverageShares FY2025 3,223,658,000, with EPS basic and diluted both 1.91. The page reference was carried from the first attempt earlier today; this session confirmed the figure against the XBRL facts. The 2Q26 ITR's EPS note states the same policy: "The Company has no instruments which might potentially affect the dilution of earnings per share."
  - The engine applied it to every period with no diluted fact (`periods_filled` FY2016–FY2022 and FY2025). The FY2016–22 per-share history therefore sits on the post-transaction count. That history enters neither the base (pinned) nor the growth blend (share inputs dropped); see SHARES_FALLBACK.
  - Measured impact (key_numbers.md): base OE/share $1.27 → $1.27, +0.00%; weighted IRR 14.34% → 14.34% (+0.00pp); "Unblocks tier: YES". The override changes no number. It removes the FY2025 diluted-count gap, without which no tier could be published.
- **base_override (re-declared, kind estimate)**: value 1.2692270927499132. The construction and the reasons are under "Audit follow-up" above, and the registry event carries its rescue impact.
- **ads_ratio (unchanged)**: 2 ordinary shares per ADS, from the FY2025 20-F, as declared on 2026-10-16.

**New flags, each resolved by name**
- **DATA_GAP:shares — SHARE_SCALE** (preliminary runs only; new in 5.5): resolved by the declared base_override pin. The final run's `data_gap_uncovered` is empty.
- **SHARE_SCALE_SUSPECT** (final run; new in 5.5): resolved.
  - The defect is the share series. The FY2023/24 diluted counts are filed in thousands and on the pre-transaction basis; FY2025 is in units on the post-transaction basis. That puts the 3-yr median at $2,068.56, 167x the price.
  - The filing check, from statements.json: AdjustedWeightedAverageShares are 1,658,604 (FY2023) and 1,643,132 (FY2024). The restated basic WeightedAverageShares for the same years are 3,317,207,000 and 3,286,264,000, with EPS basic = diluted of R$1.52 and R$1.69. Doubled for the 2025 net 2-for-1 and scaled by 1,000, each diluted fact matches its restated basic count within a thousand shares.
  - Only the denominator is wrong: every OE leg is filed in BRL units. The pin (1.26923 in the flag) is the FY2025 figure on a units count, built as shown above.
  - The market cap uses the latest diluted count as filed (3,223,658,000 ÷ 2). It is reliable here because the cover-page count agrees within 25%. `scale_breaks` and `growth_inputs_dropped` are why the growth starts come from revenue and the latest prints (below), not from the blend.
- **DATA_GAP:shares** (FY2025 diluted count missing; preliminary run 1 only; a 5.4 flag new to this folder): resolved by the kind "filing" shares_override from the 20-F EPS note. The final run carries `OVERRIDE_APPLIED:shares` in its place.
- **OVERRIDE_APPLIED:shares** (new to this folder): one filing-sourced override. It fills only periods with no diluted fact (FY2016–22 and FY2025) and replaces no filed value. Its impact is +0.00% on the base and +0.00pp on the IRR.
- **SHARES_FALLBACK** (a 5.4 flag new to this folder): "no diluted share count filed for 2016, 2017, 2018, 2019, 2020, 2021, 2022".
  - Those years carry the override count (CSV `shares_tag` OVERRIDE). Their true weighted counts were about 1.67–1.69 billion on the pre-transaction basis (fundamentals.json shares_diluted, BASIC:WeightedAverageShares: FY2020 1,688,615,000; FY2022 1,670,851,000).
  - Their per-share history is therefore approximate. None of those years enters the base, the growth blend or the revenue CAGRs (no revenue tag), so the flag touches only the per-share history display.
- **TIER_BAND** (a 5.4 flag new to this folder): "bear-case tier C (11.3%) vs bull-case tier B (17.4%)".
  - The verdict is sized to the bear end, and the bear end is C (bear 11.32%), the same as the final tier.
  - Only the bull and super-bull scenarios (17.43%, 22.40%; 30% combined weight) clear 15%. The super bear (8.84%) is D.

**Flags carried from 2026-10-16** (new figures; resolutions restated where the audit changed them)
- **STALE_FY** (10 months; "Months since FY end: 9.6"): resolved, with an escalation. The 2026-10-16 resolution and this addendum's first draft said no trailing IFRS operating cash flow existed. That was wrong.
  - **What the filing prints.** The 2Q26 ITR 6-K (accession 0001292814-26-004412, filed 2026-09-02) carries full IFRS interim statements. Its consolidated cash-flow statement gives, for the six months to 06.30.2026 vs 06.30.2025:
    - net cash generated by operating activities: R$10,452,294 thousand vs R$10,963,371 thousand;
    - additions to PP&E, intangible assets and others: R$4,672,144 thousand vs R$4,664,649 thousand.
  - **TTM legs** (FY2025 as filed, BRL, statements.json, plus 6M26 less 6M25):
    - OCF: R$20,717,402 thousand + 10,452,294 − 10,963,371 = R$20,206,325 thousand.
    - Capex: R$9,457,557 thousand + 4,672,144 − 4,664,649 = R$9,465,052 thousand.
    - SBC: held at the FY2025 XBRL figure of R$53,792 thousand, because the ITR cash-flow statement prints no SBC line.
    - OE: R$10,687,481 thousand, against FY2025's R$11,206,053 thousand, 4.6% lower in BRL.
  - **Why OCF fell.** The decline is working capital and cash costs, not operations.
    - Cash generated from operations was R$12,125,344 thousand vs R$12,328,601 thousand.
    - Trade receivables absorbed R$928,809 thousand (vs R$472,949 thousand) and inventories R$308,056 thousand (vs a release of R$65,632 thousand). Trade payables absorbed R$73,177 thousand (vs a release of R$350,256 thousand).
    - Income taxes paid were R$525,592 thousand (vs R$348,874 thousand) and interest paid R$1,147,458 thousand (vs R$1,016,356 thousand).
  - **Per ADS.** On the ITR's 6M26 weighted count of 3,195,606 thousand, TTM OE is about R$6.69 per ADS, against about R$6.95 for FY2025. In USD the result depends on the rate.
    - At the FY2025 rate (0.18256) it is about $1.22, replay 13.91%.
    - At the 2026-06-30 ECB reference rate (0.19311, frankfurter.app, the engine's FX source) it is about $1.29, replay 14.54%.
    - Both are Tier C. The USD figure rises only because the real strengthened; the BRL economics weakened.
  - **Why it is not the base.** ttm.py cannot read IFRS facts, and a base built from 6-K figures is outside bounded authority (c), which allows only this run's printed figures. So the FY2025 pin stands, and the TTM pin question is escalated to the main agent with these figures.
  - **Tier risk.** None upward: the TTM base sits about 3.9% below the B line on the replay, and below it at today's rate too. The 2026-10-16 claim that the interim prints "run ahead of FY2025" holds for revenue and net income, but not for IFRS operating cash flow.
- **BASE_DIVERGENCE** (latest FY OE/share 1.27 vs 3-yr median 2068.56): the median is the distorted figure, for the share-unit reason under SHARE_SCALE_SUSPECT. The OE totals stay stable: FY2023 $2,043,840,075.89, FY2024 $1,699,459,237.38, FY2025 $2,045,777,035.68 (financials_history.csv `oe_conservative`). FY2025 is in line with FY2023 and is not a peak. On the restated counts the three years sit within the range shown in the alternatives table.
- **OE_VOLATILE**: an artefact of the same per-share break; the OE totals above are stable. The bear-side weight stays widened (15% super bear) for Brazil and FX risk.
- **NI_OCF_DIVERGENCE** (2023, 2024): structural, as resolved above. Network D&A (FY2025 $2,728,250,394.24) is added back to OCF, and the conservative OE deducts the full capex that replaces it.
- **FX_CONVERTED**: BRL at ECB period-end rates (0.16169 at 2024-12-31 and 0.18256 at 2025-12-31 in `fx_conversion`). The TTM check above shows the size of the risk: the real's move since year-end changes the USD base more than six months of operations did.
- **ADS_RATIO_APPLIED**: per-share figures are ×2.0 ordinary shares per ADS, from the FY2025 20-F (unchanged). Ruling 1 now also applies the ratio to the market cap.
- **BUYBACK_TAILWIND no longer fires.** Its "87.6%/yr shrink" was the unit break, and 5.5 drops the share-count CAGR. A real but modest buyback continues: statements.json shows share repurchases of R$1,746,480,000 in FY2025, and the ITR's 6M26 weighted count (3,195,606 thousand) is below FY2025's. No growth credit is taken for it.

**Growth recalibration (re-verified 2026-10-19)**
- The scenario starts are unchanged from 2026-10-16: -2.0% / 1.0% / 5.0% / 9.0% / 14.0%. Only the offsets changed, because g_base moved from the -5.00% artefact floor to the 3.00% default. The new offsets are -0.05 / -0.02 / +0.02 / +0.06 / +0.11, with the same probabilities (15/25/30/20/10), moat 5 and default multipliers.
- Base +5%: FY2025 BRL net operating revenue rose 6.7% (R$59,595.0M vs R$55,845.0M, FY2025 20-F MD&A) against IPCA inflation of 4.3%.
- Bull +9%: the 2Q26 BRL prints (revenue +7.6%, EBITDA +10.9%) hold in USD.
- Super bull +14%: a strong real, buyback shrink and margin expansion together.
- Bear +1% and super bear -2%: BRL depreciation, price competition and the working-capital drag seen in 6M26 absorb the nominal growth.
- The TTM OE above is 4.6% below FY2025 in BRL, a reason the verdict is sized to the bear end. The releases consulted give no revenue or OE guidance. The stated commitment is to distribute at least 100% of FY26 net income, so no start sits above a quoted guidance figure.

**Moat evidence (WORKER_SPEC step 5; source fundamentals.json / statements.json, not engine output)**
- `roic_proxy` FY2020–25 reads about 6.8%, 7.0%, 6.5%, 8.5%, 8.5% and 10.2%: single-digit returns rising to about 10%, below Brazil's policy rate since 2022.
- fundamentals.json leaves gross margin null, because no IFRS revenue tag is mapped. statements.json shows gross profit growing faster than cost of revenue: R$22,684,751,000 vs R$29,415,400,000 in FY2023, and R$26,669,632,000 vs R$32,925,368,000 in FY2025.
- This is a scale and position franchise without excess returns on capital. The moat stays 5/10, moderate and narrow.
- Minority holders: VIV has no listed majority-owned subsidiary. Noncontrolling interests are R$280,983,000 at FY2025 (statements.json), immaterial to the consolidated OE.

**Method limit, stated with figures (not a defect, no override)**
- Under IFRS 16, lease principal payments sit in financing cash flow, so OCF − capex − SBC does not deduct them. Ruling 5 rejected a lease leg in the engine.
- The size of the omission, from the 2Q26 ITR:
  - Lease liabilities were R$15,432,854 thousand at 12.31.2025 (Note 20.a.1).
  - The 6M26 financing line "Loan payments, financing, debentures, leases and other creditors", which covers lease principal together with debt repayments, was R$1,940,054 thousand (6M25 R$1,906,432 thousand).
- The company's own 2025 free cash flow was R$9,153 million, per secondary coverage of the 4Q25 release. Check the release for its exact lease treatment.
- That is below the bear scenario's 0.90 OE multiplier. On that basis the bear (11.32%) and super-bear (8.84%) IRRs are the relevant range, not the 14.34% headline.
- This is a further reason the verdict is sized to the bear end, and the bear end is still Tier C. It is not converted into a tier override: no engine figure measures the IRR on a lease-deducted basis, and the bear-end tier already equals the final tier.

**Why the tier is C.** The weighted IRR of 14.34% sits in the C band (10–15%), and the bear end is also C (11.32%).
- At $12.40 the weighted path clears 15% only at $11.72 (IV@15%), 20% at $8.26 and 25% at $6.36.
- Every alternative base above is C, the TTM figure included, so no tier override is taken. Scope is in ($19.987B).
- Confidence stays **low**:
  - the base is carried by a declared pin over mis-scaled filed counts;
  - the FY2025 count rests on a filing override;
  - the TTM question is escalated;
  - translation uses BRL period-end FX;
  - IFRS 16 leases are not deducted.
- score.json has `alert_eligible` false and `exit_alert_eligible` false ("tier exists only because of a judgment override").

**judgment.json changes (2026-10-19).**
- The shares_override was added.
- The base_override was re-declared: value 1.2692270927499132, a corrected source and reason, and `kind` "estimate".
- The `one_liner` was updated to the final figures ($12.40, 14.34%, bear 11.32% / bull 17.43%, IV@15% $11.72, base $1.27/ADS).
- Moat, probabilities, confidence and ads_ratio are unchanged.

**Data section (enrichment, 2026-10-19).** All six steps ran without failure.
- fundamentals.py: written. It notes that no dividends-per-share facts are filed and that a 20-F filer has no quarterly facts.
- prices.py: ten years of closes, latest 2026-10-16.
- segments.py: no dimensioned segment facts, so segments.json has no tables.
- statements.py: written, as filed in BRL. It blanked an implausible FY2023 shares_outstanding cell (1.653e+12) and logged a power-of-ten disagreement on NumberOfSharesOutstanding for 2022 (kept 1.66356e+09). These are the same unit slips described above.
- profile.py: About text from 20-F Item 4.B; street.json written.
- reprice.py: re-run after the final make_score; live.json written, tier unchanged vs final.

**Research used (2026-10-19).**
- [2Q26 ITR Form 6-K (SEC EDGAR)](https://www.sec.gov/Archives/edgar/data/1066119/000129281426004412/vivitr2q26_6k.htm), accession 0001292814-26-004412, filed 2026-09-02. Used for the interim cash-flow statement, the EPS note (weighted count 3,195,606 thousand), Note 20.a borrowings, leases and 5G licences, and Note 17 FISTEL.
- [Q2 2026 earnings release Form 6-K](https://www.sec.gov/Archives/edgar/data/0001066119/000129281426003922/vivpr2q26_6k.htm): revenue +7.6%, EBITDA +10.9%, first-half net income +17.9%, the 100%-of-FY26-net-income distribution commitment.
- [FY2025 Form 20-F (SEC EDGAR)](https://www.sec.gov/Archives/edgar/data/1066119/000207097926000018/viv-20251231.htm) and its XBRL facts (companyfacts): FY2025 investing lines, SBC, revenue R$59,595.0M (+6.7%).
- ECB reference rates via frankfurter.app: BRL→USD 0.19311 on 2026-06-30.
- 4Q25 release coverage ([Barchart copy](https://www.barchart.com/story/news/370738/4q25-results-telefonica-brasil-s-a)): 2025 free cash flow of R$9,153M, as reported there.
