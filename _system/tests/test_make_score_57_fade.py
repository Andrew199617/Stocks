#!/usr/bin/env python3
"""M6 in make_score (engine 5.7.0; Andrew, 2026-10-20: "eroding moat should fade faster and vice versa"; design
10_moat_fade, decisions 10b, lane defaults Q4-Q6; lane L3b). Run: python _system/tests/test_make_score_57_fade.py.
Offline: synthetic folders in a temp STOCKS_BASE (test_make_score_55.Run: make_score.py as a subprocess), the moat
scorecard fixtures of test_moat_scorecard and engine records built with the engine's own valuation functions at the
hold under test (test_moat_fade.hold_record).

T16 test_rebuttal_is_influence_under_erosion · T16b test_rebuttal_needs_an_anchor · T17
test_make_score_refuses_trend_mismatch · T18 test_make_score_in_sync_records_fade · T19 test_fade_gate_drift_on_rebuild
· T20 test_legacy_record_report_only · T21 test_final_run_args_carries_moat_trend · T22 test_fade_registry_events · T28
test_no_projection_records_fade · test_commodity_exemption_is_an_anchored_influence_field. Each fails on 4f7d6f1
(r57/L3b/failing_first.log): there the engine record carries no hold, make_score never checks the trend, the rebuttal
is checked only under G6, and no fade block, line or event exists.
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
for _p in (HERE, SYS):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import test_make_score_55 as H  # noqa: E402
import test_moat_scorecard as TM  # noqa: E402
from test_moat_fade import hold_record, _gm_rows, UPV, UPGM, DNV, DNGM, LABELS  # noqa: E402
import dcf_engine as E  # noqa: E402
import moat_scorecard as M  # noqa: E402

CUR = E.ENGINE_RELEASE
MOAT = 6


def syn(trend="stable", release=None, moat=MOAT, tier_f=False):
    """A replayable synthetic engine record (test_make_score_55._numbers plus g_base 6.6%, so the offsets give two
    scenarios at or below terminal — starts -5.4% / 1.6% / 6.6% / 11.6% / 18.6% — and IRRs (21.73% at hold 2, 20.52%
    at 0, 22.24% at 3) that equal no fixture row's figure: the quote matcher compares values, so a coincidence would
    let a restatement trace to an unrelated number) whose scenario figures are the engine's at the hold of `trend`;
    trend None: a record from before 5.7 (no hold keys, release 5.6.0 unless given)."""
    n = H._numbers()
    n["moat_score"] = moat
    n["inputs"] = dict(n["inputs"], moat=moat)
    n["g_base"] = 0.066
    n["cap_years"] = round(E.cap_years_for_moat(moat), 1)
    n["g_terminal"] = 0.025
    if tier_f:
        n.update(tier_by_numbers="F", implied_irr_weighted=None, implied_irr_base=None, iv_at_15=None, iv_at_12=None,
                 upside_at_15=None, scenarios={}, weighted={}, f_subtype="no_cash_generation", base_oe_per_share=-1.5)
        n.pop("g_base")
        if trend is not None:
            n.update(moat_trend=trend, hold_years=E.HOLD_BY_TREND[trend])
            n["inputs"] = dict(n["inputs"], moat_trend=trend, hold_years=E.HOLD_BY_TREND[trend], hold_rule="above_terminal")
        n["engine_release"] = release or CUR
        return n
    m = hold_record(n, trend or "stable")
    if trend is None:
        m.pop("moat_trend")
        m.pop("hold_years")
        for k in ("moat_trend", "hold_years", "hold_rule"):
            m["inputs"].pop(k)
        for k in LABELS:
            m["scenarios"][k].pop("hold_years")
        m["engine_release"] = release or "5.6.0"
    else:
        m["engine_release"] = release or CUR
    m.pop("content_hash", None)
    return m


def fade_run(rows, n=None, sc="base", facts=None, sic="3561", csv_rows=None, prior_score=None, moat=MOAT):
    n = n if n is not None else syn()
    j = H._judgment(n, moat_score=moat)
    if sc == "base":
        sc = TM.base_scorecard()
    if sc is not None:
        j["moat_scorecard"] = sc
    files = {"TST/fundamentals.json": {"cik": 1, "currency": "USD", "profile": {"sic": sic}, "annual": rows},
             "TST/facts.json": {"schema": 1, "ticker": "TST", "facts": facts if facts is not None else TM.base_facts()}}
    return H.Run(n, j, files=files, csv_rows=csv_rows, prior_score=prior_score).run()


def ero_rows():
    return _gm_rows(DNV, DNGM)        # governing roic -8.50pp, gross margin -4.00pp: MOAT_EROSION


def wid_rows():
    return _gm_rows(UPV, UPGM)        # +9.50pp / +3.00pp, returns_on_capital +2: every data guard passes


def rebut(text, extra_facts=()):
    sc = TM.base_scorecard()
    sc["erosion_rebuttal"] = text
    return sc, TM.with_facts(list(extra_facts))


def _done(r):
    try:
        r.close()
    except Exception:  # noqa: BLE001
        pass


def check(r, ok=True, *needles):
    try:
        if ok:
            r.ok()
        else:
            r.refused(*needles)
            assert not os.path.exists(r.registry), "a refusal wrote the registry"
        return r
    except Exception:
        _done(r)
        raise


# ---------------------------------------------------------------------------
def test_rebuttal_is_influence_under_erosion():
    """T16: MOAT_EROSION fired with erosion_risks 0 (G6 does not apply): a rebuttal restores the 2-year hold, so on a
    5.7 authoring run it is an influence field whenever declared — "a cycle" (no number) is refused; a traced,
    anchored number scores at hold 2 (the engine ran stable)."""
    sc, facts = rebut("a cycle, not erosion")
    r = check(fade_run(ero_rows(), syn("stable"), sc=sc, facts=facts), False,
              "judgment.json moat_scorecard.erosion_rebuttal carries no number")
    _done(r)
    sc, facts = rebut("a price cycle: price realization 4.5% [F3]")
    r = check(fade_run(ero_rows(), syn("stable"), sc=sc, facts=facts))
    try:
        f = r.score()["moat_evidence"]["fade"]
        assert (f["rule"], f["trend"], f["hold_years"], f["in_sync"]) == ("eroding_rebutted", "stable", 2, True), f
        inf = r.score()["declared_facts"]["influence"]["moat_scorecard.erosion_rebuttal"]
        assert inf["facts"] == ["F3"], inf
    finally:
        _done(r)


def test_rebuttal_needs_an_anchor():
    """T16b (10 §1.4): the trend test's own figures, its counterfactual and the record's hold-moved valuation outputs
    TRACE but never ANCHOR a rebuttal: restating the measured decline, the record's weighted IRR or the hold-0
    counterfactual is refused; a cited company filing fact tagged erosion_rebuttal (a price / volume / cycle figure)
    or a filed-history figure anchors it; a third-party or untagged fact does not; in the tangible-only case (DD) the
    plain-ROIC figures anchor, on a roic-governed erosion they are untraced."""
    n = syn("stable")
    restate = "governing ROIC -8.50pp and gross margin -4.00pp: cyclical"
    sc, facts = rebut(restate)
    r = check(fade_run(ero_rows(), n, sc=sc, facts=facts), False,
              "judgment.json moat_scorecard.erosion_rebuttal traces only through figures that restate the measurement")
    _done(r)
    irr_txt = f"{n['implied_irr_weighted'] * 100:.2f}%"
    sc, facts = rebut(f"at hold 2 the weighted IRR is {irr_txt}")
    r = check(fade_run(ero_rows(), n, sc=sc, facts=facts), False, "traces only through figures that restate")
    _done(r)
    probe = H._stamp(dict(n, ticker="TST"))
    cf0 = M.fade_counterfactual(probe, [0])[0]
    assert cf0["irr_weighted"] is not None and cf0["irr_weighted"] < n["implied_irr_weighted"]
    sc, facts = rebut(f"at hold 0 it would be {cf0['irr_weighted'] * 100:.2f}%")
    r = check(fade_run(ero_rows(), n, sc=sc, facts=facts), False, "traces only through figures that restate")
    _done(r)
    coil = TM.fact("F40", "hot_rolled_coil_price_change", "FY2023", 0.31, unit="pct", type="actual",
                   used=("erosion_rebuttal",))
    good = restate + "; hot-rolled coil prices fell 31% in FY2023 [F40]"
    sc, facts = rebut(good, [coil])
    r = check(fade_run(ero_rows(), n, sc=sc, facts=facts))
    try:
        assert r.score()["moat_evidence"]["fade"]["rule"] == "eroding_rebutted"
    finally:
        _done(r)
    tp = dict(coil, kind="third_party", source={"url": "https://example.com/coil", "publisher": "Example",
                                                 "published": "2024-01-10"})
    sc, facts = rebut(good, [tp])
    r = check(fade_run(ero_rows(), n, sc=sc, facts=facts), False, "rests only on third-party facts (F40)")
    _done(r)
    sc, facts = rebut(good, [dict(coil, used_for=["context"])])
    r = check(fade_run(ero_rows(), n, sc=sc, facts=facts), False, "cites F40, but F40 does not list used_for erosion_rebuttal")
    _done(r)
    csv_rows = [{"period_end": f"{y}-12-31", "fy_label": str(y), "revenue": rev, "net_income": 1, "operating_income": 1,
                 "ocf": 10, "capex": 1, "capex_assumed_zero": "False", "equity": 1000, "cash": 0, "debt_current": 0,
                 "debt_lt": 0, "tax": 0}
                for y, rev in zip((2021, 2022, 2023, 2024, 2025), (1500e6, 1400e6, 1234.5e6, 1300e6, 1350e6))]
    sc, facts = rebut(restate + "; revenue fell to $1,234.5M in FY2023 in the down-cycle")
    r = check(fade_run(ero_rows(), n, sc=sc, facts=facts, csv_rows=csv_rows))
    _done(r)
    # the tangible-only case (DD-shaped: tangible ROIC -5.46pp, plain ROIC only -2.73pp)
    dd = [TM.row(y, p, goodwill=500, gross_margin=g) for y, p, g in
          zip(TM.YEARS, (0.0463, 0.0463, 0.035, 0.019, 0.019), (0.40, 0.40, 0.39, 0.3776, 0.3776))]
    plain = "plain ROIC fell only 2.73pp, under the 3pp threshold"
    sc, facts = rebut(plain)
    r = check(fade_run(dd, syn("stable", moat=4), sc=sc, facts=facts, moat=4), True)
    try:
        f = r.score()["moat_evidence"]["fade"]
        assert f["measure"] == "roic_tangible" and f["rule"] == "eroding_rebutted", (f["measure"], f["rule"])
    finally:
        _done(r)
    r = check(fade_run(ero_rows(), n, sc=sc, facts=facts), False, "quotes 2.73pp that is neither an engine figure")
    _done(r)


def test_make_score_refuses_trend_mismatch():
    """T17: on a 5.7 authoring run make_score refuses (before any write) an engine run whose recorded trend or hold is
    not the trend test's — eroding data run at stable; a confirmed widening run at stable; a failed widening guard run
    at widening; a record pairing eroding with hold 2; a per-scenario hold that is neither the run's nor 2."""
    r = check(fade_run(ero_rows(), syn("stable")), False,
              "moat fade: make_score's trend test says eroding (governing roic -8.50pp FY2021-22 -> FY2024-25, gross "
              "margin -4.00pp; no erosion_rebuttal) -> --moat-trend eroding (growth hold 0 years), but the engine ran "
              "--moat-trend stable (hold 2) — rerun the final pass with --moat-trend eroding")
    _done(r)
    r = check(fade_run(wid_rows(), syn("stable")), False,
              "says widening (", "-> --moat-trend widening (growth hold 3 years), but the engine ran --moat-trend stable",
              "or declare moat_scorecard.widening_declined")
    _done(r)
    r = check(fade_run(wid_rows(), syn("widening"), sic="1040"), False,
              "says stable (widening guard failed: commodity SIC 1040", "but the engine ran --moat-trend widening (hold 3)",
              "rerun the final pass with --moat-trend stable")
    _done(r)
    bad = syn("eroding")
    bad["hold_years"] = 2
    bad["inputs"]["hold_years"] = 2
    r = check(fade_run(ero_rows(), bad), False,
              "dcf_numbers.json records moat_trend eroding with hold_years 2 — the engine pairs eroding with 0")
    _done(r)
    bad = syn("eroding")
    bad["scenarios"]["super_bear"]["hold_years"] = 7
    r = check(fade_run(ero_rows(), bad), False,
              "dcf_numbers.json scenarios.super_bear.hold_years 7 is neither the run's hold 0 nor the default 2")
    _done(r)


