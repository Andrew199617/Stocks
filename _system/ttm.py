#!/usr/bin/env python3
"""TTM owner's-earnings calculator (v5, 2026-10-13 — agents never hand-compute TTM again).

Usage: python3 ttm.py <TICKER> [--cik N]

Computes trailing-twelve-month OCF, capex, SBC and diluted shares from EDGAR
companyfacts 10-Q YTD facts: TTM = FY - prior-year YTD + current YTD, with the
YTD periods matched by fiscal-year start. Prints JSON with every input value
(FY, prior YTD, current YTD, tag used) so the arithmetic is auditable.

Capex policy (round-2, 2026-10-14): if a filer has NO capex facts in
companyfacts at all (any candidate tag, any period), that is a data gap —
exit 3 — UNLESS a judgment capex_override fills it. The old zero-fill-with-
warning path is gone: ttm.py holds the same standard as the engine's
DATA_GAP gate. If capex facts exist but any of the three TTM inputs is
missing (e.g. APP FY25), that is likewise a data gap: exit 3. Missing
OCF/SBC/shares facts also exit 3. Exit 2 = no CIK found.

On success the full output is also written to <TICKER>/ttm.json — the
machine-readable provenance for the engine's --ttm base pin (make_score.py
refuses a pinned base that differs from ttm.json). Day counts are
INCLUSIVE (end - start + 1) so a filled annual leg is exactly the override
value, matching the engine's annual fill. Leg matching tolerates a filed
fact whose start date is within a few days of the expected period start
(match on end date + nearest start): a real filed fact is never replaced
by an override fill. DCF_TTM_NO_WRITE=1 suppresses the ttm.json write
(make_score.py's measurement runs must not clobber the worker's file).

Overrides (v5.1, 2026-10-13): judgment.json may carry capex_override /
sbc_override / shares_override ({value, source, reason, kind}). For a field
with an override, the TTM legs are assembled on the OCF anchor timeline: a
leg uses the filer's own fact when one exists for the anchor period,
otherwise it is filled with the override value prorated by days in the leg
period (value x days/365) — so a fully untagged year nets to exactly the
override value in the TTM. Filled legs are listed in overrides_used, and an
override-filled capex leg raises no CAPEX_NOT_FILED warning. Share counts
are averages, not flows: a shares override is used unprorated as the TTM
denominator. DCF_NO_OVERRIDES=1 disables override loading.

v5.5 (2026-10-19, engine release 5.5.0 — the same rules as dcf_engine.py,
imported from it so the two never drift; us-gaap only, USD only, per exact
leg period):
- Capex legs: per exact (start, end) period, dcf_engine.capex_for_period over
  the shared lists (CAPEX_ROLLUP_TAGS / CAPEX_COMPONENT_TAGS /
  CAPEX_INTANGIBLE_TAGS, us-gaap entries only): the PP&E roll-up is
  authoritative, else the additive components (E&P, other PP&E, construction
  in process, productive assets, capital improvements) are summed with the
  zero-guard; intangible purchases filed for the same exact period are added
  on top, never on an OVERRIDE-filled leg. A leg with no PP&E value is
  "missing" exactly as before (override fill or hard block). The *_tag leg
  fields carry the '+'-joined provenance; ttm.json gains capex_components
  {leg: capex_for_period result}.
- SBC legs: where ShareBasedCompensation and
  AllocatedShareBasedCompensationExpense report the same exact period and
  Allocated is larger, Allocated is used (dcf_engine.reconcile_sbc);
  ttm.json sbc_reconciled_legs lists the legs it changed.
- Split basis: a split confirmed by the shared helpers (a ratio filed after
  the FY end, confirmed by a post-event dei count against the FY diluted
  leg) rescales ytd_current by the confirmed ratio only when ytd_current is
  still on the pre-split basis (ytd_current / dei within +-15% of
  1 / ratio); recorded as split_adjustment.
- Overrides pass an explicit `currency` declaration through (validated by
  make_score; ttm.py reads USD facts only, so nothing is converted here).
- [ADDITION — ECHO; not in the rulings, it stops an approved change from
  producing a wrong number silently] Cumulative duplicates: an intangible
  purchase fact on a leg period is dropped when the same tag carries the
  identical (non-zero, USD) value on a context longer than 380 days —
  dcf_engine.cumulative_context_values feeding capex_for_period's
  `cumulative` argument, the engine's rule verbatim; the drop is listed in
  ttm.json capex_components[leg].dropped with reason 'cumulative_duplicate'.
  ECHO files PaymentsToAcquireIntangibleAssets 30,000,000,000 on its H1-2025
  YTD context and on 2018-01-01..2025-12-31: added to the prior-YTD leg it
  turned TTM capex negative (-29.36B) and the TTM base into a fake
  +83.18/share. Intangible leg only (new in 5.5).
- [ADDITION — verifier round 1, rulings E5/E6/E10] capex_for_period's
  parts-of-total rule (E5) and its negative / $0 intangible rule (E6) apply
  per leg as in the engine (a $0 intangible fact is never joined or warned
  about). E10: when a capex_override is declared and a leg is now FILLED by a
  PP&E value whose tags are all outside the 5.4 capex list, at a value outside
  0.5x-2x of the override prorated to that leg (the amount 5.4 filled from the
  override), a warning is appended and the leg is recorded in ttm.json
  capex_override_superseded_legs ({} when none) — the per-leg twin of the
  engine's OVERRIDE_SUPERSEDED_BY_FILED_TAG:capex.
- [ADDITION — verifier round 2, R2-PIN] TTM denominator scale: when
  ttm_shares_diluted (the current-YTD diluted count) is outside 1/100-100x of
  the FY diluted leg or of the latest usable cover-page (dei) count, a warning
  names both counts (a 10-Q count filed in thousands as units makes
  ttm_oe_per_share 1,000x too large). No value changes here: the engine's
  share-scale guard now also tests the pin it is given (|pin| > 20x the price
  is DATA_GAP:shares — SHARE_SCALE), so such a pin gaps instead of scoring.
- [ADDITION — verifier round 4] Two per-leg rules gave wrong TTMs, because TTM
  SUBTRACTS the prior-YTD leg:
  R4-SBC (decision 6 can only raise SBC) sbc_floor: when the reconciled legs give
  a TTM below the unreconciled one (each reconciled leg on its Share figure —
  the 5.4 merge), the prior-YTD leg keeps its ShareBasedCompensation figure;
  ttm.json sbc_reconciliation_withdrawn_legs records it ({} when none) with a
  warning (SYM 228,899,000 -> 234,533,000; JHX, RKT, INCY, BJ likewise). When
  the reconciliation changes some legs but not all three, a warning says the TTM
  mixes tags (sbc_mixed_tag_warning); the per-leg values stand — one tag for all
  three legs would put JLL's TTM SBC at $1.5M (its 10-Qs file only the Share
  slice).
  R4-INTANG add_intangibles: the FY and prior-YTD legs add their intangible
  purchases only when their remainder is measurable (an FY intangible fact at
  least as large as the prior-YTD one, or no prior-YTD fact); otherwise neither
  does ('remainder_unknown', warning) and the current-YTD leg still adds its own.
  The TTM intangible contribution is never negative (BAX: -6,000,000 -> +3,000,000).
"""
import json, sys, os, csv, time, urllib.request, urllib.error, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dcf_engine as _engine  # v5.5: shared capex / SBC / split rules (no I/O at import)

