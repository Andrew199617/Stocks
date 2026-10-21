#!/usr/bin/env python3
"""Engine 5.7 — ruling R1, the mechanical sector-misfit notch and EDGAR SIC misfit detection (Andrew, 2026-10-19;
lane L1 of the rulings PR, design 01 re-anchored by rebase/L1.md; Q1 default (b) of 12_lane_defaults).
Run: python _system/tests/test_misfit_notch_57.py (or python -m pytest _system/tests). No network: engine runs go
through engine55_harness (fixtures, temp bases), make_score runs as a subprocess in a temp STOCKS_BASE through
test_make_score_55.Run (the registry redirected), reprice / build_site are called as pure functions.

Each test names how it fails on the scaffold (e22e814) — the code before this lane:
 T-1  test_release_is_570: the release is 5.7.0 and is_57_run is the rulings predicate (L0 shipped both: this one
      PASSES on e22e814 by design and pins them for the lane's own obligations).
 T-2  test_sic_ranges_and_the_sector_set_aside: the misfit SIC classes, the Q1 (b) set-aside predicate and the
      sector_model record (e22e814: no sic_sets_aside_sector / sector_model_record).
 T-3  test_engine_flags_a_sic_only_misfit: a modeled fixture (AR, Energy) given SIC 6324 is a misfit by SIC, with
      the SIC flag text and a sector_model record (e22e814: no flag, no record).
 T-4  test_engine_sector_flag_text_unchanged: the universe-sector flag is byte-identical, basis sector (+ sic).
 T-4b test_engine_sector_set_aside_by_sic: a Utilities fixture with SIC 4953 (waste) is not flagged; the switch off
      flags it again (e22e814: flagged, no record).
 T-5  test_sic_fetch_failure_degrades: a failed EDGAR fetch falls back to the folder's fundamentals.json / profile.json
      SIC, and to the sector rule alone with neither (e22e814: no fallback, no record).
 T-6  test_one_submissions_fetch_per_run: the SIC comes from the run's ONE submissions fetch (e22e814: one fetch, but
      no SIC read — no sector_model).
 T-9  test_delta_nwc_uses_assembled_current_debt: NWC subtracts the assembled current debt (synthetic filer with
      LongTermDebtCurrent only, and the ATO fixture's component-only rows) (e22e814: the aggregate tag only).
 T-7  test_notch_matrix, T-8 test_57_requires_a_numeric_reason, T-10 test_payable_pin_not_notched_and_double_softening
      _kept, T-11 test_hand_pin_is_notched, T-12 test_folder_sic_detects_on_rebuild (incl. the EDU set-aside), T-13
      test_legacy_registry_date_carries, T-17 test_registry_with_misfit_notch_reloads, T-19
      test_notch_on_iprd_adjusted_tier, T-20 test_iprd_hand_override_on_a_misfit, plus
      test_seed_judgment_skips_the_notch and test_tier_block_quotes_echoed_reasons: make_score's notch, refusals,
      registry, key_numbers tier block (e22e814: tier_final = override or numbers tier, no block, no event, no
      refusal, unquoted reasons).
 T-14 test_live_tier_follows_notch and T-18 test_notched_score_live_is_shown: reprice's live notch and build_site
      showing live figures beside every notched state, the unrebuilt legacy score included (e22e814: the live tier
      is the raw numbers tier; T-18 also fails because the score is not notched).
Review fixes of 2026-10-21 (each fails on d9618aa, the lane's first commit, as well as on e22e814):
 test_switch_reaches_a_57_record: SIC_SETS_ASIDE_SECTOR reaches a 5.7 engine record on its next rebuild (d9618aa:
      the recorded misfit=false was final). test_sic_only_57_basis_names_no_sector: a 5.7 SIC-only misfit's basis
      and refusal heads name no universe sector (d9618aa: 'universe sector Health Care'). test_legacy_date_carries_
      through_whitespace: a legacy reason with surrounding whitespace keeps its first date (d9618aa: re-dated).
      test_d_not_applied_reason_beside_a_d_to_f_override: the D block never says there is no tier below D (d9618aa:
      it did, under a published F).
"""
import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
ROOT = os.path.dirname(SYS)
for _p in (HERE, SYS):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import make_score as M  # noqa: E402
import dcf_engine as E  # noqa: E402  (the shared module make_score and reprice use)
import reprice as R  # noqa: E402
import engine55_harness as H  # noqa: E402
import rulings57  # noqa: E402
from test_make_score_55 import Run, _numbers, _judgment, _stamp, _with, _run_with_registry, T, MAKE_SCORE  # noqa: E402

CUR = E.ENGINE_RELEASE
OLD = "5.5.0"   # output from before the rulings release: rebuilt, never bound by the 5.7 obligations
FIN_FLAG = "SECTOR_MODEL_MISMATCH: Finance sector — OE/capex DCF fits finance names poorly; grade confidence low"
RE_FLAG = "SECTOR_MODEL_MISMATCH: Real Estate sector — OE/capex DCF fits real estate names poorly; grade confidence low"
UT_FLAG = "SECTOR_MODEL_MISMATCH: Utilities sector — OE/capex DCF fits utilities names poorly; grade confidence low"
MANAGED_CARE = {"sic": "6324", "sic_description": "Hospital & Medical Service Plans"}
WHY57 = "payable EPS of $4.10 on the 10-K implies a weighted IRR of 13.25%"


def _args(t):
    """The recorded run's scenario inputs, without its base pin (the temp base holds no ttm.json / judgment.json)."""
    rec = H.recorded(t)
    a = H.recorded_args(rec) if rec and rec.get("inputs") else ["--moat", "5"]
    if "--ttm" in a:
        a.remove("--ttm")
    if "--base-oe-ps" in a:
        i = a.index("--base-oe-ps")
        del a[i:i + 2]
    return a


def _engine_run(t, fixture=None, base=None, patch=None):
    fx = fixture or H.load_fixture(t)
    out = H.run_engine(t, args=_args(t), fixture=fx, base=base or H.make_base(fx, {}, None, copy_repo_files=False),
                       patch=patch)
    assert out["exit"] == 0, out["stdout"][-1500:]
    return out


def _sector_flags(n):
    return [f for f in n.get("fragility_flags") or [] if str(f).startswith("SECTOR_MODEL_MISMATCH")]


def _misfit(release=CUR, tier="B", irr=0.17, flags=(FIN_FLAG,), **kw):
    """A synthetic engine record that is a sector misfit by its flag (the pre-5.7 shape; sector_model absent)."""
    n = _numbers(release=release, tier_by_numbers=tier, implied_irr_weighted=irr, implied_irr_base=irr,
                 fragility_flags=list(flags), **kw)
    return n


def _f_record(release=CUR, flags=(FIN_FLAG,)):
    return _misfit(release=release, tier="F", irr=None, iv_at_15=None, iv_at_12=None, upside_at_15=None,
                   scenarios={}, weighted={}, f_subtype="no_cash_generation", base_oe_per_share=-1.5)


# ===========================================================================
# Engine: release, SIC detection, sector_model, the shared submissions fetch, delta_nwc
# ===========================================================================
def test_release_is_570():
    """T-1: the rulings release (L0's bump, which the lane's obligations key on)."""
    assert E.ENGINE_RELEASE == "5.7.0" and M.RELEASE_57 == (5, 7, 0)
    assert M.is_57_run({"engine_release": "5.7.0"}) and M.is_57_run({"engine_release": "5.7.1"})
    assert not M.is_57_run({"engine_release": "5.6.0"}) and not M.is_57_run({"engine_release": OLD})
    assert not M.is_57_run({})


