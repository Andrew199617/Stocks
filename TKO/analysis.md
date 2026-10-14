# TKO — TKO Group Holdings, Inc. (NYSE: TKO)
Run date: 2026-10-13. **Status: BLOCKED — engine v5 DATA_GAP (capex). No tier emitted, no score.json** (make_score.py refuses on a data gap by design). This file documents the block and everything a future re-run needs.

## What it is
Premium sports/entertainment holding company formed in September 2023 by combining UFC and WWE. On February 28, 2025 it closed the acquisition of IMG (sports marketing/media rights, excluding licensing/models/tennis-golf representation and the full events portfolio), On Location (premium event hospitality), and PBR from Endeavor in an all-equity transaction valued at $3.25B (plus $50M of purchase-price adjustments settled in equity); Endeavor received ~26.54M TKO OpCo common units and an equal number of Class B shares. Asset-light model: venues are rented, PPE net is only ~$0.64B against $4.74B of FY2025 revenue.

## Engine v5 preliminary run (2026-10-13)
- Price $173.86 (Nasdaq quote API); diluted shares 194.0M; market cap ~$33.7B (in scope, < $40B); net debt $2.93B.
- FY2025 (10-K filed 2026-02-25): revenue $4,735.2M, operating income $835.0M, net income $195.4M, OCF $1,285.7M, SBC $117.6M, D&A $485.0M.
- Engine result: exit 4, `data_gap: ["capex"]`, `tier_by_numbers: null`. The history CSV the engine wrote carries capex = 0 / `capex_assumed_zero` for every year — that zero is the gap, not a filing fact.

## The data gap — capex exists, but only under a custom extension tag
- EDGAR companyfacts for CIK 1973266 (namespaces: us-gaap, dei, ecd) contains **no** standard capex tag at all: none of `PaymentsToAcquirePropertyPlantAndEquipment`, `PaymentsForConstructionInProcess`, `PaymentsToAcquireOtherPropertyPlantAndEquipment`, `PaymentsToAcquireProductiveAssets`, or `PaymentsToAcquireOtherProductiveAssets` is present. The engine's `period_series()` reads only the us-gaap namespace, so it extracts no capex for FY2023–2025 and the v5 gate correctly refuses a tier.
- The filing itself discloses capex on the cash-flow line "Purchases of property, buildings and equipment and other assets", tagged in the inline XBRL with TKO's own extension tag `tko:PaymentsToAcquirePropertyPlantAndEquipmentAndOther`. Verified directly in the filings (values in $M):
  - FY2023: $93.753M · FY2024: $118.818M · FY2025: $126.953M (FY2025 10-K, accession 0001193125-26-071651)
  - H1 2026: $44.444M vs H1 2025: $48.631M (Q2 2026 10-Q, accession 0001193125-26-330592)
- Magnitude cross-check: total FY2025 net cash used in investing was only $146.9M, consistent with capex of ~$127M plus ~$30.7M of investments in affiliates and ~$8.7M of acquisitions, partly offset by asset-sale proceeds. Capex is ~2.7% of revenue and ~10% of OCF — small, but not zero, and v5's whole point is that a missing value is never silently treated as zero.
- Corrected conservative owner's earnings **for the future re-run's reference only** (OCF − real capex − SBC; NOT a scored base, no DCF was run): FY2025: $1,285.7M − $127.0M − $117.6M = $1,041.2M ≈ $5.37/share on 194.0M diluted shares. FY2024: $586.1M − $118.8M − $103.5M = $363.8M ≈ $2.12/share. FY2023: $266.2M − $93.8M − $64.5M = $107.9M ≈ $1.30/share — per-share history straddles the mergers (below), so these are not a clean growth series.

## Other fragility flags (context for the re-run)
- **STALE_FY** — FY2025 ended 2025-12-31, ~9 months before this run. Q2 2026 10-Q is available (H1 2026 OCF $1,068.5M vs H1 2025 $559.0M per the 10-Q cash-flow statement); a TTM base should be computed with `ttm.py` on the re-run — noting ttm.py's capex policy will hit the same custom-tag problem and must be handled then, not hand-waved.
- **DILUTION (share count +53.0%/yr)** — merger issuance, not compensation dilution: share count stepped 82.8M (2023) → 171.9M (2024) → 194.0M (2025) on the WWE combination accounting and the February 2025 Endeavor-asset deal (~26.54M units/shares). SBC is modest ($117.6M in FY2025, ~9% of OCF). The engine's −5pp dilution adjustment to growth would be wrong-headed on a re-run; the growth inputs need to be set on the post-merger combined basis instead.
- **BASIS_BREAK_SUSPECT** — confirmed and structural: revenue +183% (2023) and +51% (2024) are the UFC/WWE combination, not organic growth; FY2025 revenue actually fell −3.1% despite consolidating IMG/On Location/PBR for ~10 months. Every historical CAGR the engine blends (rev CAGR 5y 46%, 3y 61%) is a merger artifact and must not be used on the re-run.
- **NI_OCF_DIVERGENCE (2023, 2024, 2025)** — net income runs far below OCF in all three years, driven substantially by merger purchase-accounting amortization inside the $224M/$458M/$485M D&A lines (non-cash), plus SBC; the residual gap needs the forensic pass on the re-run before any OE base is trusted.

## Verdict
- **Blocked (blocked_no_data), not scored.** Root cause is engine coverage, not disclosure: TKO is a US GAAP filer with complete audited financials, but its capex lives only in an extension taxonomy that neither EDGAR companyfacts nor the engine reads.
- Revisit when the engine merges extension-taxonomy tags for capex (the filing-verified tag above is the wiring candidate, values already confirmed against two filings), or if TKO adopts a standard us-gaap capex tag. Do NOT score F — owner's earnings are clearly positive on the corrected figures above.
