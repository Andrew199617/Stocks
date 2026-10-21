#!/usr/bin/env python3
"""Engine release 5.7 — capex components (R8) and capitalized software as capex (R9) (Andrew, 2026-10-19; assigned to
Claude; design 09_capex.md rev. 3 with the 09b decisions and the ba2bfc0 rebase map).
Run: python _system/tests/test_engine_57_capex.py (or python -m pytest _system/tests). No network.

R8 — KNX filed its whole capex line as PaymentsToAcquireMachineryAndEquipment, a tag on no engine list, beside a ~$1M
PaymentsToAcquireOtherProductiveAssets line that was: the component group read ~$1M. The component group now sums
every filed PP&E component (machinery and equipment, mining assets, furniture and fixtures — the last two
sub-classes, never the whole leg on their own), and CAPEX_UNLISTED_COMPONENT stops the next KNX.
R9 — capitalized software / development (PaymentsToDevelopSoftware, PaymentsToAcquireSoftware, PaymentsForSoftware,
ifrs-full PaymentsForDevelopmentProjectExpenditure) joins the additive intangible capex leg, with double-count
guards (parts_of_total on the intangible leg, ppe_duplicate, in_ppe_total) and per-year provenance; the 5.6 IPR&D
overlap guard compares only the purchased-intangible part; ttm.json carries the engine release that built it.

Every case runs offline: direct calls of the pure helpers (capex_for_period, unlisted_capex_components, _v55_flags,
ttm.py's capex_assembly / add_intangibles / superseded_capex_legs), and dcf_engine.main() / ttm.main() through
engine55_harness on the KNX / JKHY fixtures (fixtures/engine55, built by build_fixtures.py from their companyfacts),
HALO and VOD (the IPR&D guard). Each test fails on the code before this lane (e22e814) unless labelled a pin; the IPR&D
guard tests (T6 family) fail there through their capex assertions, and their guard halves are proven against
mutants that revert one subtraction line each (the lane's failing-first log records both).
"""
import copy
import importlib.util
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
ROOT = os.path.dirname(SYS)
for _p in (HERE, SYS):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import engine55_harness as H  # noqa: E402

E = H._engine()   # a private dcf_engine copy (neutral argv) for the unit tests

IF = "ifrs-full"
PRIMARY = "PaymentsToAcquirePropertyPlantAndEquipment"
OTHER_PPE = "PaymentsToAcquireOtherPropertyPlantAndEquipment"
PRODUCTIVE = "PaymentsToAcquireProductiveAssets"
OTHER_PRODUCTIVE = "PaymentsToAcquireOtherProductiveAssets"
CAP_IMPROVEMENTS = "PaymentsForCapitalImprovements"
ME = "PaymentsToAcquireMachineryAndEquipment"
MINING = "PaymentsToAcquireMiningAssets"
FF = "PaymentsToAcquireFurnitureAndFixtures"
INTANG = "PaymentsToAcquireIntangibleAssets"
OTHER_INTANG = "PaymentsToAcquireOtherIntangibleAssets"
IFRS_PPE = "PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities"
IFRS_INTANG = "PurchaseOfIntangibleAssetsClassifiedAsInvestingActivities"
PTDS = "PaymentsToDevelopSoftware"
PTAS = "PaymentsToAcquireSoftware"
PFS = "PaymentsForSoftware"
DEV = "PaymentsForDevelopmentProjectExpenditure"
CCSA = "CapitalizedComputerSoftwareAdditions"
OCF = "NetCashProvidedByUsedInOperatingActivities"
IPRD_EXPENSE = "ResearchAndDevelopmentAssetAcquiredOtherThanThroughBusinessCombinationWrittenOff"
COMPONENTS_55 = ["PaymentsToExploreAndDevelopOilAndGasProperties", "PaymentsToAcquireOilAndGasProperty", OTHER_PPE,
                 "PaymentsForConstructionInProcess", PRODUCTIVE, OTHER_PRODUCTIVE, CAP_IMPROVEMENTS]
INTANGIBLES_55 = [INTANG, OTHER_INTANG, IFRS_INTANG]
SOFTWARE_NAMES = {PTDS, PTAS, PFS, DEV}
NEW_COMPONENTS = {ME, MINING, FF}
PRE57_FIXTURES = ["AR", "APA", "ELS", "JLL", "DD", "NTNX", "TEM", "VIV", "TLK", "PUK", "CX", "CCJ", "STZ", "APP",
                  "BNT", "IESC", "WF", "VOD", "ATO", "RBC", "FER", "PR", "HALO"]
KNX_ARGS = ["--moat", "5"]     # KNX is unscored (pending in the queue): moat 5, universe.csv price $64.47, no judgment


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
_CACHE = {}


def _cached(key, fn):
    if key not in _CACHE:
        _CACHE[key] = fn()
    return _CACHE[key]


