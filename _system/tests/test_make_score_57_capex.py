#!/usr/bin/env python3
"""make_score.py under engine release 5.7 — capex components (R8) and capitalized software (R9) (Andrew, 2026-10-19;
assigned to Claude; design 09_capex.md §6 with 09b and the ba2bfc0 rebase map A5-A9).
Run: python _system/tests/test_make_score_57_capex.py (or python -m pytest _system/tests). No network.

Every end-to-end case runs make_score.py on a synthetic folder in a temp STOCKS_BASE, the test_make_score_55.py way
(an engine-stamped dcf_numbers.json, the registry redirected, fail-loud engine / ttm.py stand-ins). The rules, on a 5.7
run only (older output rebuilds unchanged):
  M1  key_numbers.md's capex-basis line names the capitalized-software part.
  M2  a capex_override that fills a last-3-FY year beside filed capitalized software needs software_included: true,
      whatever its value (M2b); M2c the same for a TTM leg of ttm.json; M2d an override-filled TTM leg of a ttm.json
      without a 5.7 stamp cannot be checked and is refused.
  M3  software_included must be a bool and is capex_override's only; M3b with the declaration the override must be at
      least the filed intangible leg (a total is never smaller than its part); M3c in USD on the engine's own
      currency basis (the leg's own fetched rate first — rebase A9); the declaration rides on the registry entry.
  M4  a 5.6.0 record with the same provenance rebuilds with no refusal and no software text.
  M5  CAPEX_UNLISTED_COMPONENT:<tag> needs judgment.json capex_unlisted_ack[<tag>] with a figure; an override does not
      release it; the ack is recorded as a capex_unlisted_ack registry event whose first date is kept; M5b the
      _OVERRIDDEN variant is never refused.
  M6  a 5.7 run whose basis read ttm.json (ttm_inputs recorded) needs ttm_inputs.ttm_engine_release >= 5.7.0.
Each fails on the code before this lane (e22e814) unless labelled a pin.
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
import make_score as M  # noqa: E402
import dcf_engine as E  # noqa: E402
import rulings57  # noqa: E402
from test_make_score_55 import (Run, _with, _numbers, _judgment, _csv_row, T, CUR, TTM_LEG_STANDIN)  # noqa: E402

PRIMARY = "PaymentsToAcquirePropertyPlantAndEquipment"
PTDS = "PaymentsToDevelopSoftware"
PTAS = "PaymentsToAcquireSoftware"
INTANG = "PaymentsToAcquireIntangibleAssets"
IFRS_INTANG = "PurchaseOfIntangibleAssetsClassifiedAsInvestingActivities"
DEV = "PaymentsForDevelopmentProjectExpenditure"
ME = "PaymentsToAcquireMachineryAndEquipment"
SOURCE = "Form 10-K FY2026, Consolidated Statements of Cash Flows (test)"


def _ov(value, **kw):
    o = {"value": value, "kind": "filing", "source": SOURCE, "reason": "DATA_GAP:capex — the FY2026 PP&E line is untagged (test)"}
    o.update(kw)
    return o


# JKHY FY2026 shape: the PP&E line filled by a capex_override, the filed software not added on top of it
JK_PROV = {"2024-06-30": {"ppe_source": "rollup", "ppe": {PRIMARY: 58118000}, "ppe_unit": "USD",
                          "intangibles": {PTDS: 167175000, PTAS: 7130000}, "intangibles_unit": "USD", "dropped": [],
                          "filed": {}, "software": {PTDS: 167175000, PTAS: 7130000}},
           "2025-06-30": {"ppe_source": "rollup", "ppe": {PRIMARY: 53358000}, "ppe_unit": "USD",
                          "intangibles": {PTDS: 172445000, PTAS: 5363000}, "intangibles_unit": "USD", "dropped": [],
                          "filed": {}, "software": {PTDS: 172445000, PTAS: 5363000}},
           "2026-06-30": {"ppe_source": "override", "ppe": {}, "ppe_unit": None, "intangibles": {},
                          "intangibles_unit": None, "dropped": [], "filed": {},
                          "intangibles_not_added": "override_present", "intangibles_filed_unit": "USD",
                          "intangibles_filed": {PTDS: 184243000, PTAS: 4108000}}}


def _jk_record(value, release=CUR, basis="no_fx", prov=None, **kw):
    """A 5.7 record whose capex_override (value, kind filing) filled FY2026 beside filed software."""
    fields = dict(capex_provenance=copy.deepcopy(prov or JK_PROV), data_gap=["capex"], data_gap_uncovered=[],
                  override_checks={"capex": {"value": float(value), "last_filed_value": 53358000, "last_filed_unit": "USD",
                                             "out_of_band": False, "ack_reason_present": False, "currency_basis": basis}},
                  overrides_applied=[dict(_ov(value), field="capex", value=float(value), periods_filled=["2026-06-30"])],
                  fragility_flags=["OVERRIDE_APPLIED:capex — filing gap in the last 3 FY filled by a judgment override"])
    fields.update(kw)
    return _numbers(release=release, **fields)


ENGINE_STANDIN = r'''import json, os, sys
# Stand-in dcf_engine.py (test_make_score_57_capex): the override-impact counterfactual's --measure replay.
here = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(os.path.join(here, "standin.json"), encoding="utf-8"))
with open(os.path.join(here, "SPAWNED_dcf_engine.py.txt"), "a", encoding="utf-8") as f:
    f.write(" ".join(sys.argv[1:]) + "\n")
a = sys.argv
base = float(a[a.index("--base-oe-ps") + 1]) if "--base-oe-ps" in a else cfg["base"]
print(json.dumps({"base_oe_per_share": base, "implied_irr_weighted": cfg["irr"], "data_gap": []}))
'''


def _scored(n, j, ttm=None, prior_registry=None):
    """make_score on a fresh folder with counterfactual stand-ins (the applied override's impact replay runs: the
    engine's --measure replay returns the record's base); the Run is returned closed with its outputs read."""
    r = Run(n, j)
    try:
        with open(os.path.join(r.sysdir, "dcf_engine.py"), "w", encoding="utf-8") as f:
            f.write(ENGINE_STANDIN)
        with open(os.path.join(r.sysdir, "ttm.py"), "w", encoding="utf-8") as f:
            f.write(TTM_LEG_STANDIN)
        with open(os.path.join(r.sysdir, "standin.json"), "w", encoding="utf-8") as f:
            json.dump({"ttm": ttm or {}, "irr": 0.17, "base": n.get("base_oe_per_share"), "ttm_builds_without": True}, f)
        if ttm is not None:
            with open(os.path.join(r.folder, "ttm.json"), "w", encoding="utf-8") as f:
                json.dump(ttm, f)
        if prior_registry is not None:
            with open(r.registry, "w", encoding="utf-8") as f:
                json.dump(prior_registry, f, indent=1)
        r.run()
        r.result = dict(r.state(), score=r.score() if r.rc == 0 else None, key=r.key() if r.rc == 0 else None,
                        entries=r.entries(), spawned=r.spawned())
    finally:
        r.close()
    return r


def _refused(r, *needles):
    assert r.rc == 1 and "REFUSED" in r.err, (r.rc, r.out[-400:], r.err[-1200:])
    for s in needles:
        assert s in r.err, f"{s!r} not in: {r.err[-1500:]}"
    assert not r.result["key_exists"], "a refusal wrote key_numbers.md"
    return r


def _ok(r):
    assert r.rc == 0, f"make_score refused: {r.err[-1500:]}"
    return r


# ===========================================================================
# M1 — the capex-basis line names capitalized software
# ===========================================================================
def test_capex_basis_line_names_capitalized_software():
    """M1: a 5.7 record whose capex_provenance names software for a year prints "…, of which capitalized software $X"
    inside the capex-basis line (CSV branch: capex_intangibles x software / intangibles; provenance branch: the
    per-tag filed figures); a year without software keeps the 5.5 text exactly."""
    prov = copy.deepcopy(JK_PROV)
    prov["2026-06-30"] = {"ppe_source": "rollup", "ppe": {PRIMARY: 67103000}, "ppe_unit": "USD",
                          "intangibles": {PTDS: 184243000, PTAS: 4108000}, "intangibles_unit": "USD", "dropped": [],
                          "filed": {}, "software": {PTDS: 184243000, PTAS: 4108000}}
    prov["2025-06-30"].pop("software")
    prov["2025-06-30"]["intangibles"] = {INTANG: 177808000}
    tag = f"{PRIMARY}+{PTDS}+{PTAS}"
    rows = [_csv_row("2024-06-30", 232423000, "rollup", tag, 58118000, 174305000),
            _csv_row("2025-06-30", 231166000, "rollup", f"{PRIMARY}+{INTANG}", 53358000, 177808000),
            _csv_row("2026-06-30", 255454000, "rollup", tag, 67103000, 188351000)]
    n = _numbers(capex_provenance=prov)
    key = _ok(_with(n, csv_rows=rows)).result["key"]
    assert (f"- Capex basis FY2026 (2026-06-30): $255.5M — rollup: {tag} (PP&E $67.1M + intangibles $188.4M, of which "
            "capitalized software $188.4M)") in key, key
    assert (f"- Capex basis FY2025 (2025-06-30): $231.2M — rollup: {PRIMARY}+{INTANG} (PP&E $53.4M + intangibles "
            "$177.8M)\n") in key, key
    key = _ok(_with(n)).result["key"]   # no CSV: the provenance branch prints the filed figures per tag
    assert (f"- Capex basis FY2026 (2026-06-30): rollup: {PRIMARY} $67.1M + {PTDS} $184.2M + {PTAS} $4.1M; of which "
            f"capitalized software: {PTDS} $184.2M + {PTAS} $4.1M") in key, key


# ===========================================================================
# M2 / M3 — a capex override beside filed capitalized software
# ===========================================================================
def test_override_year_with_filed_software_needs_declaration():
    """M2: the override fills FY2026 while the filing reports 188,351,000 of capitalized software the engine did not
    add on top (an override is the TOTAL line): refused, naming the year and the figure, and saying the declaration
    is required either way."""
    n = _jk_record(67103000)
    _refused(_scored(n, _judgment(n, capex_override=_ov(67103000))),
             "capex_override 67,103,000 fills FY2026 (2026-06-30): 188,351,000 (PaymentsToAcquireSoftware, "
             "PaymentsToDevelopSoftware)", "The declaration is required either way", "software_included: true")


def test_raised_override_still_needs_the_declaration():
    """M2b: raising the figure to the total (PP&E + software, 255,454,000) without the declaration is still refused —
    the record still reads override_present beside filed software; with software_included: true it scores, and the
    capex field's registry entry carries the declaration."""
    n = _jk_record(255454000)
    _refused(_scored(n, _judgment(n, capex_override=_ov(255454000))), "fills FY2026 (2026-06-30): 188,351,000")
    r = _ok(_scored(n, _judgment(n, capex_override=_ov(255454000, software_included=True))))
    ent = [e for e in r.result["entries"] if e.get("field") == "capex"]
    assert len(ent) == 1 and ent[0]["software_included"] is True, ent


