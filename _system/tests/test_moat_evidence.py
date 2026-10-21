#!/usr/bin/env python3
"""Moat rubric 2: operating-basis ROIC and the measured moat anchor (moat_evidence.py, 2026-10-21).
Run: python _system/tests/test_moat_evidence.py (or python -m pytest _system/tests).

Andrew's request in the "Tighten moat scoring" thread (2026-10-20): moat
scores sat 82% at 4-6 and tracked measured returns only at Spearman 0.30, and
the old roic_proxy = NOPAT / (equity + debt − cash) was wrong exactly where
moats are widest. No network, no company folders: the rows are trimmed copies
of committed fundamentals.json files frozen in
fixtures/moat_evidence/fundamentals_rows.json, each carrying the OLD
roic_proxy it was written with, so every ROIC case also proves the old figure
was wrong (the test fails on the code before this change: there was no
moat_evidence module, and fundamentals.build_annual wrote the old figure).

1. ROIC per row (roic_row / roic_series): VRSN's negative equity is
   customer-funded capital, not −35%; MANH's cash ≈ equity is capital-light,
   not −1540% / +651%; IBRX's and ALNY's losses stay negative (old +43% /
   +22%); MTD's unfiled operating income falls back to pretax + interest at a
   known non-financial SIC (36.9%, old none); DKS reads 19.9% (old 75%);
   NTNX FY2024's thin profit on negative capital is 2.8% evidence, not +100%;
   NVR's unclassified balance sheet takes the assets basis. No fallback at a
   financial or blank SIC (an NLY-shaped row would add back repo interest).
2. fundamentals.build_annual writes the new keys (companyfacts-shaped facts).
3. Paths: ARCC (blank SIC) and NLY (mortgage REIT) → roe_fin, BXP → reit_prior,
   WEC → roe_util, HBAN → tangible ROE, an operating real-estate SIC → roic.
4. Anchors, terms and caps: VRSN 9 (record), ROP 3, MOH thin_margin 4, IBKR
   data_check 6, HPQ low_margin 7, NVR non_operating_basis 7, FIG
   insufficient history (band 0-5); band ±2 with 9-10 only from anchor 8.
5. Reasons: ACQUIRED_GOODWILL lifts a serial acquirer by 1 (ROP 6 explained,
   7 not); WCN fails its tangible test; CYCLE_ADJUSTED cannot lift a serial
   acquirer (TYL); EXPENSED_INVESTMENT (NTNX); NO_DURABLE_SOURCE explains a
   low moat only; SHORT_HISTORY keeps the entry gate closed and is refused
   with 5+ usable years; malformed reasons and sources raise ValueError; an
   explicitly empty moat_sources caps the band at 4.
6. record() / key_numbers_lines() / the CLI.
"""
import json
import os
import subprocess
import sys
import tempfile
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
sys.path.insert(0, SYS)
import moat_evidence as M  # noqa: E402
import fundamentals as F  # noqa: E402

with open(os.path.join(HERE, "fixtures", "moat_evidence", "fundamentals_rows.json"), encoding="utf-8") as _f:
    FX = json.load(_f)
TEXT = "The filing states the figure this reason rests on, in these words."


def fu(t):
    return FX[t]


def row(t, fy):
    f = fu(t)
    return next(r for r in f["annual"] if r["fy"] == fy), M.sic_int(f)


def ev(t):
    return M.evidence(fu(t))


def reason(code, **kw):
    return dict({"code": code, "text": TEXT}, **kw)


def raises(fn, needle):
    try:
        fn()
    except ValueError as e:
        assert needle in str(e), f"{needle!r} not in {e}"
        return
    raise AssertionError(f"expected ValueError containing {needle!r}")


# ---------------------------------------------------------------- 1. ROIC per row
def test_negative_equity_is_customer_funded_not_a_negative_return():
    r, s = row("VRSN", "2025")
    assert r["roic_proxy"] < -0.3, "fixture: the old proxy read VRSN FY2025 at -35%"
    x = M.roic_row(r, s)
    assert x["roic_proxy"] is None and x["roic_class"] == "customer_funded" and x["roic_basis"] == "operating", x
    assert M.roic_series([r], s)[0]["v"] == 1.0, "a profit over capital <= 0 is clipped to +100% evidence, never flipped"


