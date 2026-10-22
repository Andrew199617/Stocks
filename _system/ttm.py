#!/usr/bin/env python3
"""TTM owner's-earnings calculator (v5, 2026-10-13 — agents never hand-compute TTM again).

Usage: python3 ttm.py <TICKER> [--cik N] [--interim | --interim-draft <6-K accession>]

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
  v5.7 (Andrew, 2026-10-19, R8 / R9): the shared lists grew with no ttm.py
  code change — CAPEX_COMPONENT_TAGS includes
  PaymentsToAcquireMachineryAndEquipment, PaymentsToAcquireMiningAssets and
  PaymentsToAcquireFurnitureAndFixtures (the last two sub-classes, read only
  beside another component: 'subclass_alone' in capex_components[leg].dropped
  otherwise), and CAPEX_INTANGIBLE_TAGS the capitalized-software tags
  CAPEX_SOFTWARE_TAGS (us-gaap entries here); capex_components[leg] carries
  software / software_tags when the leg's software was read (the engine's
  IPR&D guard subtracts it), and the override-leg warning names the software
  it did not add. superseded_capex_legs treats a leg whose 5.4-tag value was
  dropped as a retag duplicate as filed under 5.4. ttm.json carries
  engine_release (the release whose rules built it): the engine records it as
  ttm_inputs.ttm_engine_release, and make_score refuses a 5.7 run whose basis
  read a ttm.json without a 5.7 stamp — run ttm.py, then the engine.
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

v5.7 (engine release 5.7.0 — Andrew's ruling R2a, 2026-10-19: "do what we gotta to get good foreign companies
working"): --interim builds ttm.json for a 20-F / 40-F filer from the DECLARED 6-K interim bridge in judgment.json
interim_bridge (schema: _system/examples/interim_bridge.example.json; rules: interim_bridge.py). TTM = the engine's
own latest-FY leg (financials_history.csv's last row, its units from capex_provenance / the engine's OCF and SBC
tags; never declared) - the prior-year interim + the current interim, per leg (OCF, PP&E capex, intangible capex,
SBC), each interim leg converted at its own period-end ECB rate (fetched; the declared rate must be within 0.5%),
the FY leg at the engine's own FY rate; the denominator is the current interim's weighted average diluted count and
ttm_oe_per_share is per ADS (the ADS ratio is applied here). Every filing leg cites the report's accession /
document / section with a verbatim snippet (at most 24 words) that shows the value, and is verified against the
6-K's own XBRL instance when EDGAR lists one (a filed fact the declaration misstates, or declares as an estimate, is
refused); an acquired-IPR&D charge the 6-K files for the current interim refuses the bridge (the engine's one-time
deduction cannot read a 6-K — default Q8, main agent 2026-10-21). The like-for-like rules, the estimate methods and
the period rules are interim_bridge.py's, run as one bundle (declaration_rule_problems) that make_score.py re-runs on
the record. The report's period (IB-P5) is an XBRL 6-K's instance dei DocumentPeriodEndDate; a 6-K without XBRL has
none in EDGAR (its reportDate is the cover date — TFII's, FUTU's 6-Ks), so there the current interim must only have
ended before the report was filed (review fix 2026-10-21). ttm.json gains `basis: "declared_interim"` (absent on
the 10-Q path), the declaration hash, the engine record it started from, the report (with the period IB-P5 used),
the per-leg record, fx, provenance and the 10-Q path's compat keys (inputs, ttm_*; capex_components null) — no new
key is hashed into ttm_input_hash. Exit 3 on any rule
(the message lists every [IB-*] code), 4 on a fetch failure (EDGAR, the 6-K instance, an ECB rate). --interim-draft
<accession> prints a draft declaration from that 6-K's XBRL (TODO markers for snippets, like-for-like and missing
legs) and writes nothing. Without --interim / --interim-draft nothing changes.

v5.7 (engine release 5.7.0 — Andrew's ruling R6, 2026-10-19/20: the real total share count for two-class companies
like VNOM): when judgment.json declares share_classes, both builders put the TTM on total economic units before the
write (apply_share_classes, policy-bearing: it changes the --ttm base): the current-YTD (interim) period must be
declared — refused with exit 3 BAD_SHARE_CLASSES otherwise, nothing written — its 0 entries dated outside it, a
shares_override YTD leg (and the declared interim share leg) attested share_basis "traded_class" (load_overrides
passes share_basis through), the units split-scaled by their own filing (an OVERRIDE leg confirms the split for the
units on their own, else the engine record's), and the exchange test run on the YTD basic count (the 6-K instance's
on the interim path). Every per-share figure (ttm_oe_per_share, ttm_oe_per_ordinary_share, the override zero-fill)
is multiplied by filed ÷ (filed + units), each original kept as <field>_filed_basis; ttm_shares_diluted is the
total and ttm_shares_diluted_filed the traded-class leg; ttm.json share_classes carries the declaration_sha256 the
engine and make_score check. VNOM: 187,553,000 + 171,536,228 units, $1,488,000,000 / 359,089,228 = $4.1438 (filed
basis $7.9338). DCF_NO_SHARE_CLASSES with DCF_TTM_NO_WRITE builds the filed-basis TTM (never written). On the interim
path IB-SH1 / the fy_diluted_count estimate compare with the engine record's FILED traded FY count (shares.fy_diluted;
fy_total_units beside it); --interim-draft drafts the share leg with share_basis "traded_class" at a declaring filer.
"""
import json, sys, os, csv, time, urllib.request, urllib.error, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dcf_engine as _engine  # v5.5: shared capex / SBC / split rules (no I/O at import)
import interim_bridge as _ib  # v5.7 (L4, R2a): the declared 6-K bridge's rules (pure, no I/O at import)
import share_classes as _sc  # v5.7 (L8, R6): the declared share classes' rules (pure, no I/O at import)

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
                # v5.7 R9: the warning names the capitalized-software part (text unchanged when none is filed)
                warnings.append(f"capex {leg}: intangible purchases filed for {per[0]}..{per[1]} "
                                f"({res['intangibles']:,.0f}"
                                + (f", of which capitalized software {res['software']:,.0f}"
                                   if res.get("software_tags") and res.get("software") else "")
                                + ") were not added on top of the override")
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


def superseded_capex_legs(capex, ov_value, warnings, results=None):
    """[ADDITION — verifier round 1, ruling E10] {leg: record} for the legs of an override-backed capex field that a
    FILED PP&E value now fills through tags all outside the 5.4 capex list (dcf_engine.CAPEX_TAGS_54 — the
    engine's OVERRIDE_SUPERSEDED_BY_FILED_TAG:capex test, applied per TTM leg) at a value outside 0.5x-2x of the
    override prorated to the leg's inclusive days (the amount the override filled under 5.4). Appends one warning
    per leg. Runs on assemble()'s output, before add_intangibles, so the value and tags are the PP&E leg's. WY: the
    override's 447,000,000 of TTM capex became 52,000,000 of PaymentsForCapitalImprovements with no warning.
    v5.7 (R8): `results` ({(start, end): capex_for_period result}, capex_assembly's second map) — a leg whose result
    dropped a 5.4-tag fact as a retag / same-filing duplicate of the line it now reads was filed under 5.4 too (RL
    re-tagged ProductiveAssets to machinery and equipment), so it is not superseded (the engine's twin rule)."""
    out = {}
    for leg in ("fy", "ytd_prior", "ytd_current"):
        tag, per = capex.get(f"{leg}_tag"), capex.get(f"{leg}_period")
        if not tag or tag == "OVERRIDE" or not per:
            continue
        if any(t in _engine.CAPEX_TAGS_54 for t in str(tag).split("+")):
            continue   # filed under 5.4 as well: the override never filled this leg
        _res = (results or {}).get(tuple(per))
        if _res and any(d[0] in _engine.CAPEX_TAGS_54 and d[2] in ("retag_duplicate", "same_filing_duplicate")
                        for d in _res.get("dropped") or []):
            continue   # v5.7: the same value was filed under a 5.4 tag (re-tagged since)
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


# ---------------------------------------------------------------------------
# v5.7 (lane L8 — Andrew's ruling R6, 2026-10-19/20): the TTM on total economic units (08 §5)
# ---------------------------------------------------------------------------
# every per-share figure either TTM builder writes; absent fields are skipped. Each is multiplied by
# k = filed / (filed + units) — whatever ADS factor or zero-fill it already carries — and kept as <field>_filed_basis
SC_PER_SHARE_FIELDS = (("ttm_oe_per_share",), ("ttm_oe_per_ordinary_share",),
                       ("override_counterfactual", "base_oe_per_share_zero_fill"))


def ytd_basic(facts, sh_leg):
    """The basic weighted count (share_classes.BASIC_TAGS, us-gaap, unit shares) whose (start, end) equals the YTD share
    leg's ytd_current_period, the latest filed winning; None when none is filed."""
    per = (sh_leg or {}).get("ytd_current_period")
    if not (isinstance(per, list) and len(per) == 2):
        return None
    best = None
    for tax, tag in _sc.BASIC_TAGS:
        if tax != "us-gaap":
            continue
        for e in (facts.get("facts", {}).get("us-gaap", {}).get(tag) or {}).get("units", {}).get("shares", []):
            if (e.get("start"), e.get("end")) != (per[0], per[1]) or e.get("form", "") not in FORMS:
                continue
            v = _sc._num(e.get("val"))
            if v is not None and (best is None or e.get("filed", "") > best[1]):
                best = (v, e.get("filed", ""))
        if best is not None:
            return best[0]
    return None