def test_software_included_declared_scores():
    """M3: the declaration's shape — a bool on capex_override only."""
    n = _jk_record(255454000)
    _refused(_with(n, _judgment(n, capex_override=_ov(255454000, software_included="yes"))),
             "capex_override.software_included must be true or false")
    j = _judgment(n, capex_override=_ov(255454000, software_included=True),
                  sbc_override={"value": 1e6, "kind": "filing", "source": "s", "reason": "r", "software_included": True})
    _refused(_with(n, j), "sbc_override.software_included is not allowed — only capex_override carries it")


def test_declared_override_smaller_than_the_filed_software_is_refused():
    """M3b: with software_included: true the override must be at least the filed intangible leg it claims to include
    — JKHY's PP&E-only 67,103,000 beside 188,351,000 of filed software is refused even when declared; 255,454,000
    and exactly 188,351,000 score; 188,350,999 is refused."""
    n = _jk_record(67103000)
    _refused(_scored(n, _judgment(n, capex_override=_ov(67103000, software_included=True))),
             "declares software_included: true", "FY2026 (2026-06-30): the override is 67,103,000 USD against "
             "188,351,000 USD of filed intangible purchases and capitalized software", "can never be smaller")
    for v, ok in ((255454000, True), (188351000, True), (188350999, False)):
        n = _jk_record(v)
        r = _scored(n, _judgment(n, capex_override=_ov(v, software_included=True)))
        if ok:
            _ok(r)
        else:
            _refused(r, f"the override is {v:,.0f} USD against 188,351,000 USD")