def test_make_score_in_sync_records_fade():
    """T18: an eroding record run at hold 0 on eroding data scores; score.json copies moat_trend / hold_years beside
    cap_years; moat_evidence.fade per 10 §6.3 (in sync; the counterfactual at hold 2 is the record replayed at 2);
    key_numbers' `- Moat:` line names the hold and the scorecard prints the Trend test and Fade direction lines."""
    n = syn("eroding")
    r = check(fade_run(ero_rows(), n))
    try:
        s, kn = r.score(), r.key()
        assert s["moat_trend"] == "eroding" and s["hold_years"] == 0
        keys = list(s)
        assert keys.index("cap_years") + 1 == keys.index("moat_trend"), keys[:20]
        f = s["moat_evidence"]["fade"]
        assert (f["version"], f["status"], f["direction"], f["rule"], f["trend"], f["hold_years"], f["in_sync"]) == (
            1, "measured", "eroding", "eroding_not_rebutted", "eroding", 0, True), f
        assert f["engine"] == {"moat_trend": "eroding", "hold_years": 0, "source": "inputs"}
        assert f["governing_change_pp"] == -8.5 and f["margin_change_pp"] == -4.0 and f["margin_basis"] == "gross"
        assert s["moat_evidence"]["erosion_test"]["direction"] == "eroding"
        rec = json.load(open(os.path.join(r.folder, "dcf_numbers.json"), encoding="utf-8"))
        exp = M.fade_counterfactual(rec, [2])[0]
        assert f["counterfactual"] == [exp] and exp["hold_years"] == 2 and exp["report_only"] is False
        assert exp["irr_weighted"] > round(rec["implied_irr_weighted"], 4)
        assert ("- Moat: 6/10 · CAP 9.8 yrs · growth hold 0 yrs (moat eroding, not rebutted; default 2) · terminal "
                "growth 2.50%") in kn, kn
        assert "- Trend test (last 5 FY, governing roic): FY2021-22 avg 29.50% -> FY2024-25 avg 21.00% (-8.50pp" in kn
        assert ("- Fade direction: eroding, erosion_rebuttal not declared -> growth hold 0 yrs · engine ran --moat-trend "
                f"eroding (hold 0): in sync · at hold 2 the weighted IRR would be {exp['irr_weighted'] * 100:.2f}% (tier "
                f"{exp['tier_by_numbers']}), IV@15 ${exp['iv_at_15']:,.2f}") in kn, kn
        json.dumps(s["moat_evidence"], allow_nan=False)
    finally:
        _done(r)