def fy_diluted_fact(facts, fy_end):
    """The FY diluted count (SHARE_TAGS, 330-380 days) ending fy_end — the leg extract_ttm would take — or None."""
    for (s, e), (v, _t) in merged_facts(facts, SHARE_TAGS, "shares").items():
        if e == fy_end and 330 <= days(s, e) <= 380:
            return v
    return None


def _engine_record_split(base, ticker):
    """dcf_numbers.json share_basis.split when its content hash verifies: the split dict, {} when the record confirmed
    no split, None when there is no verified record."""
    try:
        with open(f"{base}/{ticker}/dcf_numbers.json", encoding="utf-8") as f:
            n = json.load(f)
    except Exception:
        return None
    if not isinstance(n, dict) or not n.get("content_hash") or _engine._content_hash(n) != n.get("content_hash"):
        return None
    s = (n.get("share_basis") or {}).get("split") if isinstance(n.get("share_basis"), dict) else None
    return s if isinstance(s, dict) and s.get("event_date") and s.get("ratio_used") else {}


def _units_split_event(out, facts, leg, engine_record, base, ticker):
    """((event_date, ratio_used, source) | None, error | None): the split the declared YTD units are placed against —
    never "no split" merely because split_adjustment did not run (rule 11). The interim leg: the engine record's
    share_basis.split. The 10-Q leg: split_adjustment's confirmed event; on an OVERRIDE YTD leg (split_adjustment is
    skipped: an override is post-split) the split is confirmed for the units on their own (confirm_split on the FY
    diluted fact vs dei, as split_adjustment does), else the engine record's; neither, with a post-FY split fact
    filed -> refused."""
    if leg == "interim":
        s = ((engine_record or {}).get("share_basis") or {}).get("split") if isinstance(engine_record, dict) else None
        return ((s["event_date"], s["ratio_used"], "engine_record") if isinstance(s, dict) and s.get("event_date")
                else None), None
    sa = out.get("split_adjustment")
    if sa:
        return (sa["event_date"], sa["ratio_used"], "split_adjustment"), None
    if out["inputs"]["shares_diluted"].get("ytd_current_tag") != "OVERRIDE":
        return None, None
    fy_end = out.get("fy_end")
    dei = (facts.get("facts", {}).get("dei", {}).get("EntityCommonStockSharesOutstanding") or {}).get("units", {})
    us = facts.get("facts", {}).get("us-gaap", {})
    split_entries = [e for t in _engine.SPLIT_RATIO_TAGS for e in ((us.get(t) or {}).get("units", {}).get("pure") or [])]
    events = _engine.split_events_post_fy(split_entries, fy_end)
    fy_count = fy_diluted_fact(facts, fy_end)
    if fy_count:
        dei_count, dei_date = _engine.latest_dei_count([e for es in dei.values() for e in es], fy_end)
        conf = _engine.confirm_split(events, fy_count, dei_count, dei_date)
        return ((conf[0], conf[1], "confirmed_for_units") if conf else None), None
    s = _engine_record_split(base, ticker)
    if s is not None:
        return ((s["event_date"], s["ratio_used"], "engine_record") if s else None), None
    if events:
        return None, ("a split ratio is filed after the FY end, the YTD share leg is a shares_override and no FY diluted "
                      "fact or engine record can confirm the split — the declared units cannot be put on a split basis; "
                      "run the engine first")
    return None, None


def apply_share_classes(out, ticker, base, facts, overrides, leg="ytd_10q", engine_record=None, interim=None):
    """v5.7 (L8, R6; 08 §5.1 / §5.4): put the TTM on total economic units when judgment.json declares share_classes —
    mutates `out` (the ttm.json dict) and returns an error string (refused: exit 3, nothing written) or None. leg
    "ytd_10q" (the 10-Q path) or "interim" (the declared 6-K bridge: interim = {"period", "shares_leg", "basic"}).
    The current-YTD (interim) period must be declared; its 0 entries dated outside it (rule 5); a shares_override
    leg, and the declared interim share leg, attest share_basis "traded_class" (rule 10); the units are split-scaled
    by their own filing (rule 11); the exchange test runs on the YTD basic count (the 6-K instance's on the interim
    path; none -> diluted_gap_reason), never on an OVERRIDE leg. Then every per-share field (SC_PER_SHARE_FIELDS) x
    k = filed / (filed + units), each original kept as <field>_filed_basis; ttm_shares_diluted = filed + units,
    ttm_shares_diluted_filed = filed; out["share_classes"] records the declaration's sha256 (the engine's and
    make_score's sync rule, share_classes.ttm_on_declaration) and the leg's out_of_band (rule 6: units over
    UNITS_MAX_MULT x the traded count; make_score refuses it without ack_reason). A zero YTD period writes the block
    with k = 1. Off only in make_score's replay: DCF_NO_SHARE_CLASSES with DCF_TTM_NO_WRITE (a filed-basis ttm.json
    is never written)."""
    decl = None if (os.environ.get(_sc.ENV_OFF) and os.environ.get("DCF_TTM_NO_WRITE")) else _sc.load(base, ticker)
    if decl is None:
        return None
    norm, errs = _sc.validate(decl)
    if errs:
        return "share_classes is malformed — " + "; ".join(errs)
    sh_leg = out["inputs"]["shares_diluted"]
    end = out["ytd_end"]
    start = (interim["period"][0] if leg == "interim" else (sh_leg.get("ytd_current_period") or [None])[0])
    units = _sc.units_by_period(norm).get(end)
    if units is None:
        return (f"share_classes is declared but has no units for the current-YTD period ending {end} — declare that "
                "period from the 10-Q's (6-K's) equity note (ownership table); 0 only for a class that did not exist "
                "during the period (rule 5), or the TTM cannot be priced on total units")
    errs = _sc.check_zero_entries(norm, end, start)
    if errs:
        return "; ".join(errs)
    inc = _sc.included_units(norm, end)
    filed = out["ttm_shares_diluted"]
    is_override = leg == "ytd_10q" and sh_leg.get("ytd_current_tag") == "OVERRIDE"
    if is_override and inc:
        return ("the YTD share leg is a shares_override (the traded-class count): no declared units can be in it — "
                "remove in_filed_count")
    if is_override and units and (overrides.get("shares") or {}).get("share_basis") != "traded_class":
        return ("shares_override fills the current-YTD share leg at a declaring filer; state that it is the traded-class "
                "count (shares_override.share_basis: \"traded_class\") — an all-class override already counts the units")
    if leg == "interim" and (units or inc) and ((interim or {}).get("shares_leg") or {}).get("share_basis") != "traded_class":
        return ("interim_bridge.legs.shares_diluted.current_interim must state share_basis \"traded_class\" at a "
                "declaring filer (the 6-K's traded-class weighted diluted count) — units are added on top of it")
    ev, why = _units_split_event(out, facts, leg, engine_record, base, ticker)
    if why:
        return why
    try:
        accn_filed = _sc.filed_dates_by_accession(facts)
        f, ubasis = _sc.units_split_scale(norm, end, accn_filed, ev and ev[0], ev and ev[1])
        fi, _ = _sc.units_split_scale(norm, end, accn_filed, ev and ev[0], ev and ev[1], included=True)
    except ValueError as e:
        return str(e)
    u, ui = units * f, inc * fi
    if is_override:
        xrec = {"test": "skipped_override"}
    elif not u and not ui:
        xrec = {"test": "zero_period"}
    else:
        if leg == "interim":
            b = (interim or {}).get("basic")
        else:
            b = ytd_basic(facts, sh_leg)
            if b and (out.get("split_adjustment") or {}).get("applied"):
                b *= out["split_adjustment"]["ratio_used"]
        why, xrec = _sc.exchange_test(filed, b, u, ui, norm)
        if why:
            return f"current YTD to {end}: {why}"
    k = filed / (filed + u)
    out["ttm_shares_diluted_filed"] = filed
    out["ttm_shares_diluted"] = filed + u
    rescaled = []
    for path in SC_PER_SHARE_FIELDS:
        parent = out
        for key in path[:-1]:
            parent = parent.get(key) if isinstance(parent, dict) else None
        v = parent.get(path[-1]) if isinstance(parent, dict) else None
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            parent[path[-1] + "_filed_basis"] = v
            parent[path[-1]] = v * k
            rescaled.append(".".join(path))
    out["share_classes"] = {"declaration_sha256": _sc.declaration_sha256(decl), "basis": norm["basis"], "leg": leg,
                            "period_end": end, "period_start": start, "units_equivalent": u, "included_units": ui,
                            "units_split_factor": f, "units_split_basis": ubasis, "split_source": ev and ev[2],
                            "exchange_test": xrec, "diluted_minus_basic": xrec.get("gap"), "zero_period": u == 0,
                            "classes": _sc.period_detail(norm, end), "filed_traded": filed, "total_units": filed + u,
                            "rescale_factor": k, "rescaled_fields": rescaled,
                            # rule 6 on the TTM leg (review 2026-10-21 finding 5): make_score refuses it without
                            # share_classes.ack_reason, as for an engine FY row
                            "out_of_band": _sc.out_of_band(u, filed)}
    sh_leg["basis"] = (sh_leg.get("basis") or "") + " + declared share-class units (judgment.json share_classes)"
    return None


