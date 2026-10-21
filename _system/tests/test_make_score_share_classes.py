#!/usr/bin/env python3
"""make_score.py and declared share classes — engine 5.7, Andrew's ruling R6 (2026-10-19/20); design 08 §8 with the
rebase map L8.md (A-4, A-6, A-8, A-14 … A-17, A-25, A-26). Run: python _system/tests/test_make_score_share_classes.py
(or python -m pytest). No network.

End-to-end cases run make_score.py on a synthetic 5.7 folder (test_make_score_55's Run: an engine-stamped
dcf_numbers.json carrying VNOM's share_classes record, the registry redirected) with a stand-in dcf_engine.py that
answers the filed-basis replay (DCF_NO_SHARE_CLASSES) and logs each spawn's argv and environment. The replay-pin
arithmetic is also tested in process (share_classes_impact with its replay runner stubbed).

M-1  R-1 shape refusals (validate errors, a snippet over 24 words or without its count, an out-of-band period
     without ack_reason, an optional reason without a digit).
M-2  R-2 sync refusals (another declaration_sha256, other units, the record absent, a record with no declaration).
M-3  R-3 / R-4 / R-5: the exclusive mismatch, a plain pin refused, an attested total-unit pin kept and replayed at
     pin × total ÷ filed with DCF_SC_PIN_SCALE; an iprd_amortized pin (native ttm_json: one replay; native median: two);
     a replay that misses the amortized declaration is "not measured"; the payable base refused.
M-4  the measured block and the share_classes registry event (units_by_period, never `periods`), first-date keeping,
     re-dating on an edit; M-4b a via-TTM --base-oe-ps run replays at ttm.json's filed-basis TTM; M-4c load_registry
     accepts both new events and refuses a misspelt one or one with a deferred-payment key; the release-mismatch carry.
M-5  the entry-alert gate (a declaration that RAISES the tier); exits never suppressed.
M-6  R-8 (UP_C_SUSPECT needs up_c_suspect_reason with a number on a 5.7 run; the up_c_suspect event).
M-7  key_numbers.md's share-class lines (undeclared records unchanged).
M-8  R-6 (ttm.json on another declaration); A-6 TTM_CHANGED on a rewritten declaration block.
M-9  R-7 / R-7b (the NCI and cap cross-checks).
M-10 score.json carries share_classes / up_c_check only when the engine record does.
M-11 R-10 (share_basis values; an OVERRIDE period added without the attestation).
Review fixes (2026-10-21; each fails on the lane's first build 49c125a):
M-1b the current-YTD period's units are banded too (rule 6: a --ttm record's share_classes.ttm, ttm.json's block).
M-3b R-4: a total_units-attested pin equal to a filed-basis per-share figure is refused (SC_REFUSE_FILED_BASIS_PIN).
M-4d a crashed / unparseable share-class replay refuses; only the engine's exit 3 is "not measured".
M-8b R-6 covers an iprd_amortized pin on native ttm_json and a basis_window "ttm" pin.
M-13 a declared 6-K interim bridge at a declaring filer scores end to end (step 4 on the filed-basis twins).
Every test fails on the code before this lane (4f7d6f1).
"""
import copy
import json
import os
import subprocess
import sys
import tempfile
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
for _p in (HERE, SYS):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import make_score as M  # noqa: E402
import dcf_engine as E  # noqa: E402
import rulings57  # noqa: E402
from test_make_score_55 import Run, _numbers, _judgment, _stamp, T, CUR, PROBS  # noqa: E402

VNOM_J = os.path.join(HERE, "fixtures", "share_classes", "VNOM_judgment.json")
DIL = "WeightedAverageNumberOfDilutedSharesOutstanding"
VN = {"2023-12-31": (74176000, 90709946), "2024-12-31": (93932000, 95525123), "2025-12-31": (142530000, 197117368)}
YTD = (187553000, 171536228)
PRICE = 45.02


def SC():
    import share_classes
    return share_classes