def _ttm():
    """A private copy of ttm.py bound to the shared dcf_engine (its helpers are pure)."""
    def load():
        H._shared_engine()
        spec = importlib.util.spec_from_file_location("_ttm_57_capex", os.path.join(SYS, "ttm.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    return _cached("ttm", load)


def run(ticker, args=(), judgment=None, ttm=None, fixture=None, patch=None):
    """dcf_engine.main() offline on the fixture in a temp base holding only the files passed here."""
    fx = fixture or H.load_fixture(ticker)
    base = H.make_base(fx, judgment, ttm, copy_repo_files=False)
    return H.run_engine(ticker, args=list(args), base=base, fixture=fx, patch=patch)


def run_ttm(ticker, judgment=None, fixture=None):
    fx = fixture or H.load_fixture(ticker)
    base = H.make_base(fx, judgment, None, copy_repo_files=False)
    return H.run_ttm(ticker, base=base, fixture=fx)


def row(rows, period):
    for r in rows:
        if r["period_end"] == period:
            return r
    raise AssertionError(f"no CSV row for {period}: {[r['period_end'] for r in rows]}")


def f(x):
    return None if x in (None, "") else float(x)


def flags(n, prefix):
    return [x for x in (n.get("fragility_flags") or []) if str(x).startswith(prefix)]


def fact(tag, value, filed="2026-02-20", unit="USD"):
    """One capex_for_period input fact (tag, value, unit, filed)."""
    return (tag, value, unit, filed)


def dropped(res):
    return {(d[0], d[-1]) for d in res.get("dropped") or []}


def _annual(tag, start, end, val, filed, accn, unit="USD", form="10-K"):
    return (tag, unit, {"start": start, "end": end, "val": val, "fy": int(end[:4]), "fp": "FY", "form": form,
                        "filed": filed, "accn": accn})


def _companyfacts(entries, cik=9990001, name="Synthetic Co"):
    """Synthetic companyfacts from (tag, unit, entry) triples (us-gaap)."""
    gaap = {}
    for tag, unit, e in entries:
        gaap.setdefault(tag, {"units": {}})["units"].setdefault(unit, []).append(dict(e))
    return {"cik": cik, "entityName": name, "facts": {"us-gaap": gaap}}


def _engine_assembly(facts, components=None, intangibles=None, eng=None):
    """dcf_engine.main()'s per-period capex assembly (period_series per tag, then capex_for_period per FY period),
    over the given component / intangible lists (default: the module's 5.7 lists)."""
    eng = eng or E
    comps = eng.CAPEX_COMPONENT_TAGS if components is None else components
    ints = eng.CAPEX_INTANGIBLE_TAGS if intangibles is None else intangibles

    def per_tag(tags):
        out = []
        for t in tags:
            vals, _, _, units, filed = eng.period_series(facts, [t], True, with_filed=True)
            out.append((eng._tag_name(t), vals, units, filed))
        return out
    groups = (per_tag(eng.CAPEX_ROLLUP_TAGS), per_tag(comps), per_tag(ints))
    cum = eng.cumulative_context_values(facts, ints)
    asm = {}
    for p in sorted({p for grp in groups for _, vals, _, _ in grp for p in vals}):
        legs = tuple([(name, vals[p], units[p], filed.get(p)) for name, vals, units, filed in grp if p in vals]
                     for grp in groups)
        asm[p] = eng.capex_for_period(*legs, cumulative=cum)
    return asm


def _halo_software(value=290000000):
    """HALO's fixture with capitalized software filed for FY2025 (a synthetic PaymentsToDevelopSoftware fact in the
    FY2025 10-K)."""
    fx = copy.deepcopy(H.load_fixture("HALO"))
    fx["facts"]["facts"]["us-gaap"][PTDS] = {"units": {"USD": [
        {"start": "2025-01-01", "end": "2025-12-31", "val": value, "fy": 2025, "fp": "FY", "form": "10-K",
         "filed": "2026-02-17", "accn": "0001159036-26-000024"}]}}
    return fx


def _ti():
    import test_engine_iprd as TI   # HALO_ARGS / HALO_TTM / HALO_J (the IPR&D lane's frozen HALO inputs)
    return TI


def _halo_period(n, period=None, window=None):
    ps = [p for p in (n.get("iprd_adjustment") or {}).get("periods") or []
          if (period is None or p.get("period") == period) and (window is None or p.get("window") == window)]
    assert len(ps) == 1, ps
    return ps[0]


# ===========================================================================
# 1. The lists (R8 / R9)
# ===========================================================================
def test_capex_lists_57():
    """T1: R8 appends machinery and equipment, mining assets and furniture and fixtures AFTER the 5.5 seven
    components (every 5.5 provenance string and tie-break keeps its order); R9 appends CAPEX_SOFTWARE_TAGS after the
    5.5 three intangible tags (PaymentsForSoftware after the two specific tags, the IFRS development tag last).
    CapitalizedComputerSoftwareAdditions (a roll-forward note element) is on no list; no tag ruled not capex is on
    a list; CAPEX_TAGS_54 is the historical 5.4 list, unchanged; the sub-classes (09b Q5: mining assets too) are
    components."""
    tn = E._tag_name
    assert list(E.CAPEX_COMPONENT_TAGS)[:7] == COMPONENTS_55
    assert list(E.CAPEX_COMPONENT_TAGS)[7:] == [ME, MINING, FF]
    assert [tn(t) for t in E.CAPEX_INTANGIBLE_TAGS][:3] == INTANGIBLES_55
    assert list(E.CAPEX_INTANGIBLE_TAGS)[3:] == list(E.CAPEX_SOFTWARE_TAGS)
    assert list(E.CAPEX_SOFTWARE_TAGS) == [PTDS, PTAS, PFS, (IF, DEV)]
    assert E.CAPEX_SOFTWARE_NAMES == SOFTWARE_NAMES == {tn(t) for t in E.CAPEX_SOFTWARE_TAGS}
    every = {tn(t) for t in E.CAPEX_ROLLUP_TAGS + E.CAPEX_COMPONENT_TAGS + E.CAPEX_INTANGIBLE_TAGS}
    assert CCSA not in every
    assert not (E.CAPEX_RULED_NOT_CAPEX & every)
    assert not any(t.startswith(E.CAPEX_RULED_NOT_CAPEX_PREFIXES) for t in every)
    assert E.CAPEX_TAGS_54 == frozenset({PRIMARY, "PaymentsForConstructionInProcess", OTHER_PPE, PRODUCTIVE,
                                         OTHER_PRODUCTIVE, IFRS_PPE, "PurchaseOfPropertyPlantAndEquipment",
                                         "PurchaseOfPropertyPlantAndEquipmentIntangibleAssetsOtherThanGoodwill"
                                         "InvestmentPropertyAndOtherNoncurrentAssets"})
    assert E.CAPEX_SUBCLASS_COMPONENTS == {FF, MINING} and E.CAPEX_SUBCLASS_COMPONENTS <= set(E.CAPEX_COMPONENT_TAGS)


def test_capex_like_vocabulary_matches_statements():
    """T14 (pin of a new constant): the unlisted-component check's vocabulary is statements.py's CAPEX_LIKE (the site
    already names unlisted capex-like tags with it), copied as a literal because the engine does not import
    statements.py."""
    import statements
    assert tuple(E.CAPEX_LIKE_WORDS) == tuple(statements.CAPEX_LIKE), (E.CAPEX_LIKE_WORDS, statements.CAPEX_LIKE)


def test_fixtures_unchanged_57():
    """T12 (pin): no pre-5.7 engine fixture carries a software tag or one of the three new components (they are
    trimmed to the 5.5 list), so test_engine_55 / test_engine_iprd's acceptance runs are the bit-identity proof."""
    for t in PRE57_FIXTURES:
        facts = H.load_fixture(t)["facts"]["facts"]
        names = {tag for tax in facts.values() for tag in tax}
        assert not (names & (SOFTWARE_NAMES | NEW_COMPONENTS)), (t, names & (SOFTWARE_NAMES | NEW_COMPONENTS))


# ===========================================================================
# 2. R8 — every filed PP&E component is summed (KNX, HUT); sub-classes never stand alone (EXR)
# ===========================================================================
def test_knx_sums_machinery_and_equipment_knx():
    """T2: KNX (Knight-Swift, CIK 1492691; unscored) — its capex line is PaymentsToAcquireMachineryAndEquipment
    ($795.4M FY2025) beside a $1.1M other-productive-assets line; 5.6 read the $1.1M (base $7.0009, Tier C, with
    CAPEX_COVERAGE_LOW firing at 0% of D&A). 5.7 sums both: FY2025 capex 796,458,000, base $0.3789, Tier D."""
    out = _cached("knx", lambda: run("KNX", KNX_ARGS, judgment={}))
    assert out["exit"] == 0, out["stdout"][-600:]
    n, rows = out["numbers"], out["rows"]
    tag = f"{OTHER_PRODUCTIVE}+{ME}"
    for p, capex in (("2023-12-31", 1072444000), ("2024-12-31", 819588000), ("2025-12-31", 796458000)):
        r = row(rows, p)
        assert f(r["capex"]) == capex and r["capex_source"] == "components" and r["capex_tag"] == tag, (p, r)
    assert n["capex_provenance"]["2025-12-31"]["ppe"] == {OTHER_PRODUCTIVE: 1066000, ME: 795392000}
    assert n["base_oe_per_share"] == 0.378863717820375, n["base_oe_per_share"]
    assert math.isclose(n["implied_irr_weighted"], 0.032783547908145166, rel_tol=1e-9), n["implied_irr_weighted"]
    assert n["tier_by_numbers"] == "D", n["tier_by_numbers"]
    assert not flags(n, "CAPEX_COVERAGE_LOW"), flags(n, "CAPEX_COVERAGE_LOW")
    assert not flags(n, "CAPEX_UNLISTED_COMPONENT"), flags(n, "CAPEX_UNLISTED_COMPONENT")   # T13: silent under 5.7


def test_knx_ttm_components_read_machinery():
    """T3: ttm.py reads the same lists — KNX's Q1-2026 YTD leg and its FY2025 leg sum M&E with the other line."""
    ppe, _ = _ttm().capex_assembly(H.load_fixture("KNX")["facts"])
    tag = f"{OTHER_PRODUCTIVE}+{ME}"
    assert ppe[("2026-01-01", "2026-03-31")] == (130037000, tag), ppe.get(("2026-01-01", "2026-03-31"))
    assert ppe[("2025-01-01", "2025-12-31")] == (796458000, tag), ppe.get(("2025-01-01", "2025-12-31"))


def test_every_filed_ppe_class_is_summed_hut():
    """T15 (list-driven): HUT's 10-K files its PP&E purchases as machinery and equipment ("Purchases of property and
    equipment") and mining assets ("Deposit paid to purchase miners and mining equipment"), neither listed before
    5.7 — no PP&E leg at all. ttm.capex_assembly now reads both (mining assets beside another class), and leg +
    intangibles equal the totals HUT's own override reason states (163,888,000 / 217,939,000)."""
    facts = _companyfacts([
        _annual(ME, "2024-01-01", "2024-12-31", 123991000, "2025-03-03", "0001-25-1"),
        _annual(MINING, "2024-01-01", "2024-12-31", 39611000, "2025-03-03", "0001-25-1"),
        _annual(INTANG, "2024-01-01", "2024-12-31", 286000, "2025-03-03", "0001-25-1"),
        _annual(ME, "2025-01-01", "2025-12-31", 202928000, "2026-02-25", "0001-26-1"),
        _annual(MINING, "2025-01-01", "2025-12-31", 14000000, "2026-02-25", "0001-26-1"),
        _annual(INTANG, "2025-01-01", "2025-12-31", 1011000, "2026-02-25", "0001-26-1")])
    ppe, res = _ttm().capex_assembly(facts)
    for per, leg, total in (("2024", 163602000, 163888000), ("2025", 216928000, 217939000)):
        k = (f"{per}-01-01", f"{per}-12-31")
        assert ppe.get(k) == (leg, f"{ME}+{MINING}"), (k, ppe.get(k))
        assert res[k]["ppe"] + res[k]["intangibles"] == total, res[k]


def test_capex_for_period_sums_what_it_is_handed():
    """T15p (PIN — passes on the old code too, by design): capex_for_period never filters by the lists, it sums the
    components it is handed; this is why T15 drives the list-driven path."""
    res = E.capex_for_period([], [fact(ME, 123991000), fact(MINING, 39611000)], [fact(INTANG, 286000)])
    assert res["ppe"] == 163602000 and res["intangibles"] == 286000, res


def test_subclass_component_never_stands_alone_exr():
    """T17 (R8 "a small other component never stands in for the whole"; 09b Q5): a sub-class component (furniture and
    fixtures, mining assets) is summed only beside a non-zero component of another class. Alone it is set aside
    before the zero-guard ('subclass_alone') and the period reads as in 5.6: EXR FY2013-21 filed $3.7-7.8M of
    furniture and fixtures and no other capex tag while spending $23-67M a year on development."""
    s1 = E.capex_for_period([], [fact(FF, 3659000)], [])
    assert s1["ppe"] is None and dropped(s1) == {(FF, "subclass_alone")}, s1
    assert [list(d) for d in s1["dropped"]] == [[FF, 3659000, "subclass_alone"]], s1["dropped"]
    s2 = E.capex_for_period([], [fact(FF, 3659000)], [fact(INTANG, 5)])
    assert s2["ppe"] is None and s2["intangibles"] == 5, s2
    s3 = E.capex_for_period([], [fact(CAP_IMPROVEMENTS, 200000000), fact(FF, 36100000)], [])   # UDR: summed
    assert s3["ppe"] == 236100000 and s3["ppe_tags"] == [CAP_IMPROVEMENTS, FF], s3
    s4 = E.capex_for_period([], [fact(OTHER_PPE, 0), fact(FF, 5000000)], [])   # a $0 other-class line admits nothing
    assert s4["ppe"] == 0 and s4["ppe_tags"] == [OTHER_PPE] and (FF, "subclass_alone") in dropped(s4), s4
    s5 = E.capex_for_period([fact(IFRS_PPE, 0)], [fact(FF, 5000000)], [])   # a $0 non-primary roll-up stays the leg
    assert s5["ppe"] == 0 and s5["ppe_source"] == "rollup" and (IFRS_PPE, "zero_guard") not in dropped(s5), s5
    s6 = E.capex_for_period([], [fact(ME, 1256000), fact(MINING, 966000)], [])   # mining assets beside M&E
    assert s6["ppe"] == 2222000, s6
    s7 = E.capex_for_period([], [fact(MINING, 966000)], [])   # 09b Q5: mining assets alone never are the leg
    assert s7["ppe"] is None and [list(d) for d in s7["dropped"]] == [[MINING, 966000, "subclass_alone"]], s7
    # the list-driven twin (ttm.py's capex_assembly): EXR-like companyfacts
    facts = _companyfacts([
        _annual(FF, "2021-01-01", "2021-12-31", 3659000, "2022-02-28", "0001-22-1"),
        _annual(PRODUCTIVE, "2023-01-01", "2023-12-31", 135577000, "2024-02-29", "0001-24-1"),
        _annual(FF, "2023-01-01", "2023-12-31", 15994000, "2024-02-29", "0001-24-1")])
    ppe, res = _ttm().capex_assembly(facts)
    assert ("2021-01-01", "2021-12-31") not in ppe, ppe
    assert (FF, "subclass_alone") in dropped(res[("2021-01-01", "2021-12-31")]), res[("2021-01-01", "2021-12-31")]
    assert ppe[("2023-01-01", "2023-12-31")] == (151571000, f"{PRODUCTIVE}+{FF}"), ppe


def test_subclass_guard_counts_only_the_leg_unit():
    """T17 s8 (review of the L9 build): "beside another class" counts only facts in the unit the component leg sums.
    The unit rule drops an other-unit fact ('unit'), so it must not admit a sub-class: M&E CNY 828M beside F&F USD 5M
    (a USD tie-break) read F&F as a USD 5M leg with M&E dropped — the silent small leg the sub-class rule exists to
    prevent (HTHT-type filers file M&E in CNY and USD). Now the sub-class is set aside and M&E is the leg in CNY;
    s8b mining assets alike; s8c two sub-classes in the majority unit; s8d a $0 non-primary roll-up still yields to
    the M&E leg (zero-guard), never to F&F. Pins (pass before the fix): s8e a sub-class beside a non-zero
    other-class fact in the leg's unit is summed and the other unit dropped (the 5.5 unit rule); s8f in CNY too."""
    s8 = E.capex_for_period([], [fact(ME, 828000000, unit="CNY"), fact(FF, 5000000)], [])
    assert (s8["ppe"], s8["ppe_unit"], s8["ppe_tags"]) == (828000000, "CNY", [ME]), s8
    assert [list(d) for d in s8["dropped"]] == [[FF, 5000000, "subclass_alone"]], s8["dropped"]
    s8b = E.capex_for_period([], [fact(ME, 828000000, unit="CNY"), fact(MINING, 14000000)], [])
    assert (s8b["ppe"], s8b["ppe_unit"]) == (828000000, "CNY") and dropped(s8b) == {(MINING, "subclass_alone")}, s8b
    s8c = E.capex_for_period([], [fact(ME, 828000000, unit="CNY"), fact(MINING, 14000000), fact(FF, 5000000)], [])
    assert (s8c["ppe"], s8c["ppe_unit"]) == (828000000, "CNY"), s8c
    assert dropped(s8c) == {(MINING, "subclass_alone"), (FF, "subclass_alone")}, s8c
    s8d = E.capex_for_period([fact(IFRS_PPE, 0)], [fact(ME, 828000000, unit="CNY"), fact(FF, 5000000)], [])
    assert (s8d["ppe"], s8d["ppe_unit"], s8d["ppe_tags"]) == (828000000, "CNY", [ME]), s8d
    assert dropped(s8d) == {(IFRS_PPE, "zero_guard"), (FF, "subclass_alone")}, s8d
    s8e = E.capex_for_period([], [fact(OTHER_PPE, 2000000), fact(FF, 5000000), fact(ME, 828000000, unit="CNY")], [])
    assert (s8e["ppe"], s8e["ppe_unit"], s8e["ppe_tags"]) == (7000000, "USD", [OTHER_PPE, FF]), s8e
    assert dropped(s8e) == {(ME, "unit")}, s8e
    s8f = E.capex_for_period([], [fact(ME, 828000000, unit="CNY"), fact(FF, 5000000, unit="CNY"),
                                  fact(MINING, 1000000)], [])
    assert (s8f["ppe"], s8f["ppe_unit"], s8f["ppe_tags"]) == (833000000, "CNY", [ME, FF]), s8f
    assert dropped(s8f) == {(MINING, "unit")}, s8f
    # the engine's own per-FY assembly (period_series per tag, then capex_for_period), on companyfacts filed in two units
    facts = _companyfacts([
        _annual(ME, "2025-01-01", "2025-12-31", 828000000, "2026-04-20", "0001-26-1", unit="CNY", form="20-F"),
        _annual(FF, "2025-01-01", "2025-12-31", 5000000, "2026-04-20", "0001-26-1", form="20-F")])
    res = _engine_assembly(facts)["2025-12-31"]
    assert (res["ppe"], res["ppe_unit"], res["ppe_tags"]) == (828000000, "CNY", [ME]), res
    assert (FF, "subclass_alone") in dropped(res), res


def test_superseded_ignores_a_retagged_54_value_rl():
    """T8 (an R8 consequence): RL re-tagged its capex line from PaymentsToAcquireProductiveAssets (a 5.4 tag) to
    machinery and equipment in its FY2026 10-K, comparatives included. With M&E listed, FY2024 keeps its value
    (ProductiveAssets dropped retag_duplicate) but no longer "uses a 5.4 tag": the old superseded test fired
    OVERRIDE_SUPERSEDED_BY_FILED_TAG:capex against RL's FY2026-only override (408.1M vs 164.8M = 2.48x) — a false
    make_score refusal. A period whose 5.4-tag value was dropped as a retag / same-filing duplicate was filed under
    5.4 too. (RL's real legs, from its companyfacts.)"""
    legs = {"2024-03-30": E.capex_for_period([], [fact(PRODUCTIVE, 164800000, "2025-05-22"), fact(ME, 164800000, "2026-05-21")], []),
            "2025-03-29": E.capex_for_period([], [fact(PRODUCTIVE, 216200000, "2025-05-22"), fact(ME, 216200000, "2026-05-21")], []),
            "2026-03-28": E.capex_for_period([], [fact(ME, 408100000, "2026-05-21")], [])}
    assert (PRODUCTIVE, "retag_duplicate") in dropped(legs["2024-03-30"]) and legs["2024-03-30"]["ppe_tags"] == [ME]
    periods = sorted(legs)
    hist = [{"period_end": p, "capex_tag": ME} for p in periods]
    checks = {}
    out = E._v55_flags({"defect": False, "rescued_by_pin": False}, {}, None, {}, {}, periods, hist, {"facts": {}},
                       {"capex": {"value": 408100000}}, legs, {"capex": set()}, periods, checks)
    assert not [x for x in out if x.startswith("OVERRIDE_SUPERSEDED_BY_FILED_TAG:capex")], out
    assert "superseded_periods" not in (checks.get("capex") or {}), checks


def test_ttm_superseded_legs_ignore_a_retag():
    """T9: ttm.py's per-leg twin (superseded_capex_legs) takes capex_assembly's results and applies the same rule."""
    T = _ttm()
    per = ("2023-04-02", "2024-03-30")
    res = {per: E.capex_for_period([], [fact(PRODUCTIVE, 164800000, "2025-05-22"), fact(ME, 164800000, "2026-05-21")], [])}
    capex = {"fy": 164800000, "fy_period": list(per), "fy_tag": ME}
    w = []
    assert T.superseded_capex_legs(capex, 408100000, w, res) == {} and w == [], w
    w2 = []   # without the results the old rule fires (the control)
    assert "fy" in T.superseded_capex_legs(capex, 408100000, w2) and w2


# ===========================================================================
# 3. R8 — "a small other component never stands in for the whole": CAPEX_UNLISTED_COMPONENT
# ===========================================================================
def test_unlisted_component_check_knx():
    """T13: against the 5.6 lists KNX's M&E line (1,071.6M / 819.2M / 795.4M) is a capex-like tag on no list,
    larger than the whole component leg it sits beside in the same 10-K (833K / 438K / 1,066K) — three hits; against
    the 5.7 lists, none. Tags ruled not capex (equipment on lease, net PaymentsForProceeds, real-estate tags) are
    never named. The no-leg variant: HUT's years with no PP&E leg under the 5.6 lists name M&E (filed in the same
    10-K as operating cash flow) with no_leg True, and _v55_flags emits the non-refusing
    CAPEX_UNLISTED_COMPONENT_OVERRIDDEN:<tag> for an override-filled year. No pre-5.7 fixture has a candidate."""
    facts = H.load_fixture("KNX")["facts"]
    last3 = ["2023-12-31", "2024-12-31", "2025-12-31"]
    asm56 = _engine_assembly(facts, COMPONENTS_55, E.CAPEX_INTANGIBLE_TAGS[:3])
    listed56 = {E._tag_name(t) for t in E.CAPEX_ROLLUP_TAGS + COMPONENTS_55 + E.CAPEX_INTANGIBLE_TAGS[:3]}
    hits = E.unlisted_capex_components(facts, asm56, last3, listed=listed56)
    assert [(h["period"], h["tag"], h["value"], h["leg_total"]) for h in hits] == [
        ("2023-12-31", ME, 1071611000, 833000), ("2024-12-31", ME, 819150000, 438000),
        ("2025-12-31", ME, 795392000, 1066000)], hits
    assert all(h["leg_tags"] == OTHER_PRODUCTIVE and h["accn"] and not h.get("no_leg") for h in hits), hits
    assert E.unlisted_capex_components(facts, _engine_assembly(facts), last3) == []
    # ruled not capex: never named even when larger than the leg
    syn = _companyfacts([_annual(OTHER_PRODUCTIVE, "2025-01-01", "2025-12-31", 1000000, "2026-02-20", "A1"),
                         _annual("PaymentsToAcquireEquipmentOnLease", "2025-01-01", "2025-12-31", 9e8, "2026-02-20", "A1"),
                         _annual("PaymentsForProceedsFromProductiveAssets", "2025-01-01", "2025-12-31", 9e8, "2026-02-20", "A1"),
                         _annual("PaymentsToDevelopRealEstateAssets", "2025-01-01", "2025-12-31", 9e8, "2026-02-20", "A1")])
    assert E.unlisted_capex_components(syn, _engine_assembly(syn), ["2025-12-31"]) == []
    # the no-leg variant (HUT, 5.6 lists: M&E and mining assets unlisted, so no PP&E leg in either year)
    hut = _companyfacts([
        _annual(ME, "2024-01-01", "2024-12-31", 123991000, "2025-03-03", "0001-25-1"),
        _annual(MINING, "2024-01-01", "2024-12-31", 39611000, "2025-03-03", "0001-25-1"),
        _annual(INTANG, "2024-01-01", "2024-12-31", 286000, "2025-03-03", "0001-25-1"),
        _annual(OCF, "2024-01-01", "2024-12-31", -68535000, "2025-03-03", "0001-25-1"),
        _annual(ME, "2025-01-01", "2025-12-31", 202928000, "2026-02-25", "0001-26-1"),
        _annual(MINING, "2025-01-01", "2025-12-31", 14000000, "2026-02-25", "0001-26-1"),
        _annual(INTANG, "2025-01-01", "2025-12-31", 1011000, "2026-02-25", "0001-26-1"),
        _annual(OCF, "2025-01-01", "2025-12-31", -139226000, "2026-02-25", "0001-26-1")])
    ps = ["2024-12-31", "2025-12-31"]
    hut56 = _engine_assembly(hut, COMPONENTS_55, E.CAPEX_INTANGIBLE_TAGS[:3])
    assert all(hut56[p]["ppe"] is None for p in ps), hut56
    nl = E.unlisted_capex_components(hut, hut56, ps, listed=listed56, no_leg_periods=ps)
    assert [(h["period"], h["tag"], h["value"], h["leg_total"], h["no_leg"]) for h in nl] == [
        ("2024-12-31", ME, 123991000, 0, True), ("2025-12-31", ME, 202928000, 0, True)], nl
    assert E.unlisted_capex_components(hut, _engine_assembly(hut), ps, no_leg_periods=ps) == []
    # _v55_flags on an engine copy that still has the 5.6 lists: the override-filled FY2025 names its fill
    E56 = H._engine()
    E56.CAPEX_COMPONENT_TAGS = COMPONENTS_55
    E56.CAPEX_INTANGIBLE_TAGS = E56.CAPEX_INTANGIBLE_TAGS[:3]
    hist = [{"period_end": "2024-12-31", "capex_tag": ""}, {"period_end": "2025-12-31", "capex_tag": "OVERRIDE"}]
    out = E56._v55_flags({"defect": False, "rescued_by_pin": False}, {}, None, {}, {}, ps, hist, hut, {}, hut56,
                         {"capex": set(ps)}, ps, {})
    ov = [x for x in out if x.startswith("CAPEX_UNLISTED_COMPONENT_OVERRIDDEN:")]
    assert len(ov) == 1 and ov[0].startswith(f"CAPEX_UNLISTED_COMPONENT_OVERRIDDEN:{ME} — FY2024 123,991,000 "
                                             "(accession 0001-25-1; DATA_GAP:capex), FY2025 202,928,000 "
                                             "(accession 0001-26-1; filled by capex_override)"), ov
    assert not [x for x in out if x.startswith("CAPEX_UNLISTED_COMPONENT:")], out
    # the refusing variant through _v55_flags on the same 5.6-list copy: KNX
    knx56 = _engine_assembly(facts, eng=E56)
    out = E56._v55_flags({"defect": False, "rescued_by_pin": False}, {}, None, {}, {}, last3,
                         [{"period_end": p, "capex_tag": OTHER_PRODUCTIVE} for p in last3], facts, {}, knx56,
                         {"capex": set()}, last3, {})
    un = [x for x in out if x.startswith("CAPEX_UNLISTED_COMPONENT:")]
    assert len(un) == 1 and un[0].startswith(f"CAPEX_UNLISTED_COMPONENT:{ME} — FY2023 1,071,611,000 (accession "), un
    assert "vs the whole component capex leg 1,066,000 (PaymentsToAcquireOtherProductiveAssets)" in un[0], un
    # end to end: dcf_engine.main() on KNX with the 5.6 lists (the engine KNX was blocked under) carries the flag
    def lists56(eng):
        eng.CAPEX_COMPONENT_TAGS = COMPONENTS_55
        eng.CAPEX_INTANGIBLE_TAGS = eng.CAPEX_INTANGIBLE_TAGS[:3]
    out = run("KNX", KNX_ARGS, judgment={}, patch=lists56)
    assert out["exit"] == 0 and f(row(out["rows"], "2025-12-31")["capex"]) == 1066000, out["stdout"][-400:]
    un = flags(out["numbers"], "CAPEX_UNLISTED_COMPONENT:")
    assert len(un) == 1 and un[0].startswith(f"CAPEX_UNLISTED_COMPONENT:{ME} — FY2023 1,071,611,000") \
        and "FY2025 795,392,000" in un[0], un
    # every pre-5.7 fixture: no candidate tag at all
    for t in PRE57_FIXTURES:
        fx = H.load_fixture(t)["facts"]
        a = _engine_assembly(fx)
        assert E.unlisted_capex_components(fx, a, sorted(a), no_leg_periods=sorted(a)) == [], t


# ===========================================================================
# 4. R9 — capitalized software is capex (JKHY), with double-count guards
# ===========================================================================
def test_jkhy_capitalized_software_is_capex_jkhy():
    """T4: JKHY (Jack Henry) capitalizes most of its development: PaymentsToDevelopSoftware $184.2M and
    PaymentsToAcquireSoftware $4.1M in FY2026 beside $67.1M of PP&E. On its recorded inputs (moat 7, price $153.19)
    5.6 published base $7.6631, 10.07%, Tier C; 5.7 adds the software: base $5.2289, 7.81%, Tier D. JKHY's
    FY2018/FY2019 PaymentsForSoftware equals the later PaymentsToAcquireSoftware re-tag (dropped retag_duplicate)."""
    rec = H.recorded("JKHY")
    out = _cached("jkhy", lambda: run("JKHY", H.recorded_args(rec), judgment=H.repo_judgment("JKHY")))
    assert out["exit"] == 0, out["stdout"][-600:]
    n, rows = out["numbers"], out["rows"]
    tag = f"{PRIMARY}+{PTDS}+{PTAS}"
    for p, intang in (("2024-06-30", 174305000), ("2025-06-30", 177808000), ("2026-06-30", 188351000)):
        r = row(rows, p)
        assert f(r["capex_intangibles"]) == intang and r["capex_tag"] == tag, (p, r)
    assert f(row(rows, "2026-06-30")["capex"]) == 255454000
    prov = n["capex_provenance"]
    assert prov["2026-06-30"]["software"] == {PTDS: 184243000, PTAS: 4108000}, prov["2026-06-30"]
    assert [PFS, 13138000, "retag_duplicate"] in prov["2018-06-30"]["dropped"], prov["2018-06-30"]
    assert [PFS, 6049000, "retag_duplicate"] in prov["2019-06-30"]["dropped"], prov["2019-06-30"]
    assert n["base_oe_per_share"] == 5.2289136833458825, n["base_oe_per_share"]
    assert math.isclose(n["implied_irr_weighted"], 0.078107428064912, rel_tol=1e-9), n["implied_irr_weighted"]
    assert n["tier_by_numbers"] == "D", n["tier_by_numbers"]
    assert rec["base_oe_per_share"] == 7.663139160791293 and rec["tier_by_numbers"] == "C"   # the published 5.4 run


def test_software_double_count_guards():
    """T5: the guards, live only when a software fact reaches the intangible leg. (a) TOST FY2022: the roll-up 16M,
    a ProductiveAssets subtotal 33M and PaymentsForSoftware 17M — the roll-up is used and the software added (the
    filer's own subtotal: 16 + 17 = 33), nothing dropped. (b) BCE FY2025 (CAD): the IFRS development tag equal to
    the PP&E line in the same filing is one line tagged twice — dropped ppe_duplicate. (c) a roll-up 33 = OtherPPE
    16 + software 17: the software is inside it (in_ppe_total). (d) the same on a component leg: the parts are
    dropped too and the leg is 33; (d2) with the part from an earlier filing the source label follows the
    survivor. (e) a software total and its software parts; (f) an intangible total containing software parts.
    (g) JKHY FY2026. (i) two different values in one filing are two disclosures (the 5.5 rule; this half a pin)."""
    a = E.capex_for_period([fact(PRIMARY, 16e6)], [fact(PRODUCTIVE, 33e6)], [fact(PFS, 17e6)])
    assert (a["ppe"], a["intangibles"], a["software"], a["software_tags"], a["dropped"]) == (16e6, 17e6, 17e6, [PFS], []), a
    b = E.capex_for_period([fact(IFRS_PPE, 3.7e9, unit="CAD")], [], [fact(IFRS_INTANG, 3e6, unit="CAD"),
                                                                    fact(DEV, 3.7e9, unit="CAD")])
    assert (DEV, "ppe_duplicate") in dropped(b) and b["intangibles"] == 3e6, b
    assert b["software"] == 0.0 and b["software_tags"] == [] and b["intangible_tags"] == [IFRS_INTANG], b
    c = E.capex_for_period([fact(PRIMARY, 33)], [fact(OTHER_PPE, 16)], [fact(PFS, 17)])
    assert (PFS, "in_ppe_total") in dropped(c) and c["intangibles"] == 0 and c["ppe"] == 33, c
    assert (OTHER_PPE, "parts_of_total") not in dropped(c), c   # a roll-up's parts were never summed
    d = E.capex_for_period([], [fact(OTHER_PPE, 16), fact(PRODUCTIVE, 33)], [fact(PFS, 17)])
    assert d["ppe"] == 33 and d["ppe_tags"] == [PRODUCTIVE] and d["intangibles"] == 0, d
    assert {(OTHER_PPE, "parts_of_total"), (PFS, "in_ppe_total")} <= dropped(d) and d["ppe_source"] == "components", d
    d2 = E.capex_for_period([], [fact(OTHER_PPE, 16, "2023-03-01"), fact(PRODUCTIVE, 33, "2024-03-01")],
                            [fact(PFS, 17, "2024-03-01")])
    assert d2["ppe"] == 33 and d2["ppe_source"] == "components", d2
    e = E.capex_for_period([fact(PRIMARY, 100)], [], [fact(PTDS, 25), fact(PTAS, 5), fact(PFS, 30)])
    assert e["intangibles"] == 30 and e["software"] == 30 and e["software_tags"] == [PFS], e
    assert {(PTDS, "parts_of_total"), (PTAS, "parts_of_total")} <= dropped(e), e
    f_ = E.capex_for_period([fact(PRIMARY, 100)], [], [fact(INTANG, 50), fact(PTDS, 30), fact(PTAS, 20)])
    assert f_["intangibles"] == 50 and f_["software"] == 0.0 and f_["software_tags"] == [], f_
    g = E.capex_for_period([fact(PRIMARY, 67103000)], [], [fact(PTDS, 184243000), fact(PTAS, 4108000)])
    assert g["intangibles"] == 188351000 and g["software"] == 188351000 and g["software_tags"] == [PTDS, PTAS], g
    i = E.capex_for_period([fact(PRIMARY, 37.4e6)], [], [fact(PTDS, 37.5e6)])
    assert i["intangibles"] == 37.5e6 and i["software"] == 37.5e6 and i["software_tags"] == [PTDS], i


def test_no_software_no_new_keys():
    """T5h (pin): a period with no software fact returns the 5.5 dict exactly (no software / software_tags key), and
    so does every period of every pre-5.7 fixture."""
    res = E.capex_for_period([fact(PRIMARY, 100)], [], [fact(INTANG, 7)])
    assert res == {"ppe": 100, "ppe_unit": "USD", "ppe_tags": [PRIMARY], "ppe_source": "rollup", "intangibles": 7.0,
                   "intangibles_unit": "USD", "intangible_tags": [INTANG], "dropped": [],
                   "provenance": f"{PRIMARY}+{INTANG}"}, res
    for t in PRE57_FIXTURES:
        for p, a in _engine_assembly(H.load_fixture(t)["facts"]).items():
            assert "software" not in a and "software_tags" not in a, (t, p, a)


def test_capitalized_software_additions_is_not_read():
    """T11 (pin): CapitalizedComputerSoftwareAdditions is a roll-forward note element (non-cash additions included,
    and at its filers inside the PP&E line: DOCU FY2026 143.4M vs 106.4M of PP&E purchases) — never read."""
    facts = _companyfacts([_annual(PRIMARY, "2025-02-01", "2026-01-31", 106400000, "2026-03-20", "D1"),
                           _annual(CCSA, "2025-02-01", "2026-01-31", 143400000, "2026-03-20", "D1")])
    a = _engine_assembly(facts)["2026-01-31"]
    assert a["ppe"] == 106400000 and a["intangibles"] == 0.0 and "software" not in a, a
    assert CCSA not in a["provenance"] and CCSA not in str(a["dropped"]), a


def test_override_year_never_takes_software_note_names_it():
    """T7: an override is the filer's TOTAL capex line, so an override year never takes the intangible leg (software
    included) on top; the OVERRIDE_APPLIED:capex note names the capitalized-software part it did not add, and the
    provenance lists what was filed with its unit. JKHY with FY2026's PP&E facts removed and a PP&E-only override."""
    fx = copy.deepcopy(H.load_fixture("JKHY"))
    g = fx["facts"]["facts"]["us-gaap"][PRIMARY]["units"]["USD"]
    fx["facts"]["facts"]["us-gaap"][PRIMARY]["units"]["USD"] = [e for e in g if e.get("end") != "2026-06-30"]
    rec = H.recorded("JKHY")
    j = H.repo_judgment("JKHY", capex_override={"value": 67103000, "kind": "filing", "reason": "test: the PP&E line",
                                                "source": "test: JKHY 10-K FY2026 cash-flow statement"})
    out = run("JKHY", H.recorded_args(rec), judgment=j, fixture=fx)
    assert out["exit"] == 0, out["stdout"][-600:]
    n, r = out["numbers"], row(out["rows"], "2026-06-30")
    assert r["capex_tag"] == "OVERRIDE" and f(r["capex"]) == 67103000 and r["capex_intangibles"] in ("", None), r
    p = n["capex_provenance"]["2026-06-30"]
    assert p["intangibles_not_added"] == "override_present", p
    assert p["intangibles_filed"] == {PTDS: 184243000, PTAS: 4108000} and p["intangibles_filed_unit"] == "USD", p
    assert "software" not in p, p
    note = flags(n, "OVERRIDE_APPLIED:capex")
    assert note and "FY2026 (188,351,000, of which capitalized software 188,351,000) were not added on top of the " \
                    "override" in note[0], note


def test_ttm_reads_software_jkhy():
    """T10: ttm.py's capex_assembly reads the software tags too (us-gaap entries of the shared list): JKHY's FY2026
    leg carries software / software_tags, so does a 10-Q YTD leg, and add_intangibles adds it."""
    T = _ttm()
    ppe, res = T.capex_assembly(H.load_fixture("JKHY")["facts"])
    fy = res[("2025-07-01", "2026-06-30")]
    assert fy["ppe"] == 67103000 and fy["software"] == 188351000 and fy["software_tags"] == [PTDS, PTAS], fy
    ytd = [k for k, v in res.items() if k[0] == "2025-07-01" and k[1] < "2026-06-30" and v.get("software_tags")]
    assert ytd, sorted(res)
    k = ytd[0]
    capex = {"fy": 67103000, "fy_period": ["2025-07-01", "2026-06-30"], "fy_tag": PRIMARY,
             "ytd_prior": 0, "ytd_prior_period": None, "ytd_prior_tag": None,
             "ytd_current": ppe[k][0], "ytd_current_period": list(k), "ytd_current_tag": ppe[k][1]}
    comps = T.add_intangibles(capex, res, [])
    assert capex["fy"] == 255454000 and comps["fy"]["software"] == 188351000, (capex, comps["fy"])
    assert capex["ytd_current"] == ppe[k][0] + res[k]["intangibles"] and comps["ytd_current"]["software_tags"], capex


def test_ttm_override_warning_names_software():
    """T10b: ttm.py's override-leg warning names the capitalized-software part it did not add (the engine's
    OVERRIDE_APPLIED note's twin); without software the 5.5 text is byte-identical."""
    T = _ttm()
    per = ("2025-07-01", "2026-06-30")
    res = {per: {"ppe": None, "intangibles": 188351000, "intangible_tags": [PTDS, PTAS], "software": 188351000,
                 "software_tags": [PTDS, PTAS], "dropped": [], "provenance": f"{PTDS}+{PTAS}"}}
    capex = {"fy": 67103000, "fy_period": list(per), "fy_tag": "OVERRIDE", "ytd_prior": 0, "ytd_prior_period": None,
             "ytd_current": 0, "ytd_current_period": None}
    w = []
    comps = T.add_intangibles(capex, res, w)
    assert comps["fy"]["intangibles_not_added"] == "override_present", comps
    assert w == ["capex fy: intangible purchases filed for 2025-07-01..2026-06-30 (188,351,000, of which capitalized "
                 "software 188,351,000) were not added on top of the override"], w
    res2 = {per: {"ppe": None, "intangibles": 5000, "intangible_tags": [INTANG], "dropped": [], "provenance": INTANG}}
    w2 = []
    T.add_intangibles(dict(capex), res2, w2)
    assert w2 == ["capex fy: intangible purchases filed for 2025-07-01..2026-06-30 (5,000) were not added on top of "
                  "the override"], w2


# ===========================================================================
# 5. The 5.6 IPR&D overlap guard reads the purchased-intangible part only (rebase A2)
# ===========================================================================
def test_iprd_overlap_guard_ignores_software_halo():
    """T6: HALO with 290M of capitalized software injected for FY2025 (>= 98% of its 284,887,000 acquired-IPR&D
    charge). The software is capex (FY2025 capex_intangibles 290M, provenance software), but the overlap guard reads
    only purchased intangibles: the charge stays deducted, with NO capex_overlap_note (the guard's FY subtraction;
    the mut_fy mutant — that subtraction reverted — adds the note)."""
    TI = _ti()
    out = run("HALO", TI.HALO_ARGS, judgment=TI.HALO_J, ttm=TI.HALO_TTM, fixture=_halo_software())
    assert out["exit"] == 0, out["stdout"][-600:]
    n = out["numbers"]
    assert f(row(out["rows"], "2025-12-31")["capex_intangibles"]) == 290000000
    assert n["capex_provenance"]["2025-12-31"]["software"] == {PTDS: 290000000}
    p = _halo_period(n, "2025-12-31", "fy")
    assert p["excluded"] is None and p["deducted"] == 284887000, p
    assert "capex_overlap_note" not in p, p


def test_iprd_paid_in_intangible_capex_is_not_met_by_software_halo():
    """T6': the same run with the worker's check declaring the charge paid inside intangible capex: capitalized
    software never meets that declaration's 98% floor, so the check is not applied (cash_flow_check_mismatch) and
    the period stays awaiting_cash_flow_check (make_score refuses it) — the mut_fy mutant reads already_in_capex."""
    TI = _ti()
    j = copy.deepcopy(TI.HALO_J)
    j["iprd_cash_flow_check"][0]["presentation"] = "paid_in_intangible_capex"
    out = run("HALO", TI.HALO_ARGS, judgment=j, ttm=TI.HALO_TTM, fixture=_halo_software())
    n = out["numbers"]
    assert n is not None, out["stdout"][-600:]
    assert f(row(out["rows"], "2025-12-31")["capex_intangibles"]) == 290000000
    p = _halo_period(n, "2025-12-31", "fy")
    assert p["excluded"] == "awaiting_cash_flow_check" and p.get("cash_flow_check_mismatch"), p


def _halo_ytd_case(presentation):
    TI = _ti()
    fx = copy.deepcopy(H.load_fixture("HALO"))
    g = fx["facts"]["facts"]["us-gaap"]
    g.setdefault(IPRD_EXPENSE, {"units": {"USD": []}})["units"].setdefault("USD", []).append(
        {"start": "2026-01-01", "end": "2026-06-30", "val": 50000000, "fy": 2026, "fp": "Q2", "form": "10-Q",
         "filed": "2026-08-04", "accn": "0001159036-26-000099"})
    ttm = copy.deepcopy(TI.HALO_TTM)
    ttm["capex_components"] = {"fy": None, "ytd_prior": None, "ytd_current": {
        "ppe": 6000000, "ppe_unit": "USD", "ppe_tags": [PRIMARY], "ppe_source": "rollup",
        "intangibles": 51000000.0, "intangibles_unit": "USD", "intangible_tags": [INTANG, PTDS], "dropped": [],
        "provenance": f"{PRIMARY}+{INTANG}+{PTDS}", "software": 50000000.0, "software_tags": [PTDS]}}
    j = copy.deepcopy(TI.HALO_J)
    j["iprd_cash_flow_check"].append({"period": "2026-06-30", "window": "ttm_current_ytd", "amount": 50000000,
                                      "presentation": presentation, "source": "test: HALO 10-Q Q2 2026 (synthetic)"})
    return run("HALO", TI.HALO_ARGS, judgment=j, ttm=ttm, fixture=fx), ttm


def test_iprd_ytd_overlap_guard_ignores_software_halo():
    """T6b: the current-YTD half — ttm.json's ytd_current leg holds 51M of intangible capex of which 50M is
    capitalized software (ttm.py writes software / software_tags since 5.7) beside a 50M YTD acquired-IPR&D charge:
    the guard reads 51M - 50M = 1M, so the charge is deducted with no capex_overlap_note (5.6 and the mut_ytd
    mutant read 51M and add the note)."""
    out, ttm = _halo_ytd_case("added_back_paid_in_investing")
    assert out["exit"] == 0, out["stdout"][-600:]
    n = out["numbers"]
    p = _halo_period(n, window="ttm_current_ytd")
    assert p["excluded"] is None and p["deducted"] == 50000000, p
    assert "capex_overlap_note" not in p, p
    assert ttm["capex_components"]["ytd_current"]["software"] == 50000000.0


def test_iprd_ytd_paid_in_intangible_capex_is_not_met_by_software_halo():
    """T6b': the YTD twin of T6' — 5.6 and the mut_ytd mutant mark the charge already_in_capex (51M >= 98% of 50M)."""
    out, _ = _halo_ytd_case("paid_in_intangible_capex")
    n = out["numbers"]
    assert n is not None, out["stdout"][-600:]
    p = _halo_period(n, window="ttm_current_ytd")
    assert p["excluded"] == "awaiting_cash_flow_check" and p.get("cash_flow_check_mismatch"), p


def test_iprd_overlap_guard_subtracts_software_in_usd_vod():
    """T6c: the FX path. VOD (EUR) with ifrs-full PaymentsForDevelopmentProjectExpenditure EUR 500M and a synthetic
    acquired-IPR&D expense EUR 2,375M (= its purchased intangibles) for FY2025, and a check declaring the charge
    paid inside intangible capex at its USD amount. The CSV's intangible leg includes the development (EUR 2,875M x
    1.0815 = 3,109,312,500); the guard reads the USD purchased intangibles only (2,568,562,500): the check is met,
    already_in_capex. The mut_fx mutant (software left in EUR) reads 2,609,312,500, mut_fy 3,109,312,500."""
    fx = copy.deepcopy(H.load_fixture("VOD"))
    F = fx["facts"]["facts"]
    accn = "0001193125-25-136298"
    F["ifrs-full"][DEV] = {"units": {"EUR": [{"start": "2024-04-01", "end": "2025-03-31", "val": 500000000, "fy": 2025,
                                              "fp": "FY", "form": "20-F", "filed": "2025-06-06", "accn": accn}]}}
    F.setdefault("us-gaap", {})[IPRD_EXPENSE] = {"units": {"EUR": [
        {"start": "2024-04-01", "end": "2025-03-31", "val": 2375000000, "fy": 2025, "fp": "FY", "form": "20-F",
         "filed": "2025-06-06", "accn": accn}]}}
    rec = H.recorded("VOD")
    j = {"iprd_cash_flow_check": [{"period": "2025-03-31", "window": "fy", "amount": 2568562500,
                                   "presentation": "paid_in_intangible_capex",
                                   "source": "test: VOD 20-F FY2025 (synthetic) intangible purchases line"}]}
    out = run("VOD", H.recorded_args(rec), judgment=j, fixture=fx)
    n = out["numbers"]
    assert n is not None, out["stdout"][-600:]
    assert math.isclose(f(row(out["rows"], "2025-03-31")["capex_intangibles"]), 3109312500, abs_tol=1.0)
    assert n["capex_provenance"]["2025-03-31"]["software"] == {DEV: 500000000}
    p = _halo_period(n, "2025-03-31", "fy")
    assert p["excluded"] == "already_in_capex", p
    assert math.isclose(p["capex_intangibles"], 2568562500, abs_tol=1.0), p["capex_intangibles"]


# ===========================================================================
# 6. ttm.json carries the engine release that built it (R8 / R9 TTM provenance; rebase A5)
# ===========================================================================
def test_ttm_json_carries_the_engine_release():
    """T16: ttm.py stamps its output with dcf_engine.ENGINE_RELEASE; an engine run whose basis reads ttm.json (the
    --ttm pin) copies a string stamp into ttm_inputs.ttm_engine_release, and records no such key for an unstamped
    (pre-5.7) file; a median run records ttm_inputs null."""
    TI = _ti()
    t = run_ttm("HALO", judgment={})
    assert t["exit"] == 0, t["stderr"][-600:]
    assert t["ttm"]["engine_release"] == E.ENGINE_RELEASE, t["ttm"].get("engine_release")
    stamped = dict(copy.deepcopy(TI.HALO_TTM), engine_release="5.7.0")
    out = run("HALO", TI.HALO_ARGS, judgment=TI.HALO_J, ttm=stamped)
    assert out["exit"] == 0, out["stdout"][-600:]
    ti = out["numbers"]["ttm_inputs"]
    assert ti["ttm_engine_release"] == "5.7.0" and ti == E.ttm_inputs_record(stamped), ti
    assert ti["ttm_input_hash"] == E.ttm_inputs_record(TI.HALO_TTM)["ttm_input_hash"]   # the stamp is outside the hash
    out = run("HALO", TI.HALO_ARGS, judgment=TI.HALO_J, ttm=TI.HALO_TTM)
    assert out["exit"] == 0 and "ttm_engine_release" not in out["numbers"]["ttm_inputs"], out["numbers"]["ttm_inputs"]
    median = [a for a in TI.HALO_ARGS if a != "--ttm"]
    out = run("HALO", median, judgment=TI.HALO_J, ttm=stamped)
    assert out["numbers"]["ttm_inputs"] is None, out["numbers"].get("ttm_inputs")


if __name__ == "__main__":
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except AssertionError as e:
                fails += 1
                print(f"FAIL {name}: {e}")
            except Exception as e:
                fails += 1
                print(f"ERROR {name}: {type(e).__name__}: {e}")
    sys.exit(1 if fails else 0)
