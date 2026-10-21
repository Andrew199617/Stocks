#!/usr/bin/env python3
"""ttm.py --interim / --interim-draft — the declared 6-K interim bridge (engine 5.7, Andrew's ruling R2a, 2026-10-19;
design 04 A.3-A.4, tests 23-28, rebase L4 amendments 10, 11, 23). Run: python _system/tests/test_ttm_interim.py (or
python -m pytest). Offline: a synthetic 20-F filer (MICC's FY2025 / H1 legs, EUR) in a temp STOCKS_BASE through
engine55_harness.run_ttm; EDGAR submissions, the 6-K instance (fixtures/instance/tiny_6k.xml) and the ECB rates are
patched. Every test fails on the L0 scaffold (e22e814: --interim is ignored and the us-gaap 10-Q path exits 3).

23. --interim builds ttm.json from the declaration and the engine's FY leg: A.4's shape with the 10-Q path's compat
    keys, per-period rates, the 6-K's XBRL verifying the filed legs, the design's MICC figures.
24. a declared value the 6-K's XBRL contradicts (IB-XBRL1); an estimate where the 6-K files the figure (IB-XBRL2).
25. a prior leg cited from another report (IB-SRC2); the accession is a 10-Q (IB-SRC1).
26. a 10-K filer (IB-FORM); engine output from another release (IB-ENG); RTO's shape — the FY leg filed in USD, the
    legs declared in GBP (IB-UNIT).
27. a fetch failure exits 4 (ECB rate, submissions, the instance); DCF_TTM_NO_WRITE writes nothing; an FY sbc_tag
    OVERRIDE records override_counterfactual.
28. without --interim the 10-Q path is untouched (no `basis`, the interim code never runs) and --interim on a 10-K
    fixture refuses instead of printing a 10-Q TTM.
T-a (amendment 10): ttm_inputs_record of a declared ttm.json moves with any rate or leg and not with provenance /
    like-for-like text; an engine --ttm run on it records exactly that ttm_inputs and, with an acquired-IPR&D charge,
    the TTM's share denominator ("ttm.json ttm_shares_diluted").
T-c (amendment 11, default Q8): an acquired-IPR&D charge the 6-K files for the current interim refuses (IB-IPRD);
    none -> "xbrl_instance: none"; a report without XBRL -> "not_scanned" and a warning.
Also --interim-draft prints a draft from the 6-K's XBRL and writes nothing.
"""
import copy
import csv
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
for _p in (HERE, SYS):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import engine55_harness as H  # noqa: E402

E = H._shared_engine()
TICKER, CIK = "SYF", 999003
ACC = "0001104659-26-088404"
EXAMPLE = os.path.join(SYS, "examples", "interim_bridge.example.json")
SIX_K = os.path.join(HERE, "fixtures", "instance", "tiny_6k.xml")
FY_RATE, RATES = 1.175, {"2025-06-30": 1.172, "2026-06-30": 1.1394}
IF = "ifrs-full"
OCF_TAG, PPE_TAG = "CashFlowsFromUsedInOperatingActivities", "PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities"
INT_TAG, SBC_TAG = "PurchaseOfIntangibleAssetsClassifiedAsInvestingActivities", "AdjustmentsForSharebasedPayments"
FY_EUR = {"ocf": 483e6, "capex_ppe": 357e6, "capex_intangibles": 3e6, "sbc": 35e6}
IPRD = "ResearchAndDevelopmentAssetAcquiredOtherThanThroughBusinessCombinationWrittenOff"


def decl():
    with open(EXAMPLE, encoding="utf-8") as f:
        return json.load(f)["interim_bridge"]


def _fy(tag, unit, val, year=2025, form="20-F"):
    return {"start": f"{year}-01-01", "end": f"{year}-12-31", "val": val, "accn": f"0009990030-{year % 100 + 1}-000010",
            "fy": year, "fp": "FY", "form": form, "filed": f"{year + 1}-03-18"}


