#!/usr/bin/env python3
"""The moat scorecard (engine 5.7, Andrew 2026-10-19, R4 REVISED: Dorsey's sources + the evidence scorecard, with the
M1b and M1c amendments; design 03b, decisions 03c, lane defaults 12). Run: python _system/tests/test_moat_scorecard.py
(or python -m pytest _system/tests). Offline: temp folders and a temp STOCKS_BASE; the end-to-end cases run
make_score.py as a subprocess in the harness of test_make_score_55 (Run, files=...). Every test fails on the code before
engine 5.7 (e22e814): there is no moat_scorecard module, no moat_evidence, no moat gate.

Unit — moat_scorecard:
 1 test_capital_returns_shared (+ F-8 test_scorecard_reads_the_same_numbers): one returns function, no tax / EBIT rule
   of its own; CSV rows on the net-income + tax rung.
 2 governing selection · 3 ladders and the cycle floor · 4 unbounded / unstable years · 5 the measures side by side
   (HPQ: ROE n/m, never -300%) · 6 industry_structure on same-ladder peers (leave-one-out by CIK, -inf peers dropped
   and counted, the waste-hauler and mixed-REIT cases) · 7 capital intensity and scale economics (03's rules) ·
   8 the core evidence and the supporting adjustment (sum / 4, 03c decision 11) · 9 the source rules S1-S9, W1-W8 ·
   10 the source caps, 10b supporting factors without a source · 11 supporting-factor rules · 12 erosion_risks threats ·
   13 the erosion test (gross margin, the operating-margin fallback, not on CSV rows) · 14 the low-return gate on the
   governing measure · 15 the reverse gate (incl. 03c decision 2) · 16 the bad-moat lint · 17 the SIC lock incl. the
   SIC-6798 mortgage-REIT rule · 18 declared-pillar rules · 19 volume x price bounds · 20 rebuild drift (20b with the
   relaxation off) · IPR&D: the one-time charge added back (lane default Q3 (b)).
End-to-end (make_score): 21 a pre-5.7 record reports only · 22 a 5.7 run needs the scorecard, sources and supporting
 block · 23 the divergence reason and its registry event · 24 the low-return and reverse reasons and events · 25 the
 erosion rebuttal event · 26 the weight floor · 27 a refusal writes nothing · 27b the influence checks reach
 check_influence with the moat evidence's numbers.
Repo-wide: 28 every recorded folder evaluates (report_only, JSON without Infinity) · 30 the worked examples in
 _system/examples/ reproduce exactly.
L3 review round 1 (2026-10-21; each fails on the lane's first build b0ba6fa, r57/L3/review_fix/ff_moat.log): R1 an
 identical make_score rerun is byte-identical (no persisted run kind) · R3 the dry run is an authoring check · R4 the
 IPR&D add-back in the rows' money unit · R5 the weight floor and the row-revenue volume x price bounds drift on a
 rebuild · R6 rulings57.add_minimal_scorecard follows the SIC lock.
Integration with L2 (R3 strict quoting, the L3 merge): the fixture facts carry snippets and ids facts.json accepts
 (snippet_for; SRC_FACTS' ids F201-F222), the reasons' cited facts their used_for tags, and 27c the moat reasons go
 through L2's real influence trace end to end.
"""
import copy
import csv
import glob
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
REPO = os.path.dirname(SYS)
sys.path.insert(0, SYS)
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import moat_scorecard as M  # noqa: E402
import fundamentals as F  # noqa: E402
import dcf_engine as E  # noqa: E402

YEARS = (2021, 2022, 2023, 2024, 2025)
LPE = "2025-12-31"


# ---------------------------------------------------------------- fixtures
def row(year, v=0.18, **kw):
    """A fundamentals.json annual row whose plain ROIC is exactly v (tax 0 on a positive pretax, IC 1,000, revenue
    2,000: invested capital 50% of revenue, a stable denominator)."""
    r = {"period_end": f"{year}-12-31", "fy": str(year), "revenue": 2000.0, "operating_income": 1000.0 * v,
         "pretax_income": 1.0, "interest_expense": None, "tax": 0.0, "net_income": 1000.0 * v, "equity": 1000.0,
         "total_debt": 0.0, "cash": 0.0, "goodwill": None, "intangibles": None, "assets": 2000.0, "liabilities": 1000.0,
         "gross_margin": 0.40, "revenue_basis": "Revenues", "cash_basis": "CashAndCashEquivalentsAtCarryingValue"}
    r.update(kw)
    return r


def rows_of(values, **kw):
    return [row(y, v, **kw) for y, v in zip(YEARS[-len(values):], values)]


def fact(fid, metric, period, value, unit="pct", used=(), kind="filing", type="metric", **kw):
    f = {"id": fid, "label": f"{metric} {period}", "value": value, "unit": unit, "scale": "", "precision": 2,
         "period": period, "kind": kind, "type": type, "metric": metric, "used_for": list(used)}
    if kind == "third_party":
        f["source"] = {"url": "https://example.com/x", "publisher": "Example", "published": "2026-01-05"}
    else:
        f["source"] = {"form": "10-K", "accession": "0000000001-26-000001", "section": "Item 7", "filed": "2026-02-20"}
    f["snippet"] = snippet_for(metric, value, unit)
    f.update(kw)
    return f


def snippet_for(metric, value, unit):
    """[Integrate L2] a snippet facts.json accepts (R3, quote_tokens.snippet_shows_value): the value as a filing
    prints it — 0.045 pct as "4.5%", a count as "1,200", USD as "$1,000,000,000" — so a fixture fact passes L2's
    validation when make_score reads facts.json (the end-to-end cases); a [low, high] range prints both ends."""
    def one(x):
        v = float(x)
        if unit in ("pct", "pp"):
            return f"{v * 100:g}%"
        if unit == "x":
            return f"{v:g}x"
        if unit == "count":
            return f"{v:,.0f}" if v.is_integer() else f"{v:g}"
        return (f"${v:,.0f}" if unit == "USD" else f"{v:,.0f} {unit}") if v.is_integer() else f"{v:g} {unit}"
    shown = " to ".join(one(x) for x in value) if isinstance(value, (list, tuple)) else one(value)
    return f"{metric.replace('_', ' ')} was {shown}"


def series(ids, metric, values, unit="pct", used=(), **kw):
    return [fact(i, metric, f"FY{y}", v, unit, used, **kw) for i, y, v in zip(ids, (2023, 2024, 2025), values)]


def base_facts():
    # [Integrate L2] F3 and F6 also carry the reason tags (facts.INFLUENCE_TAGS) of the moat reasons that cite them in
    # the end-to-end cases: L2's check_influence refuses a cited fact that does not list the field's used_for tag
    f1_3 = series(("F1", "F2", "F3"), "price_realization", (0.04, 0.05, 0.045), used=("moat:pricing_power",))
    f1_3[2]["used_for"] += ["moat_divergence", "low_roic", "erosion_rebuttal"]
    f4_6 = series(("F4", "F5", "F6"), "retention_rate", (0.95, 0.96, 0.96), used=("moat:retention", "moat:sources"))
    f4_6[2]["used_for"] += ["moat_divergence", "high_return_low_moat"]
    return (f1_3 + f4_6
            + series(("F7", "F8", "F9"), "customers", (1000, 1100, 1200), unit="count", used=("moat:reach_and_growth",))
            + [fact("F10", "spec_in_cycle_years", "FY2025", 7, unit="count", type="event", unit_label="years",
                    used=("moat:switching_costs", "moat:sources"))]
            + series(("F11", "F12", "F13"), "largest_customer_share", (0.06, 0.06, 0.05), used=("moat:concentration",))
            + [fact("F14", "competitor_launches", "FY2025", 1, unit="count", type="event", used=("moat:erosion_risks",))])


def na(reason="fixture: not applicable"):
    return {"applicable": False, "not_applicable_reason": reason}


def base_scorecard():
    return {"version": 1, "business_type": "industrial",
            "business_type_reason": "Engineered components: 100% of revenue is manufactured products (segments.json).",
            "sources": [{"type": "switching_costs", "subtype": "embedded_component", "strength": "narrow",
                         "facts": ["F10"], "metrics": [], "rationale": "Spec-in parts requalified only at a redesign."}],
            "pillars": {"pricing_power": {"score": 1, "rationale": "price realization", "facts": ["F1", "F2", "F3"]},
                        "retention": {"score": 1, "rationale": "retention", "facts": ["F4", "F5", "F6"]},
                        "reach_and_growth": {"score": 0, "rationale": "customers", "facts": ["F7", "F8", "F9"]},
                        "switching_costs": {"score": 1, "rationale": "spec-in", "facts": ["F10"]},
                        "concentration": {"score": 0, "rationale": "largest customer", "facts": ["F11", "F12", "F13"]},
                        "erosion_risks": {"score": 0, "rationale": "a launch", "facts": ["F14"]},
                        "customer_regard": na()},
            "supporting": {k: na() for k in M.SUPPORTING},
            "volume_price": None, "moat_divergence_reason": None, "low_roic_reason": None,
            "high_return_low_moat_reason": None, "erosion_rebuttal": None}