def test_fade_gate_drift_on_rebuild():
    """T19 (03c decision 6 kept for the fade, lane default Q5): a REBUILD of the same run, declaration and facts whose
    fundamentals.json moved so the trend reads stable records gate drift fade_sync (not refused); the numbers stay the
    engine's; fade.in_sync false; the Fade direction line says so. (T19b, the switch: test_moat_fade.)"""
    n = syn("eroding")
    r = check(fade_run(ero_rows(), n))
    try:
        first = r.score()
        path = os.path.join(r.folder, "fundamentals.json")
        doc = json.load(open(path, encoding="utf-8"))
        doc["annual"] = _gm_rows([0.20] * 5, [0.40] * 5)
        json.dump(doc, open(path, "w", encoding="utf-8"), indent=1)
        r.run().ok()
        s = r.score()
        f = s["moat_evidence"]["fade"]
        assert f["in_sync"] is False and f["trend"] == "stable" and f["rule"] == "no_trend"
        dr = [d for d in s["moat_evidence"]["gate_drift"] if d["gate"] == "fade_sync"]
        assert len(dr) == 1 and "data moved since the engine run; the next engine run passes --moat-trend stable" in dr[0]["detail"]
        for k in ("implied_irr", "iv_at_15", "tier_by_numbers", "hold_years", "moat_trend"):
            assert s[k] == first[k], k
        kn = r.key()
        assert "OUT OF SYNC — gate drift on this rebuild" in kn and "- Gate drift on this rebuild" in kn and "fade_sync" in kn
    finally:
        _done(r)


