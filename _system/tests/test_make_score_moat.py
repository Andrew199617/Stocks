#!/usr/bin/env python3
"""make_score.py under moat rubric 2 (2026-10-21; Andrew's request in the "Tighten moat scoring" thread, 2026-10-20).
Run: python _system/tests/test_make_score_moat.py (or python -m pytest _system/tests).

End-to-end on a synthetic folder in a temp STOCKS_BASE (test_make_score_55's
harness: an engine-stamped dcf_numbers.json, the registry redirected, no
network), with a fundamentals.json copied from the frozen fixture rows of
test_moat_evidence. Every case fails on the code before this change (no
moat_evidence block, no key_numbers lines, no entry-gate reason):

1. A Tier A score whose moat sits above its evidence band with no reason
   (ROP-shaped returns, moat 7 vs band 1-5): alert_eligible false with
   "moat 7 above the evidence band 1–5 (unexplained) — MOAT_ABOVE_EVIDENCE",
   score.json moat_evidence records it, key_numbers.md prints the evidence,
   make_score prints the flag. A Tier B score with the same moat keeps its
   exit gate: the moat closes entries only.
2. In band (HALO-shaped, moat 7 vs 4-8) or explained by a mechanically tested
   reason (ROP at 6 with ACQUIRED_GOODWILL): the entry gate stays open.
3. A text-only reason (SHORT_HISTORY on FIG-shaped history) is recorded as an
   explanation but keeps the entry gate closed.
4. Below the band (MANH-shaped, moat 6 vs 7-10): recorded as
   MOAT_BELOW_EVIDENCE, no gate touched.
5. No fundamentals.json: moat_evidence "not_measured", the score is written,
   the gates are as before.
6. A malformed moat_evidence_reason or moat_sources refuses with nothing
   written; well-formed moat_sources are copied to score.json.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
sys.path.insert(0, SYS)
sys.path.insert(0, HERE)
import make_score as MS  # noqa: E402
import test_make_score_55 as H  # noqa: E402  (the harness only: its tests are not collected from this module)

with open(os.path.join(HERE, "fixtures", "moat_evidence", "fundamentals_rows.json"), encoding="utf-8") as _f:
    FX = json.load(_f)
TEXT = "The filing states the figure this reason rests on, in these words."


def _run(shape, moat, tier="A", fundamentals=True, **jkw):
    """make_score on a fresh folder: tier A (weighted IRR 22%) or B, the engine run at `moat`, `shape`'s fundamentals."""
    kw = dict(tier_by_numbers=tier, implied_irr_weighted=0.22 if tier == "A" else 0.17, moat_score=moat)
    n = H._numbers(**kw)
    n["inputs"] = dict(n["inputs"], moat=moat)
    j = H._judgment(n, moat_score=moat, **jkw)
    r = H.Run(n, j)
    try:
        if fundamentals:
            with open(os.path.join(r.folder, "fundamentals.json"), "w", encoding="utf-8") as f:
                json.dump(FX[shape], f)
        r.run()
        r.result = dict(r.state(), score=r.score() if r.rc == 0 else None, key=r.key() if r.rc == 0 else None)
    finally:
        r.close()
    return r


def test_moat_above_the_band_closes_the_entry_gate():
    r = _run("ROP", 7).ok()
    s = r.result["score"]
    assert s["tier_final"] == "A" and s["alert_eligible"] is False, s
    assert s["alert_suppressed_reason"] == "moat 7 above the evidence band 1–5 (unexplained) — MOAT_ABOVE_EVIDENCE", s
    me = s["moat_evidence"]
    assert me["rubric"] == 2 and me["status"] == "outside_band_unexplained" and me["flag"] == "MOAT_ABOVE_EVIDENCE"
    assert me["evidence_band"] == [1, 5] and me["anchor_r"] == 3 and me["entry_gate_closed"] is True
    k = r.result["key"]
    assert "- Moat evidence (roic, hurdle 10%)" in k and "→ anchor 3.12 (3) · band 1–5" in k
    assert "- Moat vs evidence: 7 → above band 1–5, unexplained (MOAT_ABOVE_EVIDENCE — entry alert closed)" in k
    assert k.index("- Moat: 7/10") < k.index("- Moat evidence"), "the evidence lines sit under the moat line"
    assert "TST moat 7 is above the evidence band 1–5 — MOAT_ABOVE_EVIDENCE; entry alert closed" in r.out, r.out
    # the same moat on a Tier B score: exits are a warning a holder needs, the moat never closes them
    s = _run("ROP", 7, tier="B").ok().result["score"]
    assert s["exit_alert_eligible"] is True and "exit_alert_suppressed_reason" not in s, s
    assert s["moat_evidence"]["flag"] == "MOAT_ABOVE_EVIDENCE"