def test_sic_ranges_and_the_sector_set_aside():
    """T-2: 01 §2.1 SIC classes (07 §1.5 BDCs as credit) and Q1 (b): a present SIC outside 6000-6799 and every misfit
    range sets a misfit universe sector aside; finance fee businesses (6200 / 6282 / 6411 / 6531) and misfit SICs never
    do; the switch off (SIC_SETS_ASIDE_SECTOR) is option (a). sector_model_record's schema (01 §6.1 + the flag)."""
    for sic, want in {"6324": "insurance_carrier", "6311": "insurance_carrier", "6331": "insurance_carrier",
                      "6399": "insurance_carrier", "6021": "bank", "6099": "bank", "6141": "credit", "6199": "credit",
                      "6726": "credit", "6211": "broker_dealer", "6798": "reit", "6510": "real_estate_lessor",
                      "4911": "utility", "4941": "utility", "4991": "utility", "4953": None, "4955": None,
                      "6411": None, "6282": None, "6200": None, "6531": None, "7370": None, "": None, None: None,
                      "abc": None}.items():
        assert E.sic_misfit_class(sic) == want, (sic, E.sic_misfit_class(sic))
    aside = {"8200": True, "4953": True, "3661": True, "7389": True, "7320": True, "0100": True, 9995: True,
             "6200": False, "6282": False, "6411": False, "6531": False, "6770": False, "6000": False, "6799": False,
             "6324": False, "4911": False, "6798": False, "4991": False, None: False, "": False, "abc": False}
    for sic, want in aside.items():
        assert E.sic_sets_aside_sector(sic) is want, (sic, want)
    saved = E.SIC_SETS_ASIDE_SECTOR
    try:
        E.SIC_SETS_ASIDE_SECTOR = False
        assert not any(E.sic_sets_aside_sector(s) for s in aside)
        assert E.sector_model_record("Real Estate", "8200", "Educational Services", "fundamentals.json")["misfit"] is True
    finally:
        E.SIC_SETS_ASIDE_SECTOR = saved
    R_ = E.sector_model_record
    assert R_("Health Care", "6324", "Hospital & Medical Service Plans", "edgar_submissions") == {
        "sector": "Health Care", "sic": "6324", "sic_description": "Hospital & Medical Service Plans",
        "sic_source": "edgar_submissions", "sic_class": "insurance_carrier", "misfit": True, "basis": ["sic"],
        "sector_set_aside_by_sic": False}
    assert R_("Utilities", "4924", None, "edgar_submissions")["basis"] == ["sector", "sic"]
    assert R_("Utilities", None, None, None) == {"sector": "Utilities", "sic": None, "sic_description": None,
                                                 "sic_source": None, "sic_class": None, "misfit": True,
                                                 "basis": ["sector"], "sector_set_aside_by_sic": False}
    assert R_("Finance", "6282", "Investment Advice", "profile.json")["basis"] == ["sector"]   # a fee business keeps it
    edu = R_("Real Estate", "8200", "Services-Educational Services", "fundamentals.json")
    assert edu["misfit"] is False and edu["basis"] == [] and edu["sector_set_aside_by_sic"] is True, edu
    assert R_("Energy", None, "ignored", "ignored") == {"sector": "Energy", "sic": None, "sic_description": None,
                                                        "sic_source": None, "sic_class": None, "misfit": False,
                                                        "basis": [], "sector_set_aside_by_sic": False}
    assert R_("", " ", None, None)["sector"] is None and R_("", " ", None, None)["sic"] is None


def test_engine_flags_a_sic_only_misfit():
    """T-3: AR (universe sector Energy) is modeled with no SIC; given EDGAR SIC 6324 it is a misfit by the SIC rule."""
    fx = H.load_fixture("AR")
    n = _engine_run("AR", fixture=fx)["numbers"]
    assert not _sector_flags(n) and n["sector_model"]["sic"] is None and n["sector_model"]["misfit"] is False, n.get("sector_model")
    n = _engine_run("AR", fixture=dict(fx, **MANAGED_CARE))["numbers"]
    sm = n["sector_model"]
    assert sm["misfit"] and sm["basis"] == ["sic"] and sm["sic_class"] == "insurance_carrier", sm
    assert sm["sic_source"] == "edgar_submissions" and sm["sector"] == "Energy", sm
    assert _sector_flags(n) == ["SECTOR_MODEL_MISMATCH: SIC 6324 (Hospital & Medical Service Plans) — OE/capex DCF fits "
                                "insurance carriers poorly (universe sector Energy; EDGAR SIC rule, 2026-10-19); grade "
                                "confidence low"], _sector_flags(n)
    assert E.misfit_status(n)[0] == "misfit" and E.misfit_status(n)[1]["source"] == "engine_sector_model"


def test_engine_sector_flag_text_unchanged():
    """T-4: ATO (Utilities) keeps the v5 flag byte for byte, with or without a SIC (01 §2.4)."""
    fx = H.load_fixture("ATO")
    for extra, basis in (({}, ["sector"]), ({"sic": "4924", "sic_description": "Natural Gas Distribution"},
                                            ["sector", "sic"])):
        n = _engine_run("ATO", fixture=dict(fx, **extra))["numbers"]
        assert _sector_flags(n) == [UT_FLAG], _sector_flags(n)
        assert n["sector_model"]["basis"] == basis and n["sector_model"]["misfit"], n["sector_model"]


def test_engine_sector_set_aside_by_sic():
    """T-4b (Q1 (b)): ATO's Utilities sector with SIC 4953 (refuse systems, outside every misfit range and 6000-6799)
    is not a misfit — no flag, sector_set_aside_by_sic; with the switch off the universe-sector flag returns."""
    fx = dict(H.load_fixture("ATO"), sic="4953", sic_description="Refuse Systems")
    n = _engine_run("ATO", fixture=fx)["numbers"]
    sm = n["sector_model"]
    assert not _sector_flags(n) and sm["misfit"] is False and sm["basis"] == [] and sm["sector_set_aside_by_sic"], sm
    assert E.misfit_status(n)[0] == "modeled" and E.misfit_status(n)[1]["sector_set_aside_by_sic"] is True
    n = _engine_run("ATO", fixture=fx, patch=lambda X: setattr(X, "SIC_SETS_ASIDE_SECTOR", False))["numbers"]
    assert _sector_flags(n) == [UT_FLAG] and n["sector_model"]["basis"] == ["sector"], n["sector_model"]


def test_sic_fetch_failure_degrades():
    """T-5 (01 §2.3, 07 §1.2 amended): edgar_submissions raising -> filer_sic (None, None) -> the folder's
    fundamentals.json profile.sic, else profile.json about.sic; with neither, sic_source null and the sector rule
    alone. The run completes either way and prints no traceback."""
    fx = H.load_fixture("AR")

    def offline(X):
        def boom(_cik):
            raise RuntimeError("offline")
        X.edgar_submissions = boom
    for files, want in (({"fundamentals.json": {"profile": MANAGED_CARE}}, ("6324", "fundamentals.json", True)),
                        ({"profile.json": {"about": {"sic": "6798", "sic_description": "Real Estate Investment Trusts"}}},
                         ("6798", "profile.json", True)),
                        ({"fundamentals.json": {"profile": {"sic": "1311"}}}, ("1311", "fundamentals.json", False)),
                        ({}, (None, None, False))):
        base = H.make_base(fx, {}, None, copy_repo_files=False)
        for name, doc in files.items():
            with open(os.path.join(base, "AR", name), "w", encoding="utf-8") as f:
                json.dump(doc, f)
        out = _engine_run("AR", fixture=fx, base=base, patch=offline)
        sm = out["numbers"]["sector_model"]
        assert (sm["sic"], sm["sic_source"], sm["misfit"]) == want, (files, sm)
        assert "Traceback" not in out["stdout"]
        assert bool(_sector_flags(out["numbers"])) == want[2]


def test_one_submissions_fetch_per_run():
    """T-6 (07 §1.2): with the real edgar_submissions / filer_annual_form, a run fetches the submissions document
    exactly once, and both the annual form and the misfit SIC come from it."""
    calls = []
    doc = {"sic": "6324", "sicDescription": "Hospital & Medical Service Plans",
           "filings": {"recent": {"form": ["8-K", "10-K"]}}}

    def real_fetch(X):
        fresh = H._engine()
        X._submissions_cache.clear()
        for name in ("edgar_submissions", "filer_annual_form"):
            setattr(X, name, types.FunctionType(getattr(fresh, name).__code__, X.__dict__, name))
        inner = X.get_json

        def counting(url, headers=None, timeout=90):
            if "/submissions/" in url:
                calls.append(url)
                return doc
            return inner(url, headers, timeout)
        X.get_json = counting
    n = _engine_run("AR", patch=real_fetch)["numbers"]
    assert len(calls) == 1 and calls[0].endswith(".json"), calls
    assert n["filer_annual_form"] == "10-K", n["filer_annual_form"]
    assert n["sector_model"]["sic"] == "6324" and n["sector_model"]["sic_source"] == "edgar_submissions", n["sector_model"]