def test_legacy_record_report_only():
    """T20: a 5.6.0 record on eroding data: no refusal; fade report_only with the would-be hold's counterfactual
    flagged report_only; the "Growth & moat" `- Moat:` line is byte for byte the pre-5.7 line; score.json carries no
    top-level hold_years / moat_trend."""
    n = syn(None)
    r = check(fade_run(ero_rows(), n, sc=None))
    try:
        s = r.score()
        assert "hold_years" not in s and "moat_trend" not in s
        f = s["moat_evidence"]["fade"]
        assert (f["rule"], f["trend"], f["hold_years"], f["in_sync"]) == ("report_only", None, None, None)
        assert len(f["counterfactual"]) == 1 and f["counterfactual"][0]["hold_years"] == 0
        assert f["counterfactual"][0]["report_only"] is True and f["counterfactual"][0]["irr_weighted"] is not None
        assert f["engine"] == {"moat_trend": None, "hold_years": 2, "source": "default"}
        kn = r.key()
        assert "- Moat: 6/10 · CAP 9.8 yrs · terminal growth 2.50%\n" in kn, kn
        assert "- Fade direction (report only, pre-5.7 record): eroding -> a 5.7 run holds growth 0 yrs unless rebutted" in kn
        assert [e for e in r.entries() if str(e.get("event", "")).startswith("moat_")] == []
    finally:
        _done(r)