def sha256_of(d):
    """Rule 8's declaration_sha256, spelled out (so the fixtures build on any code; test M-4 holds it equal to
    share_classes.declaration_sha256)."""
    import hashlib
    return hashlib.sha256(json.dumps(d, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def decl():
    with open(VNOM_J, encoding="utf-8") as f:
        return json.load(f)["share_classes"]


def sc_record(d=None, applied=None, ttm=None, nci=None, cap=None, **kw):
    d = d or decl()
    ap = applied if applied is not None else [
        {"period_end": p, "period_start": p[:4] + "-01-01", "filed_traded": f, "filed_traded_tag": DIL,
         "declared_units": float(u), "units_split_factor": 1.0, "units_split_basis": "no_split",
         "units_equivalent": float(u), "total_units": float(f + u), "included_units": 0.0, "diluted_minus_basic": 0.0,
         "exchange_test": {"test": "passed", "basic": float(f), "gap": 0.0}, "count_bases": ["period_end"],
         "out_of_band": False, "share_basis_attested": None, "classes": []} for p, (f, u) in VN.items()]
    la = ap[-1] if ap else {"filed_traded": 142530000, "units_equivalent": 0.0, "total_units": 142530000.0,
                             "period_end": "2025-12-31"}
    rec = {"declared": True, "basis": d["basis"], "declaration_sha256": sha256_of(d),
           "traded_class": d["traded_class"],
           "classes": [{"name": c["name"], "holder": c["holder"], "exchange_ratio": float(c["exchange_ratio"])} for c in d["classes"]],
           "applied": ap, "ttm": ttm, "base_window_complete": True, "zero_periods": [], "included_periods": [],
           "calc_entries": [], "checks_relaxed": None, "counterfactual_notes": [], "unused_periods": [],
           "ttm_ytd_end_seen": None, "series_excluded_periods": [], "growth_inputs_shortened": {},
           "growth_inputs_dropped": [], "growth_inputs_dropped_values": {},
           "latest": {"period_end": la["period_end"], "filed_traded": la["filed_traded"],
                      "units_equivalent": la["units_equivalent"], "total_units": la["total_units"],
                      "declared_share_of_total": la["units_equivalent"] / la["total_units"]},
           "market_cap": {"filed_basis": PRICE * la["filed_traded"], "total_units": PRICE * la["total_units"],
                          "units_period": la["period_end"]},
           "nci_check": nci or {"nci_share_of_equity": 0.5708, "nci_share_of_net_income_3fy": 0.5217,
                                "declared_share_of_total": 0.5804, "gap_pp": 0.96, "tolerance_pp": 15, "agrees": True},
           "cap_check": cap or {"cap_ratio": 2.5201, "universe_price": 42.99, "declared_uplift": 1.383, "band": 0.05,
                                "gap": False},
           "ack_reason_present": False, "counterfactual": False}
    rec.update(kw)
    return rec


UPC = {"nci_share_of_net_income_3fy": 0.5217, "nci_years": [], "nci_share_of_equity": 0.5708, "s": 0.5708,
       "diluted_to_basic": 1.0, "units_in_diluted": False, "cover_by_class": True, "dei_to_diluted": None,
       "universe_price": 42.99, "universe_cap_to_filed_cap": 2.5201, "count_gap": True, "domestic": True,
       "threshold": 0.2, "suspect": True, "suppressed_by": "share_classes"}
SC_FLAG = ("SHARE_CLASSES_DECLARED: up_c_exchangeable_units — per-share figures divide by total economic units: the "
           "filed traded-class diluted count plus 2 declared classes (exchange ratio 1) for FY2023, FY2024, FY2025")


def declared(d=None, rec=None, **kw):
    """A 5.7 record on the median base with VNOM's declaration applied (tier C, 12.48%)."""
    fields = dict(price=PRICE, shares_diluted_latest=339647368.0, market_cap_est=PRICE * 339647368,
                  base_oe_per_share=3.23556058644467, tier_by_numbers="C", implied_irr_weighted=0.1248,
                  implied_irr_base=0.1248, share_classes=rec if rec is not None else sc_record(d), up_c_check=dict(UPC),
                  fragility_flags=[SC_FLAG],
                  market_cap_basis={"shares_used": 339647368.0, "shares_source": "diluted_latest+share_classes",
                                    "ads_ratio": None, "traded_shares": 142530000, "declared_units": 197117368.0,
                                    "units_period": "2025-12-31",
                                    "formula": "price × (traded-class shares + declared class-equivalent units)"})
    fields.update(kw)
    return _numbers(release=CUR, **fields)


def ttm_doc(d=None, sha=None, per_unit=1488000000 / 359089228):
    tt = {"ticker": T, "fy_end": "2025-12-31", "ytd_end": "2026-06-30",
          "inputs": {"ocf": {"fy_period": ["2025-01-01", "2025-12-31"], "ytd_prior_period": ["2025-01-01", "2025-06-30"],
                             "ytd_current_period": ["2026-01-01", "2026-06-30"]},
                     "shares_diluted": {"ytd_current": YTD[0], "ytd_current_tag": DIL}},
          "ttm_ocf": 1495000000, "ttm_capex": 0.0, "ttm_sbc": 7000000.0, "ttm_shares_diluted": float(sum(YTD)),
          "ttm_shares_diluted_filed": YTD[0], "ttm_oe_total": 1488000000.0, "ttm_oe_per_share": per_unit,
          "ttm_oe_per_share_filed_basis": 7.933757391244075, "warnings": [], "overrides_used": [],
          "share_classes": {"declaration_sha256": sha or sha256_of(d or decl()), "basis": "up_c_exchangeable_units",
                            "leg": "ytd_10q", "period_end": "2026-06-30", "period_start": "2026-01-01",
                            "units_equivalent": float(YTD[1]), "filed_traded": YTD[0], "total_units": float(sum(YTD)),
                            "units_split_basis": "no_split", "diluted_minus_basic": 0.0, "exchange_test": {"test": "passed"}}}
    return tt


def ttm_pinned(d=None, tt=None, **kw):
    """A 5.7 --ttm record on the declared ttm.json (Tier B, 15.02%), its ttm_inputs the engine's record of it."""
    tt = tt or ttm_doc(d)
    rulings57.add_ttm_engine_release(tt)
    rec = sc_record(d, ttm={"period_end": "2026-06-30", "filed_traded": YTD[0], "units_equivalent": float(YTD[1]),
                            "total_units": float(sum(YTD)), "units_split_basis": "no_split", "diluted_minus_basic": 0.0,
                            "leg": "ytd_10q", "period_start": "2026-01-01", "ttm_oe_per_share": tt["ttm_oe_per_share"],
                            "ttm_oe_per_share_filed_basis": tt["ttm_oe_per_share_filed_basis"]})
    n = declared(rec=rec, base_oe_per_share=tt["ttm_oe_per_share"], base_source="ttm_json", tier_by_numbers="B",
                 implied_irr_weighted=0.1502, implied_irr_base=0.1502,
                 inputs={"moat": 6, "probs": PROBS, "offsets": [-0.12, -0.05, 0.0, 0.05, 0.12],
                         "mults": [0.75, 0.9, 1.0, 1.1, 1.25], "g_terminal": 0.025,
                         "base_oe_ps_arg": tt["ttm_oe_per_share"], "base_pin_source": "ttm_json"},
                 ttm_inputs=E.ttm_inputs_record(tt), **kw)
    return n, tt


FILED = {"base_oe_per_share": 7.933757391244075, "implied_irr_weighted": 0.2505, "tier_by_numbers": "S",
         "market_cap_est": PRICE * 142530000, "base_oe_normalized_per_share": 7.338805865431839,
         "shares_diluted_latest": 142530000, "data_gap": [], "data_gap_uncovered": []}

STANDIN = r'''import json, os, sys
# Stand-in dcf_engine.py (test_make_score_share_classes): the filed-basis replay of make_score's share_classes_impact.
here = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(os.path.join(here, "standin.json"), encoding="utf-8"))
log = os.path.join(here, "SPAWNED_dcf_engine.py.txt")
calls = open(log, encoding="utf-8").read().splitlines() if os.path.exists(log) else []
env = {k: os.environ.get(k) for k in ("DCF_NO_SHARE_CLASSES", "DCF_SC_PIN_SCALE", "DCF_NO_OVERRIDES", "DCF_IPRD_HOLD")}
with open(log, "a", encoding="utf-8") as f:
    f.write(json.dumps({"argv": sys.argv[1:], "env": env}) + "\n")
recs = cfg.get("replies") or []
rec = recs[min(len(calls), len(recs) - 1)] if recs else cfg.get("reply")
if rec.get("_exit"):
    print(rec.get("_stdout", "BAD_SHARE_CLASSES for TST: stand-in refusal"))
    sys.exit(rec["_exit"])
print(json.dumps(rec))
'''


def run_ms(n, j=None, tt=None, replies=None, prior_registry=None, judgment_text=None, files=None):
    """make_score on a fresh folder (the stand-in engine answers the replays); returns the closed Run with its outputs."""
    r = Run(n, j if j is not None else (None if judgment_text else _judgment(n, share_classes=decl())),
            judgment_text=judgment_text, files=files)
    try:
        with open(os.path.join(r.sysdir, "dcf_engine.py"), "w", encoding="utf-8") as f:
            f.write(STANDIN)
        with open(os.path.join(r.sysdir, "standin.json"), "w", encoding="utf-8") as f:
            json.dump({"replies": replies or [FILED]}, f)
        if tt is not None:
            with open(os.path.join(r.folder, "ttm.json"), "w", encoding="utf-8") as f:
                json.dump(tt, f)
        if judgment_text is not None:
            rulings57.add_minimal_scorecard_as_written(r.folder)
        if prior_registry is not None:
            with open(r.registry, "w", encoding="utf-8") as f:
                json.dump(prior_registry, f, indent=1)
        r.run()
        log = os.path.join(r.sysdir, "SPAWNED_dcf_engine.py.txt")
        calls = [json.loads(x) for x in open(log, encoding="utf-8").read().splitlines()] if os.path.exists(log) else []
        r.result = dict(r.state(), score=r.score() if r.rc == 0 else None, key=r.key() if r.rc == 0 else None,
                        entries=r.entries(), calls=calls)
    finally:
        r.close()
    return r


def ok(r):
    assert r.rc == 0, f"make_score refused: {r.err[-2500:]}"
    return r


def refused(r, *needles):
    assert r.rc == 1 and "REFUSED" in r.err, (r.rc, r.out[-400:], r.err[-1500:])
    for s in needles:
        assert s in r.err, f"{s!r} not in: {r.err[-1500:]}"
    assert not r.result["key_exists"], "a refusal wrote key_numbers.md"
    return r


# ===========================================================================
# M-1 / M-2
# ===========================================================================
def test_shape_refusals():
    """M-1 (R-1): every share_classes.validate error refuses (here: an estimate count); a snippet over 24 words, or
    one that does not show its count; an optional reason without a digit; an out-of-band period without ack_reason."""
    for edit, needle in ((lambda d: d["classes"][0]["periods"][0].update(kind="estimate"), "kind must be"),
                         (lambda d: d["classes"][0]["periods"][0].update(snippet=" ".join(["word"] * 25) + " 90,709,946"),
                          "over 24 words"),
                         (lambda d: d["classes"][0]["periods"][0].update(snippet="Class B shares outstanding"),
                          "does not show the count 90,709,946"),
                         (lambda d: d.update(cap_gap_reason="the screener counts one class"), "cap_gap_reason must carry a number")):
        d = decl()
        edit(d)
        refused(run_ms(declared(d), j=_judgment(share_classes=d)), "share_classes", needle)
    rec = sc_record()
    rec["applied"][0]["out_of_band"] = True
    refused(run_ms(declared(rec=rec)), "out of band", "ack_reason")


OOB_UNITS = 187553000 * 21 + 6746384     # VNOM's 2026-06-30 Class B units at 21x the YTD Class A count, + TWR IV's


def _oob_decl(ack=None):
    d = decl()
    for p in d["classes"][0]["periods"]:
        if p["period_end"] == "2026-06-30":
            p["value"], p["snippet"] = 187553000 * 21, f"{187553000 * 21:,} units outstanding (test)"
    if ack:
        d["ack_reason"] = ack
    return d


def _oob_ttm(d):
    tt = ttm_doc(d, per_unit=1488000000 / (YTD[0] + OOB_UNITS))
    tt["share_classes"].update(units_equivalent=float(OOB_UNITS), total_units=float(YTD[0] + OOB_UNITS))
    tt["ttm_shares_diluted"] = float(YTD[0] + OOB_UNITS)
    return tt


def test_ttm_period_out_of_band_needs_ack_reason():
    """M-1b (rule 6 / R-1; review 2026-10-21 finding 5): the current-YTD period's units over 20x its traded count —
    in a --ttm record's share_classes.ttm, or in ttm.json's block on this declaration beside a median score — refuse
    without share_classes.ack_reason, like an out-of-band FY row (they had scored: R-1 read share_classes.applied
    only); with an ack_reason that carries the counts both score."""
    d = _oob_decl()
    n, tt = ttm_pinned(d, tt=_oob_ttm(d))
    n["share_classes"]["ttm"].update(units_equivalent=float(OOB_UNITS), total_units=float(YTD[0] + OOB_UNITS))
    refused(run_ms(n, j=_judgment(share_classes=d), tt=tt), "out of band", "TTM to 2026-06-30", "ack_reason")
    refused(run_ms(declared(d), j=_judgment(share_classes=d), tt=tt), "out of band", "TTM to 2026-06-30", "ack_reason")
    da = _oob_decl(ack=f"test: the YTD units {OOB_UNITS:,} are a multiple of the 187,553,000 traded Class A shares")
    na, tta = ttm_pinned(da, tt=_oob_ttm(da))
    na["share_classes"]["ttm"].update(units_equivalent=float(OOB_UNITS), total_units=float(YTD[0] + OOB_UNITS))
    ok(run_ms(na, j=_judgment(share_classes=da), tt=tta))
    ok(run_ms(declared(da), j=_judgment(share_classes=da), tt=tta))


def test_sync_refusals():
    """M-2 (R-2): the record's declaration_sha256 not the declaration's; applied units that are not the declaration's;
    no record while declared (a run before the declaration); a record while judgment.json declares none — each "out
    of sync … rerun the engine (and ttm.py)"."""
    d = decl()
    d["classes"][0]["periods"][0]["snippet"] = "Class B common stock: 90,709,946 shares issued and outstanding"
    refused(run_ms(declared(), j=_judgment(share_classes=d)), "out of sync", "declaration_sha256", "rerun the engine")
    rec = sc_record()
    rec["applied"][1]["declared_units"] = 1.0
    refused(run_ms(declared(rec=rec)), "out of sync", "2024-12-31")
    n = declared()
    n.pop("share_classes")
    refused(run_ms(n), "out of sync", "recorded none")
    refused(run_ms(declared(), j=_judgment()), "out of sync", "declares none")


# ===========================================================================
# M-3 — exclusive, the pins, payable
# ===========================================================================
def test_mismatch_pins_and_payable():
    """M-3 (R-3 / R-4 / R-5): share_class_mismatch beside a declaration refuses; VNOM's 2026-10-16 plain pin (no
    share_basis) refuses ("share_classes replaces a share-basis base pin"); the same pin attested share_basis
    "total_units" (basis_window fy: the latest FY's units) scores, measured as declared_pin, replayed at pin ×
    339,647,368 ÷ 142,530,000 with DCF_SC_PIN_SCALE; a share_period contradicting its basis_window refuses; a
    payable_earnings_5y base beside a declaration refuses."""
    j = _judgment(share_classes=decl(), share_class_mismatch={"value": True, "source": "t", "reason": "t"})
    refused(run_ms(declared(), j=j), "SHARE_CLASS_MISMATCH")
    pin = 4.143427182330288
    bo = {"value": pin, "source": "test: the engine's OE over the total units 339,647,368",
          "reason": "test: the per-unit TTM base of an Up-C filer"}
    inp = {"moat": 6, "probs": PROBS, "offsets": [-0.12, -0.05, 0.0, 0.05, 0.12], "mults": [0.75, 0.9, 1.0, 1.1, 1.25],
           "g_terminal": 0.025, "base_oe_ps_arg": pin, "base_pin_source": "base_oe_ps_arg",
           "base_basis_window": {"window": "fy"}}
    n = declared(base_oe_per_share=pin, base_source="agent_supplied_ttm_override", inputs=inp)
    refused(run_ms(n, j=_judgment(share_classes=decl(), base_override=dict(bo, basis_window={"window": "fy"}))),
            "share_classes replaces a share-basis base pin", "share_basis")
    j = _judgment(share_classes=decl(), base_override=dict(bo, basis_window={"window": "fy"}, share_basis="total_units"))
    r = ok(run_ms(n, j=j))
    blk = r.result["score"]["share_classes"]
    assert blk["base_used"] == "declared_pin" and abs(blk["replay_pin"] - pin * 339647368 / 142530000) < 1e-9, blk
    call = r.result["calls"][-1]
    assert call["env"]["DCF_NO_SHARE_CLASSES"] == "1" and abs(float(call["env"]["DCF_SC_PIN_SCALE"]) - 339647368 / 142530000 * pin / pin) < 1e-6
    assert call["argv"][call["argv"].index("--base-oe-ps") + 1] == repr(pin * 339647368 / 142530000), call
    bo_ev = [e for e in r.result["entries"] if e.get("event") == "base_override"]
    assert bo_ev and bo_ev[0]["share_basis"] == "total_units", bo_ev
    j = _judgment(share_classes=decl(), base_override=dict(bo, basis_window={"window": "fy"}, share_basis="total_units",
                                                           share_period="2026-06-30"))
    refused(run_ms(n, j=j), "contradicts its basis_window")
    pay = {"value": 1.0, "kind": "filing", "basis": "payable_earnings_5y", "figures": [1e6] * 5, "shares": 1e6,
           "source": "t", "reason": "t"}
    refused(run_ms(declared(), j=_judgment(share_classes=decl(), base_override=pay)))


# VNOM-shaped FY owner's earnings for the CSV rows the R-4 filed-basis test reads (period: OE, filed, total units)
FY_OE = {"2023-12-31": 600e6, "2024-12-31": 700e6, "2025-12-31": 1046e6}


def _fy_rows(oe=None):
    oe = oe or FY_OE
    return [{"period_end": p, "oe_conservative": repr(oe[p]), "shares_diluted": repr(float(f + u)),
             "shares_tag": f"{DIL}+SHARE_CLASSES", "oe_per_share": repr(oe[p] / (f + u))} for p, (f, u) in VN.items()]


def _sync_refusal(n, j, tt=None, rows=None):
    """check_share_classes_sync (R-2 … R-10) in process on a temp folder holding j, tt and the CSV rows: None when it
    passes, else the refusal text."""
    import contextlib
    import csv
    import io
    base = tempfile.mkdtemp(prefix="sc_sync_")
    folder = os.path.join(base, T)
    os.makedirs(folder)
    with open(os.path.join(folder, "judgment.json"), "w", encoding="utf-8") as f:
        json.dump(j, f)
    if tt is not None:
        with open(os.path.join(folder, "ttm.json"), "w", encoding="utf-8") as f:
            json.dump(tt, f)
    if rows:
        with open(os.path.join(folder, "financials_history.csv"), "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    saved, err = M.BASE, io.StringIO()
    try:
        M.BASE = base
        with contextlib.redirect_stderr(err):
            M.check_share_classes_sync(n, j.get("share_classes"), folder)
        return None
    except SystemExit:
        return err.getvalue()
    finally:
        M.BASE = saved
        shutil.rmtree(base, ignore_errors=True)


def test_attested_pin_on_a_filed_basis_figure_is_refused():
    """M-3b (R-4; a rule beyond 08's attestation text — review 2026-10-21 finding 3, raised with Andrew; switch
    make_score.SC_REFUSE_FILED_BASIS_PIN): a base_override attested share_basis "total_units" whose value is a
    filed-basis per-share figure the run or ttm.json carries — ttm.json's ttm_oe_per_share_filed_basis ($7.9338:
    VNOM's fake Tier S, 25.05%, which had scored) or an applied FY's OE ÷ its filed traded count (financials_history.csv)
    — is refused; the per-unit figures (TTM $4.1438, FY2025 OE ÷ total units) pass; a value that is a total-unit
    figure as well as a filed-basis one is not refused; the switch off restores 08's attestation-only rule."""
    n, tt = ttm_pinned()
    fb = tt["ttm_oe_per_share_filed_basis"]
    bw = {"window": "ttm", "ytd_current_period": ["2026-01-01", "2026-06-30"]}
    inp = dict(n["inputs"], base_oe_ps_arg=fb, base_pin_source="base_oe_ps_arg", base_basis_window=bw)
    nf = dict(n, base_oe_per_share=fb, base_source="agent_supplied_ttm_override", inputs=inp, tier_by_numbers="S",
              implied_irr_weighted=0.2505, implied_irr_base=0.2505)
    bo = {"value": fb, "share_basis": "total_units", "basis_window": bw,
          "source": f"test: ttm.json ttm_oe_per_share_filed_basis {fb:.6f} (TTM to 2026-06-30)",
          "reason": "test: TTM owner's earnings per share, 1,488,000,000 / 187,553,000"}
    refused(run_ms(nf, j=_judgment(share_classes=decl(), base_override=bo), tt=tt),
            "filed-basis", "ttm_oe_per_share_filed_basis", "total_units")
    # in process: the FY figures from financials_history.csv (applied periods' OE ÷ filed traded count)
    rows = _fy_rows()
    fy25_filed = FY_OE["2025-12-31"] / VN["2025-12-31"][0]
    fy23_filed = FY_OE["2023-12-31"] / VN["2023-12-31"][0]
    fy25_total = FY_OE["2025-12-31"] / sum(VN["2025-12-31"])
    fyw = {"window": "fy"}
    for val, needle in ((fy25_filed, "FY2025"), (fy23_filed, "FY2023"), (fb, "ttm_oe_per_share_filed_basis")):
        nn = dict(n, base_oe_per_share=val, inputs=dict(n["inputs"], base_oe_ps_arg=val, base_pin_source="base_oe_ps_arg"))
        msg = _sync_refusal(nn, {"share_classes": decl(), "base_override": dict(bo, value=val, basis_window=fyw)}, tt, rows)
        assert msg and "filed-basis" in msg and needle in msg, (val, msg)
    for val in (fy25_total, tt["ttm_oe_per_share"]):
        nn = dict(n, base_oe_per_share=val, inputs=dict(n["inputs"], base_oe_ps_arg=val, base_pin_source="base_oe_ps_arg"))
        assert _sync_refusal(nn, {"share_classes": decl(), "base_override": dict(bo, value=val, basis_window=fyw)},
                             tt, rows) is None, val
    # FY2024's per-unit figure built equal to FY2025's filed-basis one: a total-unit figure too, so not refused
    oe = dict(FY_OE, **{"2024-12-31": fy25_filed * sum(VN["2024-12-31"])})
    nn = dict(n, base_oe_per_share=fy25_filed,
              inputs=dict(n["inputs"], base_oe_ps_arg=fy25_filed, base_pin_source="base_oe_ps_arg"))
    assert _sync_refusal(nn, {"share_classes": decl(), "base_override": dict(bo, value=fy25_filed, basis_window=fyw)},
                         tt, _fy_rows(oe)) is None
    saved = M.SC_REFUSE_FILED_BASIS_PIN
    try:
        M.SC_REFUSE_FILED_BASIS_PIN = False
        nn = dict(n, base_oe_per_share=fy25_filed,
                  inputs=dict(n["inputs"], base_oe_ps_arg=fy25_filed, base_pin_source="base_oe_ps_arg"))
        assert _sync_refusal(nn, {"share_classes": decl(), "base_override": dict(bo, value=fy25_filed, basis_window=fyw)},
                             tt, rows) is None
    finally:
        M.SC_REFUSE_FILED_BASIS_PIN = saved


# ---------------------------------------------------------------------------
# in process: share_classes_impact with its replay stubbed (A-17 / M-3 / M-4b)
# ---------------------------------------------------------------------------
class Stub:
    def __init__(self, replies):
        self.replies, self.calls = list(replies), []

    def __call__(self, cmd, env):
        self.calls.append((list(cmd), dict(env)))
        r = self.replies[min(len(self.calls) - 1, len(self.replies) - 1)]
        if isinstance(r, tuple):
            return r
        return 0, r, ""


def impact(n, j, tt=None, replies=(FILED,), release=None):
    base = tempfile.mkdtemp(prefix="sc_impact_")
    os.makedirs(os.path.join(base, T))
    with open(os.path.join(base, T, "judgment.json"), "w", encoding="utf-8") as f:
        json.dump(j, f)
    if tt is not None:
        with open(os.path.join(base, T, "ttm.json"), "w", encoding="utf-8") as f:
            json.dump(tt, f)
    saved = (M.BASE, M._sc_replay, M.ENGINE_RELEASE, M.registry_prior_entries)
    stub = Stub(replies)
    try:
        M.BASE, M._sc_replay = base, stub
        if release:
            M.ENGINE_RELEASE = release
            M.registry_prior_entries = lambda t: []
        out = M.share_classes_impact(T, n, j.get("share_classes"))
    finally:
        M.BASE, M._sc_replay, M.ENGINE_RELEASE, M.registry_prior_entries = saved
        shutil.rmtree(base, ignore_errors=True)
    return out, stub.calls


def _amort_record(native, value, figures, shares, tt):
    n, _ = ttm_pinned(tt=tt) if native == "ttm_json" else (declared(), None)
    n = dict(n, base_oe_per_share=value, inputs=dict(n.get("inputs") or {}, base_oe_ps_arg=value,
                                                    base_pin_source="base_oe_ps_arg"),
             base_source="agent_supplied_ttm_override",
             iprd_adjustment={"treatment": "amortized_in_base",
                              "amortized": {"basis": "iprd_amortized", "native_base": native, "figures": figures,
                                            "shares": shares, "native_base_per_share": 1.0, "pinned_per_share": value}})
    return n


def test_amortized_and_via_ttm_replay_pins():
    """M-3 (amortized, A-4) and M-4b (via-TTM, revision 2 finding 2), in process: an iprd_amortized pin on native
    ttm_json replays once at pin × TTM total ÷ TTM filed with DCF_SC_PIN_SCALE = that ÷ the declared value (recorded
    replay_pin_scale); on the native median, two replays — the filed median first, then
    iprd_amortized_value(its median, figures, its count); a replay that did not recognise the declaration (one_time)
    is "not measured"; a via-TTM --base-oe-ps (no base_override) replays at ttm.json's ttm_oe_per_share_filed_basis
    and gives the filed-basis base and tier; a ttm.json without that field is "not measured"; an engine refusal in
    the replay (exit 3) is recorded, not refused (A-17)."""
    tt = ttm_doc()
    val = 4.0
    n = _amort_record("ttm_json", val, [15e6, 0.0, 20e6], float(sum(YTD)), tt)
    bo = {"basis": "iprd_amortized", "kind": "filing", "native_base": "ttm_json", "figures": [15e6, 0.0, 20e6],
          "shares": float(sum(YTD)), "value": val, "source": "t", "reason": "t"}
    rep = dict(FILED, iprd_adjustment={"treatment": "amortized_in_base", "amortized": {"counterfactual_replay": "x"}})
    blk, calls = impact(n, {"share_classes": decl(), "base_override": bo}, tt, replies=(rep,))
    exp = val * sum(YTD) / YTD[0]
    assert blk["base_used"] == "iprd_amortized_pin" and abs(blk["replay_pin"] - exp) < 1e-9 and len(calls) == 1, blk
    assert abs(blk["replay_pin_scale"] - round(exp / val, 6)) < 1e-12 and calls[0][1]["DCF_SC_PIN_SCALE"] == repr(exp / val)
    assert blk["measured"] and blk["note"] == "x"
    one = dict(FILED, iprd_adjustment={"treatment": E.IPRD_TREATMENT_ONE_TIME})
    blk, _ = impact(n, {"share_classes": decl(), "base_override": bo}, tt, replies=(one,))
    assert blk["measured"] is False and "did not recognise the amortized declaration" in blk["note"], blk
    nm = _amort_record("median_of_last_3_fy_oe_per_share", val, [15e6, 0.0, 20e6], 339647368.0, None)
    bm = dict(bo, native_base="median_of_last_3_fy_oe_per_share", shares=339647368.0)
    step1 = dict(FILED, base_oe_normalized_per_share=7.338805865431839, shares_diluted_latest=142530000)
    blk, calls = impact(nm, {"share_classes": decl(), "base_override": bm}, None, replies=(step1, rep))
    exp = E.iprd_amortized_value(7.338805865431839, [15e6, 0.0, 20e6], 142530000)
    assert len(calls) == 2 and "--base-oe-ps" not in calls[0][0] and abs(blk["replay_pin"] - exp) < 1e-12, (blk, calls)
    assert calls[1][1]["DCF_SC_PIN_SCALE"] == repr(exp / val)
    # via-TTM --base-oe-ps (no base_override)
    nv, tt = ttm_pinned()
    nv = dict(nv, inputs=dict(nv["inputs"], base_pin_source="base_oe_ps_arg"), base_source="agent_supplied_ttm_override")
    blk, calls = impact(nv, {"share_classes": decl()}, tt)
    assert blk["base_used"] == "ttm" and blk["replay_pin"] == 7.933757391244075 and "DCF_SC_PIN_SCALE" not in calls[0][1]
    assert calls[0][0][calls[0][0].index("--base-oe-ps") + 1] == repr(7.933757391244075) and "--ttm" not in calls[0][0]
    assert blk["base_oe_filed_basis"] == 7.9338 and blk["tier_filed_basis"] == "S" and blk["raises_tier"] is False
    tt2 = {k: v for k, v in tt.items() if k != "ttm_oe_per_share_filed_basis"}
    blk, calls = impact(nv, {"share_classes": decl()}, tt2)
    assert blk["measured"] is False and "filed-basis TTM" in blk["note"] and calls == []
    blk, _ = impact(nv, {"share_classes": decl()}, tt, replies=((3, None, "BAD_TTM_SHARE_BASIS for TST: x"),))
    assert blk["measured"] is False and "the filed-class run does not score (BAD_TTM_SHARE_BASIS" in blk["note"], blk
    blk, _ = impact(declared(), {"share_classes": decl()}, None, release="9.9.9")
    assert blk["measured"] is False and blk["note"].startswith("not measured"), blk


def _impact_refusal(n, j, tt=None, replies=(FILED,)):
    """share_classes_impact's refusal text (None when it returned a block)."""
    import contextlib
    import io
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err):
            impact(n, j, tt, replies=replies)
        return None
    except SystemExit:
        return err.getvalue()


def test_a_crashed_share_class_replay_refuses():
    """M-4d (08 §8.4 "a replay failure refuses (nothing written)", rebase A-17; review 2026-10-21 finding 4): only the
    engine's own refusal (exit 3) is recorded measured: false. A replay that crashed (exit 1, a traceback — it had been
    recorded "the filed-class run does not score", which also skipped the R6 entry-alert suppression), exited 2,
    timed out (no exit code) or exited 0 without a JSON object refuses the score — on the one-step replay and on step 1
    of the amortized two-step; exit 3 at step 1 is "not measured" with no second replay."""
    tb = (1, None, "Traceback (most recent call last):")
    for rep in (tb, (2, None, "NO_CIK for TST"), (None, None, ""), (0, None, "Traceback (most recent call last):")):
        msg = _impact_refusal(declared(), {"share_classes": decl()}, None, replies=(rep,))
        assert msg and "did not complete" in msg and "retry make_score" in msg, (rep, msg)
    blk, _ = impact(declared(), {"share_classes": decl()}, None, replies=((3, None, "BAD_SHARE_CLASSES for TST: x"),))
    assert blk["measured"] is False and "does not score (BAD_SHARE_CLASSES" in blk["note"], blk
    nm = _amort_record("median_of_last_3_fy_oe_per_share", 4.0, [15e6, 0.0, 20e6], 339647368.0, None)
    bm = {"basis": "iprd_amortized", "kind": "filing", "native_base": "median_of_last_3_fy_oe_per_share",
          "figures": [15e6, 0.0, 20e6], "shares": 339647368.0, "value": 4.0, "source": "t", "reason": "t"}
    for rep in (tb, (0, None, "")):
        msg = _impact_refusal(nm, {"share_classes": decl(), "base_override": bm}, None, replies=(rep,))
        assert msg and "did not complete" in msg and "step 1" in msg, (rep, msg)
    blk, calls = impact(nm, {"share_classes": decl(), "base_override": bm}, None,
                        replies=((3, None, "BAD_TTM_SHARES for TST: x"),))
    assert blk["measured"] is False and "BAD_TTM_SHARES" in blk["note"] and len(calls) == 1, (blk, calls)


# ===========================================================================
# M-4 / M-4c — the measured block and the registry
# ===========================================================================
def test_measured_block_and_registry_event():
    """M-4 (08 §8.4 / §8.6, A-14): a --ttm run on the declared ttm.json replays at ttm.json's filed-basis TTM
    (--base-oe-ps 7.933757391244075, no --ttm, DCF_NO_SHARE_CLASSES): score.json share_classes carries both bases
    ($7.9338 S → $4.1438 B, 25.05% → 15.02%, the caps) and the share_classes registry event the same block with
    units_by_period (never `periods`); an unchanged declaration keeps its first date, an edited one re-dates."""
    n, tt = ttm_pinned()
    r = ok(run_ms(n, tt=tt))
    c = r.result["calls"][-1]
    assert "--ttm" not in c["argv"] and c["argv"][c["argv"].index("--base-oe-ps") + 1] == repr(7.933757391244075), c
    assert c["env"]["DCF_NO_SHARE_CLASSES"] == "1" and c["env"]["DCF_NO_OVERRIDES"] is None and c["env"]["DCF_IPRD_HOLD"] is None
    blk = r.result["score"]["share_classes"]
    assert (blk["base_used"], blk["base_oe_filed_basis"], blk["base_oe_total_units"]) == ("ttm", 7.9338, 4.1438), blk
    assert (blk["tier_filed_basis"], blk["tier_total_units"], blk["weighted_irr_impact_pp"]) == ("S", "B", -10.03), blk
    assert blk["measured"] and blk["raises_tier"] is False and blk["latest"]["total_units"] == 339647368
    assert blk["ttm"] == {"period_end": "2026-06-30", "filed_traded": 187553000, "units_equivalent": 171536228,
                          "total_units": 359089228}, blk["ttm"]
    ev = [e for e in r.result["entries"] if e.get("event") == "share_classes"]
    assert len(ev) == 1 and "periods" not in ev[0] and ev[0]["units_by_period"]["2026-06-30"] == 171536228, ev
    assert ev[0]["declaration_sha256"] == sha256_of(decl()) == SC().declaration_sha256(decl()) and ev[0]["base_oe_filed_basis"] == 7.9338
    prior = {"entries": [dict(ev[0], date="2026-10-01")]}
    r2 = ok(run_ms(n, tt=tt, prior_registry=prior))
    assert [e["date"] for e in r2.result["entries"] if e.get("event") == "share_classes"] == ["2026-10-01"]
    d = decl()
    d["classes"][0]["periods"][0]["snippet"] = "Class B common stock: 90,709,946 shares issued and outstanding"
    n3, tt3 = ttm_pinned(d)
    r3 = ok(run_ms(n3, j=_judgment(share_classes=d), tt=tt3, prior_registry=prior))
    assert [e["date"] for e in r3.result["entries"] if e.get("event") == "share_classes"] != ["2026-10-01"]


def test_registry_loads_the_new_events():
    """M-4c (rebase I-1 / A-14): load_registry accepts a registry holding a share_classes and an up_c_suspect event;
    the same registry with the event misspelt (share_class) or a share_classes event carrying `periods` (an
    iprd_deferred_payment field) is refused."""
    good = [{"ticker": "VNOM", "event": "share_classes", "date": "2026-10-21", "basis": "up_c_exchangeable_units",
             "declaration_sha256": "a" * 64, "units_by_period": {"2025-12-31": 197117368}},
            {"ticker": "ARES", "event": "up_c_suspect", "date": "2026-10-21", "reason": "four classes, 327,035,461"}]
    tmp = tempfile.mkdtemp(prefix="sc_reg_")
    path = os.path.join(tmp, "reg.json")
    saved = M.REGISTRY
    try:
        M.REGISTRY = path
        for entries, ok_ in ((good, True), ([dict(good[0], event="share_class")], False),
                             ([dict(good[0], periods=[{"period": "2025-12-31", "amount": 1.0}])], False)):
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"entries": entries}, f)
            try:
                reg = M.load_registry()
                assert ok_ and reg["entries"] == entries, entries
            except SystemExit:
                assert not ok_, entries
    finally:
        M.REGISTRY = saved
        shutil.rmtree(tmp, ignore_errors=True)