def test_cash_near_equity_is_capital_light_not_a_swing():
    for fy, old in (("2025", -15.39), ("2024", 6.51)):
        r, s = row("MANH", fy)
        assert abs(r["roic_proxy"] - old) < 0.01, f"fixture: old proxy {r['roic_proxy']}"
        x = M.roic_row(r, s)
        assert x["roic_proxy"] is None and x["roic_class"] == "capital_light", x
        assert M.roic_series([r], s)[0]["v"] == 1.0


def test_losses_stay_negative():
    for t, fy in (("IBRX", "2024"), ("ALNY", "2023")):
        r, s = row(t, fy)
        assert r["roic_proxy"] > 0.2, f"fixture: the old proxy read {t} FY{fy}'s loss as {r['roic_proxy']:+.0%}"
        x = M.roic_row(r, s)
        assert x["roic_proxy"] < 0 and M.roic_series([r], s)[0]["v"] < 0, (t, x)


def test_unfiled_operating_income_falls_back_at_a_known_non_financial_sic():
    r, s = row("MTD", "2025")
    assert r["roic_proxy"] is None and r.get("operating_income") is None, "fixture: MTD files no OperatingIncomeLoss"
    assert s == 3826
    n, basis = M.nopat(r, s)
    assert basis == "pretax+interest"
    assert abs(M.roic_row(r, s)["roic_proxy"] - 0.3687) < 0.0005
    assert M.nopat(r, None) == (None, None), "a blank SIC gets no fallback"
    nly = {"fy": "2025", "operating_income": None, "pretax_income": 1e9, "interest_expense": 4.8e9, "tax": 0,
           "net_income": 1e9, "assets": 9e10, "liab_current": None, "equity": 1.2e10}
    assert M.nopat(nly, 6798) == (None, None), "a mortgage REIT's repo interest is never added back"
    assert M.roic_row(nly, 6798)["roic_class"] == "financial"
    assert M.roic_row(nly, 6021)["roic_proxy"] is None


def test_operating_capital_reads_the_debt_the_old_proxy_missed():
    r, s = row("DKS", "2025")
    assert r["roic_proxy"] > 0.7, "fixture: old proxy 75%"
    x = M.roic_row(r, s)
    assert abs(x["roic_proxy"] - 0.1988) < 0.0005 and x["roic_basis"] == "operating", x


def test_thin_profit_on_negative_capital_stays_thin():
    r, s = row("NTNX", "2024")
    x, e = M.roic_row(r, s), M.roic_series([r], s)[0]
    assert x["roic_proxy"] is None and x["roic_class"] == "customer_funded"
    assert 0 < e["v"] < 0.05, f"NTNX FY2024 evidence {e['v']} (NOPAT over 10% of revenue, not +100%)"


def test_unclassified_balance_sheet_takes_the_assets_basis():
    r, s = row("NVR", "2025")
    assert r["roic_proxy"] is None and r.get("liab_current") is None
    assert M.invested_capital(r)[1] == "assets"
    x = M.roic_row(r, s)
    assert x["roic_basis"] == "assets" and abs(x["roic_proxy"] - 0.3435) < 0.0005


def test_financing_basis_when_total_debt_covers_the_balance_sheet():
    r = {"assets": 100.0, "liab_current": None, "equity": 40.0, "total_debt": 50.0, "liabilities": 60.0, "cash": 10.0,
         "operating_income": 10.0, "pretax_income": 10.0, "tax": 2.1, "revenue": 100.0}
    assert M.invested_capital(r) == (80.0, "financing")
    r["liabilities"] = 120.0   # liabilities − debt = 70% of assets: the debt figure does not cover the balance sheet
    assert M.invested_capital(r)[1] == "assets"