def companyfacts(unit="EUR"):
    f = {"cik": CIK, "entityName": "SYNTH FOREIGN (test)", "facts": {IF: {}}}
    for tag, key in ((OCF_TAG, "ocf"), (PPE_TAG, "capex_ppe"), (INT_TAG, "capex_intangibles"), (SBC_TAG, "sbc")):
        f["facts"][IF][tag] = {"units": {unit: [_fy(tag, unit, FY_EUR[key] * 0.9, 2024), _fy(tag, unit, FY_EUR[key])]}}
    return f


def engine_record(release=None, form="20-F", unit="EUR", **kw):
    n = {"ticker": TICKER, "cik": CIK, "engine_version": 5, "engine_release": release or E.ENGINE_RELEASE,
         "as_of": "2026-10-21", "filer_annual_form": form, "latest_period_end": "2025-12-31",
         "ads_ratio": {"ratio": 1.0, "source": "test 20-F cover", "reason": "ordinary shares trade directly"},
         "fx_conversion": ({"from_currency": unit, "to_currency": "USD", "rates_by_currency": {unit: {"2025-12-31": FY_RATE}}}
                           if unit != "USD" else None),
         "capex_provenance": {"2025-12-31": {"ppe_source": "rollup", "ppe": {PPE_TAG: FY_EUR["capex_ppe"]}, "ppe_unit": unit,
                                             "intangibles": {INT_TAG: FY_EUR["capex_intangibles"]}, "intangibles_unit": unit,
                                             "dropped": [], "filed": {}}},
         "sbc_provenance": {}, "override_checks": {}, "fragility_flags": ["STALE_FY: latest fiscal year ended 10 months ago"]}
    n.update(kw)
    n["content_hash"] = E._content_hash(n)
    return n


def csv_rows(rate=FY_RATE, **kw):
    cols = ["period_end", "fy_label", "ocf", "ocf_tag", "capex", "capex_assumed_zero", "capex_tag", "sbc_tag", "sbc",
            "shares_diluted", "shares_tag", "capex_ppe", "capex_intangibles", "capex_source"]
    rows = []
    for y, g in ((2024, 0.9), (2025, 1.0)):
        r = {"period_end": f"{y}-12-31", "fy_label": str(y), "ocf": FY_EUR["ocf"] * g * rate, "ocf_tag": OCF_TAG,
             "capex": (FY_EUR["capex_ppe"] + FY_EUR["capex_intangibles"]) * g * rate, "capex_assumed_zero": "False",
             "capex_tag": f"{PPE_TAG}+{INT_TAG}", "sbc_tag": SBC_TAG, "sbc": FY_EUR["sbc"] * g * rate,
             "shares_diluted": 615600000, "shares_tag": "AdjustedWeightedAverageShares",
             "capex_ppe": FY_EUR["capex_ppe"] * g * rate, "capex_intangibles": FY_EUR["capex_intangibles"] * g * rate,
             "capex_source": "rollup"}
        rows.append(r)
    rows[-1].update(kw)
    return cols, rows


def submissions(form="6-K", is_xbrl=1, acc=ACC):
    return {"filings": {"recent": {"form": [form, "20-F"], "accessionNumber": [acc, "0009990030-26-000010"],
                                   "filingDate": ["2026-07-30", "2026-03-18"], "reportDate": ["2026-06-30", "2025-12-31"],
                                   "primaryDocument": ["micc-20260630x6k.htm", "syf-20251231.htm"],
                                   "isXBRL": [is_xbrl, 1]}}}


def six_k(extra=""):
    with open(SIX_K, "rb") as f:
        data = f.read()
    return data.replace(b"</xbrli:xbrl>", extra.encode("utf-8") + b"</xbrli:xbrl>") if extra else data


