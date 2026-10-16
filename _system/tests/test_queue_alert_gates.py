#!/usr/bin/env python3
"""make_score.py alert-gate tests (the pass-2 alert rule in SECOND_PASS.md).
Run: python _system/tests/test_queue_alert_gates.py (or python -m pytest _system/tests).

Covers the Codex finding on PR #2 ("use an exit-appropriate eligibility check
for S/A downgrades"): alert_eligible is false below Tier A by construction, so
an A -> B exit could never alert. make_score.py now also writes
exit_alert_eligible (+ exit_alert_suppressed_reason). Tests: alert_reasons()
on the exit cases (clean downgrade, low confidence, misfit, override-only
tier, a judgment override pushing an S/A numeric tier below A, which still
alerts, an override between two sub-A tiers, the IRR floor); alert_eligible /
alert_suppressed_reason unchanged on an exhaustive grid against the pre-fix
logic; make_score.py end to end on a synthetic folder in a temp STOCKS_BASE
(an engine-stamped dcf_numbers.json with a valid content_hash, no network, no
real folder); and the same run under the locale encoding (-X utf8=0, cp1252
on Windows) with raw UTF-8 judgment text and a key_numbers.md arrow.
"""
import hashlib
import itertools
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

MAKE_SCORE = os.path.join(SYS, "make_score.py")
LABELS = ["super_bear", "bear", "base", "bull", "super_bull"]
PROBS = [0.1, 0.25, 0.3, 0.25, 0.1]


def old_entry_reasons(tier_final, tier_by_numbers, override, conf, model_fit, unblocks, irr_at_floor):
    """make_score.py's alert reasons before the fix, verbatim."""
    reasons = []
    if tier_final in ("S", "A"):
        if conf == "low": reasons.append("confidence low")
        if model_fit == "misfit": reasons.append("sector model misfit")
        if unblocks: reasons.append("tier exists only because of a judgment override")
        if override and tier_by_numbers not in ("S", "A"):
            reasons.append(f"tier rests on a judgment tier override (numeric tier {tier_by_numbers})")
        if irr_at_floor: reasons.append("IRR at solver floor")
    return reasons


def test_entry_reasons_unchanged_on_every_input():
    tiers = ("S", "A", "B", "C", "D", "F")
    n = 0
    for numeric, override, conf, fit, unb, floor in itertools.product(
            tiers, (None,) + tiers, ("low", "medium", "high"), ("modeled", "misfit"), (False, True), (False, True)):
        final = override or numeric
        entry, _ = M.alert_reasons(final, numeric, override, conf, fit, unb, floor)
        assert entry == old_entry_reasons(final, numeric, override, conf, fit, unb, floor), (numeric, override, conf, fit, unb, floor)
        n += 1
    assert n == 6 * 7 * 3 * 2 * 2 * 2


def test_exit_reasons():
    R = M.alert_reasons
    # The reviewer's case: a clean A -> B downgrade (numbers say B, medium confidence).
    assert R("B", "B", None, "medium", "modeled", False, False) == ([], [])
    assert R("D", "D", None, "high", "modeled", False, False) == ([], [])
    assert R("B", "B", None, "low", "modeled", False, False) == ([], ["confidence low"])
    assert R("C", "C", None, "medium", "misfit", False, False) == ([], ["sector model misfit"])
    assert R("B", "B", None, "medium", "modeled", True, False) == ([], ["tier exists only because of a judgment override"])
    # A judgment override pushing an S/A numeric tier below A (EXPE's real
    # shape: numbers A, override B) is still an exit warning; only a
    # judgment-only upgrade is kept from alerting.
    assert R("B", "A", "B", "medium", "modeled", False, False) == ([], [])
    # An override between two sub-A tiers does not decide the exit.
    assert R("C", "B", "C", "medium", "modeled", False, False) == ([], [])
    # The IRR floor confirms a drop ("at most terminal growth"); it suppresses entries only.
    assert R("F", "F", None, "medium", "modeled", False, True) == ([], [])
    assert R("A", "A", None, "medium", "modeled", False, True) == (["IRR at solver floor"], [])
    # S/A scores carry no exit reasons; sub-A scores carry no entry reasons.
    assert R("A", "A", None, "low", "misfit", True, True)[1] == []
    assert R("B", "B", None, "low", "misfit", True, True)[0] == []