def test_tax_rate_fallback_and_current_debt():
    assert M.tax_rate({"pretax_income": 100, "tax": 25}) == 0.25
    assert M.tax_rate({"pretax_income": -5, "tax": 1}) == 0.21
    assert M.tax_rate({"pretax_income": 100, "tax": 80}) == 0.21
    assert M.current_debt({"debt_current": 7}) == 7
    assert M.current_debt({"total_debt": 30, "debt_lt": 25}) == 5
    assert M.current_debt({}) == 0.0


# ---------------------------------------------------------------- 2. fundamentals.py writes the new keys
def _facts(entries):
    out = {"facts": {}}
    for tag, unit, e in entries:
        out["facts"].setdefault("us-gaap", {}).setdefault(tag, {"units": {}})["units"].setdefault(unit, []).append(e)
    return out


def _dur(tag, end, val):
    return (tag, "USD", {"start": f"{end[:4]}-01-01", "end": end, "val": val, "form": "10-K", "fp": "FY",
                         "filed": f"{int(end[:4]) + 1}-02-15", "accn": "K" + end})


def _inst(tag, end, val):
    return (tag, "USD", {"end": end, "val": val, "form": "10-K", "fp": "FY", "filed": f"{int(end[:4]) + 1}-02-15",
                         "accn": "K" + end})


def test_fundamentals_build_annual_writes_the_operating_basis_roic():
    # VRSN FY2025 shape: 1.6B revenue, 1.1B operating income, equity −2.2B after buybacks, current liabilities above
    # assets − cash. The old row read (1.1B × 0.79) / (−2.2B + 1.8B − 0.6B) = −87%.
    end = "2025-12-31"
    facts = _facts([_dur("Revenues", end, 1.6e9), _dur("OperatingIncomeLoss", end, 1.1e9),
                    _dur("IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest", end, 1.05e9),
                    _dur("IncomeTaxExpenseBenefit", end, 0.25e9), _dur("NetIncomeLoss", end, 0.8e9),
                    _inst("Assets", end, 1.4e9), _inst("LiabilitiesCurrent", end, 1.3e9),
                    _inst("CashAndCashEquivalentsAtCarryingValue", end, 0.6e9), _inst("StockholdersEquity", end, -2.2e9),
                    _inst("LongTermDebtNoncurrent", end, 1.8e9)])
    for sic in (7371, None):
        rows, _, _ = F.build_annual(facts, sic=sic)
        r = next(x for x in rows if x["period_end"] == end)
        assert r["roic_proxy"] is None and r["roic_class"] == "customer_funded" and r["roic_basis"] == "operating", r
        for k in M.ROIC_KEYS:
            assert k in r
    # MTD shape: no OperatingIncomeLoss — the pretax + interest fallback needs the filer's SIC
    facts = _facts([_dur("Revenues", end, 4e9), _dur("IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest", end, 1e9),
                    _dur("IncomeTaxExpenseBenefit", end, 0.2e9), _dur("InterestExpense", end, 0.1e9),
                    _dur("NetIncomeLoss", end, 0.8e9), _inst("Assets", end, 4e9), _inst("LiabilitiesCurrent", end, 1.5e9),
                    _inst("CashAndCashEquivalentsAtCarryingValue", end, 0.1e9), _inst("StockholdersEquity", end, 0.2e9)])
    r = next(x for x in F.build_annual(facts)[0] if x["period_end"] == end)
    assert r["roic_proxy"] is None, "no SIC (build_annual before the submissions profile): no fallback"
    r = next(x for x in F.build_annual(facts, sic=3826)[0] if x["period_end"] == end)
    assert abs(r["roic_proxy"] - (1.1e9 * 0.8) / (4e9 - 0.1e9 - 1.5e9)) < 1e-9, r
    # fundamentals.main() re-applies the keys with the profile's SIC once the submissions are read
    src = open(os.path.join(SYS, "fundamentals.py"), encoding="utf-8").read()
    assert 'moat_evidence.apply_roic(annual, moat_evidence.sic_int(profile.get("sic")))' in src