def _eur_record(value, basis, rates=None, leg_fx=None, currency=None):
    prov = {"2023-12-31": {"ppe_source": "rollup", "ppe": {}, "intangibles": {}, "dropped": [], "filed": {}},
            "2024-12-31": {"ppe_source": "rollup", "ppe": {}, "intangibles": {}, "dropped": [], "filed": {}},
            "2025-12-31": {"ppe_source": "override", "ppe": {}, "ppe_unit": None, "intangibles": {},
                           "intangibles_unit": None, "dropped": [], "filed": {},
                           "intangibles_not_added": "override_present", "intangibles_filed_unit": "EUR",
                           "intangibles_filed": {IFRS_INTANG: 203000000, DEV: 263000000}}}
    if leg_fx:
        prov["2025-12-31"]["intangibles_fx"] = leg_fx
    fx = {"from_currency": "EUR", "to_currency": "USD", "rates": dict(rates or {}),
          "rates_by_currency": {"EUR": dict(rates)} if rates else {}, "converted_fields": ["ocf"],
          "overrides_usd_verbatim": {"capex": basis} if basis == "declared_usd" else {}}
    o = _ov(value, **({"currency": currency} if currency else {}))
    n = _numbers(capex_provenance=prov, data_gap=["capex"], data_gap_uncovered=[], fx_conversion=fx,
                 override_checks={"capex": {"value": float(value), "last_filed_value": 4e8, "last_filed_unit": "EUR",
                                            "out_of_band": False, "ack_reason_present": False, "currency_basis": basis}},
                 overrides_applied=[dict(o, field="capex", value=float(value), periods_filled=["2025-12-31"])])
    return n, o