# ===========================================================================
# M-5 / M-6
# ===========================================================================
def test_entry_alert_suppressed_when_the_declaration_raises_the_tier():
    """M-5 (08 §8.8, 08b decision 3): share_classes_raise_reason names a measured raise only; alert_reasons appends it
    to the ENTRY reasons of a final S/A tier, never to the exits; without the keyword the gates are unchanged."""
    up = {"measured": True, "raises_tier": True, "tier_filed_basis": "B", "tier_total_units": "A"}
    txt = M.share_classes_raise_reason(up)
    assert txt == "share-class declaration raises the tier (B on the filed class → A on total units)"
    assert M.share_classes_raise_reason(dict(up, raises_tier=False)) is None
    assert M.share_classes_raise_reason(dict(up, measured=False)) is None
    e, x = M.alert_reasons("A", "A", None, "medium", "modeled", False, False, share_classes_raise=txt)
    assert e == [txt] and x == []
    e, x = M.alert_reasons("C", "C", None, "medium", "modeled", False, False, share_classes_raise=txt)
    assert e == [] and x == []
    assert M.alert_reasons("A", "A", None, "medium", "modeled", False, False) == ([], [])


def test_up_c_suspect_needs_a_reason():
    """M-6 (R-8): a 5.7 record flagged UP_C_SUSPECT with no declaration refuses without up_c_suspect_reason, and with
    one that carries no number; with a numeric reason it scores, records the up_c_suspect registry event and the
    waiver in score.json up_c_check; 5.6 output with the flag text has no obligation."""
    flag = ("UP_C_SUSPECT: noncontrolling interests hold 57.1% of equity — per-share figures may cover only the traded "
            "class (filed latest diluted 1,000,000,000)")
    uc = dict(UPC, suppressed_by=None)
    n = _numbers(release=CUR, fragility_flags=[flag], up_c_check=uc)
    jt = json.dumps(_judgment(n), indent=1, ensure_ascii=False) + "\n"
    refused(run_ms(n, judgment_text=jt), "UP_C_SUSPECT is unresolved", "up_c_suspect_reason")
    jt = json.dumps(_judgment(n, up_c_suspect_reason="an ordinary subsidiary minority"), indent=1) + "\n"
    refused(run_ms(n, judgment_text=jt), "up_c_suspect_reason must be a non-empty string carrying the number")
    why = "the filed diluted count covers every class: diluted ÷ basic 1.000 on the EPS note"
    r = ok(run_ms(n, j=_judgment(n, up_c_suspect_reason=why)))
    ev = [e for e in r.result["entries"] if e.get("event") == "up_c_suspect"]
    assert len(ev) == 1 and ev[0]["reason"] == why and ev[0]["s"] == 0.5708, ev
    assert r.result["score"]["up_c_check"] == {"suspect": True, "s": 0.5708, "suppressed_by": None, "waived_reason": why}
    assert "- Up-C check:" in r.result["key"] and "waived: “" in r.result["key"]
    old = _numbers(release="5.6.0", fragility_flags=[flag])
    ok(run_ms(old, j=_judgment(old)))


