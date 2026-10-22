#!/usr/bin/env python3
"""industry_returns.py — the same-ladder SIC-group governing-return medians the moat scorecard's industry_structure
pillar reads (engine 5.7, Andrew 2026-10-19, R4 revised M2; design 03b §3.3, decisions 03c 5 and 13). Run:
python _system/tests/test_industry_returns.py (or python -m pytest _system/tests). Offline. Fails on the code before
engine 5.7 (e22e814): the script does not exist.

29 test_industry_returns_builds_from_repo — build(BASE) over the checkout: deterministic, every member's measure and
   ladder in their sets, every group on one ladder, no Infinity; the leave-one-out median make_score scores equals the
   one recomputed from the file's members for three tickers; 2:49 never mixes the utilities with the waste companies.
   test_dedupe_drop_stable_write_and_check — on a synthetic base: one member per CIK (FWONA / FWONK), a -inf peer
   dropped and counted (03c decision 13 option (b)), the stable write (only `built` differs on a rebuild with no data
   change), --check exit codes, labels by level.
   test_committed_file_is_consistent / test_consistency_is_not_currency (L3 review R2, 2026-10-21) — the committed
   file is checked for internal consistency only, never for currency: between two daily-cron runs it is legitimately
   one or more re-scores behind (03b §3.3.2 / §3.3.3), so a merged company PR must not turn the suite red; --check
   (exit 1 when stale) stays the currency tool.
"""
import contextlib
import io
import json
import math
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
REPO = os.path.dirname(SYS)
sys.path.insert(0, SYS)
import industry_returns as IR  # noqa: E402
import moat_scorecard as M  # noqa: E402
import dcf_engine as E  # noqa: E402


def test_industry_returns_builds_from_repo():
    a = IR.build(REPO, built="2026-10-21")
    b = IR.build(REPO, built="2026-10-21")
    assert a == b, "deterministic"
    json.dumps(a, allow_nan=False)
    assert a["schema"] == 1 and a["rule"]["min_peers"] == 5 and a["rule"]["same_ladder"] is True
    assert list(a["members"]) == sorted(a["members"]) and list(a["groups"]) == sorted(a["groups"])
    for t, m in a["members"].items():
        assert m["measure"] in ("roic", "roic_tangible", "roe") and m["ladder"] in ("default", "real_assets", "roe"), (t, m)
        assert (m["median"] is None) == (m["median_note"] is not None), (t, m)
    for k, g in a["groups"].items():
        lad = k.split("|")[0]
        assert all(a["members"][t]["ladder"] == lad for t in g["members"]), k
        assert len(g["members"]) >= 2 and g["n"] + g["n_dropped"] <= len(g["members"])
    # 2:49: the default-ladder waste companies never share a group with the real-asset utilities
    for k, g in a["groups"].items():
        if k.endswith("|2:49"):
            assert len({a["members"][t]["ladder"] for t in g["members"]}) == 1
    # leave-one-out: make_score's industry median equals the one recomputed from the file for three measured tickers
    ind = dict(a, _sha256="x" * 64)
    checked = 0
    for t in sorted(a["members"]):
        if checked >= 3:
            break
        folder = os.path.join(REPO, t)
        n = json.load(open(os.path.join(folder, "dcf_numbers.json"), encoding="utf-8"))
        j = json.load(open(os.path.join(folder, "judgment.json"), encoding="utf-8"))
        ev = M.evaluate(folder, n, j, is_57=False, sic=a["members"][t]["sic"], industry=ind)
        p = ev["pillars"]["industry_structure"]
        if p["status"] != "measured":
            continue
        g = a["groups"][f"{p['ladder']}|{p['group']}"]
        own_cik = str(a["members"][t].get("cik"))
        vals = [M._peer_value(a["members"][x]) for x in g["members"] if x != t and str(a["members"][x].get("cik")) != own_cik]
        vals = [v for v in vals if v is not None and v != -math.inf]
        med = M._median(vals)
        assert len(vals) == p["peers"] and (p["median"] == M._r(med) if math.isfinite(med) else p["median_note"] == "unbounded_high"), t
        checked += 1
    assert checked == 3