def _f(v):
    try:
        return float(v) if v not in (None, "") else None
    except ValueError:
        return None


def test_delta_nwc_uses_assembled_current_debt():
    """T-9 (01 §7; HII #29, AVTR): NWC = (current assets - cash) - (current liabilities - ASSEMBLED current debt).
    (a) A synthetic filer with no DebtCurrent but LongTermDebtCurrent: delta_nwc is the change of
    AC - cash - (LC - LTDcurrent). (b) The ATO fixture (component-only current debt): every row's delta_nwc is the
    change of the NWC recomputed from the fixture's own facts with the CSV's debt_current (= d_cur), and the old
    aggregate-only formula differs on at least one row. oe_maintenance moves by the opposite amount."""
    import test_engine_55 as T55
    facts = T55._syn_facts()
    ug = facts["facts"]["us-gaap"]
    ug.pop("DebtCurrent", None)
    ac, lc, ltdc = {}, {}, {}
    for i, y in enumerate(T55.SYN_YEARS):
        ac[y], lc[y], ltdc[y] = 400e6 + 25e6 * i, 250e6 + 10e6 * i * i, 20e6 + 15e6 * (i % 3)
        for tag, v in (("AssetsCurrent", ac[y]), ("LiabilitiesCurrent", lc[y]), ("LongTermDebtCurrent", ltdc[y])):
            T55._syn_put(facts, tag, "USD", T55._ctx(None, f"{y}-12-31", v, filed=f"{y + 1}-02-20"))
    out = T55._syn_run(facts)
    assert out["exit"] == 0, out["stdout"][-1500:]
    rows = {r["period_end"][:4]: r for r in out["rows"]}
    checked = 0
    for prev, y in zip(T55.SYN_YEARS, T55.SYN_YEARS[1:]):
        r = rows[str(y)]
        assert _f(r["debt_current"]) == ltdc[y], r["debt_current"]
        want = (ac[y] - 100e6 - (lc[y] - ltdc[y])) - (ac[prev] - 100e6 - (lc[prev] - ltdc[prev]))
        old = (ac[y] - 100e6 - lc[y]) - (ac[prev] - 100e6 - lc[prev])
        assert abs(_f(r["delta_nwc"]) - want) < 1.0, (y, r["delta_nwc"], want, old)
        ni, da, cx = _f(r["net_income"]), _f(r["da"]), _f(r["capex"])
        assert abs(_f(r["oe_maintenance"]) - (ni + da - min(cx, da) - want)) < 1.0, (y, r["oe_maintenance"])
        checked += want != old
    assert checked >= 3, checked
    # (b) ATO, the real fixture
    fx = H.load_fixture("ATO")
    rows = _engine_run("ATO", fixture=fx)["rows"]
    IF = "ifrs-full"
    ser = {k: E.period_series(fx["facts"], tags, False)[0] for k, tags in (
        ("ac", ["AssetsCurrent", (IF, "CurrentAssets")]), ("lc", ["LiabilitiesCurrent", (IF, "CurrentLiabilities")]),
        ("cash", ["CashAndCashEquivalentsAtCarryingValue", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
                  (IF, "CashAndCashEquivalents")]),
        ("agg", ["DebtCurrent", (IF, "CurrentBorrowingsAndCurrentPortionOfNoncurrentBorrowings")]))}
    prev_new = prev_old = None
    differs = compared = 0
    for r in rows:
        p = r["period_end"]
        a, l, c = ser["ac"].get(p), ser["lc"].get(p), ser["cash"].get(p) or 0
        if a is None or l is None:
            assert _f(r["delta_nwc"]) is None or prev_new is not None, r
            continue
        new = (a - c) - (l - (_f(r["debt_current"]) or 0))
        old = (a - c) - (l - (ser["agg"].get(p) or 0))
        if prev_new is not None:
            assert abs(_f(r["delta_nwc"]) - (new - prev_new)) < 1.0, (p, r["delta_nwc"], new - prev_new)
            compared += 1
            differs += abs((new - prev_new) - (old - prev_old)) > 1.0
        prev_new, prev_old = new, old
    assert compared >= 5 and differs >= 1, (compared, differs)


# ===========================================================================
# make_score: the notch, its refusals, its record
# ===========================================================================
def _events(r, event):
    return [e for e in r.result["entries"] if e.get("event") == event]


def test_notch_matrix():
    """T-7 (01 §3.3, §3.7, §3.8): a 5.7 misfit at B publishes C with the worker's reason and one misfit_notch event;
    D and F are not notched (the block says why, no event); a further downgrade below the notch is in force (its
    reason kept, both events, "agent override below the notch"); an override at or above the numbers tier is
    refused (R-1) before anything is written."""
    r = _with(_misfit(), _judgment(None, misfit_notch_reason=WHY57))
    assert r.rc == 0, r.err
    s = r.result["score"]
    mn = s["misfit_notch"]
    assert s["tier_final"] == "C" and s["tier_by_numbers"] == "B" and s["model_fit"] == "misfit", s
    assert mn["applies"] is True and mn["tier_after_notch"] == "C" and mn["reason"] == WHY57, mn
    assert mn["reason_source"] == "judgment" and mn["not_applied"] is None, mn
    assert mn["basis"] == {"source": "engine_flag", "sector": "Finance", "sic": None, "sic_description": None,
                           "sic_class": None, "sic_source": None}, mn["basis"]
    assert "tier_override_reason" not in s
    ev = _events(r, "misfit_notch")
    assert len(ev) == 1 and not _events(r, "tier_override"), r.result["entries"]
    assert {k: ev[0][k] for k in ("ticker", "tier_by_numbers", "tier_final", "weighted_irr", "reason", "reason_source",
                                  "basis")} == {"ticker": T, "tier_by_numbers": "B", "tier_final": "C",
                                                "weighted_irr": 0.17, "reason": WHY57, "reason_source": "judgment",
                                                "basis": "engine_flag"}, ev[0]
    assert "- Tier: C (sector-misfit notch: numbers tier B → C) · confidence medium" in r.result["key"], r.result["key"]
    assert f"- Misfit notch (judgment): “{WHY57}”" in r.result["key"]
    # D: the lowest graded tier
    r = _with(_misfit(tier="D", irr=0.061), _judgment(None))
    assert r.rc == 0, r.err
    mn = r.result["score"]["misfit_notch"]
    assert r.result["score"]["tier_final"] == "D" and mn["applies"] is False and mn["not_applied"] == "tier_floor_D", mn
    assert mn["reason"].startswith("cannot notch: numbers tier D (weighted IRR 6.10%)") and mn["tier_after_notch"] == "D", mn
    assert not _events(r, "misfit_notch") and "- Misfit notch: not applied — “cannot notch" in r.result["key"]
    # F: no positive owner's earnings
    r = _with(_f_record(), _judgment(None))
    assert r.rc == 0, r.err
    mn = r.result["score"]["misfit_notch"]
    assert r.result["score"]["tier_final"] == "F" and mn["not_applied"] == "tier_F" and not mn["applies"], mn
    assert mn["reason"].startswith("cannot notch: numbers tier F (no_cash_generation; base OE/share $-1.50)"), mn["reason"]
    assert not _events(r, "misfit_notch")
    # a further downgrade below the notch
    down = "test: the 10-K's dividends from subsidiaries imply 9.5%, below the notch"
    r = _with(_misfit(), _judgment(None, misfit_notch_reason=WHY57, tier_override="D", tier_override_reason=down))
    assert r.rc == 0, r.err
    s = r.result["score"]
    assert s["tier_final"] == "D" and s["tier_override_reason"] == down and s["misfit_notch"]["tier_after_notch"] == "C", s
    assert (f"- Tier: D (sector-misfit notch: numbers tier B → C; agent override below the notch: “{down}”)"
            in r.result["key"]), r.result["key"]
    assert [e["tier_final"] for e in _events(r, "misfit_notch")] == ["C"]
    assert [e["tier_final"] for e in _events(r, "tier_override")] == ["D"]
    # R-1: at or above the numbers tier (above the notch), on a 5.7 run and on a rebuild
    for rel, ov, lower in ((CUR, "B", "D"), (CUR, "A", "D"), (CUR, "S", "D"), (OLD, "B", "C"), (OLD, "A", "C")):
        r = _with(_misfit(release=rel), _judgment(None, misfit_notch_reason=WHY57, tier_override=ov,
                                                  tier_override_reason="test: a lift 1%"))
        r.refused(f"tier_override {ov} is above the misfit-notched tier C",
                  "numbers tier B at a weighted IRR of 17.00% publishes one notch lower as C",
                  f"(or {lower} or lower with a reason)")
        assert not r.result["entries"], r.result["entries"]