def test_declared_override_is_compared_in_usd_on_the_engine_basis():
    """M3c: an EUR filer (PHG-like): FY2025's filed intangible leg is EUR 203M of intangible purchases + EUR 263M of
    capitalized development (DEV, R9's IFRS line) = USD 503,280,000 at the record's 1.08. A converted EUR 1,000M
    override with the declaration scores; EUR 400M (USD 432,000,000) is refused; a declared-USD 500,000,000 is
    refused; a rate the record lacks is refused as unverifiable — and (rebase A9) the leg's own fetched rate
    (capex_provenance intangibles_fx, never in rates_by_currency) is used when that table lacks it."""
    rates = {"2025-12-31": 1.08}
    n, o = _eur_record(1e9, "converted", rates)
    _ok(_scored(n, _judgment(n, capex_override=dict(o, software_included=True))))
    n, o = _eur_record(4e8, "converted", rates)
    _refused(_scored(n, _judgment(n, capex_override=dict(o, software_included=True))),
             "the override is 432,000,000 USD against 503,280,000 USD")
    n, o = _eur_record(5e8, "declared_usd", rates, currency="USD")
    _refused(_scored(n, _judgment(n, capex_override=dict(o, software_included=True))),
             "the override is 500,000,000 USD against 503,280,000 USD")
    n, o = _eur_record(1e9, "converted", None)
    _refused(_scored(n, _judgment(n, capex_override=dict(o, software_included=True))), "unverifiable")
    n, o = _eur_record(6e8, "declared_usd", None, leg_fx={"currency": "EUR", "rate": 1.08}, currency="USD")
    _ok(_scored(n, _judgment(n, capex_override=dict(o, software_included=True))))
    n, o = _eur_record(5e8, "declared_usd", None, leg_fx={"currency": "EUR", "rate": 1.08}, currency="USD")
    _refused(_scored(n, _judgment(n, capex_override=dict(o, software_included=True))), "503,280,000 USD")