def _folder(base, t, sic, roic, cik, btype_flags=()):
    d = os.path.join(base, t)
    os.makedirs(d)
    rows = [{"period_end": f"{y}-12-31", "fy": str(y), "revenue": 2000.0, "operating_income": 1000.0 * roic, "pretax_income": 1.0,
             "tax": 0.0, "net_income": 1000.0 * roic, "equity": 1000.0 if roic > -1 else -50.0, "total_debt": 0.0, "cash": 0.0,
             "assets": 2000.0} for y in (2021, 2022, 2023, 2024, 2025)]
    if roic == -9:   # a loss on non-positive capital every year: a -inf median
        for r in rows:
            r.update(operating_income=-100.0, net_income=-100.0, equity=-50.0)
    json.dump({"cik": cik, "profile": {"sic": sic, "sic_description": f"Industry {sic}"}, "annual": rows},
              open(os.path.join(d, "fundamentals.json"), "w", encoding="utf-8"))
    json.dump({"ticker": t, "cik": cik, "fragility_flags": list(btype_flags)}, open(os.path.join(d, "dcf_numbers.json"), "w", encoding="utf-8"))
    json.dump({"moat_score": 5}, open(os.path.join(d, "judgment.json"), "w", encoding="utf-8"))
    json.dump({"ticker": t}, open(os.path.join(d, "score.json"), "w", encoding="utf-8"))


def test_dedupe_drop_stable_write_and_check():
    base = tempfile.mkdtemp(prefix="industry_returns_")
    saved = IR.BASE
    try:
        for i, v in enumerate((0.10, 0.12, 0.14, 0.16, 0.18, 0.20)):
            _folder(base, f"P{i}", "3561", v, 100 + i)
        _folder(base, "FWONA", "3561", 0.30, 777)
        _folder(base, "FWONK", "3561", 0.30, 777)          # the same CIK: one member
        _folder(base, "LOSS", "3561", -9, 888)             # -inf median: dropped from the group median, counted
        _folder(base, "NOSIC", "", 0.2, 999)
        _folder(base, "BANK", "6022", 0.12, 555)            # a bank: the ROE ladder, its own group
        out = IR.build(base, built="2026-10-21")
        assert "FWONA" in out["members"] and out["excluded"]["FWONK"] == "same CIK as FWONA (one member per CIK)"
        assert out["excluded"]["NOSIC"] == "no SIC" and out["members"]["LOSS"]["median_note"] == "loss_on_nonpositive_capital"
        g = out["groups"]["default|4:3561"]
        assert g["members"] == ["FWONA", "LOSS", "P0", "P1", "P2", "P3", "P4", "P5"] and g["n"] == 7 and g["n_dropped"] == 1
        assert g["median"] == 0.16 and g["label"] == "Industry 3561" and g["metric_mix"] == {"roic": 8}
        assert out["groups"]["default|3:356"]["label"] == "SIC 356x · Industrial and Commercial Machinery and Computer Equipment"
        assert out["groups"]["default|2:35"]["label"] == "SIC 35 · Industrial and Commercial Machinery and Computer Equipment"
        assert out["members"]["BANK"]["ladder"] == "roe" and "roe|4:6022" not in out["groups"], "a one-member group is not stored"
        # the pillar for P0: leave-one-out, the -inf peer dropped and counted, FWONK never a peer
        n = {"ticker": "P0", "cik": 100, "fragility_flags": []}
        ev = M.evaluate(os.path.join(base, "P0"), n, {"moat_score": 5}, sic="3561", industry=dict(out, _sha256="y" * 64))
        p = ev["pillars"]["industry_structure"]
        assert p["peers"] == 6 and p["peers_dropped"] == 1 and p["median"] == 0.17 and p["rank"] == 7 and p["of"] == 7, p
        # the stable write and --check
        IR.BASE = base
        path = os.path.join(base, "_system", M.INDUSTRY_FILE)
        with contextlib.redirect_stdout(io.StringIO()):
            assert IR.main(["--check"]) == 1, "no file yet"
            assert IR.main(["--write"]) == 0 and os.path.exists(path)
            first = open(path, encoding="utf-8").read()
            assert IR.main(["--check"]) == 0
            doc = json.load(open(path, encoding="utf-8"))
            doc["built"] = "2020-01-01"
            json.dump(doc, open(path, "w", encoding="utf-8"), indent=1)
            assert IR.main(["--check"]) == 0, "only `built` differs: current"
            assert IR.write(path, IR.build(base)) is False, "a rebuild with no data change leaves the file"
            _folder(base, "P9", "3561", 0.5, 109)
            assert IR.main(["--check"]) == 1
            assert IR.main(["--write"]) == 0 and open(path, encoding="utf-8").read() != first
            assert IR.main(["--write", "--check"]) == 2
            js = os.path.join(base, "x.json")
            assert IR.main(["--json", js]) == 0 and json.load(open(js, encoding="utf-8"))["members"]["P9"]["median"] == 0.5
    finally:
        IR.BASE = saved
        shutil.rmtree(base, ignore_errors=True)