def test_57_requires_a_numeric_reason():
    """T-8 (01 §3.3-3.5): on a 5.7 run of a notched misfit, misfit_notch_reason is required (R-3) and carries a number
    (R-4), and an override equal to the notch is refused as redundant (R-2); misfit_notch_reason must be a string or
    null on any run (R-5). Output from before 5.7 rebuilds: a legacy one-notch override is accepted (its reason
    becomes the notch reason, reason_source tier_override, no tier_override event, no tier_override_reason), and
    with no reason at all make_score writes the auto one with the weighted IRR."""
    _with(_misfit(), _judgment(None, misfit_notch_reason=None)).refused(
        "misfit_notch_reason is required on a 5.7 run of a sector misfit", "the reason must carry a number")
    _with(_misfit(), _judgment(None, misfit_notch_reason="screens materially lower")).refused(
        "misfit_notch_reason must carry a number", "got 'screens materially lower'")
    _with(_misfit(), _judgment(None, misfit_notch_reason=WHY57, tier_override="C",
                               tier_override_reason="one notch, 13%")).refused(
        "tier_override C only restates the mechanical misfit notch", "put the reason in misfit_notch_reason")
    for rel in (CUR, OLD):
        _with(_misfit(release=rel), _judgment(None, misfit_notch_reason=5)).refused(
            "misfit_notch_reason must be a string or null")
    legacy = "SECTOR_MODEL_MISMATCH insurer artifact: float in OCF; softened one notch (NI_OCF gap 48%)"
    r = _with(_misfit(release=OLD), _judgment(None, tier_override="C", tier_override_reason=legacy))
    assert r.rc == 0, r.err
    s = r.result["score"]
    assert s["tier_final"] == "C" and "tier_override_reason" not in s, s
    assert s["misfit_notch"]["reason"] == legacy and s["misfit_notch"]["reason_source"] == "tier_override", s
    assert [e["reason_source"] for e in _events(r, "misfit_notch")] == ["tier_override"] and not _events(r, "tier_override")
    assert "agent override" not in r.result["key"] and f"- Misfit notch (tier_override): “{legacy}”" in r.result["key"]
    r = _with(_misfit(release=OLD), _judgment(None))
    assert r.rc == 0, r.err
    mn = r.result["score"]["misfit_notch"]
    assert r.result["score"]["tier_final"] == "C" and mn["reason_source"] == "auto", mn
    assert mn["reason"] == ("Sector misfit (universe sector Finance): numbers tier B at a weighted IRR of 17.00% publishes "
                            "one notch lower as C — the mechanical sector-misfit notch (Andrew, 2026-10-19): the "
                            "owner's-earnings DCF fits finance names poorly. No worker reason on record."), mn["reason"]
    # a worker reason on a rebuild is used (and needs no number there)
    r = _with(_misfit(release=OLD), _judgment(None, misfit_notch_reason="the payable measure is lower"))
    assert r.rc == 0 and r.result["score"]["misfit_notch"]["reason_source"] == "judgment", r.err


def test_payable_pin_not_notched_and_double_softening_kept():
    """T-10 (R1 exception (a)): a misfit on the payable-earnings pin is not notched (not_applied payable_base, its
    reason prints the pin and the IRR; no event) on a 5.7 run with no misfit_notch_reason; an override below the
    numbers tier still hits the existing double-counting refusal, message unchanged."""
    import test_payable_base as TP
    r = TP._score_files(TP._n(flags=[FIN_FLAG]), TP._j())
    assert r["rc"] == 0, r["stderr"] + r["stdout"]
    s, mn = r["score"], r["score"]["misfit_notch"]
    assert s["tier_final"] == "C" and mn["applies"] is False and mn["not_applied"] == "payable_base", mn
    assert mn["reason"].startswith("not notched: the base is the payable-earnings pin (payable_earnings_5y, $27.21/share "
                                   "via --base-judgment; weighted IRR 12.00%)"), mn["reason"]
    assert "- Misfit notch: not applied — “not notched: the base is the payable-earnings pin" in r["key"], r["key"]
    assert not [e for e in r["registry"]["entries"] if e.get("event") in ("misfit_notch", "tier_override")]
    r = TP._score_files(TP._n(flags=[FIN_FLAG]), TP._j(override="D"))
    assert r["rc"] != 0 and "double-counting" in r["stderr"] and "misfit-notched" not in r["stderr"], r["stderr"]


def test_hand_pin_is_notched():
    """T-11 (R1: "a hand pin such as SF's net-income base via --base-oe-ps IS notched"): a declared non-payable
    base_override pin on a misfit at C publishes D."""
    n = _misfit(release="5.4.0", tier="C", irr=0.117, base_oe_per_share=3.0, base_source="agent_supplied_ttm_override")
    n["inputs"] = dict(n["inputs"], base_oe_ps_arg=3.0, base_pin_source="base_oe_ps_arg")
    bo = {"value": 3.0, "kind": "filing", "source": "FY2025 10-K: net income to common $330.5M / 110.2M diluted shares",
          "reason": "test: the OCF base carries client cash; the net-income base"}
    r = _with(n, _judgment(None, base_override=bo))
    assert r.rc == 0, r.err
    s = r.result["score"]
    assert s["tier_final"] == "D" and s["misfit_notch"]["applies"] and s["misfit_notch"]["reason_source"] == "auto", s
    assert "numbers tier C at a weighted IRR of 11.70% publishes one notch lower as D" in s["misfit_notch"]["reason"]
    assert [e["tier_final"] for e in _events(r, "misfit_notch")] == ["D"] and _events(r, "base_override")