def _ttm_leg(stamped=True, legs_filled=True, value=67103000):
    per = ["2026-07-01", "2026-09-30"]
    tt = {"ttm_oe_per_share": 2.0, "ttm_shares_diluted": 1e9,
          "inputs": {"capex": {"fy_period": ["2025-07-01", "2026-06-30"], "fy_tag": PRIMARY,
                               "ytd_prior_period": ["2025-07-01", "2025-09-30"], "ytd_prior_tag": PRIMARY,
                               "ytd_current_period": per, "ytd_current_tag": "OVERRIDE"}},
          "capex_components": {"fy": None, "ytd_prior": None, "ytd_current": {
              "ppe": None, "intangibles": 49000000.0, "intangibles_unit": "USD", "intangible_tags": [INTANG, PTDS],
              "intangibles_not_added": "override_present", "software": 48000000.0, "software_tags": [PTDS],
              "dropped": [], "provenance": f"{INTANG}+{PTDS}"}},
          "overrides_used": [{"field": "capex", "value": float(value), "kind": "filing", "source": SOURCE,
                              "legs_filled": ({"ytd_current": {"period": per, "amount": value * 92 / 365.0, "days": 92,
                                                               "prorated": True}} if legs_filled else {})}],
          "warnings": []}
    if stamped:
        tt["engine_release"] = E.ENGINE_RELEASE
    return tt


def test_ttm_leg_override_beside_filed_software_is_refused():
    """M2c: no FY year has software beside the override, but ttm.json's current-YTD leg is override-filled beside
    48,000,000 of filed software: refused without the declaration; with it, the override as ttm.py filled the leg
    (67,103,000 x 92 / 365 = 16,913,633; the design's 16,913,060 was an arithmetic slip) is below the leg's
    49,000,000 of intangibles — refused; 255,454,000 (64,388,405 for the leg) scores. Without legs_filled the leg is
    prorated as ttm.py does."""
    prov = {"2024-06-30": {"intangibles": {PTDS: 1}}, "2025-06-30": {"intangibles": {PTDS: 1}},
            "2026-06-30": {"intangibles": {PTDS: 1}}}
    n = _numbers(capex_provenance=prov)
    _refused(_scored(n, _judgment(n, capex_override=_ov(67103000)), ttm=_ttm_leg()),
             "fills TTM ytd_current leg (2026-07-01..2026-09-30): 48,000,000 (PaymentsToDevelopSoftware)")
    _refused(_scored(n, _judgment(n, capex_override=_ov(67103000, software_included=True)), ttm=_ttm_leg()),
             "TTM ytd_current leg (2026-07-01..2026-09-30): the override is 16,913,633 USD against 49,000,000 USD")
    _ok(_scored(n, _judgment(n, capex_override=_ov(255454000, software_included=True)), ttm=_ttm_leg(value=255454000)))
    _refused(_scored(n, _judgment(n, capex_override=_ov(67103000, software_included=True)),
                     ttm=_ttm_leg(legs_filled=False)), "the override is 16,913,633 USD")


