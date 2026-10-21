#!/usr/bin/env python3
"""Declared share classes (Up-C / multi-class share basis) — engine 5.7, Andrew's ruling R6 (2026-10-19/20: "Fix the
engine so it can use the real total share count for two-class companies like VNOM"); designs 08_share_classes.md
(revision 3) + 08b decisions + the rebase map L8.md. Run: python _system/tests/test_share_classes_57.py (or python -m
pytest). Offline: engine55_harness fixtures (VNOM from its real companyfacts, CIK 2074176; DD, TLK, VOD) and the
synthetic SYN filer of test_engine_55 / test_engine_iprd; ttm.py through run_ttm; the interim bridge through
test_ttm_interim's synthetic 20-F folder.

T-1  VNOM's declaration reproduces the merged base ($4.1434/unit to the cent, from the same TTM total) and Tier B.
T-2  VNOM without it: the fake Tier S (25.05%) and UP_C_SUSPECT naming 57.1% / 52.2%.
T-3  every per-share figure on total units (CSV rows, the median, the share CAGR, the record).
T-4  base-window / YTD coverage, the typo guard, roll-forward (unused periods).
T-5  undeclared history leaves the per-share series (the growth inputs shortened).
T-5b zero periods are dated and never straddle (RKT's collapse); A-21's day-weighted kind calc.
T-6  ttm.json's share basis must be the declaration's (the 08 §5.3 table; share_classes.ttm_on_declaration).
T-7  the counterfactual switch (DCF_NO_SHARE_CLASSES with --measure) restores the filed basis, incl. the IPR&D window
     and denominator; the three refusal gates record instead of exiting in that replay only.
T-8  the IPR&D charge per share is per economic unit; the amortized replay (DCF_SC_PIN_SCALE); a share-scale defect
     beside a declaration is refused.
T-9  up_c_signals on the calibration shapes, price drift, malformed facts; the engine never breaks on the detector.
T-10 / T-10b  the cover-page divergence on the traded count; the cap topped up with the units nearest the dei date.
T-11 units follow the split basis of their own filing (engine and ttm.py).
T-12 share_classes and share_class_mismatch are exclusive.
T-13 reprice's live cap prices total units (a guard: passes before L8 too).
T-14 / T-14b an all-class shares_override and a dei fallback row are refused; the no-override replay.
T-15 a diluted count that already includes the exchange; in_filed_count.
T-16 multi_class_common: the exchange ratio scales the units.
T-17 / T-17b ADS filers: units in ordinary shares; the declared interim bridge rescales every per-share field.
T-18 the cap cross-check (universe.csv's own price).
A-6  ttm.json's share-class keys are optional hashed input legs (every committed ttm.json hashes as before).
Review fixes (2026-10-21; each fails on the lane's first build 49c125a):
T-4b rule 6's band covers the current-YTD period (ttm.json's block and the record's share_classes.ttm: out_of_band).
T-8c an iprd_amortized pin on native ttm_json and a basis_window "ttm" pin need ttm.json on the declaration.
T-14c a dei / outstanding fallback row cannot carry in_filed_count units (rule 5b: no basic count to verify them).
T-17c a 20-F filer's declared 6-K bridge current-interim period passes the typo guard (the preliminary run scores).
Every test fails on the code before this lane (4f7d6f1) except T-13 (a guard) and the A-6 compat half.
"""
import copy
import datetime
import gzip
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
ROOT = os.path.dirname(SYS)
for _p in (HERE, SYS):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import engine55_harness as H  # noqa: E402
from test_engine_55 import _syn_facts, _syn_put, _ctx, _syn_fixture, args_for, flags, SYN_YEARS  # noqa: E402

E = H._shared_engine()
VNOM_J = os.path.join(HERE, "fixtures", "share_classes", "VNOM_judgment.json")
VARGS = ["--moat", "6", "--probs", "0.15,0.25,0.3,0.2,0.1", "--offsets", "-0.42,-0.32,-0.24,-0.17,-0.1",
         "--mults", "0.75,0.9,1.0,1.1,1.25"]
ACC = "0000999001-26-000004"      # a synthetic EDGAR accession (in no companyfacts: looked up only beside a split)
DIL = "WeightedAverageNumberOfDilutedSharesOutstanding"
BASIC = "WeightedAverageNumberOfSharesOutstandingBasic"
LAST3 = ("2023-12-31", "2024-12-31", "2025-12-31")


def SC():
    """share_classes (lane L8's module; absent before 5.7 — each test that needs it fails on the old code)."""
    import share_classes
    return share_classes