UA = {"User-Agent": "Muse research andrewmauro199612@gmail.com"}
BASE = os.environ.get("STOCKS_BASE") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # v5.4: runs anywhere
SYS = f"{BASE}/_system"

OCF_TAGS = ["NetCashProvidedByUsedInOperatingActivities",
            "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"]
# v5.5: capex candidates are dcf_engine's shared lists (us-gaap entries only —
# ttm.py reads us-gaap 10-K / 10-Q facts); this union is for reference.
CAPEX_TAGS = [t for t in _engine.CAPEX_ROLLUP_TAGS + _engine.CAPEX_COMPONENT_TAGS if isinstance(t, str)]
SBC_TAGS = [_engine.SBC_SHARE_TAG, _engine.SBC_ALLOCATED_TAG]
SHARE_TAGS = ["WeightedAverageNumberOfDilutedSharesOutstanding",
              "WeightedAverageNumberOfSharesOutstandingDiluted",
              "WeightedAverageNumberOfSharesOutstandingBasic"]
FORMS = ("10-K", "10-K/A", "10-Q", "10-Q/A")


def get_json(url, headers=UA, timeout=90):
    last = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read())
        except Exception as e:  # retry with backoff on any transient fetch failure
            last = e
            if attempt < 2:
                time.sleep(2 ** attempt)
    raise last