# ---------------------------------------------------------------- 3. paths
def test_paths():
    assert M.path_for(fu("ARCC")) == "roe_fin", "a BDC with no SIC and no operating income is a lender"
    assert M.path_for(fu("NLY")) == "roe_fin", "a mortgage REIT is a spread lender"
    assert M.path_for(fu("BXP")) == "reit_prior"
    assert M.path_for(fu("WEC")) == "roe_util"
    assert M.path_for(fu("HBAN")) == "roe_fin" and ev("HBAN")["series"][-1]["label"] == "rote"
    op = {"profile": {"sic": "6531"}, "annual": [{"operating_income": 1.0}] * 5}
    assert M.path_for(op) == "roic", "a real-estate services operator (CBRE, JLL) is judged on ROIC"
    e = ev("BXP")
    assert e["status"] == "prior" and e["anchor_r"] == 4 and e["band"] == [2, 6]


# ---------------------------------------------------------------- 4. anchors
def test_anchors_terms_and_caps():
    e = ev("VRSN")
    assert e["anchor_r"] == 9 and e["terms"] == {"record": 1.0} and e["band"] == [7, 10]
    e = ev("ROP")
    assert e["anchor_r"] == 3 and e["band"] == [1, 5] and e["serial_acquirer"] is True
    e = ev("MOH")
    assert e["anchor"] == 4.0 and "thin_margin" in e["caps"], "float ROE at a 2% net margin is not a moat"
    e = ev("IBKR")
    assert e["anchor_r"] == 6 and "data_check" in e["caps"]
    e = ev("HPQ")
    assert e["anchor_r"] == 7 and e["caps"] == {"low_margin": 7.0}, "supplier float, not pricing power"
    e = ev("NVR")
    assert e["anchor_r"] == 7 and "non_operating_basis" in e["caps"]
    e = ev("FIG")
    assert e["status"] == "insufficient_history" and e["anchor"] is None and e["band"] == [0, 5]
    e = ev("WEC")
    assert e["path"] == "roe_util" and e["anchor"] <= 6.0
    assert M.evidence(None)["status"] == "not_measured" and M.evidence({"annual": []})["band"] is None


def test_band_reaches_9_and_10_only_from_anchor_8():
    assert M.band_for(7) == [5, 8] and M.band_for(8) == [6, 10] and M.band_for(9) == [7, 10]
    assert M.band_for(0) == [0, 2] and M.band_for(1) == [0, 3]


# ---------------------------------------------------------------- 5. assessment and reasons
def test_assess_in_band_above_and_below():
    a = M.assess(ev("HALO"), 7)
    assert a["status"] == "in_band" and not a["entry_gate_closed"] and not a["sources_declared"]
    a = M.assess(ev("ROP"), 7)
    assert a["status"] == "outside_band_unexplained" and a["flag"] == "MOAT_ABOVE_EVIDENCE" and a["entry_gate_closed"]
    a = M.assess(ev("MANH"), 6)
    assert a["status"] == "outside_band_unexplained" and a["flag"] == "MOAT_BELOW_EVIDENCE"
    assert a["entry_gate_closed"] is False, "a moat below its band closes no gate"
    assert M.assess(M.evidence(None), 9) == {"moat": 9.0, "sources_declared": False, "entry_gate_closed": False,
                                              "status": "not_measured"}


def test_acquired_goodwill_lifts_a_serial_acquirer_by_one():
    e = ev("ROP")
    a = M.assess(e, 6, reason("ACQUIRED_GOODWILL"))
    assert a["status"] == "outside_band_explained" and a["reach"] == [1, 6] and a["reason_tested"] is True
    assert a["entry_gate_closed"] is False, "a mechanically tested reason reopens the entry gate"
    a = M.assess(e, 7, reason("ACQUIRED_GOODWILL"))
    assert a["status"] == "outside_band_unexplained" and a["entry_gate_closed"] and "reach 1–6" in a["reason_rejected"]
    ok, *_, why = M.check_reason(ev("WCN"), reason("ACQUIRED_GOODWILL"))
    assert not ok and why == "tangible ROIC >= 20% in 0/5 years (needs 3)", why