def sha256_of(d):
    """Rule 8's declaration_sha256, spelled out so the synthetic ttm.json fixtures build on any code (T-1 holds
    ttm.py's block equal to share_classes.declaration_sha256)."""
    import hashlib
    return hashlib.sha256(json.dumps(d, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


_CACHE = {}


def _cached(key, fn):
    if key not in _CACHE:
        _CACHE[key] = fn()
    return _CACHE[key]


# ---------------------------------------------------------------------------
# VNOM (the case)
# ---------------------------------------------------------------------------
def vj(drop=(), **over):
    with open(VNOM_J, encoding="utf-8") as f:
        j = json.load(f)
    for k in drop:
        j.pop(k, None)
    j.update(over)
    return j


def vdecl():
    return vj()["share_classes"]


def drop_period(d, pe):
    d = copy.deepcopy(d)
    for c in d["classes"]:
        c["periods"] = [p for p in c["periods"] if p["period_end"] != pe]
    return d


def add_period(d, pe, values):
    d = copy.deepcopy(d)
    for c, v in zip(d["classes"], values):
        c["periods"].append({"period_end": pe, "value": v, "count_basis": "period_end", "kind": "filing",
                             "accession": "0002074176-26-000030", "source": f"Form 10-Q (test), units at {pe}",
                             "snippet": f"{v:,} units outstanding"})
    return d


def v_ttm(j):
    key = ("vttm", json.dumps(j, sort_keys=True))
    return _cached(key, lambda: H.run_ttm("VNOM", judgment=j))


def v_run(args=(), j=None, ttm=None, measure=False, env=None, no_ttm=False, fixture=None):
    j = vj() if j is None else j
    fx = fixture or H.load_fixture("VNOM")
    base = H.make_base(fx, j, None if no_ttm else ttm, copy_repo_files=False)
    return H.run_engine("VNOM", args=VARGS + list(args), base=base, fixture=fx, measure=measure, env=env)


def v_declared():
    def go():
        t = v_ttm(vj())
        assert t["exit"] == 0, t["stderr"][-1500:]
        out = v_run(["--ttm"], ttm=t["ttm"])
        assert out["exit"] == 0, out["stdout"][-1500:]
        return t["ttm"], out
    return _cached("v_declared", go)


def v_undeclared_ttm():
    def go():
        t = H.run_ttm("VNOM", judgment=vj(drop=("share_classes",)))
        assert t["exit"] == 0, t["stderr"][-1500:]
        return t["ttm"]
    return _cached("v_undeclared_ttm", go)


def _refused(out, *needles, stream="stdout", code=3):
    text = out[stream]
    assert out["exit"] == code, (out["exit"], text[-1500:])
    for s in needles:
        assert s in text, (s, text[-1500:])
    return out


# ---------------------------------------------------------------------------
# the synthetic filer (test_engine_55's SYN: 2019-2025, 100M diluted shares, a basic count beside it here)
# ---------------------------------------------------------------------------
def syn(shares=None, basic=None, dei=(100e6, "2026-01-31", "2026-02-20"), extra_dei=()):
    """shares: {year: diluted count} (None = not filed); basic: {year: basic count} (default 100M every year, None =
    not filed) — the basic count is independent of the diluted one, so a 2.69x diluted year keeps basic 100M."""
    f = _syn_facts(shares=shares, dei=dei)
    b = dict.fromkeys(SYN_YEARS, 100e6)
    b.update(basic or {})
    for y in SYN_YEARS:
        if b.get(y) is not None:
            _syn_put(f, BASIC, "shares", _ctx(f"{y}-01-01", f"{y}-12-31", b[y], filed=f"{y + 1}-02-20"))
    for cnt, date, filed in extra_dei:
        _syn_put(f, "EntityCommonStockSharesOutstanding", "shares",
                 {"end": date, "val": cnt, "fy": int(date[:4]), "fp": "FY", "form": "10-K", "filed": filed,
                  "accn": f"0000999001-{filed[2:4]}-000002"}, taxonomy="dei")
    return f


def ent(pe, value, **kw):
    e = {"period_end": pe, "value": value, "count_basis": "period_end", "kind": "filing", "accession": ACC,
         "source": f"test filing: units outstanding at {pe}", "snippet": f"{value:,.0f} units outstanding"}
    e.update(kw)
    return e


def zent(pe, event, date, **kw):
    e = ent(pe, 0, zero_event=event, event_date=date, source=f"test filing: the class {event} on {date}",
            snippet=f"the class {event.replace('_', ' ')} on {date}")
    e.update(kw)
    return e


def sdecl(units, periods=LAST3, ratio=1, basis="up_c_exchangeable_units", entries=None, **top):
    ps = entries if entries is not None else [ent(p, units[p] if isinstance(units, dict) else units) for p in periods]
    c = {"name": "OpCo units (test)", "holder": "test holders", "exchange_ratio": ratio, "periods": ps}
    if ratio != 1:
        c["ratio_source"] = "test filing: the class's economic rights per share"
    d = {"basis": basis, "traded_class": "Class A common stock (test)",
         "reason": "test: OpCo units held outside the filer, 20% of the units", "classes": [c]}
    d.update(top)
    return d


def s_run(facts, j=None, extra=(), ttm=None, price=30.0, env=None, measure=False, universe=None):
    fx = _syn_fixture(facts, price)
    if universe:
        fx["universe_row"].update(universe)
    base = H.make_base(fx, j if j is not None else {}, ttm, copy_repo_files=False)
    return H.run_engine("SYN", args=args_for(5, extra=list(extra)), base=base, fixture=fx, measure=measure, env=env)


def _ok(out):
    assert out["exit"] == 0, out["stdout"][-2000:]
    return out["numbers"]


def rowmap(out):
    return {r["period_end"]: r for r in out["rows"] or []}


def scflag(n, prefix="SHARE_CLASSES_DECLARED"):
    return flags(n, prefix)


# ===========================================================================
# T-1 / T-2 / T-3 — VNOM
# ===========================================================================
def test_vnom_declaration_reproduces_the_corrected_base_and_tier_b():
    """T-1 (R6 acceptance): ttm.py applies the declaration — 187,553,000 Class A + 171,536,228 declared units =
    359,089,228, $1,488,000,000 TTM OE / unit = $4.1438, the merged base_override pin's $4.1434 to the cent from the
    same TTM total (filed basis $7.9338 kept beside it) — and the engine's --ttm run on that ttm.json scores Tier B,
    15.025%, on total units: 339,647,368 latest-FY units, a $15.291B cap, no false HIGH_NET_DEBT, SHARE_CLASSES_DECLARED
    and no UP_C_SUSPECT / SHARE_CLASSES_CAP_GAP."""
    tt, out = v_declared()
    assert tt["ttm_shares_diluted"] == 359089228 and tt["ttm_shares_diluted_filed"] == 187553000, tt["ttm_shares_diluted"]
    assert abs(tt["ttm_oe_per_share"] - 4.143427182330288) < 0.005 and round(tt["ttm_oe_per_share"], 2) == 4.14
    assert abs(tt["ttm_oe_per_share"] - 1488000000 / 359089228) < 1e-12, tt["ttm_oe_per_share"]
    assert tt["ttm_oe_per_share_filed_basis"] == 7.933757391244075
    blk = tt["share_classes"]
    assert blk["declaration_sha256"] == SC().declaration_sha256(vdecl()) and blk["units_equivalent"] == 171536228
    assert blk["exchange_test"]["test"] == "passed" and blk["diluted_minus_basic"] == 0 and blk["units_split_basis"] == "no_split"
    n = out["numbers"]
    assert n["base_source"] == "ttm_json" and abs(n["base_oe_per_share"] - 4.143427182330288) < 0.005
    assert n["tier_by_numbers"] == "B" and 0.1500 <= n["implied_irr_weighted"] < 0.1505, n["implied_irr_weighted"]
    assert n["shares_diluted_latest"] == 339647368 and abs(n["market_cap_est"] - 15290924507.36) < 1
    assert n["market_cap_basis"]["shares_source"] == "diluted_latest+share_classes", n["market_cap_basis"]
    assert n["market_cap_basis"]["traded_shares"] == 142530000 and n["market_cap_basis"]["declared_units"] == 197117368
    assert abs(n["irr_bear"] - 0.0998) < 0.0005 and n["tier_bear"] == "D" and abs(n["iv_at_15"] - 45.12) < 0.01
    assert scflag(n) and not flags(n, "UP_C_SUSPECT") and not flags(n, "HIGH_NET_DEBT") and not flags(n, "SHARE_CLASSES_CAP_GAP")
    assert n["share_classes"]["ttm"]["total_units"] == 359089228 and n["up_c_check"]["suppressed_by"] == "share_classes"
    assert n["ttm_inputs"]["ttm_shares_diluted"] == 359089228.0


def test_vnom_without_declaration_flags_up_c_suspect():
    """T-2: the same filing facts with no declaration: --ttm on the filed Class A count is the fake Tier S
    ($7.9338, 25.05%) and UP_C_SUSPECT fires — noncontrolling interests 57.1% of equity, 52.2% of consolidated net
    income over 3 FY, the cover page by class (no undimensioned count), the screener's cap 2.52x its price × the filed
    count, diluted ÷ basic 1.000; up_c_check records the detector."""
    out = v_run(["--ttm"], j=vj(drop=("share_classes",)), ttm=v_undeclared_ttm())
    n = _ok(out)
    assert n["base_oe_per_share"] == 7.933757391244075 and n["tier_by_numbers"] == "S"
    assert abs(n["implied_irr_weighted"] - 0.2505) < 0.0005, n["implied_irr_weighted"]
    uc = n["up_c_check"]
    assert uc["suspect"] is True and uc["suppressed_by"] is None and uc["cover_by_class"] is True
    assert abs(uc["nci_share_of_equity"] - 0.5708) < 1e-4 and abs(uc["nci_share_of_net_income_3fy"] - 0.5217) < 1e-4, uc
    assert abs(uc["universe_cap_to_filed_cap"] - 2.5201) < 1e-4 and uc["diluted_to_basic"] == 1.0
    f = flags(n, "UP_C_SUSPECT")
    assert len(f) == 1 and "57.1% of equity" in f[0] and "52.2% of consolidated net income" in f[0], f
    assert "142,530,000" in f[0] and "up_c_suspect_reason" in f[0] and n["share_classes"] is None


def test_declared_units_enter_every_per_share_figure():
    """T-3: on the median base every declared CSV row divides by total units (filed + units, shares_tag
    ...+SHARE_CLASSES, oe_per_share = OE / total); the median is $3.2356, the share-count CAGR 43.49%; the record lists
    the three applied periods with the exchange test (diluted = basic: gap 0) and no split."""
    out = v_run(no_ttm=True)
    n = _ok(out)
    assert n["base_oe_normalized_per_share"] == 3.23556058644467 and n["share_cagr"] == 0.4348779858283134
    exp = {"2023-12-31": (74176000, 90709946), "2024-12-31": (93932000, 95525123), "2025-12-31": (142530000, 197117368)}
    rows = rowmap(out)
    for p, (filed, u) in exp.items():
        r = rows[p]
        assert float(r["shares_diluted"]) == filed + u and r["shares_tag"].endswith("+SHARE_CLASSES"), r
        assert abs(float(r["oe_per_share"]) - float(r["oe_conservative"]) / (filed + u)) < 1e-12
    ap = n["share_classes"]["applied"]
    assert [a["period_end"] for a in ap] == list(exp) and all(a["units_split_basis"] == "no_split" for a in ap)
    assert all(a["diluted_minus_basic"] == 0 and a["exchange_test"]["test"] == "passed" for a in ap)
    assert n["share_classes"]["latest"]["total_units"] == 339647368 and abs(n["share_classes"]["latest"]["declared_share_of_total"] - 0.5804) < 1e-4
    nc = n["share_classes"]["nci_check"]
    assert nc["agrees"] is True and nc["gap_pp"] < 1.0, nc
    assert n["share_classes"]["cap_check"]["gap"] is False and n["share_classes"]["cap_check"]["cap_ratio"] == 2.5201
    assert n["share_classes"]["unused_periods"] == ["2026-06-30"] and n["tier_by_numbers"] == "C"


# ===========================================================================
# T-4 — coverage, typo guard, roll-forward
# ===========================================================================
def test_base_window_and_ttm_period_must_be_declared():
    """T-4: a base-window FY undeclared (FY2024) refuses (BAD_SHARE_CLASSES, exit 3, naming it); ttm.py refuses an
    undeclared current-YTD period; a stray typo period end (no filed share fact ends there) or a future one refuses;
    a class missing a period another class lists, or a kind other than filing / calc, refuses. Roll-forward: the
    prior YTD (2026-03-31, a filed share-fact period end) declared beside the current one scores, listed in
    unused_periods with nothing applied; a median run without ttm.json lists the declared YTD as unused."""
    j = vj(share_classes=drop_period(vdecl(), "2024-12-31"))
    _refused(v_run(no_ttm=True, j=j), "BAD_SHARE_CLASSES", "FY2024")
    t = H.run_ttm("VNOM", judgment=vj(share_classes=drop_period(vdecl(), "2026-06-30")))
    _refused(t, "BAD_SHARE_CLASSES", "no units for the current-YTD period ending 2026-06-30", stream="stderr")
    for bad in ("2025-12-30", "2027-03-31"):
        j = vj(share_classes=add_period(vdecl(), bad, [1000000, 0]))
        if bad == "2027-03-31":
            j["share_classes"]["classes"][1]["periods"][-1].update(
                zero_event="not_yet_issued", event_date="2027-04-01", source="not issued until April 1, 2027")
        else:
            j["share_classes"]["classes"][1]["periods"][-1].update(
                value=10093670, snippet="10,093,670 units outstanding")
        _refused(v_run(no_ttm=True, j=j), "BAD_SHARE_CLASSES", bad)
    d = vdecl()
    d["classes"][1]["periods"] = d["classes"][1]["periods"][:-1]
    _refused(v_run(no_ttm=True, j=vj(share_classes=d)), "BAD_SHARE_CLASSES", "does not list 2026-06-30")
    d = vdecl()
    d["classes"][0]["periods"][0]["kind"] = "estimate"
    _refused(v_run(no_ttm=True, j=vj(share_classes=d)), "BAD_SHARE_CLASSES", "kind must be")
    # roll-forward: the previous YTD left in the declaration
    rf = vj(share_classes=add_period(vdecl(), "2026-03-31", [164811000, 6746384]))
    t = v_ttm(rf)
    assert t["exit"] == 0, t["stderr"][-1500:]
    n = _ok(v_run(["--ttm"], j=rf, ttm=t["ttm"]))
    assert n["share_classes"]["unused_periods"] == ["2026-03-31"], n["share_classes"]["unused_periods"]
    assert "2026-03-31" not in [a["period_end"] for a in n["share_classes"]["applied"]]
    n = _ok(v_run(no_ttm=True))
    assert n["share_classes"]["unused_periods"] == ["2026-06-30"] and n["share_classes"]["ttm_ytd_end_seen"] is None


def _vnom_ytd_units(mult):
    """VNOM's judgment with the 2026-06-30 Class B units set to `mult` x the YTD Class A count (187,553,000)."""
    j = vj()
    big = 187553000 * mult
    for p in j["share_classes"]["classes"][0]["periods"]:
        if p["period_end"] == "2026-06-30":
            p["value"], p["snippet"] = big, f"{big:,} units outstanding (test)"
    return j


def test_ttm_period_units_are_banded():
    """T-4b (rule 6; review 2026-10-21 finding 5): the sanity band (units <= 20x the traded count unless ack_reason)
    covers the current-YTD period ttm.py applies — the period a --ttm base divides by — not only the engine's FY rows.
    VNOM's own YTD units (0.91x the Class A count) are in band in ttm.json's block and the engine record's
    share_classes.ttm; at 21x (3,945,359,384 units on 187,553,000) both record out_of_band true while every FY row
    stays in band (make_score refuses it without ack_reason, M-1b)."""
    tt, out = v_declared()
    assert tt["share_classes"]["out_of_band"] is False, tt["share_classes"]
    assert out["numbers"]["share_classes"]["ttm"]["out_of_band"] is False, out["numbers"]["share_classes"]["ttm"]
    j = _vnom_ytd_units(21)
    t = H.run_ttm("VNOM", judgment=j)
    assert t["exit"] == 0, t["stderr"][-1500:]
    blk = t["ttm"]["share_classes"]
    assert blk["units_equivalent"] == 3945359384 and blk["out_of_band"] is True, blk
    n = _ok(v_run(["--ttm"], j=j, ttm=t["ttm"]))
    rec = n["share_classes"]
    assert rec["ttm"]["out_of_band"] is True and not any(a["out_of_band"] for a in rec["applied"]), rec["ttm"]


# ===========================================================================
# T-5 / T-5b — the per-share series, zero periods, A-21
# ===========================================================================
def test_undeclared_history_leaves_the_per_share_series():
    """T-5: a 20% declaration on the last 3 FY of the 7-year synthetic filer: FY2019-FY2022 keep their filed counts
    with blank oe_per_share / fcf_per_share; the share CAGR spans the declared counts only (from FY2023, not FY2022);
    series_excluded_periods / growth_inputs_shortened record it and SHARE_CLASSES_DECLARED names it."""
    out = s_run(syn(), {"share_classes": sdecl(20e6)})
    n = _ok(out)
    rows = rowmap(out)
    for y in (2019, 2020, 2021, 2022):
        r = rows[f"{y}-12-31"]
        assert float(r["shares_diluted"]) == 100e6 and r["oe_per_share"] == "" and r["fcf_per_share"] == "", r
        assert not r["shares_tag"].endswith("+SHARE_CLASSES")
    for p in LAST3:
        assert float(rows[p]["shares_diluted"]) == 120e6 and rows[p]["shares_tag"] == f"{DIL}+SHARE_CLASSES"
    rec = n["share_classes"]
    assert rec["series_excluded_periods"] == ["2019-12-31", "2020-12-31", "2021-12-31", "2022-12-31"]
    assert rec["growth_inputs_shortened"] == {"share_cagr": {"mixed_basis_from": "2022-12-31", "declared_from": "2023-12-31"}}
    assert n["share_cagr"] == 0.0 and rec["growth_inputs_dropped"] == []
    f = scflag(n)
    assert f and "history FY2019, FY2020, FY2021, FY2022 excluded from per-share inputs" in f[0], f


def _straddle_decl(fy2022_units=20e6, fy2023=None, ended="2023-06-30", tail=True):
    """RKT's shape on the synthetic filer: the class existed all of FY2022 (20% of the count), collapsed on `ended`
    inside FY2023, gone in FY2024-FY2025 (zero periods)."""
    es = [ent("2022-12-31", fy2022_units)]
    es.append(fy2023 if fy2023 is not None else zent("2023-12-31", "ended", ended))
    if tail:
        es += [zent("2024-12-31", "ended", ended), zent("2025-12-31", "ended", ended)]
    return sdecl(None, entries=es)


def test_zero_periods_are_dated_and_never_straddle():
    """T-5b (rule 5; 08 revision 3 finding 4): FY2023 straddles a 2023-06-30 collapse — declared 0 it refuses ("the
    class existed for part of this period"); declared as its weighted-average units it applies; FY2024 / FY2025
    declared 0 (ended on or before their starts) are zero periods on the filed count, inside oe_ps_hist and the share
    series, and the share CAGR runs over FY2022-FY2025 on total units. An event_date not written in its own
    source / snippet, a not_yet_issued dated on or before the period end, a 0 without zero_event, every period 0:
    refused. ttm.py: a YTD entry of 0 straddling its event refuses, weighted units score."""
    _refused(s_run(syn(), {"share_classes": _straddle_decl()}), "BAD_SHARE_CLASSES", "existed for part of this period",
             "2023-06-30 inside 2023-01-01..2023-12-31")
    w = ent("2023-12-31", 10e6, count_basis="weighted_average")
    out = s_run(syn(), {"share_classes": _straddle_decl(fy2023=w)})
    n = _ok(out)
    rows = rowmap(out)
    assert float(rows["2023-12-31"]["shares_diluted"]) == 110e6 and rows["2023-12-31"]["shares_tag"].endswith("+SHARE_CLASSES")
    assert float(rows["2022-12-31"]["shares_diluted"]) == 120e6
    for p in ("2024-12-31", "2025-12-31"):
        assert float(rows[p]["shares_diluted"]) == 100e6 and rows[p]["oe_per_share"] != "", rows[p]
    rec = n["share_classes"]
    assert [z["period_end"] for z in rec["zero_periods"]] == ["2024-12-31", "2025-12-31"]
    assert rec["series_excluded_periods"] == ["2019-12-31", "2020-12-31", "2021-12-31"]
    yrs = (datetime.date(2025, 12, 31) - datetime.date(2022, 12, 31)).days / 365.25
    assert abs(n["share_cagr"] - ((100e6 / 120e6) ** (1 / yrs) - 1)) < 1e-12, n["share_cagr"]
    assert "FY2024 declared 0" in scflag(n)[0]
    # malformed zero entries
    bad = _straddle_decl(fy2023=w)
    bad["classes"][0]["periods"][2]["source"] = "test filing: the class is gone"
    bad["classes"][0]["periods"][2]["snippet"] = "the class is gone"
    _refused(s_run(syn(), {"share_classes": bad}), "BAD_SHARE_CLASSES", "not written in its own source")
    early = sdecl(None, entries=[zent("2023-12-31", "not_yet_issued", "2023-12-31"), ent("2024-12-31", 10e6),
                                 ent("2025-12-31", 10e6)])
    _refused(s_run(syn(), {"share_classes": early}), "BAD_SHARE_CLASSES", "existed for part of this period")
    nz = sdecl(None, entries=[ent("2023-12-31", 0), ent("2024-12-31", 10e6), ent("2025-12-31", 10e6)])
    _refused(s_run(syn(), {"share_classes": nz}), "BAD_SHARE_CLASSES", "zero_event must say why")
    allz = sdecl(None, entries=[zent(p, "ended", "2022-12-31") for p in LAST3])
    _refused(s_run(syn(), {"share_classes": allz}), "BAD_SHARE_CLASSES", "every declared count is 0")
    # ttm.py on VNOM: the TWR IV units declared 0 for the YTD, "ended" mid-YTD (2026-03-31) — straddling
    d = vdecl()
    twr = d["classes"][1]["periods"][-1]
    twr.update(value=0, zero_event="ended", event_date="2026-03-31",
               source="the TWR IV units were exchanged on March 31, 2026", snippet="exchanged on March 31, 2026")
    _refused(H.run_ttm("VNOM", judgment=vj(share_classes=d)), "BAD_SHARE_CLASSES", "existed for part of this period",
             stream="stderr")
    twr.update(value=3373192, count_basis="weighted_average", snippet="weighted average 3,373,192 units")
    for k in ("zero_event", "event_date"):
        twr.pop(k)
    t = H.run_ttm("VNOM", judgment=vj(share_classes=d))
    assert t["exit"] == 0 and t["ttm"]["ttm_shares_diluted"] == 187553000 + 164789844 + 3373192, t["stderr"][-800:]


def _calc_entry(value, event="ended", date="2023-07-02", counts=((20e6, "2022-12-31"), (20e6, "2023-07-01"))):
    return ent("2023-12-31", value, kind="calc", count_basis="weighted_average",
               source=f"test filing: the class ended on {date} (8-K {ACC})",
               snippet=f"collapse completed {date}",
               calc={"method": "day_weighted", "event": event, "event_date": date, "event_accession": ACC,
                     "counts": [{"value": v, "as_of": d, "accession": ACC, "snippet": f"{v:,.0f} units at {d}"}
                                for v, d in counts]})


def test_a_straddle_year_may_declare_a_day_weighted_calc():
    """A-21 (08b decision 8, the main agent 2026-10-20): a straddle year with no printed weighted-average unit count
    declares kind calc — a day-weighted average of two dated, cited counts over the class's existence in the period
    (20M units from 2023-01-01 to the 2023-07-02 collapse: 182 of 365 days = 9,972,603) — re-derived by the engine to
    one unit and recorded; off by more than one unit, or on a period the event does not straddle, it refuses."""
    exp = 20e6 * 182 / 365
    v = round(exp)
    out = s_run(syn(), {"share_classes": _straddle_decl(fy2023=_calc_entry(v), ended="2023-07-02")})
    n = _ok(out)
    assert float(rowmap(out)["2023-12-31"]["shares_diluted"]) == 100e6 + v
    ce = n["share_classes"]["calc_entries"]
    assert len(ce) == 1 and abs(ce[0]["rederived"] - exp) < 1e-6 and ce[0]["value"] == v, ce
    _refused(s_run(syn(), {"share_classes": _straddle_decl(fy2023=_calc_entry(v + 2), ended="2023-07-02")}),
             "BAD_SHARE_CLASSES", "does not reproduce the day-weighted average")
    full = sdecl(None, entries=[ent("2022-12-31", 20e6), _calc_entry(v, date="2024-02-01",
                                                                      counts=((20e6, "2022-12-31"), (20e6, "2023-12-31"))),
                                ent("2024-12-31", 20e6), ent("2025-12-31", 20e6)])
    _refused(s_run(syn(), {"share_classes": full}), "BAD_SHARE_CLASSES", "does not fall inside 2023-01-01..2023-12-31")
    norm, errs = SC().validate(sdecl(None, entries=[dict(_calc_entry(v), count_basis="period_end"), ent("2024-12-31", 1),
                                                    ent("2025-12-31", 1)]))
    assert norm is None and any("count_basis must be weighted_average" in e for e in errs), errs


# ===========================================================================
# T-6 — the §5.3 table
# ===========================================================================
def test_ttm_json_share_basis_must_match_the_declaration():
    """T-6 (08 §5.3; share_classes.ttm_on_declaration, the one rule the engine, make_score R-6 and R7 share): a --ttm
    pin is refused BAD_TTM_SHARE_BASIS (exit 3) when ttm.json carries no block while judgment.json declares, carries
    another declaration's sha, or carries a block while nothing is declared; a via-TTM --base-oe-ps equal to a
    filed-basis ttm.json at a declaring filer is refused the same way. The table itself, row by row."""
    tt, _ = v_declared()
    _refused(v_run(["--ttm"], ttm=v_undeclared_ttm()), "BAD_TTM_SHARE_BASIS", "built before the share_classes declaration")
    edited = vdecl()
    edited["classes"][0]["periods"][0]["snippet"] += " (edited)"
    _refused(v_run(["--ttm"], j=vj(share_classes=edited), ttm=tt), "BAD_TTM_SHARE_BASIS", "another share_classes declaration")
    _refused(v_run(["--ttm"], j=vj(drop=("share_classes",)), ttm=tt), "BAD_TTM_SHARE_BASIS",
             "on total units but judgment.json declares no share_classes")
    _refused(v_run(["--base-oe-ps", repr(7.933757391244075)], ttm=v_undeclared_ttm()), "BAD_TTM_SHARE_BASIS",
             "--base-oe-ps pin is ttm.json's TTM figure")
    T = SC().ttm_on_declaration
    d = vdecl()
    assert T({"ttm_oe_per_share": 1.0}, None) == (True, None)
    assert T(tt, d) == (True, None)
    assert T({"ttm_oe_per_share": 1.0}, d)[0] is False and T(tt, None)[0] is False and T(tt, edited)[0] is False
    assert T(None, None) == (True, None) and T(None, d)[0] is False


# ===========================================================================
# T-7 / T-8 — the counterfactual, IPR&D, the share-scale guard
# ===========================================================================
def _iprd_facts(expense, ytd=None):
    from test_engine_iprd import EXPENSE, _ytd
    f = syn()
    for y, v in expense.items():
        _syn_put(f, EXPENSE, "USD", _ctx(f"{y}-01-01", f"{y}-12-31", v, filed=f"{y + 1}-02-20"))
    if ytd:
        _ytd(f, EXPENSE, "2026-01-01", "2026-06-30", ytd, "2026-08-05")
    return f


def _with_checks(facts, j):
    from test_engine_iprd import with_checks
    return with_checks(facts, j)


DECL25 = sdecl(None, entries=[ent(p, 25e6) for p in LAST3] + [ent("2026-06-30", 25e6)])


def _declared_ttm(decl, per_unit, total, filed):
    """ttm.json as ttm.py writes it on `decl` (synthetic: the SYN filer has no 10-Q OCF legs)."""
    from test_engine_iprd import _ttm_doc
    t = _ttm_doc(per_unit, total)
    k = filed / total
    t.update(ttm_shares_diluted_filed=filed, ttm_oe_per_share_filed_basis=per_unit / k,
             share_classes={"declaration_sha256": sha256_of(decl), "basis": decl["basis"],
                            "leg": "ytd_10q", "period_end": "2026-06-30", "period_start": "2026-01-01",
                            "units_equivalent": total - filed, "filed_traded": filed, "total_units": total,
                            "units_split_basis": "no_split", "diluted_minus_basic": 0.0, "rescale_factor": k})
    return t


def test_counterfactual_switch_restores_the_filed_basis():
    """T-7 (08 §4.6, rebase A-3 / A-5): DCF_NO_SHARE_CLASSES=1 with --measure loads no declaration and reads a
    declared ttm.json through its filed-basis view: --ttm pins ttm_oe_per_share_filed_basis, the IPR&D window keeps
    the current-YTD leg and the denominator is ttm_shares_diluted_filed (also for a --base-oe-ps pin equal to the
    filed TTM); without --measure the switch is ignored; a declared ttm.json missing its filed field refuses
    BAD_TTM_SHARE_BASIS (not BAD_TTM_SHARES); a deferred payment the engine refuses is recorded, not exited, in that
    replay only; DCF_NO_OVERRIDES keeps the declaration on."""
    f = _iprd_facts({2025: 20e6}, ytd=30e6)
    j = _with_checks(f, {"share_classes": DECL25})
    tt = _declared_ttm(DECL25, 2.1, 125e6, 100e6)
    fin = _ok(s_run(f, j, ["--ttm"], ttm=tt))
    ip = fin["iprd_adjustment"]
    assert fin["base_oe_per_share"] == 2.1 and ip["shares_denominator"] == 125e6 and ip["shares_basis"] == "total_units"
    assert ip["window"]["ttm_current_ytd"] == ["2026-01-01", "2026-06-30"] and abs(ip["charge_per_share"] - 50e6 / 125e6) < 1e-12
    off = {"DCF_NO_SHARE_CLASSES": "1"}
    cf = _ok(s_run(f, j, ["--ttm"], ttm=tt, env=off, measure=True))
    assert abs(cf["base_oe_per_share"] - 2.625) < 1e-12 and cf["shares_diluted_latest"] == 100e6, cf["base_oe_per_share"]
    ipc = cf["iprd_adjustment"]
    assert ipc["shares_denominator"] == 100e6 and ipc["window"]["ttm_current_ytd"] == ["2026-01-01", "2026-06-30"]
    assert "shares_basis" not in ipc and cf["share_classes"]["counterfactual"] is True and cf["share_classes"]["declared"] is False
    cf2 = _ok(s_run(f, j, ["--base-oe-ps", repr(2.625)], ttm=tt, env=off, measure=True))
    assert cf2["iprd_adjustment"]["shares_denominator"] == 100e6 and cf2["iprd_adjustment"]["window"]["ttm_current_ytd"]
    ign = _ok(s_run(f, j, ["--ttm"], ttm=tt, env=off))
    assert ign["base_oe_per_share"] == 2.1 and ign["share_classes"]["declared"] is True
    broken = {k: v for k, v in tt.items() if k != "ttm_shares_diluted_filed"}
    _refused(s_run(f, j, ["--ttm"], ttm=broken, env=off, measure=True), "BAD_TTM_SHARE_BASIS", "filed-basis field is missing")
    no_ov = _ok(s_run(f, j, ["--ttm"], ttm=tt, env={"DCF_NO_OVERRIDES": "1"}, measure=True))
    assert no_ov["share_classes"]["declared"] is True and no_ov["shares_diluted_latest"] == 125e6
    # a deferred payment the engine refuses: exit 3 on a run, recorded in the share-class replay
    from test_engine_iprd import deferred
    f2 = _iprd_facts({2023: 15e6, 2025: 20e6})
    j2 = _with_checks(f2, {"share_classes": sdecl(25e6),
                           "iprd_deferred_payment": [deferred(period="2023-12-31", amount=15e6, first="2025-12-31")]})
    _refused(s_run(f2, j2), "BAD_IPRD_DEFERRED_PAYMENT", "must precede")
    rp = _ok(s_run(f2, j2, env=off, measure=True))
    assert rp["iprd_adjustment"]["deferred_payments_refused"], rp["iprd_adjustment"]


def test_iprd_charge_per_share_is_per_total_unit():
    """T-8 (08 §4.5 / §4.6, rebase A-4 / A-9 / 08b decision 9): on a declared median run the acquired-IPR&D charge
    per share divides by total units (20M / 125M) and records shares_basis total_units (shares_source keeps its
    pre-5.7 text); the filed-basis replay recomputes it on the filed count. The amortized replay: an iprd_amortized
    pin on native base ttm_json declared on total units scores amortized_in_base; make_score's replay pin (pin × TTM
    total ÷ TTM filed) with DCF_SC_PIN_SCALE is still recognised (amortized_in_base, the YTD window, native base =
    the filed-basis TTM, counterfactual_replay recorded) — without the scale it would deduct the charge again
    (one_time). A share-scale defect (the latest count filed in thousands) beside a declaration refuses; the same
    count fixed by a traded-class shares_override scores."""
    f = _iprd_facts({2025: 20e6})
    j = _with_checks(f, {"share_classes": sdecl(25e6)})
    n = _ok(s_run(f, j))
    ip = n["iprd_adjustment"]
    assert ip["shares_denominator"] == 125e6 and abs(ip["charge_per_share"] - 20e6 / 125e6) < 1e-12, ip
    assert ip["shares_basis"] == "total_units" and ip["shares_source"] == "diluted_latest"
    cf = _ok(s_run(f, j, env={"DCF_NO_SHARE_CLASSES": "1"}, measure=True))
    assert abs(cf["iprd_adjustment"]["charge_per_share"] - 0.2) < 1e-12 and "shares_basis" not in cf["iprd_adjustment"]
    # the amortized replay (native ttm_json): per unit 2.0 on 125M units, 2.5 per filed share on 100M
    f = _iprd_facts({2023: 15e6, 2025: 20e6})
    tt = _declared_ttm(DECL25, 2.0, 125e6, 100e6)
    d = {"basis": "iprd_amortized", "kind": "filing", "native_base": "ttm_json", "figures": [15e6, 0.0, 20e6],
         "shares": 125e6, "value": 2.0 - 35e6 / 3 / 125e6, "source": "test: this run's figures on total units",
         "reason": "test: acquisition-led R&D recurs"}
    j = _with_checks(f, {"share_classes": DECL25, "base_override": d})
    fin = _ok(s_run(f, j, ["--base-oe-ps", repr(d["value"])], ttm=tt))
    assert fin["iprd_adjustment"]["treatment"] == "amortized_in_base", fin["iprd_adjustment"]["treatment"]
    pin, scale = d["value"] * 125e6 / 100e6, 125e6 / 100e6
    rp = _ok(s_run(f, j, ["--base-oe-ps", repr(pin)], ttm=tt, measure=True,
                   env={"DCF_NO_SHARE_CLASSES": "1", "DCF_SC_PIN_SCALE": repr(scale)}))
    ip = rp["iprd_adjustment"]
    assert ip["treatment"] == "amortized_in_base" and E.iprd_charge_per_share(rp) == 0.0, ip["treatment"]
    assert ip["window"]["ttm_current_ytd"] == ["2026-01-01", "2026-06-30"] and ip["amortized"]["native_base_per_share"] == 2.5
    assert ip["amortized"]["counterfactual_replay"].startswith("share-class counterfactual")
    assert ip["amortized"]["counterfactual_not_revalidated"], ip["amortized"]
    noscale = _ok(s_run(f, j, ["--base-oe-ps", repr(pin)], ttm=tt, measure=True, env={"DCF_NO_SHARE_CLASSES": "1"}))
    assert noscale["iprd_adjustment"]["treatment"] == E.IPRD_TREATMENT_ONE_TIME, noscale["iprd_adjustment"]["treatment"]
    _refused(s_run(f, j, ["--base-oe-ps", repr(pin)], ttm=tt, measure=True,
                   env={"DCF_NO_SHARE_CLASSES": "1", "DCF_SC_PIN_SCALE": "-1"}), "BAD_SHARE_CLASSES", "DCF_SC_PIN_SCALE")
    # the share-scale guard: FY2025's only count is a basic count filed in thousands
    bad = syn(shares={2025: None}, basic={2025: 100e3})
    _refused(s_run(bad, {"share_classes": sdecl(25e6)}), "BAD_SHARE_CLASSES", "mis-scaled",
             "fix the traded count first")
    from test_engine_55 import _o
    n = _ok(s_run(bad, {"share_classes": sdecl(25e6), "shares_override": _o(100e6, share_basis="traded_class")}))
    assert n["shares_diluted_latest"] == 125e6 and n["share_scale"]["defect"] is False


def test_declared_pin_replay_keeps_its_basis_window():
    """T-8b (rebase A-4): a plain total-unit pin ($2.00/unit, built from ttm.json's TTM figures on another
    denominator) declaring basis_window "ttm" and share_basis "total_units" reads the current-YTD IPR&D leg; make_score's
    share-class replay pins it at × total ÷ filed of its share period (2.50 per filed share) with DCF_SC_PIN_SCALE 1.25,
    and the engine still recognises the declaration (the YTD window kept, inputs.base_basis_window recorded) — without
    the scale the window falls back to the FY window."""
    from test_engine_iprd import ttm_window_decl
    f = _iprd_facts({2025: 20e6}, ytd=30e6)
    tt = _declared_ttm(DECL25, 2.1, 125e6, 100e6)
    bo = dict(ttm_window_decl(2.0), share_basis="total_units")
    j = _with_checks(f, {"share_classes": DECL25, "base_override": bo})
    fin = _ok(s_run(f, j, ["--base-oe-ps", "2.0"], ttm=tt))
    assert fin["iprd_adjustment"]["window"]["ttm_current_ytd"] == ["2026-01-01", "2026-06-30"], fin["iprd_adjustment"]["window"]
    off = {"DCF_NO_SHARE_CLASSES": "1", "DCF_SC_PIN_SCALE": repr(1.25)}
    rp = _ok(s_run(f, j, ["--base-oe-ps", repr(2.5)], ttm=tt, env=off, measure=True))
    assert rp["iprd_adjustment"]["window"]["ttm_current_ytd"] == ["2026-01-01", "2026-06-30"]
    assert rp["inputs"]["base_basis_window"]["window"] == "ttm", rp["inputs"]
    ns = _ok(s_run(f, j, ["--base-oe-ps", repr(2.5)], ttm=tt, env={"DCF_NO_SHARE_CLASSES": "1"}, measure=True))
    assert ns["iprd_adjustment"]["window"]["ttm_current_ytd"] is None and "base_basis_window" not in ns["inputs"]


def test_ttm_basis_pins_need_ttm_json_on_the_declaration():
    """T-8c (08 §5.3: "the same table runs for an IPR&D ttm_json basis"; review 2026-10-21 finding 2): an
    iprd_amortized pin on native base ttm_json and a plain pin declaring basis_window "ttm" read ttm.json as their TTM
    basis (its figure, current-YTD leg and share count), so at a declaring filer a ttm.json not on the declaration —
    the filed-basis file left from before it (ttm.py refuses to rewrite it until the YTD is declared) — refuses
    BAD_TTM_SHARE_BASIS exactly as --ttm does (the amortized pin had shipped 2.5 per filed share beside 125M total
    units); on the declared ttm.json both score (T-8 / T-8b); without a declaration the same pins on the block-less
    ttm.json score as before."""
    from test_engine_iprd import _ttm_doc, ttm_window_decl
    f = _iprd_facts({2023: 15e6, 2025: 20e6})
    stale = _ttm_doc(2.5, 100e6)
    d = {"basis": "iprd_amortized", "kind": "filing", "native_base": "ttm_json", "figures": [15e6, 0.0, 20e6],
         "shares": 100e6, "value": 2.5 - 35e6 / 3 / 100e6, "source": "test: this run's figures on the filed count",
         "reason": "test: acquisition-led R&D recurs"}
    _refused(s_run(f, _with_checks(f, {"share_classes": DECL25, "base_override": d}), ["--base-oe-ps", repr(d["value"])],
                   ttm=stale),
             "BAD_TTM_SHARE_BASIS", "native base is ttm.json's TTM", "built before the share_classes declaration")
    und = _ok(s_run(f, _with_checks(f, {"base_override": d}), ["--base-oe-ps", repr(d["value"])], ttm=stale))
    assert und["iprd_adjustment"]["treatment"] == "amortized_in_base", und["iprd_adjustment"]["treatment"]
    f2 = _iprd_facts({2025: 20e6}, ytd=30e6)
    bo = dict(ttm_window_decl(2.0), share_basis="total_units")
    _refused(s_run(f2, _with_checks(f2, {"share_classes": DECL25, "base_override": bo}), ["--base-oe-ps", "2.0"],
                   ttm=_ttm_doc(2.5, 100e6)),
             "BAD_TTM_SHARE_BASIS", "basis_window \"ttm\"", "built before the share_classes declaration")
    other = dict(DECL25, reason=DECL25["reason"] + " (another declaration)")
    _refused(s_run(f2, _with_checks(f2, {"share_classes": other, "base_override": bo}), ["--base-oe-ps", "2.0"],
                   ttm=_declared_ttm(DECL25, 2.1, 125e6, 100e6)),
             "BAD_TTM_SHARE_BASIS", "another share_classes declaration")
    plain = {k: v for k, v in ttm_window_decl(2.0).items()}
    n = _ok(s_run(f2, _with_checks(f2, {"base_override": plain}), ["--base-oe-ps", "2.0"], ttm=_ttm_doc(2.5, 100e6)))
    assert n["iprd_adjustment"]["window"]["ttm_current_ytd"] == ["2026-01-01", "2026-06-30"], n["iprd_adjustment"]["window"]


# ===========================================================================
# T-9 — the detector
# ===========================================================================
def _cf(years=(2023, 2024, 2025), nci=None, cons=None, parent=None, eq_total=None, eq_parent=None, minority=None,
        diluted=100e6, basic=100e6, nci_unit="USD"):
    f = {"facts": {"us-gaap": {}}}

    def put(tag, unit, e):
        f["facts"]["us-gaap"].setdefault(tag, {"units": {}})["units"].setdefault(unit, []).append(e)
    for i, y in enumerate(years):
        dur = {"start": f"{y}-01-01", "end": f"{y}-12-31", "form": "10-K", "fp": "FY", "filed": f"{y + 1}-02-20",
               "accn": f"0000999002-{(y + 1) % 100:02d}-000001"}
        for tag, unit, vals in (("NetIncomeLossAttributableToNoncontrollingInterest", nci_unit, nci),
                                ("ProfitLoss", "USD", cons), ("NetIncomeLoss", "USD", parent),
                                (DIL, "shares", [diluted] * len(years) if diluted else None),
                                (BASIC, "shares", [basic] * len(years) if basic else None)):
            if vals is not None:
                put(tag, unit, dict(dur, val=vals[i]))
    last = f"{years[-1]}-12-31"
    inst = {"end": last, "form": "10-K", "fp": "FY", "filed": f"{years[-1] + 1}-02-20"}
    for tag, v in (("StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest", eq_total),
                   ("StockholdersEquity", eq_parent), ("MinorityInterest", minority)):
        if v is not None:
            put(tag, "USD", dict(inst, val=v))
    return f


W = ["2023-12-31", "2024-12-31", "2025-12-31"]


def _sig(f, dei=None, up=None, ucap=None, form="10-K", shares=100e6, ads=None):
    return SC().up_c_signals(f, W, "2025-12-31", shares, dei, up, ucap, ads, form)


def test_up_c_signals_calibration_shapes():
    """T-9 (08 §6, revision 3 findings 1, 5, 10; rebase A-12): the shipped rule on the calibration shapes — VNOM fires
    (equity 57.1%, net income 52.2%, cover page by class); RKT fires (equity share clamped to 0, net income 0.91);
    TKO / TPG / QSR stay silent (their diluted counts carry the exchange); DVA (an undimensioned cover page 0.84x the
    diluted count) and a 20-F stay silent; s 0.199 silent, 0.200 fires; the ProfitLoss - NetIncomeLoss and total -
    parent equity fallbacks; negative parent equity gives no equity share; AES (s 1.00, cover page 0.999x, universe
    cap 0.999x of universe.csv's own price × count) stays silent; no universe price -> that leg null, the others
    decide; malformed facts (a string or bool value, a fact without units, an empty unit list, an NCI line only in
    EUR) never raise."""
    vn = _cf(nci=[301e6, 245e6, -138e6], cons=[501e6, 604e6, -206e6], eq_total=10363e6, eq_parent=4448e6, minority=5915e6,
             diluted=142.53e6, basic=142.53e6)
    r = _sig(vn, up=42.99, ucap=15441788450, shares=142.53e6)
    assert r["suspect"] and abs(r["s"] - 0.5708) < 1e-4 and abs(r["nci_share_of_net_income_3fy"] - 0.5217) < 1e-4, r
    assert r["cover_by_class"] and abs(r["universe_cap_to_filed_cap"] - 2.5201) < 1e-4 and r["nci_years"][2][1] == -138e6
    rkt = _cf(nci=[910e6] * 3, cons=[1000e6] * 3, eq_total=1000e6, eq_parent=1050e6, minority=-50e6)
    r = _sig(rkt)
    assert r["suspect"] and r["nci_share_of_equity"] == 0.0 and abs(r["s"] - 0.91) < 1e-9, r
    for d2b, s_ni in ((2.401, 0.84), (2.694, 0.713), (1.389, 0.296)):          # TKO, TPG, QSR
        r = _sig(_cf(nci=[s_ni * 1e9] * 3, cons=[1e9] * 3, diluted=d2b * 100e6, basic=100e6), shares=d2b * 100e6)
        assert r["units_in_diluted"] and not r["suspect"], (d2b, r)
    dva = _cf(nci=[0.25e9] * 3, cons=[1e9] * 3)
    assert not _sig(dva, dei=84e6, up=10.0, ucap=0.9e9)["suspect"]
    assert not _sig(vn, form="20-F", up=42.99, ucap=15441788450, shares=142.53e6)["suspect"]
    for m, fires in ((199e6, False), (200e6, True)):
        r = _sig(_cf(eq_total=1000e6, eq_parent=1000e6 - m, minority=m))
        assert r["suspect"] is fires and abs(r["s"] - m / 1000e6) < 1e-12, (m, r)
    fb = _sig(_cf(cons=[100e6] * 3, parent=[70e6] * 3))
    assert abs(fb["nci_share_of_net_income_3fy"] - 0.3) < 1e-12 and fb["suspect"], fb
    eqfb = _sig(_cf(eq_total=1000e6, eq_parent=600e6))
    assert abs(eqfb["nci_share_of_equity"] - 0.4) < 1e-12
    assert _sig(_cf(eq_total=1000e6, eq_parent=-10e6, minority=500e6))["nci_share_of_equity"] is None
    aes = _cf(nci=[1e9] * 3, cons=[1e9] * 3)
    for run_price_factor in (0.9, 1.0, 1.1):     # the run price is no input: universe.csv's own price and cap only
        r = _sig(aes, dei=99.9e6, up=50.0, ucap=50.0 * 100e6 * 0.999)
        assert not r["suspect"] and abs(r["universe_cap_to_filed_cap"] - 0.999) < 1e-12, r
    r = _sig(vn, up=None, ucap=15441788450, shares=142.53e6)
    assert r["universe_cap_to_filed_cap"] is None and r["suspect"] and r["cover_by_class"]
    junk = _cf(nci=["301", True, None], cons=[501e6, 604e6, -206e6], nci_unit="EUR")
    junk["facts"]["us-gaap"]["MinorityInterest"] = {}
    junk["facts"]["us-gaap"]["ProfitLoss"]["units"]["USD"].append({"start": "2025-01-01", "end": "2025-12-31", "val": "x"})
    junk["facts"]["us-gaap"]["NetIncomeLoss"] = {"units": {"USD": []}}
    r = _sig(junk)
    assert isinstance(r, dict) and r["suspect"] is False, r


def test_engine_never_breaks_on_the_detector():
    """T-9, engine side (08 §6.4, A-12): an exception inside up_c_signals is recorded (up_c_check.error, suspect
    false) and adds no flag; a 20-F filer without an applied ADS ratio (the share-scale block nulls its universe cap)
    still records universe.csv's cap ratio; the synthetic filer with an NCI line computes its record."""
    fake = types.SimpleNamespace(**{k: getattr(SC(), k) for k in dir(SC()) if not k.startswith("__")})

    def boom(*a, **k):
        raise ValueError("synthetic detector failure")
    fake.up_c_signals = boom
    out = s_run(syn(), {})
    n0 = _ok(out)
    assert "error" not in n0["up_c_check"] and n0["up_c_check"]["suspect"] is False, n0["up_c_check"]
    fx = _syn_fixture(syn())
    base = H.make_base(fx, {}, None, copy_repo_files=False)
    n = _ok(H.run_engine("SYN", args=args_for(5), base=base, fixture=fx, patch=lambda M: setattr(M, "_sc", fake)))
    assert "synthetic detector failure" in n["up_c_check"]["error"] and n["up_c_check"]["suspect"] is False
    assert not flags(n, "UP_C_SUSPECT")
    tlk = H.repo_judgment("TLK", drop=("ads_ratio",))
    fx = H.load_fixture("TLK")
    base = H.make_base(fx, tlk, None, copy_repo_files=False)
    n = H.run_engine("TLK", args=args_for(6), base=base, fixture=fx)["numbers"]
    assert n["up_c_check"]["universe_cap_to_filed_cap"] is not None and n["up_c_check"]["domestic"] is False, n["up_c_check"]


# ===========================================================================
# T-10 / T-10b — divergence and the cap
# ===========================================================================
def test_divergence_and_cap_use_the_traded_count_then_add_units():
    """T-10 (08 §4.5, A-1): a cover-page count equal to the traded class after the FY end raises no divergence and the
    cap is price × (traded + units) on diluted_latest+share_classes; a cover page that sums every class (outside the
    band of the traded count, inside the total's) is recorded compared_to total_units, applied false, no switch."""
    n = _ok(s_run(syn(), {"share_classes": sdecl(25e6)}))
    assert n["share_basis"]["divergence"] is None and n["market_cap_est"] == 30.0 * 125e6
    mb = n["market_cap_basis"]
    assert mb["shares_source"] == "diluted_latest+share_classes" and mb["traded_shares"] == 100e6 and mb["declared_units"] == 25e6
    assert mb["formula"].startswith("price × (traded-class shares + declared")
    n = _ok(s_run(syn(dei=(150e6, "2026-01-31", "2026-02-20")), {"share_classes": sdecl(50e6)}))
    dv = n["share_basis"]["divergence"]
    assert dv["compared_to"] == "total_units" and dv["applied"] is False and dv["note"] == "cover page counts every class"
    assert n["market_cap_est"] == 30.0 * 150e6 and n["market_cap_basis"]["shares_source"] == "diluted_latest+share_classes"
    assert not flags(n, "SHARE_BASIS_DIVERGENCE")


def test_divergence_cap_takes_units_nearest_the_dei_date():
    """T-10b (08 §4.5): VNOM with a 200,000,000 Class A cover-page count dated 2026-08-01 (outside the band of the
    142.53M FY count): the cap counts dei + the units of the declared period nearest the dei date (2026-06-30:
    171,536,228, 32 days before), and the flag names the gap; with the YTD period undeclared, FY2025's 197,117,368
    (213 days)."""
    fx = copy.deepcopy(H.load_fixture("VNOM"))
    fx["facts"]["facts"].setdefault("dei", {})["EntityCommonStockSharesOutstanding"] = {"units": {"shares": [
        {"end": "2026-08-01", "val": 200000000, "fy": 2026, "fp": "Q2", "form": "10-Q", "filed": "2026-08-05",
         "accn": "0002074176-26-000053"}]}}
    n = _ok(v_run(no_ttm=True, fixture=fx))
    dv = n["share_basis"]["divergence"]
    assert dv["applied"] and dv["units_period"] == "2026-06-30" and dv["units_period_gap_days"] == 32, dv
    assert n["market_cap_basis"]["shares_used"] == 200000000 + 171536228 and n["market_cap_basis"]["shares_source"] == "dei_latest+share_classes"
    assert "32 days before the cover-page count" in scflag(n)[0]
    n = _ok(v_run(no_ttm=True, fixture=fx, j=vj(share_classes=drop_period(vdecl(), "2026-06-30"))))
    dv = n["share_basis"]["divergence"]
    assert dv["units_period"] == "2025-12-31" and dv["units_period_gap_days"] == 213 and dv["units_added"] == 197117368


# ===========================================================================
# T-11 — splits
# ===========================================================================
DD_10K, DD_10Q_PRE, DD_10Q_POST = "0001666700-26-000013", "0001666700-26-000031", "0001666700-26-000053"


def _dd_decl(accn, units_by_year, ytd=None, **kw):
    es = [ent(p, units_by_year[p[:4]], accession=accn, **kw) for p in LAST3]
    if ytd:
        es.append(ent("2026-06-30", ytd[0], accession=ytd[1]))
    return sdecl(None, entries=es)


def _dd_run(j, facts=None):
    fx = copy.deepcopy(H.load_fixture("DD"))
    if facts:
        facts(fx["facts"])
    base = H.make_base(fx, j, None, copy_repo_files=False)
    return H.run_engine("DD", args=args_for(5), base=base, fixture=fx)


def test_split_scales_units_by_their_own_filing():
    """T-11 (rule 11, 08 §4.5): DD's 1-for-3 split (effective 2026-06-30, confirmed by the post-event cover page) —
    units cited from its FY2025 10-K (filed before the event) are rescaled × 1/3 beside the rescaled rows
    (pre_split_rescaled); units from the post-split 10-Q's restated comparatives stay as filed (post_split); an
    accession outside DD's companyfacts needs split_basis (refused without it, rescaled with pre_split); an OVERRIDE
    row (post-split, never rescaled) takes pre-split-sourced units × 1/3."""
    pre = {"2023": 45e6, "2024": 42e6, "2025": 42e6}
    out = _dd_run({"share_classes": _dd_decl(DD_10K, pre)})
    n = _ok(out)
    for a in n["share_classes"]["applied"]:
        assert a["units_split_basis"] == "pre_split_rescaled" and abs(a["units_split_factor"] - 1 / 3) < 1e-12, a
        assert abs(a["units_equivalent"] - pre[a["period_end"][:4]] / 3) < 1e-6
    post = {"2023": 15e6, "2024": 14e6, "2025": 14e6}
    n = _ok(_dd_run({"share_classes": _dd_decl(DD_10Q_POST, post)}))
    assert all(a["units_split_basis"] == "post_split" and a["units_equivalent"] == post[a["period_end"][:4]]
               for a in n["share_classes"]["applied"])
    _refused(_dd_run({"share_classes": _dd_decl(ACC, pre)}), "BAD_SHARE_CLASSES", "not in the filer's companyfacts")
    n = _ok(_dd_run({"share_classes": _dd_decl(ACC, pre, split_basis="pre_split")}))
    assert all(a["units_split_basis"] == "pre_split_rescaled" for a in n["share_classes"]["applied"])

    def drop_fy2025(f):
        for t in (DIL, BASIC):
            es = f["facts"]["us-gaap"][t]["units"]["shares"]
            f["facts"]["us-gaap"][t]["units"]["shares"] = [e for e in es if e.get("end") != "2025-12-31"]
    from test_engine_55 import _o
    j = {"share_classes": _dd_decl(DD_10K, pre), "shares_override": _o(139733333, share_basis="traded_class")}
    out = _dd_run(j, facts=drop_fy2025)
    n = _ok(out)
    r = rowmap(out)["2025-12-31"]
    assert abs(float(r["shares_diluted"]) - (139733333 + 42e6 / 3)) < 1e-3 and r["shares_tag"] == "OVERRIDE+SHARE_CLASSES", r
    a = [x for x in n["share_classes"]["applied"] if x["period_end"] == "2025-12-31"][0]
    assert a["filed_traded"] == 139733333 and a["exchange_test"]["test"] == "skipped_override"


def _dd_ttm(j, drop_ytd=True, drop_fy=False, engine_split=None, drop_split=False):
    fx = copy.deepcopy(H.load_fixture("DD"))
    us = fx["facts"]["facts"]["us-gaap"]
    import ttm as _t
    for t in _t.SHARE_TAGS:
        if t in us:
            es = us[t]["units"]["shares"]
            # drop_fy: no FY2025 count and no 2025 YTD either (else ttm.py builds its share leg on FY2024's timeline)
            us[t]["units"]["shares"] = [e for e in es if not (drop_ytd and e.get("start") == "2026-01-01")
                                        and not (drop_fy and (e.get("end") == "2025-12-31"
                                                              or e.get("start") == "2025-01-01"))]
    base = H.make_base(fx, j, None, copy_repo_files=False)
    if engine_split is not None:
        n = {"ticker": "DD", "share_basis": {"split": engine_split}}
        n["content_hash"] = E._content_hash(n)
        with open(os.path.join(base, "DD", "dcf_numbers.json"), "w", encoding="utf-8") as f:
            json.dump(n, f)
    return H.run_ttm("DD", base=base, fixture=fx)


def test_ttm_split_basis_for_an_override_ytd_leg():
    """T-11, ttm.py (revision 3 finding 8): a current-YTD share leg filled by a traded-class shares_override
    (split_adjustment skipped: an override is post-split) beside YTD units from DD's pre-split Q1 10-Q — the split is
    confirmed for the units on their own (confirm_split on the FY diluted fact vs the cover page): units × 1/3,
    split_source confirmed_for_units; with no FY diluted fact the engine record's share_basis.split
    (engine_record); with neither and a post-FY split fact filed, refused."""
    from test_engine_55 import _o
    pre = {"2023": 45e6, "2024": 42e6, "2025": 42e6}
    j = {"share_classes": _dd_decl(DD_10K, pre, ytd=(42e6, DD_10Q_PRE)),
         "shares_override": _o(139733333, share_basis="traded_class")}
    t = _dd_ttm(j)
    assert t["exit"] == 0, t["stderr"][-1500:]
    sc = t["ttm"]["share_classes"]
    assert sc["split_source"] == "confirmed_for_units" and abs(sc["units_equivalent"] - 14e6) < 1e-6, sc
    assert sc["exchange_test"]["test"] == "skipped_override" and t["ttm"]["ttm_shares_diluted"] == 139733333 + 14e6
    split = {"event_date": "2026-06-30", "ratio_used": 1 / 3, "ratio_filed": 0.333}
    t = _dd_ttm(j, drop_fy=True, engine_split=split)
    assert t["exit"] == 0 and t["ttm"]["share_classes"]["split_source"] == "engine_record", t["stderr"][-1500:]
    _refused(_dd_ttm(j, drop_fy=True), "BAD_SHARE_CLASSES", "cannot be put on a split basis", stream="stderr")


# ===========================================================================
# T-12 / T-13
# ===========================================================================
def test_share_classes_and_share_class_mismatch_are_exclusive():
    """T-12: both declared -> BAD_SHARE_CLASSES (exit 3), no DATA_GAP route."""
    _refused(v_run(no_ttm=True, j=vj(share_class_mismatch={"value": True, "source": "test", "reason": "test"})),
             "BAD_SHARE_CLASSES", "exclusive")


def test_live_cap_uses_total_units_for_declared_share_classes():
    """T-13 (a guard; rebase A-18): reprice.live_market_cap prices a declared record on market_cap_basis.shares_used
    (the total), ÷ the ADS ratio, × the split factor since scoring — never shares_diluted_latest's traded count."""
    import reprice
    n = {"shares_diluted_latest": 339647368, "market_cap_basis": {"shares_used": 339647368,
                                                                 "shares_source": "diluted_latest+share_classes"}}
    assert reprice.live_market_cap(n, 45.02) == 45.02 * 339647368
    n2 = dict(n, shares_diluted_latest=142530000, ads_ratio={"ratio": 2.0})
    assert reprice.live_market_cap(n2, 45.02, factor=2.0) == 45.02 * 339647368 / 2.0 * 2.0


# ===========================================================================
# T-14 / T-14b — double counts
# ===========================================================================
def test_all_class_override_beside_a_declaration_is_refused():
    """T-14 (rule 10, 08 §4.2 a / c): the latest FY filled by a shares_override beside declared units — no share_basis
    or all_classes refused; traded_class scores with units on top (no exchange test on an OVERRIDE row). A dei
    fallback row in a declared period needs ack_reason. ttm.py: a YTD leg filled by a shares_override without the
    traded-class attestation refuses; with it the units go on top (exchange_test skipped_override); ttm.py's
    load_overrides passes share_basis through."""
    from test_engine_55 import _o
    f = syn(shares={2025: None})
    d = sdecl(25e6)
    _refused(s_run(f, {"share_classes": d, "shares_override": _o(125e6)}), "BAD_SHARE_CLASSES",
             "shares_override fills FY2025", "traded-class count")
    _refused(s_run(f, {"share_classes": d, "shares_override": _o(125e6, share_basis="all_classes")}), "BAD_SHARE_CLASSES")
    out = s_run(f, {"share_classes": d, "shares_override": _o(100e6, share_basis="traded_class")})
    n = _ok(out)
    r = rowmap(out)["2025-12-31"]
    assert float(r["shares_diluted"]) == 125e6 and r["shares_tag"] == "OVERRIDE+SHARE_CLASSES"
    a = n["share_classes"]["applied"][-1]
    assert a["share_basis_attested"] == "traded_class" and a["exchange_test"] == {"test": "skipped_override"}
    # a dei fallback row (FY2022: no diluted / basic count; a cover page dated 2023-01-31)
    f = syn(shares={2022: None}, basic={2022: None}, extra_dei=((100e6, "2023-01-31", "2023-02-20"),))
    d = sdecl(None, entries=[ent(p, 25e6) for p in ("2022-12-31",) + LAST3])
    _refused(s_run(f, {"share_classes": d}), "BAD_SHARE_CLASSES", "FY2022's count is a fallback (FALLBACK:dei:")
    d["ack_reason"] = "test: the cover page counts 100,000,000 Class A shares only (the 10-K cover)"
    out = s_run(f, {"share_classes": d})
    _ok(out)
    assert rowmap(out)["2022-12-31"]["shares_tag"].startswith("FALLBACK:dei:") and float(rowmap(out)["2022-12-31"]["shares_diluted"]) == 125e6
    # ttm.py: VNOM's YTD share facts removed, the leg filled by a shares_override
    fx = copy.deepcopy(H.load_fixture("VNOM"))
    for t in (DIL, BASIC):
        es = fx["facts"]["facts"]["us-gaap"][t]["units"]["shares"]
        fx["facts"]["facts"]["us-gaap"][t]["units"]["shares"] = [e for e in es if e.get("start") != "2026-01-01"]

    def ttm_with(ov):
        base = H.make_base(fx, vj(shares_override=ov), None, copy_repo_files=False)
        return H.run_ttm("VNOM", base=base, fixture=fx)
    _refused(ttm_with(_o(187553000)), "BAD_SHARE_CLASSES", "shares_override fills the current-YTD share leg", stream="stderr")
    t = ttm_with(_o(187553000, share_basis="traded_class"))
    assert t["exit"] == 0, t["stderr"][-1500:]
    assert t["ttm"]["ttm_shares_diluted"] == 187553000 + 171536228 and t["ttm"]["share_classes"]["exchange_test"] == {"test": "skipped_override"}
    spec = importlib.util.spec_from_file_location("_ttm_l8_probe", os.path.join(SYS, "ttm.py"))
    T = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(T)
    b = H.make_base(fx, vj(shares_override=_o(187553000, share_basis="traded_class")), None, copy_repo_files=False)
    T.BASE = b
    assert T.load_overrides("VNOM")["shares"]["share_basis"] == "traded_class"
    shutil.rmtree(b, ignore_errors=True)


def test_fallback_row_cannot_carry_in_filed_count_units():
    """T-14c (rule 5b; review 2026-10-21 finding 6): in_filed_count units are verified by diluted − basic, and a
    cover-page / outstanding fallback row has no basic count to verify them — while ack_reason attests that count is
    the traded class only, the opposite of in_filed_count. T-14's dei fallback FY2022 with its units marked
    in_filed_count is refused, with ack_reason or without (it had scored, "skipped_fallback_ack", nothing added, the
    year's per-share figure on the traded class only); the same row without in_filed_count takes the units (T-14)."""
    f = syn(shares={2022: None}, basic={2022: None}, extra_dei=((100e6, "2023-01-31", "2023-02-20"),))
    d = sdecl(None, entries=[ent(p, 25e6) for p in ("2022-12-31",) + LAST3])
    d["classes"][0]["periods"][0]["in_filed_count"] = True
    for ack in (True, False):
        dd = copy.deepcopy(d)
        if ack:
            dd["ack_reason"] = "test: the cover page counts 100,000,000 Class A shares only (the 10-K cover)"
        _refused(s_run(f, {"share_classes": dd}), "BAD_SHARE_CLASSES", "FY2022", "fallback", "in_filed_count")
    ok = copy.deepcopy(d)
    ok["classes"][0]["periods"][0].pop("in_filed_count")
    ok["ack_reason"] = "test: the cover page counts 100,000,000 Class A shares only (the 10-K cover)"
    out = s_run(f, {"share_classes": ok})
    n = _ok(out)
    assert float(rowmap(out)["2022-12-31"]["shares_diluted"]) == 125e6 and n["share_classes"]["included_periods"] == []


def test_no_override_replay_leaves_fallback_rows_without_units():
    """T-14b (08 §8.3, revision 3 finding 11): FY2025's only count is the all-class CommonStockSharesOutstanding
    (125M) and FY2024's a basic count; a traded-class shares_override fills both on the final run. In the field-
    override replay (DCF_NO_OVERRIDES=1 --measure) FY2025 falls back to the outstanding count and gets NO units
    (checks_relaxed names it) while FY2024's basic fallback still takes them; the same environment without --measure
    refuses as a run would."""
    from test_engine_55 import _o
    f = syn(shares={2024: None, 2025: None}, basic={2025: None})
    _syn_put(f, "CommonStockSharesOutstanding", "shares", _ctx(None, "2025-12-31", 125e6, filed="2026-02-20"))
    j = {"share_classes": sdecl(25e6), "shares_override": _o(100e6, share_basis="traded_class")}
    fin = _ok(s_run(f, j))
    assert [a["filed_traded_tag"] for a in fin["share_classes"]["applied"]] == [DIL, "OVERRIDE", "OVERRIDE"]
    out = s_run(f, j, env={"DCF_NO_OVERRIDES": "1"}, measure=True)
    rp = _ok(out)
    cr = rp["share_classes"]["checks_relaxed"]
    assert cr["reason"] == "no_overrides_counterfactual" and [x["period_end"] for x in cr["periods_left_on_fallback"]] == ["2025-12-31"], cr
    assert cr["periods_left_on_fallback"][0]["tag"] == "FALLBACK:CommonStockSharesOutstanding"
    ap = {a["period_end"]: a for a in rp["share_classes"]["applied"]}
    assert ap["2024-12-31"]["filed_traded_tag"] == f"FALLBACK:{BASIC}" and "2025-12-31" not in ap
    assert rp["shares_diluted_latest"] == 125e6 and "field-override replay: FY2025 left on its fallback count" in scflag(rp)[0]
    _refused(s_run(f, j, env={"DCF_NO_OVERRIDES": "1"}), "BAD_SHARE_CLASSES", "FY2025's count is a fallback")


# ===========================================================================
# T-15 / T-16 / T-17
# ===========================================================================
def test_diluted_count_that_includes_the_exchange():
    """T-15 (rule 5b, 08 §4.2 b): FY2025's diluted count is 2.69x basic (if-converted: the units are in it) — declared
    units ~ the gap refuse ("already includes the exchange"); with diluted_gap_reason they apply; marked
    in_filed_count they are verified and nothing is added (included_periods); in_filed_count on a period whose
    diluted = basic refuses ("does not carry the exchange"), and on an OVERRIDE row; no basic count refuses unless
    diluted_gap_reason. ttm.py: a YTD leg 2.69x its basic count refuses; no YTD basic fact refuses unless
    diluted_gap_reason."""
    from test_engine_55 import _o
    f = syn(shares={2025: 269e6})
    d = sdecl({"2023-12-31": 25e6, "2024-12-31": 25e6, "2025-12-31": 169e6})
    _refused(s_run(f, {"share_classes": d}), "BAD_SHARE_CLASSES", "2025-12-31", "already includes the exchange")
    d2 = dict(d, diluted_gap_reason="test: diluted − basic 169,000,000 is RSUs per the EPS note; the units are antidilutive")
    assert float(rowmap(s_run(f, {"share_classes": d2}))["2025-12-31"]["shares_diluted"]) == 269e6 + 169e6
    d3 = copy.deepcopy(d)
    d3["classes"][0]["periods"][2]["in_filed_count"] = True
    out = s_run(f, {"share_classes": d3})
    n = _ok(out)
    r = rowmap(out)["2025-12-31"]
    assert float(r["shares_diluted"]) == 269e6 and not r["shares_tag"].endswith("+SHARE_CLASSES")
    ip = n["share_classes"]["included_periods"]
    assert len(ip) == 1 and ip[0]["included_units"] == 169e6 and ip[0]["exchange_test"]["test"] == "passed", ip
    assert [a["period_end"] for a in n["share_classes"]["applied"]] == ["2023-12-31", "2024-12-31"]
    d4 = copy.deepcopy(d)
    d4["classes"][0]["periods"][1]["in_filed_count"] = True
    _refused(s_run(f, {"share_classes": d4}), "BAD_SHARE_CLASSES", "does not carry the exchange")
    _refused(s_run(syn(shares={2025: None}), {"share_classes": d3, "shares_override": _o(100e6, share_basis="traded_class")}),
             "BAD_SHARE_CLASSES", "is a shares_override")
    nb = syn(basic={2024: None})
    _refused(s_run(nb, {"share_classes": sdecl(25e6)}), "BAD_SHARE_CLASSES", "no basic weighted count")
    _ok(s_run(nb, {"share_classes": sdecl(25e6, diluted_gap_reason="test: the 10-K files no basic count; 0 units are in the diluted count")}))
    # ttm.py on VNOM's YTD leg
    fx = copy.deepcopy(H.load_fixture("VNOM"))
    for e in fx["facts"]["facts"]["us-gaap"][DIL]["units"]["shares"]:
        if (e.get("start"), e.get("end")) == ("2026-01-01", "2026-06-30"):
            e["val"] = 187553000 * 2.69
    _refused(H.run_ttm("VNOM", base=H.make_base(fx, vj(), None, copy_repo_files=False), fixture=fx),
             "BAD_SHARE_CLASSES", "already includes the exchange", stream="stderr")
    fx = copy.deepcopy(H.load_fixture("VNOM"))
    es = fx["facts"]["facts"]["us-gaap"][BASIC]["units"]["shares"]
    fx["facts"]["facts"]["us-gaap"][BASIC]["units"]["shares"] = [e for e in es if e.get("start") != "2026-01-01"]
    _refused(H.run_ttm("VNOM", base=H.make_base(fx, vj(), None, copy_repo_files=False), fixture=fx),
             "BAD_SHARE_CLASSES", "no basic weighted count", stream="stderr")
    jr = vj()
    jr["share_classes"]["diluted_gap_reason"] = "test: the 10-Q's EPS note: diluted − basic 0; 171,536,228 units excluded"
    t = H.run_ttm("VNOM", base=H.make_base(fx, jr, None, copy_repo_files=False), fixture=fx)
    assert t["exit"] == 0 and t["ttm"]["share_classes"]["exchange_test"]["test"] == "not_possible_reason_given"


def test_multi_class_common_ratio_scales_the_units():
    """T-16 (rule 2): ONON's shape — one class of 1,000,000,000 voting shares at 1/10 of a traded share's economics
    (exchange_ratio 0.1) adds 100,000,000 units per period; a ratio of 10,000 is accepted, 10,001 refused; a ratio
    other than 1 without ratio_source refuses."""
    out = s_run(syn(), {"share_classes": sdecl(1e9, ratio=0.1, basis="multi_class_common")})
    n = _ok(out)
    assert all(a["units_equivalent"] == 1e8 and a["total_units"] == 2e8 for a in n["share_classes"]["applied"])
    assert n["share_classes"]["nci_check"]["agrees"] is None
    assert SC().validate(sdecl(1, ratio=10000))[1] == []
    assert any("exchange_ratio" in e for e in SC().validate(sdecl(1, ratio=10001))[1])
    d = sdecl(1e9, ratio=0.1)
    d["classes"][0].pop("ratio_source")
    _refused(s_run(syn(), {"share_classes": d}), "BAD_SHARE_CLASSES", "ratio_source is required")


def test_ads_filer_units_are_in_ordinary_shares():
    """T-17 (rule 2, 08 §4.5): TLK (ADS 100) and VOD (ADS 10) with a 10% multi_class_common declaration in ordinary
    shares (ratio 1): the cap is price × (filed + units) ÷ ads_ratio and every per-share figure is OE / (filed +
    units) × ads_ratio; the formula names ÷ ads_ratio. TLK's rows are traded-class shares_override rows."""
    for t, moat in (("TLK", 6), ("VOD", 4)):
        j = H.repo_judgment(t)
        fx = H.load_fixture(t)
        base0 = H.make_base(fx, j, None, copy_repo_files=False)
        plain = H.run_engine(t, args=args_for(moat), base=base0, fixture=fx)
        rows0 = rowmap(plain)
        last3 = sorted(rows0)[-3:]
        if t == "TLK":
            j["shares_override"] = dict(j["shares_override"], share_basis="traded_class")
        units = {p: round(float(rows0[p]["shares_diluted"]) * 0.1) for p in last3}
        j["share_classes"] = sdecl(units, periods=last3, basis="multi_class_common")
        base = H.make_base(fx, j, None, copy_repo_files=False)
        out = H.run_engine(t, args=args_for(moat), base=base, fixture=fx)
        n = _ok(out)
        ads = n["ads_ratio"]["ratio"]
        lp = last3[-1]
        tot = float(rows0[lp]["shares_diluted"]) + units[lp]
        assert abs(n["market_cap_est"] - n["price"] * tot / ads) < 1e-3 * n["market_cap_est"], (t, n["market_cap_est"])
        assert abs(n["base_oe_latest_per_share"] - float(rows0[lp]["oe_conservative"]) / tot * ads) < 1e-9, t
        assert n["market_cap_basis"]["formula"].endswith("÷ ads_ratio"), n["market_cap_basis"]


def test_interim_ads_bridge_rescales_every_per_share_field():
    """T-17b (08 §5.4, revision 3 finding 1): the declared 6-K bridge at an ADS filer (ratio 2) with a 10% declaration
    for the current interim (61,700,000 units on 617,000,000 ordinary shares, the share leg attested traded_class):
    every per-share field × 617 / 678.7 — the per-ADS pin, the per-ordinary figure and the override zero-fill —
    each original kept as *_filed_basis; the share leg without share_basis refuses; the instance's basic count runs
    the exchange test; an engine record that added units to the FY row: IB-SH1 compares the filed traded FY count."""
    import test_ttm_interim as TI
    d = TI.decl()
    d["legs"]["shares_diluted"]["current_interim"]["share_basis"] = "traded_class"
    sc = sdecl(None, entries=[ent("2026-06-30", 61700000)])
    ads = {"ratio": 2.0, "source": "test 20-F cover", "reason": "2 ordinary shares per ADS"}
    n = TI.engine_record(ads_ratio=ads)
    plain = TI._once(n=n, judgment={"ads_ratio": ads}, d=TI.decl())
    assert plain["exit"] == 0, plain["stderr"][-1500:]
    out = TI._once(n=n, judgment={"ads_ratio": ads, "share_classes": sc}, d=d)
    assert out["exit"] == 0, out["stderr"][-1500:]
    t, p = out["ttm"], plain["ttm"]
    k = 617e6 / 678.7e6
    assert t["ttm_shares_diluted"] == 678.7e6 and t["ttm_shares_diluted_filed"] == 617e6
    assert abs(t["ttm_oe_per_share"] - p["ttm_oe_per_share"] * k) < 1e-12 and t["ttm_oe_per_share_filed_basis"] == p["ttm_oe_per_share"]
    assert abs(t["ttm_oe_per_share"] - t["ttm_oe_total"] / 678.7e6 * 2.0) < 1e-12
    assert abs(t["ttm_oe_per_ordinary_share"] - p["ttm_oe_per_ordinary_share"] * k) < 1e-12
    assert t["share_classes"]["leg"] == "interim" and t["share_classes"]["exchange_test"]["test"] == "passed"
    out = TI._once(n=n, judgment={"ads_ratio": ads, "share_classes": sc}, d=TI.decl())
    assert out["exit"] == 3 and "share_basis \"traded_class\"" in out["stderr"], out["stderr"][-800:]
    # the override zero-fill (an FY SBC override) is rescaled too
    cols, rows = TI.csv_rows(sbc_tag="OVERRIDE")
    n2 = TI.engine_record(ads_ratio=ads, override_checks={"sbc": {"value": 35e6, "currency_basis": "converted"}})
    out = TI._once(n=n2, rows=(cols, rows), judgment={"ads_ratio": ads, "share_classes": sc}, d=d)
    assert out["exit"] == 0, out["stderr"][-1500:]
    cf = out["ttm"]["override_counterfactual"]
    assert abs(cf["base_oe_per_share_zero_fill"] - cf["base_oe_per_share_zero_fill_filed_basis"] * k) < 1e-12, cf
    # the engine record added units to the FY row: the bridge's FY count is the filed traded one
    cols, rows = TI.csv_rows(shares_diluted=615600000 + 61560000, shares_tag="AdjustedWeightedAverageShares+SHARE_CLASSES")
    n3 = TI.engine_record(ads_ratio=ads, share_classes={"declared": True, "applied": [
        {"period_end": "2025-12-31", "filed_traded": 615600000, "total_units": 677160000}]})
    out = TI._once(n=n3, rows=(cols, rows), judgment={"ads_ratio": ads, "share_classes": sc}, d=d)
    assert out["exit"] == 0, out["stderr"][-1500:]
    assert out["ttm"]["shares"]["fy_diluted"] == 615600000 and out["ttm"]["shares"]["fy_total_units"] == 677160000
    # a fy_diluted_count estimate (a 6-K without XBRL: no basic count either, so diluted_gap_reason) equal to the CSV
    # total would add the units twice ([IB-EST2]); equal to the filed traded FY count it scores
    scr = dict(sc, diluted_gap_reason="test: the 6-K prints no basic count; 0 units are in its diluted count")
    for val, good in ((677160000, False), (615600000, True)):
        de = TI._leg(d, "shares_diluted", "current_interim", kind="estimate", method="fy_diluted_count", value=val,
                     reason="test: the 6-K prints no diluted count for the interim")
        for k in ("snippet", "source"):
            de["legs"]["shares_diluted"]["current_interim"].pop(k, None)
        out = TI._once(n=n3, rows=(cols, rows), judgment={"ads_ratio": ads, "share_classes": scr}, d=de,
                       sub=TI.submissions(is_xbrl=0))
        assert (out["exit"] == 0) is good, (val, out["exit"], out["stderr"][-1500:])
        if not good:
            assert "[IB-EST2]" in out["stderr"] and "615600000" in out["stderr"].replace(",", ""), out["stderr"][-800:]
    # --interim-draft at a declaring filer drafts the share leg with share_basis traded_class
    out = TI._once(args=("--interim-draft", TI.ACC), judgment={"interim_bridge": None, "share_classes": sc})
    assert out["exit"] == 0, out["stderr"][-1000:]
    assert out["ttm"]["interim_bridge"]["legs"]["shares_diluted"]["current_interim"]["share_basis"] == "traded_class"


def test_bridge_period_passes_the_typo_guard_at_a_20f_filer():
    """T-17c (08 §4.3's typo guard beside §5.4's bridge; review 2026-10-21 finding 1): a 20-F filer's 6-K interim share
    count is not in companyfacts, so its current-interim period end is no filed share-fact period end. Declared
    beside an interim_bridge whose current interim ends there, the preliminary (median) run — the first step of the
    bridge workflow, before ttm.py --interim writes ttm.json — records it unused and scores (it had refused, so the
    bridge could never start at a declaring filer); without the bridge declaration, at a period the bridge does not
    end on, or at a 10-K filer it is still refused as a typo."""
    import test_make_score_57_interim as IB
    fx = IB.foreign_fixture()
    for y in IB.YEARS:
        IB._put(fx["facts"], IB.IF, "WeightedAverageShares", "shares",
                {"accn": f"0009990030-{(y + 1) % 100:02d}-000010", "fy": y, "fp": "FY", "form": "20-F",
                 "filed": f"{y + 1}-03-18", "start": f"{y}-01-01", "end": f"{y}-12-31", "val": 615600000})

    def run(ytd, bridge):
        sc = sdecl(None, entries=[ent(p, 61560000) for p in LAST3] + [ent(ytd, 61700000)], basis="multi_class_common")
        j = {"ads_ratio": dict(IB.ADS), "share_classes": sc}
        if bridge:
            j["interim_bridge"] = IB.decl()
        return H.run_engine(IB.FX_T, args=IB.ARGS, judgment=j, fixture=fx)
    _refused(run("2026-06-30", False), "BAD_SHARE_CLASSES", "declares 2026-06-30", "no period end")
    n = _ok(run("2026-06-30", True))
    assert n["share_classes"]["unused_periods"] == ["2026-06-30"], n["share_classes"]["unused_periods"]
    assert [a["period_end"] for a in n["share_classes"]["applied"]] == list(LAST3) and n["shares_diluted_latest"] == 677160000
    _refused(run("2026-03-31", True), "BAD_SHARE_CLASSES", "declares 2026-03-31")
    _refused(s_run(syn(), {"share_classes": DECL25, "interim_bridge": IB.decl()}), "BAD_SHARE_CLASSES", "declares 2026-06-30")


# ===========================================================================
# T-18 — the cap cross-check
# ===========================================================================
def test_cap_gap_cross_check():
    """T-18 (08 §4.8, revision 3 finding 5): universe.csv's cap equal to its price × the filed count (ratio 1.00) with
    a 40% declaration -> SHARE_CLASSES_CAP_GAP (cap_check.gap true); ratio 1.04 with a 5% uplift -> no gap (band
    edges); VNOM (2.5201) -> none; no universe cap or price -> gap null; the same cases at run prices 10% above and
    below the screener's give the same cap_ratio and gap (universe.csv's own price)."""
    for px in (27.0, 30.0, 33.0):
        n = _ok(s_run(syn(), {"share_classes": sdecl(40e6)}, price=px, universe={"price": "30", "market_cap": str(30 * 100e6)}))
        cc = n["share_classes"]["cap_check"]
        assert cc["gap"] is True and cc["cap_ratio"] == 1.0 and cc["declared_uplift"] == 0.4, (px, cc)
        assert flags(n, "SHARE_CLASSES_CAP_GAP")
        n = _ok(s_run(syn(), {"share_classes": sdecl(5e6)}, price=px, universe={"price": "30", "market_cap": str(30 * 104e6)}))
        cc = n["share_classes"]["cap_check"]
        assert cc["gap"] is False and cc["cap_ratio"] == 1.04 and not flags(n, "SHARE_CLASSES_CAP_GAP"), (px, cc)
    for uni in ({"price": "30", "market_cap": ""}, {"price": "", "market_cap": str(3e9)}):
        n = _ok(s_run(syn(), {"share_classes": sdecl(40e6)}, universe=uni))
        assert n["share_classes"]["cap_check"]["gap"] is None and not flags(n, "SHARE_CLASSES_CAP_GAP")
    _, out = v_declared()
    assert out["numbers"]["share_classes"]["cap_check"]["cap_ratio"] == 2.5201 and out["numbers"]["share_classes"]["cap_check"]["gap"] is False


# ===========================================================================
# A-6 — optional hashed ttm.json legs
# ===========================================================================
def test_share_class_keys_are_optional_ttm_input_legs():
    """A-6 (rebase I-3): ttm_input_legs hashes share_classes and the filed-basis twins when ttm.json carries them, so
    a declared ttm.json rewritten on another declaration (equal totals) changes ttm_input_hash; a ttm.json without
    them hashes as before — every committed ttm.json's legs equal the legs without the optional keys."""
    tt, _ = v_declared()
    legs = E.ttm_input_legs(tt)
    for k in ("share_classes", "ttm_shares_diluted_filed", "ttm_oe_per_share_filed_basis"):
        assert k in legs, k
    other = copy.deepcopy(tt)
    other["share_classes"]["declaration_sha256"] = "0" * 64
    assert E.ttm_inputs_record(other)["ttm_input_hash"] != E.ttm_inputs_record(tt)["ttm_input_hash"]
    saved = E.TTM_INPUT_OPTIONAL_FIELDS
    seen = 0
    for t in sorted(os.listdir(ROOT)):
        p = os.path.join(ROOT, t, "ttm.json")
        if not os.path.isfile(p):
            continue
        with open(p, encoding="utf-8") as f:
            doc = json.load(f)
        now = E.ttm_inputs_record(doc)
        try:
            E.TTM_INPUT_OPTIONAL_FIELDS = ()
            before = E.ttm_inputs_record(doc)
        finally:
            E.TTM_INPUT_OPTIONAL_FIELDS = saved
        assert now == before, t
        seen += 1
    assert seen > 50, seen


# ===========================================================================
# the module, unit by unit
# ===========================================================================
def test_validate_and_the_derived_figures():
    """share_classes.validate (rules 1-5b, 9): VNOM's declaration validates and sums to its units per period;
    dates_in reads ISO and written dates; each malformed shape is named; declaration_sha256 moves with any edit."""
    S = SC()
    norm, errs = S.validate(vdecl())
    assert errs == [] and S.units_by_period(norm) == {"2023-12-31": 90709946, "2024-12-31": 95525123,
                                                       "2025-12-31": 197117368, "2026-06-30": 171536228}
    assert S.dates_in("closed October 1, 2024; also 2025-06-30 and Sept. 30, 2025 and 2 January 2024") == {
        "2024-10-01", "2025-06-30", "2025-09-30", "2024-01-02"}
    cases = [({"basis": "other"}, "basis must be"), ({"reason": "no number here"}, "reason must carry a number"),
             ({"traded_class": ""}, "traded_class"), ({"classes": []}, "classes must list"),
             ({"ack_reason": "no digits"}, "ack_reason must carry a number")]
    for over, needle in cases:
        d = dict(vdecl(), **over)
        assert any(needle in e for e in S.validate(d)[1]), (over, S.validate(d)[1])
    d = vdecl()
    d["classes"][0]["periods"][0]["accession"] = "bad"
    assert any("accession" in e for e in S.validate(d)[1])
    d = vdecl()
    d["classes"][0]["periods"][0]["value"] = 1.5
    assert any("integer-valued" in e for e in S.validate(d)[1])
    d = vdecl()
    d["classes"][0]["periods"][0]["in_filed_count"] = "yes"
    assert any("in_filed_count" in e for e in S.validate(d)[1])
    assert S.validate("not an object")[0] is None
    e2 = vdecl()
    e2["classes"][0]["periods"][0]["source"] += "."
    assert S.declaration_sha256(e2) != S.declaration_sha256(vdecl())
    ok, rec = S.exchange_test(100e6, 100e6, 25e6, 0.0, {})
    assert ok is None and rec["test"] == "passed"
    why, rec = S.exchange_test(269e6, 100e6, 169e6, 0.0, {})
    assert "already includes the exchange" in why and rec["test"] == "exchange_in_count"


if __name__ == "__main__":
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn) and fn.__module__ == __name__:
            try:
                fn()
                print(f"PASS {name}")
            except AssertionError as e:
                fails += 1
                print(f"FAIL {name}: {str(e)[:2000]}")
            except Exception as e:
                fails += 1
                import traceback
                print(f"ERROR {name}: {type(e).__name__}: {e}\n{traceback.format_exc()[-2500:]}")
    sys.exit(1 if fails else 0)