# ===========================================================================
# M-7 — key_numbers.md
# ===========================================================================
def test_key_numbers_share_class_lines():
    """M-7 (08 §8.7, A-25): the shares line reads total economic units (filed traded-class + declared); right after
    the basis lines, the declaration (traded class in curly quotes), one line per declared period, the TTM line, the
    measured impact and the NCI cross-check — inside "Base owner's earnings"; an undeclared 5.7 record keeps the
    shares line byte for byte and prints no share-class line."""
    n, tt = ttm_pinned()
    key = ok(run_ms(n, tt=tt)).result["key"]
    sec = key.split("## Base owner's earnings")[1].split("\n## ")[0]
    assert ("- Shares diluted (latest): 339,647,368 total economic units (filed traded-class diluted 142,530,000 + "
            "declared 197,117,368)") in sec
    assert ("- Share classes (declared, up_c_exchangeable_units; traded class “Class A common stock (Nasdaq: VNOM)”): "
            "per-share figures divide by the filed traded-class diluted count plus the declared class-equivalent units") in sec
    assert "  - FY2025: 142,530,000 + 197,117,368 = 339,647,368 (period-end counts:" in sec
    assert ("  - TTM to 2026-06-30: 187,553,000 + 171,536,228 = 359,089,228 → TTM OE/unit $4.1438 (filed-class basis "
            "$7.9338)") in sec
    assert ("- Share classes measured impact (filed traded class → total units, same final configuration): base OE/share "
            "$7.9338 → $4.1438 (-47.77%) · weighted IRR 25.05% → 15.02% (-10.03pp) · tier S → B") in sec
    assert "- Share classes cross-check: declared units are 58.04% of total units at FY2025" in sec and "within 15pp" in sec
    plain = _numbers(release=CUR, up_c_check=dict(UPC, suspect=False, suppressed_by=None))
    k0 = ok(run_ms(plain, j=_judgment(plain))).result["key"]
    assert "- Shares diluted (latest): 1,000,000,000\n" in k0 and "Share classes" not in k0 and "Up-C check" not in k0