def test_cycle_adjusted_cannot_lift_a_serial_acquirer():
    e = ev("TYL")
    ok, lo, hi, mech, why = M.check_reason(e, reason("CYCLE_ADJUSTED"))
    assert ok and mech and hi == e["band"][1], (lo, hi, why)
    ok, lo, hi, _, why = M.check_reason(ev("DKS"), reason("CYCLE_ADJUSTED"))
    assert ok and (lo, hi) == (4, 8), why


def test_expensed_investment():
    a = M.assess(ev("NTNX"), 6, reason("EXPENSED_INVESTMENT"))
    assert a["status"] == "outside_band_explained" and a["reach"] == [1, 6] and not a["entry_gate_closed"]
    ok, *_, why = M.check_reason(ev("ROP"), reason("EXPENSED_INVESTMENT"))
    assert not ok and "15%" in why


def test_text_only_reasons_and_direction():
    a = M.assess(ev("MANH"), 6, reason("NO_DURABLE_SOURCE"))
    assert a["status"] == "outside_band_explained" and a["reason_tested"] is False and not a["entry_gate_closed"]
    a = M.assess(ev("ROP"), 7, reason("NO_DURABLE_SOURCE"))
    assert a["status"] == "outside_band_unexplained" and "below the band only" in a["reason_rejected"]
    a = M.assess(ev("FIG"), 7, reason("SHORT_HISTORY"))
    assert a["status"] == "outside_band_explained" and a["entry_gate_closed"] is True, \
        "a text-only reason records the explanation but never reopens the entry alert"
    a = M.assess(ev("ROP"), 7, reason("SHORT_HISTORY"))
    assert a["status"] == "outside_band_unexplained" and "fewer than 5 usable years" in a["reason_rejected"]
    a = M.assess(ev("ROP"), 7, reason("MEASUREMENT_DEFECT", field="operating_income", fy="2024"))
    assert a["status"] == "outside_band_explained" and a["entry_gate_closed"] is True


def test_business_changed():
    a = M.assess(ev("HBAN"), 8, reason("BUSINESS_CHANGED", since_fy="2023"))
    assert a["status"] == "outside_band_explained" and a["reach"][1] == 8
    ok, *_, why = M.check_reason(ev("HBAN"), reason("BUSINESS_CHANGED", since_fy="2099"))
    assert not ok and "after every fiscal year" in why


def test_malformed_judgment_fields_raise():
    raises(lambda: M.assess(ev("ROP"), 7, {"code": "GOODWILL", "text": TEXT}), "moat_evidence_reason.code")
    raises(lambda: M.assess(ev("ROP"), 7, {"code": "ACQUIRED_GOODWILL", "text": "acquired"}), ">= 40 characters")
    raises(lambda: M.assess(ev("ROP"), 7, "ACQUIRED_GOODWILL"), "must be an object")
    raises(lambda: M.check_reason_shape(reason("BUSINESS_CHANGED")), "since_fy")
    raises(lambda: M.check_reason_shape(reason("MEASUREMENT_DEFECT", field="roic_proxy", fy="2024")), "field")
    raises(lambda: M.assess(ev("ROP"), 4, None, "switching_costs"), "must be a list")
    raises(lambda: M.assess(ev("ROP"), 4, None, [{"source": "brand", "evidence": "a famous consumer brand name"}]), "source must be one of")
    raises(lambda: M.assess(ev("ROP"), 4, None, [{"source": "switching_costs", "evidence": "sticky"}]), ">= 20 characters")
    # a malformed reason raises even when the moat is in band (make_score refuses it before anything is written)
    raises(lambda: M.assess(ev("HALO"), 7, {"code": "X", "text": TEXT}), "moat_evidence_reason.code")


def test_explicitly_empty_sources_cap_the_band_at_4():
    a = M.assess(ev("ODFL"), 7, None, [])
    assert a["band"] == [4, 4] and a["status"] == "outside_band_unexplained" and a["sources_declared"] is True
    src = [{"source": "cost_advantage", "evidence": "densest less-than-truckload terminal network in the US"}]
    assert M.assess(ev("ODFL"), 9, None, src)["status"] == "in_band"
    a = M.assess(ev("NTNX"), 5, reason("EXPENSED_INVESTMENT"), [])
    assert a["status"] == "outside_band_unexplained", "no reason reaches past the no-source cap"


