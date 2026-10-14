# DCF Brittleness Audit — 2026-10-12 (engine v3 → v4)

Andrew's brief: the sweep exists to tip him to stocks that look interesting against a 15-25%
hurdle. A brittle model is worse than no model there — it manufactures false tips and buries
real ones. Everything below was found by reading the engine end-to-end and stress-testing it
on MSFT, KO, XOM, NVDA, INTC, and APP. Fixes are in `dcf_engine.py` v4 unless marked accepted.

## The core problem, in one line
The model's output for a single stock swung from **Tier C (11.2%) to Tier A (20.6%)** across
four defensible-looking runs of APP in one day. The business didn't change — the *inputs*
(base year, growth cap, base definition) did. Most brittleness = input choices masquerading
as conclusions. v4's job is to make those choices explicit, normalized, and flagged.

## Fixed in v4

1. **Single-year base (biggest flaw).** v3 built the entire DCF on the latest fiscal year's
   owner's earnings. One cyclical peak/trough, one-off, or working-capital spike became the
   foundation. *Fix:* base = median of the last 3 fiscal years' OE/share. Cyclicals get a
   through-cycle base (XOM norm $7.15 vs trough $5.48); one-off years stop dominating.
   *Known cost, handled by flag:* for genuine inflections the median lags reality (APP median
   $4.96 vs latest $11.00) — BASE_DIVERGENCE fires and the agent must resolve it explicitly,
   usually with the TTM override (fix 2), never silently.

2. **Stale fiscal year.** FY ends can be 9+ months old at run time (APP, KO, NVDA all flagged).
   v3 priced today's stock off last year's earning power with no warning. *Fix:* STALE_FY flag
   (>7 months) and a `--base-oe-ps` override so the agent can substitute a TTM base computed
   from 10-Q YTD figures (APP TTM OE/share $12.57, built line-by-line from EDGAR, not estimated).

3. **Growth from one endpoint CAGR.** v3 used 5-yr revenue CAGR only — endpoint-sensitive,
   corrupted by restatement basis breaks, and blind to deceleration. *Fix:* blended growth =
   median of four independent signals (rev CAGR 5y, rev CAGR 3y, latest rev YoY, OE/share CAGR),
   so no single artifact runs the model. The APP cap incident (20% cap → super-bull 32% vs
   +53-70% actuals) stays as the standing warning: caps now 35%/50% and the cron requires a
   growth-start sanity check against actual prints, with written reasons for deviations.

4. **Buybacks/dilution ignored.** v3 grew OE/share at the total-OE growth rate. A company
   shrinking its count 3%/yr (APP: −2.7%/yr) compounds per-share value faster than the
   business; a diluter (INTC: +3.2%/yr) slower. *Fix:* share-count CAGR over the available
   window adjusts the growth rate, clamped ±5pp, reported as its own line.

5. **Fade shape was wrong twice.** It faded from year 1 (double-penalizing current growers
   whose near-term prints are the most visible), and below-terminal growers stayed depressed
   forever (a trough cyclical could never recover). *Fix:* growth holds for 2 years, then
   converges linearly to terminal over the moat CAP — in either direction.

6. **EDGAR tag switching truncated history.** The fetcher used only the first tag with any
   data; filers that changed tags lost years silently. *Fix:* candidate tags merged per period.

7. **Share count can be missing entirely.** XOM stopped tagging weighted diluted shares in
   XBRL after 2013 — v3 would have produced per-share nonsense or a crash. *Fix:* fallbacks to
   basic shares, shares outstanding, and dei EntityCommonStockSharesOutstanding.

8. **Wrong-entity CIK produced a fake verdict.** SEC's ticker map now points XOM at a new
   holding-company CIK with zero filing history; v3 scored that emptiness as Tier F.
   *Fix:* <2 usable years is a hard `NO_DATA` exit (exit 3), never a tier; the sweep marks it
   blocked and the agent hunts the operating parent's CIK and reruns with `--cik`
   (XOM verified: CIK 34088 restores full history).

9. **Earnings vs cash flow divergence was invisible.** KO 2024-25: net income rose while OCF
   halved on a one-off IRS tax deposit — OE (built on OCF) looked permanently impaired.
   *Fix:* NI_OCF_DIVERGENCE flag for gaps >40% that D&A can't explain (refined after XOM
   false-positived — asset-heavy D&A gaps are structural). The flag names the years; the agent
   must find the one-off before trusting the base.

10. **No uncertainty reporting.** v3 emitted a tier and nothing about how much to trust it.
    *Fix:* every run emits diagnostics (OE yield, terminal-value share of IV, scenario spread,
    net debt / normalized OE, months since FY end) and a fragility_flags list the agent must
    address in analysis.md: LOW_OE_YIELD, HIGH_TV_SHARE, WIDE_SCENARIO_SPREAD, HIGH_NET_DEBT,
    BIG_NET_CASH, DILUTION / BUYBACK_TAILWIND, BASIS_BREAK_SUSPECT, OE_VOLATILE, THIN_HISTORY,
    SECTOR_MODEL_MISMATCH, STALE_FY, BASE_DIVERGENCE, NI_OCF_DIVERGENCE, CIK_FALLBACK.

## Accepted limitations (documented, not fixed — know them when reading a tip)
- **It's a screening DCF.** One standardized model for 2,617 companies buys comparability at
  the cost of per-company nuance. A Tier S/A/B tip means "worth your deep look," not "buy."
- **OE growth ≈ revenue growth.** The blend uses revenue signals for OE growth; margin
  expansion/contraction is handled only through scenario multipliers and agent judgment.
- **SBC is subtracted AND diluted shares are used** — mildly double-counts dilution; it is the
  conservative direction and it is consistent across all companies.
- **OE is a levered (post-interest) flow discounted at equity hurdles** — consistent for the
  IRR question being asked, but heavy leverage still distorts it; HIGH_NET_DEBT exists for this.
- **Probability-weighted IRR is the IRR of the expected cash-flow path**, not the average of
  scenario IRRs. It is the right number for ranking, slightly optimistic vs true expected IRR
  when the spread is wide — another reason WIDE_SCENARIO_SPREAD caps confidence.
- **Banks/insurers/REITs fit poorly** (flagged, confidence low). A future v5 could route
  financials to a dividend/ROE model; until then their tiers are soft.
- **Terminal growth is 2.5% for everyone** (parameter `--gterm`). Declining industries should
  get less; the agent can set it with a written reason.

## What this means for the tips you get
- Trust the *flags* as much as the tier. A Tier B with no flags is a better tip than a Tier A
  carrying STALE_FY + WIDE_SCENARIO_SPREAD + LOW_OE_YIELD.
- When a company's method range spans multiple tiers (APP spanned C→A), the writeup now says
  so and sizes the verdict to the conservative end.
- The daily HTML ranks by weighted IRR; read the confidence column with it.
