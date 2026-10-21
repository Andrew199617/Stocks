#!/usr/bin/env python3
"""interim_bridge.py — the declared 6-K interim bridge's rules and arithmetic (engine 5.7, Andrew's ruling R2a,
2026-10-19; design 04 A.1-A.2, tests 14-22, rebase L4 amendments 20-21). Pure: no network, no files but the committed
example. Run: python _system/tests/test_interim_bridge.py (or python -m pytest). Every test fails on the L0 scaffold
(e22e814: no module, ImportError).

14. the MICC example (_system/examples/interim_bridge.example.json) validates and computes the design's figures: OE
    $364,301,098 (±1), EUR 320,000,000 local, $0.590439/share at per-period ECB rates (FY 1.175 / H1 2025 1.172 /
    H1 2026 1.1394) and the H1 2026 diluted count.
15. one refusal per period rule IB-P0..IB-P6, each with its message.
16. estimate rules: an OCF estimate (IB-EST1), fy_prorated 3% off (IB-EST2), a method not allowed for the field
    (IB-EST3), a missing SBC leg (IB-EST4); comparative_carried / combined_in_ppe / fy_diluted_count.
17. snippet_shows_value: 539 / 276 / "(182)" / "1,234.5" show their values, 538,000,000 is not shown; a snippet over
    24 words is refused (IB-SNIP).
18. like-for-like: a material acquisition unresolved (IB-LFL2), immaterial without a revenue share / at 6% (IB-LFL3),
    outside_window inside the window (IB-LFL4), restated without fy_leg_consistent (IB-LFL1), a material
    discontinued operation (IB-LFL5); the MICC demerger same_business_perimeter passes.
19. per-period FX: the prior leg converts at 1.172, the current at 1.1394; one rate for all legs gives another TTM.
20. the ADS ratio scales the pin (ratio 5: per share × 5) and leaves the per-ordinary figure unchanged.
21. definitions: FY intangibles 0 and an interim intangible leg > 0 (IB-DEF1); FY SBC 0 and interim SBC > 0 (IB-DEF2).
22. declaration_hash is canonical (key order and whitespace do not move it; a value does).
T-i (amendment 20): a zero current-interim share count is a shape error.
Also: shape errors name their path; recompute_from_record reproduces compute from the record alone.
Review fixes (2026-10-21; each fails on the pre-fix L4 head 6fc70cd): a material false change inside the window
carries its revenue-share evidence whatever the resolution, same_business_perimeter is for a demerger only and
comparatives_re_presented needs the consistent restatement; IB-P5 reads the report's period only from an XBRL 6-K
(a non-XBRL 6-K's EDGAR reportDate is its cover date) and checks the filing date always; declaration_rule_problems
bundles every pure rule ttm.py enforces (make_score re-runs it).
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
sys.path.insert(0, SYS)
import interim_bridge as IB  # noqa: E402

EXAMPLE = os.path.join(SYS, "examples", "interim_bridge.example.json")
FY_LOCAL = {"ocf": 483e6, "capex_ppe": 357e6, "capex_intangibles": 3e6, "sbc": 35e6}
RATES = {"fy": 1.175, "prior_interim": 1.172, "current_interim": 1.1394}
FY_PERIOD = ["2025-01-01", "2025-12-31"]
TODAY = "2026-10-21"


def decl():
    with open(EXAMPLE, encoding="utf-8") as f:
        return json.load(f)["interim_bridge"]


def fy_leg(local=FY_LOCAL, r=RATES["fy"]):
    return {k: {"local": v, "usd": v * r} for k, v in local.items()}


def test_micc_example_validates_and_computes():
    d = decl()
    assert IB.validate_shape(d) == [], IB.validate_shape(d)
    assert IB.check_periods(d, FY_PERIOD, TODAY, report_date="2026-06-30") == []
    assert IB.check_like_for_like(d) == []
    assert IB.check_estimates(d, FY_LOCAL, FY_PERIOD) == []
    assert IB.check_definitions(d, {k: v * RATES["fy"] for k, v in FY_LOCAL.items()}) == []
    assert IB.snippet_problems(d) == [], IB.snippet_problems(d)
    out = IB.compute(d, fy_leg(), RATES, 1.0)
    assert abs(out["ttm_ocf"] - 858189600) < 1e-3, out["ttm_ocf"]
    assert abs(out["legs"]["capex_ppe"]["ttm_usd"] - 451045800) < 1e-3
    assert abs(out["legs"]["capex_intangibles"]["ttm_usd"] - 3476502) < 1, out["legs"]["capex_intangibles"]
    assert abs(out["ttm_capex"] - 454522302) < 1, out["ttm_capex"]
    assert abs(out["ttm_sbc"] - 39366200) < 1e-3
    assert abs(out["ttm_oe_total"] - 364301098) < 1, out["ttm_oe_total"]
    assert abs(out["ttm_oe_total_local"] - 320000000) < 1e-3, out["ttm_oe_total_local"]
    assert out["ttm_shares_diluted"] == 617000000
    assert abs(out["ttm_oe_per_share"] - 0.590439) < 1e-6 and out["ttm_oe_per_share"] == out["ttm_oe_per_ordinary_share"]
    est, unv = IB.leg_lists(d)
    assert est == ["capex_intangibles.prior_interim", "capex_intangibles.current_interim"] and unv == [], (est, unv)


def _p(d, **per):
    d = copy.deepcopy(d)
    for k, v in per.items():
        if k == "fy":
            d["fy_period"] = v
        else:
            d[k]["period"] = v
    return d


def test_period_rules():
    d = decl()
    cases = [
        (FY_PERIOD, _p(d, fy=["2024-01-01", "2024-12-31"]), "[IB-P0] interim_bridge.fy_period 2024-01-01..2024-12-31 is "
         "not the engine's latest fiscal year 2025-01-01..2025-12-31"),
        (FY_PERIOD, _p(d, prior_interim=["2025-02-01", "2025-06-30"]), "[IB-P1] prior interim starts 2025-02-01, 31 days "
         "from the FY start 2025-01-01 — the prior interim must be the first part of the latest FY"),
        (FY_PERIOD, _p(d, current_interim=["2026-01-20", "2026-06-30"]), "[IB-P2] current interim starts 2026-01-20, 20 "
         "days after the FY end 2025-12-31 (must be 1-10)"),
        (FY_PERIOD, _p(d, current_interim=["2026-01-01", "2026-09-30"]), "[IB-P3] interim lengths differ: prior 181 days, "
         "current 273 days"),
        (FY_PERIOD, _p(d, prior_interim=["2025-01-01", "2025-05-31"], current_interim=["2026-01-01", "2026-06-30"]),
         "[IB-P4] prior interim ends 2025-05-31, not the same months as the current interim end 2026-06-30 one year earlier"),
        (FY_PERIOD, d, None),
        (FY_PERIOD, _p(d, current_interim=["2026-01-01", "2026-06-30"]), None),
        (FY_PERIOD, _p(d, prior_interim=["2025-06-30", "2025-01-01"]), "[IB-P6] a period's start is after its end: "
         "prior_interim 2025-06-30..2025-01-01"),
    ]
    for fy, dd, want in cases:
        got = IB.check_periods(dd, fy, TODAY, report_date="2026-06-30")
        if want is None:
            assert got == [], got
        else:
            assert any(g.startswith(want) for g in got), (want, got)
    # IB-P5: after today / not the report's period / not after the FY end
    got = IB.check_periods(d, FY_PERIOD, "2026-06-01", report_date="2026-06-30")
    assert any(g.startswith("[IB-P5] current interim ends 2026-06-30: after today 2026-06-01") for g in got), got
    got = IB.check_periods(d, FY_PERIOD, TODAY, report_date="2026-03-31")
    assert any("not the report's period 2026-03-31 (±3 days)" in g and g.startswith("[IB-P5]") for g in got), got
    early = _p(d, fy=["2025-07-01", "2026-06-30"], prior_interim=["2025-07-01", "2025-12-31"],
               current_interim=["2026-01-01", "2026-06-30"])
    got = IB.check_periods(early, ["2025-07-01", "2026-06-30"], TODAY)
    assert any(g.startswith("[IB-P5] current interim ends 2026-06-30: not after the FY end 2026-06-30") for g in got), got


def _leg(d, f, name, **kw):
    d = copy.deepcopy(d)
    if kw.get("_drop"):
        del d["legs"][f][name]
    else:
        d["legs"][f][name].update(kw)
    return d


def test_estimate_rules():
    d = decl()
    est = _leg(d, "ocf", "prior_interim", kind="estimate", method="fy_prorated")
    assert any(g.startswith("[IB-EST1] ocf.prior_interim must be kind filing") for g in IB.check_estimates(est, FY_LOCAL)), \
        IB.check_estimates(est, FY_LOCAL)
    off = _leg(d, "capex_intangibles", "current_interim", value=1487671 * 1.03)
    got = IB.check_estimates(off, FY_LOCAL)
    assert got and got[0].startswith("[IB-EST2] capex_intangibles.current_interim (fy_prorated) declares") and \
        "the method gives 1,487,671" in got[0], got
    within = _leg(d, "capex_intangibles", "current_interim", value=1487671 * 1.009)
    assert IB.check_estimates(within, FY_LOCAL) == []
    bad = _leg(d, "capex_intangibles", "current_interim", method="fy_diluted_count")
    assert "[IB-EST3] method fy_diluted_count is not allowed for capex_intangibles" in IB.check_estimates(bad, FY_LOCAL)
    gone = _leg(d, "sbc", "current_interim", _drop=True)
    got = IB.check_estimates(gone, FY_LOCAL)
    assert any(g.startswith("[IB-EST4] sbc.current_interim is missing — condensed statements often omit SBC or "
                            "intangibles") for g in got), got
    no_shares = copy.deepcopy(d)
    del no_shares["legs"]["shares_diluted"]
    assert any(g.startswith("[IB-EST4] shares_diluted.current_interim is missing") for g in IB.check_estimates(no_shares, FY_LOCAL))
    # comparative_carried: the current leg carries the FILED prior leg's value
    cc = _leg(d, "sbc", "current_interim", kind="estimate", method="comparative_carried", value=19000000)
    assert IB.check_estimates(cc, FY_LOCAL) == []
    cc_bad = _leg(d, "sbc", "current_interim", kind="estimate", method="comparative_carried", value=18000000)
    assert any(g.startswith("[IB-EST2] sbc.current_interim (comparative_carried)") for g in IB.check_estimates(cc_bad, FY_LOCAL))
    # combined_in_ppe: 0, and the PP&E leg names the combined line
    comb = _leg(d, "capex_intangibles", "prior_interim", method="combined_in_ppe", value=0)
    comb = _leg(comb, "capex_intangibles", "current_interim", method="combined_in_ppe", value=0)
    got = IB.check_estimates(comb, FY_LOCAL)
    assert len(got) == 2 and all(g.startswith("[IB-EST2] capex_intangibles.") and "combined_in_ppe" in g for g in got), got
    for name in ("prior_interim", "current_interim"):
        comb = _leg(comb, "capex_ppe", name, reason="the line is 'Purchase of property, plant and equipment and intangible assets'")
    assert IB.check_estimates(comb, FY_LOCAL) == []
    # fy_diluted_count: exactly the CSV FY diluted count
    fyc = _leg(d, "shares_diluted", "current_interim", kind="estimate", method="fy_diluted_count", value=615600000)
    assert IB.check_estimates(fyc, FY_LOCAL, fy_shares=615600000) == []
    assert any(g.startswith("[IB-EST2] shares_diluted.current_interim (fy_diluted_count)")
               for g in IB.check_estimates(fyc, FY_LOCAL, fy_shares=615600001))


def test_snippet_shows_value():
    sn = "Income tax paid (84) (122) Net cash flow from operating activities 539 276"
    assert IB.snippet_shows_value(sn, 539000000) and IB.snippet_shows_value(sn, 276000000)
    assert not IB.snippet_shows_value(sn, 538000000)
    assert IB.snippet_shows_value("Purchase of property, plant and equipment (182) (150)", 182000000)
    assert IB.snippet_shows_value("Revenue 1,234.5 1,100.0", 1234500000)
    assert not IB.snippet_shows_value("Revenue 1,234.5", 1234600000)
    assert IB.snippet_shows_value("Diluted average number of shares (millions of share units) 617", 617000000)
    long_sn = " ".join(["word"] * 24) + " 539"
    d = _leg(decl(), "ocf", "current_interim", snippet=long_sn)
    assert IB.snippet_problems(d) == ["[IB-SNIP] ocf.current_interim snippet is 25 words (at most 24, R3)"], IB.snippet_problems(d)
    d = _leg(decl(), "ocf", "current_interim", snippet="Net cash flow from operating activities 538")
    assert IB.snippet_problems(d) == ["[IB-SNIP] ocf.current_interim snippet does not show 539,000,000 at any "
                                      "presentation scale"], IB.snippet_problems(d)
    assert IB.SNIPPET_MAX_WORDS == 24


def _pc(d, i, **kw):
    d = copy.deepcopy(d)
    d["like_for_like"]["perimeter_changes"][i].update(kw)
    return d


def test_like_for_like():
    d = decl()
    assert IB.check_like_for_like(d) == []           # MICC: demerger same_business_perimeter + immaterial acquisition
    acq = _pc(d, 1, material=True, resolution="same_business_perimeter")
    got = IB.check_like_for_like(acq)
    assert got and got[0].startswith("[IB-LFL2] perimeter change acquisition on 2026-03-30 lies inside the bridge window "
                                     "2025-01-01..2026-06-30, is material"), got
    for rs in (None, 0.06):
        imm = _pc(d, 1, revenue_share=rs)
        got = IB.check_like_for_like(imm)
        assert got and got[0].startswith("[IB-LFL3] acquisition on 2026-03-30 declared immaterial without revenue_share "
                                         f"below 5% (got {rs})"), got
    outw = _pc(d, 1, resolution="outside_window", material=False)
    assert IB.check_like_for_like(outw) == ["[IB-LFL4] resolution outside_window but 2026-03-30 is inside 2025-01-01..2026-06-30"]
    really_out = _pc(d, 1, resolution="outside_window", effective_date="2026-08-01")
    assert IB.check_like_for_like(really_out) == []
    rest = copy.deepcopy(d)
    rest["like_for_like"].update(comparative_restated=True, restatement={"description": "x", "fy_leg_consistent": False,
                                                                         "source": {}, "snippet": "s"})
    assert any(g.startswith("[IB-LFL1] the comparative was restated") for g in IB.check_like_for_like(rest))
    disc = _pc(d, 0, kind="discontinued_operation")
    assert any(g.startswith("[IB-LFL5] a material discontinued_operation inside the window (2025-12-06)")
               for g in IB.check_like_for_like(disc)), IB.check_like_for_like(disc)
    # a restated comparative consistent with the FY leg resolves a material disposal re-presented
    ok = _pc(d, 1, kind="disposal", material=True, resolution="comparatives_re_presented")
    ok["like_for_like"].update(comparative_restated=True, restatement={"description": "x", "fy_leg_consistent": True,
                                                                       "source": {}, "snippet": "s"})
    assert IB.check_like_for_like(ok) == []


def test_like_for_like_evidence_whatever_the_resolution():
    """Review fix (2026-10-21): inside the window, `material: false` carries the IB-LFL3 evidence (revenue_share below
    5% and its source) whatever the resolution; same_business_perimeter resolves a demerger only and
    comparatives_re_presented needs comparative_restated and restatement.fy_leg_consistent true, whatever `material`
    says (R2: "a restatement, demerger or material disposal / acquisition only when declared and resolved"). On the
    pre-fix code an unevidenced material false passed under any resolution but "immaterial"."""
    d = decl()

    def acq(**kw):
        x = _pc(d, 1, **kw)
        x["like_for_like"]["perimeter_changes"][1].pop("revenue_share", None)
        return x
    lfl2 = ("[IB-LFL2] perimeter change acquisition on 2026-03-30 lies inside the bridge window 2025-01-01..2026-06-30, "
            "is declared not material, and its resolution {} does not resolve it")
    got = IB.check_like_for_like(acq(resolution="same_business_perimeter"))
    assert len(got) == 1 and got[0].startswith(lfl2.format("same_business_perimeter")), got
    assert "same_business_perimeter resolves a demerger only" in got[0], got
    got = IB.check_like_for_like(acq(resolution="comparatives_re_presented"))
    assert len(got) == 1 and got[0].startswith(lfl2.format("comparatives_re_presented")), got
    assert "comparative_restated and restatement.fy_leg_consistent true" in got[0], got
    # the evidence does not make a non-demerger "same perimeter"
    got = IB.check_like_for_like(_pc(d, 1, resolution="same_business_perimeter"))
    assert len(got) == 1 and got[0].startswith(lfl2.format("same_business_perimeter")), got
    # comparatives re-presented consistently resolve the change; a material false still carries its evidence
    rest = {"comparative_restated": True, "restatement": {"description": "x", "fy_leg_consistent": True, "source": {},
                                                          "snippet": "s"}}
    cr = _pc(d, 1, resolution="comparatives_re_presented")
    cr["like_for_like"].update(copy.deepcopy(rest))
    assert IB.check_like_for_like(cr) == []
    cr_bare = acq(resolution="comparatives_re_presented")
    cr_bare["like_for_like"].update(copy.deepcopy(rest))
    got = IB.check_like_for_like(cr_bare)
    assert got == ["[IB-LFL3] acquisition on 2026-03-30 declared not material (resolution comparatives_re_presented) "
                   "without revenue_share below 5% (got None) and its source"], got
    # a demerger declared not material: same_business_perimeter resolves it, the not-material claim needs its share
    dem = _pc(d, 0, material=False)
    got = IB.check_like_for_like(dem)
    assert got == ["[IB-LFL3] demerger on 2025-12-06 declared not material (resolution same_business_perimeter) "
                   "without revenue_share below 5% (got None) and its source"], got
    assert IB.check_like_for_like(_pc(d, 0, material=False, revenue_share=0.01)) == []
    # a material change re-presented without the restatement: LFL2 as before
    got = IB.check_like_for_like(_pc(d, 1, kind="disposal", material=True, resolution="comparatives_re_presented"))
    assert len(got) == 1 and got[0].startswith("[IB-LFL2] perimeter change disposal on 2026-03-30 lies inside the bridge "
                                               "window 2025-01-01..2026-06-30, is material"), got
    # outside the window nothing needs resolving
    assert IB.check_like_for_like(acq(resolution="same_business_perimeter", effective_date="2026-08-01")) == []


def test_report_period_is_the_xbrl_period_only():
    """Review fix (2026-10-21; live EDGAR: TFII's Q2 6-K 0001193125-26-318068 filed 2026-07-27 has reportDate
    2026-07-27 and isXBRL 0, every FUTU 6-K's reportDate is its filingDate, VIV's October 6-Ks say 2026-12-31):
    EDGAR's reportDate of a 6-K without XBRL is its cover date, not the interim's period end. IB-P5 compares the current
    interim with the report's period only for an XBRL 6-K (its instance's dei DocumentPeriodEndDate, else its EDGAR
    reportDate), and with the filing date always (an interim report is filed after its period ends)."""
    d = decl()
    assert IB.report_period_end(True, "2026-06-30", "2026-07-30") == ("2026-06-30", IB.PERIOD_SOURCE_DEI)
    assert IB.report_period_end(True, "2026-06-30T00:00:00", None) == ("2026-06-30", IB.PERIOD_SOURCE_DEI)
    assert IB.report_period_end(True, None, "2026-06-30") == ("2026-06-30", IB.PERIOD_SOURCE_EDGAR)
    assert IB.report_period_end(False, None, "2026-07-27") == (None, None)
    assert IB.report_period_end(True, None, None) == (None, None)
    # TFII's shape: no report period to compare, filed after the interim ended
    assert IB.check_periods(d, FY_PERIOD, TODAY, report_date=None, filed="2026-07-27") == []
    # a report filed before the current interim ended is not its source (a Q1 6-K cited for H1 legs)
    got = IB.check_periods(d, FY_PERIOD, TODAY, filed="2026-05-28")
    assert got == ["[IB-P5] current interim ends 2026-06-30: not before the report's filing date 2026-05-28"], got
    # XBRL: within 3 days of the report's period, which a source label names
    assert IB.check_periods(d, FY_PERIOD, TODAY, report_date="2026-07-02", filed="2026-07-30") == []
    got = IB.check_periods(d, FY_PERIOD, TODAY, report_date="2026-03-31", filed="2026-07-30",
                           report_source=IB.PERIOD_SOURCE_DEI)
    assert got == ["[IB-P5] current interim ends 2026-06-30: not the report's period 2026-03-31 (±3 days; "
                   f"{IB.PERIOD_SOURCE_DEI})"], got
    assert IB.check_report_period(d, "2026-03-31", IB.PERIOD_SOURCE_DEI) == got
    assert IB.check_report_period(d, "2026-06-30", IB.PERIOD_SOURCE_DEI) == []
    assert IB.check_report_period(d, None) == []


def test_declaration_rules_bundle():
    """Review fix (2026-10-21): declaration_rule_problems runs every pure rule ttm.py --interim enforces on a
    declaration (periods, sources, snippets, estimates, definitions, like-for-like, the share band), so make_score
    re-runs exactly the rules ttm.py ran — the two never drift."""
    d = decl()
    fy_usd = {k: v * 1.175 for k, v in FY_LOCAL.items()}
    kw = dict(fy_period=FY_PERIOD, fy_local=FY_LOCAL, fy_usd=fy_usd, fy_shares=615600000, today=TODAY,
              report_date="2026-06-30", filed="2026-07-30")
    assert IB.declaration_rule_problems(d, **kw) == [], IB.declaration_rule_problems(d, **kw)
    other_src = copy.deepcopy(d)
    other_src["legs"]["sbc"]["prior_interim"]["source"]["accession"] = "0001104659-25-070000"
    cases = [
        (_pc(d, 1, material=True, resolution="same_business_perimeter"), {}, "[IB-LFL2]"),
        (_leg(d, "ocf", "current_interim", snippet="Net cash flow from operating activities 123 456"), {}, "[IB-SNIP]"),
        (other_src, {}, "[IB-SRC2] sbc.prior_interim cites accession 0001104659-25-070000"),
        (_leg(d, "capex_intangibles", "current_interim", value=1487671 * 1.03), {}, "[IB-EST2]"),
        (d, {"fy_usd": dict(fy_usd, capex_intangibles=0)}, "[IB-DEF1]"),
        (d, {"report_date": "2026-03-31"}, "[IB-P5]"),
        (d, {"fy_period": ["2024-01-01", "2024-12-31"]}, "[IB-P0]"),
        (_leg(d, "shares_diluted", "current_interim", value=6170000000), {}, "[IB-SH1]"),
    ]
    for dd, over, code in cases:
        got = IB.declaration_rule_problems(dd, **dict(kw, **over))
        assert any(g.startswith(code) for g in got), (code, got)
    rest = copy.deepcopy(d)
    rest["like_for_like"].update(comparative_restated=True, comparative_note="restated",
                                 comparative_source=dict(d["like_for_like"]["comparative_source"]),
                                 comparative_snippet="restated",
                                 restatement={"description": "re-presented", "fy_leg_consistent": False,
                                              "source": dict(d["like_for_like"]["comparative_source"]), "snippet": "x"})
    assert any(g.startswith("[IB-LFL1]") for g in IB.declaration_rule_problems(rest, **kw))
    usd = copy.deepcopy(d)
    usd["currency"], usd["fx"] = "USD", {"basis": "issuer_convenience_translation", "source": "the report",
                                         "prior_interim": {"date": "2025-06-30", "rate": 1.172,
                                                           "snippet": "translated at US$1.25 per euro"},
                                         "current_interim": {"date": "2026-06-30", "rate": 1.1394,
                                                             "snippet": "translated at US$1.1394 per euro"}}
    got = IB.snippet_problems(usd)
    assert got == ["[IB-SNIP] fx.prior_interim snippet does not show the report's rate 1.172"], got


def test_per_period_fx():
    d = decl()
    per = IB.compute(d, fy_leg(), RATES, 1.0)
    assert per["legs"]["ocf"]["prior_interim"]["usd"] == 276e6 * 1.172
    assert per["legs"]["ocf"]["current_interim"]["usd"] == 539e6 * 1.1394
    one = IB.compute(d, fy_leg(), {"fy": 1.175, "prior_interim": 1.175, "current_interim": 1.175}, 1.0)
    assert abs(one["ttm_oe_total"] - per["ttm_oe_total"]) > 1e6, (one["ttm_oe_total"], per["ttm_oe_total"])
    assert abs(one["ttm_oe_total"] - 320e6 * 1.175) < 1   # one rate: the local OE at that rate


def test_ads_ratio_scales_the_pin():
    d = decl()
    a = IB.compute(d, fy_leg(), RATES, 1.0)
    b = IB.compute(d, fy_leg(), RATES, 5.0)
    assert b["ttm_oe_per_ordinary_share"] == a["ttm_oe_per_ordinary_share"]
    assert abs(b["ttm_oe_per_share"] - 5 * a["ttm_oe_per_share"]) < 1e-12 and b["ads_ratio"] == 5.0
    assert b["ttm_shares_diluted"] == 617000000           # the ordinary count, never per ADS


def test_definitions():
    d = decl()
    fy_usd = {k: v * 1.175 for k, v in FY_LOCAL.items()}
    no_int = dict(fy_usd, capex_intangibles=0)
    got = IB.check_definitions(d, no_int)
    assert got == ["[IB-DEF1] the engine's FY capex has no intangible purchases (capex_provenance) but prior_interim "
                   "declares 1,487,671 — the TTM would mix capex definitions",
                   "[IB-DEF1] the engine's FY capex has no intangible purchases (capex_provenance) but current_interim "
                   "declares 1,487,671 — the TTM would mix capex definitions"], got
    got = IB.check_definitions(d, dict(fy_usd, sbc=0))
    assert len(got) == 2 and all(g.startswith("[IB-DEF2] the engine's FY SBC is 0 but sbc.") for g in got), got
    gone = copy.deepcopy(d)
    del gone["legs"]["capex_intangibles"]
    got = IB.check_definitions(gone, fy_usd)
    assert len(got) == 2 and all(g.startswith("[IB-EST4] capex_intangibles.") for g in got), got


def test_declaration_hash_is_canonical():
    d = decl()
    h = IB.declaration_hash(d)
    reordered = json.loads(json.dumps(d, sort_keys=True, indent=4))
    assert IB.declaration_hash(dict(reversed(list(reordered.items())))) == h
    assert IB.declaration_hash(json.loads(json.dumps(d, separators=(",", ":")))) == h
    moved = _leg(d, "ocf", "current_interim", value=539000001)
    assert IB.declaration_hash(moved) != h
    text = _leg(d, "ocf", "current_interim", reason="another reason")
    assert IB.declaration_hash(text) != h               # the declaration is the record: any edit re-runs ttm.py
    assert len(h) == 64


def test_shares_leg_zero_refused():
    d = _leg(decl(), "shares_diluted", "current_interim", value=0)
    assert IB.validate_shape(d) == ["[IB-SHAPE] interim_bridge.legs.shares_diluted.current_interim.value: a share count "
                                    "must be > 0 (got 0)"], IB.validate_shape(d)
    flow_zero = _leg(decl(), "sbc", "current_interim", value=0)
    assert IB.validate_shape(flow_zero) == []              # a flow leg may be zero


def test_shape_errors_name_their_path():
    d = decl()
    bad = copy.deepcopy(d)
    bad["basis"] = "ttm"
    bad["currency"] = "eur"
    bad["legs"]["ocf"]["prior_interim"]["source"]["accession"] = "88404"
    bad["legs"]["capex_ppe"]["current_interim"]["value"] = -1
    bad["legs"]["capex_intangibles"]["prior_interim"]["method"] = "guess"
    bad["legs"]["sbc"]["oops"] = {}
    bad["fx"]["prior_interim"]["date"] = "2025-06-29"
    bad["like_for_like"]["perimeter_changes"][1]["kind"] = "merger"
    del bad["reason"]
    got = IB.validate_shape(bad)
    for want in ("[IB-SHAPE] interim_bridge.basis: must be 'fy_minus_prior_interim_plus_current_interim'",
                 "[IB-SHAPE] interim_bridge.currency: an ISO 4217 code in upper case",
                 "[IB-SHAPE] interim_bridge.legs.ocf.prior_interim.source.accession: must be an EDGAR accession",
                 "[IB-SHAPE] interim_bridge.legs.capex_ppe.current_interim.value: a finite number >= 0",
                 "[IB-SHAPE] interim_bridge.legs.capex_intangibles.prior_interim.method: one of",
                 "[IB-SHAPE] interim_bridge.legs.sbc.oops: unknown leg",
                 "[IB-SHAPE] interim_bridge.fx.prior_interim.date: 2025-06-29 is not the period end 2025-06-30",
                 "[IB-SHAPE] interim_bridge.like_for_like.perimeter_changes[1].kind: one of",
                 "[IB-SHAPE] interim_bridge.reason: why the bridge is the right base"):
        assert any(g.startswith(want) for g in got), (want, got)
    assert IB.validate_shape("x") == ["[IB-SHAPE] interim_bridge: must be an object (see "
                                      "_system/examples/interim_bridge.example.json)"]
    usd = copy.deepcopy(d)
    usd["currency"] = "USD"
    assert any(g.startswith("[IB-SHAPE] interim_bridge.fx.basis: USD legs take basis none") for g in IB.validate_shape(usd))


def test_recompute_from_record():
    d = decl()
    out = IB.compute(d, fy_leg(), RATES, 2.0)
    rec = {"legs": out["legs"], "fx": {"rates_used": RATES}, "ads_ratio": 2.0,
           "shares": {"current_interim": {"value": 617000000}}}
    again = IB.recompute_from_record(rec)
    for k in ("ttm_ocf", "ttm_capex", "ttm_sbc", "ttm_oe_total", "ttm_oe_total_local", "ttm_oe_per_share",
              "ttm_oe_per_ordinary_share"):
        assert again[k] == out[k], k
    rec["legs"]["sbc"]["current_interim"]["local"] = 18000001
    assert IB.recompute_from_record(rec)["ttm_oe_per_share"] != out["ttm_oe_per_share"]
    assert IB.recompute_from_record({"legs": {}}) is None


if __name__ == "__main__":
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn) and fn.__module__ == __name__:
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