class Folder:
    """A temp STOCKS_BASE with the synthetic filer's engine record, CSV and judgment.json."""

    def __init__(self, d=None, n=None, rows=None, judgment=None, facts=None):
        self.facts = facts or companyfacts()
        self.fixture = {"ticker": TICKER, "cik": CIK, "entityName": self.facts["entityName"], "facts": self.facts,
                        "universe_row": {"ticker": TICKER, "name": "Synth Foreign", "sector": "", "price": "20",
                                         "market_cap": "", "cik": str(CIK)}}
        self.base = H.make_base(self.fixture, None, None, copy_repo_files=False)
        self.folder = os.path.join(self.base, TICKER)
        n = n or engine_record()
        cols, rs = rows or csv_rows()
        j = {"interim_bridge": d if d is not None else decl(),
             "ads_ratio": {"ratio": 1.0, "source": "test 20-F cover", "reason": "ordinary shares trade directly"}}
        if judgment:
            j.update(judgment)
        self._write("dcf_numbers.json", n)
        self._write("judgment.json", j)
        with open(os.path.join(self.folder, "financials_history.csv"), "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(rs)

    def _write(self, name, obj):
        with open(os.path.join(self.folder, name), "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=1, ensure_ascii=False)

    def run(self, args=("--interim",), sub=None, instance=None, rates=None, env=None, calls=None):
        sub = sub if sub is not None else submissions()
        inst = instance if instance is not None else six_k()
        rates = RATES if rates is None else rates

        def patch(T):
            sys.argv.extend(args)
            T.fetch_submissions = sub if callable(sub) else (lambda cik: sub)
            T.fetch_report_instance = inst if callable(inst) else (lambda cik, filing: (inst, "https://www.sec.gov/x/micc-20260630x6k_htm.xml"))
            T.fx_rate = rates if callable(rates) else (lambda ccy, date: rates.get(date) if ccy == "EUR" else None)
            if calls is not None:
                calls.append(T)
        return H.run_ttm(TICKER, base=self.base, fixture=self.fixture, patch=patch, keep_base=True, env=env)

    def written(self):
        p = os.path.join(self.folder, "ttm.json")
        return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None

    def close(self):
        shutil.rmtree(self.base, ignore_errors=True)


def _once(**kw):
    f = Folder(**{k: v for k, v in kw.items() if k in ("d", "n", "rows", "judgment", "facts")})
    try:
        out = f.run(**{k: v for k, v in kw.items() if k in ("args", "sub", "instance", "rates", "env", "calls")})
        out["written"] = f.written()
        return out
    finally:
        f.close()


def _leg(d, field, name, **kw):
    d = copy.deepcopy(d)
    d["legs"][field][name].update(kw)
    return d


def _refused(out, *needles, code=3):
    assert out["exit"] == code, (out["exit"], out["stderr"][-1500:], out["stdout"][-500:])
    for s in needles:
        assert s in out["stderr"], (s, out["stderr"])
    assert out["written"] is None, "a refused run wrote ttm.json"


# ---------------------------------------------------------------------------
# 23. the record
# ---------------------------------------------------------------------------
def test_interim_builds_ttm_json():
    out = _once()
    assert out["exit"] == 0, out["stderr"][-2000:]
    t = out["ttm"]
    assert out["written"] == t
    assert t["basis"] == "declared_interim" and t["engine_release"] == E.ENGINE_RELEASE
    assert t["built_by"] == f"ttm.py --interim (release {E.ENGINE_RELEASE})"
    import interim_bridge as IB
    assert t["declaration_hash"] == IB.declaration_hash(decl())
    assert t["engine_record"]["engine_release"] == E.ENGINE_RELEASE and t["engine_record"]["latest_period_end"] == "2025-12-31"
    assert (t["fy_end"], t["ytd_end"], t["currency"]) == ("2025-12-31", "2026-06-30", "EUR")
    assert t["periods"] == {"fy": ["2025-01-01", "2025-12-31"], "prior_interim": ["2025-01-01", "2025-06-30"],
                            "current_interim": ["2026-01-01", "2026-06-30"]}
    assert t["fx"]["rates_used"] == {"fy": 1.175, "prior_interim": 1.172, "current_interim": 1.1394}
    assert t["fx"]["prior_interim"]["declared"] == 1.172 and t["fx"]["basis"] == "ecb_period_end"
    assert abs(t["ttm_ocf"] - 858189600) < 1e-3 and abs(t["ttm_capex"] - 454522302) < 1
    assert abs(t["ttm_sbc"] - 39366200) < 1e-3 and abs(t["ttm_oe_total"] - 364301098) < 1
    assert abs(t["ttm_oe_total_local"] - 320e6) < 1e-3 and t["ttm_shares_diluted"] == 617000000
    assert abs(t["ttm_oe_per_share"] - 0.590439) < 1e-6 and t["ads_ratio"] == 1.0
    legs = t["legs"]
    for f in ("ocf", "capex_ppe", "sbc"):
        for name in ("prior_interim", "current_interim"):
            assert legs[f][name]["verified"] == "xbrl_instance" and legs[f][name]["kind"] == "filing", (f, name, legs[f][name])
    assert legs["ocf"]["current_interim"]["xbrl_tag"] == OCF_TAG and legs["ocf"]["current_interim"]["xbrl_value"] == 539000000
    assert legs["capex_intangibles"]["prior_interim"] == {"local": 1487671, "usd": 1487671 * 1.172, "kind": "estimate",
                                                          "verified": "estimate", "method": "fy_prorated"}
    assert legs["ocf"]["fy"]["unit"] == "EUR" and abs(legs["ocf"]["fy"]["local"] - 483e6) < 1e-3
    assert t["shares"]["current_interim"]["verified"] == "xbrl_instance"
    assert t["shares"]["current_interim"]["xbrl_tag"] == "AdjustedWeightedAverageShares"   # the basic count never verifies
    assert t["estimate_legs"] == ["capex_intangibles.prior_interim", "capex_intangibles.current_interim"]
    assert t["xbrl_verified_legs"] == sorted(["capex_ppe.current_interim", "capex_ppe.prior_interim", "ocf.current_interim",
                                              "ocf.prior_interim", "sbc.current_interim", "sbc.prior_interim",
                                              "shares_diluted.current_interim"])
    assert t["unverified_legs"] == [] and t["iprd_interim_scan"] == "xbrl_instance: none"
    assert t["report"]["accession"] == ACC and t["report"]["is_xbrl"] is True and t["report"]["report_date"] == "2026-06-30"
    assert len(t["provenance"]) == 7 and t["provenance"][0]["snippet"].startswith("Income tax paid")
    assert t["override_counterfactual"] is None and t["overrides_used"] == []
    # the 10-Q path's compat keys (the engine's --ttm / Tier F / IPR&D readers, the site's TTM card)
    ins = t["inputs"]
    assert ins["ocf"]["ytd_current_period"] == ["2026-01-01", "2026-06-30"] and ins["ocf"]["fy_tag"] == "ENGINE_FY"
    assert ins["ocf"]["ytd_prior_tag"] == f"6-K {ACC}" and ins["ocf"]["ttm"] == t["ttm_ocf"]
    assert abs(ins["capex"]["ttm"] - t["ttm_capex"]) < 1e-6 and ins["shares_diluted"]["ytd_current"] == 617000000
    for k in ("capex_components", "split_adjustment"):
        assert t[k] is None, k
    for k in ("sbc_reconciled_legs", "capex_override_superseded_legs", "sbc_reconciliation_withdrawn_legs"):
        assert t[k] == {}, k
    rec = E.ttm_inputs_record(t)
    assert rec["ttm_oe_per_share"] == t["ttm_oe_per_share"] and rec["ytd_current_period"] == ["2026-01-01", "2026-06-30"]
    assert rec["ttm_shares_diluted"] == 617000000.0


# ---------------------------------------------------------------------------
# 24-26. refusals
# ---------------------------------------------------------------------------
def test_xbrl_mismatch_refuses():
    d = _leg(decl(), "ocf", "current_interim", value=538000000,
             snippet="Net cash flow from operating activities 538 276")
    _refused(_once(d=d), f"[IB-XBRL1] ocf.current_interim declares 538,000,000 but the report's XBRL files {OCF_TAG} = "
                         "539,000,000 for 2026-01-01..2026-06-30")


def test_estimate_on_a_filed_fact_refuses():
    d = _leg(decl(), "sbc", "current_interim", kind="estimate", method="fy_prorated", value=35e6 * 181 / 365)
    _refused(_once(d=d), f"[IB-XBRL2] sbc.current_interim is declared kind estimate but the report files {SBC_TAG} = "
                         "18,000,000 for 2026-01-01..2026-06-30 — declare it kind filing")


def test_prior_leg_from_another_report_refuses():
    d = copy.deepcopy(decl())
    d["legs"]["ocf"]["prior_interim"]["source"]["accession"] = "0001104659-25-070000"
    _refused(_once(d=d), "[IB-SRC2] ocf.prior_interim cites accession 0001104659-25-070000, not the report "
                         f"{ACC} — both interim legs come from the same report")


def test_10q_accession_refuses():
    _refused(_once(sub=submissions(form="10-Q")), f"[IB-SRC1] accession {ACC} is 10-Q, not a 6-K")
    _refused(_once(sub=submissions(acc="0001104659-26-000001")), f"[IB-SRC1] accession {ACC} not found in EDGAR submissions")


def test_10k_filer_refuses():
    _refused(_once(n=engine_record(form="10-K")), "[IB-FORM] --interim is for 20-F / 40-F filers")


def test_stale_engine_release_refuses():
    _refused(_once(n=engine_record(release="5.6.0")), f"[IB-ENG] dcf_numbers.json is from release 5.6.0, not "
                                                      f"{E.ENGINE_RELEASE}")
    n = engine_record()
    n["base_oe_per_share"] = 9.99            # edited after the run: the hash no longer verifies
    _refused(_once(n=n), "[IB-ENG] dcf_numbers.json content_hash does not verify")


def test_unit_mismatch_refuses():
    # RTO's shape: the FY leg is filed in USD (the issuer presents in USD), the interim legs are declared in GBP
    d = copy.deepcopy(decl())
    d["currency"] = "GBP"
    out = _once(d=d, n=engine_record(unit="USD"), rows=csv_rows(rate=1.0), facts=companyfacts("USD"))
    _refused(out, "[IB-UNIT] the engine's FY ocf for 2025-12-31 is filed in USD but the interim legs are declared in GBP")


def test_shape_and_missing_declaration_refuse():
    out = _once(judgment={"interim_bridge": None})
    _refused(out, "[IB-SHAPE] judgment.json declares no interim_bridge — --interim builds ttm.json only from a declared bridge")
    out = _once(d=_leg(decl(), "shares_diluted", "current_interim", value=0))
    _refused(out, "[IB-SHAPE] interim_bridge.legs.shares_diluted.current_interim.value: a share count must be > 0")


# ---------------------------------------------------------------------------
# 27. fetch failures, the no-write switch, the override counterfactual
# ---------------------------------------------------------------------------
def test_fetch_failure_exits_4():
    out = _once(rates={})
    _refused(out, "ttm.py --interim: cannot verify the interim bridge for SYF: the ECB EUR/USD reference rate for "
                  "2025-06-30 unavailable", code=4)

    def boom(*_a):
        raise RuntimeError("EDGAR 503")
    _refused(_once(sub=boom), "EDGAR submissions unavailable (EDGAR 503) — retry", code=4)
    _refused(_once(instance=boom), "the 6-K's XBRL instance unavailable (EDGAR 503) — retry", code=4)
    _refused(_once(instance=lambda cik, filing: (None, None)), "the 6-K's XBRL instance unavailable (EDGAR lists the "
                                                               "report as XBRL but its folder holds no instance)", code=4)


def test_declared_rate_off_by_more_than_half_a_percent_refuses():
    d = copy.deepcopy(decl())
    d["fx"]["current_interim"]["rate"] = 1.16
    _refused(_once(d=d), "[IB-FX3] interim_bridge.fx.current_interim.rate 1.16 is not the ECB reference rate 1.1394 for "
                         "2026-06-30")
    d = copy.deepcopy(decl())
    d["fx"]["fy"]["rate"] = 1.18
    _refused(_once(d=d), "[IB-FX2] interim_bridge.fx.fy.rate 1.18 is not the engine's FY rate 1.175")


def test_no_write_env():
    out = _once(env={"DCF_TTM_NO_WRITE": "1"})
    assert out["exit"] == 0 and out["ttm"]["basis"] == "declared_interim" and out["written"] is None


def test_override_counterfactual_recorded():
    n = engine_record(override_checks={"sbc": {"value": 35e6, "last_filed_value": None, "last_filed_unit": None,
                                               "out_of_band": True, "ack_reason_present": True,
                                               "currency_basis": "converted"}})
    out = _once(n=n, rows=csv_rows(sbc_tag="OVERRIDE"))
    assert out["exit"] == 0, out["stderr"][-1500:]
    t = out["ttm"]
    cf = t["override_counterfactual"]
    assert set(cf["fy_fields_override_filled"]) == {"sbc"} and abs(cf["fy_fields_override_filled"]["sbc"] - t["ttm_sbc"]) < 1e-6
    assert abs(cf["ttm_oe_total_zero_fill"] - (t["ttm_oe_total"] + t["ttm_sbc"])) < 1e-6
    assert abs(cf["base_oe_per_share_zero_fill"] - cf["ttm_oe_total_zero_fill"] / 617000000) < 1e-12
    assert t["legs"]["sbc"]["fy"]["unit"] == "OVERRIDE" and t["legs"]["sbc"]["fy"]["local"] == 35e6


# ---------------------------------------------------------------------------
# 28. the 10-Q path
# ---------------------------------------------------------------------------
def test_plain_ttm_unchanged():
    from test_engine_55 import JLL_J
    for t, j in (("AR", {}), ("ELS", {}), ("JLL", JLL_J), ("DD", {})):
        fx = H.load_fixture(t)

        def stub(T):
            def boom(*_a, **_k):
                raise AssertionError("the interim code ran on the 10-Q path")
            T.interim_cli = T.interim_main = T.build_interim = boom
        plain = H.run_ttm(t, base=H.make_base(fx, j, None, copy_repo_files=False), fixture=fx, patch=stub)
        assert plain["exit"] == 0, (t, plain["stderr"][-500:])
        assert "basis" not in plain["ttm"] and "declaration_hash" not in plain["ttm"], t
        assert set(plain["ttm"]) == {"ticker", "cik", "entity", "fy_end", "ytd_end", "inputs", "ttm_ocf", "ttm_capex",
                                     "ttm_sbc", "ttm_shares_diluted", "ttm_oe_total", "ttm_oe_per_share", "warnings",
                                     "overrides_used", "capex_components", "sbc_reconciled_legs", "split_adjustment",
                                     "capex_override_superseded_legs", "sbc_reconciliation_withdrawn_legs"}, (t, sorted(plain["ttm"]))
        # --interim never falls back to the 10-Q TTM at a 10-K filer: no declaration, refused
        inter = H.run_ttm(t, base=H.make_base(fx, j, None, copy_repo_files=False), fixture=fx,
                          patch=lambda T: sys.argv.append("--interim"))
        assert inter["exit"] == 3 and inter["ttm"] is None, (t, inter["exit"], inter["stdout"][-300:])
        assert "[IB-SHAPE] judgment.json declares no interim_bridge" in inter["stderr"], inter["stderr"]


# ---------------------------------------------------------------------------
# T-a: ttm_inputs of a declared ttm.json (amendment 10)
# ---------------------------------------------------------------------------
def test_declared_interim_ttm_inputs_bound():
    t = _once()["ttm"]
    h = E.ttm_inputs_record(t)["ttm_input_hash"]
    text = copy.deepcopy(t)
    text["provenance"][0]["snippet"] = "another snippet"
    text["like_for_like"]["comparative_note"] = "another note"
    text["warnings"] = ["x"]
    assert E.ttm_inputs_record(text)["ttm_input_hash"] == h        # provenance and prose are not inputs
    other = _once(rates={"2025-06-30": 1.171, "2026-06-30": 1.1394})["ttm"]
    assert other is None or E.ttm_inputs_record(other)["ttm_input_hash"] != h
    moved = _once(rates={"2025-06-30": 1.1725, "2026-06-30": 1.1394})["ttm"]   # within 0.5% of the declared 1.172
    assert moved is not None and E.ttm_inputs_record(moved)["ttm_input_hash"] != h
    d = _leg(decl(), "sbc", "current_interim", value=18400000, snippet="Non-cash charge for share-based compensation 18.4 19")
    leg_moved = _once(d=d, instance=six_k().replace(b">18000000<", b">18400000<"))["ttm"]
    assert leg_moved is not None and E.ttm_inputs_record(leg_moved)["ttm_input_hash"] != h
    # the TTM_INPUT_TOP_FIELDS list is not extended (every committed ttm.json keeps its hash)
    assert E.TTM_INPUT_TOP_FIELDS == ("fy_end", "ytd_end", "inputs", "ttm_ocf", "ttm_capex", "ttm_sbc",
                                      "ttm_shares_diluted", "ttm_oe_total", "ttm_oe_per_share", "capex_components",
                                      "split_adjustment")
    # an engine --ttm run on the declared ttm.json reads it like a 10-Q one; with an acquired-IPR&D charge the
    # denominator is the TTM's (the current interim's diluted count), never the FY count
    import test_engine_iprd as TI
    n = TI._ok(TI._run(TI._facts(expense={2025: 20e6}), extra=["--ttm"], ttm=t))
    assert n["ttm_inputs"] == E.ttm_inputs_record(t), (n["ttm_inputs"], E.ttm_inputs_record(t))
    assert n["base_oe_per_share"] == t["ttm_oe_per_share"] and n["base_source"] == "ttm_json"
    blk = n["iprd_adjustment"]
    assert blk["shares_source"] == "ttm.json ttm_shares_diluted" and blk["shares_denominator"] == 617000000, blk
    assert blk["window"]["ttm_current_ytd"] == ["2026-01-01", "2026-06-30"], blk["window"]


# ---------------------------------------------------------------------------
# T-c: acquired IPR&D in the current interim (amendment 11, default Q8)
# ---------------------------------------------------------------------------
def test_ib_iprd_refuses_current_interim_charge():
    fact = (f'<us-gaap:{IPRD} contextRef="H126" unitRef="EUR" decimals="-6">5000000</us-gaap:{IPRD}>')
    _refused(_once(instance=six_k(fact)), f"[IB-IPRD] the 6-K files {IPRD} = 5,000,000 for 2026-01-01..2026-06-30: an "
                                          "acquired-IPR&D charge in the current interim")
    prior_only = fact.replace('contextRef="H126"', 'contextRef="H125"')
    out = _once(instance=six_k(prior_only))
    assert out["exit"] == 0 and out["ttm"]["iprd_interim_scan"] == "xbrl_instance: none", out["stderr"][-800:]
    out = _once(sub=submissions(is_xbrl=0))
    assert out["exit"] == 0, out["stderr"][-800:]
    t = out["ttm"]
    assert t["iprd_interim_scan"] == "not_scanned (the report has no XBRL instance)"
    assert any("no XBRL instance" in w and "acquired-IPR&D" in w for w in t["warnings"]), t["warnings"]
    assert t["legs"]["ocf"]["current_interim"]["verified"] == "snippet" and t["xbrl_verified_legs"] == []


# ---------------------------------------------------------------------------
# --interim-draft
# ---------------------------------------------------------------------------
def test_interim_draft_prints_and_writes_nothing():
    out = _once(args=("--interim-draft", ACC), judgment={"interim_bridge": None})
    assert out["exit"] == 0, out["stderr"][-1000:]
    assert out["written"] is None
    dr = out["ttm"]["interim_bridge"]
    assert dr["prior_interim"]["period"] == ["2025-01-01", "2025-06-30"]
    assert dr["current_interim"]["period"] == ["2026-01-01", "2026-06-30"]
    assert dr["legs"]["ocf"]["current_interim"]["value"] == 539000000 and dr["legs"]["ocf"]["current_interim"]["kind"] == "filing"
    assert dr["legs"]["shares_diluted"]["current_interim"]["value"] == 617000000
    assert dr["legs"]["capex_intangibles"]["prior_interim"]["value"] is None
    assert "TODO" in dr["legs"]["capex_intangibles"]["prior_interim"]["kind"]
    assert dr["fx"]["fy"]["rate"] == 1.175 and dr["fx"]["current_interim"]["rate"] == 1.1394
    assert dr["currency"] == "EUR" and dr["fy_period"] == ["2025-01-01", "2025-12-31"]


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