def test_final_run_args_carries_moat_trend():
    """T21 (10 §5.4, rebase A7): _final_run_args replays a 5.7 record's --moat-trend right after the --gterm pair (a
    legacy record: none, the engine default), so every counterfactual spawn — compute_override_impact,
    payable_pin_impact, iprd_amortized_impact — runs on the scored hold."""
    import make_score as MS
    n = syn("eroding")
    args = MS._final_run_args(n)
    g = args.index("--gterm")
    assert args[g + 2:g + 4] == ["--moat-trend", "eroding"], args
    assert "--moat-trend" not in MS._final_run_args(syn(None))
    seen = []
    saved = MS._run_json

    def fake(cmd, env_extra=None, timeout=600):
        seen.append(cmd)
        return {"base_oe_per_share": 3.0, "implied_irr_weighted": 0.1, "tier_by_numbers": "D", "data_gap": [],
                "iprd_adjustment": {}}
    MS._run_json = fake
    try:
        MS.payable_pin_impact("TST", n)
        am = dict(n, iprd_adjustment={"treatment": "amortized_in_base",
                                      "amortized": {"native_base": "median", "native_base_per_share": 3.0}})
        MS.iprd_amortized_impact("TST", am)
        MS.compute_override_impact("TST", dict(n, overrides_applied=[{"field": "capex", "value": 1, "kind": "estimate"}]))
    finally:
        MS._run_json = saved
    assert len(seen) >= 3, seen
    for cmd in seen:
        i = cmd.index("--moat-trend")
        assert cmd[i + 1] == "eroding", cmd


def test_fade_registry_events():
    """T22 (10 §5.6): a rebutted erosion records moat_erosion_rebuttal with hold_years 2, hold_without 0 and both
    weighted IRRs; a declined widening records moat_widening_declined (hold 2 vs 3); both pass the registry's own
    check (declared events, no deferred-payment key); a second run keeps the first date; a rebuild whose fade drifted
    writes neither."""
    import make_score as MS
    sc, facts = rebut("a price cycle: price realization 4.5% [F3]")
    n = syn("stable")
    r = check(fade_run(ero_rows(), n, sc=sc, facts=facts))
    try:
        ev = r.entries("moat_erosion_rebuttal")
        assert len(ev) == 1, r.entries()
        e = ev[0]
        assert e["hold_years"] == 2 and e["hold_without"] == 0 and e["moat_score"] == 6.0
        assert e["irr_weighted"] == round(n["implied_irr_weighted"], 4)
        assert e["irr_weighted_without"] == r.score()["moat_evidence"]["fade"]["counterfactual"][0]["irr_weighted"]
        assert e["irr_weighted_without"] < e["irr_weighted"] and e["governing_change_pp"] == -8.5
        assert e["margin_change_pp"] == -4.0 and e["margin_basis"] == "gross" and e["reason"] == sc["erosion_rebuttal"]
        assert MS.registry_entry_problem(e) is None and not set(e) & set(MS.IPRD_DEFERRED_EVENT_KEYS)
        reg = json.load(open(r.registry, encoding="utf-8"))
        for x in reg["entries"]:
            if x.get("event") == "moat_erosion_rebuttal":
                x["date"] = "2026-10-01"
        json.dump(reg, open(r.registry, "w", encoding="utf-8"))
        r.run().ok()
        assert [x["date"] for x in r.entries("moat_erosion_rebuttal")] == ["2026-10-01"]
        # the data moves (rebuild): the rebuttal no longer has an erosion to answer -> fade drift, no event
        path = os.path.join(r.folder, "fundamentals.json")
        doc = json.load(open(path, encoding="utf-8"))
        doc["annual"] = _gm_rows([0.30, 0.30, 0.30, 0.30, 0.30], [0.40] * 5)
        json.dump(doc, open(path, "w", encoding="utf-8"), indent=1)
        r.run().ok()
        f = r.score()["moat_evidence"]["fade"]
        assert f["rule"] == "no_trend" and f["in_sync"] is True and f["rebuttal_unused"] is True, f
        assert r.entries("moat_erosion_rebuttal") == [], "an unused rebuttal records no event"
    finally:
        _done(r)
    sc = TM.base_scorecard()
    sc["widening_declined"] = "a recovery from the 2021 trough, not a wider moat"
    r = check(fade_run(wid_rows(), syn("stable"), sc=sc))
    try:
        ev = r.entries("moat_widening_declined")
        assert len(ev) == 1, r.entries()
        e = ev[0]
        assert e["hold_years"] == 2 and e["hold_without"] == 3 and e["irr_weighted_without"] > e["irr_weighted"]
        assert e["reason"] == sc["widening_declined"] and e["governing_change_pp"] == 9.5
        assert MS.registry_entry_problem(e) is None and not set(e) & set(MS.IPRD_DEFERRED_EVENT_KEYS)
    finally:
        _done(r)
    # a drifted rebuild: run eroding at hold 0, then the data turns widening-free flat -> drift, and no fade event
    me = {"status": "checked", "moat_score": 6, "gates": {}, "erosion_test": {}, "gate_drift": [{"gate": "fade_sync"}],
          "fade": {"rule": "eroding_rebutted", "hold_years": 2, "counterfactual": []}}
    assert MS._moat_events("TST", "2026-10-21", me, n={"implied_irr_weighted": 0.1}) == []
    me["gate_drift"] = []
    out = MS._moat_events("TST", "2026-10-21", me, n={"implied_irr_weighted": 0.1})
    assert [x["event"] for x in out] == ["moat_erosion_rebuttal"] and out[0]["irr_weighted_without"] is None


