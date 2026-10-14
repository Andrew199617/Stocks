# Alcon Inc. (ALC) — BLOCKED: IFRS filer, engine cannot read modern filings

**Status:** Blocked via queue.py as DATA_GAP (IFRS) on 2026-10-14. No tier scored — the preliminary engine output must not be used.

## What happened

- Preliminary engine run (CIK 1167379, correct CIK — same registrant, re-registered for the 2019 Novartis spin-off) returned only fiscal years 2007–2010 in `financials_history.csv`, with `latest_period_end: 2010-12-31` and flag `STALE_FY: latest fiscal year ended 189 months ago`.
- On that stale slice it computed base OE/share $6.5372, weighted IRR 19.80%, Tier B — a spurious result on 15-year-old data from the pre-acquisition Alcon (acquired by Novartis in 2011, spun off again in 2019).
- Root cause verified directly against EDGAR companyfacts for CIK 1167379: the modern company files under IFRS. Its companyfacts payload carries an `ifrs-full` namespace (270 tags, including `Revenue`, `ProfitLoss`); the engine and `ttm.py` read only `us-gaap` tags, so the only usable facts they find are the 2007–2010 US-GAAP-era filings.
- `ttm.py ALC` exits 3: "ocf: no annual (FY) fact; sbc: no annual (FY) fact; shares_diluted: no annual (FY) fact; capex: no capex facts in companyfacts under any candidate tag" — confirming no in-bounds override can fix this; the gap is the entire modern filing history, not a single missing period.
- Other flags on the stale run (BUYBACK_TAILWIND −99%/yr share CAGR, OE_VOLATILE, WIDE_SCENARIO_SPREAD, ADS_RATIO_MISSING) are artifacts of the truncated 2007–2010 slice (including a corrupted 2007 share count of 302,162,019,000,000 in the CSV) and are not resolvable — they disappear only when the engine can read the IFRS filings.

## Business context (from research, for the eventual re-run)

- Alcon is the global eye-care leader: Surgical (IOLs incl. PanOptix/Vivity, UNITY/CENTURION equipment, consumables) and Vision Care (contact lenses, Systane/TRYPTYR ocular health).
- Q2 2026: sales $2.8B, +8% reported / +7% cc; Surgical $1.6B, Vision Care $1.2B; core diluted EPS $0.84 (+9% YoY); reported EPS $0.00 after a ~$402M non-cash PowerVision discontinuation charge; FY26 guidance raised to 5–7% cc sales growth, core EPS growth 12–15% cc.
- Moat-relevant: #1 in premium IOLs / phaco ecosystem with high surgeon switching costs vs J&J Vision, Bausch + Lomb, Zeiss — to be scored properly once IFRS data is readable.

## Verdict

Not scorable under engine v5. Needs a main-agent decision: IFRS tag support in the engine (the known P1/P2 backlog item) or an explicit IFRS go/no-go — the same class of block as JD (non-USD/foreign filer). No bounded override under step 8 covers a whole-namespace gap.