def test_in_band_or_tested_reason_keeps_the_entry_gate():
    s = _run("HALO", 7).ok().result["score"]
    assert s["alert_eligible"] is True and s["moat_evidence"]["status"] == "in_band", s
    r = _run("ROP", 6, moat_evidence_reason={"code": "ACQUIRED_GOODWILL", "text": TEXT}).ok()
    s = r.result["score"]
    assert s["alert_eligible"] is True and "alert_suppressed_reason" not in s, s
    me = s["moat_evidence"]
    assert me["status"] == "outside_band_explained" and me["reach"] == [1, 6] and me["reason_tested"] is True
    assert "explained by ACQUIRED_GOODWILL (reach 1–6)" in r.result["key"]
    assert "MOAT_ABOVE_EVIDENCE" not in r.out


def test_text_only_reason_keeps_the_entry_gate_closed():
    s = _run("FIG", 7, moat_evidence_reason={"code": "SHORT_HISTORY", "text": TEXT}).ok().result["score"]
    assert s["alert_eligible"] is False and s["moat_evidence"]["status"] == "outside_band_explained", s
    assert s["alert_suppressed_reason"] == ("moat 7 above the evidence band 0–5 (explained only by the text reason "
                                            "SHORT_HISTORY) — MOAT_ABOVE_EVIDENCE"), s


def test_moat_below_the_band_is_recorded_only():
    r = _run("MANH", 6).ok()
    s = r.result["score"]
    assert s["alert_eligible"] is True and s["moat_evidence"]["flag"] == "MOAT_BELOW_EVIDENCE", s
    assert "MOAT_BELOW_EVIDENCE; recorded, no gate" in r.out
    s = _run("MANH", 6, tier="B").ok().result["score"]
    assert s["exit_alert_eligible"] is True


def test_no_fundamentals_is_not_measured():
    r = _run("ROP", 7, fundamentals=False).ok()
    s = r.result["score"]
    assert s["alert_eligible"] is True and s["moat_evidence"]["status"] == "not_measured", s
    assert s["moat_evidence"]["evidence_status"] == "not_measured"
    assert "- Moat evidence: not measured (no fundamentals.json)" in r.result["key"]
    assert "- Moat vs evidence: 7 → not measured" in r.result["key"]


def test_malformed_reason_or_sources_refuse_and_sources_are_recorded():
    _run("ROP", 7, moat_evidence_reason={"code": "GOODWILL", "text": TEXT}).refused("moat_evidence_reason.code")
    _run("ROP", 7, moat_evidence_reason="ACQUIRED_GOODWILL").refused("moat_evidence_reason must be an object")
    _run("ROP", 7, moat_sources="switching_costs").refused("moat_sources must be a list")
    _run("HALO", 7, moat_sources=[{"source": "patents", "evidence": "a long patent list on the drug platform"}]
         ).refused("source must be one of")
    # the shapes refuse even with no fundamentals.json to measure against
    _run("ROP", 7, fundamentals=False, moat_evidence_reason={"code": "X", "text": TEXT}).refused("moat_evidence_reason.code")
    src = [{"source": "intangible_assets", "evidence": "ENHANZE royalties run to the 2030s on partner drugs"}]
    s = _run("HALO", 7, moat_sources=src).ok().result["score"]
    assert s["moat_sources"] == src and s["moat_evidence"]["sources_declared"] is True
    s = _run("HALO", 7, moat_sources=[]).ok().result["score"]
    assert s["moat_evidence"]["band"] == [4, 4] and s["alert_eligible"] is False, "an explicitly empty list caps at 4"


def test_alert_reasons_moat_gate_unit():
    gate = "moat 7 above the evidence band 1–5 (unexplained) — MOAT_ABOVE_EVIDENCE"
    assert MS.alert_reasons("A", "A", None, "medium", "modeled", False, False, moat_gate=gate) == ([gate], [])
    assert MS.alert_reasons("B", "B", None, "medium", "modeled", False, False, moat_gate=gate) == ([], [])
    assert MS.alert_reasons("A", "A", None, "medium", "modeled", False, False) == ([], [])
    assert MS.moat_gate_reason({"entry_gate_closed": False}) is None
    assert MS.moat_gate_reason({"entry_gate_closed": True, "band": [1, 5], "moat": 7.0,
                                "status": "outside_band_unexplained"}) == gate


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