def test_folder_sic_detects_on_rebuild():
    """T-12 (01 §3.2 rule 4; Q1 (b) on a rebuild): output from before 5.7 with no flag but a folder SIC of 6324 is a
    misfit on rebuild (basis folder_sic) and notched C -> D; SIC 4953 is modeled. EDU's shape — the Real Estate flag of
    an older run beside the folder's SIC 8200 — is modeled, tier unchanged, the set-aside recorded with its reason;
    with the switch off it is a misfit again (pure check)."""
    fund = lambda sic, desc: {"TST/fundamentals.json": {"profile": {"sic": sic, "sic_description": desc}}}  # noqa: E731
    r = _with(_misfit(release=OLD, tier="C", irr=0.1213, flags=()), _judgment(None),
              files=fund("6324", "Hospital & Medical Service Plans"))
    assert r.rc == 0, r.err
    s = r.result["score"]
    assert s["model_fit"] == "misfit" and s["tier_final"] == "D", s
    mn = s["misfit_notch"]
    assert mn["basis"] == {"source": "folder_sic", "sector": None, "sic": "6324",
                           "sic_description": "Hospital & Medical Service Plans", "sic_class": "insurance_carrier",
                           "sic_source": "fundamentals.json"}, mn["basis"]
    assert mn["reason"].startswith("Sector misfit (EDGAR SIC 6324 Hospital & Medical Service Plans (insurance carriers)): "
                                   "numbers tier C at a weighted IRR of 12.13% publishes one notch lower as D"), mn["reason"]
    assert "fits insurance carriers poorly" in mn["reason"]
    r = _with(_misfit(release=OLD, tier="C", irr=0.1213, flags=()), _judgment(None), files=fund("4953", "Refuse Systems"))
    assert r.rc == 0 and r.result["score"]["model_fit"] == "modeled" and r.result["score"]["tier_final"] == "C", r.err
    assert "misfit_notch" not in r.result["score"] and "misfit_sector_set_aside" not in r.result["score"]
    # EDU: Nasdaq's Real Estate sector, EDGAR SIC 8200 education
    edu = _misfit(release=OLD, tier="C", irr=0.1494, flags=(RE_FLAG,))
    r = _with(edu, _judgment(None), files=fund("8200", "Services-Educational Services"))
    assert r.rc == 0, r.err
    s = r.result["score"]
    assert s["model_fit"] == "modeled" and s["tier_final"] == "C" and "misfit_notch" not in s, s
    sa = s["misfit_sector_set_aside"]
    assert (sa["sector"], sa["sic"], sa["sic_source"], sa["source"]) == ("Real Estate", "8200", "fundamentals.json",
                                                                         "folder_sic"), sa
    assert "EDGAR SIC 8200 Services-Educational Services lies outside" in sa["reason"] and "Q1 (b)" in sa["reason"], sa
    assert "- Sector misfit set aside: “EDGAR SIC 8200" in r.result["key"], r.result["key"]
    assert "sector model misfit" not in json.dumps(s), s.get("exit_alert_suppressed_reason")
    assert not _events(r, "misfit_notch")
    d = tempfile.mkdtemp(prefix="l1_sic_")
    try:
        os.makedirs(os.path.join(d, "EDU"))
        with open(os.path.join(d, "EDU", "fundamentals.json"), "w", encoding="utf-8") as f:
            json.dump({"profile": {"sic": "8200"}}, f)
        assert E.misfit_status(edu, d, "EDU")[0] == "modeled"
        saved = E.SIC_SETS_ASIDE_SECTOR
        try:
            E.SIC_SETS_ASIDE_SECTOR = False
            fit, b = E.misfit_status(edu, d, "EDU")
            assert fit == "misfit" and b["source"] == "engine_flag" and b["sector"] == "Real Estate", (fit, b)
        finally:
            E.SIC_SETS_ASIDE_SECTOR = saved
    finally:
        shutil.rmtree(d, ignore_errors=True)
    # a 5.7 record's sector_model is final; a SIC-rule flag is never read as a sector (rebase §3 item 7)
    sm = E.sector_model_record("Health Care", "6324", "Hospital & Medical Service Plans", "edgar_submissions")
    assert E.misfit_status({"sector_model": sm})[1]["source"] == "engine_sector_model"
    assert E.misfit_status({"sector_model": E.sector_model_record("Industrials", "3711", None, "edgar_submissions"),
                            "fragility_flags": [FIN_FLAG]}) == ("modeled", None)
    sic_flag = ("SECTOR_MODEL_MISMATCH: SIC 6324 (Hospital & Medical Service Plans) — OE/capex DCF fits insurance "
                "carriers poorly (universe sector Health Care; EDGAR SIC rule, 2026-10-19); grade confidence low")
    fit, b = E.misfit_status({"fragility_flags": [sic_flag]})
    assert fit == "misfit" and b["source"] == "engine_flag" and b["sector"] is None, b


def test_legacy_registry_date_carries():
    """T-13 (01 §3.7): a rebuilt legacy one-notch override records a misfit_notch event that keeps the date the
    tier_override event was first taken (keep_first_dates' cross-index); a changed reason is a new declaration."""
    why = "insurer float in OCF; softened one notch to C (NI vs OCF gap 41%)"
    prior = [{"ticker": T, "event": "tier_override", "date": "2026-10-14", "tier_by_numbers": "B", "tier_final": "C",
              "reason": why}]
    r = _run_with_registry(_misfit(release=OLD), _judgment(None, tier_override="C", tier_override_reason=why), prior)
    assert r.rc == 0, r.err
    ev = _events(r, "misfit_notch")
    assert len(ev) == 1 and ev[0]["date"] == "2026-10-14" and ev[0]["reason_source"] == "tier_override", ev
    assert not _events(r, "tier_override"), r.result["entries"]
    r = _run_with_registry(_misfit(release=OLD), _judgment(None, tier_override="C", tier_override_reason=why + " (v2)"),
                           prior)
    assert r.rc == 0 and _events(r, "misfit_notch")[0]["date"] > "2026-10-14", r.result["entries"]


def test_registry_with_misfit_notch_reloads():
    """T-17 (rebase §2.1): a registry holding a misfit_notch event loads on the next run (load_registry refuses an
    unknown event type), and an unchanged declaration keeps its first date."""
    r = Run(_misfit(), _judgment(None, misfit_notch_reason=WHY57))
    try:
        r.run().ok()
        reg = json.load(open(r.registry, encoding="utf-8"))
        ev = [e for e in reg["entries"] if e.get("event") == "misfit_notch"]
        assert len(ev) == 1, reg
        ev[0]["date"] = "2026-10-01"
        with open(r.registry, "w", encoding="utf-8") as f:
            json.dump(reg, f, indent=1)
        r.run().ok()
        assert [e["date"] for e in r.entries("misfit_notch")] == ["2026-10-01"], r.entries()
    finally:
        r.close()


def test_seed_judgment_skips_the_notch():
    """01 §3.6: seeding judgment.json from a score.json never turns the mechanical notch into a tier_override (a
    judgment override in force, or a non-misfit one, is still seeded)."""
    sc = {"scenarios": {lbl: {"prob": p} for lbl, p in zip(M.LABELS, [0.1, 0.25, 0.3, 0.25, 0.1])},
          "tier_by_numbers": "B", "tier_final": "C", "name": "X", "sector": "Finance", "moat_score": 5,
          "moat_justification": "m", "one_liner": "o", "confidence": "low", "in_scope_under_40b": True,
          "misfit_notch": {"applies": True, "tier_by_numbers": "B", "tier_after_notch": "C"}}
    d = tempfile.mkdtemp(prefix="l1_seed_")
    try:
        for score, want in ((sc, None), (dict(sc, tier_final="D"), "D"),
                            ({k: v for k, v in sc.items() if k != "misfit_notch"}, "C")):
            M.seed_judgment(d, score)
            assert json.load(open(os.path.join(d, "judgment.json"), encoding="utf-8"))["tier_override"] == want, score
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_tier_block_quotes_echoed_reasons():
    """07 §1.10: the tier block echoes worker text through quoted() — a non-misfit override's reason too."""
    n = _numbers(release=OLD)
    r = _with(n, _judgment(n, tier_override="C", tier_override_reason="test: sized like a C (net debt 3.1x)"))
    assert r.rc == 0, r.err
    assert "- Tier: C (agent override of B: “test: sized like a C (net debt 3.1x)”) · confidence medium" in r.result["key"]
    assert "misfit_notch" not in r.result["score"] and r.result["score"]["tier_override_reason"].startswith("test:")
    assert [e["tier_final"] for e in _events(r, "tier_override")] == ["C"]


def test_rulings57_add_notch_reason():
    """07 G16 / rebase §3 item 14: the pre-existing tests' 5.7 obligation for a notched misfit — a current-release
    misfit at S-C off the payable base gets a misfit_notch_reason with one number; every other record (a modeled
    name, D / F, the payable base, output from before 5.7, a judgment that already sets the field) is untouched, and
    so is tier_override."""
    n = _misfit()
    _, j = rulings57.apply(n, _judgment(None, tier_override="D", tier_override_reason="r 1"))
    assert j["misfit_notch_reason"] == rulings57.NOTCH_REASON and j["tier_override"] == "D", j
    assert any(c.isdigit() for c in rulings57.NOTCH_REASON)
    sm = E.sector_model_record("Health Care", "6324", None, "edgar_submissions")
    assert "misfit_notch_reason" in rulings57.apply(_numbers(sector_model=sm), _judgment(None))[1]
    for rec in (_numbers(), _misfit(tier="D", irr=0.06), _f_record(), _misfit(release=OLD),
                _misfit(payable_base={"basis": "payable_earnings_5y"})):
        j0 = _judgment(None)
        assert rulings57.apply(rec, j0)[1] == j0, rec.get("tier_by_numbers")
    j0 = _judgment(None, misfit_notch_reason=None)
    assert rulings57.apply(n, j0)[1] == j0