# ===========================================================================
# M-8 — R-6 and A-6
# ===========================================================================
def test_ttm_json_off_the_declaration():
    """M-8 (R-6) and A-6: a --ttm score whose ttm.json was rewritten on another declaration after the run — with the
    run's ttm_inputs recorded, the share_classes block is a hashed leg, so TTM_CHANGED fires even with equal totals;
    for a record without ttm_inputs, R-6 refuses "ttm.json is not on this share_classes declaration"."""
    n, tt = ttm_pinned()
    other = copy.deepcopy(tt)
    other["share_classes"]["declaration_sha256"] = "f" * 64
    refused(run_ms(n, tt=other), M.TTM_CHANGED)
    n2 = {k: v for k, v in n.items() if k != "ttm_inputs"}
    refused(run_ms(n2, tt=other), "ttm.json is not on this share_classes declaration", "R-6")
    # a median score is never refused by a stale ttm.json
    ok(run_ms(declared(), tt=other))


def _r6_refusal(n, j_sc, tt):
    """check_ttm_on_declaration (R-6) in process: None when it passes, else the refusal text."""
    import contextlib
    import io
    base = tempfile.mkdtemp(prefix="sc_r6_")
    saved, err = M.BASE, io.StringIO()
    try:
        M.BASE = base
        with contextlib.redirect_stderr(err):
            M.check_ttm_on_declaration(n, j_sc, tt)
        return None
    except SystemExit:
        return err.getvalue()
    finally:
        M.BASE = saved
        shutil.rmtree(base, ignore_errors=True)