class Case:
    """A temp folder (fundamentals.json rows and/or financials_history.csv, facts.json) + a judgment + a record."""

    def __init__(self, rows=None, csv_rows=None, facts=None, sc="base", moat=6, release="5.7.0", sic=None, n_extra=None,
                 profile_sic=None, j_extra=None):
        self.tmp = tempfile.mkdtemp(prefix="moat_case_")
        self.folder = os.path.join(self.tmp, "TST")
        os.makedirs(self.folder)
        self.rows = rows if rows is not None else rows_of([0.18] * 5)
        if self.rows:
            doc = {"cik": 1, "currency": "USD", "annual": self.rows}
            if profile_sic:
                doc["profile"] = {"sic": profile_sic}
            json.dump(doc, open(os.path.join(self.folder, "fundamentals.json"), "w", encoding="utf-8"))
        if csv_rows:
            with open(os.path.join(self.folder, "financials_history.csv"), "w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
                w.writeheader()
                w.writerows(csv_rows)
        self.facts = facts if facts is not None else base_facts()
        json.dump({"schema": 1, "ticker": "TST", "facts": self.facts},
                  open(os.path.join(self.folder, "facts.json"), "w", encoding="utf-8"))
        self.sc = base_scorecard() if sc == "base" else sc
        self.j = {"moat_score": moat, "moat_justification": "test", "moat_for": [], "moat_against": []}
        if self.sc is not None:
            self.j["moat_scorecard"] = self.sc
        self.j.update(j_extra or {})
        self.n = {"ticker": "TST", "engine_release": release, "latest_period_end": LPE, "fragility_flags": [],
                  "content_hash": "h" * 64, "cik": 1}
        self.n.update(n_extra or {})
        self.sic = sic

    def ev(self, is_57=None, industry=None, prior=None):
        is57 = M._facts.is_rulings_run(self.n) if is_57 is None else is_57
        try:
            return M.evaluate(self.folder, self.n, self.j, facts={f["id"]: f for f in self.facts}, is_57=is57, sic=self.sic,
                              industry=industry, prior=prior)
        finally:
            pass

    def close(self):
        shutil.rmtree(self.tmp, ignore_errors=True)


def run_case(**kw):
    c = Case(**{k: v for k, v in kw.items() if k not in ("mut", "is_57", "industry", "prior")})
    try:
        if kw.get("mut"):
            kw["mut"](c)
        return c.ev(is_57=kw.get("is_57"), industry=kw.get("industry"), prior=kw.get("prior"))
    finally:
        c.close()


def refuses(needles, **kw):
    try:
        ev = run_case(**kw)
    except M.MoatRefusal as e:
        msg = str(e)
        for s in ([needles] if isinstance(needles, str) else needles):
            assert s in msg, f"{s!r} not in refusal: {msg}"
        return msg
    raise AssertionError(f"expected a refusal containing {needles!r}; evaluate returned evidence {ev.get('evidence_score')}")


def passes(**kw):
    ev = run_case(**kw)
    json.dumps(ev, allow_nan=False)
    return ev


def mutate_sc(fn):
    def m(c):
        fn(c.sc)
        c.j["moat_scorecard"] = c.sc
    return m


def with_facts(extra):
    return base_facts() + extra


# ---------------------------------------------------------------- 1. one returns function
def test_capital_returns_shared():
    rs = rows_of([0.18, 0.20, 0.22, 0.25, 0.30], goodwill=100.0, intangibles=50.0)
    c = Case(rows=rs, sc=None, release="5.6.0")
    try:
        src, rows, _ = M.window_rows(c.folder, c.n)
        assert src == "fundamentals.json"
        for r, raw in zip(rows, rs):
            cr = F.capital_returns_from_row(raw)
            for k in F.CAPITAL_RETURNS_KEYS:
                assert r[k] == cr[k], (k, r[k], cr[k])
    finally:
        c.close()
    # a CSV-only folder: rows through capital_returns_from_row(csv_row(r), csv=True), net income + tax without OI
    csv_rows = [{"period_end": f"{y}-12-31", "fy_label": str(y), "revenue": 1000, "net_income": 80, "operating_income": "",
                 "ocf": 120, "capex": 30, "capex_assumed_zero": "False", "equity": 500, "cash": 50, "debt_current": 10,
                 "debt_lt": 90, "tax": 20} for y in YEARS]
    c = Case(rows=[], csv_rows=csv_rows, sc=None, release="5.6.0")
    try:
        src, rows, _ = M.window_rows(c.folder, c.n)
        assert src == "financials_history.csv" and len(rows) == 5
        for r, raw in zip(rows, csv_rows):
            cr = F.capital_returns_from_row(M.csv_row({k: str(v) for k, v in raw.items()}), csv=True)
            assert r["roic"] == cr["roic"] and r["roic_basis"] == "net_income_plus_tax"
            assert r["roic"] == 100 * (1 - 20 / 100) / (500 + 100 - 50)
    finally:
        c.close()
    # the 5.5 CSV shape: debt_total is the engine's assembled debt, assets / liabilities are read (ROA measurable)
    r55 = M.csv_row({"period_end": "2025-12-31", "fy_label": "2025", "debt_total": "300", "debt_current": "10", "debt_lt": "90",
                     "assets": "2000", "liabilities": "1500", "cash": "40"})
    assert r55["total_debt"] == 300.0 and r55["assets"] == 2000.0 and r55["liabilities"] == 1500.0 and r55["cash"] == 40.0
    assert M.csv_row({"period_end": "2025-12-31", "debt_current": "10"})["total_debt"] == 10.0
    assert M.csv_row({"period_end": "2025-12-31"})["total_debt"] is None
    # moat_scorecard.py carries no tax-rate or EBIT-fallback expression of its own
    src_text = open(os.path.join(SYS, "moat_scorecard.py"), encoding="utf-8").read()
    assert "0.21" not in src_text, "the 21% default lives in fundamentals.row_tax_rate only"
    assert not re.search(r"pretax\w*[\"'\]\)]*\s*[-+*/]|[-+*/]\s*\(?\s*\w*\[?[\"']?pretax", src_text), "no EBIT arithmetic on pretax income"


def test_scorecard_reads_the_same_numbers():
    """F-8: a refreshed fundamentals.json row's recorded returns keys equal capital_returns_from_row bit for bit, and the
    scorecard's ROIC / tangible series are the file's; repo-wide over every committed fundamentals.json once refreshed
    (files without `roic` are skipped)."""
    rs = rows_of([0.18, 0.20, 0.22, 0.25, 0.30], goodwill=100.0, intangibles=50.0)
    refreshed = [dict(r, **F.capital_returns_from_row(r)) for r in rs]
    c = Case(rows=refreshed, sc=None, release="5.6.0")
    try:
        ev = c.ev()
        ser = ev["pillars"]["returns_on_capital"]["series"]
        for e, r in zip(ser, refreshed):
            assert e["roic"] == M._r(r["roic"]) and e["roic_tangible"] == M._r(r["roic_tangible"])
    finally:
        c.close()
    checked = 0
    for fp in glob.glob(os.path.join(REPO, "*", "fundamentals.json")):
        doc = json.load(open(fp, encoding="utf-8"))
        for r in doc.get("annual") or []:
            if "roic" not in r:
                continue
            cr = F.capital_returns_from_row(r)
            for k in F.CAPITAL_RETURNS_KEYS:
                assert r.get(k) == cr[k], (fp, r.get("period_end"), k)
            checked += 1
    print(f"   F-8 repo-wide: {checked} refreshed fundamentals.json row(s) compared")


# ---------------------------------------------------------------- 2-5. returns_on_capital
def test_governing_selection():
    roic = M.pillar_returns_on_capital
    rs = [M.year_record(r, False) for r in rows_of([0.2] * 5, goodwill=600.0, intangibles=40.0)]   # 64% of IC
    m, lad, why = M.governing("industrial", rs)
    assert (m, lad) == ("roic_tangible", "default") and "64.00% of invested capital (> 30%): tangible ROIC governs" in why
    rs = [M.year_record(r, False) for r in rows_of([0.2] * 5, goodwill=250.0)]                        # 25%
    assert M.governing("industrial", rs)[0] == "roic" and "(<= 30%): ROIC governs" in M.governing("industrial", rs)[2]
    assert M.governing("financial_balance_sheet", rs)[:2] == ("roe", "roe")
    assert M.governing("real_assets", rs)[:2] == ("roic", "real_assets")
    rs = [M.year_record(r, False) for r in rows_of([0.2] * 5, equity=-100.0)]                         # IC <= 0 every year
    assert M.governing("industrial", rs)[0] == "roic" and "not positive in any year" in M.governing("industrial", rs)[2]
    p = roic("industrial", "fundamentals.json", rs)
    assert p["metric"] == "roic" and p["ladder"] == "default" and p["governing_reason"]


def test_ladders_and_cycle_floor():
    def score(vals, btype="industrial", **kw):
        return M.pillar_returns_on_capital(btype, "x", [M.year_record(r, False) for r in rows_of(vals, **kw)])["score"]
    assert score([0.22] * 5) == 2 and score([0.22, 0.22, 0.08, 0.22, 0.22]) == 1, "+2 needs every year >= the 10% floor"
    assert score([0.17] * 5) == 1 and score([0.12] * 5) == 0 and score([0.07] * 5) == -1 and score([0.03] * 5) == -2
    assert score([0.09] * 5, "real_assets") == 2 and score([0.065] * 5, "real_assets") == 1
    assert score([0.05] * 5, "real_assets") == 0 and score([0.03] * 5, "real_assets") == -1 and score([0.01] * 5, "real_assets") == -2
    assert score([0.09, 0.09, 0.03, 0.09, 0.09], "real_assets") == 1, "real-asset floor 4%"
    assert score([0.16] * 5, "financial_balance_sheet") == 2 and score([0.13] * 5, "financial_balance_sheet") == 1
    assert score([0.10] * 5, "financial_balance_sheet") == 0 and score([0.07] * 5, "financial_balance_sheet") == -1
    assert score([0.05] * 5, "financial_balance_sheet") == -2
    assert score([0.16, 0.16, 0.08, 0.16, 0.16], "financial_balance_sheet") == 1, "ROE floor 9%"
    # fewer than 3 valid years: insufficient, weight 0
    p = M.pillar_returns_on_capital("industrial", "x", [M.year_record(r, False) for r in rows_of([0.2, 0.2])])
    assert p["status"] == "insufficient_data" and p["score"] is None and "at least 3 needed" in p["reason"]
    core, w = M.core_evidence({"returns_on_capital": p})
    assert core is None and w == 0
    # 03c decision 2: tangible-governed +2 also needs the plain ROIC median >= 10% (else +1)
    rs = [M.year_record(r, False) for r in rows_of([0.08] * 5, goodwill=800.0)]   # tangible 40%, plain 8%
    p = M.pillar_returns_on_capital("industrial", "x", rs)
    assert p["metric"] == "roic_tangible" and p["score"] == 1 and p["plain_roic_check"]["capped"] is True
    assert p["plain_roic_check"]["median"] == 0.08 and p["plain_roic_check"]["line"] == 0.10
    rs = [M.year_record(r, False) for r in rows_of([0.12] * 5, goodwill=500.0)]   # tangible 24%, plain 12%
    p = M.pillar_returns_on_capital("industrial", "x", rs)
    assert p["score"] == 2 and p["plain_roic_check"]["capped"] is False and p["sustained_plus2"] is True


def test_unbounded_and_unstable():
    # VRSN shape: profit on negative invested capital every year -> +2 sustained, no negative number anywhere
    c = Case(rows=rows_of([0.3] * 5, equity=-2154.0), sc=None, release="5.6.0")
    try:
        ev = c.ev()
        p = ev["pillars"]["returns_on_capital"]
        assert p["score"] == 2 and p["sustained_plus2"] is True and p["median"] is None and p["median_note"] == "unbounded_high"
        assert all(s["roic"] is None and s["roic_note"] == "unbounded_high" for s in p["series"])
        assert ev["governing"]["median_note"] == "unbounded_high"
        json.dumps(ev, allow_nan=False)
    finally:
        c.close()
    # DUOL shape: losses on non-positive capital -> -inf years
    c = Case(rows=rows_of([-0.1] * 5, equity=-50.0), sc=None, release="5.6.0")
    try:
        p = c.ev()["pillars"]["returns_on_capital"]
        assert p["score"] == -2 and p["median_note"] == "loss_on_nonpositive_capital" and p["min"] is None
    finally:
        c.close()
    # a 3%-of-revenue denominator -> ROIC_DENOMINATOR_UNSTABLE in moat_evidence.flags
    c = Case(rows=rows_of([0.2] * 5, equity=60.0), sc=None, release="5.6.0")
    try:
        ev = c.ev()
        assert "ROIC_DENOMINATOR_UNSTABLE" in ev["flags"] and ev["pillars"]["returns_on_capital"]["median_note"] == "unbounded_high"
        json.dumps(ev, allow_nan=False)
    finally:
        c.close()
    assert M._median([-math.inf, -math.inf, math.inf, math.inf]) == -math.inf, "an undefined pair takes the lower value"
    assert M._median([0.1, 0.2, math.inf, math.inf]) == math.inf and M._median([0.1, 0.3]) == 0.2


def test_side_by_side_measures():
    # HPQ shape: negative equity, ROE n/m (never the -300% figure) in moat_evidence and key_numbers.md
    rs = rows_of([0.3] * 5, equity=-1200.0, total_debt=1500.0, cash=200.0, goodwill=400.0)
    for r in rs:
        r["roe"] = r["net_income"] / r["equity"]   # what fundamentals.json stores: -0.25 (sign-meaningless)
    c = Case(rows=rs, sc=None, release="5.6.0")
    try:
        ev = c.ev()
        p = ev["pillars"]["returns_on_capital"]
        assert all(s["roe_note"] == "negative_equity" and s["roe"] is None for s in p["series"])
        assert set(p["medians"]) == {"roic", "roic_note", "roic_tangible", "roic_tangible_note", "roe", "roe_note", "roa"}
        assert p["medians"]["roe"] is None and p["roa_cross_check"]["applies"] is True
        txt = "\n".join(M.key_numbers_lines(ev))
        assert "ROE n/m" in txt and "n/m (negative equity)" in txt and "-25.00%" not in txt and "-25%" not in txt
        assert "Side by side, 5-FY medians: ROIC" in txt and "ROA 15.00%" in txt
        assert -0.25 not in M.numeric_leaves(ev)
    finally:
        c.close()
    # a balance-sheet financial: ROA printed without the 7% line
    c = Case(rows=rows_of([0.14] * 5), sc=None, release="5.6.0", sic="6022")
    try:
        ev = c.ev()
        assert ev["business_type_hint"] == "financial_balance_sheet" and ev["pillars"]["returns_on_capital"]["metric"] == "roe"
        assert ev["pillars"]["returns_on_capital"]["roa_cross_check"]["applies"] is False
        assert "cross-check" not in "\n".join(M.key_numbers_lines(ev))
    finally:
        c.close()


def industry_doc(groups, members, built="2026-10-21"):
    return {"schema": 1, "built": built, "members": members, "groups": groups, "_sha256": "ab" * 32}


def _members(ladder, vals, sic="3823", prefix="P", start_cik=100):
    return {f"{prefix}{i}": {"sic": sic, "cik": start_cik + i, "ladder": ladder, "measure": "roic",
                             "median": None if v in (math.inf, -math.inf) else v,
                             "median_note": "unbounded_high" if v == math.inf else ("loss_on_nonpositive_capital" if v == -math.inf else None)}
            for i, v in enumerate(vals)}


def test_industry_structure_same_ladder():
    roc = M.pillar_returns_on_capital("industrial", "x", [M.year_record(r, False) for r in rows_of([0.18] * 5)])
    mem = _members("default", [0.10, 0.12, 0.20, 0.25, 0.30, math.inf, -math.inf])
    mem["TST"] = {"sic": "3823", "cik": 1, "ladder": "default", "measure": "roic", "median": 0.99}   # the company itself
    mem["TSTB"] = {"sic": "3823", "cik": 1, "ladder": "default", "measure": "roic", "median": 0.98}  # same CIK: a dual class
    g = {"default|4:3823": {"members": sorted(mem), "label": "Industrial instruments"}}
    p = M.pillar_industry_structure("industrial", "TST", "3823", roc, industry_doc(g, mem), cik=1)
    assert p["status"] == "measured" and p["group"] == "4:3823" and p["level"] == 4 and p["ladder"] == "default"
    assert p["peers"] == 6 and p["peers_dropped"] == 1, "self and its same-CIK class excluded; the -inf peer dropped and counted"
    assert p["median"] == 0.225 and p["score"] == 2 and p["rank"] == 5 and p["of"] == 7, p   # 4 peers above 18%
    assert p["file_built"] == "2026-10-21" and p["file_sha256"] == "ab" * 32 and p["weight"] == 1.5
    # fallback 4 -> 3 -> 2 until >= 5 same-ladder peers; the company's ladder only
    mem2 = _members("default", [0.1, 0.1, 0.1], sic="3823") | _members("default", [0.3] * 5, sic="3829", prefix="Q", start_cik=200)
    g2 = {"default|4:3823": {"members": [k for k in mem2 if k.startswith("P")]},
          "default|3:382": {"members": sorted(mem2), "label": "SIC 382x · Measuring"}}
    p = M.pillar_industry_structure("industrial", "TST", "3823", roc, industry_doc(g2, mem2), cik=1)
    assert p["level"] == 3 and p["peers"] == 8 and p["label"] == "SIC 382x · Measuring"
    # the waste-hauler case: 13 real-asset utilities + 2 default-ladder peers in 2:49 -> insufficient, not -2
    util = _members("real_assets", [0.049] * 13, sic="4911", prefix="U")
    waste = _members("default", [0.18, 0.20], sic="4953", prefix="W", start_cik=300)
    g3 = {"real_assets|2:49": {"members": sorted(util)}, "default|2:49": {"members": sorted(waste)}}
    p = M.pillar_industry_structure("industrial", "WCN", "4953", roc, industry_doc(g3, util | waste))
    assert p["status"] == "insufficient_data" and p["score"] is None
    assert p["reason"] == "fewer than 5 same-ladder peers (default) at SIC 2-digit 49"
    # a mixed REIT group: an equity REIT is scored on its 6 real-asset peers only, never the ROE-ladder mortgage REITs
    reits = _members("real_assets", [0.07, 0.075, 0.08, 0.06, 0.09, 0.07], sic="6798", prefix="R")
    mreit = _members("roe", [0.12, 0.10], sic="6798", prefix="M", start_cik=400)
    g4 = {"real_assets|4:6798": {"members": sorted(reits)}, "roe|4:6798": {"members": sorted(mreit)}}
    roc_ra = M.pillar_returns_on_capital("real_assets", "x", [M.year_record(r, False) for r in rows_of([0.07] * 5)])
    p = M.pillar_industry_structure("real_assets", "EXR", "6798", roc_ra, industry_doc(g4, reits | mreit))
    assert p["peers"] == 6 and p["ladder"] == "real_assets" and p["median"] == 0.0725 and p["score"] == 1
    # missing file / no SIC
    assert M.pillar_industry_structure("industrial", "TST", "3823", roc, None)["reason"].endswith("missing or unreadable")
    assert M.pillar_industry_structure("industrial", "TST", None, roc, industry_doc(g, mem))["reason"] == "no SIC on record"
    # an unmeasured company has no rank
    roc_u = M.pillar_returns_on_capital("industrial", "x", [M.year_record(r, False) for r in rows_of([0.2, 0.2])])
    p = M.pillar_industry_structure("industrial", "TST", "3823", roc_u, industry_doc(g, mem), cik=1)
    assert p["rank"] is None and p["of"] == 7


# ---------------------------------------------------------------- 7. capital intensity and scale economics (03's rules)
def test_capital_intensity_and_scale_unchanged():
    def ci(ratios, zero_year=False, neg_ocf=False):
        rows = []
        for i, (y, x) in enumerate(zip(YEARS, ratios)):
            ocf = -10 if (neg_ocf and i == 0) else 100
            rows.append({"period_end": f"{y}-12-31", "fy_label": str(y), "revenue": 1000, "ocf": ocf, "capex": x * 100,
                         "capex_assumed_zero": "True" if (zero_year and i == 1) else "False"})
        c = Case(rows=[], csv_rows=rows, sc=None, release="5.6.0")
        try:
            return M.pillar_capital_intensity("industrial", c.folder)
        finally:
            c.close()
    assert [ci([m] * 5)["score"] for m in (0.10, 0.25, 0.45, 0.70, 1.20)] == [2, 1, 0, -1, -2]
    p = ci([0.1] * 5, zero_year=True)
    assert p["series"][1]["note"] == "capex not filed (assumed zero)" and p["median"] == 0.1
    p = ci([0.6, 0.6, 0.6, 0.9, 0.9], neg_ocf=True)
    assert p["series"][0]["note"] == "ocf <= 0" and p["median"] == 0.9 and p["score"] == -2, "OCF <= 0 counts +inf"
    assert M.pillar_capital_intensity("real_assets", "/nowhere")["status"] == "not_applicable"
    assert M.pillar_capital_intensity("financial_balance_sheet", "/nowhere")["status"] == "not_applicable"

    def se(revs, margins):
        rs = [M.year_record(row(y, revenue=rv, operating_income=rv * m), False) for y, rv, m in zip(YEARS, revs, margins)]
        return M.pillar_scale_economics("industrial", "x", rs)
    grow = [1000 * 1.1 ** i for i in range(5)]
    flat = [1000 * 1.01 ** i for i in range(5)]
    assert se(grow, [0.10, 0.10, 0.12, 0.14, 0.14])["score"] == 2           # g 10%, +4pp
    assert se(grow, [0.20, 0.20, 0.17, 0.14, 0.14])["score"] == -2          # g 10%, -6pp
    assert se(flat, [0.10, 0.10, 0.12, 0.14, 0.14])["score"] == 1, "cost-cutting is not scale: capped at +1"
    p = se(grow, [0.10, 1.50, 0.12, 0.14, 0.14])
    assert p["series"][1]["note"].startswith("operating income above revenue") and p["status"] == "measured"
    p = se(grow, [0.10, 1.50, 1.50, 0.14, 0.14])
    assert p["status"] == "insufficient_data", "SBAC shape: fewer than 4 valid years"
    assert M.pillar_scale_economics("financial_balance_sheet", "x", [])["status"] == "not_applicable"


# ---------------------------------------------------------------- 8. evidence
def test_evidence_core_and_supporting():
    assert set(M.WEIGHTS) == set(M.CORE) and len(M.CORE) == 11 and sum(M.WEIGHTS.values()) == 16.0
    assert not set(M.WEIGHTS) & set(M.SUPPORTING)
    top = {k: {"status": "scored", "score": M.RANGES[k][1]} for k in M.CORE}
    bot = {k: {"status": "scored", "score": M.RANGES[k][0]} for k in M.CORE}
    assert M.core_evidence(top) == (10.0, 16.0), "all at the top of their range incl. erosion_risks +1"
    assert M.core_evidence(bot)[0] == 0.0
    mix = {"returns_on_capital": {"status": "measured", "score": 1}, "retention": {"status": "scored", "score": -1},
           "pricing_power": {"status": "not_applicable", "score": None}, "concentration": {"status": "unsupported_neutral", "score": 0}}
    assert M.core_evidence(mix) == (round(5 + 2.5 * (3 * 1 - 2 * 1) / 5, 2), 5.0), "+-2 pillars give 5 + 2.5 x mean; excluded statuses carry no weight"

    def adj(scores):
        sup = {k: (na() if v is None else ({"score": v, "rationale": "r", "facts": []} if v == 0 else
                                         {"score": v, "rationale": "r", "facts": ["E1"]})) for k, v in zip(M.SUPPORTING, scores)}
        ctx = {"facts": {"E1": fact("E1", "launch", "FY2025", 1, unit="count", type="event",
                                    used=tuple(f"moat:{k}" for k in M.SUPPORTING), kind="filing")},
               "calendar": {}, "lpe": LPE}
        return M.check_supporting(sup, ctx)
    # event facts stand alone only on execution / management: build the +1 cases on those two, and pq/ms with series below
    out, status = adj([None, None, 1, 1])
    assert out["adjustment"] == 0.5 and status == "scored", "product_quality N/A ... execution +1, management +1: 2 / 4"
    out, status = adj([None, None, None, -2])
    assert out["adjustment"] == -0.5, "management -2 alone moves the evidence by 0.50 (03c decision 11)"
    out, status = adj([None, None, None, None])
    assert out["adjustment"] == 0.0 and status == "none_applicable"
    out, status = adj([0, 0, 1, 0])
    assert out["adjustment"] == 0.25 and out["product_quality"]["status"] == "unsupported_neutral"
    assert M.evidence(9.6, 1.0) == 10.0 and M.evidence(0.4, -1.0) == 0.0 and M.evidence(None, 0.5) is None
    # four at +1 -> +1.00; (+1, 0, +1, -1) -> +0.25 (series facts for product_quality / market_share)
    fx = with_facts(series(("S1", "S2", "S3"), "net_promoter", (0.5, 0.52, 0.55), used=("moat:product_quality",))
                    + series(("S4", "S5", "S6"), "unit_share", (0.2, 0.21, 0.22), used=("moat:market_share",))
                    + [fact("S7", "on_time", "FY2025", 1, unit="count", type="event", used=("moat:execution", "moat:management"))])

    def sup_ev(pq, ms, ex, mg):
        def m(c):
            c.sc["supporting"] = {"product_quality": {"score": pq, "rationale": "r", "facts": ["S1", "S2", "S3"] if pq else []},
                                  "market_share": {"score": ms, "rationale": "r", "facts": ["S4", "S5", "S6"] if ms else []},
                                  "execution": {"score": ex, "rationale": "r", "facts": ["S7"] if ex else []},
                                  "management": {"score": mg, "rationale": "r", "facts": ["S7"] if mg else []}}
        return passes(facts=fx, mut=m)
    e = sup_ev(1, 1, 1, 1)
    assert e["supporting_adjustment"] == 1.0 and e["supporting"]["sum"] == 4 and e["supporting"]["divisor"] == 4.0
    assert e["evidence_score"] == min(10.0, round(e["core_evidence_score"] + 1.0, 2))
    assert sup_ev(1, 0, 1, -1)["supporting_adjustment"] == 0.25
    assert sup_ev(1, 0, 0, 0)["supporting_adjustment"] == 0.25, "a fact-less 0 counts (fails on the round-2 rule: +1.00)"
    # the weight floor counts core pillars only: core weight 7.5 refuses G2 however many supporting factors are scored
    def thin(c):
        for k in ("retention", "pricing_power", "switching_costs"):
            c.sc["pillars"][k] = {"score": 0, "rationale": "r", "facts": []}
        c.sc["sources"] = []
        c.j["moat_score"] = 3
        c.sc["supporting"] = {"product_quality": {"score": 1, "rationale": "r", "facts": ["S1", "S2", "S3"]},
                              "market_share": {"score": 1, "rationale": "r", "facts": ["S4", "S5", "S6"]},
                              "execution": {"score": 1, "rationale": "r", "facts": ["S7"]},
                              "management": {"score": 1, "rationale": "r", "facts": ["S7"]}}
    refuses("moat evidence weight 7.5 < 8", facts=fx, mut=thin)


# ---------------------------------------------------------------- 9-10b. sources and caps
SRC_FACTS = ([fact("F201", "license_grant", "FY2025", 1, unit="count", type="event", used=("moat:sources",))]
             # ([Integrate L2] precision 1: at 40.00% the FY2023 share would equal the synthetic rows' gross margin 0.40 at
             # 4 significant digits, which L2's duplicate rule refuses as an undeclared folder figure, 02 §4.5)
             + series(("F202", "F203", "F204"), "aftermarket_revenue_share", (0.40, 0.42, 0.44), used=("moat:sources",),
                      precision=1)
             + [fact("F205", "competitor_count", "FY2025", 3, unit="count", type="actual", used=("moat:sources",)),
                fact("F206", "patent_years_left", "FY2025", 8, unit="count", type="event", unit_label="years", used=("moat:sources",)),
                fact("F207", "patent_years_left", "FY2025", 3.5, unit="count", type="event", unit_label="years", used=("moat:sources",)),
                fact("F208", "analyst_brand_rank", "FY2025", 1, unit="count", type="event", kind="third_party", used=("moat:sources",)),
                fact("F209", "user_count", "FY2025", 1e6, unit="count", type="event", used=("moat:sources",))]
             + [fact(f"F21{i}", "unit_cost_lead", f"FY{y}", 0.05, used=("moat:sources",)) for i, y in enumerate(YEARS)]
             + series(("F220", "F221", "F222"), "revenue", (1e9, 1.1e9, 1.2e9), unit="USD", used=("moat:sources",)))


def src(typ, sub, strength="narrow", facts=("F201",), metrics=(), **kw):
    s = {"type": typ, "subtype": sub, "strength": strength, "facts": list(facts), "metrics": list(metrics), "rationale": "fixture"}
    s.update(kw)
    return s


def with_sources(*sources, moat=None, pillars=None, reason=None):
    def m(c):
        c.sc["sources"] = list(sources)
        for k, v in (pillars or {}).items():
            c.sc["pillars"][k] = v
        if moat is not None:
            c.j["moat_score"] = moat
        if reason is not None:
            c.sc["moat_divergence_reason"] = reason
    return m


def ok_source(s, **kw):
    return passes(facts=with_facts(SRC_FACTS), mut=with_sources(s, **{k: v for k, v in kw.items() if k in ("moat", "pillars", "reason")}),
                  **{k: v for k, v in kw.items() if k not in ("moat", "pillars", "reason")})


def bad_source(needle, *sources, **kw):
    return refuses(needle, facts=with_facts(SRC_FACTS), mut=with_sources(*sources, **{k: v for k, v in kw.items() if k in ("moat", "pillars", "reason")}),
                   **{k: v for k, v in kw.items() if k not in ("moat", "pillars", "reason")})


EXTRA_FOR = {("intangible_assets", "patent"): {"expiry_years": {"fact": "F206"}, "facts": ("F206",)},
             ("switching_costs", "installed_base_aftermarket"): {"facts": ("F202", "F203", "F204")},
             ("efficient_scale", "niche"): {"facts": ("F205",), "competitors": ["Rival One", "Rival Two", "Rival Three"]},
             ("efficient_scale", "infrastructure"): {"facts": ("F205",), "competitors": ["Rival One", "Rival Two", "Rival Three"]},
             ("counter_positioning", "business_model"): {"incumbents": ["agent-network carriers"]}}


def test_sources_rules():
    # every (type, subtype) of the closed enum is accepted once (narrow, with the evidence its rules need)
    for typ, subs in M.SOURCE_TYPES.items():
        for sub in subs:
            kw = dict(EXTRA_FOR.get((typ, sub), {}))
            facts = kw.pop("facts", ("F201",))
            ev = ok_source(src(typ, sub, facts=facts, **kw))
            assert ev["sources"]["items"][0]["type"] == typ and ev["sources"]["count"] == 1, (typ, sub)
    # S1: a bad subtype, a duplicate, an unknown key (no `supports` anywhere), a non-source type
    bad_source("subtype 'brand' is not a subtype of switching_costs (allowed: workflow_training, data_integration, contractual, "
               "risk_of_change, embedded_component, installed_base_aftermarket)", src("switching_costs", "brand"))
    bad_source("is declared twice", src("switching_costs", "embedded_component", facts=("F10",)),
               src("switching_costs", "embedded_component", facts=("F10",)))
    bad_source("unknown key(s) ['supports']", src("switching_costs", "embedded_component", facts=("F10",), supports="x"))
    bad_source("type 'market_share' is not a moat source", src("market_share", "x"))
    bad_source("unknown key(s) ['competitors']", src("switching_costs", "embedded_component", facts=("F10",), competitors=["A1"]))
    bad_source("unknown key(s) ['expiry_years']", src("intangible_assets", "brand", expiry_years={"fact": "F206"}))
    # S1a: every retired alias refuses with its replacement
    for (t0, s0), (t1, s1) in M.SUBTYPE_ALIASES.items():
        bad_source(f"{t0}/{s0} is a retired name — use {t1}/{s1}", src(t0, s0))
    # S2 no support; S3 a metric at +0; W8 (a) returns on capital with no fact
    bad_source("has no support — cite facts.json ids", src("cost_advantage", "location", facts=()))
    bad_source("cites metric scale_economics, which scored +0 — a metric supports a source only at +1 or better",
               src("cost_advantage", "location", metrics=("scale_economics",)))
    bad_source("cites returns_on_capital with no fact", src("cost_advantage", "location", facts=(), metrics=("returns_on_capital",)),
               rows=rows_of([0.25] * 5))
    # a fact without moat:sources in used_for refuses
    bad_source("cites F1, but F1 does not list used_for moat:sources", src("cost_advantage", "location", facts=("F1",)))
    # S4 brand needs pricing_power or retention at +1
    zero = {"score": 0, "rationale": "r", "facts": []}
    bad_source("intangible_assets/brand needs pricing_power or retention at +1 or better", src("intangible_assets", "brand"),
               pillars={"pricing_power": zero, "retention": zero})
    ok_source(src("intangible_assets", "brand"), pillars={"pricing_power": zero})
    # S5 switching_costs needs its pillar at +1; S6 network effects need reach or retention at +1
    bad_source("is declared but the switching_costs pillar scores +0", src("switching_costs", "contractual"),
               pillars={"switching_costs": zero})
    bad_source("needs reach_and_growth or retention at +1 or better", src("network_effects", "user_network"),
               pillars={"retention": zero})
    # S7 size advantage with scale_economics -1 (margins fell as revenue grew)
    falling = [row(y, revenue=2000 * 1.1 ** i, operating_income=2000 * 1.1 ** i * m) for i, (y, m) in
               enumerate(zip(YEARS, (0.20, 0.20, 0.18, 0.17, 0.17)))]
    bad_source("size_advantage/distribution_density with scale_economics -1 (margins fell as revenue grew",
               src("size_advantage", "distribution_density"), rows=falling)
    # S8 installed-base aftermarket needs an aftermarket / recurring revenue share series
    bad_source("needs an aftermarket or recurring revenue share series", src("switching_costs", "installed_base_aftermarket"))
    ok_source(src("switching_costs", "installed_base_aftermarket", facts=("F202", "F203", "F204")))
    # S9 efficient scale: competitor_count (<= 5, named, not third-party), returns above the cost of capital, no price war
    es = lambda **kw: src("efficient_scale", "niche", facts=("F205",), competitors=["Rival One", "Rival Two", "Rival Three"], **kw)  # noqa: E731
    bad_source("needs a competitor_count fact", src("efficient_scale", "infrastructure", competitors=["A1"]))
    seven = [fact("F205", "competitor_count", "FY2025", 7, unit="count", type="actual", used=("moat:sources",))]
    refuses("needs a competitor_count fact of 5 or fewer", facts=with_facts([f for f in SRC_FACTS if f["id"] != "F205"] + seven),
            mut=with_sources(es()))
    bad_source("names 2 competitors but its competitor_count fact (F205) says 3",
               src("efficient_scale", "niche", facts=("F205",), competitors=["Rival One", "Rival Two"]))
    bad_source("with governing roic median 7.40% (< 10%)", es(), rows=rows_of([0.074] * 5))
    ok_source(es(), rows=rows_of([0.12] * 5))
    # real assets: 4.5% refuses on the 6% line, 6.5% passes (a utility SIC locks real_assets)
    def ra(c):
        c.sc["business_type"] = "real_assets"
        c.sc["pillars"]["switching_costs"] = na()
        c.sc["sources"] = [es()]
    refuses("(< 6% on the real-asset ladder)", facts=with_facts(SRC_FACTS), rows=rows_of([0.045] * 5), sic="4911", mut=ra)
    passes(facts=with_facts(SRC_FACTS), rows=rows_of([0.065] * 5), sic="4911", mut=ra)
    # 03c decision 15: the ROE line is 12% (a bank: 11.0% refuses, 12.5% passes)
    def bank(c):
        c.sc["business_type"] = "financial_balance_sheet"
        c.sc["sources"] = [es()]
    refuses("with governing roe median 11.00% (< 12%)", facts=with_facts(SRC_FACTS), rows=rows_of([0.11] * 5), sic="6022", mut=bank)
    passes(facts=with_facts(SRC_FACTS), rows=rows_of([0.125] * 5), sic="6022", mut=bank)
    neg = {"score": -1, "rationale": "r", "facts": ["F1", "F2", "F3"]}
    bad_source("with pricing_power -1: returns above the cost of capital must come without a price war", es(),
               pillars={"pricing_power": neg})
    sub_threat = {"score": -1, "rationale": "r", "facts": ["F14"], "threats": [{"type": "subsidized_competitor", "facts": ["F14"]}]}
    bad_source("and a subsidized_competitor threat", es(), pillars={"erosion_risks": sub_threat})
    # W1 third-party-only wide; W8 (b) metric-only wide; a metric-only narrow source passes
    bad_source("is wide on third-party facts only (F208)", src("intangible_assets", "brand", strength="wide", facts=("F208",)))
    capex_csv = [{"period_end": f"{y}-12-31", "fy_label": str(y), "revenue": 2000, "ocf": 400, "capex": 40,
                  "capex_assumed_zero": "False"} for y in YEARS]
    ok_source(src("cost_advantage", "location", facts=(), metrics=("capital_intensity",)), csv_rows=capex_csv)
    bad_source("is wide on metrics only (capital_intensity): a source with no fact is narrow at most",
               src("cost_advantage", "location", strength="wide", facts=(), metrics=("capital_intensity",)), csv_rows=capex_csv)
    # W2 process: wide only on a 5-FY lead series (03c decision 14: no extra pillar condition)
    bad_source("covers 5 fiscal years with a lead every year (3 FY cited)",
               src("cost_advantage", "process", strength="wide", facts=("F212", "F213", "F214")))
    ok_source(src("cost_advantage", "process", strength="wide", facts=("F210", "F211", "F212", "F213", "F214")))
    lag = [dict(f, value=-0.01) if f["id"] == "F212" else f for f in SRC_FACTS]
    refuses("with a lead every year", facts=with_facts(lag),
            mut=with_sources(src("cost_advantage", "process", strength="wide", facts=("F210", "F211", "F212", "F213", "F214"))))
    # W3 consumer retail switching costs are narrow; elsewhere wide needs pricing_power +1
    def retail(c):
        c.sc["business_type"] = "consumer_brands_retail"
        c.sc["pillars"]["customer_regard"] = {"score": 0, "rationale": "r", "facts": []}
        c.sc["sources"] = [src("switching_costs", "contractual", strength="wide", facts=("F10",))]
    refuses("is wide at a consumer_brands_retail company", facts=with_facts(SRC_FACTS), mut=retail)
    bad_source("is wide with pricing_power +0", src("switching_costs", "contractual", strength="wide", facts=("F10",)),
               pillars={"pricing_power": zero})
    # W4 size advantage wide needs scale_economics +1
    bad_source("size_advantage/manufacturing_scale is wide with scale_economics +0",
               src("size_advantage", "manufacturing_scale", strength="wide"))
    # W5 patents carry their expiry; under 5 years is narrow
    bad_source("intangible_assets/patent needs expiry_years", src("intangible_assets", "patent", facts=("F206",)))
    bad_source("is wide with 3.5 years of protection left (F207)",
               src("intangible_assets", "patent", strength="wide", facts=("F207",), expiry_years={"fact": "F207"}))
    ok_source(src("intangible_assets", "patent", facts=("F207",), expiry_years={"fact": "F207"}))
    ok_source(src("intangible_assets", "patent", strength="wide", facts=("F206",), expiry_years={"fact": "F206"}), moat=7)
    # W6 counter-positioning: narrow only, incumbents named, at least one fact
    bad_source("counter-positioning is narrow and time-limited",
               src("counter_positioning", "business_model", strength="wide", incumbents=["agent-network carriers"]))
    bad_source("counter_positioning needs incumbents", src("counter_positioning", "business_model", facts=(),
                                                          metrics=("capital_intensity",), incumbents=["agent carriers"]),
               csv_rows=capex_csv)
    bad_source("counter_positioning needs incumbents", src("counter_positioning", "business_model"))
    # W7 customer captivity wide needs retention +1 AND a retention / repeat-purchase series (a revenue series is not one)
    bad_source("is wide without retention at +1 or better and a retention or repeat-purchase series",
               src("customer_captivity", "habit", strength="wide", facts=("F209",)))
    bad_source("is wide without retention at +1 or better and a retention or repeat-purchase series",
               src("customer_captivity", "habit", strength="wide", facts=("F220", "F221", "F222")))
    ok_source(src("customer_captivity", "habit", strength="wide", facts=("F4", "F5", "F6")), moat=7)
    bad_source("is wide without retention", src("customer_captivity", "habit", strength="wide", facts=("F4", "F5", "F6")),
               pillars={"retention": zero, "pricing_power": {"score": 1, "rationale": "r", "facts": ["F1", "F2", "F3"]}})
    # the review's case: two wide metric-only sources backed by returns on capital, ROC +2 sustained, moat 9 -> refused
    bad_source("cites returns_on_capital with no fact",
               src("intangible_assets", "license_regulatory", strength="wide", facts=(), metrics=("returns_on_capital",)),
               src("cost_advantage", "location", strength="wide", facts=(), metrics=("returns_on_capital",)),
               moat=9, rows=rows_of([0.3] * 5))


def test_source_caps():
    reason = "evidence 6.63 vs moat: cycle; 3 [F1]"
    bad_source("moat_score 4 with no source in moat_scorecard.sources: a moat with no moat source (see SOURCE_TYPES) is capped at 3",
               moat=4, reason=reason)
    passes(facts=with_facts(SRC_FACTS), mut=with_sources(moat=3, reason=reason))
    narrow = src("switching_costs", "embedded_component", facts=("F10",))
    bad_source("moat_score 7 rests on one narrow source (switching_costs/embedded_component): one narrow source caps the moat at 6",
               narrow, moat=7)
    ok_source(narrow, moat=6)
    wide = src("switching_costs", "embedded_component", strength="wide", facts=("F10",))
    ev = ok_source(wide, moat=8)
    assert ev["sources"]["cap"]["max_moat"] == 8 and ev["sources"]["widest"] == "wide"
    wide2 = src("customer_captivity", "search_cost_trust", strength="wide", facts=("F4", "F5", "F6"))
    # moat 9: two wide sources and returns_on_capital +2 sustained
    bad_source("returns_on_capital +2, not sustained", wide, wide2, moat=9,
               rows=rows_of([0.25, 0.25, 0.12, 0.25, 0.25], gross_margin=0.4))
    ev = passes(facts=with_facts(SRC_FACTS), mut=with_sources(wide, wide2, moat=9), rows=rows_of([0.25] * 5))
    assert ev["sources"]["cap"] == {"max_moat": 10, "moat_9_ok": True, "reason": "two wide sources and returns_on_capital +2 sustained: 9-10 possible"}
    bad_source("needs two wide sources and returns_on_capital +2 sustained (every year at or above 15%): 1 wide source(s)",
               wide, src("customer_captivity", "search_cost_trust", facts=("F4", "F5", "F6")), moat=9, rows=rows_of([0.25] * 5))
    # counter-positioning (narrow only) caps at 6
    cp = src("counter_positioning", "business_model", incumbents=["agent-network carriers"])
    bad_source("one narrow source caps the moat at 6", cp, moat=7)
    # W8 (c): two narrow sources of which one is metric-only cap at 6; two fact-backed narrow sources reach 7
    capex_csv = [{"period_end": f"{y}-12-31", "fy_label": str(y), "revenue": 2000, "ocf": 400, "capex": 40,
                  "capex_assumed_zero": "False"} for y in YEARS]
    bad_source("rests on 2 sources of which only 1 cites a fact (cost_advantage/location is metric-only): 7+ needs a wide "
               "source or two fact-backed sources", narrow, src("cost_advantage", "location", facts=(), metrics=("capital_intensity",)),
               moat=7, csv_rows=capex_csv)
    ev = passes(facts=with_facts(SRC_FACTS), mut=with_sources(narrow, src("cost_advantage", "location"), moat=7))
    assert ev["sources"]["fact_backed"] == 2 and ev["sources"]["cap"]["max_moat"] == 8


def test_supporting_without_source():
    """10b (M1b): no source; product_quality +1 and execution +1, market_share and management N/A -> adjustment +0.50
    (03c decision 11: sum / 4); moat 3 passes, moat 4 still refuses with the cap message even when the evidence is >= 6
    and a divergence reason is declared."""
    fx = with_facts(series(("S1", "S2", "S3"), "net_promoter", (0.5, 0.52, 0.55), used=("moat:product_quality",))
                    + [fact("S7", "on_time", "FY2025", 1, unit="count", type="event", used=("moat:execution",))])

    def m(moat):
        def f(c):
            c.sc["sources"] = []
            c.j["moat_score"] = moat
            c.sc["moat_divergence_reason"] = "evidence 7.13 against 3: the products carry it [F1]"
            c.sc["supporting"] = {"product_quality": {"score": 1, "rationale": "r", "facts": ["S1", "S2", "S3"]},
                                  "market_share": na(), "execution": {"score": 1, "rationale": "r", "facts": ["S7"]},
                                  "management": na()}
        return f
    ev = passes(facts=fx, mut=m(3))
    assert ev["supporting_adjustment"] == 0.5 and ev["evidence_score"] == round(ev["core_evidence_score"] + 0.5, 2)
    assert ev["evidence_score"] >= 6 and ev["sources"]["count"] == 0 and ev["sources"]["widest"] == "none"
    refuses("moat_score 4 with no source", facts=fx, mut=m(4))


def test_supporting_factors():
    fx = with_facts(series(("S1", "S2", "S3"), "net_promoter", (0.5, 0.52, 0.55), used=("moat:product_quality",))
                    + [fact("S7", "write_down", "FY2025", 1, unit="count", type="event", used=("moat:execution", "moat:management", "moat:product_quality")),
                       fact("S8", "analyst_view", "FY2025", 1, unit="count", type="event", kind="third_party", used=("moat:management",))])

    def sup(**kw):
        def m(c):
            for k, v in kw.items():
                c.sc["supporting"][k] = v
        return m
    refuses("moat_scorecard.supporting.market_share score 2 is outside -1..+1", facts=fx,
            mut=sup(market_share={"score": 2, "rationale": "r", "facts": ["S1", "S2", "S3"]}))
    refuses("moat_scorecard.supporting.product_quality score -2 is outside -1..+1", facts=fx,
            mut=sup(product_quality={"score": -2, "rationale": "r", "facts": ["S1", "S2", "S3"]}))
    refuses("moat_scorecard.supporting.execution score 2 is outside -1..+1", facts=fx,
            mut=sup(execution={"score": 2, "rationale": "r", "facts": ["S7"]}))
    refuses("management score -3 is outside -2..+1 (-2 is reserved for value-destroying reinvestment outside the moat)",
            facts=fx, mut=sup(management={"score": -3, "rationale": "r", "facts": ["S7"]}))
    ev = passes(facts=fx, mut=sup(management={"score": -2, "rationale": "r", "facts": ["S7"]}))
    assert ev["supporting"]["management"]["score"] == -2 and ev["supporting_adjustment"] == -0.5
    refuses("management -2 rests on third-party facts only (S8): third-party-only support caps a score at +-1", facts=fx,
            mut=sup(management={"score": -2, "rationale": "r", "facts": ["S8"]}))
    refuses("moat_scorecard.supporting.execution.score must be an integer", facts=fx,
            mut=sup(execution={"score": True, "rationale": "r", "facts": ["S7"]}))

    def drop(c):
        del c.sc["supporting"]["execution"]
    refuses("moat_scorecard.supporting.execution is missing — score it with facts or declare applicable: false with "
            "not_applicable_reason", facts=fx, mut=drop)
    for bt in M.BUSINESS_TYPES:   # N/A is allowed for every factor at every business type
        def all_na(c, bt=bt):
            c.sc["supporting"] = {k: na() for k in M.SUPPORTING}
        ev = run_case(facts=fx, mut=all_na, is_57=False)
        assert ev["supporting_status"] == "none_applicable"
    refuses("moat_scorecard.supporting.execution scores +1 with no facts", facts=fx,
            mut=sup(execution={"score": 1, "rationale": "r", "facts": []}))
    passes(facts=fx, mut=sup(execution={"score": 1, "rationale": "r", "facts": ["S7"]}))
    refuses("moat_scorecard.supporting.product_quality scores +1 on point facts only (S7) — event facts may stand alone only "
            "on execution and management", facts=fx, mut=sup(product_quality={"score": 1, "rationale": "r", "facts": ["S7"]}))
    refuses("unknown key(s) ['supports']", facts=fx, mut=sup(supports={"score": 1}))
    refuses("has unknown key(s) ['supports']", facts=fx,
            mut=sup(execution={"score": 1, "rationale": "r", "facts": ["S7"], "supports": "switching_costs"}))
    for old, new in (("market_position", "supporting.market_share"), ("reinvestment_discipline", "supporting.management"),
                     ("capital_allocation", "supporting.management"), ("durability_risks", "pillars.erosion_risks")):
        refuses(f"moat_scorecard.pillars.{old} is not a pillar since the M1b amendment — score it under {new}",
                mut=mutate_sc(lambda s, old=old: s["pillars"].__setitem__(old, {"score": 1, "rationale": "r", "facts": []})))


def test_erosion_risks_threats():
    th = lambda score, threats, facts=("F14",): {"score": score, "rationale": "r", "facts": list(facts), "threats": threats}  # noqa: E731
    er = lambda p: mutate_sc(lambda s: s["pillars"].__setitem__("erosion_risks", p))  # noqa: E731
    refuses("erosion_risks scores -1 with no threats", mut=er(th(-1, [])))
    refuses("type 'kodak' is not one of technology_substitution", mut=er(th(-1, [{"type": "kodak", "facts": ["F14"]}])))
    refuses("cites F13, which the pillar's facts do not list", mut=er(th(-1, [{"type": "regulation", "facts": ["F13"]}])))
    refuses("regulation is listed twice", mut=er(th(-1, [{"type": "regulation", "facts": ["F14"]}, {"type": "regulation", "facts": ["F14"]}])))
    ev = passes(mut=er(th(-1, [{"type": "technology_substitution", "facts": ["F14"]}])))
    assert ev["pillars"]["erosion_risks"]["threats"] == [{"type": "technology_substitution", "facts": ["F14"]}]
    refuses("erosion_risks score 2 is outside -2..+1", mut=er(th(2, [])))
    passes(mut=er(th(1, [])))   # +1 on an event fact alone (no threat material within the fade horizon)
    refuses("erosion_risks has unknown key(s) ['threat']", mut=er({"score": 0, "rationale": "r", "facts": [], "threat": []}))
    refuses("retention has unknown key(s) ['threats']",
            mut=mutate_sc(lambda s: s["pillars"]["retention"].__setitem__("threats", [])))


# ---------------------------------------------------------------- 13. erosion test
DOWN = [0.30, 0.29, 0.26, 0.22, 0.20]


def test_erosion_test():
    gm_down = [0.45, 0.44, 0.42, 0.41, 0.40]
    rs = [row(y, v, gross_margin=g) for y, v, g in zip(YEARS, DOWN, gm_down)]
    c = Case(rows=rs, sc=None, release="5.6.0")
    try:
        ev = c.ev()
        e = ev["erosion_test"]
        assert e["status"] == "measured" and e["fired"] is True and e["margin_basis"] == "gross"
        assert e["governing_change_pp"] == -8.5 and e["margin_change_pp"] == -4.0 and "MOAT_EROSION" in ev["flags"]
        assert set(e) >= {"status", "fired", "governing_change_pp", "margin_change_pp", "margin_basis", "slope_governing", "slope_margin"}
    finally:
        c.close()
    # only returns down: not fired
    e = run_case(rows=rows_of(DOWN), sc=None, release="5.6.0")["erosion_test"]
    assert e["status"] == "measured" and e["fired"] is False
    # three years: not measured
    assert run_case(rows=rows_of(DOWN[-3:]), sc=None, release="5.6.0")["erosion_test"]["status"] == "not_measured"
    # no gross margin: the operating margin (operating income / revenue) — fundamentals.json rows only (lane default Q4)
    rs = [row(y, v, gross_margin=None, operating_income=1000 * v, revenue=2000 * (1 + i * 0.25)) for i, (y, v) in enumerate(zip(YEARS, DOWN))]
    e = run_case(rows=rs, sc=None, release="5.6.0")["erosion_test"]
    assert e["status"] == "measured" and e["margin_basis"] == "operating" and e["fired"] is True, e
    # a financial with no gross margin and no operating-income tag: not measured
    rs = [row(y, v, gross_margin=None, operating_income=None) for y, v in zip(YEARS, DOWN)]
    assert run_case(rows=rs, sc=None, release="5.6.0", sic="6022")["erosion_test"]["status"] == "not_measured"
    # a CSV-only folder is never measured
    csv_rows = [{"period_end": f"{y}-12-31", "fy_label": str(y), "revenue": 2000, "operating_income": 1000 * v, "net_income": 1000 * v,
                 "tax": 0, "equity": 1000, "cash": 0, "debt_current": 0, "debt_lt": 0, "ocf": 100, "capex": 10,
                 "capex_assumed_zero": "False"} for y, v in zip(YEARS, DOWN)]
    e = run_case(rows=[], csv_rows=csv_rows, sc=None, release="5.6.0")["erosion_test"]
    assert e["status"] == "not_measured" and "CSV-only" in e["reason"]
    # G6 on a 5.7 run: erosion_risks +1 under MOAT_EROSION needs a numeric rebuttal; 0 passes without one
    rs = [row(y, v, gross_margin=g) for y, v, g in zip(YEARS, DOWN, gm_down)]
    plus = mutate_sc(lambda s: s["pillars"].__setitem__("erosion_risks", {"score": 1, "rationale": "r", "facts": ["F14"]}))
    refuses(["MOAT_EROSION: governing roic fell -8.50pp", "gross margin -4.00pp", "erosion_risks +1 needs moat_scorecard.erosion_rebuttal"],
            rows=rs, mut=plus)

    def plus_reb(c):
        plus(c)
        c.sc["erosion_rebuttal"] = "a price cycle, not erosion: realized price -12% [F1]"
    ev = passes(rows=rs, mut=plus_reb)
    assert ev["gates"]["erosion"]["applies"] is True
    passes(rows=rs)


# ---------------------------------------------------------------- 14-15. low-return and reverse gates
def test_low_return_gate_governing():
    wide = src("switching_costs", "embedded_component", strength="wide", facts=("F10",))
    # ROP shape: plain ROIC 5.8%, goodwill above invested capital -> tangible unbounded; ROC +1 (03c 2), G4 clears
    rop = rows_of([0.058] * 5, goodwill=1200.0)
    ev = passes(rows=rop, facts=with_facts(SRC_FACTS), mut=with_sources(wide, moat=7))
    p = ev["pillars"]["returns_on_capital"]
    assert p["metric"] == "roic_tangible" and p["median_note"] == "unbounded_high" and p["score"] == 1
    assert ev["gates"]["low_return"]["applies"] is False
    # a plain 8% non-acquirer at moat 7 refuses; a numeric reason passes
    refuses("moat_score 7 >= 7 on median roic 8.00% (< 10%) — add moat_scorecard.low_roic_reason carrying a number",
            rows=rows_of([0.08] * 5), facts=with_facts(SRC_FACTS), mut=with_sources(wide, moat=7))

    def with_reason(c):
        with_sources(wide, moat=7)(c)
        c.sc["low_roic_reason"] = "early-scale year: 2025 margin 9% [F1]"
    ev = passes(rows=rows_of([0.08] * 5), facts=with_facts(SRC_FACTS), mut=with_reason)
    assert ev["gates"]["low_return"]["applies"] is True and ev["gates"]["low_return"]["reason"]
    # a reason without a number does not count
    def wordy(c):
        with_sources(wide, moat=7)(c)
        c.sc["low_roic_reason"] = "the history understates the franchise"
    refuses("low_roic_reason carrying a number", rows=rows_of([0.08] * 5), facts=with_facts(SRC_FACTS), mut=wordy)
    # a balance-sheet financial at moat 7 on ROE 13% (< 15%) refuses
    def bank7(c):
        with_sources(wide, moat=7)(c)
        c.sc["business_type"] = "financial_balance_sheet"
    refuses("moat_score 7 >= 7 on median roe 13.00% (< 15%)", rows=rows_of([0.13] * 5), sic="6022", facts=with_facts(SRC_FACTS), mut=bank7)
    # unmeasured refuses
    refuses("moat_score 7 >= 7 on median roic unmeasured", rows=rows_of([0.2, 0.2]), facts=with_facts(SRC_FACTS),
            mut=with_sources(wide, moat=7))


def test_reverse_gate():
    narrow = src("switching_costs", "embedded_component", facts=("F10",))
    div = "evidence 7.21 vs 4: a cycle peak [F1]"
    refuses("moat_score 4 <= 4 on governing roic median 31.00% with every year >= 15% (FY2021-FY2025) — add "
            "moat_scorecard.high_return_low_moat_reason", rows=rows_of([0.31] * 5), mut=with_sources(narrow, moat=4, reason=div),
            facts=with_facts(SRC_FACTS))

    def with_reason(c):
        with_sources(narrow, moat=4, reason=div)(c)
        c.sc["high_return_low_moat_reason"] = "returns from leverage: debt 4.1x OE [F1]"
    ev = passes(rows=rows_of([0.31] * 5), mut=with_reason, facts=with_facts(SRC_FACTS))
    assert ev["gates"]["reverse"]["applies"] is True
    ev = passes(rows=rows_of([0.31, 0.31, 0.14, 0.31, 0.31]), mut=with_sources(narrow, moat=4, reason=div), facts=with_facts(SRC_FACTS))
    assert ev["gates"]["reverse"]["applies"] is False, "one year at 14% does not fire"
    ev = passes(rows=rows_of([0.31] * 5), mut=with_sources(narrow, moat=5, reason=div), facts=with_facts(SRC_FACTS))
    assert ev["gates"]["reverse"]["applies"] is False, "moat 5 does not fire"
    refuses("moat_score 4 <= 4 on governing roic median unbounded", rows=rows_of([0.31] * 5, equity=-50.0),
            mut=with_sources(narrow, moat=4, reason=div), facts=with_facts(SRC_FACTS))
    # 03c decision 2: under tangible governance the gate fires only with the plain ROIC median >= 10%
    ev = passes(rows=rows_of([0.08] * 5, goodwill=800.0), mut=with_sources(narrow, moat=4, reason=div), facts=with_facts(SRC_FACTS))
    p = ev["pillars"]["returns_on_capital"]
    assert p["metric"] == "roic_tangible" and p["median"] >= 0.20 and ev["gates"]["reverse"]["applies"] is False


# ---------------------------------------------------------------- 16. lint
LINT_CASES = [("management is the moat", True), ("unregulated market leader", True), ("#1 share in US dental", True),
              ("first-mover advantage in payments", True), ("technology lead in GPUs", True), ("fast-growing users", True),
              ("large TAM", True), ("strategic partnerships with OEMs", True), ("culture of execution", True),
              ("leader in embedded switching costs", False), ("executive team turnover", False), ("regulated utility leader", False),
              ("habit-forming daily purchase leader", False), ("leading installed base with aftermarket", False),
              ("no. 1 in a niche with few competitors", False), ("industry leader with best-in-class execution", True),
              ("trusted management", True), ("management team investors trust", True),
              ("best-in-class execution at scale", True), ("leading market share in contract manufacturing", True),
              ("great products with recurring launches", True), ("execution on acquisitions integration", True),
              ("market leader in networking gear", True), ("great management culture; strong retention of executives", True),
              ("habitat for leading products", True),
              ("leader with switching costs in core banking", False), ("leading network effects in payments", False),
              ("leader in economies of scale for parcel delivery", False), ("trusted provider of audit services, leader", False),
              ("leading share on multi-year contracts", False), ("leader; recurring revenue 80%", False),
              ("leader; customer retention 97%", False), ("habitual purchase leader", False)]


def test_lint():
    assert len(LINT_CASES) == 33
    for text, flag in LINT_CASES:
        out = M.lint_bad_moats({"moat_for": [text]}, False)
        assert bool(out) == flag, (text, out)
        for x in out:
            assert set(x) == {"field", "matched"} and x["matched"] in text.lower() and x["field"] == "moat_for[0]"
    out = M.lint_bad_moats({"moat_for": ["switching costs", "industry leader with best-in-class execution"],
                            "moat_justification": "a dominant leader"}, False)
    assert out == [{"field": "moat_for[1]", "matched": "leader"}, {"field": "moat_justification", "matched": "dominant"}]
    sup = {"moat_for": ["great products (supporting: product_quality)"]}
    assert M.lint_bad_moats(sup, True) == [] and M.lint_bad_moats(sup, False) == [{"field": "moat_for[0]", "matched": "great products"}]
    # the source rationales are scanned too; the lint never refuses
    ev = passes(mut=mutate_sc(lambda s: s["sources"][0].__setitem__("rationale", "the market leader")))
    assert {"field": "moat_scorecard.sources[0].rationale", "matched": "leader"} in ev["moat_lint"]


# ---------------------------------------------------------------- 17. SIC lock
def test_sic_lock_from_misfit_class():
    assert M.type_lock("6331", None)[0] == {"financial_balance_sheet"} and M.type_lock("4911", None)[0] == {"real_assets"}
    assert M.type_lock("6211", None)[0] is None and M.type_lock(None, None) == (None, None, None)
    assert M.type_lock("6798", {"liabilities": 40, "assets": 100, "operating_income": 5})[0] == {"real_assets", "financial_balance_sheet"}
    refuses("moat_scorecard.business_type industrial contradicts SIC 6331: a filer in this SIC range is scored as "
            "financial_balance_sheet", sic="6331")
    refuses("contradicts SIC 4911", sic="4911")
    # NLY shape: liabilities 88% of assets, no operating-income tag (pretax filed) -> locked financial_balance_sheet
    nly = rows_of([0.12] * 5, liabilities=1760.0, assets=2000.0, operating_income=None, pretax_income=120.0)
    assert M.type_lock("6798", nly[-1])[1] == "liabilities 88.00% of assets and no operating-income tag (FY2025)"
    refuses("moat_scorecard.business_type real_assets at SIC 6798 with liabilities 88.00% of assets and no operating-income tag "
            "(FY2025): a mortgage-REIT balance sheet is locked to financial_balance_sheet (ROE governs)", sic="6798", rows=nly,
            mut=mutate_sc(lambda s: s.update(business_type="real_assets")))
    ev = run_case(sc=None, release="5.6.0", sic="6798", rows=nly)
    assert ev["business_type_hint"] == "financial_balance_sheet" and ev["pillars"]["returns_on_capital"]["metric"] == "roe"
    # AGNC shape (the bank revenue basis) and the financial-assets share (03b §3.1 rules (b), (a)) -> locked
    agnc = rows_of([0.07] * 5, revenue_basis="InterestIncomeExpenseNet + NoninterestIncome")
    assert M.type_lock("6798", agnc[-1])[0] == {"financial_balance_sheet"}
    assert M.type_lock("6798", dict(agnc[-1], revenue_basis="Revenues (bank total)"))[0] == {"financial_balance_sheet"}
    assert M.type_lock("6798", dict(nly[-1], liabilities=100.0, financial_assets_pct_assets=0.53))[1] == \
        "loans and debt securities 53.00% of assets (FY2025)"
    # CCI (liabilities 105%, operating income tagged) and AMH (42%, no OI, no pretax) stay unlocked
    assert M.type_lock("6798", rows_of([0.05], liabilities=2100.0, assets=2000.0)[-1])[0] == {"real_assets", "financial_balance_sheet"}
    assert M.type_lock("6798", rows_of([0.05], liabilities=840.0, operating_income=None, pretax_income=None)[-1])[0] == \
        {"real_assets", "financial_balance_sheet"}
    # an unlocked REIT declaring real_assets needs a numeric business_type_reason
    def reit(reason):
        def m(c):
            c.sc["business_type"] = "real_assets"
            c.sc["business_type_reason"] = reason
            c.sc["pillars"]["switching_costs"] = na()
            c.sc["sources"] = [src("cost_advantage", "location")]
        return m
    refuses("moat_scorecard.business_type real_assets at SIC 6798 needs business_type_reason carrying a number", sic="6798",
            rows=rows_of([0.07] * 5), facts=with_facts(SRC_FACTS), mut=reit("owned real estate"))
    ev = passes(sic="6798", rows=rows_of([0.07] * 5), facts=with_facts(SRC_FACTS), mut=reit("rental revenue 94% of total revenue FY2025"))
    assert ev["type_lock"]["reason_required"] is True and ev["type_lock"]["sic_class"] == "reit"


# ---------------------------------------------------------------- 18-19. declared pillars, volume x price
def test_declared_pillar_rules():
    p = lambda name, v: mutate_sc(lambda s: s["pillars"].__setitem__(name, v))  # noqa: E731
    refuses("unknown key(s) ['moat_position']", mut=p("moat_position", {"score": 0}))
    refuses("moat_scorecard.pillars is missing ['customer_regard']", mut=mutate_sc(lambda s: s["pillars"].pop("customer_regard")))
    refuses("pricing_power score 3 is outside -2..+2", mut=p("pricing_power", {"score": 3, "rationale": "r", "facts": ["F1", "F2", "F3"]}))
    refuses("pricing_power.score must be an integer", mut=p("pricing_power", {"score": True, "rationale": "r", "facts": []}))
    refuses("cites F99, which facts.json does not declare", mut=p("pricing_power", {"score": 1, "rationale": "r", "facts": ["F99"]}))
    refuses("facts must be a list of distinct facts.json ids", mut=p("pricing_power", {"score": 1, "rationale": "r", "facts": ["F1", "F1"]}))
    refuses("scores +1 with no facts", mut=p("pricing_power", {"score": 1, "rationale": "r", "facts": []}))
    refuses("not a series: F1 (price_realization: 2 period(s))", mut=p("pricing_power", {"score": 1, "rationale": "r", "facts": ["F1", "F2"]}))
    short = [fact(f"H{i}", "churn", per, 0.02, used=("moat:retention",)) for i, per in enumerate(("2025-03-31", "2025-06-30", "2025-09-30"))]
    refuses("not a series: H0 (churn: 3 period(s))", facts=with_facts(short),
            mut=p("retention", {"score": 1, "rationale": "r", "facts": ["H0", "H1", "H2"]}))
    tp = series(("T1", "T2", "T3"), "app_rating", (4.6, 4.7, 4.7), unit="x", used=("moat:customer_regard",), kind="third_party")
    refuses("scores +2 on third-party facts only (T1, T2, T3) — third-party-only pillars are capped at |score| <= 1",
            facts=with_facts(tp), mut=p("customer_regard", {"score": 2, "rationale": "r", "facts": ["T1", "T2", "T3"]}))
    passes(facts=with_facts(tp), mut=p("customer_regard", {"score": 1, "rationale": "r", "facts": ["T1", "T2", "T3"]}))
    refuses("pricing_power scores +1 on point facts only (F10)",
            facts=[dict(f, used_for=f["used_for"] + ["moat:pricing_power"]) if f["id"] == "F10" else f for f in base_facts()],
            mut=p("pricing_power", {"score": 1, "rationale": "r", "facts": ["F10"]}))
    passes(mut=p("erosion_risks", {"score": -1, "rationale": "r", "facts": ["F14"], "threats": [{"type": "regulation", "facts": ["F14"]}]}))
    refuses("pricing_power cannot be not applicable for business type industrial (allowed: ['customer_regard'])",
            mut=p("pricing_power", na()))
    refuses("returns_on_capital is mechanical (make_score derives it); it may carry only a 'comment'",
            mut=p("returns_on_capital", {"score": 2}))
    ev = passes(mut=p("returns_on_capital", {"comment": "net-cash balance sheet"}))
    assert ev["pillars"]["returns_on_capital"]["comment"] == "net-cash balance sheet"
    refuses("cites F1, but F1 does not list used_for moat:retention", mut=p("retention", {"score": 1, "rationale": "r", "facts": ["F1", "F2", "F3"]}))
    guide = series(("K1", "K2", "K3"), "price_realization", (0.04, 0.05, 0.06), used=("moat:pricing_power",), type="guidance")
    refuses("of type 'guidance': a moat pillar cites only actual, metric or event facts", facts=with_facts(guide),
            mut=p("pricing_power", {"score": 1, "rationale": "r", "facts": ["K1", "K2", "K3"]}))
    rng = [fact("K4", "price_realization", "FY2025", [0.04, 0.05], used=("moat:pricing_power",))]
    refuses("a range value", facts=with_facts(rng), mut=p("pricing_power", {"score": 1, "rationale": "r", "facts": ["K4"]}))
    # reach_and_growth: +2 on growth rates only refuses; with a user-count series passes; +1 on rates passes
    gr = series(("R1", "R2", "R3"), "customer_growth", (0.10, 0.12, 0.11), used=("moat:reach_and_growth",))
    refuses("reach_and_growth +2 cites growth rates only (R1, R2, R3)", facts=with_facts(gr),
            mut=p("reach_and_growth", {"score": 2, "rationale": "r", "facts": ["R1", "R2", "R3"]}))
    passes(facts=with_facts(gr), mut=p("reach_and_growth", {"score": 2, "rationale": "r", "facts": ["R1", "R2", "R3", "F7", "F8", "F9"]}))
    ev = passes(facts=with_facts(gr), mut=p("reach_and_growth", {"score": 1, "rationale": "r", "facts": ["R1", "R2", "R3"]}))
    assert ev["pillars"]["reach_and_growth"]["growth_rate_facts_only"] is True
    # an unsupported 0 carries no weight
    ev = passes(mut=p("concentration", {"score": 0, "rationale": "r", "facts": []}))
    assert ev["pillars"]["concentration"]["status"] == "unsupported_neutral" and ev["pillars"]["concentration"]["weight_counted"] is False


def test_volume_price_bounds():
    assert M.classify(-0.01, 0.0) == "declining" and M.classify(-0.01, 0.03) == "pricing_power"
    assert M.classify(0.0, 0.0) == "declining" and M.classify(0.05, 0.01) == "mixed"
    assert M.classify(-0.05, 0.02) == "harvesting" and M.classify(0.05, -0.02) == "buying_growth"
    subs = series(("V1", "V2", "V3"), "paid_subscribers", (21.0e6, 22.4e6, 23.6e6), unit="count",
                  used=("moat:reach_and_growth", "moat:pricing_power"))
    rs = [row(y, revenue=rv) for y, rv in zip(YEARS, (900e6, 1000e6, 1250e6, 1400e6, 1560e6))]

    def vp(pp=1, rg=1, extra=None):
        def m(c):
            c.sc["volume_price"] = {"mode": "levels", "volume_facts": ["V1", "V2", "V3"], "volume_basis": "period_end", "revenue": "total"}
            c.sc["pillars"]["pricing_power"] = {"score": pp, "rationale": "r", "facts": ["V1", "V2", "V3"]}
            c.sc["pillars"]["reach_and_growth"] = {"score": rg, "rationale": "r", "facts": ["V1", "V2", "V3"]}
            if extra:
                extra(c)
        return m
    ev = passes(rows=rs, facts=with_facts(subs), mut=vp())
    v = ev["volume_price"]
    assert v["class"] == "pricing_power" and v["volume_cagr"] == 0.0601 and v["price_cagr"] == 0.0538
    refuses("pricing_power +0 outside [+1, +2]", rows=rs, facts=with_facts(subs), mut=vp(pp=0))
    refuses("reach_and_growth +2 outside [-2, +1]", rows=rs, facts=with_facts(subs), mut=vp(rg=2))
    # buying growth: users up while revenue per user falls -> pair <= 0
    bg = series(("V1", "V2", "V3"), "paid_subscribers", (21.0e6, 26.25e6, 33.6e6), unit="count",
                used=("moat:reach_and_growth", "moat:pricing_power"))
    refuses("-> buying_growth) bounds the scores", rows=rs, facts=with_facts(bg), mut=vp(pp=0, rg=1))
    refuses("pricing_power cannot be not applicable", rows=rs, facts=with_facts(subs),
            mut=vp(extra=lambda c: c.sc["pillars"].__setitem__("pricing_power", na())))
    # growth_rates mode: pct fractions, geometric means
    gro = (series(("W1", "W2", "W3"), "organic_volume_growth", (-0.01, 0.02, 0.0), used=("moat:reach_and_growth",))
           + series(("W4", "W5", "W6"), "price_realization_rate", (0.06, 0.04, 0.03), used=("moat:pricing_power",)))

    def gm(c):
        c.sc["volume_price"] = {"mode": "growth_rates", "volume_facts": ["W1", "W2", "W3"], "price_facts": ["W4", "W5", "W6"]}
        c.sc["pillars"]["pricing_power"] = {"score": 2, "rationale": "r", "facts": ["W4", "W5", "W6"]}
        c.sc["pillars"]["reach_and_growth"] = {"score": 0, "rationale": "r", "facts": ["W1", "W2", "W3"]}
    v = passes(facts=with_facts(gro), mut=gm)["volume_price"]
    assert v["class"] == "pricing_power" and v["volume_cagr"] == 0.0033 and v["price_cagr"] == 0.0433
    # consumer_users needs the decomposition on a 5.7 run
    def cu(c):
        c.sc["business_type"] = "consumer_users"
        c.sc["pillars"]["customer_regard"] = {"score": 0, "rationale": "r", "facts": []}
    refuses("volume_price (users x revenue per user) is required for business type consumer_users", mut=cu)


# ---------------------------------------------------------------- 20. rebuild drift
def test_rebuild_drift():
    assert M.GATE_DRIFT_ON_REBUILD is True, "03c decision 6"
    wide = src("switching_costs", "embedded_component", strength="wide", facts=("F10",))
    c = Case(rows=rows_of([0.18] * 5), facts=with_facts(SRC_FACTS))
    try:
        with_sources(wide, moat=8)(c)
        first = c.ev()
        assert "run_kind" not in first and M.run_kind(c.folder, c.n, c.j, True, None) == "authoring"
        assert first["within_tolerance"] is True and first["gate_drift"] == []
        prior = {"dcf_content_hash": c.n["content_hash"], "moat_evidence": first}
        # the SEC refresh moves the data: ROIC 18% -> 3% (returns_on_capital +1 -> -2), evidence falls outside +-2
        json.dump({"cik": 1, "annual": rows_of([0.03] * 5)}, open(os.path.join(c.folder, "fundamentals.json"), "w", encoding="utf-8"))
        ev = c.ev(prior=prior)
        assert M.run_kind(c.folder, c.n, c.j, True, prior) == "rebuild" and ev["within_tolerance"] is False
        assert [d["gate"] for d in ev["gate_drift"]] == ["divergence", "low_return"], ev["gate_drift"]   # 3% at moat 8: G4 too
        assert ev["gates"]["divergence"]["drifted"] is True and ev["gates"]["low_return"]["drifted"] is True
        txt = "\n".join(M.key_numbers_lines(ev))
        assert "Gate drift on this rebuild" in txt and "divergence" in txt
        # the same change with an edited scorecard is an authoring run: refused
        c.sc["pillars"]["concentration"]["rationale"] = "edited"
        try:
            c.ev(prior=prior)
            raise AssertionError("an edited declaration is an authoring run")
        except M.MoatRefusal as e:
            assert "from the evidence score" in str(e)
        c.sc["pillars"]["concentration"]["rationale"] = "largest customer"
        # an edited facts.json (judgment unchanged) is an authoring run too (rebase amendment 3.2 (d))
        doc = json.load(open(os.path.join(c.folder, "facts.json"), encoding="utf-8"))
        doc["facts"][0]["label"] = "edited"
        json.dump(doc, open(os.path.join(c.folder, "facts.json"), "w", encoding="utf-8"))
        try:
            c.ev(prior=prior)
            raise AssertionError("an edited facts.json is an authoring run")
        except M.MoatRefusal as e:
            assert "from the evidence score" in str(e)
        # another engine run (content hash) is an authoring run
        c.n["content_hash"] = "x" * 64
        try:
            c.ev(prior=prior)
            raise AssertionError("another engine run is an authoring run")
        except M.MoatRefusal:
            pass
    finally:
        c.close()
    # a rebuild whose declaration has no source at moat 5 (a code change that newly enforces the cap) still refuses
    c = Case(rows=rows_of([0.18] * 5))
    try:
        c.sc["sources"] = []
        c.j["moat_score"] = 5
        prior = {"dcf_content_hash": c.n["content_hash"],
                 "moat_evidence": {"status": "checked", "declaration_sha256": M.declaration_sha256(c.j),
                                   "facts_sha256": M.facts_sha256(c.folder)}}
        try:
            c.ev(prior=prior)
            raise AssertionError("declaration-only caps never drift")
        except M.MoatRefusal as e:
            assert "with no source" in str(e)
    finally:
        c.close()


def test_rebuild_refuses_without_drift_relaxation():
    saved = M.GATE_DRIFT_ON_REBUILD
    M.GATE_DRIFT_ON_REBUILD = False
    wide = src("switching_costs", "embedded_component", strength="wide", facts=("F10",))
    c = Case(rows=rows_of([0.18] * 5), facts=with_facts(SRC_FACTS))
    try:
        with_sources(wide, moat=8)(c)
        prior = {"dcf_content_hash": c.n["content_hash"], "moat_evidence": c.ev()}
        json.dump({"cik": 1, "annual": rows_of([0.03] * 5)}, open(os.path.join(c.folder, "fundamentals.json"), "w", encoding="utf-8"))
        try:
            c.ev(prior=prior)
            raise AssertionError("with GATE_DRIFT_ON_REBUILD False every gate refuses on a rebuild")
        except M.MoatRefusal as e:
            assert "from the evidence score" in str(e) and "moat_divergence_reason" in str(e)
    finally:
        M.GATE_DRIFT_ON_REBUILD = saved
        c.close()


# ---------------------------------------------------------------- acquired IPR&D (lane default Q3 (b))
def iprd_block(period="2025-12-31", amount=300.0, treatment="one_time_value_deduction", recurrent=False):
    return {"treatment": treatment, "recurrent": recurrent, "total": amount,
            "periods": [{"period": period, "window": "fy", "expense": amount, "amount": amount, "deducted": amount,
                         "fx_rate": None, "excluded": None}]}


def test_iprd_addback():
    """The one-time acquired-IPR&D charge engine 5.6 deducts once from value is added back to EBIT in returns_on_capital
    and scale_economics for that fiscal year (never when recurrent); the flag and the per-year add-back stay on record
    (HALO FY2025: $284.9M of $469.0M operating income; plain ROIC 15.5% -> ~25%, scale -2 -> +1)."""
    # FY2025 operating income 100 after a 300 charge (400 before it): ROIC 10% as filed, 40% with the add-back
    rs = rows_of([0.40, 0.40, 0.40, 0.40, 0.10])
    c = Case(rows=rs, sc=None, release="5.6.0", n_extra={"iprd_adjustment": iprd_block()})
    try:
        ev = c.ev()
        last = ev["pillars"]["returns_on_capital"]["series"][-1]
        assert last["roic"] == 0.40 and last["iprd_addback"] == 300.0
        assert "IPRD_CHARGE_IN_WINDOW" in ev["flags"]
        assert ev["iprd_in_window"] == [{"period": "2025-12-31", "amount": 300.0, "unit": "USD", "amount_usd": 300.0,
                                         "filed_unit": "USD", "fx_rate": None, "pct_of_operating_income": 3.0,
                                         "treatment": "one_time_value_deduction", "recurrent": False, "addback": True}]
        assert ev["pillars"]["scale_economics"]["series"][-1]["margin"] == 0.2
        txt = "\n".join(M.key_numbers_lines(ev))
        assert "Acquired IPR&D inside the window: FY2025 $300 (300.00% of operating income) — added back to operating income" in txt
        assert 300.0 in M.numeric_leaves(ev)
    finally:
        c.close()
    # recurrent: read as filed, flagged
    ev = run_case(rows=rs, sc=None, release="5.6.0", n_extra={"iprd_adjustment": iprd_block(recurrent=True)})
    assert ev["pillars"]["returns_on_capital"]["series"][-1]["roic"] == 0.10 and "IPRD_CHARGE_IN_WINDOW" in ev["flags"]
    assert ev["iprd_in_window"][0]["addback"] is False
    # treatment none / no block / a period outside the window: nothing
    ev = run_case(rows=rs, sc=None, release="5.6.0", n_extra={"iprd_adjustment": iprd_block(treatment="none")})
    assert "IPRD_CHARGE_IN_WINDOW" not in ev["flags"] and "iprd_in_window" not in ev
    ev = run_case(rows=rs, sc=None, release="5.6.0", n_extra={"iprd_adjustment": iprd_block(period="2019-12-31")})
    assert "iprd_in_window" not in ev
    # the one switch
    saved = M.ADDBACK_IPRD
    M.ADDBACK_IPRD = False
    try:
        ev = run_case(rows=rs, sc=None, release="5.6.0", n_extra={"iprd_adjustment": iprd_block()})
        assert ev["pillars"]["returns_on_capital"]["series"][-1]["roic"] == 0.10 and ev["iprd_in_window"][0]["addback"] is False
    finally:
        M.ADDBACK_IPRD = saved
    # the real HALO record (engine 5.6.0) when the checkout has it
    halo = os.path.join(REPO, "HALO")
    if os.path.exists(os.path.join(halo, "fundamentals.json")):
        n = json.load(open(os.path.join(halo, "dcf_numbers.json"), encoding="utf-8"))
        j = json.load(open(os.path.join(halo, "judgment.json"), encoding="utf-8"))
        ev = M.evaluate(halo, n, j, is_57=False, sic="2836")
        fy25 = ev["pillars"]["returns_on_capital"]["series"][-1]
        assert fy25["iprd_addback"] == 284887000.0 and round(fy25["roic"], 3) == 0.249, fy25
        assert ev["iprd_in_window"][0]["pct_of_operating_income"] == 0.6074 and ev["pillars"]["scale_economics"]["score"] == 1


# ---------------------------------------------------------------- end-to-end (make_score.py in a temp STOCKS_BASE)
def _e2e(moat=6, sc="base", rows=None, facts=None, release=None, industry=None, csv_rows=None, judgment_text=False,
         sic="3561", prior_score=None):
    """A make_score run on a synthetic folder (test_make_score_55.Run): fundamentals.json rows, facts.json and
    _system/industry_returns.json written into the temp base; the judgment carries its own scorecard (so the G16 helper
    adds none)."""
    import test_make_score_55 as H
    n = H._numbers(**({"release": release} if release else {}))
    n["moat_score"] = moat
    n["inputs"] = dict(n["inputs"], moat=moat)
    j = H._judgment(n, moat_score=moat, moat_for=["industry leader with best-in-class execution", "switching costs"])
    if sc == "base":
        sc = base_scorecard()
    if sc is not None:
        j["moat_scorecard"] = sc
    files = {"TST/fundamentals.json": {"cik": 1, "currency": "USD", "profile": {"sic": sic},
                                       "annual": rows if rows is not None else rows_of([0.18] * 5)},
             "TST/facts.json": {"schema": 1, "ticker": "TST", "facts": facts if facts is not None else base_facts()}}
    if industry is not None:
        files["_system/industry_returns.json"] = industry
    if judgment_text:
        r = H.Run(n, judgment_text=json.dumps(j, indent=1), files=files, csv_rows=csv_rows, prior_score=prior_score)
    else:
        r = H.Run(n, j, files=files, csv_rows=csv_rows, prior_score=prior_score)
    return r.run()


def _industry_for(sic="3561", vals=(0.10, 0.12, 0.20, 0.25, 0.30)):
    mem = _members("default", list(vals), sic=sic)
    return {"schema": 1, "built": "2026-10-21", "members": mem,
            "groups": {f"default|4:{sic}": {"members": sorted(mem), "label": "Pumps and pumping equipment"}}}


def test_pre57_record_reports_only():
    """21: a 5.6.0 record (HALO's release): moat_evidence report_only, scorecard absent, the mechanical pillars incl.
    industry_structure from the data base's industry_returns.json, lint, the build line; key_numbers.md ends with the
    Moat scorecard section; no moat event; nothing refused."""
    r = _e2e(sc=None, release="5.6.0", industry=_industry_for(), moat=8)
    try:
        r.ok()
        s = r.score()
        me = s["moat_evidence"]
        assert me["status"] == "report_only" and me["scorecard"] == "absent" and me["supporting_status"] == "absent"
        assert me["governing"]["measure"] == "roic" and me["pillars"]["industry_structure"]["status"] == "measured"
        assert me["moat_lint"] == [{"field": "moat_for[0]", "matched": "leader"}]
        assert me["industry_file"]["built"] == "2026-10-21" and len(me["industry_file"]["sha256"]) == 64
        json.dumps(me, allow_nan=False)
        kn = r.key()
        # [Integrate L2] 07 §1.9: the Moat scorecard is the last engine-side section; the folder's facts.json makes
        # L2's "Declared facts (not engine output)" follow it, last of all
        tail = kn.rstrip("\n").split("\n## ")
        assert tail[-2].startswith("Moat scorecard\n") and tail[-1].startswith("Declared facts (not engine output)\n"), \
            "the Moat scorecard section comes last before Declared facts"
        assert "- Scorecard: none declared (engine output predates release 5.7.0)" in kn
        assert f"- industry_returns.json built 2026-10-21 (sha256 {me['industry_file']['sha256'][:8]}…)" in kn
        assert "make_score.py: industry_returns.json built 2026-10-21" in r.out
        assert [e for e in r.entries() if str(e.get("event", "")).startswith("moat_")] == []
        assert "moat_evidence" in __import__("make_score").SCORE_DECISION_KEYS
    finally:
        r.close()


def test_57_requires_scorecard_and_sources():
    """22: on a 5.7 run, no scorecard refuses; sources [] at moat 6 refuses (cap 3); a scorecard without the
    supporting block refuses. Each refusal writes nothing."""
    r = _e2e(sc=None, judgment_text=True)
    try:
        r.refused("an engine 5.7 run needs judgment.json moat_scorecard (WORKER_SPEC step 5) — none declared")
        assert not os.path.exists(r.registry)
    finally:
        r.close()
    sc = base_scorecard()
    sc["sources"] = []
    r = _e2e(sc=sc)
    try:
        r.refused("moat_score 6 with no source in moat_scorecard.sources: a moat with no moat source (see SOURCE_TYPES) is capped at 3")
    finally:
        r.close()
    sc = base_scorecard()
    del sc["supporting"]
    r = _e2e(sc=sc)
    try:
        r.refused("moat_scorecard.supporting is required on a 5.7 run")
    finally:
        r.close()
    r = _e2e()
    try:
        r.ok()
        me = r.score()["moat_evidence"]
        assert me["status"] == "checked" and "run_kind" not in me and me["sources"]["count"] == 1
        assert "## Moat scorecard" in r.key() and "| switching_costs/embedded_component | narrow | F10 | yes |" in r.key()
    finally:
        r.close()


def test_57_divergence_reason():
    """23: a moat more than 2 from the evidence score refuses; a reason without a number refuses; with a number it
    scores, the registry records moat_divergence (evidence, core evidence, supporting adjustment, divergence) and an
    unchanged declaration keeps its first date."""
    sc = base_scorecard()
    sc["sources"] = []
    r = _e2e(sc=sc, moat=3)
    try:
        r.refused("moat_score 3 is 3.63 from the evidence score 6.63 (tolerance +/-2) — add moat_scorecard.moat_divergence_reason "
                  "carrying a number")
    finally:
        r.close()
    sc["moat_divergence_reason"] = "the evidence overstates a commodity business"
    r = _e2e(sc=sc, moat=3)
    try:
        r.refused("moat_divergence_reason carrying a number")
    finally:
        r.close()
    sc["moat_divergence_reason"] = "price realization 4.5% is cyclical [F3]"
    r = _e2e(sc=sc, moat=3)
    try:
        r.ok()
        ev = r.entries("moat_divergence")
        assert len(ev) == 1 and ev[0]["moat_score"] == 3.0 and isinstance(ev[0]["moat_score"], float)
        assert ev[0]["evidence_score"] == 6.63 and ev[0]["core_evidence_score"] == 6.63 and ev[0]["supporting_adjustment"] == 0.0
        assert ev[0]["divergence"] == -3.63 and ev[0]["reason"] == sc["moat_divergence_reason"]
        assert not set(ev[0]) & {"deal", "first_charged_period", "contingent_total", "paid_to_date", "periods"}
        # keep_first_dates: the same declaration on a later run keeps the first date
        reg = json.load(open(r.registry, encoding="utf-8"))
        for e in reg["entries"]:
            if e.get("event") == "moat_divergence":
                e["date"] = "2026-10-01"
        json.dump(reg, open(r.registry, "w", encoding="utf-8"))
        r.run().ok()
        assert [e["date"] for e in r.entries("moat_divergence")] == ["2026-10-01"]
        assert "- Gates (checked):" in r.key() and "divergence applies — reason declared in judgment.json" in r.key()
        assert sc["moat_divergence_reason"] not in r.key(), "worker text is never printed"
    finally:
        r.close()


def test_57_low_and_reverse_reasons():
    """24: G4 / G5 refuse without a numeric reason, score with one, and record moat_low_roic /
    moat_high_return_low_moat."""
    wide = src("switching_costs", "embedded_component", strength="wide", facts=("F10",))
    sc = base_scorecard()
    sc["sources"] = [wide]
    r = _e2e(sc=sc, moat=7, rows=rows_of([0.08] * 5), facts=with_facts(SRC_FACTS))
    try:
        r.refused("moat_score 7 >= 7 on median roic 8.00% (< 10%)")
    finally:
        r.close()
    sc["low_roic_reason"] = "early-scale years: price realization 4.5% [F3]"
    r = _e2e(sc=sc, moat=7, rows=rows_of([0.08] * 5), facts=with_facts(SRC_FACTS))
    try:
        r.ok()
        ev = r.entries("moat_low_roic")
        assert len(ev) == 1 and ev[0]["measure"] == "roic" and ev[0]["median"] == 0.08 and ev[0]["moat_score"] == 7.0
    finally:
        r.close()
    sc = base_scorecard()
    sc["moat_divergence_reason"] = "a cycle peak: retention 96% [F6]"
    r = _e2e(sc=sc, moat=4, rows=rows_of([0.31] * 5))
    try:
        r.refused("moat_score 4 <= 4 on governing roic median 31.00% with every year >= 15%")
    finally:
        r.close()
    sc["high_return_low_moat_reason"] = "returns from leverage at a cycle peak: retention 96% [F6]"
    r = _e2e(sc=sc, moat=4, rows=rows_of([0.31] * 5))
    try:
        r.ok()
        ev = r.entries("moat_high_return_low_moat")
        assert len(ev) == 1 and ev[0]["median"] == 0.31 and ev[0]["min"] == 0.31 and ev[0]["measure"] == "roic"
        assert len(r.entries("moat_divergence")) == 1
    finally:
        r.close()


def test_57_erosion_rebuttal_event():
    """25: MOAT_EROSION with erosion_risks +1 and a numeric rebuttal records moat_erosion_rebuttal."""
    sc = base_scorecard()
    sc["pillars"]["erosion_risks"] = {"score": 1, "rationale": "r", "facts": ["F14"]}
    rows = [row(y, v, gross_margin=g) for y, v, g in zip(YEARS, DOWN, (0.45, 0.44, 0.42, 0.41, 0.40))]
    r = _e2e(sc=sc, rows=rows)
    try:
        r.refused("MOAT_EROSION: governing roic fell -8.50pp")
    finally:
        r.close()
    sc["erosion_rebuttal"] = "a price cycle: price realization 4.5% [F3]"
    r = _e2e(sc=sc, rows=rows)
    try:
        r.ok()
        ev = r.entries("moat_erosion_rebuttal")
        assert len(ev) == 1 and ev[0]["governing_change_pp"] == -8.5 and ev[0]["margin_change_pp"] == -4.0
        assert ev[0]["margin_basis"] == "gross" and "MOAT_EROSION" in r.score()["moat_evidence"]["flags"]
        assert "- Flags: MOAT_EROSION" in r.key()
    finally:
        r.close()


def test_57_weight_floor():
    """26: a scorecard of unsupported zeros on a CSV-only folder (core weight < 8) refuses."""
    sc = base_scorecard()
    for k in ("pricing_power", "retention", "reach_and_growth", "switching_costs", "concentration", "erosion_risks"):
        sc["pillars"][k] = {"score": 0, "rationale": "r", "facts": []}
    sc["sources"] = []
    sc["moat_divergence_reason"] = "x 1 [F1]"
    r = _e2e(sc=sc, moat=3, rows=[])
    try:
        r.refused("moat evidence weight 0 < 8: too little of the scorecard is measured or fact-supported")
    finally:
        r.close()


def test_refusal_writes_nothing():
    """27: any moat refusal leaves score.json, key_numbers.md and the registry untouched (evaluate runs before
    registry_transaction); a prior score.json stays byte for byte."""
    prior = {"ticker": "TST", "tier_final": "B", "note": "the prior score"}
    sc = base_scorecard()
    sc["sources"] = []
    r = _e2e(sc=sc, prior_score=prior)
    try:
        r.refused("is capped at 3")
        assert not os.path.exists(r.registry) and r.score() == prior
    finally:
        r.close()


def test_moat_reasons_reach_check_influence():
    """27b (07 §1.12 step 7): on an authoring 5.7 run each moat reason whose gate applies (and a REIT's
    business_type_reason) goes through make_score.check_influence with the moat evidence's numeric leaves; a rebuild
    and legacy output check nothing."""
    import make_score as MS
    calls = []
    saved = MS.check_influence
    MS.check_influence = lambda field, text, ids, fc, folder, n, extra=None, **k: calls.append((field, text, ids, extra))
    try:
        sc = base_scorecard()
        sc["sources"] = []
        sc["moat_divergence_reason"] = "price realization 4.5% is cyclical [F3]"
        sc["low_roic_reason"] = "not applicable here 1 [F1]"
        me = run_case(sc=sc, moat=3)
        j = {"moat_scorecard": sc}
        done = MS.moat_reason_checks(me, j, None, "/nowhere", {"engine_release": "5.7.0"})
        assert done == [("moat_divergence_reason", sc["moat_divergence_reason"])], "only reasons whose gate applies"
        assert calls[0][0] == "moat_scorecard.moat_divergence_reason" and calls[0][2] == ["F3"]
        assert 6.63 in calls[0][3] and -3.63 in calls[0][3], "the moat evidence's numbers are engine sources"
        calls.clear()
        assert MS.moat_reason_checks(me, j, None, "/nowhere", {}, run_kind="rebuild") == [] and calls == []
        assert MS.moat_reason_checks(dict(me, status="report_only"), j, None, "/nowhere", {}) == []
        assert MS.moat_reason_checks(None, j, None, "/nowhere", {}) == []
        me2 = dict(me, type_lock=dict(me["type_lock"], reason_required=True))
        done = MS.moat_reason_checks(me2, {"moat_scorecard": dict(sc, business_type_reason="rental revenue 94%")}, None, "/x", {})
        assert done[-1] == ("business_type_reason", "rental revenue 94%") and calls[-1][0] == "moat_scorecard.business_type_reason"
    finally:
        MS.check_influence = saved
    # the facts make_score hands the scorecard: the facts check's by_id when present, else facts.json itself
    class FC:
        by_id = {"F1": {"id": "F1"}}
    assert MS.moat_facts_by_id(FC(), "/nowhere") == {"F1": {"id": "F1"}}
    c = Case()
    try:
        assert set(MS.moat_facts_by_id(None, c.folder)) == {f["id"] for f in base_facts()}
    finally:
        c.close()
    assert MS.moat_facts_by_id(None, "/nowhere") == {}
    # the events: pure, one per applying gate with a declared reason, none on a drifted gate or legacy output
    me = {"status": "checked", "moat_score": 6, "evidence_score": 3.5, "core_evidence_score": 3.0, "supporting_adjustment": 0.5,
          "divergence": 2.5, "governing": {"measure": "roic"},
          "gates": {"divergence": {"applies": True, "reason": "r 1", "drifted": False},
                    "low_return": {"applies": True, "reason": "r 2", "drifted": True, "measure": "roic", "median": 0.08},
                    "reverse": {"applies": False, "reason": "r 3"}, "erosion": {"applies": True, "reason": None}}}
    ev = MS._moat_events("TST", "2026-10-21", me)
    assert [e["event"] for e in ev] == ["moat_divergence"] and ev[0]["moat_score"] == 6.0
    assert MS._moat_events("TST", "2026-10-21", dict(me, status="report_only")) == [] and MS._moat_events("TST", "d", None) == []
    for e in ev:
        assert MS.registry_entry_problem(e) is None, MS.registry_entry_problem(e)


def test_57_moat_reasons_through_the_real_influence_trace():
    """[Integrate L3] (R4 revised x R3, Andrew 2026-10-19; 07 §1.6, §1.12 step 7): end to end, a moat reason whose gate
    applies goes through L2's REAL check_influence, not a stand-in — a cited fact must list the field's used_for tag
    (moat_divergence, low_roic), every figure must trace to an engine source, the moat evidence's own numbers or a cited
    fact, and third-party facts never carry it alone; each refusal writes nothing. Fails on the L3 lane alone
    (48d3737: L0's no-op check_influence scores case a; r57/merge_L3/l3tree). At the L3 merge commit 269c624 the
    end-to-end moat cases never reached the trace: L2's facts.json validation refused their fixtures first."""
    div = base_scorecard()
    div["sources"] = []                                 # moat 3 vs evidence 6.63: the divergence gate applies
    # (a) the cited fact lacks the reason's tag (F1 lists moat:pricing_power only)
    div["moat_divergence_reason"] = "price realization 4% is cyclical [F1]"
    r = _e2e(sc=div, moat=3)
    try:
        r.refused("judgment.json moat_scorecard.moat_divergence_reason cites F1, but F1 does not list used_for "
                  "moat_divergence")
        assert not os.path.exists(r.registry)
    finally:
        r.close()
    # (b) a figure in no generated file and no cited fact
    div["moat_divergence_reason"] = "price realization 7.7% is cyclical [F3]"
    r = _e2e(sc=div, moat=3)
    try:
        r.refused("judgment.json moat_scorecard.moat_divergence_reason quotes 7.7% that is neither an engine figure nor "
                  "a fact it cites")
    finally:
        r.close()
    # (c) the moat evidence's own number (a numeric leaf, 07 §1.12 step 7) traces with no fact cited
    div["moat_divergence_reason"] = "the evidence score 6.63 overstates a commodity business"
    r = _e2e(sc=div, moat=3)
    try:
        r.ok()
        inf = r.score()["declared_facts"]["influence"]["moat_scorecard.moat_divergence_reason"]
        assert inf["facts"] == [] and inf["engine_numbers"] == 1 and not inf["third_party_only"], inf
        assert [e["reason"] for e in r.entries("moat_divergence")] == [div["moat_divergence_reason"]]
    finally:
        r.close()
    # (d) low_roic_reason: the cited fact must list low_roic (F6 lists moat_divergence / high_return_low_moat)
    wide = src("switching_costs", "embedded_component", strength="wide", facts=("F10",))
    low = base_scorecard()
    low["sources"] = [wide]
    low["low_roic_reason"] = "early-scale years: retention 96% [F6]"
    r = _e2e(sc=low, moat=7, rows=rows_of([0.08] * 5))
    try:
        r.refused("judgment.json moat_scorecard.low_roic_reason cites F6, but F6 does not list used_for low_roic")
    finally:
        r.close()
    # (e) third-party facts alone never carry a moat reason (R3)
    tp = fact("F15", "analyst_price_realization", "FY2025", 0.0837, kind="third_party", type="actual",
              used=("moat_divergence",))
    div["moat_divergence_reason"] = "analysts see price realization of 8.37% [F15]"   # (a figure no leaf holds)
    r = _e2e(sc=div, moat=3, facts=with_facts([tp]))
    try:
        r.refused("judgment.json moat_scorecard.moat_divergence_reason rests only on third-party facts (F15)")
    finally:
        r.close()


# ---------------------------------------------------------------- review fixes (L3 review round 1, 2026-10-21)
def test_identical_rerun_is_byte_identical():
    """R1: two make_score runs on the same 5.7 folder with nothing changed between them (the second is a REBUILD of
    the first) write byte-identical score.json and key_numbers.md. moat_evidence is in SCORE_DECISION_KEYS, and L5's
    pr_worktree prepare reruns make_score on the sweep's committed score.json (always a rebuild) and refuses on any
    mismatch: moat_evidence must depend only on the inputs (declaration, facts, data, industry file), never on the run
    kind (authoring vs rebuild is make_score's own bookkeeping, moat_scorecard.run_kind)."""
    import make_score as MS
    r = _e2e(industry=_industry_for())
    try:
        r.ok()
        sp, kp = os.path.join(r.folder, "score.json"), os.path.join(r.folder, "key_numbers.md")
        s1, k1 = open(sp, "rb").read(), open(kp, "rb").read()
        first = json.loads(s1)
        assert first["moat_evidence"]["status"] == "checked"
        r.run().ok()
        s2 = json.loads(open(sp, "rb").read())
        diff = sorted(k for k in MS.SCORE_DECISION_KEYS if first.get(k) != s2.get(k))
        assert diff == [], (diff, sorted(k for k in first["moat_evidence"] if first["moat_evidence"].get(k) != s2["moat_evidence"].get(k)))
        assert open(sp, "rb").read() == s1, "score.json is byte-identical on an identical rerun"
        assert open(kp, "rb").read() == k1, "key_numbers.md is byte-identical on an identical rerun"
        assert "run_kind" not in first["moat_evidence"], "the run kind is never persisted"
        # ... and the second run WAS a rebuild (the moat reasons' influence checks skip it), the first an authoring run
        n = json.load(open(os.path.join(r.folder, "dcf_numbers.json"), encoding="utf-8"))
        j = json.load(open(r.jpath, encoding="utf-8"))
        assert M.run_kind(r.folder, n, j, True, first) == "rebuild"
        assert M.run_kind(r.folder, n, j, True, None) == "authoring" and M.run_kind(r.folder, n, j, False, first) is None
    finally:
        r.close()


def test_dry_run_is_an_authoring_check():
    """R3: python3 _system/moat_scorecard.py <T> — the dry run WORKER_SPEC step 5 runs before the final engine run —
    is always an AUTHORING check (prior=None): a gate that would refuse the next engine run refuses here (exit 1), even
    when the folder's score.json would make this a rebuild that only records drift."""
    import contextlib
    import io
    wide = src("switching_costs", "embedded_component", strength="wide", facts=("F10",))
    c = Case(rows=rows_of([0.18] * 5), facts=with_facts(SRC_FACTS))
    saved = os.environ.get("STOCKS_BASE")
    try:
        with_sources(wide, moat=8)(c)
        first = c.ev()
        assert first["gate_drift"] == []
        # the folder as make_score left it: dcf_numbers.json, judgment.json, score.json carrying this run's hash
        json.dump(c.n, open(os.path.join(c.folder, "dcf_numbers.json"), "w", encoding="utf-8"))
        json.dump(c.j, open(os.path.join(c.folder, "judgment.json"), "w", encoding="utf-8"))
        json.dump({"dcf_content_hash": c.n["content_hash"], "moat_evidence": first},
                  open(os.path.join(c.folder, "score.json"), "w", encoding="utf-8"))
        os.environ["STOCKS_BASE"] = c.tmp

        def dry():
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = M.main(["TST"])
            return rc, buf.getvalue()
        rc, out = dry()
        assert rc == 0 and "passes the 5.7 rules" in out, out
        # an SEC refresh moves the data (ROIC 18% -> 3%): at moat 8 the divergence and low-return gates now fail
        json.dump({"cik": 1, "annual": rows_of([0.03] * 5)}, open(os.path.join(c.folder, "fundamentals.json"), "w", encoding="utf-8"))
        rc, out = dry()
        assert rc == 1 and "REFUSED" in out and "from the evidence score" in out, out
        assert "passes the 5.7 rules" not in out and "Gate drift" not in out, out
    finally:
        if saved is None:
            os.environ.pop("STOCKS_BASE", None)
        else:
            os.environ["STOCKS_BASE"] = saved
        c.close()


def _fx_block(native=100.0, rate=1.10, unit="EUR", basis="expense"):
    """An engine-5.6 period record for a charge filed in `unit` and converted at `rate` (dcf_engine._iprd_record: the
    expense / amount / deducted figures are USD, expense_unit / cash_unit the filed unit, fx_rate the rate used)."""
    usd = native * rate
    p = {"period": "2025-12-31", "window": "fy", "expense_tag": "ResearchAndDevelopmentInProcess", "expense": usd,
         "expense_unit": unit, "cash": None, "cash_unit": None, "amount": usd, "amount_basis": basis, "fx_rate": rate,
         "deducted": usd, "excluded": None}
    if basis == "cash_outflow":
        p.update(cash=usd, cash_unit=unit, tag_used="PaymentsToAcquireInProcessResearchAndDevelopment")
    return {"treatment": "one_time_value_deduction", "recurrent": False, "total": usd, "periods": [p]}


def test_iprd_addback_in_the_rows_money_unit():
    """R4: the acquired-IPR&D add-back is in the money unit of the rows it is added to — fundamentals.json's own
    `currency` (a 20-F filer's rows are as filed, never converted), USD on financials_history.csv (the engine's
    converted rows). The engine's period record is USD (expense = native x fx_rate), so a EUR filer's EUR 100 charge
    recorded as USD 110 at 1.10 adds back EUR 100, not 110; key_numbers.md prints it in that unit."""
    rs = rows_of([0.18] * 5)                     # FY2025 operating income 180 (EUR) as filed
    for basis in ("expense", "cash_outflow"):
        c = Case(rows=rs, sc=None, release="5.6.0", n_extra={"iprd_adjustment": _fx_block(basis=basis)})
        try:
            doc = json.load(open(os.path.join(c.folder, "fundamentals.json"), encoding="utf-8"))
            doc["currency"] = "EUR"
            json.dump(doc, open(os.path.join(c.folder, "fundamentals.json"), "w", encoding="utf-8"))
            ev = c.ev()
            w = ev["iprd_in_window"][0]
            assert w["amount"] == 100.0 and w["unit"] == "EUR" and w["amount_usd"] == 110.0 and w["addback"] is True, (basis, w)
            assert w["pct_of_operating_income"] == 0.5556, w
            last = ev["pillars"]["returns_on_capital"]["series"][-1]
            assert last["iprd_addback"] == 100.0 and last["roic"] == 0.28, last      # (180 + 100) / 1,000
            txt = "\n".join(M.key_numbers_lines(ev))
            assert "Acquired IPR&D inside the window: FY2025 100 EUR (55.56% of operating income)" in txt, txt
        finally:
            c.close()
    # the engine's CSV rows are USD: the USD figure is added back
    csv_rows = [{"period_end": f"{y}-12-31", "fy_label": str(y), "revenue": 2000, "net_income": 180, "operating_income": 180,
                 "ocf": 300, "capex": 30, "capex_assumed_zero": "False", "equity": 1000, "cash": 0, "debt_total": 0, "tax": 0}
                for y in YEARS]
    c = Case(rows=[], csv_rows=csv_rows, sc=None, release="5.6.0", n_extra={"iprd_adjustment": _fx_block()})
    try:
        ev = c.ev()
        w = ev["iprd_in_window"][0]
        assert w["amount"] == 110.0 and w["unit"] == "USD" and w["addback"] is True, w
        assert ev["pillars"]["returns_on_capital"]["series"][-1]["iprd_addback"] == 110.0
        assert "FY2025 $110 (61.11% of operating income)" in "\n".join(M.key_numbers_lines(ev))
    finally:
        c.close()
    # a USD filer's USD rows with a USD charge: unchanged (HALO's shape)
    c = Case(rows=rs, sc=None, release="5.6.0", n_extra={"iprd_adjustment": iprd_block(amount=100.0)})
    try:
        w = c.ev()["iprd_in_window"][0]
        assert w["amount"] == 100.0 and w["unit"] == "USD" and w["amount_usd"] == 100.0 and w["addback"] is True, w
    finally:
        c.close()
    # rows in a currency the charge was not filed in (GBP rows, a EUR charge): no add-back, listed with the reason
    c = Case(rows=rs, sc=None, release="5.6.0", n_extra={"iprd_adjustment": _fx_block()})
    try:
        doc = json.load(open(os.path.join(c.folder, "fundamentals.json"), encoding="utf-8"))
        doc["currency"] = "GBP"
        json.dump(doc, open(os.path.join(c.folder, "fundamentals.json"), "w", encoding="utf-8"))
        ev = c.ev()
        w = ev["iprd_in_window"][0]
        assert w["addback"] is False and w["amount"] is None and w["unit"] == "GBP" and w["amount_usd"] == 110.0, w
        assert "unit_note" in w and ev["pillars"]["returns_on_capital"]["series"][-1].get("iprd_addback") is None
        assert "FY2025 $110 (USD; the GBP rows are not converted) — not added back" in "\n".join(M.key_numbers_lines(ev))
        json.dumps(ev, allow_nan=False)
    finally:
        c.close()


def _thin(sc):
    """Declared core weight 6.5 (concentration and erosion_risks fact-less zeros): the scorecard needs the mechanical
    pillars to clear the weight floor of 8."""
    sc["pillars"]["concentration"] = {"score": 0, "rationale": "no facts", "facts": []}
    sc["pillars"]["erosion_risks"] = {"score": 0, "rationale": "no facts", "facts": []}


def test_rebuild_drift_weight_floor_and_volume_price():
    """R5 (03c decision 6, lane default Q5): G2's weight floor counts the MECHANICAL pillars, so a rebuild whose data
    left returns_on_capital insufficient records drift (weight_floor) instead of refusing; an authoring run refuses; a
    scorecard whose declared weight could not reach the floor even with every mechanical pillar measured is a
    declaration failure and refuses on a rebuild too. The volume x price bounds read revenue from the annual rows when
    no revenue facts are declared: a restated revenue that moves the class drifts on a rebuild (volume_price); bounds
    on declared revenue facts refuse everywhere."""
    c = Case(rows=rows_of([0.18] * 5))
    try:
        _thin(c.sc)
        first = c.ev()
        assert first["evidence_weight"] == 10.5 and first["gate_drift"] == []
        prior = {"dcf_content_hash": c.n["content_hash"], "moat_evidence": first}
        # an SEC refresh drops the equity tag (no_equity every year): returns_on_capital becomes insufficient_data
        json.dump({"cik": 1, "annual": [dict(r, equity=None) for r in rows_of([0.18] * 5)]},
                  open(os.path.join(c.folder, "fundamentals.json"), "w", encoding="utf-8"))
        ev = c.ev(prior=prior)
        assert ev["evidence_weight"] == 7.5 and [d["gate"] for d in ev["gate_drift"]] == ["weight_floor"], ev["gate_drift"]
        assert "moat evidence weight 7.5 < 8" in ev["gate_drift"][0]["detail"]
        assert "Gate drift on this rebuild (recorded, not refused; the next authoring run resolves it): weight_floor" in \
            "\n".join(M.key_numbers_lines(ev))
        try:
            c.ev(prior=None)
            raise AssertionError("an authoring run refuses the weight floor")
        except M.MoatRefusal as e:
            assert "moat evidence weight 7.5 < 8" in str(e)
    finally:
        c.close()
    # declared weight 1.0: even every mechanical pillar measured (6.5) cannot reach 8 -> a declaration failure
    c = Case(rows=rows_of([0.18] * 5))
    try:
        for k in ("pricing_power", "retention", "switching_costs", "concentration", "erosion_risks"):
            c.sc["pillars"][k] = {"score": 0, "rationale": "no facts", "facts": []}
        c.sc["sources"] = []
        c.j["moat_score"] = 3
        prior = {"dcf_content_hash": c.n["content_hash"],
                 "moat_evidence": {"status": "checked", "declaration_sha256": M.declaration_sha256(c.j),
                                   "facts_sha256": M.facts_sha256(c.folder)}}
        try:
            c.ev(prior=prior)
            raise AssertionError("a declaration that cannot reach the floor refuses on a rebuild")
        except M.MoatRefusal as e:
            assert "moat evidence weight" in str(e) and "< 8" in str(e)
    finally:
        c.close()
    # volume x price on the rows' revenue: users +6%/yr, revenue per user +5%/yr -> pricing_power (pp +1 allowed)
    subs = series(("V1", "V2", "V3"), "paid_subscribers", (21.0e6, 22.4e6, 23.6e6), unit="count",
                  used=("moat:reach_and_growth", "moat:pricing_power"))
    rs = [row(y, revenue=rv) for y, rv in zip(YEARS, (900e6, 1000e6, 1250e6, 1400e6, 1560e6))]

    def vp(revenue_facts=None):
        def m(c):
            c.sc["volume_price"] = {"mode": "levels", "volume_facts": ["V1", "V2", "V3"], "volume_basis": "period_end",
                                    "revenue": "total"}
            if revenue_facts:
                c.sc["volume_price"]["revenue_facts"] = list(revenue_facts)
            c.sc["pillars"]["pricing_power"] = {"score": 1, "rationale": "r", "facts": ["V1", "V2", "V3"]}
            c.sc["pillars"]["reach_and_growth"] = {"score": 1, "rationale": "r", "facts": ["V1", "V2", "V3"]}
            c.j["moat_scorecard"] = c.sc
        return m
    c = Case(rows=rs, facts=with_facts(subs))
    try:
        vp()(c)
        first = c.ev()
        assert first["volume_price"]["class"] == "pricing_power" and first["gate_drift"] == []
        prior = {"dcf_content_hash": c.n["content_hash"], "moat_evidence": first}
        # the refresh restates revenue flat while subscribers grow: buying growth bounds pricing_power to <= 0
        flat = [row(y, revenue=rv) for y, rv in zip(YEARS, (900e6, 1000e6, 1250e6, 1250e6, 1250e6))]
        json.dump({"cik": 1, "annual": flat}, open(os.path.join(c.folder, "fundamentals.json"), "w", encoding="utf-8"))
        ev = c.ev(prior=prior)
        assert [d["gate"] for d in ev["gate_drift"]] == ["volume_price"], ev["gate_drift"]
        assert "bounds the scores" in ev["gate_drift"][0]["detail"] and ev["volume_price"]["class"] == "buying_growth"
        try:
            c.ev(prior=None)
            raise AssertionError("an authoring run refuses the bounds")
        except M.MoatRefusal as e:
            assert "bounds the scores" in str(e)
    finally:
        c.close()
    # the same bounds on DECLARED revenue facts depend on the declaration only: they refuse on a rebuild
    revf = series(("R1", "R2", "R3"), "revenue", (1250e6, 1250e6, 1250e6), unit="USD", used=("moat:pricing_power",))
    c = Case(rows=rs, facts=with_facts(subs + revf))
    try:
        vp(revenue_facts=("R1", "R2", "R3"))(c)
        prior = {"dcf_content_hash": c.n["content_hash"],
                 "moat_evidence": {"status": "checked", "declaration_sha256": M.declaration_sha256(c.j),
                                   "facts_sha256": M.facts_sha256(c.folder)}}
        try:
            c.ev(prior=prior)
            raise AssertionError("bounds on declared revenue facts never drift")
        except M.MoatRefusal as e:
            assert "bounds the scores" in str(e)
    finally:
        c.close()


def test_minimal_scorecard_follows_the_sic_lock():
    """R6 (03b §17 (f), rebase L3 §3.10): rulings57.add_minimal_scorecard declares the SIC lock's type — resolved the
    way make_score resolves the SIC (dcf_numbers.json sector_model.sic, else dcf_engine.folder_sic) — else industrial,
    so a current-release test record at a bank, an insurer or a utility scores instead of being refused before the
    test's own assertion. An unlocked REIT (two allowed types) gets financial_balance_sheet, which needs no numeric
    business_type_reason."""
    import test_make_score_55 as H
    cases = (("6022", "financial_balance_sheet"), ("6331", "financial_balance_sheet"), ("4911", "real_assets"),
             ("6798", "financial_balance_sheet"), ("3561", "industrial"), (None, "industrial"))
    for sic, want in cases:
        files = ({"TST/fundamentals.json": {"cik": 1, "currency": "USD", "profile": {"sic": sic}, "annual": []}}
                 if sic else None)
        r = H.Run(H._numbers(), files=files).run()
        try:
            r.ok()
            me = r.score()["moat_evidence"]
            assert me["business_type"] == want and me["status"] == "checked", (sic, me["business_type"])
        finally:
            r.close()
    n = H._numbers()
    n["sector_model"] = {"sic": "6022"}                    # L1's engine field wins over the folder files
    r = H.Run(n).run()
    try:
        r.ok()
        assert r.score()["moat_evidence"]["business_type"] == "financial_balance_sheet"
    finally:
        r.close()


# ---------------------------------------------------------------- repo-wide
def test_all_recorded_folders_evaluate():
    """28: every folder with score.json + judgment.json: evaluate(is_57=False) returns report_only without raising,
    JSON without Infinity / NaN, every pillar score in its range or None (HALO's 5.6.0 record and its IPR&D add-back
    included)."""
    ind = M.load_industry(os.path.join(SYS))
    n_ok = 0
    for sp in sorted(glob.glob(os.path.join(REPO, "*", "score.json"))):
        d = os.path.dirname(sp)
        t = os.path.basename(d)
        if t.startswith("_") or not os.path.exists(os.path.join(d, "judgment.json")):
            continue
        n = json.load(open(os.path.join(d, "dcf_numbers.json"), encoding="utf-8"))
        j = json.load(open(os.path.join(d, "judgment.json"), encoding="utf-8"))
        sic = (n.get("sector_model") or {}).get("sic") or E.folder_sic(REPO, t)[0]
        ev = M.evaluate(d, n, j, is_57=False, sic=sic, industry=ind)
        assert ev["status"] == "report_only" and ev["scorecard"] == "absent", t
        json.dumps(ev, allow_nan=False)
        for k in M.CORE:
            s = ev["pillars"][k].get("score") if k in ev["pillars"] else None
            assert s is None or M.RANGES[k][0] <= s <= M.RANGES[k][1], (t, k, s)
        n_ok += 1
    print(f"   {n_ok} recorded folders evaluated report_only")


EXAMPLES_DIR = os.path.join(SYS, "examples")


def example_folder(doc, base):
    """Rebuild an example's synthetic folder (and its industry file) under base; returns (folder, n, j, facts, industry)."""
    inp = doc["inputs"]
    folder = os.path.join(base, doc["ticker"])
    os.makedirs(folder, exist_ok=True)
    if inp.get("fundamentals_annual"):
        json.dump({"cik": inp.get("cik"), "currency": "USD", "profile": {"sic": doc["sic"]}, "annual": inp["fundamentals_annual"]},
                  open(os.path.join(folder, "fundamentals.json"), "w", encoding="utf-8"), indent=1)
    rows = inp.get("financials_history_csv_rows") or []
    if rows:
        with open(os.path.join(folder, "financials_history.csv"), "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    json.dump(inp["facts"], open(os.path.join(folder, "facts.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    sysd = os.path.join(base, "_system")
    os.makedirs(sysd, exist_ok=True)
    with open(os.path.join(sysd, M.INDUSTRY_FILE), "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(inp["industry_returns"], indent=1, ensure_ascii=False) + "\n")
    return folder, inp["dcf_numbers_excerpt"], inp["judgment_excerpt"], {x["id"]: x for x in inp["facts"]["facts"]}, M.load_industry(sysd)


def evaluate_example(doc):
    base = tempfile.mkdtemp(prefix="moat_example_")
    try:
        folder, n, j, facts, ind = example_folder(doc, base)
        return M.evaluate(folder, n, j, facts=facts, is_57=True, sic=doc["sic"], industry=ind)
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_examples_match():
    """30: each _system/examples/moat_scorecard_*.json (FICTIONAL companies, 02's facts schema): rebuild the synthetic
    folder, evaluate with the 5.7 rules on, and compare with expected_moat_evidence exactly (generated by the module,
    never hand-edited)."""
    paths = sorted(glob.glob(os.path.join(EXAMPLES_DIR, "moat_scorecard_*.json")))
    names = {os.path.basename(p) for p in paths}
    assert {"moat_scorecard_consumer_subscription.json", "moat_scorecard_industrial.json", "moat_scorecard_insurer.json",
            "moat_scorecard_reverse_gate.json", "moat_scorecard_no_source.json"} <= names, names
    for p in paths:
        doc = json.load(open(p, encoding="utf-8"))
        assert "FICTIONAL" in doc["_note"]
        got = evaluate_example(doc)
        assert got == doc["expected_moat_evidence"], (os.path.basename(p), [k for k in got if got.get(k) != doc["expected_moat_evidence"].get(k)])
    adj = {os.path.basename(p): json.load(open(p, encoding="utf-8"))["expected_moat_evidence"]["supporting_adjustment"] for p in paths}
    assert adj["moat_scorecard_consumer_subscription.json"] == 0.5 and adj["moat_scorecard_industrial.json"] == 0.0
    assert adj["moat_scorecard_insurer.json"] == 0.0 and adj["moat_scorecard_no_source.json"] == 0.5


if __name__ == "__main__":
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("PASS", name)
            except Exception as e:  # noqa: BLE001
                fails += 1
                import traceback
                traceback.print_exc()
                print("FAIL", name, e)
    sys.exit(1 if fails else 0)