def _iprd():
    import test_make_score_iprd as TMI
    return TMI


def test_notch_on_iprd_adjusted_tier():
    """T-19 (07 G2; rebase §3 item 8): the notch acts on the IPR&D-ADJUSTED numbers tier, and the auto reason prints
    the adjusted weighted IRR with the deduction named."""
    TMI = _iprd()
    n = copy.deepcopy(TMI._one_time())
    tb = n["tier_by_numbers"]
    assert tb in ("S", "A", "B", "C") and n["iprd_adjustment"]["charge_per_share"] > 0, (tb, n["iprd_adjustment"])
    n["fragility_flags"] = list(n["fragility_flags"]) + [FIN_FLAG]
    r = TMI._score(dict(n, engine_release="5.6.0"))
    assert r.rc == 0, r.err[-800:]
    mn = r.result["score"]["misfit_notch"]
    assert r.result["score"]["tier_final"] == E.notch_tier(tb) and mn["reason_source"] == "auto", mn
    assert (f"numbers tier {tb} at a weighted IRR of {n['implied_irr_weighted'] * 100:.2f}% (after the one-time "
            f"acquired-IPR&D deduction) publishes one notch lower as {E.notch_tier(tb)}") in mn["reason"], mn["reason"]
    r = TMI._score(n, TMI._j(misfit_notch_reason=WHY57))   # a 5.7 run: the worker's reason, the same adjusted tier
    assert r.rc == 0 and r.result["score"]["tier_final"] == E.notch_tier(tb), r.err[-800:]


def test_iprd_hand_override_on_a_misfit():
    """T-20 (rebase §3 item 6): treatment not_applied_share_count_unverified REQUIRES the main agent's quantified
    tier_override; on a 5.7 misfit that override may sit AT the notched tier (no R-2) and is then in force (its reason
    kept, both events); an override at the numbers tier is still refused (R-1: the hand-adjusted tier is notched)."""
    TMI = _iprd()
    n, bo = TMI._share_count_unverified()
    n = copy.deepcopy(n)
    tb = n["tier_by_numbers"]
    assert tb in ("S", "A", "B", "C") and M.iprd_override_required(n), tb
    n["fragility_flags"] = list(n["fragility_flags"]) + [FIN_FLAG]
    why = ("main agent: $40,000,000 / 100,000,000 verified diluted shares (FY2025 10-K cover) = $0.40/share deducted "
           "by hand; adjusted weighted IRR 9.6%, same band")
    r = TMI._score(n, TMI._j(base_override=bo, tier_override=E.notch_tier(tb), tier_override_reason=why,
                             misfit_notch_reason=WHY57))
    assert r.rc == 0, r.err[-800:]
    s = r.result["score"]
    assert s["tier_final"] == E.notch_tier(tb) and s["tier_override_reason"] == why, s
    assert s["misfit_notch"]["applies"] and s["misfit_notch"]["tier_after_notch"] == E.notch_tier(tb), s["misfit_notch"]
    assert [e["tier_final"] for e in r.result["entries"] if e.get("event") == "misfit_notch"] == [E.notch_tier(tb)]
    assert [e["tier_final"] for e in r.result["entries"] if e.get("event") == "tier_override"] == [E.notch_tier(tb)]
    assert "agent override at the notched tier (acquired-IPR&D hand deduction)" in r.result["key"], r.result["key"]
    r = TMI._score(n, TMI._j(base_override=bo, tier_override=tb, tier_override_reason=why, misfit_notch_reason=WHY57))
    assert r.rc == 1 and f"tier_override {tb} is above the misfit-notched tier" in r.err, r.err[-800:]


# ===========================================================================
# Review fixes (2026-10-21) — each of these fails on d9618aa, the lane's first commit
# ===========================================================================
# make_score.py with dcf_engine.SIC_SETS_ASIDE_SECTOR set False before make_score imports the engine — Q1 option (a),
# exactly as Andrew would set it by editing the one constant
SWITCH_OFF = r'''import runpy, sys
sys.path.insert(0, sys.argv[1])
import dcf_engine
dcf_engine.SIC_SETS_ASIDE_SECTOR = False
script, ticker = sys.argv[2], sys.argv[3]
sys.argv = [script, ticker]
runpy.run_path(script, run_name="__main__")
'''


class _SwitchOffRun(Run):
    """Run, with make_score.py started through SWITCH_OFF (the same temp STOCKS_BASE, registry and folder)."""

    def run(self):
        env = dict(os.environ, STOCKS_BASE=self.base, PYTHONIOENCODING="utf-8", MAKE_SCORE_REGISTRY=self.registry)
        r = subprocess.run([sys.executable, "-P", "-c", SWITCH_OFF, SYS, MAKE_SCORE, T], capture_output=True,
                           text=True, encoding="utf-8", env=env, timeout=120)
        self.rc, self.out, self.err = r.returncode, r.stdout, r.stderr
        return self


def _with_switch_off(n, j):
    r = _SwitchOffRun(n, j).run()
    try:
        r.result = dict(r.state(), score=r.score() if r.rc == 0 else None, key=r.key() if r.rc == 0 else None,
                        entries=r.entries())
    finally:
        r.close()
    return r


EDU_SIC = ("8200", "Services-Educational Services", "edgar_submissions")


def test_switch_reaches_a_57_record():
    """Review fix 1: SIC_SETS_ASIDE_SECTOR is the ONE switch for Q1 — it reaches a record the 5.7 engine wrote, not only
    an older one. misfit_status re-derives a 5.7 record's answer from the universe sector and SIC the engine recorded,
    under the current rules (sector_model_record), so EDU scored at 5.7 with the switch on (set aside, no flag) is a
    misfit once the switch is off: notched C -> D, no misfit_sector_set_aside; and a record the engine wrote with the
    switch off (the Real Estate flag, misfit) is set aside once it is on. (d9618aa: the recorded misfit was final, so
    flipping the switch left every 5.7 set-aside name modeled until an engine re-run.)"""
    on = E.sector_model_record("Real Estate", *EDU_SIC)
    assert on["misfit"] is False and on["sector_set_aside_by_sic"] is True, on
    edu = _numbers(release=CUR, tier_by_numbers="C", implied_irr_weighted=0.1494, implied_irr_base=0.1494,
                   fragility_flags=[], sector_model=on)
    saved = E.SIC_SETS_ASIDE_SECTOR
    try:
        E.SIC_SETS_ASIDE_SECTOR = False
        fit, b = E.misfit_status(edu)
        assert fit == "misfit" and b == {"source": "engine_sector_model", "sector": "Real Estate", "sic": "8200",
                                         "sic_description": "Services-Educational Services", "sic_class": None,
                                         "sic_source": "edgar_submissions"}, (fit, b)
        assert M.misfit_set_aside_record(fit, b) is None
        written_off = dict(edu, sector_model=E.sector_model_record("Real Estate", *EDU_SIC), fragility_flags=[RE_FLAG])
        assert written_off["sector_model"]["misfit"] is True and E.misfit_status(written_off)[0] == "misfit"
    finally:
        E.SIC_SETS_ASIDE_SECTOR = saved
    fit, b = E.misfit_status(written_off)          # the switch back on: the record written with it off is set aside
    assert fit == "modeled" and b["sector_set_aside_by_sic"] is True and b["source"] == "engine_sector_model", (fit, b)
    # make_score end to end: the default switch, then option (a)
    j = _judgment(None, misfit_notch_reason=WHY57)
    r = _with(edu, j)
    assert r.rc == 0, r.err
    s = r.result["score"]
    assert s["model_fit"] == "modeled" and s["tier_final"] == "C" and "misfit_notch" not in s, s
    sa = s["misfit_sector_set_aside"]
    assert (sa["sector"], sa["sic"], sa["sic_source"], sa["source"]) == ("Real Estate", "8200", "edgar_submissions",
                                                                         "engine_sector_model"), sa
    r = _with_switch_off(edu, j)
    assert r.rc == 0, r.err
    s = r.result["score"]
    assert s["model_fit"] == "misfit" and s["tier_final"] == "D" and "misfit_sector_set_aside" not in s, s
    mn = s["misfit_notch"]
    assert mn["applies"] and mn["tier_after_notch"] == "D" and mn["reason"] == WHY57, mn
    assert mn["basis"]["sector"] == "Real Estate" and mn["basis"]["source"] == "engine_sector_model", mn["basis"]
    assert "- Tier: D (sector-misfit notch: numbers tier C → D)" in r.result["key"], r.result["key"]
    assert "Sector misfit set aside" not in r.result["key"], r.result["key"]
    assert [e["tier_final"] for e in r.result["entries"] if e.get("event") == "misfit_notch"] == ["D"]