def test_committed_file_is_consistent():
    """The committed _system/industry_returns.json is internally consistent (IR.consistency_problems: the schema and
    rule this code writes, one ladder per group, one member per CIK, every group's members / n / n_dropped / median /
    metric mix / label recomputable from its members). It is NOT compared with a fresh build of the checkout: 03b
    §3.3.2 / §3.3.3 — a company PR does not rebuild it, so between two daily-cron runs it is legitimately one or more
    re-scores behind (--check is the currency tool; the daily cron and rebuild_scores.py --write it)."""
    path = os.path.join(SYS, M.INDUSTRY_FILE)
    if not os.path.exists(path):
        print("   (no committed industry_returns.json in this tree — skipped)")
        return
    doc = json.load(open(path, encoding="utf-8"))
    assert IR.consistency_problems(doc) == [], IR.consistency_problems(doc)[:5]


def test_consistency_is_not_currency():
    """L3 review R2: a merged company PR that moves a member's governing return leaves the committed file stale
    (--check exit 1) but consistent — the suite stays green until the next daily cron --write; a corrupted file is
    caught (a group's n, its median, a member on another ladder, a member also excluded, two members of one CIK)."""
    base = tempfile.mkdtemp(prefix="industry_returns_c_")
    saved = IR.BASE
    try:
        for i, v in enumerate((0.10, 0.12, 0.14, 0.16, 0.18, 0.20)):
            _folder(base, f"P{i}", "3561", v, 100 + i)
        _folder(base, "BANK", "6022", 0.12, 555)
        _folder(base, "BANK2", "6022", 0.14, 556)
        IR.BASE = base
        path = os.path.join(base, "_system", M.INDUSTRY_FILE)
        with contextlib.redirect_stdout(io.StringIO()):
            assert IR.main(["--write"]) == 0
            # the company PR: P3's re-score halves its returns; the file is not rebuilt
            shutil.rmtree(os.path.join(base, "P3"))
            _folder(base, "P3", "3561", 0.08, 103)
            assert IR.main(["--check"]) == 1, "stale"
        doc = json.load(open(path, encoding="utf-8"))
        assert IR.consistency_problems(doc) == [], IR.consistency_problems(doc)
        assert IR.groups_from(doc["members"]) == doc["groups"]

        def bad(mut, needle):
            d = json.loads(json.dumps(doc))
            mut(d)
            probs = IR.consistency_problems(d)
            assert any(needle in p for p in probs), (needle, probs)
        bad(lambda d: d["groups"]["default|4:3561"].__setitem__("n", 5), "default|4:3561")
        bad(lambda d: d["groups"]["default|4:3561"].__setitem__("median", 0.5), "default|4:3561")
        bad(lambda d: d["members"]["P0"].__setitem__("ladder", "roe"), "member P0: ladder 'roe'")
        bad(lambda d: d["groups"]["default|4:3561"]["members"].remove("P0"), "default|4:3561")
        bad(lambda d: d["excluded"].__setitem__("P1", "no SIC"), "P1")
        bad(lambda d: d["members"]["P2"].__setitem__("cik", 100), "CIK")
        bad(lambda d: d.__setitem__("schema", 2), "schema")
        bad(lambda d: d["members"]["P4"].update(median=None, median_note=None), "P4")
    finally:
        IR.BASE = saved
        shutil.rmtree(base, ignore_errors=True)


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