CORE_FX_TAGS = (("us-gaap", "NetCashProvidedByUsedInOperatingActivities"), ("us-gaap", "Revenues"),
                ("us-gaap", "NetIncomeLoss"), ("ifrs-full", "CashFlowsFromUsedInOperatingActivities"),
                ("ifrs-full", "Revenue"), ("ifrs-full", "ProfitLoss"))


def foreign_reporting_currencies(facts):
    """[v5.5 — Codex, PR #31] Non-USD units on the filer's core facts (OCF / revenue / net income, us-gaap or IFRS)
    ending within three years of its latest core fact: a filer that reports (or once reported) in a foreign currency
    and files USD translations alongside (JD, HTHT). Empty for a USD reporter."""
    entries = []
    for tax, tag in CORE_FX_TAGS:
        for u, arr in (((facts.get("facts", {}).get(tax) or {}).get(tag) or {}).get("units") or {}).items():
            for e in arr:
                if e.get("end"):
                    entries.append((e["end"], u))
    if not entries:
        return set()
    latest = max(end for end, _ in entries)
    cutoff = f"{int(latest[:4]) - 3}{latest[4:]}"
    return {u for end, u in entries if end >= cutoff and u not in ("USD", "USD/shares", "shares", "pure")}


def nonusd_intangible_periods(facts):
    """[PR #31 verifier] {(start, end): {units}} for intangible-purchase facts (the shared us-gaap list) the annual
    engine would convert and add but ttm.py's USD-only reading cannot include: a POSITIVE amount in a unit other than
    USD, on a tag that files no USD fact for that exact period (the engine prefers a tag's USD fact, drops negative
    intangible facts and adds nothing for a $0 one)."""
    out = {}
    for t in _engine.CAPEX_INTANGIBLE_TAGS:
        if not isinstance(t, str):
            continue
        units = ((facts.get("facts", {}).get("us-gaap", {}).get(t) or {}).get("units") or {})
        usd_periods = {(e.get("start"), e.get("end")) for e in units.get("USD") or [] if e.get("form", "") in FORMS}
        for u, arr in units.items():
            if u == "USD":
                continue
            for e in arr:
                per = (e.get("start"), e.get("end"))
                if (e.get("form", "") in FORMS and per[0] and per[1] and per not in usd_periods
                        and isinstance(e.get("val"), (int, float)) and e["val"] > 0):
                    out.setdefault(per, set()).add(u)
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
            # v5.7 (L8, R6 rule 10): the shares_override's attested basis — a YTD leg it fills takes declared units only
            # when it is the traded-class count (apply_share_classes)
            if field == "shares" and isinstance(o.get("share_basis"), str) and o["share_basis"].strip():
                out[field]["share_basis"] = o["share_basis"].strip()
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
    if "--interim" in sys.argv or "--interim-draft" in sys.argv:   # v5.7 (L4, R2a): the declared 6-K bridge
        return interim_cli(ticker, cik)
    facts = get_json(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json")

    problems, warnings = [], []
    overrides = load_overrides(ticker)
    overrides_used = []
    # [v5.5 — Codex, PR #31] ttm.py's legs are USD only and it holds no FX rates: a capex / SBC override is used
    # verbatim only when it declares currency "USD" or the filer has no non-USD core facts. At a filer reporting in
    # another currency (USD translations alongside, JD / HTHT) an undeclared override would put local-currency
    # amounts into USD legs, so it is refused and the TTM is not built (exit 3).
    # [PR #31 verifier] refused only where it would FILL a leg (assemble below): with every leg filed the override
    # fills nothing and the TTM builds as before.
    _foreign = foreign_reporting_currencies(facts)
    ccy_refused = {}
    for _field in ("capex", "sbc"):
        _o = overrides.get(_field)
        if _o and _o.get("currency") != "USD" and _foreign:
            ccy_refused[_field] = (f"{_field}: the {_field}_override is not declared currency \"USD\" at a filer whose "
                                   f"core facts are filed in {', '.join(sorted(_foreign))} — ttm.py's legs are USD only "
                                   "and it cannot convert the override to fill a missing leg; declare the filing's "
                                   "US-dollar figure with currency \"USD\", or leave the TTM unbuilt")
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
            elif field in ccy_refused:
                if ccy_refused[field] not in problems:
                    problems.append(ccy_refused[field])
                legs[leg] = (per, 0.0, "REFUSED")
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
        capex_superseded = superseded_capex_legs(capex, overrides["capex"]["value"], warnings,
                                                 capex_results)   # [ADDITION — E10]; v5.7: the retag twin rule
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
        # [Codex review 3, PR #31] ttm.py reads USD facts only and holds no FX rates: a leg whose intangible
        # purchases are filed only in another currency would enter this TTM as $0 while the annual engine converts
        # and adds them (an overstated pin), so the TTM is refused (exit 3) — never on an override-filled leg, where
        # intangibles are not added
        _nonusd = nonusd_intangible_periods(facts)
        for _leg in ("fy", "ytd_prior", "ytd_current"):
            _per = tuple(capex.get(f"{_leg}_period") or ())
            _comp = (capex_components or {}).get(_leg)
            if (_per in _nonusd and isinstance(_comp, dict) and not _comp.get("intangibles")
                    and capex.get(f"{_leg}_tag") != "OVERRIDE"):
                problems.append(f"capex {_leg}: intangible purchases for {_per[0]}..{_per[1]} are filed only in "
                                f"{', '.join(sorted(_nonusd[_per]))}; ttm.py reads USD facts only and holds no FX rates, so "
                                "it cannot include them (the annual engine converts and adds them) — no TTM base; use the "
                                "median base")

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
           "sbc_reconciliation_withdrawn_legs": sbc_withdrawn,
           # v5.7 (R8/R9 TTM provenance): the engine release whose capex / SBC rules built this file; the engine
           # records it as ttm_inputs.ttm_engine_release and make_score refuses a 5.7 run whose basis read a
           # ttm.json without a 5.7 stamp
           "engine_release": _engine.ENGINE_RELEASE}
    # v5.7 (L8, R6; 08 §5.1): a share_classes declaration puts the TTM on total economic units (refused: nothing written)
    _sc_err = apply_share_classes(out, ticker, BASE, facts, overrides, leg="ytd_10q")
    if _sc_err:
        print(f"BAD_SHARE_CLASSES for {ticker}: {_sc_err}", file=sys.stderr)
        sys.exit(3)
    if not os.environ.get("DCF_TTM_NO_WRITE"):
        # Machine-readable provenance for the base pin: the engine's --ttm
        # reads this file, and make_score.py refuses a pinned base that
        # differs from it by >0.1%.
        with open(f"{BASE}/{ticker}/ttm.json", "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))


# ===========================================================================
# v5.7 (lane L4 — Andrew's ruling R2a, 2026-10-19): --interim / --interim-draft, the declared 6-K interim bridge
# ===========================================================================
# A 20-F / 40-F filer's TTM = the engine's own latest FY leg - the prior-year interim + the current interim, per leg,
# each interim leg DECLARED in judgment.json interim_bridge (accession / document / section, a verbatim snippet) and
# converted at its own period-end rate; interim_bridge.py holds the rules, ttm.py builds the record, make_score
# re-verifies it. Exit 0 = ttm.json written (unless DCF_TTM_NO_WRITE); 3 = a rule refused (the same code make_score
# reads as "ttm.py decided"); 4 = a fetch failed (EDGAR, the 6-K instance, an ECB rate) — retry.
INTERIM_REFUSED, INTERIM_FETCH_FAILED = 3, 4
REPORT_TAG = "6-K"
_FY_FORMS = ("10-K", "10-K/A", "20-F", "40-F")


def fetch_submissions(cik):
    """EDGAR submissions (dcf_engine.edgar_submissions; raises on failure). Tests patch it."""
    return _engine.edgar_submissions(cik)


def fetch_report_instance(cik, filing):
    """The 6-K's own XBRL 2.1 instance as an (instance bytes, instance URL) pair — (None, None) when its folder holds
    none (xbrl_instance.locate_instance; the lane's (bytes, url) convention). A non-404 fetch failure raises. Tests
    patch it."""
    import xbrl_instance as _xi
    return _xi.locate_instance(cik, filing.get("accession"), filing.get("primary"), filing.get("form"),
                               filing.get("period"))


def fx_rate(ccy, date):
    """The ECB reference rate ccy -> USD for date (dcf_engine.fx_rate: frankfurter, closest business day); None when
    unavailable. Tests patch it."""
    return _engine.fx_rate(ccy, date)


def _pair(t):
    return t if isinstance(t, tuple) else ("us-gaap", t)


def _load_judgment(ticker):
    try:
        with open(f"{BASE}/{ticker}/judgment.json", encoding="utf-8") as f:
            j = json.load(f)
        return j if isinstance(j, dict) else {}
    except Exception:
        return {}


def load_engine_record(ticker):
    """(dcf_numbers.json, financials_history.csv rows, problems): the engine's own latest-FY leg the bridge starts from
    — its content hash verified, from this release, a 20-F / 40-F filer, with the 5.5 capex columns and the CSV's last
    row the record's latest_period_end."""
    try:
        with open(f"{BASE}/{ticker}/dcf_numbers.json", encoding="utf-8") as f:
            n = json.load(f)
    except Exception as e:
        return None, None, [f"[IB-ENG] {ticker}/dcf_numbers.json is missing or unreadable ({e}) — run the preliminary "
                            "engine pass before ttm.py --interim"]
    if not isinstance(n, dict) or not n.get("content_hash") or _engine._content_hash(n) != n.get("content_hash"):
        return n, None, ["[IB-ENG] dcf_numbers.json content_hash does not verify — the engine output was edited; rerun "
                         "the engine"]
    problems = []
    if n.get("engine_release") != _engine.ENGINE_RELEASE:
        problems.append(f"[IB-ENG] dcf_numbers.json is from release {n.get('engine_release')}, not "
                        f"{_engine.ENGINE_RELEASE} — run the preliminary engine pass under the current release before "
                        "ttm.py --interim")
    if n.get("filer_annual_form") not in ("20-F", "40-F"):
        problems.append("[IB-FORM] --interim is for 20-F / 40-F filers; a 10-K filer's TTM comes from 10-Q YTD facts "
                        f"(ttm.py without --interim) — dcf_numbers.json filer_annual_form {n.get('filer_annual_form')!r}")
    try:
        with open(f"{BASE}/{ticker}/financials_history.csv", encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
    except Exception as e:
        return n, None, problems + [f"[IB-ENG] {ticker}/financials_history.csv is missing or unreadable ({e})"]
    if not rows or "capex_ppe" not in rows[-1] or "capex_intangibles" not in rows[-1]:
        problems.append("[IB-ENG] financials_history.csv has no capex_ppe / capex_intangibles columns — rerun the engine "
                        "(release 5.5 or later)")
    elif rows[-1].get("period_end") != n.get("latest_period_end"):
        problems.append(f"[IB-ENG] financials_history.csv's last row ends {rows[-1].get('period_end')}, not the record's "
                        f"latest_period_end {n.get('latest_period_end')} — the CSV and dcf_numbers.json are not one run")
    return n, rows, problems


def _merge_committed_instance(ticker, facts, rec):
    """companyfacts plus the committed <T>/annual_instance.json when the engine read its FY from it (Part B), so the FY
    leg's units are judged on the facts the engine used."""
    import xbrl_instance as _xi
    try:
        with open(f"{BASE}/{ticker}/annual_instance.json", encoding="utf-8") as f:
            doc = json.load(f)
    except Exception as e:
        return facts, [f"[IB-ENG] dcf_numbers.json read its FY from {rec.get('accession')}'s XBRL instance but "
                       f"{ticker}/annual_instance.json is unreadable ({e})"]
    if (doc.get("accession") != rec.get("accession")
            or _xi.facts_sha256(doc.get("facts"), doc.get("conflicts")) != rec.get("facts_sha256")):
        return facts, [f"[IB-ENG] {ticker}/annual_instance.json is not the instance the engine read "
                       f"({rec.get('accession')}) — rerun the engine"]
    filing = {"form": rec.get("form"), "accession": rec.get("accession"), "filed": rec.get("filed")}
    merged, _ = _xi.merge_into_companyfacts(facts, _xi.to_companyfacts_entries(doc["facts"], filing,
                                                                               doc.get("fiscal_year_focus")))
    return merged, []


def _fy_start(facts, fy_end):
    """The start of the annual OCF fact ending at fy_end (330-380 days, fp FY, an annual form; latest filing wins)."""
    best = None
    for tax, tag in (_pair(t) for t in _engine.ENGINE_OCF_TAGS):
        for arr in (((facts.get("facts") or {}).get(tax) or {}).get(tag) or {}).get("units", {}).values():
            for e in arr:
                if (e.get("end") != fy_end or not e.get("start") or e.get("fp") != "FY"
                        or e.get("form") not in _FY_FORMS or not (330 <= days(e["start"], e["end"]) - 1 <= 380)):
                    continue
                if best is None or e.get("filed", "") > best.get("filed", ""):
                    best = e
    return best["start"] if best else None


def _csv_num(v):
    try:
        return float(v) if v not in (None, "") else None
    except ValueError:
        return None


def fy_leg_from_engine(n, rows, facts, currency):
    """(fy_leg, fy_period, problems): the engine's own latest-FY leg, never declared. USD from financials_history.csv's
    last row (ocf, capex_ppe, capex_intangibles (blank -> 0; not added on an assumed-zero row), sbc, shares_diluted);
    the filed unit from capex_provenance (PP&E / intangibles), the engine's OCF tags (period_series) and the reconciled
    SBC tag (sbc_provenance, else the engine's SBC tags). Local value = USD / the FY rate when the unit is the declared
    currency (≠ USD), = USD when both are USD; an OVERRIDE field reads its override's currency basis; anything else is
    IB-UNIT (a bridge mixes no units)."""
    problems = []
    row = rows[-1]
    fy_end = row["period_end"]
    rates = ((n.get("fx_conversion") or {}).get("rates_by_currency") or {}).get(currency) or {}
    r_fy = 1.0 if currency == "USD" else rates.get(fy_end)
    prov = (n.get("capex_provenance") or {}).get(fy_end) or {}
    ocf_unit = _engine.period_series(facts, _engine.ENGINE_OCF_TAGS, True)[3].get(fy_end)
    sp = (n.get("sbc_provenance") or {}).get(fy_end)
    sbc_unit = None
    if isinstance(sp, dict) and sp.get("used"):
        src = sp.get("share") if sp["used"] == _engine.SBC_SHARE_TAG else sp.get("allocated")
        sbc_unit = src[1] if isinstance(src, list) and len(src) == 2 else None
    if sbc_unit is None:
        sbc_unit = _engine.period_series(facts, _engine.ENGINE_SBC_TAGS, True)[3].get(fy_end)
    assumed_zero = str(row.get("capex_assumed_zero")) == "True"
    intang_rate = (prov.get("intangibles_fx") or {}).get("rate") if isinstance(prov.get("intangibles_fx"), dict) else None
    spec = (("ocf", _csv_num(row.get("ocf")), row.get("ocf_tag"), ocf_unit, "ocf", None),
            ("capex_ppe", _csv_num(row.get("capex_ppe")), row.get("capex_tag"), prov.get("ppe_unit"), "capex_ppe", "capex"),
            ("capex_intangibles", 0.0 if assumed_zero else (_csv_num(row.get("capex_intangibles")) or 0.0),
             row.get("capex_tag"), prov.get("intangibles_unit"), "capex_intangibles", "capex"),
            ("sbc", _csv_num(row.get("sbc")), row.get("sbc_tag"), sbc_unit, "sbc", "sbc"))
    fy = {}
    for field, usd, tag, unit, col, ov_key in spec:
        rec = {"usd": usd, "tag": tag, "unit": unit,
               "source": f"financials_history.csv {col} (engine {n.get('engine_release')})", "local": None}
        if usd is None:
            problems.append(f"[IB-ENG] financials_history.csv has no FY {field} for {fy_end}")
        elif tag == "OVERRIDE" and ov_key and (field != "capex_intangibles" or usd):
            ov = (n.get("override_checks") or {}).get(ov_key) or {}
            basis = ov.get("currency_basis")
            if basis == "converted" and currency != "USD":
                rec["local"] = float(ov.get("value"))     # declared in the reporting currency, converted by the engine
            elif basis in ("no_fx", "declared_usd", "last_filed_unit_usd") and currency == "USD":
                rec["local"] = usd
            else:
                problems.append(f"[IB-UNIT] the engine's FY {field} for {fy_end} is a judgment override (currency_basis "
                                f"{basis}) but the interim legs are declared in {currency} — a bridge mixes no units; "
                                "declare the legs in the override's unit")
            rec["unit"] = "OVERRIDE"
        elif usd == 0 and unit is None:
            rec["local"] = 0.0
        elif unit == currency:
            r = intang_rate if (field == "capex_intangibles" and intang_rate) else r_fy
            rec["local"] = usd if currency == "USD" else (usd / r if r else None)
        else:
            problems.append(f"[IB-UNIT] the engine's FY {field} for {fy_end} is filed in {unit} but the interim legs are "
                            f"declared in {currency} — a bridge mixes no units; declare the legs in {unit} (USD: the "
                            "report's US-dollar or convenience-translation columns)")
        fy[field] = rec
    fy["shares_diluted"] = {"value": _csv_num(row.get("shares_diluted")), "tag": row.get("shares_tag")}
    return fy, [_fy_start(facts, fy_end), fy_end], problems


def _tol(e):
    d = e.get("decimals")
    return 0.5 * 10 ** (-d) if isinstance(d, int) and not isinstance(d, bool) and d <= 0 else 0.5


def _interim_capex(entries):
    """The engine's own capex assembly (dcf_engine.capex_for_period over CAPEX_ROLLUP_TAGS / CAPEX_COMPONENT_TAGS /
    CAPEX_INTANGIBLE_TAGS) on one interim period's undimensioned facts in one unit — the single place the interim legs
    meet the capex lists (lane L9's R8 / R9 lists apply here too). Returns {"ppe": (value, tags, tolerance) | None,
    "intangibles": (value, tags, tolerance) | None, "result": capex_for_period's record}."""
    idx = {(e["taxonomy"], e["tag"]): e for e in entries}

    def grp(tags):
        return [(_engine._tag_name(t), idx[_pair(t)]["val"], idx[_pair(t)]["unit"], None) for t in tags if _pair(t) in idx]
    res = _engine.capex_for_period(grp(_engine.CAPEX_ROLLUP_TAGS), grp(_engine.CAPEX_COMPONENT_TAGS),
                                   grp(_engine.CAPEX_INTANGIBLE_TAGS))
    by_name = {_engine._tag_name(t): idx[_pair(t)] for t in (_engine.CAPEX_ROLLUP_TAGS + _engine.CAPEX_COMPONENT_TAGS
                                                              + _engine.CAPEX_INTANGIBLE_TAGS) if _pair(t) in idx}
    out = {"ppe": None, "intangibles": None, "result": res}
    if res["ppe"] is not None:
        out["ppe"] = (res["ppe"], "+".join(res["ppe_tags"]), sum(_tol(by_name[t]) for t in res["ppe_tags"]))
    if res["intangible_tags"]:
        out["intangibles"] = (res["intangibles"], "+".join(res["intangible_tags"]),
                              sum(_tol(by_name[t]) for t in res["intangible_tags"]))
    return out


def report_xbrl_values(parsed, periods, currency):
    """({(field, leg): (value, tag, tolerance)}, conflicts) — per interim leg, the undimensioned facts with the leg's
    period (start within 5 days, the same end) in unit `currency` (shares: "shares"): OCF from the engine's OCF tags in
    priority order; PP&E / intangibles from the engine's capex assembly (_interim_capex); SBC from the engine's SBC
    tags (ShareBasedCompensation / Allocated reconciled as the engine does); the diluted count from the diluted tags
    only (basic tags never verify a diluted leg)."""
    import xbrl_instance as _xi
    by_per, conflicts = _xi.interim_facts(parsed, [tuple(p) for p in periods.values()])
    out = {}
    for name, per in periods.items():
        ents = by_per.get(tuple(per)) or []
        money = [e for e in ents if e["unit"] == currency]
        idx = {(e["taxonomy"], e["tag"]): e for e in money}
        for t in _engine.ENGINE_OCF_TAGS:
            if _pair(t) in idx:
                e = idx[_pair(t)]
                out[("ocf", name)] = (e["val"], e["tag"], _tol(e))
                break
        cap = _interim_capex(money)
        if cap["ppe"] is not None:
            out[("capex_ppe", name)] = cap["ppe"]
        if cap["intangibles"] is not None:
            out[("capex_intangibles", name)] = cap["intangibles"]
        sh, al = idx.get(("us-gaap", _engine.SBC_SHARE_TAG)), idx.get(("us-gaap", _engine.SBC_ALLOCATED_TAG))
        if sh or al:
            v, _, tag, _, _ = _engine.reconcile_sbc((sh["val"], currency) if sh else None,
                                                    (al["val"], currency) if al else None)
            src = sh if tag == _engine.SBC_SHARE_TAG else al
            out[("sbc", name)] = (v, tag, _tol(src))
        else:
            for t in _engine.ENGINE_SBC_TAGS:
                if _pair(t) in idx:
                    e = idx[_pair(t)]
                    out[("sbc", name)] = (e["val"], e["tag"], _tol(e))
                    break
        if name == "current_interim":
            sidx = {(e["taxonomy"], e["tag"]): e for e in ents if e["unit"] == "shares"}
            for t in _engine.DILUTED_ONLY_TAGS:
                if _pair(t) in sidx:
                    e = sidx[_pair(t)]
                    out[("shares_diluted", name)] = (e["val"], e["tag"], _tol(e))
                    break
    return out, conflicts


def interim_basic_count(parsed, period):
    """v5.7 (L8, R6; 08 §5.4): the 6-K instance's undimensioned basic weighted count (share_classes.BASIC_TAGS: us-gaap
    basic, ifrs-full WeightedAverageShares) for the current interim period — the share-class exchange test's basic
    (companyfacts holds no 6-K count); None when the instance files none."""
    import xbrl_instance as _xi
    by_per, _ = _xi.interim_facts(parsed, [tuple(period)])
    ents = {(e["taxonomy"], e["tag"]): e for e in by_per.get(tuple(period)) or [] if e.get("unit") == "shares"}
    for t in _sc.BASIC_TAGS:
        e = ents.get(t)
        if e is not None and _sc._num(e.get("val")) is not None:
            return float(e["val"])
    return None


def iprd_interim_scan(parsed, period):
    """[(tag, value)] of acquired-IPR&D figures (dcf_engine.IPRD_EXPENSE_TAGS, IPRD_CASH_TAG; any unit, > 0) the 6-K
    files for the current interim — a charge the engine's one-time deduction cannot read (it reads 10-K / 10-Q facts).
    Rebase amendment 11 / default Q8 (main agent, 2026-10-21): refuse the bridge."""
    import xbrl_instance as _xi
    by_per, _ = _xi.interim_facts(parsed, [tuple(period)])
    names = set(_engine.IPRD_EXPENSE_TAGS) | {_engine.IPRD_CASH_TAG}
    return [(e["tag"], e["val"]) for e in by_per.get(tuple(period)) or []
            if e["taxonomy"] == "us-gaap" and e["tag"] in names and isinstance(e["val"], (int, float)) and e["val"] > 0]


def submissions_filing(sub, accession):
    """The submissions record of `accession` as {"form", "accession", "filed", "period", "primary", "isXBRL"}, else None."""
    rec = ((sub or {}).get("filings") or {}).get("recent") or {}
    accs = rec.get("accessionNumber") or []
    if accession not in accs:
        return None
    i = accs.index(accession)

    def at(k):
        col = rec.get(k) or []
        return col[i] if i < len(col) else None
    return {"form": at("form"), "accession": accession, "filed": at("filingDate"), "period": at("reportDate"),
            "primary": at("primaryDocument"), "isXBRL": at("isXBRL")}


def _interim_rates(decl, n, fy_period, problems):
    """(rates_used, fx record) — raises _FetchFailed when an ECB rate cannot be fetched. Currency ≠ USD: the FY rate is
    the engine's own (fx_conversion.rates_by_currency) and must equal the declared one (IB-FX1 / IB-FX2); each interim
    rate is FETCHED (dcf_engine.fx_rate) and the declared one must be within FX_TOLERANCE of it (IB-FX3); the fetched
    rates are used. USD legs: rates 1 (basis none, or the issuer's convenience translation, whose printed rate the
    snippet must show)."""
    ccy, fx = decl["currency"], decl["fx"]
    per = _ib.periods_of(decl)
    if ccy == "USD":
        rec = {"basis": fx["basis"], "source": fx.get("source"),
               "rates_used": {"fy": 1.0, "prior_interim": 1.0, "current_interim": 1.0}}
        if fx["basis"] == "issuer_convenience_translation":
            for name in _ib.LEG_NAMES:     # the rate snippets are judged by _ib.snippet_problems (the rule bundle)
                r = fx[name]
                rec[name] = {"date": r["date"], "rate": r["rate"], "snippet": r.get("snippet")}
        return rec["rates_used"], rec
    fy_end = fy_period[1] if fy_period else per["fy"][1]
    r_fy = (((n.get("fx_conversion") or {}).get("rates_by_currency") or {}).get(ccy) or {}).get(fy_end)
    if r_fy is None:
        problems.append(f"[IB-FX1] the engine did not convert {ccy} at {fy_end} (dcf_numbers.json fx_conversion) — the "
                        "FY leg and the interim legs must be the same currency")
    elif abs(float(fx["fy"]["rate"]) - float(r_fy)) > 1e-9:
        problems.append(f"[IB-FX2] interim_bridge.fx.fy.rate {fx['fy']['rate']} is not the engine's FY rate {r_fy} for "
                        f"{fy_end} (dcf_numbers.json fx_conversion) — copy the rate the engine used")
    used = {"fy": r_fy}
    rec = {"basis": "ecb_period_end", "source": fx.get("source"),
           "fy": {"date": fy_end, "rate": r_fy, "source": "dcf_numbers.json fx_conversion (the engine's FY conversion)"}}
    for name in _ib.LEG_NAMES:
        end = per[name][1]
        got = fx_rate(ccy, end)
        if got is None:
            raise _FetchFailed(f"the ECB {ccy}/USD reference rate for {end}", "frankfurter returned none")
        dec = float(fx[name]["rate"])
        if abs(dec - got) > _ib.FX_TOLERANCE * got:
            problems.append(f"[IB-FX3] interim_bridge.fx.{name}.rate {dec} is not the ECB reference rate {got} for {end} "
                            "(frankfurter, closest business day) — copy the rate ttm.py prints")
        used[name] = float(got)
        rec[name] = {"date": end, "rate": float(got), "declared": dec, "source": "ECB via frankfurter (dcf_engine.fx_rate)"}
    rec["rates_used"] = used
    return used, rec


class _FetchFailed(Exception):
    def __init__(self, what, err):
        super().__init__(what)
        self.what, self.err = what, err


def build_interim(ticker, cik, j, decl, n, rows, facts, today=None):
    """(ttm.json record | None, problems, warnings) — every rule of the declared bridge (design 04 A.3 steps 4-14).
    Raises _FetchFailed when EDGAR or an ECB rate cannot be read and no rule has refused yet; once one has, the run
    refuses (exit 3) on the rules found so far — retrying a fetch would not make it scoreable."""
    problems, warnings = [], []
    try:
        return _build_interim(ticker, cik, j, decl, n, rows, facts, today, problems, warnings)
    except _FetchFailed as e:
        if not problems:
            raise
        return None, problems + [f"(not checked: {e.what} unavailable — {e.err})"], warnings


def _build_interim(ticker, cik, j, decl, n, rows, facts, today, problems, warnings):
    ccy = decl["currency"]
    rep_acc = decl["report"]["accession"]
    per = _ib.periods_of(decl)
    today = today or _engine.ET_TODAY.isoformat()
    fy, fy_period, p = fy_leg_from_engine(n, rows, facts, ccy)
    problems += p
    if fy_period[0] is None:
        problems.append(f"[IB-ENG] no annual operating cash flow fact ends at the engine's FY end {fy_period[1]} — the FY "
                        "start cannot be read")
        fy_period = None
    rates, fx_rec = _interim_rates(decl, n, fy_period, problems)
    try:
        sub = fetch_submissions(cik)
    except Exception as e:
        raise _FetchFailed("EDGAR submissions", e)
    filing = submissions_filing(sub, rep_acc)
    if filing is None:
        problems.append(f"[IB-SRC1] accession {rep_acc} not found in EDGAR submissions")
    elif filing["form"] not in _ib.REPORT_FORMS:
        problems.append(f"[IB-SRC1] accession {rep_acc} is {filing['form']}, not a 6-K — the bridge reads 6-K interim "
                        "reports (a 10-Q filer uses ttm.py without --interim)")
    fy_local = {f: fy[f]["local"] for f in _ib.FLOW_FIELDS}
    fy_usd = {f: fy[f]["usd"] for f in _ib.FLOW_FIELDS}
    fy_shares = fy["shares_diluted"]["value"]
    # v5.7 (L8, 08 §5.4): on a declared engine record the CSV's FY count is total units — IB-SH1, the warning band and
    # the fy_diluted_count estimate compare with the FILED traded FY count (else the units would be added twice)
    fy_total_units = fy_shares
    _sc_fy = next((a for a in ((n.get("share_classes") or {}).get("applied") or [])
                   if isinstance(a, dict) and a.get("period_end") == (fy_period[1] if fy_period else None)), None) \
        if isinstance(n.get("share_classes"), dict) else None
    if _sc_fy and isinstance(_sc_fy.get("filed_traded"), (int, float)):
        fy_shares = float(_sc_fy["filed_traded"])
    ib_basic = None   # v5.7 (L8): the 6-K instance's basic weighted count for the current interim (the exchange test)
    # every pure rule, in the one bundle make_score re-runs on the record (review fix 2026-10-21); the report's own
    # period is not known yet (an XBRL 6-K's comes from its instance below), the filing date is
    filed = (filing or {}).get("filed")
    problems += _ib.declaration_rule_problems(decl, fy_period, fy_local, fy_usd, fy_shares, today, report_date=None,
                                              filed=filed)
    is_xbrl = bool(filing) and str(filing.get("isXBRL")) == "1"
    period_end, period_src = None, None
    verified, xbrl_seen = {}, {}
    iprd_scan = "not_scanned (the report has no XBRL instance)"
    instance_url = None
    if is_xbrl:
        try:
            data, instance_url = fetch_report_instance(cik, filing)
        except Exception as e:
            raise _FetchFailed("the 6-K's XBRL instance", e)
        if not data:
            raise _FetchFailed("the 6-K's XBRL instance", "EDGAR lists the report as XBRL but its folder holds no instance")
        import xbrl_instance as _xi
        try:
            parsed = _xi.parse_undimensioned(data)
        except Exception as e:
            problems.append(f"[IB-XBRL0] the 6-K's XBRL instance is unreadable ({e}) — the declared legs cannot be "
                            "verified against it")
            parsed = None
        if parsed is not None:
            # IB-P5's report period: the instance's own dei DocumentPeriodEndDate (EDGAR's reportDate the fallback)
            period_end, period_src = _ib.report_period_end(True, (parsed.get("dei") or {}).get("DocumentPeriodEndDate"),
                                                           filing.get("period"))
            problems += _ib.check_report_period(decl, period_end, period_src)
            vals, conflicts = report_xbrl_values(parsed, {k: per[k] for k in _ib.LEG_NAMES}, ccy)
            ib_basic = interim_basic_count(parsed, per["current_interim"])   # v5.7 (L8)
            if conflicts:
                warnings.append("the 6-K's XBRL instance carries conflicting values for "
                                + ", ".join(f"{c['tag']} {c['start']}..{c['end']}" for c in conflicts) + " (not read)")
            for (f, name), (v, tag, tol) in sorted(vals.items()):
                x = _ib.leg(decl, f, name)
                if x is None:
                    continue
                xbrl_seen[(f, name)] = (v, tag)
                if x.get("kind") == "estimate":
                    problems.append(f"[IB-XBRL2] {f}.{name} is declared kind estimate but the report files {tag} = {v:,} "
                                    f"for {per[name][0]}..{per[name][1]} — declare it kind filing")
                elif abs(float(x["value"]) - float(v)) > tol:
                    problems.append(f"[IB-XBRL1] {f}.{name} declares {x['value']:,} but the report's XBRL files {tag} = "
                                    f"{v:,} for {per[name][0]}..{per[name][1]}")
                else:
                    verified[(f, name)] = "xbrl_instance"
            hits = iprd_interim_scan(parsed, per["current_interim"])
            if hits:
                for tag, v in hits:
                    problems.append(f"[IB-IPRD] the 6-K files {tag} = {v:,} for {per['current_interim'][0]}.."
                                    f"{per['current_interim'][1]}: an acquired-IPR&D charge in the current interim, which "
                                    "the engine's one-time deduction cannot read (it reads 10-K / 10-Q facts) — block "
                                    "NEEDS_MAIN_AGENT: base")
                iprd_scan = "xbrl_instance: " + ", ".join(f"{t} {v:,}" for t, v in hits)
            else:
                iprd_scan = "xbrl_instance: none"
    else:
        warnings.append("the 6-K has no XBRL instance (EDGAR isXBRL 0): every filing leg is verified by its snippet only, "
                        "and no acquired-IPR&D charge in the current interim can be detected")
        if filing:
            warnings.append(f"EDGAR's reportDate {filing.get('period')} for a 6-K without XBRL is its cover date, not the "
                            "interim's period end: IB-P5 checks only that the current interim ended before the report "
                            f"was filed ({filed})")
    sx = _ib.leg(decl, _ib.SHARES_FIELD, "current_interim")
    if sx and sx.get("kind") == "estimate" and sx.get("method") == "fy_diluted_count":
        warnings.append("shares_diluted.current_interim is the FY diluted count (fy_diluted_count): the report prints no "
                        "diluted count for the interim")
    ads = (j.get("ads_ratio") or {}).get("ratio") if isinstance(j.get("ads_ratio"), dict) else None
    n_ads = (n.get("ads_ratio") or {}).get("ratio") if isinstance(n.get("ads_ratio"), dict) else None
    if not (isinstance(ads, (int, float)) and not isinstance(ads, bool) and ads > 0):
        problems.append("[IB-ADS] a 20-F / 40-F bridge needs judgment.json ads_ratio — the pin is per ADS, like the price "
                        "(the engine takes TTM pins as per-ADS already)")
    elif n_ads is None or abs(float(ads) - float(n_ads)) > 1e-12:
        problems.append(f"[IB-ADS] judgment.json ads_ratio {ads} is not the ratio the engine applied ({n_ads}) — rerun the "
                        "engine with the current judgment.json")
    if problems or any(fy[f]["local"] is None for f in _ib.FLOW_FIELDS) or rates.get("fy") is None:
        return None, problems or ["[IB-UNIT] the engine's FY leg could not be read in the declared currency"], warnings
    out = _ib.compute(decl, {f: {"local": fy[f]["local"], "usd": fy[f]["usd"]} for f in _ib.FLOW_FIELDS},
                      rates, float(ads))
    shares = out["ttm_shares_diluted"]
    if fy_shares:
        ratio = shares / fy_shares          # outside 1/10-10x already refused (IB-SH1, _ib.check_share_band)
        if not (_engine.DIVERGENCE_BAND[0] <= ratio <= _engine.DIVERGENCE_BAND[1]):
            warnings.append(f"shares: the current-interim diluted count {shares:,.0f} is {ratio:.4g}x the FY diluted count "
                            f"{fy_shares:,.0f} (outside {_engine.DIVERGENCE_BAND[0]}-{_engine.DIVERGENCE_BAND[1]}x) — check "
                            "for a split, a large issuance or a different share class")
    else:
        ratio = None
    if problems:
        return None, problems, warnings
    est, unv = _ib.leg_lists(decl)
    acc_tag = f"{REPORT_TAG} {rep_acc}"
    legs, prov = {}, []
    for f in _ib.FLOW_FIELDS:
        lr = out["legs"][f]
        legs[f] = {"fy": dict(fy[f], local=lr["fy"]["local"], usd=lr["fy"]["usd"]),
                   "ttm_local": lr["ttm_local"], "ttm_usd": lr["ttm_usd"]}
        for name in _ib.LEG_NAMES:
            x = _ib.leg(decl, f, name)
            rec = {"local": lr[name]["local"], "usd": lr[name]["usd"], "kind": x["kind"],
                   "verified": ("estimate" if x["kind"] == "estimate" else verified.get((f, name), "snippet"))}
            if x["kind"] == "estimate":
                rec["method"] = x.get("method")
            if (f, name) in xbrl_seen:
                rec["xbrl_tag"], rec["xbrl_value"] = xbrl_seen[(f, name)][1], xbrl_seen[(f, name)][0]
            legs[f][name] = rec
            if x["kind"] == "filing":
                src = x.get("source") or {}
                prov.append({"field": f, "leg": name, "accession": src.get("accession"), "document": src.get("document"),
                             "page": src.get("page"), "section": src.get("section"), "snippet": x.get("snippet"),
                             "verified": rec["verified"], "xbrl_tag": rec.get("xbrl_tag")})
    srec = {"value": shares, "kind": sx["kind"],
            "verified": "estimate" if sx["kind"] == "estimate" else verified.get(("shares_diluted", "current_interim"), "snippet")}
    if sx["kind"] == "estimate":
        srec["method"] = sx.get("method")
    if ("shares_diluted", "current_interim") in xbrl_seen:
        srec["xbrl_tag"], srec["xbrl_value"] = xbrl_seen[("shares_diluted", "current_interim")][1], \
            xbrl_seen[("shares_diluted", "current_interim")][0]
    if sx.get("share_basis") is not None:
        srec["share_basis"] = sx["share_basis"]
    if sx["kind"] == "filing":
        src = sx.get("source") or {}
        prov.append({"field": "shares_diluted", "leg": "current_interim", "accession": src.get("accession"),
                     "document": src.get("document"), "page": src.get("page"), "section": src.get("section"),
                     "snippet": sx.get("snippet"), "verified": srec["verified"], "xbrl_tag": srec.get("xbrl_tag")})
    # v5.7 share classes (L8, 08 §15 item 3b): apply_share_classes(..., leg="interim", ...) runs on the finished record
    # below (it rescales the override zero-fill too)
    filled = {}
    if fy["capex_ppe"]["tag"] == "OVERRIDE":
        filled["capex"] = out["ttm_capex"]
    if fy["sbc"]["tag"] == "OVERRIDE":
        filled["sbc"] = out["ttm_sbc"]
    if fy["shares_diluted"].get("tag") == "OVERRIDE":
        warnings.append("the engine's FY diluted count is a shares_override; the TTM denominator is the current interim's "
                        "declared count, so the override does not move the bridged base")
    cf = None
    if filled:
        zf = out["ttm_oe_total"] + sum(filled.values())
        cf = {"fy_fields_override_filled": filled, "ttm_oe_total_zero_fill": zf,
              "base_oe_per_share_zero_fill": zf / shares * float(ads)}

    def _inp(field_vals, tag_fy):
        fyv, pv, cv, tv = field_vals
        return {"fy": fyv, "fy_period": list(fy_period), "fy_tag": tag_fy, "ytd_prior": pv,
                "ytd_prior_period": list(per["prior_interim"]), "ytd_prior_tag": acc_tag, "ytd_current": cv,
                "ytd_current_period": list(per["current_interim"]), "ytd_current_tag": acc_tag, "ttm": tv}
    L = out["legs"]
    cap = [L["capex_ppe"][k]["usd"] + L["capex_intangibles"][k]["usd"] for k in ("fy", "prior_interim", "current_interim")]
    inputs = {"ocf": _inp((L["ocf"]["fy"]["usd"], L["ocf"]["prior_interim"]["usd"], L["ocf"]["current_interim"]["usd"],
                           out["ttm_ocf"]), "ENGINE_FY"),
              "capex": _inp((cap[0], cap[1], cap[2], out["ttm_capex"]), "ENGINE_FY"),
              "sbc": _inp((L["sbc"]["fy"]["usd"], L["sbc"]["prior_interim"]["usd"], L["sbc"]["current_interim"]["usd"],
                           out["ttm_sbc"]), "ENGINE_FY"),
              "shares_diluted": {"ytd_current": shares, "ytd_current_period": list(per["current_interim"]),
                                 "ytd_current_tag": acc_tag,
                                 "basis": "ttm_shares_diluted = current interim weighted average diluted shares (declared, 6-K)"}}
    lfl = dict(decl["like_for_like"])
    lfl["checks_passed"] = ["IB-LFL1", "IB-LFL2", "IB-LFL3", "IB-LFL4", "IB-LFL5"]
    rec = {"ticker": ticker, "cik": cik, "entity": facts.get("entityName"),
           "basis": _ib.RECORD_BASIS,
           "engine_release": _engine.ENGINE_RELEASE,
           "built_by": f"ttm.py --interim (release {_engine.ENGINE_RELEASE})",
           "declaration_hash": _ib.declaration_hash(decl),
           "engine_record": {"engine_release": n.get("engine_release"), "content_hash": n.get("content_hash"),
                             "latest_period_end": n.get("latest_period_end")},
           "fy_end": fy_period[1], "ytd_end": per["current_interim"][1],
           "currency": ccy,
           "periods": {"fy": list(fy_period), "prior_interim": list(per["prior_interim"]),
                       "current_interim": list(per["current_interim"])},
           "report": {"form": filing["form"], "accession": rep_acc, "document": decl["report"].get("document"),
                      "filed": filing.get("filed"), "report_date": filing.get("period"),
                      "is_xbrl": is_xbrl, "instance_url": instance_url,
                      # IB-P5's report period (make_score re-runs the rule on it): an XBRL 6-K's dei period end; null
                      # for a 6-K without XBRL (its EDGAR reportDate is the cover date)
                      "period_end": period_end, "period_end_source": period_src},
           "fx": fx_rec,
           "legs": legs,
           "shares": {"current_interim": srec, "fy_diluted": fy_shares, "ratio_to_fy": ratio},
           "ads_ratio": float(ads),
           "inputs": inputs,
           "ttm_ocf": out["ttm_ocf"], "ttm_capex": out["ttm_capex"], "ttm_sbc": out["ttm_sbc"],
           "ttm_shares_diluted": shares, "ttm_oe_total": out["ttm_oe_total"],
           "ttm_oe_total_local": out["ttm_oe_total_local"],
           "ttm_oe_per_ordinary_share": out["ttm_oe_per_ordinary_share"], "ttm_oe_per_share": out["ttm_oe_per_share"],
           "estimate_legs": est, "unverified_legs": unv,
           "xbrl_verified_legs": [f"{f}.{name}" for (f, name), how in sorted(verified.items()) if how == "xbrl_instance"],
           "iprd_interim_scan": iprd_scan,
           "like_for_like": lfl,
           "override_counterfactual": cf,
           "provenance": prov,
           "warnings": warnings, "overrides_used": [],
           # the 10-Q path's provenance keys, empty here (a declared bridge assembles no capex / SBC / split per leg)
           "capex_components": None, "sbc_reconciled_legs": {}, "split_adjustment": None,
           "capex_override_superseded_legs": {}, "sbc_reconciliation_withdrawn_legs": {}}
    # v5.7 (L8, R6; 08 §5.4): a share_classes declaration rescales every per-share figure of the bridge (the per-ADS pin,
    # the per-ordinary figure, the override zero-fill) to total economic units; refused like any other bridge rule
    if fy_total_units != fy_shares:
        rec["shares"]["fy_total_units"] = fy_total_units
    _sc_err = apply_share_classes(rec, ticker, BASE, facts, {}, leg="interim", engine_record=n,
                                  interim={"period": list(per["current_interim"]), "shares_leg": sx, "basic": ib_basic})
    if _sc_err:
        return None, [f"[IB-SC] {_sc_err}"], warnings
    return rec, [], warnings


def _interim_cik(ticker, cik_resolved, n):
    if "--cik" in sys.argv:
        return int(sys.argv[sys.argv.index("--cik") + 1])
    return int((n or {}).get("cik") or cik_resolved)


def interim_main(ticker, cik):
    """ttm.py <TICKER> --interim: build <T>/ttm.json from judgment.json interim_bridge (design 04 A.3)."""
    shown = [cik]

    def refuse(ps):
        print(f"ttm.py --interim: cannot build the declared interim bridge for {ticker} (CIK {shown[0]}): " + "; ".join(ps),
              file=sys.stderr)
        sys.exit(INTERIM_REFUSED)

    def fetch_failed(what, err):
        print(f"ttm.py --interim: cannot verify the interim bridge for {ticker}: {what} unavailable ({err}) — retry",
              file=sys.stderr)
        sys.exit(INTERIM_FETCH_FAILED)
    j = _load_judgment(ticker)
    decl = j.get("interim_bridge")
    if decl is None:
        refuse(["[IB-SHAPE] judgment.json declares no interim_bridge — --interim builds ttm.json only from a declared "
                "bridge"])
    shape = _ib.validate_shape(decl)
    if shape:
        refuse(shape)
    n, rows, eng = load_engine_record(ticker)
    if eng or rows is None:
        refuse(eng or ["[IB-ENG] financials_history.csv is missing"])
    cik = _interim_cik(ticker, cik, n)
    shown[0] = cik
    try:
        facts = get_json(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json")
    except Exception as e:
        fetch_failed("EDGAR companyfacts", e)
    ai = n.get("annual_from_instance") or {}
    if ai.get("applied"):
        facts, p = _merge_committed_instance(ticker, facts, ai)
        if p:
            refuse(p)
    try:
        rec, problems, warnings = build_interim(ticker, cik, j, decl, n, rows, facts)
    except _FetchFailed as e:
        fetch_failed(e.what, e.err)
    if problems:
        refuse(problems)
    if not os.environ.get("DCF_TTM_NO_WRITE"):
        with open(f"{BASE}/{ticker}/ttm.json", "w", encoding="utf-8") as f:
            json.dump(rec, f, indent=1)
    print(json.dumps(rec, indent=1))


def _draft_periods(parsed, fy_period, report_date):
    """(prior [s, e], current [s, e]) the 6-K's durations suggest: the current interim starts 1-10 days after the FY
    end and ends at the report's period; the prior one ends a year earlier (±6 days) and starts at the FY start (±5)."""
    durs = {(f["start"], f["end"]) for f in parsed["facts"] if f["instant"] is None}
    cur = sorted((s, e) for s, e in durs if e == report_date and 1 <= days(fy_period[1], s) - 1 <= 10)
    if not cur:
        return None, None
    cs, ce = cur[0]
    target = shift_year(ce, -1)
    pri = sorted((abs(days(target, e) - 1), s, e) for s, e in durs
                 if abs(days(target, e) - 1) <= 6 and abs(days(fy_period[0], s) - 1) <= 5)
    return ([pri[0][1], pri[0][2]] if pri else None), [cs, ce]


def interim_draft_main(ticker, cik, accession):
    """ttm.py <TICKER> --interim-draft <6-K accession>: prints a draft interim_bridge (every leg the 6-K's XBRL files,
    the periods, the ECB rates for both interim ends and the engine's FY rate, "TODO" markers for snippets,
    like_for_like and missing legs). Writes nothing; exit 3 / 4 as --interim."""
    def refuse(ps):
        print(f"ttm.py --interim-draft: cannot draft the interim bridge for {ticker} (CIK {cik}): " + "; ".join(ps),
              file=sys.stderr)
        sys.exit(INTERIM_REFUSED)

    def fetch_failed(what, err):
        print(f"ttm.py --interim-draft: {what} unavailable for {ticker} ({err}) — retry", file=sys.stderr)
        sys.exit(INTERIM_FETCH_FAILED)
    n, rows, eng = load_engine_record(ticker)
    if n is None or rows is None:
        refuse(eng)
    cik = _interim_cik(ticker, cik, n)
    try:
        facts = get_json(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json")
        sub = fetch_submissions(cik)
    except Exception as e:
        fetch_failed("EDGAR companyfacts / submissions", e)
    filing = submissions_filing(sub, accession)
    if filing is None or filing["form"] not in _ib.REPORT_FORMS:
        refuse([f"[IB-SRC1] accession {accession} is not a 6-K in EDGAR submissions"])
    if str(filing.get("isXBRL")) != "1":
        refuse([f"the 6-K {accession} has no XBRL instance (EDGAR isXBRL 0) — draft the bridge by hand from the report"])
    try:
        data, url = fetch_report_instance(cik, filing)
    except Exception as e:
        fetch_failed("the 6-K's XBRL instance", e)
    if not data:
        fetch_failed("the 6-K's XBRL instance", "no instance in the filing folder")
    import xbrl_instance as _xi
    parsed = _xi.parse_undimensioned(data)
    fy_end = n.get("latest_period_end")
    fy_period = [_fy_start(facts, fy_end), fy_end]
    if fy_period[0] is None:
        refuse([f"[IB-ENG] no annual operating cash flow fact ends at the engine's FY end {fy_end}"])
    rp, _src = _ib.report_period_end(True, (parsed.get("dei") or {}).get("DocumentPeriodEndDate"), filing.get("period"))
    prior, cur = _draft_periods(parsed, fy_period, rp)
    if cur is None:
        refuse([f"the 6-K's XBRL instance files no duration ending at the report's period {rp} ({_src}) that starts "
                f"1-10 days after the FY end {fy_end}"])
    fxc = n.get("fx_conversion") or {}
    ccy = fxc.get("from_currency") or "USD"
    periods = {"prior_interim": prior or ["TODO", "TODO"], "current_interim": cur}
    vals, _ = report_xbrl_values(parsed, {k: v for k, v in periods.items() if "TODO" not in v}, ccy)
    todo_src = {"accession": accession, "document": filing.get("primary"), "page": None, "section": "TODO"}
    legs = {}
    for f in _ib.FLOW_FIELDS + (_ib.SHARES_FIELD,):
        legs[f] = {}
        for name in (("current_interim",) if f == _ib.SHARES_FIELD else _ib.LEG_NAMES):
            v = vals.get((f, name))
            legs[f][name] = ({"value": v[0], "kind": "filing", "source": dict(todo_src), "snippet": "TODO: the report's "
                              f"words showing {v[0]:,} (at most {_ib.SNIPPET_MAX_WORDS})", "reason": "TODO",
                              "_xbrl_tag": v[1]}
                             if v else {"value": None, "kind": "TODO: filing (from the report) or estimate with a method "
                                        f"({', '.join(m for m, fs in _ib.ESTIMATE_METHODS.items() if f in fs) or 'none'})",
                                        "reason": "TODO: the 6-K's XBRL files no undimensioned fact for this leg"})
    if _load_judgment(ticker).get("share_classes") is not None:
        # v5.7 (L8, R6; 08 §5.4): at a declaring filer the share leg is the traded-class count (units go on top of it)
        legs[_ib.SHARES_FIELD]["current_interim"]["share_basis"] = "traded_class"
    fx = {"basis": "ecb_period_end" if ccy != "USD" else "none",
          "source": "frankfurter.app ECB reference rates (dcf_engine.fx_rate), closest business day to each period end"}
    if ccy != "USD":
        fx["fy"] = {"date": fy_end, "rate": ((fxc.get("rates_by_currency") or {}).get(ccy) or {}).get(fy_end)}
        for name, p in periods.items():
            fx[name] = {"date": p[1], "rate": fx_rate(ccy, p[1]) if "TODO" not in p else None}
    draft = {"basis": _ib.BASIS, "currency": ccy, "fy_period": fy_period,
             "prior_interim": {"period": periods["prior_interim"]}, "current_interim": {"period": cur},
             "report": {"form": filing["form"], "accession": accession, "document": filing.get("primary"),
                        "filed": filing.get("filed"), "title": "TODO"},
             "legs": legs,
             "like_for_like": {"comparative_restated": "TODO: true / false", "comparative_note": "TODO",
                               "perimeter_changes": "TODO: [] or each acquisition / disposal / demerger in "
                                                    f"{periods['prior_interim'][0]}..{cur[1]}"},
             "fx": fx, "reason": "TODO: why the bridge is the right base (with a number)"}
    print(json.dumps({"interim_bridge": draft, "instance_url": url}, indent=1))


def interim_cli(ticker, cik):
    """The --interim / --interim-draft entry point (main() dispatches here before any 10-Q work)."""
    if "--interim-draft" in sys.argv:
        i = sys.argv.index("--interim-draft")
        acc = sys.argv[i + 1] if i + 1 < len(sys.argv) else None
        if not acc or acc.startswith("--"):
            print("ttm.py --interim-draft: give the 6-K accession (NNNNNNNNNN-YY-NNNNNN)", file=sys.stderr)
            sys.exit(2)
        return interim_draft_main(ticker, cik, acc)
    return interim_main(ticker, cik)


if __name__ == "__main__":
    main()