def test_ttm_basis_pins_off_the_declaration_refuse():
    """M-8b (R-6 / 08 §5.3 "the same table runs for an IPR&D ttm_json basis"; review 2026-10-21 finding 2): an
    iprd_amortized pin on native base ttm_json and a plain pin the engine read on basis_window "ttm" are TTM-basis
    scores too, so a ttm.json that is not on the declaration beside them (another declaration_sha256, or no block)
    is refused like a --ttm one (they had passed: R-6 saw only --ttm and a via-TTM --base-oe-ps); on the declaration
    they pass; a median score is still never refused."""
    tt = ttm_doc()
    other = copy.deepcopy(tt)
    other["share_classes"]["declaration_sha256"] = "f" * 64
    no_block = {k: v for k, v in tt.items() if k != "share_classes"}
    na = _amort_record("ttm_json", 4.0, [15e6, 0.0, 20e6], float(sum(YTD)), tt)
    nw, _ = ttm_pinned(tt=tt)
    bw = {"window": "ttm", "ytd_current_period": ["2026-01-01", "2026-06-30"]}
    nw = dict(nw, base_oe_per_share=2.0, base_source="agent_supplied_ttm_override",
              inputs=dict(nw["inputs"], base_oe_ps_arg=2.0, base_pin_source="base_oe_ps_arg", base_basis_window=bw))
    for n in (na, nw):
        assert _r6_refusal(n, decl(), tt) is None
        msg = _r6_refusal(n, decl(), other)
        assert msg and "ttm.json is not on this share_classes declaration" in msg and "another share_classes" in msg, msg
        msg = _r6_refusal(n, decl(), no_block)
        assert msg and "built before the share_classes declaration" in msg and "R-6" in msg, msg
        assert "on total units but judgment.json declares no share_classes" in (_r6_refusal(n, None, tt) or "")
    assert _r6_refusal(declared(), decl(), other) is None