def test_unstamped_ttm_override_leg_cannot_be_checked():
    """M2d (rebase A6): a ttm.json with no 5.7 stamp records no capitalized software, so an override-filled TTM leg
    in it cannot be checked — refused (rerun ttm.py), never passed silently; the same file with no override-filled
    leg is no concern of this check."""
    prov = {"2026-06-30": {"intangibles": {PTDS: 1}}}
    n = _numbers(capex_provenance=prov)
    tt = _ttm_leg(stamped=False)
    for leg in tt["capex_components"].values():
        if isinstance(leg, dict):
            leg.pop("software", None)
            leg.pop("software_tags", None)
    _refused(_scored(n, _judgment(n, capex_override=_ov(255454000, software_included=True)), ttm=tt),
             "fills TTM ytd_current leg (2026-07-01..2026-09-30) of a ttm.json stamped engine_release none (pre-5.7)",
             "rerun ttm.py with the current engine")
    tt["inputs"]["capex"]["ytd_current_tag"] = PRIMARY
    _ok(_scored(n, _judgment(n, capex_override=_ov(255454000, software_included=True)), ttm=tt))


def test_pre57_record_rebuilds_unchanged():
    """M4 (pin of the release gate): a 5.6.0 record with the M2 override-year provenance (a pre-5.7 engine records no
    `software` map) and the M2c ttm.json, unstamped, rebuilds with no refusal and no software text — the rules bind
    5.7 runs only."""
    prov = copy.deepcopy(JK_PROV)
    for p in prov.values():
        p.pop("software", None)
        p.pop("intangibles_filed_unit", None)
    n = _jk_record(67103000, release="5.6.0", prov=prov)
    r = _ok(_scored(n, _judgment(n, capex_override=_ov(67103000)), ttm=_ttm_leg(stamped=False)))
    assert "capitalized software" not in r.result["key"], r.result["key"]


# ===========================================================================
# M5 — CAPEX_UNLISTED_COMPONENT needs capex_unlisted_ack (R8)
# ===========================================================================
UNLISTED = (f"CAPEX_UNLISTED_COMPONENT:{ME} — FY2024 819,150,000 (accession 0001492691-25-000012) vs the whole component "
            "capex leg 438,000 (PaymentsToAcquireOtherProductiveAssets), FY2025 795,392,000 (accession "
            "0001492691-26-000010) vs the whole component capex leg 1,066,000 (PaymentsToAcquireOtherProductiveAssets): a "
            "capex-like cash-flow tag on no engine capex list exceeds the component leg in the same filing")
ACK = "lease buy-outs of $795.4M in FY2025, not capex (test)"


def test_unlisted_capex_component_is_refused():
    """M5: a 5.7 record flagged CAPEX_UNLISTED_COMPONENT:<tag> is refused, naming the tag, NEEDS_MAIN_AGENT: capex and
    capex_unlisted_ack; a capex override does not release it (an override never replaces a filed leg); an ack with a
    figure scores and is recorded as a capex_unlisted_ack registry event {tag, reason, value} that keeps its first
    date on a re-run; an ack reason without a figure is refused by validation; a 5.6.0 record is not refused."""
    n = _numbers(fragility_flags=[UNLISTED])
    _refused(_with(n, _judgment(n)), "CAPEX_UNLISTED_COMPONENT", ME, "NEEDS_MAIN_AGENT: capex", "capex_unlisted_ack")
    _refused(_with(n, _judgment(n, capex_override=_ov(796458000))), "CAPEX_UNLISTED_COMPONENT", "capex_unlisted_ack")
    prior = {"entries": [{"ticker": T, "event": "capex_unlisted_ack", "date": "2026-10-01", "tag": ME, "reason": ACK,
                          "value": 795392000.0},
                         {"ticker": "OTHR", "event": "capex_unlisted_ack", "date": "2026-09-30", "tag": ME,
                          "reason": "other 1", "value": None}]}
    r = _ok(_scored(n, _judgment(n, capex_unlisted_ack={ME: ACK}), prior_registry=prior))
    ev = [e for e in r.result["entries"] if e.get("event") == "capex_unlisted_ack" and e["ticker"] == T]
    assert ev == [{"ticker": T, "event": "capex_unlisted_ack", "date": "2026-10-01", "tag": ME, "reason": ACK,
                   "value": 795392000.0}], ev
    assert prior["entries"][1] in r.result["entries"]
    r = _ok(_scored(n, _judgment(n, capex_unlisted_ack={ME: ACK})))   # a first ack is dated today
    ev = [e for e in r.result["entries"] if e.get("event") == "capex_unlisted_ack"]
    assert len(ev) == 1 and ev[0]["date"] > "2026-10-01" and ev[0]["value"] == 795392000.0, ev
    _refused(_with(n, _judgment(n, capex_unlisted_ack={ME: "lease buy-outs, not capex"})),
             "capex_unlisted_ack.PaymentsToAcquireMachineryAndEquipment must say why", "carry the figure")
    _refused(_with(n, _judgment(n, capex_unlisted_ack={})), "capex_unlisted_ack must be a non-empty object")
    old = _numbers(release="5.6.0", fragility_flags=[UNLISTED])
    _ok(_with(old, _judgment(old)))
    assert M.capex_unlisted_acks(n, {"capex_unlisted_ack": {ME: ACK}}) == [{"tag": ME, "reason": ACK, "value": 795392000.0}]
    assert M._capex_events(T, "2026-10-21", None, n) == []