def test_no_projection_records_fade():
    """T28: a Tier F 5.7 record (no scenarios) on widening — then eroding — data with the engine at the default
    stable scores on an authoring run: fade rule no_projection, in_sync / trend / hold null, no counterfactual, no
    registry event, no gate drift."""
    for rows in (wid_rows(), ero_rows()):
        r = check(fade_run(rows, syn("stable", tier_f=True)))
        try:
            me = r.score()["moat_evidence"]
            f = me["fade"]
            assert (f["rule"], f["trend"], f["hold_years"], f["in_sync"], f["counterfactual"]) == (
                "no_projection", None, None, None, []), f
            assert f["direction"] in ("widening", "eroding") and me["gate_drift"] == []
            assert [e for e in r.entries() if e.get("event") in ("moat_erosion_rebuttal", "moat_widening_declined")] == []
            assert "(no projection: Tier F record, the hold changes nothing) · engine recorded --moat-trend stable" in r.key()
        finally:
            _done(r)


def test_commodity_exemption_is_an_anchored_influence_field():
    """10 §1.3 guard 4 / 10b OQ10: a business_type_reason that lifts the commodity guard (a widening at SIC 1040
    confirmed at hold 3) goes through check_influence with the anchor rule — its cost-position fact must list
    business_type_reason (else refused); with it the widening scores at hold 3."""
    sc = TM.base_scorecard()
    sc["business_type_reason"] = "First-quartile cost: cash cost $412 per tonne [F30], an engineered-service mix"
    cost = TM.fact("F30", "cash_cost_per_unit", "FY2025", 412, unit="USD", type="actual", used=("business_type_reason",))
    r = check(fade_run(wid_rows(), syn("widening"), sc=sc, facts=TM.with_facts([cost]), sic="1040"))
    try:
        f = r.score()["moat_evidence"]["fade"]
        assert f["rule"] == "widening_confirmed" and f["guards"]["commodity_sic"]["exempted_by_reason"]
        assert r.score()["hold_years"] == 3
        assert r.score()["declared_facts"]["influence"]["moat_scorecard.business_type_reason"]["facts"] == ["F30"]
    finally:
        _done(r)
    sc["business_type_reason"] = "First-quartile cost: cash cost $412 per tonne [F30]; 70% of revenue is services"
    r = check(fade_run(wid_rows(), syn("widening"), sc=sc, facts=TM.with_facts([cost]), sic="1040"), False,
              "judgment.json moat_scorecard.business_type_reason quotes 70% that is neither an engine figure")
    _done(r)


if __name__ == "__main__":
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except Exception as e:  # noqa: BLE001
                fails += 1
                import traceback
                traceback.print_exc()
                print(f"FAIL {name}: {type(e).__name__}: {e}")
    sys.exit(1 if fails else 0)