# ===========================================================================
# M-9 / M-10 / M-11
# ===========================================================================
def test_cross_check_reasons():
    """M-9 (R-7 / R-7b): nci_check.agrees false needs share_classes.nci_gap_reason; cap_check.gap true needs
    cap_gap_reason — each a reason carrying a number."""
    rec = sc_record(nci={"nci_share_of_equity": 0.10, "nci_share_of_net_income_3fy": 0.12, "declared_share_of_total": 0.5804,
                         "gap_pp": 46.04, "tolerance_pp": 15, "agrees": False})
    refused(run_ms(declared(rec=rec)), "SHARE_CLASSES_NCI_GAP", "nci_gap_reason")
    rec = sc_record(cap={"cap_ratio": 1.0, "universe_price": 42.99, "declared_uplift": 1.383, "band": 0.05, "gap": True})
    refused(run_ms(declared(rec=rec)), "SHARE_CLASSES_CAP_GAP", "cap_gap_reason")


def test_score_blocks_only_on_records_that_carry_them():
    """M-10 (08 §8.5): a 5.6 record gets neither share_classes nor up_c_check; an undeclared 5.7 record gets
    up_c_check only; a declared one both (counts as integers)."""
    old = _numbers(release="5.6.0")
    s = ok(run_ms(old, j=_judgment(old))).result["score"]
    assert "share_classes" not in s and "up_c_check" not in s
    plain = _numbers(release=CUR, up_c_check=dict(UPC, suspect=False, suppressed_by=None))
    s = ok(run_ms(plain, j=_judgment(plain))).result["score"]
    assert "share_classes" not in s and s["up_c_check"]["suspect"] is False
    s = ok(run_ms(declared())).result["score"]
    assert s["share_classes"]["latest"]["filed_traded"] == 142530000 and s["share_classes"]["base_used"] == "median_3y"
    assert s["up_c_check"]["suppressed_by"] == "share_classes" and "share_classes" in M.SCORE_DECISION_KEYS