def test_unlisted_overridden_variant_is_not_refused():
    """M5b (pin of the prefix rule): the _OVERRIDDEN variant (an unread capex-like tag in a year with no PP&E leg,
    which an override fills) is never refused — the refusal matches 'CAPEX_UNLISTED_COMPONENT:' only."""
    n = _numbers(fragility_flags=[f"CAPEX_UNLISTED_COMPONENT_OVERRIDDEN:{ME} — FY2026 408,100,000 (accession x; filled by "
                                  "capex_override): a capex-like cash-flow tag on no engine capex list"])
    r = _ok(_with(n, _judgment(n)))
    assert not [e for e in r.result["entries"] if e.get("event") == "capex_unlisted_ack"]


# ===========================================================================
# M6 — a 5.7 run whose basis read ttm.json needs a 5.7-stamped ttm.json (rebase A5 / A6)
# ===========================================================================
TTM_PIN = 3.0


def _tt(stamp=None):
    t = {"ttm_oe_per_share": TTM_PIN, "ttm_shares_diluted": 1e9, "ttm_oe_total": 3e9, "ttm_ocf": 4e9,
         "ttm_capex": 8e8, "ttm_sbc": 2e8, "fy_end": "2025-12-31", "ytd_end": "2026-06-30",
         "inputs": {"ocf": {"fy_period": ["2025-01-01", "2025-12-31"], "ytd_prior_period": ["2025-01-01", "2025-06-30"],
                            "ytd_current_period": ["2026-01-01", "2026-06-30"]}},
         "capex_components": None, "overrides_used": [], "warnings": []}
    if stamp is not None:
        t["engine_release"] = stamp
    return t


def _pin_record(kind, tt, release=CUR):
    """kind: 'ttm' (--ttm), 'undeclared' (--base-oe-ps = ttm.json's figure), 'window_ttm' / 'window_fy' (a declared
    plain pin with basis_window), 'median'. ttm_inputs as the engine records it (ttm_inputs_record when the basis
    reads ttm.json, null otherwise)."""
    n = _numbers(release=release)
    if kind == "ttm":
        n.update(base_oe_per_share=TTM_PIN, base_source="ttm_json", ttm_inputs=E.ttm_inputs_record(tt))
        n["inputs"] = dict(n["inputs"], base_oe_ps_arg=TTM_PIN, base_pin_source="ttm_json")
    elif kind == "undeclared":
        n.update(base_oe_per_share=TTM_PIN, base_source="agent_supplied_ttm_override", ttm_inputs=E.ttm_inputs_record(tt))
        n["inputs"] = dict(n["inputs"], base_oe_ps_arg=TTM_PIN, base_pin_source="base_oe_ps_arg")
    elif kind in ("window_ttm", "window_fy"):
        bw = ({"window": "ttm", "ytd_current_period": ["2026-01-01", "2026-06-30"]} if kind == "window_ttm"
              else {"window": "fy"})
        n.update(base_oe_per_share=2.5, base_source="agent_supplied_ttm_override",
                 ttm_inputs=E.ttm_inputs_record(tt) if kind == "window_ttm" else None)
        n["inputs"] = dict(n["inputs"], base_oe_ps_arg=2.5, base_pin_source="base_oe_ps_arg", base_basis_window=bw)
    else:
        n.update(ttm_inputs=None)
    return n


