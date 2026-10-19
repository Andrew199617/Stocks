#!/usr/bin/env python3
"""Insurer payable-earnings base (Andrew, 2026-10-19; Codex review of PR #8).
Run: python _system/tests/test_payable_base.py (or python -m pytest _system/tests).
No network: the engine's pure helpers, make_score's validation / impact /
provenance / double-softening paths, and make_score.py end to end on a
synthetic folder in a temp STOCKS_BASE.

What the rule needs, and what each test proves fails on the parent code:
1. The declared base is actually applied — `dcf_engine.payable_base_per_share`
   and `load_payable_base` exist, reproduce RNR's $27.2074/sh from the five
   filed figures, and refuse a declaration that does not reproduce.
2. ADS scaling — the pin is multiplied by ads_ratio (per-ordinary figures,
   per-ADS price).
3. make_score has a payable-base counterfactual path (`base_used` =
   payable_5y) instead of routing the pin through the TTM branch, which
   fails at any filer without a TTM.
4. The provenance check accepts the payable shape (figure for figure) and
   key_numbers.md emits the five figures so analysis.md can quote them.
5. The one-notch misfit tier_override on top of the payable base is refused.
6. A payable declaration is binding: a run not pinned through --base-judgment
   is refused (Codex round 2, P1).
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
sys.path.insert(0, SYS)
import make_score as M  # noqa: E402
import dcf_engine as E  # noqa: E402

MAKE_SCORE = os.path.join(SYS, "make_score.py")
LABELS = ["super_bear", "bear", "base", "bull", "super_bull"]
PROBS = [0.15, 0.3, 0.3, 0.15, 0.1]
# RNR: operating income available to common, FY2021-25, from the Q4 releases.
RNR_FIGS = [81_599_000.0, 322_791_000.0, 1_824_910_000.0, 2_234_426_000.0, 1_859_691_000.0]
RNR_SHARES = 46_483_000.0
RNR_BASE = 27.207439278876148


def _bo(value=RNR_BASE, **kw):
    o = {"value": value, "kind": "filing", "basis": "payable_earnings_5y",
         "figures": list(RNR_FIGS), "shares": RNR_SHARES,
         "source": "Q4 earnings releases FY2021/FY2023/FY2025", "reason": "insurer payable-earnings rule"}
    o.update(kw)
    return o


def test_engine_helper_reproduces_rnr_and_scales_by_ads_ratio():
    assert abs(E.payable_base_per_share(RNR_FIGS, RNR_SHARES) - RNR_BASE) < 1e-9
    # Per-ordinary figures at an ADS filer: the pin is per ADS.
    assert abs(E.payable_base_per_share(RNR_FIGS, RNR_SHARES, {"ratio": 4.0}) - 4 * RNR_BASE) < 1e-9
    for bad in ((RNR_FIGS[:4], RNR_SHARES), (RNR_FIGS, 0)):
        try:
            E.payable_base_per_share(*bad)
            raise AssertionError(f"accepted {bad}")
        except ValueError:
            pass


def test_engine_load_payable_base_validates_the_declaration():
    base = tempfile.mkdtemp(prefix="payable_")
    old = E.BASE
    try:
        E.BASE = base
        os.makedirs(os.path.join(base, "T"))
        p = os.path.join(base, "T", "judgment.json")

        def write(o):
            with open(p, "w", encoding="utf-8") as f:
                json.dump({"base_override": o}, f)

        write(_bo())
        assert E.load_payable_base("T")["value"] == RNR_BASE
        for o in (_bo(value=77.78),                       # does not reproduce
                  _bo(kind="estimate"),                   # must be filing
                  _bo(figures=RNR_FIGS[:3]),              # five figures
                  _bo(shares=0),                          # positive shares
                  _bo(basis="median_3y"),                 # wrong basis
                  _bo(source="")):                        # provenance
            write(o)
            try:
                E.load_payable_base("T")
                raise AssertionError(f"accepted {o}")
            except ValueError:
                pass
    finally:
        E.BASE = old
        shutil.rmtree(base, ignore_errors=True)


def test_measure_run_drops_the_judgment_pin():
    """_measure_run compares engine-native bases: --base-judgment is dropped
    like --ttm, so the counterfactual never re-pins."""
    old = sys.argv
    try:
        sys.argv = ["dcf_engine.py", "T", "--moat", "5", "--base-judgment", "--measure"]
        calls = {}

        def fake_run(args, **kw):
            calls["args"] = args
            raise RuntimeError("stop")
        real = E.subprocess.run
        E.subprocess.run = fake_run
        try:
            E._measure_run("T", 10.0, True)
        finally:
            E.subprocess.run = real
        assert "--base-judgment" not in calls["args"] and "--moat" in calls["args"], calls
    finally:
        sys.argv = old


def _n(payable=True, flags=(), gap=()):
    n = {"ticker": "TST", "engine_version": 5, "engine_release": "5.4", "data_gap": list(gap), "as_of": "2026-10-19",
         "tier_by_numbers": "C", "moat_score": 5, "price": 351.06, "price_source": "manual",
         "market_cap_est": 1.46e10, "cik": 1, "latest_period_end": "2025-12-31",
         "base_oe_per_share": RNR_BASE, "base_source": "judgment_base_override",
         "inputs": {"moat": 5.0, "probs": PROBS, "offsets": [-0.33, -0.256, -0.226, -0.186, -0.11],
                    "mults": [0.75, 0.9, 1.0, 1.1, 1.25], "g_terminal": 0.025,
                    "base_oe_ps_arg": RNR_BASE, "base_pin_source": "judgment_base_override"},
         "scenarios": {lbl: {"prob": p, "iv_at_15": 260.0, "iv_at_12": 320.0, "irr": 0.12, "g_start": 0.03,
                             "oe_mult": 1.0} for lbl, p in zip(LABELS, PROBS)},
         "weighted": {"iv_at_15": 260.0, "iv_at_12": 320.0, "iv_at_10": 380.0},
         "implied_irr_weighted": 0.12, "implied_irr_base": 0.12, "iv_at_15": 260.0, "iv_at_12": 320.0,
         "upside_at_15": -0.26, "fragility_flags": list(flags), "diagnostics": {},
         "payable_base": {"basis": "payable_earnings_5y", "figures": list(RNR_FIGS), "average": sum(RNR_FIGS) / 5,
                          "shares": RNR_SHARES, "per_ordinary_share": RNR_BASE, "ads_ratio": 1.0,
                          "pinned_per_share": RNR_BASE} if payable else None}
    return n


def test_make_score_impact_uses_the_payable_branch_not_ttm():
    """Parent code: any --base-oe-ps pin is a 'ttm' base and calls ttm.py,
    which fails at a filer with no TTM (RNR). The payable branch replays the
    same pin with field overrides off and never touches ttm.py."""
    n = _n(gap=["capex"])
    n["data_gap_uncovered"] = []
    seen = []

    def fake_run_json(cmd, env_extra=None, timeout=600):
        seen.append((cmd, env_extra))
        assert "ttm.py" not in " ".join(cmd), cmd
        assert "--base-oe-ps" in cmd and env_extra == {"DCF_NO_OVERRIDES": "1"}
        return {"base_oe_per_share": RNR_BASE, "implied_irr_weighted": 0.118, "data_gap": []}
    real = M._run_json
    M._run_json = fake_run_json
    try:
        imp = M.compute_override_impact("TST", n)
    finally:
        M._run_json = real
    assert seen, "no counterfactual replay ran"
    assert imp["base_used"] == "payable_5y", imp
    assert imp["base_oe_impact_pct"] == 0.0 and imp["base_oe_with_override"] == round(RNR_BASE, 4), imp
    assert abs(imp["weighted_irr_impact_pp"] - 0.2) < 1e-6 and imp["unblocks_tier"] is True, imp

    # The gate firing in the replay (the override covers the only capex
    # history) is an honest null when the override unblocks the tier.
    M._run_json = lambda cmd, env_extra=None, timeout=600: {"base_oe_per_share": None, "implied_irr_weighted": None,
                                                           "data_gap": ["capex"]}
    try:
        imp = M.compute_override_impact("TST", n)
    finally:
        M._run_json = real
    assert imp["weighted_irr_without_override"] is None and imp["unblocks_tier"] is True, imp


def test_validate_and_double_softening():
    assert M.validate_base_override({"base_override": _bo()})["value"] == RNR_BASE
    for o in (_bo(value=77.78), _bo(kind="estimate"), _bo(figures=RNR_FIGS[:4])):
        try:
            M.validate_base_override({"base_override": o})
            raise AssertionError(f"accepted {o}")
        except SystemExit:
            pass
    n = _n()
    assert M.check_no_double_softening(n, {"tier_override": None}, "misfit") is None
    assert M.check_no_double_softening(n, {"tier_override": "D"}, "misfit"), "notch on top of the payable base must refuse"
    assert M.check_no_double_softening(_n(payable=False), {"tier_override": "D"}, "misfit") is None  # OCF base: the 10-15 rule
    assert M.check_no_double_softening(n, {"tier_override": "D"}, "modeled") is None


def _score_files(n, j):
    base = tempfile.mkdtemp(prefix="payable_e2e_")
    try:
        t = "TST"
        os.makedirs(os.path.join(base, t)); os.makedirs(os.path.join(base, "_system"))
        canon = json.dumps(n, sort_keys=True, separators=(",", ":"), default=str)
        n["content_hash"] = hashlib.sha256(canon.encode()).hexdigest()
        for name, obj in (("dcf_numbers.json", n), ("judgment.json", j)):
            with open(os.path.join(base, t, name), "w", encoding="utf-8") as f:
                json.dump(obj, f, indent=1, ensure_ascii=False)
        reg = os.path.join(base, "_system", "overrides_registry.json")
        env = dict(os.environ, STOCKS_BASE=base, PYTHONIOENCODING="utf-8", MAKE_SCORE_REGISTRY=reg)
        r = subprocess.run([sys.executable, MAKE_SCORE, t], capture_output=True, text=True, encoding="utf-8",
                           env=env, timeout=120)
        out = {"rc": r.returncode, "stderr": r.stderr, "stdout": r.stdout}
        if r.returncode == 0:
            with open(os.path.join(base, t, "score.json"), encoding="utf-8") as f:
                out["score"] = json.load(f)
            with open(os.path.join(base, t, "key_numbers.md"), encoding="utf-8") as f:
                out["key"] = f.read()
            with open(reg, encoding="utf-8") as f:
                out["registry"] = json.load(f)
        return out
    finally:
        shutil.rmtree(base, ignore_errors=True)


def _j(override=None, bo=None):
    return {"name": "Test Re", "sector": "Finance / Reinsurance", "moat_score": 5, "moat_justification": "t",
            "probs_used": PROBS, "one_liner": "t", "confidence": "low",
            "tier_override": override, "tier_override_reason": "one notch" if override else None,
            "in_scope_under_40b": True, "base_override": bo if bo is not None else _bo()}


def test_make_score_end_to_end_on_the_payable_base():
    misfit = ["SECTOR_MODEL_MISMATCH: Finance sector — OE/capex DCF fits finance names poorly; grade confidence low"]
    r = _score_files(_n(flags=misfit), _j())
    assert r["rc"] == 0, r["stderr"] + r["stdout"]
    s = r["score"]
    assert s["tier_final"] == "C" and s["model_fit"] == "misfit", s
    assert abs(s["base_oe_per_share"] - RNR_BASE) < 1e-6, s
    assert "## Payable-earnings base" in r["key"] and "$1,824,910,000" in r["key"], r["key"]
    ev = [e for e in r["registry"]["entries"] if e.get("event") == "base_override"]
    assert ev and ev[0]["basis"] == "payable_earnings_5y" and ev[0]["figures"] == RNR_FIGS, ev
    # Provenance: a declaration whose figures differ from the engine's record is refused.
    bad = _bo(); bad["figures"][0] = 81_599_001.0; bad["value"] = sum(bad["figures"]) / 5 / RNR_SHARES
    r = _score_files(_n(flags=misfit), _j(bo=bad))
    assert r["rc"] != 0 and "provenance" in (r["stderr"] + r["stdout"]), r
    # The 2026-10-15 notch on top of the payable base is refused.
    r = _score_files(_n(flags=misfit), _j(override="D"))
    assert r["rc"] != 0 and "double-counting" in (r["stderr"] + r["stdout"]), r
    # A payable declaration is binding: a run not pinned through
    # --base-judgment (median run, or a --base-oe-ps typed with the
    # per-ordinary value) is refused, never scored on the wrong base.
    n = _n(payable=False); n["base_source"] = "median_of_last_3_fy_oe_per_share"
    n["inputs"].update({"base_oe_ps_arg": None, "base_pin_source": None}); n["base_oe_per_share"] = 77.78
    r = _score_files(n, _j())
    assert r["rc"] != 0 and "--base-judgment" in (r["stderr"] + r["stdout"]), r
    n = _n(payable=False); n["inputs"]["base_pin_source"] = "base_oe_ps_arg"
    r = _score_files(n, _j())
    assert r["rc"] != 0 and "--base-judgment" in (r["stderr"] + r["stdout"]), r


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