def _folder(base, tier_by_numbers="B", confidence="medium", override=None, one_liner="test", extra_n=None):
    t = "TST"
    os.makedirs(os.path.join(base, t), exist_ok=True)
    os.makedirs(os.path.join(base, "_system"), exist_ok=True)
    n = {"ticker": t, "engine_version": 5, "engine_release": "5.4", "data_gap": [], "as_of": "2026-10-15",
         "tier_by_numbers": tier_by_numbers, "moat_score": 6, "price": 50.0, "price_source": "nasdaq",
         "market_cap_est": 5e9, "cik": 1, "latest_period_end": "2025-12-31",
         "base_oe_per_share": 3.0, "base_source": "median_3y", "inputs": {},
         "scenarios": {lbl: {"prob": p, "iv_at_15": 50.0, "iv_at_12": 60.0, "irr": 0.13, "g_start": 0.08,
                             "oe_mult": 1.0} for lbl, p in zip(LABELS, PROBS)},
         "weighted": {"iv_at_15": 50.0, "iv_at_12": 60.0, "iv_at_10": 70.0},
         "implied_irr_weighted": 0.13, "implied_irr_base": 0.13, "iv_at_15": 50.0, "iv_at_12": 60.0,
         "upside_at_15": 0.0, "fragility_flags": [], "diagnostics": {}}
    n.update(extra_n or {})
    canon = json.dumps(n, sort_keys=True, separators=(",", ":"), default=str)
    n["content_hash"] = hashlib.sha256(canon.encode()).hexdigest()
    j = {"name": "Test Co", "sector": "Industrials", "moat_score": 6, "moat_justification": "test",
         "probs_used": PROBS, "one_liner": one_liner, "confidence": confidence,
         "tier_override": override, "tier_override_reason": "test reason" if override else None,
         "in_scope_under_40b": True}
    for name, obj in (("dcf_numbers.json", n), ("judgment.json", j)):
        with open(os.path.join(base, t, name), "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=1, ensure_ascii=False)  # raw UTF-8, like the real judgment files
    return t


def _score_files(locale_encoding=False, **kw):
    """(score.json, key_numbers.md text) from make_score.py on a synthetic
    folder. locale_encoding runs it with UTF-8 mode off, so open() defaults to
    the locale encoding (cp1252 on Windows), as on a PC without PYTHONUTF8."""
    base = tempfile.mkdtemp(prefix="alert_gates_")
    try:
        t = _folder(base, **kw)
        env = dict(os.environ, STOCKS_BASE=base, PYTHONIOENCODING="utf-8",
                   MAKE_SCORE_REGISTRY=os.path.join(base, "_system", "overrides_registry.json"))
        env.pop("PYTHONUTF8", None)
        flags = ["-X", "utf8=0"] if locale_encoding else []
        r = subprocess.run([sys.executable, *flags, MAKE_SCORE, t], capture_output=True, text=True,
                           encoding="utf-8", env=env, timeout=120)
        assert r.returncode == 0, r.stderr
        with open(os.path.join(base, t, "score.json"), encoding="utf-8") as f:
            score = json.load(f)
        with open(os.path.join(base, t, "key_numbers.md"), encoding="utf-8") as f:
            return score, f.read()
    finally:
        shutil.rmtree(base, ignore_errors=True)


def _score(**kw):
    return _score_files(**kw)[0]


def test_make_score_end_to_end():
    s = _score(tier_by_numbers="B")  # the A -> B downgrade a second pass would write
    assert s["tier_final"] == "B" and s["alert_eligible"] is False and s["exit_alert_eligible"] is True, s
    assert "alert_suppressed_reason" not in s and "exit_alert_suppressed_reason" not in s
    s = _score(tier_by_numbers="B", confidence="low")
    assert s["exit_alert_eligible"] is False and s["exit_alert_suppressed_reason"] == "confidence low", s
    s = _score(tier_by_numbers="A", override="B")  # a judgment downgrade still warns
    assert s["tier_final"] == "B" and s["exit_alert_eligible"] is True, s
    assert "exit_alert_suppressed_reason" not in s, s
    s = _score(tier_by_numbers="A")  # entries are gated exactly as before
    assert s["alert_eligible"] is True and s["exit_alert_eligible"] is False, s
    assert "alert_suppressed_reason" not in s and "exit_alert_suppressed_reason" not in s
    s = _score(tier_by_numbers="A", confidence="low")
    assert s["alert_eligible"] is False and s["alert_suppressed_reason"] == "confidence low", s
    assert "exit_alert_suppressed_reason" not in s


def test_make_score_utf8_under_the_locale_encoding():
    """Most real judgment.json files carry raw UTF-8. Under cp1252 the old
    open() calls turned it into mojibake (or refused bytes such as 0x81) and
    crashed writing key_numbers.md's arrow after score.json was written."""
    text = "\u00c1 la carte pricing \u2192 durable margins \u2014 12% ROIC"
    s, key = _score_files(locale_encoding=True, tier_by_numbers="B", one_liner=text,
                          extra_n={"g_blend": 0.08, "g_base": 0.07})
    assert s["one_liner"] == text, s["one_liner"]
    assert "\u2192 g_base 7.00%" in key and "\u2014 key numbers" in key, key[:300]


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