# ---------------------------------------------------------------- 6. record / key_numbers lines / CLI
def test_record_and_key_numbers_lines():
    e = ev("ROP")
    a = M.assess(e, 7)
    rec = M.record(e, a)
    assert rec["rubric"] == M.RUBRIC == 2 and rec["evidence_band"] == [1, 5] and rec["evidence_status"] == "measured"
    assert rec["status"] == "outside_band_unexplained" and rec["band"] == [1, 5] and len(rec["series"]) == 5
    assert rec["series"][-1][0] == "2025" and "moat" not in rec
    json.dumps(rec)
    L = M.key_numbers_lines(e, a)
    assert L[0].startswith("- Moat evidence (roic, hurdle 10%)") and "→ anchor 3.12 (3) · band 1–5" in L[0], L[0]
    assert L[1].startswith("- ROIC ex-goodwill (context only)") and "serial acquirer" in L[1]
    assert "- Moat vs evidence: 7 → above band 1–5, unexplained (MOAT_ABOVE_EVIDENCE — entry alert closed)" in L
    assert "- Moat sources: not declared (judgment.json moat_sources, rubric 2)" in L
    L = M.key_numbers_lines(ev("VRSN"), M.assess(ev("VRSN"), 9))
    assert "n/a (capital <= 0)" in L[1] and "(customer_funded)" in L[0] and "→ in band 7–10" in L[2]
    assert M.key_numbers_lines(M.evidence(None))[0].startswith("- Moat evidence: not measured")
    assert "insufficient history" in M.key_numbers_lines(ev("FIG"))[0]


def test_cli():
    base = tempfile.mkdtemp(prefix="moat_evidence_")
    try:
        os.makedirs(os.path.join(base, "ROP"))
        with open(os.path.join(base, "ROP", "fundamentals.json"), "w", encoding="utf-8") as f:
            json.dump(fu("ROP"), f)
        env = dict(os.environ, STOCKS_BASE=base, PYTHONIOENCODING="utf-8")
        cli = [sys.executable, os.path.join(SYS, "moat_evidence.py"), "ROP"]
        r = subprocess.run(cli + ["--moat", "7"], capture_output=True, text=True, encoding="utf-8", env=env, timeout=60)
        assert r.returncode == 0 and "→ anchor 3.12 (3) · band 1–5" in r.stdout and "MOAT_ABOVE_EVIDENCE" in r.stdout, r
        r = subprocess.run(cli + ["--json"], capture_output=True, text=True, encoding="utf-8", env=env, timeout=60)
        assert r.returncode == 0 and json.loads(r.stdout)["anchor_r"] == 3, r
        with open(os.path.join(base, "ROP", "judgment.json"), "w", encoding="utf-8") as f:
            json.dump({"moat_score": 6, "moat_evidence_reason": reason("ACQUIRED_GOODWILL")}, f)
        r = subprocess.run(cli, capture_output=True, text=True, encoding="utf-8", env=env, timeout=60)
        assert r.returncode == 0 and "explained by ACQUIRED_GOODWILL (reach 1–6)" in r.stdout, r
        with open(os.path.join(base, "ROP", "judgment.json"), "w", encoding="utf-8") as f:
            json.dump({"moat_score": 6, "moat_evidence_reason": {"code": "NOPE", "text": TEXT}}, f)
        r = subprocess.run(cli, capture_output=True, text=True, encoding="utf-8", env=env, timeout=60)
        assert r.returncode == 1 and "malformed" in r.stderr, r
    finally:
        shutil.rmtree(base, ignore_errors=True)


if __name__ == "__main__":
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn(); print(f"PASS {name}")
            except AssertionError as e:
                fails += 1; print(f"FAIL {name}: {e}")
            except Exception as e:
                fails += 1; print(f"ERROR {name}: {type(e).__name__}: {e}")
    sys.exit(1 if fails else 0)