def test_sic_only_57_basis_names_no_sector():
    """Review fix 2: on a 5.7 run of a misfit caught only by its SIC (OSCR / MOH / CNC: universe sector Health Care,
    SIC 6324) the basis names no universe sector (01 §6.3: the misfit sector or null), so the reason and every refusal
    head read 'sector misfit (EDGAR SIC 6324 ...)', exactly as a rebuild from the folder SIC does; a record where the
    sector rule fired keeps its sector. (d9618aa: basis.sector 'Health Care', and 'universe sector Health Care' in every
    head, as if the sector rule had fired.)"""
    sm = E.sector_model_record("Health Care", "6324", "Hospital & Medical Service Plans", "edgar_submissions")
    want = {"source": "engine_sector_model", "sector": None, "sic": "6324",
            "sic_description": "Hospital & Medical Service Plans", "sic_class": "insurance_carrier",
            "sic_source": "edgar_submissions"}
    assert E.misfit_status({"sector_model": sm}) == ("misfit", want), E.misfit_status({"sector_model": sm})
    rebuilt = E.misfit_status({}, sic=("6324", "Hospital & Medical Service Plans", "fundamentals.json"))[1]
    same = lambda b: {k: v for k, v in b.items() if k not in ("source", "sic_source")}  # noqa: E731
    assert same(rebuilt) == same(want), rebuilt
    for sector, sic, desc in (("Finance", "6211", "Security Brokers, Dealers & Flotation Companies"),
                              ("Finance", "6282", "Investment Advice"), ("Utilities", "4924", "Natural Gas Distribution"),
                              ("Utilities", None, None)):
        rec = E.sector_model_record(sector, sic, desc, "edgar_submissions")
        assert E.misfit_status({"sector_model": rec})[1]["sector"] == sector, rec
    flag = ("SECTOR_MODEL_MISMATCH: SIC 6324 (Hospital & Medical Service Plans) — OE/capex DCF fits insurance carriers "
            "poorly (universe sector Health Care; EDGAR SIC rule, 2026-10-19); grade confidence low")
    n = _numbers(release=CUR, tier_by_numbers="C", implied_irr_weighted=0.1213, implied_irr_base=0.1213,
                 fragility_flags=[flag], sector_model=sm)
    head = ("sector misfit (EDGAR SIC 6324 Hospital & Medical Service Plans (insurance carriers)): numbers tier C at a "
            "weighted IRR of 12.13% publishes one notch lower as D")
    r = _with(n, _judgment(None, misfit_notch_reason=None))    # R-3 (None keeps rulings57 from adding a reason)
    r.refused(f"misfit_notch_reason is required on a 5.7 run of a sector misfit ({head})")
    assert "universe sector" not in r.err, r.err
    r = _with(n, _judgment(None, misfit_notch_reason=WHY57, tier_override="B", tier_override_reason="test: a lift 1%"))
    r.refused(f"tier_override B is above the misfit-notched tier D — {head}")                                   # R-1
    r = _with(n, _judgment(None, misfit_notch_reason=WHY57))
    assert r.rc == 0, r.err
    assert r.result["score"]["misfit_notch"]["basis"] == want, r.result["score"]["misfit_notch"]["basis"]


def test_legacy_date_carries_through_whitespace():
    """Review fix 4: a legacy one-notch reason saved with surrounding whitespace keeps the date it was first taken.
    The old tier_override event recorded the raw text and the misfit_notch event records it stripped (score.json too),
    so keep_first_dates' cross-index compares the legacy reason stripped. (d9618aa: re-dated the run day.)"""
    core = "insurer float in OCF; softened one notch to C (NI vs OCF gap 41%)"
    for raw in (core + " ", "\n" + core + "  \n"):
        prior = [{"ticker": T, "event": "tier_override", "date": "2026-10-14", "tier_by_numbers": "B",
                  "tier_final": "C", "reason": raw}]
        r = _run_with_registry(_misfit(release=OLD), _judgment(None, tier_override="C", tier_override_reason=raw), prior)
        assert r.rc == 0, r.err
        ev = _events(r, "misfit_notch")
        assert len(ev) == 1 and ev[0]["date"] == "2026-10-14" and ev[0]["reason"] == core, (repr(raw), ev)
        assert r.result["score"]["misfit_notch"]["reason"] == core, r.result["score"]["misfit_notch"]
    new = [{"ticker": T, "event": "misfit_notch", "date": "2026-10-21", "tier_by_numbers": "B", "tier_final": "C",
            "reason": core}]
    M.keep_first_dates(new, prior)
    assert new[0]["date"] == "2026-10-14", new
    other = [dict(new[0], date="2026-10-21", reason=core + " (v2)")]   # a changed reason is still a new declaration
    M.keep_first_dates(other, prior)
    assert other[0]["date"] == "2026-10-21", other


D_NOT_APPLIED = ("cannot notch: numbers tier D (weighted IRR 6.10%) is the lowest graded tier (F means no positive "
                 "owner's earnings, not a notch) — the mechanical sector-misfit notch (Andrew, 2026-10-19) is not applied")


def test_d_not_applied_reason_beside_a_d_to_f_override():
    """Review fix 5: the D block's reason never claims there is no tier below D — 01 §3.3 keeps a D misfit's D -> F
    judgment override, and key_numbers.md prints that published F right above the reason. (d9618aa: 'so there is no
    tier below it to publish'.)"""
    why_f = "test: going concern doubt, 2 covenant breaches"
    for j, tier in ((_judgment(None), "D"), (_judgment(None, tier_override="F", tier_override_reason=why_f), "F")):
        r = _with(_misfit(tier="D", irr=0.061), j)
        assert r.rc == 0, r.err
        s = r.result["score"]
        mn = s["misfit_notch"]
        assert s["tier_final"] == tier and mn["not_applied"] == "tier_floor_D" and mn["reason"] == D_NOT_APPLIED, s
        assert f"- Misfit notch: not applied — “{D_NOT_APPLIED}”" in r.result["key"], r.result["key"]
        assert "no tier below" not in r.result["key"], r.result["key"]
    assert f"- Tier: F (agent override of D: “{why_f}”)" in r.result["key"], r.result["key"]


# ===========================================================================
# reprice: the live tier follows the notch; build_site shows it
# ===========================================================================
def _app_misfit():
    """APP's committed run as a Finance misfit (flag added, re-stamped) and its score as make_score's notch would
    write it (numbers B -> C)."""
    n = json.load(open(os.path.join(ROOT, "APP", "dcf_numbers.json"), encoding="utf-8"))
    s = json.load(open(os.path.join(ROOT, "APP", "score.json"), encoding="utf-8"))
    n = _stamp(dict(n, fragility_flags=list(n.get("fragility_flags") or []) + [FIN_FLAG]))
    blk = {"applies": True, "tier_by_numbers": "B", "tier_after_notch": "C", "reason": "auto 18.43%",
           "reason_source": "auto", "not_applied": None,
           "basis": {"source": "engine_flag", "sector": "Finance", "sic": None, "sic_description": None,
                     "sic_class": None, "sic_source": None}}
    s = dict(s, tier_final="C", model_fit="misfit", misfit_notch=blk, dcf_content_hash=n["content_hash"])
    s.pop("tier_override_reason", None)
    return n, s