def _pin_judgment(n):
    bw = (n.get("inputs") or {}).get("base_basis_window")
    if bw is None:
        return _judgment(n)
    return _judgment(n, base_override={"value": 2.5, "source": "ttm.json TTM OCF less capex and SBC over 1.2B units "
                                                             "(test)", "reason": "per-unit base (test)",
                                       "basis_window": bw})


def _pin_run(kind, tt, release=CUR):
    n = _pin_record(kind, tt, release)
    r = Run(n, _pin_judgment(n))
    try:
        with open(os.path.join(r.folder, "ttm.json"), "w", encoding="utf-8") as f:
            json.dump(tt, f)
        r.run()
        r.result = dict(r.state())
    finally:
        r.close()
    return r


def test_pre57_ttm_json_is_refused_on_a_57_run():
    """M6: (a) a --ttm record on an unstamped ttm.json is refused ("rerun ttm.py with the current engine");
    (b) stamped 5.6.0 refused; (c) 5.7.0 scores; (d) a declared basis_window "ttm" pin on an unstamped ttm.json and
    (e) an undeclared --base-oe-ps pin equal to ttm.json's figure are refused; (f) a median record (ttm_inputs null)
    beside an unstamped ttm.json and (f2) a basis_window "fy" pin score; (g) a 5.6.0 record is never refused."""
    need = ("ttm.json predates engine 5.7", "rerun ttm.py with the current engine")
    _refused(_pin_run("ttm", _tt()), *need, "stamped engine_release none (pre-5.7)")
    _refused(_pin_run("ttm", _tt("5.6.0")), *need, "stamped engine_release 5.6.0")
    _ok(_pin_run("ttm", _tt("5.7.0")))
    _refused(_pin_run("window_ttm", _tt()), *need)
    _refused(_pin_run("undeclared", _tt()), *need)
    _ok(_pin_run("median", _tt()))
    _ok(_pin_run("window_fy", _tt()))
    _ok(_pin_run("ttm", _tt(), release="5.6.0"))
    # a ttm.json regenerated (re-stamped) after the run is TTM_CHANGED first — the remedy is to rerun the engine
    n = _pin_record("ttm", _tt())
    r = Run(n, _judgment(n))
    try:
        with open(os.path.join(r.folder, "ttm.json"), "w", encoding="utf-8") as f:
            json.dump(_tt(E.ENGINE_RELEASE), f)
        r.run()
        r.result = dict(r.state())
        _refused(r, "ttm.json changed after the engine run")
    finally:
        r.close()


def test_rulings57_stamps_a_hand_written_ttm_json():
    """A8: the G16 helper stamps a test's hand-written ttm.json with the current release and, for a record whose basis
    read it, re-derives ttm_inputs (and the content hash) — so a pre-existing test's current-release TTM record is
    a 5.7 run on a 5.7 ttm.json; a median record (ttm_inputs null) is left as it is."""
    tt = _tt()
    n = dict(_pin_record("ttm", tt), content_hash="x")
    assert rulings57.add_ttm_engine_release(tt, n) is tt and tt["engine_release"] == E.ENGINE_RELEASE
    assert n["ttm_inputs"] == E.ttm_inputs_record(tt) and n["ttm_inputs"]["ttm_engine_release"] == E.ENGINE_RELEASE
    assert n["content_hash"] == rulings57.content_hash(n)
    m = _pin_record("median", _tt())
    m0 = copy.deepcopy(m)
    rulings57.add_ttm_engine_release(_tt(), m)
    assert m == m0


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