def test_share_basis_values_and_attestation():
    """M-11 (R-10 / A-26): shares_override.share_basis outside {traded_class, all_classes} refuses; an applied OVERRIDE
    period recorded without the traded_class attestation (older engine output) refuses "rerun the engine"; the
    attestation withdrawn from judgment.json after the run refuses."""
    j = _judgment(share_classes=decl(), shares_override={"value": 1e8, "kind": "filing", "source": "t", "reason": "t",
                                                         "share_basis": "partial"})
    refused(run_ms(declared(), j=j), "share_basis 'partial' is not one of")
    rec = sc_record()
    rec["applied"][-1].update(filed_traded_tag="OVERRIDE", share_basis_attested=None)
    refused(run_ms(declared(rec=rec)), "without a traded_class attestation", "rerun the engine")


# ===========================================================================
# M-13 — a declared 6-K interim bridge at a declaring filer, end to end
# ===========================================================================
IB_UNITS = {"2023-12-31": 61560000, "2024-12-31": 61560000, "2025-12-31": 61560000, "2026-06-30": 61700000}
_IB_CACHE = {}


def _ib_declared_pipeline():
    """(n, csv rows, ttm.json, fixture, judgment): test_make_score_57_interim's synthetic 20-F filer (615,600,000
    ordinary shares each FY, 617,000,000 in the 6-K interim; a basic count beside each FY diluted count) with a 10%
    multi_class_common declaration (61,560,000 Class B per FY, 61,700,000 at 2026-06-30) and the bridge's share leg
    attested traded_class — the real preliminary engine run, ttm.py --interim and the final --ttm run, offline."""
    if "pipe" in _IB_CACHE:
        return copy.deepcopy(_IB_CACHE["pipe"])
    import engine55_harness as H
    import test_make_score_57_interim as IB
    from test_share_classes_57 import ent
    fx = IB.foreign_fixture()
    for y in IB.YEARS:
        IB._put(fx["facts"], IB.IF, "WeightedAverageShares", "shares",
                {"accn": f"0009990030-{(y + 1) % 100:02d}-000010", "fy": y, "fp": "FY", "form": "20-F",
                 "filed": f"{y + 1}-03-18", "start": f"{y}-01-01", "end": f"{y}-12-31", "val": 615600000})
    sc = {"basis": "multi_class_common", "traded_class": "Ordinary shares (test)",
          "reason": "test: the Class B shares, 61,560,000 at FY2025, are outside the 615,600,000 ordinary count",
          "classes": [{"name": "Class B shares (test)", "holder": "founders (test)", "exchange_ratio": 1,
                       "periods": [ent(p, v) for p, v in IB_UNITS.items()]}]}
    d = IB.decl()
    d["legs"]["shares_diluted"]["current_interim"]["share_basis"] = "traded_class"
    j = IB.judgment(share_classes=sc, interim_bridge=d)
    base = H.make_base(fx, j, None, copy_repo_files=False)
    try:
        pre = H.run_engine(IB.FX_T, args=IB.ARGS, base=base, fixture=fx, keep_base=True)
        assert pre["exit"] == 0, pre["stdout"][-2000:]
        t = H.run_ttm(IB.FX_T, base=base, fixture=fx, patch=IB._ttm_patch, keep_base=True)
        assert t["exit"] == 0, t["stderr"][-2000:]
        fin = H.run_engine(IB.FX_T, args=IB.ARGS + ["--ttm"], base=base, fixture=fx, keep_base=True)
        assert fin["exit"] == 0, fin["stdout"][-2000:]
        out = (fin["numbers"], fin["rows"], t["ttm"], fx, j)
    finally:
        shutil.rmtree(base, ignore_errors=True)
    _IB_CACHE["pipe"] = out
    return copy.deepcopy(out)


def test_declared_interim_bridge_at_a_declaring_filer_scores():
    """M-13 (08 §5.4 / §9 "interim bridge (L4)"; review 2026-10-21 finding 1): at a declaring filer ttm.py --interim
    rescales the bridge's per-share figures onto total units (617,000,000 + 61,700,000 = 678,700,000), so make_score's
    step-4 re-derivation of the bridge (interim_bridge.recompute_from_record, on the filed share leg) is compared with
    the filed-basis twins and the rescale is re-derived from the share_classes block — it had read every such ttm.json
    as edited and refused every declared bridge. End to end: the --ttm score on the bridge scores, with the share-class
    replay at ttm_oe_per_share_filed_basis; a ttm.json whose total-unit pin was edited (or whose block disagrees with
    the declaration) is still refused at step 4."""
    n, rows, tt, fx, j = _ib_declared_pipeline()
    import test_make_score_57_interim as IB
    assert tt["ttm_shares_diluted"] == 678700000 and tt["ttm_shares_diluted_filed"] == 617000000, tt["ttm_shares_diluted"]
    assert n["base_oe_per_share"] == tt["ttm_oe_per_share"] and n["share_classes"]["ttm"]["leg"] == "interim"
    r = IB.score(n, j, rows, tt, fx)
    assert r.rc == 0, r.err[-3000:]
    s = r.result["score"]
    assert s["interim_bridge"]["basis"] == "declared_interim", s["interim_bridge"]
    sc = s["share_classes"]
    assert sc["base_used"] == "ttm" and sc["measured"] and sc["replay_pin"] == tt["ttm_oe_per_share_filed_basis"], sc
    assert sc["base_oe_total_units"] == round(tt["ttm_oe_per_share"], 4), sc
    # in process: step 4 on the declared ttm.json, then on ttm.json edited after ttm.py
    assert [m for st, m in M._interim_problems(n, j, tt) if st == 4] == []
    for edit in (lambda t: t.update(ttm_oe_per_share=t["ttm_oe_per_share"] * 1.01),
                 lambda t: t.update(ttm_shares_diluted=t["ttm_shares_diluted"] + 1e6),
                 lambda t: t["share_classes"].update(units_equivalent=t["share_classes"]["units_equivalent"] + 1e6),
                 lambda t: t.update(ttm_oe_per_share_filed_basis=t["ttm_oe_per_share_filed_basis"] * 1.01)):
        bad = copy.deepcopy(tt)
        edit(bad)
        assert [m for st, m in M._interim_problems(n, j, bad) if st == 4], bad


if __name__ == "__main__":
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn) and fn.__module__ == __name__:
            try:
                fn()
                print(f"PASS {name}")
            except AssertionError as e:
                fails += 1
                print(f"FAIL {name}: {str(e)[:2500]}")
            except Exception as e:
                fails += 1
                import traceback
                print(f"ERROR {name}: {type(e).__name__}: {e}\n{traceback.format_exc()[-2500:]}")
    sys.exit(1 if fails else 0)