def resolve_cik(ticker):
    if "--cik" in sys.argv:
        return int(sys.argv[sys.argv.index("--cik") + 1])
    sec = json.load(open(f"{SYS}/sec_tickers_exchange.json", encoding="utf-8"))
    cik_by_ticker = {}
    for rec in sec["data"]:
        cik_by_ticker.setdefault(rec[2].upper(), rec[0])
    for cand in (ticker, ticker.replace("/", "-"), ticker.replace("/", ".")):
        if cand in cik_by_ticker:
            return cik_by_ticker[cand]
    with open(f"{SYS}/universe.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["ticker"] == ticker and row.get("cik"):
                return int(row["cik"])
    return None


def tag_facts(facts, tag, unit):
    """{(start, end): (value, filed)} for ONE us-gaap tag in one unit — latest
    filing wins per exact period."""
    best = {}
    for e in (facts.get("facts", {}).get("us-gaap", {}).get(tag) or {}).get("units", {}).get(unit, []):
        if e.get("form", "") not in FORMS or not e.get("start") or not e.get("end"):
            continue
        key = (e["start"], e["end"])
        prev = best.get(key)
        if prev is None or e.get("filed", "") > prev[1]:
            best[key] = (e["val"], e.get("filed", ""))
    return best


def merged_facts(facts, tags, unit):
    """{(start, end): (value, tag)} across candidate tags — per exact period the
    highest-priority tag that reports it wins; latest filing wins within a tag."""
    merged = {}
    for tag in tags:
        for k, (v, _) in tag_facts(facts, tag, unit).items():
            if k not in merged:
                merged[k] = (v, tag)
    return merged


def capex_assembly(facts):
    """v5.5 (decisions 3-5): ({(start, end): (ppe_value, ppe_provenance)},
    {(start, end): capex_for_period result}) — per exact period, the engine's
    capex_for_period over the shared lists' us-gaap tags, USD facts only (the
    (taxonomy, tag) IFRS entries are skipped: ttm.py reads us-gaap). Periods
    with no PP&E value are absent from the first map (the leg is missing)."""
    groups = [[(t, tag_facts(facts, t, "USD")) for t in tags if isinstance(t, str)]
              for tags in (_engine.CAPEX_ROLLUP_TAGS, _engine.CAPEX_COMPONENT_TAGS, _engine.CAPEX_INTANGIBLE_TAGS)]
    # [ADDITION — ECHO] the engine's cumulative-duplicate rule on the intangible leg (same helper, USD facts):
    # a leg's intangible value that the same tag also files on a >380-day context is a cumulative total.
    cumulative = _engine.cumulative_context_values(
        facts, [t for t in _engine.CAPEX_INTANGIBLE_TAGS if isinstance(t, str)], units=("USD",))
    periods = {per for grp in groups for _, m in grp for per in m}
    ppe, results = {}, {}
    for per in sorted(periods):
        legs = [[(t, m[per][0], "USD", m[per][1]) for t, m in grp if per in m] for grp in groups]
        res = _engine.capex_for_period(*legs, cumulative=cumulative)
        results[per] = res
        if res["ppe"] is not None:
            ppe[per] = (res["ppe"], "+".join(res["ppe_tags"]))
    return ppe, results


def add_intangibles(capex, results, warnings):
    """v5.5: total capex per leg = the PP&E leg + intangible purchases filed for
    that exact leg period — never on an OVERRIDE-filled leg (an override is the
    filer's total capex line). Recomputes capex["ttm"]; returns
    {leg: capex_for_period result} for ttm.json capex_components.
    [ADDITION — verifier round 4, R4-INTANG] The FY and prior-YTD legs enter the TTM as one difference (the rest of
    the last fiscal year), so their intangible purchases are added only when that remainder is measurable: a
    prior-YTD intangible fact with no FY intangible fact (BAX, IONQ: a 10-Q files the line, the 10-K does not — the
    10-K figure is unknown, at least the prior-YTD amount), or a prior-YTD amount above the FY amount, leaves it
    unknown — neither leg adds its intangibles (capex_components[leg].intangibles_not_added 'remainder_unknown',
    with a warning). The current-YTD leg still adds its own. An OVERRIDE-filled FY leg is the filer's total line, so
    a filed prior-YTD leg still adds its intangibles there (one total basis). The TTM intangible contribution is
    therefore never negative (BAX: 0 - 9,000,000 + 3,000,000 = -6,000,000 had cut TTM capex below 5.4's)."""
    comps, add = {}, {}
    for leg in ("fy", "ytd_prior", "ytd_current"):
        per = capex.get(f"{leg}_period")
        res = results.get(tuple(per)) if per else None
        if res is None:
            comps[leg] = None
            continue
        rec = dict(res, dropped=[list(d) for d in res["dropped"]])
        # [ADDITION — ruling E6] capex_for_period never joins a $0 or negative intangible fact, so a leg whose only
        # intangible facts are $0 has no intangible_tags: nothing is added, joined or warned about here.
        if res["intangible_tags"] and res["intangibles"]:
            if capex.get(f"{leg}_tag") == "OVERRIDE":
                rec["intangibles_not_added"] = "override_present"
                warnings.append(f"capex {leg}: intangible purchases filed for {per[0]}..{per[1]} "
                                f"({res['intangibles']:,.0f}) were not added on top of the override")
            else:
                add[leg] = res
        comps[leg] = rec
    # [ADDITION — R4-INTANG] the FY - prior-YTD remainder of intangible purchases must be measurable
    if "ytd_prior" in add and capex.get("fy_tag") != "OVERRIDE":
        fy_amt = add["fy"]["intangibles"] if "fy" in add else None
        pr_amt = add["ytd_prior"]["intangibles"]
        if fy_amt is None or fy_amt < pr_amt:
            for leg in ("fy", "ytd_prior"):
                if leg in add:
                    comps[leg]["intangibles_not_added"] = "remainder_unknown"
                    del add[leg]
            pp = capex["ytd_prior_period"]
            why = ("no intangible purchase is filed for the FY leg" if fy_amt is None
                   else f"the FY leg files less ({fy_amt:,.0f})")
            warnings.append(f"capex: intangible purchases are filed for the prior-YTD leg {pp[0]}..{pp[1]} "
                            f"({pr_amt:,.0f}) but {why}, so the FY - prior-YTD remainder is unknown — neither leg adds "
                            "its intangibles (the current-YTD leg still adds its own); check the 10-K's investing section")
    for leg, res in add.items():
        capex[leg] = capex[leg] + res["intangibles"]
        capex[f"{leg}_tag"] = res["provenance"]
    capex["ttm"] = capex["fy"] - capex["ytd_prior"] + capex["ytd_current"]
    return comps


def superseded_capex_legs(capex, ov_value, warnings):
    """[ADDITION — verifier round 1, ruling E10] {leg: record} for the legs of an override-backed capex field that a
    FILED PP&E value now fills through tags all outside the 5.4 capex list (dcf_engine.CAPEX_TAGS_54 — the
    engine's OVERRIDE_SUPERSEDED_BY_FILED_TAG:capex test, applied per TTM leg) at a value outside 0.5x-2x of the
    override prorated to the leg's inclusive days (the amount the override filled under 5.4). Appends one warning
    per leg. Runs on assemble()'s output, before add_intangibles, so the value and tags are the PP&E leg's. WY: the
    override's 447,000,000 of TTM capex became 52,000,000 of PaymentsForCapitalImprovements with no warning."""
    out = {}
    for leg in ("fy", "ytd_prior", "ytd_current"):
        tag, per = capex.get(f"{leg}_tag"), capex.get(f"{leg}_period")
        if not tag or tag == "OVERRIDE" or not per:
            continue
        if any(t in _engine.CAPEX_TAGS_54 for t in str(tag).split("+")):
            continue   # filed under 5.4 as well: the override never filled this leg
        filed = capex[leg]
        ov_amt = ov_value * days(per[0], per[1]) / 365.0
        off = (ov_amt != 0) if filed == 0 else not (0.5 <= ov_amt / filed <= 2)
        if not off:
            continue
        out[leg] = {"period": list(per), "override": ov_value, "override_prorated": ov_amt,
                    "filed_ppe": filed, "filed_tags": tag}
        warnings.append(f"capex {leg}: the capex_override ({ov_value:,.0f}/yr, {ov_amt:,.0f} prorated to {per[0]}..{per[1]}) "
                        f"is outside 0.5x-2x of the PP&E capex now FILED for that leg ({filed:,.0f}, {tag}) under a tag "
                        "5.4 did not read — the filed value is used (an override never replaces a filed value), so the "
                        "override fills nothing there; reconcile it against the cash-flow statement and remove it or "
                        "justify it in analysis.md")
    return out


def sbc_reconciled(facts):
    """v5.5 (decision 6): ({(start, end): (value, tag)}, {(start, end): note}) —
    ShareBasedCompensation first, AllocatedShareBasedCompensationExpense when
    Share is absent (the 5.4 merge) OR when both report the exact period and
    Allocated is larger (dcf_engine.reconcile_sbc; USD only, so one unit)."""
    share = tag_facts(facts, _engine.SBC_SHARE_TAG, "USD")
    alloc = tag_facts(facts, _engine.SBC_ALLOCATED_TAG, "USD")
    merged, reconciled = {}, {}
    for per in set(share) | set(alloc):
        s, a = share.get(per), alloc.get(per)
        v, _, tag, rec, note = _engine.reconcile_sbc((s[0], "USD") if s else None, (a[0], "USD") if a else None)
        merged[per] = (v, tag)
        if rec:
            reconciled[per] = {"share": s[0], "allocated": a[0], "note": note}
    return merged, reconciled


def sbc_floor(sbc, reconciled, warnings):
    """[ADDITION — verifier round 4, R4-SBC] Decision 6 replaces a SMALLER ShareBasedCompensation figure with
    Allocated, so it can only raise SBC — but TTM = FY - prior YTD + current YTD subtracts the prior-YTD leg, and
    raising that leg LOWERS the TTM. When the reconciled legs give a TTM below the unreconciled one (each reconciled
    leg back on its Share figure: the 5.4 merge), the prior-YTD leg keeps its Share figure (sbc is updated in place)
    and the TTM is recomputed: never below the 5.4 TTM. SYM: FY Share 183,936,000 (Allocated 174,402,000 is lower), only
    the prior YTD reconciled (97,956,000 over 92,322,000): TTM 228,899,000 against Share's 234,533,000. The FY and
    current-YTD legs are never touched (raising them raises the TTM). Returns {} or {"ytd_prior": record} for
    ttm.json sbc_reconciliation_withdrawn_legs; appends a warning when it acts."""
    if not sbc or not sbc.get("ytd_prior_period"):
        return {}

    def recon(leg):
        per = tuple(sbc[f"{leg}_period"]) if sbc.get(f"{leg}_period") else None
        return reconciled.get(per) if (per in reconciled and sbc.get(f"{leg}_tag") == _engine.SBC_ALLOCATED_TAG) else None
    r_p = recon("ytd_prior")
    if not r_p:
        return {}
    unrec = {leg: (recon(leg)["share"] if recon(leg) else sbc[leg]) for leg in ("fy", "ytd_prior", "ytd_current")}
    ttm_unrec = unrec["fy"] - unrec["ytd_prior"] + unrec["ytd_current"]
    if sbc["ttm"] >= ttm_unrec:
        return {}
    ttm_rec = sbc["ttm"]
    sbc["ytd_prior"], sbc["ytd_prior_tag"] = r_p["share"], _engine.SBC_SHARE_TAG
    sbc["ttm"] = sbc["fy"] - sbc["ytd_prior"] + sbc["ytd_current"]
    per = sbc["ytd_prior_period"]
    warnings.append(f"sbc ytd_prior: AllocatedShareBasedCompensationExpense ({r_p['allocated']:,.0f}) exceeds "
                    f"ShareBasedCompensation ({r_p['share']:,.0f}) for {per[0]}..{per[1]}, but that leg is SUBTRACTED, so "
                    f"using it would lower TTM SBC to {ttm_rec:,.0f} — below the unreconciled {ttm_unrec:,.0f}; the "
                    f"ShareBasedCompensation figure is kept on that leg (TTM SBC {sbc['ttm']:,.0f})")
    return {"ytd_prior": {"period": list(per), "share": r_p["share"], "allocated": r_p["allocated"],
                          "ttm_reconciled": ttm_rec, "ttm_unreconciled": ttm_unrec, "ttm_used": sbc["ttm"]}}


def sbc_mixed_tag_warning(sbc, reconciled_legs, warnings):
    """[ADDITION — verifier round 4, R4-SBC] When the reconciliation changed some TTM legs but not all three, the TTM
    mixes ShareBasedCompensation and AllocatedShareBasedCompensationExpense across legs (JLL: Allocated $112.0M on the
    FY leg, while its 10-Qs file only the Share slice, $1.4M / $0.2M) — appends one informational warning naming
    each leg's tag. No value changes: the per-leg rule stands (choosing one tag for all three legs would put JLL's
    TTM SBC at $1.5M)."""
    if not sbc or not reconciled_legs or len(reconciled_legs) == 3:
        return
    legs = ", ".join(f"{leg} {sbc.get(f'{leg}_tag')}" for leg in ("fy", "ytd_prior", "ytd_current"))
    warnings.append(f"sbc: AllocatedShareBasedCompensationExpense replaced a smaller ShareBasedCompensation on "
                    f"{', '.join(sorted(reconciled_legs))} only, so the TTM mixes tags across legs ({legs}) — check that "
                    "each leg's figure is the filer's total stock compensation for its period (a 10-Q often files only "
                    "one of the two tags)")


def split_adjustment(facts, shares):
    """v5.5 (decision 2b): the engine's split rule applied to the TTM
    denominator. With the event confirmed by the shared helpers (FY diluted
    leg as shares_latest), ytd_current is multiplied by ratio_used only when it
    is still on the pre-split basis (ytd_current / dei within +-15% of
    1 / ratio_used). Returns the record (None when no split is confirmed) and
    rescales shares["ytd_current"] in place when applied."""
    if not shares or shares.get("fy") is None or not shares.get("fy_period") or not shares.get("ytd_current"):
        return None
    fy_end = shares["fy_period"][1]
    dei = (facts.get("facts", {}).get("dei", {}).get("EntityCommonStockSharesOutstanding") or {}).get("units", {})
    dei_count, dei_date = _engine.latest_dei_count([e for es in dei.values() for e in es], fy_end)
    us = facts.get("facts", {}).get("us-gaap", {})
    split_entries = [e for t in _engine.SPLIT_RATIO_TAGS for e in ((us.get(t) or {}).get("units", {}).get("pure") or [])]
    conf = _engine.confirm_split(_engine.split_events_post_fy(split_entries, fy_end), shares["fy"], dei_count, dei_date)
    if not conf:
        return None
    ev_date, ratio_used, ev = conf
    cur = shares["ytd_current"]
    applied = abs((cur / dei_count) * ratio_used - 1) <= _engine.SPLIT_CONFIRM_TOL
    rec = {"event_date": ev_date, "ratio_filed": ev["ratio_filed"], "ratio_used": ratio_used,
           "dei_count": dei_count, "dei_date": dei_date, "fy_diluted": shares["fy"],
           "ytd_current_before": cur, "applied": applied}
    if applied:
        shares["ytd_current"] = cur * ratio_used
        rec["ytd_current_after"] = shares["ytd_current"]
    return rec


def share_scale_warnings(facts, shares):
    """[ADDITION — verifier round 2, R2-PIN] Warnings (a list, empty when clean) for a TTM denominator
    (shares["ytd_current"]) outside dcf_engine.SHARE_SCALE_DEI_BAND (1/100-100x) of the FY diluted leg
    (shares["fy"]) or of the latest usable cover-page count (dcf_engine.latest_dei_count, dated no earlier than
    18 months before the FY end). Informational: no value changes."""
    cur = shares.get("ytd_current") if shares else None
    if not cur or cur <= 0:
        return []
    lo, hi = _engine.SHARE_SCALE_DEI_BAND
    out = []
    fy = shares.get("fy")
    if fy and fy > 0 and not (lo <= cur / fy <= hi):
        out.append(f"shares: the TTM denominator {cur:,.0f} (ytd_current) is {cur / fy:.6g}x the FY diluted count {fy:,.0f} "
                   "(outside 1/100-100x) — a count filed in thousands as units? ttm_oe_per_share is off by the same factor; "
                   "the engine gaps a pin above 20x the price (DATA_GAP:shares — SHARE_SCALE)")
    fy_end = (shares.get("fy_period") or [None, None])[1] or (shares.get("ytd_current_period") or [None, None])[1]
    dei = (facts.get("facts", {}).get("dei", {}).get("EntityCommonStockSharesOutstanding") or {}).get("units", {})
    dei_count, dei_date = _engine.latest_dei_count([e for es in dei.values() for e in es], fy_end)
    if dei_count and not (lo <= cur / dei_count <= hi):
        out.append(f"shares: the TTM denominator {cur:,.0f} (ytd_current) is {cur / dei_count:.6g}x the cover-page count "
                   f"{dei_count:,.0f} ({dei_date}; outside 1/100-100x) — a count filed in thousands as units? "
                   "ttm_oe_per_share is off by the same factor; the engine gaps a pin above 20x the price "
                   "(DATA_GAP:shares — SHARE_SCALE)")
    return out


def load_overrides(ticker):
    """Structured judgment overrides from {ticker}/judgment.json — same
    validation as dcf_engine.py: a malformed override is ignored here and
    refused by make_score.py."""
    if os.environ.get("DCF_NO_OVERRIDES"):
        return {}
    try:
        j = json.load(open(f"{BASE}/{ticker}/judgment.json", encoding="utf-8"))
    except Exception:
        return {}
    out = {}
    for field, key in (("capex", "capex_override"), ("sbc", "sbc_override"), ("shares", "shares_override")):
        o = j.get(key) if isinstance(j, dict) else None
        if (isinstance(o, dict) and isinstance(o.get("value"), (int, float))
                and not isinstance(o.get("value"), bool)
                and o.get("kind") in ("filing", "estimate")
                and str(o.get("source") or "").strip() and str(o.get("reason") or "").strip()):
            out[field] = {"value": float(o["value"]), "kind": o["kind"],
                          "source": o["source"], "reason": o["reason"]}
            if isinstance(o.get("currency"), str) and o["currency"].strip():
                out[field]["currency"] = o["currency"].strip().upper()  # v5.5: passed through, validated by make_score
    return out


def days(a, b):
    """INCLUSIVE day count of the period a..b (end - start + 1) — a calendar
    fiscal year is 365 days, so an override-filled annual leg comes to exactly
    the override value, matching the engine's annual fill (round-2: the old
    exclusive count made APP's FY leg $18.95M against the engine's $19.00M)."""
    return (datetime.date.fromisoformat(b) - datetime.date.fromisoformat(a)).days + 1


def start_diff(a, b):
    return abs((datetime.date.fromisoformat(a) - datetime.date.fromisoformat(b)).days)


def shift_year(dstr, delta):
    d = datetime.date.fromisoformat(dstr)
    try:
        return d.replace(year=d.year + delta).isoformat()
    except ValueError:  # Feb 29
        return d.replace(year=d.year + delta, day=28).isoformat()


def extract_ttm(series, label, problems):
    """series: {(start,end): (val, tag)}. Returns dict of inputs or None."""
    annual = [(s, e, v, t) for (s, e), (v, t) in series.items() if 330 <= days(s, e) <= 380]
    if not annual:
        problems.append(f"{label}: no annual (FY) fact")
        return None
    fy_start, fy_end, fy_val, fy_tag = max(annual, key=lambda x: x[1])
    # current-year YTD: periods starting at the fiscal-year start that follows fy_end
    starts_after = sorted({s for (s, e) in series if s > fy_start and 0 <= days(fy_end, s) <= 10})
    cur = None
    for st in starts_after:
        cands = [(e, v, t) for (s, e), (v, t) in series.items() if s == st and days(s, e) <= 300]
        if cands:
            e, v, t = max(cands, key=lambda x: x[0])
            cur = (st, e, v, t)
            break
    if cur is None:
        problems.append(f"{label}: no post-FY YTD fact (no 10-Q since the {fy_end} fiscal year end)")
        return None
    cur_start, cur_end, cur_val, cur_tag = cur
    # prior-year YTD: same fiscal start as the FY (within a few days — filers
    # occasionally shift a period start), ending ~1 year before cur_end
    target_end = shift_year(cur_end, -1)
    prior, prior_key = None, None
    for (s, e), (v, t) in series.items():
        if start_diff(s, fy_start) <= 5 and abs((datetime.date.fromisoformat(e) - datetime.date.fromisoformat(target_end)).days) <= 6:
            key = (start_diff(s, fy_start), -datetime.date.fromisoformat(e).toordinal())
            if prior is None or key < prior_key:
                prior, prior_key = (s, e, v, t), key
    if prior is None:
        problems.append(f"{label}: no prior-year YTD fact matching {target_end} (FY start {fy_start})")
        return None
    return {"fy": fy_val, "fy_period": [fy_start, fy_end], "fy_tag": fy_tag,
            "ytd_prior": prior[2], "ytd_prior_period": [prior[0], prior[1]], "ytd_prior_tag": prior[3],
            "ytd_current": cur_val, "ytd_current_period": [cur_start, cur_end], "ytd_current_tag": cur_tag,
            "ttm": fy_val - prior[2] + cur_val}


def main():
    ticker = sys.argv[1].upper()
    cik = resolve_cik(ticker)
    if cik is None:
        print(f"ttm.py: NO_CIK for {ticker}", file=sys.stderr)
        sys.exit(2)
    facts = get_json(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json")

    problems, warnings = [], []
    overrides = load_overrides(ticker)
    overrides_used = []
    ocf = extract_ttm(merged_facts(facts, OCF_TAGS, "USD"), "ocf", problems)
    anchor = None
    if ocf:
        anchor = {"fy": tuple(ocf["fy_period"]), "ytd_prior": tuple(ocf["ytd_prior_period"]),
                  "ytd_current": tuple(ocf["ytd_current_period"])}

    def assemble(series, field):
        """TTM legs on the OCF anchor timeline for an override-backed field:
        the filer's own fact wins when one exists for the anchor period —
        including a fact whose start is shifted a few days (matched on end
        date + nearest start), so a real filed fact is never replaced by an
        override fill; a truly missing leg is filled with the override
        prorated by inclusive days (x days/365)."""
        ov = overrides[field]
        legs, filled_legs = {}, {}
        for leg in ("fy", "ytd_prior", "ytd_current"):
            per = anchor[leg]
            hit = series.get(per)
            if not hit:
                cands = [(start_diff(s, per[0]), (s, e), v) for (s, e), v in series.items()
                         if e == per[1] and start_diff(s, per[0]) <= 5]
                if cands:
                    cands.sort(key=lambda x: x[0])
                    _, k, v = cands[0]
                    hit = (v, series[k][1])
                    per = k
            if hit:
                legs[leg] = (per, hit[0], hit[1])
            else:
                d = days(per[0], per[1])
                amt = ov["value"] * d / 365.0
                legs[leg] = (per, amt, "OVERRIDE")
                filled_legs[leg] = {"period": list(per), "amount": amt, "days": d, "prorated": True}
        if filled_legs:
            overrides_used.append({"field": field, "value": ov["value"], "kind": ov["kind"],
                                   "source": ov["source"], "legs_filled": filled_legs})
        fy, pr, cu = legs["fy"], legs["ytd_prior"], legs["ytd_current"]
        return {"fy": fy[1], "fy_period": list(fy[0]), "fy_tag": fy[2],
                "ytd_prior": pr[1], "ytd_prior_period": list(pr[0]), "ytd_prior_tag": pr[2],
                "ytd_current": cu[1], "ytd_current_period": list(cu[0]), "ytd_current_tag": cu[2],
                "ttm": fy[1] - pr[1] + cu[1]}

    sbc_series, sbc_recon = sbc_reconciled(facts)   # v5.5: Allocated used where it exceeds Share
    if "sbc" in overrides and anchor:
        sbc = assemble(sbc_series, "sbc")
    else:
        sbc = extract_ttm(sbc_series, "sbc", problems)
    sbc_withdrawn = sbc_floor(sbc, sbc_recon, warnings)   # [ADDITION — R4-SBC] never below the unreconciled TTM
    sbc_reconciled_legs = {}
    for leg in ("fy", "ytd_prior", "ytd_current"):
        per = tuple(sbc[f"{leg}_period"]) if sbc and sbc.get(f"{leg}_period") else None
        if per in sbc_recon and sbc.get(f"{leg}_tag") == _engine.SBC_ALLOCATED_TAG:
            sbc_reconciled_legs[leg] = dict(sbc_recon[per], period=list(per))
    sbc_mixed_tag_warning(sbc, sbc_reconciled_legs, warnings)   # [ADDITION — R4-SBC] informational

    _plen = len(problems)
    shares = extract_ttm(merged_facts(facts, SHARE_TAGS, "shares"), "shares_diluted", problems)
    if shares is None and "shares" in overrides:
        del problems[_plen:]  # the override rescues the missing share count
        ov = overrides["shares"]
        shares = {"fy": None, "fy_period": None, "fy_tag": None,
                  "ytd_prior": None, "ytd_prior_period": None, "ytd_prior_tag": None,
                  "ytd_current": ov["value"],
                  "ytd_current_period": list(anchor["ytd_current"]) if anchor else None,
                  "ytd_current_tag": "OVERRIDE", "ttm": None}
        overrides_used.append({"field": "shares", "value": ov["value"], "kind": ov["kind"],
                               "source": ov["source"],
                               "legs_filled": {"ytd_current": {"amount": ov["value"], "prorated": False,
                                               "note": "share counts are weighted averages, not flows — used unprorated as the TTM denominator"}}})
    split_adj = split_adjustment(facts, shares) if shares and shares.get("ytd_current_tag") != "OVERRIDE" else None
    warnings.extend(share_scale_warnings(facts, shares))   # [ADDITION — R2-PIN] informational

    capex_series, capex_results = capex_assembly(facts)   # v5.5: PP&E leg per exact period
    capex_components = None
    capex_superseded = {}
    if "capex" in overrides and anchor:
        capex = assemble(capex_series, "capex")
        capex_superseded = superseded_capex_legs(capex, overrides["capex"]["value"], warnings)   # [ADDITION — E10]
    elif not capex_series:
        # Round-2: no more zero-fill-with-warning. A never-filed capex is a
        # data gap here exactly as in the engine (DATA_GAP:capex); only a
        # judgment override (the branch above) may fill it.
        problems.append("capex: no capex facts in companyfacts under any candidate tag and no "
                        "capex_override in judgment.json — refusing to zero-fill (same DATA_GAP standard as the engine)")
        capex = {"fy": 0, "ytd_prior": 0, "ytd_current": 0, "ttm": 0,
                 "fy_period": None, "ytd_prior_period": None, "ytd_current_period": None,
                 "fy_tag": None, "ytd_prior_tag": None, "ytd_current_tag": None}
    else:
        capex = extract_ttm(capex_series, "capex", problems)
    if capex and capex.get("fy_period"):
        capex_components = add_intangibles(capex, capex_results, warnings)   # v5.5: + intangible purchases

    if problems:
        print(f"ttm.py: cannot compute TTM for {ticker} (CIK {cik}): " + "; ".join(problems), file=sys.stderr)
        sys.exit(3)

    oe_total = ocf["ttm"] - capex["ttm"] - sbc["ttm"]
    shares_in = dict(shares)
    shares_in.pop("ttm", None)  # share counts are weighted averages, not flows — a "TTM sum" is meaningless; the TTM denominator is the current-YTD average
    shares_in["basis"] = "ttm_shares_diluted = ytd_current (weighted average diluted shares for the current YTD period)"
    out = {"ticker": ticker, "cik": cik, "entity": facts.get("entityName"),
           "fy_end": ocf["fy_period"][1], "ytd_end": ocf["ytd_current_period"][1],
           "inputs": {"ocf": ocf, "capex": capex, "sbc": sbc, "shares_diluted": shares_in},
           "ttm_ocf": ocf["ttm"], "ttm_capex": capex["ttm"], "ttm_sbc": sbc["ttm"],
           "ttm_shares_diluted": shares["ytd_current"],
           "ttm_oe_total": oe_total,
           "ttm_oe_per_share": oe_total / shares["ytd_current"] if shares["ytd_current"] else None,
           "warnings": warnings, "overrides_used": overrides_used,
           # v5.5 provenance (see the module docstring)
           "capex_components": capex_components, "sbc_reconciled_legs": sbc_reconciled_legs,
           "split_adjustment": split_adj,
           # [ADDITION — ruling E10] override-backed capex legs a 5.5-new filed tag now fills off-band ({} when none)
           "capex_override_superseded_legs": capex_superseded,
           # [ADDITION — verifier round 4, R4-SBC] a reconciled prior-YTD leg withdrawn because it lowered the TTM
           "sbc_reconciliation_withdrawn_legs": sbc_withdrawn}
    if not os.environ.get("DCF_TTM_NO_WRITE"):
        # Machine-readable provenance for the base pin: the engine's --ttm
        # reads this file, and make_score.py refuses a pinned base that
        # differs from it by >0.1%.
        with open(f"{BASE}/{ticker}/ttm.json", "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
