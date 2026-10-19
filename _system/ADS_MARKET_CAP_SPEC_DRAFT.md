# SPEC — ADS-adjusted market cap for the DCF engine (v5.4.0)

Status: IMPLEMENTED 2026-10-18 — Andrew approved the fix the same day, from
Codex's PR #3 review (prepared as a draft earlier that day). `market_cap_est()`
in `dcf_engine.py` now computes price × shares ÷ ads_ratio; `reprice.py`'s live
cap uses the same helper on the recorded ratio; `make_score.py` follows via
`market_cap_est` and needed no change. Tests: `test_market_cap_ads_ratio`
(engine) and `test_ads_ratio_divides_live_market_cap` (reprice). The eight
cases below are the pre-fix record; the affected names are re-scored as
separate data PRs, and TLK completes from its saved workup.

This consolidates eight verified instances of one defect: when an ads_ratio
applies, the engine scales per-share figures to the ADS basis but computes
market cap from the unscaled ordinary share count. TLK (2026-10-17) is the
first case where the defect *blocks* a name instead of merely polluting its
recorded scope flag.

## Root cause (verified in code, 2026-10-18)

`dcf_engine.py` line 950 (pre-fix):

```python
mktcap = (price * shares) if (price and shares) else (...)
```

`price` is the per-ADS traded price and `shares` is the ordinary share count
from EDGAR. `load_ads_ratio` (line 328) is applied to the per-share OE history
(lines 968–973) but never to `mktcap`. The correct traded cap when an
ads_ratio applies is:

```
market_cap_est = price * shares / ads_ratio
```

(ordinary shares ÷ shares-per-ADS = ADS count; × per-ADS price = traded cap.
For a ratio below 1, e.g. FMS at 0.5, the same formula corrects an
*under*statement.)

`make_score.py` (lines ~769–776) computes scope from `market_cap_est` and
refuses a `judgment.json` `in_scope_under_40b` claim that contradicts it —
which is why a worker cannot fix this from judgment.json without falsifying
the scope field.

## The eight verified cases

1. **TLK (Telkom Indonesia) — BLOCKED, not scored.** ads_ratio 100.
   Engine cap $1,092.66B = $11.03 × 99,062,216,600 ordinary shares; true cap
   ~$10.9B (990,622,166 ADS × $11.03; MarketBeat $10.64B). The worker
   completed everything else — filing-sourced overrides (sbc $0, shares,
   ads_ratio 100; measured impact zero), final run Tier B by numbers,
   weighted IRR 19.11%, IV@15% $14.39, moat 6/10, confidence low — and
   correctly refused to set `in_scope_under_40b: false` to satisfy the
   scorer. Queue status `blocked_no_data`, NEEDS_MAIN_AGENT: market_cap/scope
   (queue_pos 406, blocked 2026-10-17). Unblock is exactly the fix below,
   then: re-run make_score.py TLK, enrichment, queue.py done, build_site.py.
   (Detail: `~/workspace/stocks/TLK/analysis.md`.)

2. **JD — scored, scope falsified by the artifact.** ads_ratio 2.
   Engine cap $79.22B vs the $36.409B universe-build cap that admitted it;
   score.json records `in_scope_under_40b: false` on the engine basis only.

3. **CHT — scored, scope falsified.** ads_ratio 10. Engine cap $361.62B
   vs ~$34.5B real — a name near the scope line recorded as 9x over it.

4. **VOD — scored, scope falsified, and genuinely borderline.** ads_ratio 10.
   Engine cap $405.57B; ADS-equivalent cap is roughly a tenth — i.e. right
   at the $40B scope line. This is the case where the correct number decides
   whether the name belongs in the sweep at all, not just what its record says.

5. **PAC — scored, scope falsified.** ads_ratio 10. Engine cap $103.03B
   vs ~$10.3B real (50,527,746 ADS × $203.90).

6. **TS (Tenaris) — scored, scope falsified.** ads_ratio 2. Engine cap
   $58.858B, 2x the traded cap.

7. **WF (Woori Financial) — scored, scope falsified.** ads_ratio 3.
   Engine cap $52.03B vs actual KRX cap KRW 23.72T (genuinely in scope).
   (Also SHARE_BASIS_SPEC_DRAFT.md case 4 — the same computation viewed
   from the share-basis side; the fix here closes that half of it.)

8. **FMS — scored, direction reversed, non-blocking.** ads_ratio 0.5
   (1 ADS = 1/2 ordinary share). Engine cap $6.456B *understates* the true
   ~$12.9B cap 2x. In scope on either basis, so nothing turned on it —
   included because it proves the fix must divide by the ratio, not
   special-case ratios > 1.

## The fix as implemented (2026-10-18)

1. `dcf_engine.py`: `market_cap_est(price, shares, ads_ratio, fallback)`
   computes `price * shares / ads_ratio["ratio"]` when price and shares are
   present (ratio defaults to 1 — bit-identical to the old formula);
   `reprice.py`'s live cap uses the same helper on the split-adjusted count.
2. Regression checks shipped as tests: `test_market_cap_ads_ratio` covers
   ratio 100 (TLK shape), ratio 2 (JD shape), ratio 0.5 (FMS shape), the
   ratio-1 / no-ratio identity and the fallback; an end-to-end A/B against
   the old engine showed APP bit-identical and JD differing only in
   `market_cap_est` and its content hash.
3. Re-scores: Andrew's ruling names PAC, EMBJ, FUTU, HTHT, LTM, TX and FMS —
   their `market_cap_est` and recorded `in_scope_under_40b` change; tiers do
   not (per-share figures are already ADS-scaled and unaffected). The other
   pre-fix cases above (JD, CHT, VOD, TS, WF) correct on their next re-score;
   VOD's corrected cap lands near the $40B line — its scope call should be
   made on the corrected number explicitly, not by default.
4. TLK completes from its saved workup (make_score + enrichment + queue done)
   and its Tier B record reaches the ranking.

## What this does NOT fix

- Share-count basis defects (thousands scaling, splits post-dating filings,
  different share classes) — those are SHARE_BASIS_SPEC_DRAFT.md, a separate
  decision.
- Net-debt / normalized-OE diagnostics that inherit ADS scaling
  inconsistently (noted on VOD) — flag for a follow-up check during
  implementation, not assumed fixed by the one-line cap change.