def _price_for(n, irr):
    paths, _ = E.replay_paths(n)
    return E.adjusted_value(paths["weighted"], irr, n["inputs"]["g_terminal"], 0.0)


def test_live_tier_follows_notch():
    """T-14 (01 §4 as amended by rebase §3 item 9): a misfit scored B -> C reads C at the scored price, B when the live
    numbers tier is A, D at C and at D (the D block: applies false); a legacy notch rebuilt (reason_source
    tier_override) is no override; a judgment downgrade below the notch is kept while the numbers tier holds and
    gives way to the NOTCHED live tier when it moves; a score with no block (scored before the notch) reprices
    exactly as before; the pure path (no score) reads the record and the folder SIC; a payable base is never
    notched; live.json carries misfit_notch and scored.tier_after_notch, and one_line says so."""
    n, s = _app_misfit()
    day = n["as_of"]
    px = {"B": n["price"], "A": _price_for(n, 0.22), "C": _price_for(n, 0.12), "D": _price_for(n, 0.08)}
    for numbers_tier, live_tier in (("B", "C"), ("A", "B"), ("C", "D"), ("D", "D")):
        lv = R.reprice(n, px[numbers_tier], day, s, today=day)
        assert lv["tier_by_numbers"] == numbers_tier and lv["tier"] == lv["tier_display"] == live_tier, (numbers_tier, lv["tier"])
        assert lv["override_active"] is False and lv["override_superseded"] is False
        assert lv["misfit_notch"] == {"tier_by_numbers": numbers_tier, "tier_after_notch": live_tier,
                                      "applies": numbers_tier != "D", "basis": "score_json"}, lv["misfit_notch"]
        assert lv["scored"]["tier_after_notch"] == "C" and lv["scored"]["tier_override_reason"] is None
        assert lv["delta"]["tier_changed_vs_final"] is (live_tier != "C")
    lv = R.reprice(n, px["B"], day, s, today=day)
    line = R.one_line(lv)
    assert "B (final C)" in line and "C (numbers B, misfit notch)" in line, line
    # the legacy notch rebuilt: no override either
    leg = dict(s, misfit_notch=dict(s["misfit_notch"], reason_source="tier_override", reason="legacy 1 notch"))
    assert R.reprice(n, px["A"], day, leg, today=day)["tier"] == "B"
    # a judgment downgrade below the notch
    dn = dict(s, tier_final="D", tier_override_reason="test: further down (9%)")
    lv = R.reprice(n, px["B"], day, dn, today=day)
    assert lv["tier"] == "D" and lv["override_active"] and not lv["override_superseded"], lv["tier"]
    assert lv["scored"]["tier_override_reason"] == "test: further down (9%)"
    lv = R.reprice(n, px["A"], day, dn, today=day)
    assert lv["tier"] == "B" and lv["override_active"] and lv["override_superseded"], lv["tier"]
    assert "override D superseded, misfit notch)" in R.one_line(lv), R.one_line(lv)
    # a score with no block (a pre-notch score of a flagged misfit: legacy tier_override C) — exactly as before L1
    old = {k: v for k, v in s.items() if k != "misfit_notch"}
    old.update(tier_override_reason="legacy one notch")
    lv = R.reprice(n, px["B"], day, old, today=day)
    assert (lv["tier"], lv["override_active"], lv["override_superseded"]) == ("C", True, False), lv["tier"]
    assert lv["scored"]["tier_override_reason"] == "legacy one notch" and lv["misfit_notch"] is None
    assert lv["scored"]["tier_after_notch"] is None
    lv = R.reprice(n, px["A"], day, old, today=day)
    assert (lv["tier"], lv["override_superseded"]) == ("A", True), lv["tier"]
    # payable base: never notched live
    pay = dict(s, misfit_notch=dict(s["misfit_notch"], applies=False, tier_after_notch="B", not_applied="payable_base"),
               tier_final="B")
    lv = R.reprice(n, px["B"], day, pay, today=day)
    assert lv["tier"] == "B" and lv["misfit_notch"] is None and not lv["override_active"], lv["tier"]
    # the pure path without a score.json
    lv = R.reprice(n, px["B"], day, None, today=day)
    assert lv["tier"] == "C" and lv["misfit_notch"]["basis"] == "engine" and lv["scored"]["tier_after_notch"] == "C"
    assert lv["delta"]["tier_changed_vs_final"] is False
    plain = json.load(open(os.path.join(ROOT, "APP", "dcf_numbers.json"), encoding="utf-8"))
    assert R.reprice(plain, px["B"], day, None, today=day)["tier"] == "B"
    lv = R.reprice(plain, px["B"], day, None, today=day, folder_sic="6324")
    assert lv["tier"] == "C" and lv["misfit_notch"]["basis"] == "folder_sic", lv["misfit_notch"]
    assert R.reprice(plain, px["B"], day, None, today=day, folder_sic="7370")["misfit_notch"] is None
    pb = dict(n, payable_base={"basis": "payable_earnings_5y"})
    assert R.reprice(pb, px["B"], day, None, today=day)["tier"] == "B"
    assert "misfit's live tier is one notch below its live numbers tier" in R.BASIS


def _app_score_run(j_kw, prior=None):
    """make_score on APP's run as a Finance misfit (folder TST, its ttm.json for the pin); returns (stamped numbers as
    on disk, score)."""
    n = json.load(open(os.path.join(ROOT, "APP", "dcf_numbers.json"), encoding="utf-8"))
    n = dict(n, ticker=T, fragility_flags=list(n.get("fragility_flags") or []) + [FIN_FLAG])
    tt = json.load(open(os.path.join(ROOT, "APP", "ttm.json"), encoding="utf-8"))
    j = dict(json.load(open(os.path.join(ROOT, "APP", "judgment.json"), encoding="utf-8")), **j_kw)   # its capex_override
    r = _with(n, j, files={"TST/ttm.json": tt})
    assert r.rc == 0, r.err[-1500:]
    return _stamp(n), r.result["score"]


def test_notched_score_live_is_shown():
    """T-18 (rebase §2.3): reprice's live.json beside a make_score notched score is shown by build_site (live_shown)
    in every state — (i) an auto notch, (ii) a rebuilt legacy notch, (iii) a further downgrade, (iv) an UNREBUILT
    legacy score (no block, its tier_override equal to the notch, as the code before the notch wrote it)."""
    import build_site as B
    legacy = "insurer artifact: OCF carries float; one notch (18.43% numbers IRR)"
    states = {}
    m, states["auto"] = _app_score_run({})
    _, states["legacy"] = _app_score_run({"tier_override": "C", "tier_override_reason": legacy})
    _, states["down"] = _app_score_run({"tier_override": "D", "tier_override_reason": "test: further down 9%"})
    assert [states[k]["tier_final"] for k in ("auto", "legacy", "down")] == ["C", "C", "D"], states
    assert "tier_override_reason" not in states["legacy"] and states["down"]["tier_override_reason"].startswith("test:")
    unrebuilt = {k: v for k, v in states["legacy"].items() if k != "misfit_notch"}
    unrebuilt["tier_override_reason"] = legacy
    states["unrebuilt"] = unrebuilt
    day = m["as_of"]
    for name, s in states.items():
        live = R.reprice(m, m["price"], day, s, today=day)
        assert live["tier"] == s["tier_final"], (name, live["tier"])
        shown, why = B.live_shown({"numbers": m, "score": s, "live": live})
        assert shown == live and why is None, (name, why)


if __name__ == "__main__":
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn(); print(f"PASS {name}")
            except AssertionError as e:
                fails += 1; print(f"FAIL {name}: {str(e)[:1500]}")
            except Exception as e:
                fails += 1; print(f"ERROR {name}: {type(e).__name__}: {str(e)[:1500]}")
    sys.exit(1 if fails else 0)
