#!/usr/bin/env python3
"""make_score.py under engine release 5.5 (DESIGN_5.5 §1, §2c, §7, §8).
Run: python _system/tests/test_make_score_55.py (or python -m pytest _system/tests).

Every end-to-end case runs make_score.py on a synthetic folder in a temp
STOCKS_BASE (an engine-stamped dcf_numbers.json with a valid content_hash, the
registry redirected with MAKE_SCORE_REGISTRY, no network, no real folder), in
the style of test_queue_alert_gates. The temp base's _system/dcf_engine.py and
_system/ttm.py — the scripts make_score spawns for the override-impact
counterfactual — are fail-loud stand-ins that leave a marker file, so a test
can prove that no counterfactual was spawned (and a control proves the
stand-in is reached when one is).

1. Pre-5.5 ADS market cap: ratio 100 / 2 / 0.5 → market_cap_b = price ×
   shares_diluted_latest ÷ ratio, market_cap_basis
   "ads_corrected_by_make_score", key_numbers.md prints the corrected cap with
   its label and the engine's old figure, and the net-debt ratio on the ADS
   basis (× ratio, with the HIGH_NET_DEBT / BIG_NET_CASH crossing named). A
   pre-5.5 run without an ADS ratio is unchanged (basis "diluted_latest").
2. Scope rewrite: judgment in_scope false + old cap > $40B + corrected cap <
   $40B → judgment.json rewritten true (one token; compact raw-UTF-8 and
   indented \\u-escaped files both keep their formatting), score
   in_scope_corrected_by_make_score, registry scope_correction event; a re-run
   is idempotent; the reverse (ratio 0.5) rewrites to false; a disagreement
   the old cap does not explain still refuses, and a 5.5 run never rewrites.
3. Release mismatch: no counterfactual subprocess is spawned; the prior
   score.json override_impact is carried (impact_carried_from_prior_score,
   counterfactual_engine_release) when it was measured on this run's base,
   else the impact fields are null with the note; a current-release run does
   spawn (control).
4. Stale-release alert suppression: Tier A pre-5.5 → alert_eligible false
   with the reason, exit_alert_eligible false; Tier B → exit gate closed with
   the reason; a current-release Tier A keeps today's gates.
5. Override currency: "USD" + filing accepted (any case), "USD" + estimate
   refused, "EUR" / non-string refused; a USD declaration the run FX-converted
   anyway (pre-5.5 with fx_conversion, or currency_basis "converted") refuses.
6. share_class_mismatch: true / object / object without source (or without
   value, with a source) all refuse; false, null, an empty object or one whose
   value is false declare nothing (the engine's rule); a 5.5 run's share_class
   gap refuses naming the declaration.
7. A 5.5 record with market_cap_basis passes through (never divided twice).
8. key_numbers.md: capex basis per last-3 FY (CSV, else capex_provenance),
   share basis (split / divergence / scale defect), SBC-reconciled periods.
9. [ADDITION — WY] OVERRIDE_SUPERSEDED_BY_FILED_TAG:capex (or recorded
   superseded_periods) beside a capex_override still in judgment.json refuses
   (applied to history years or filling nothing), naming the filed periods and
   both resolutions; with the override removed it scores.
10. [ADDITION — HTHT] an applied override recorded currency_basis
   'last_filed_unit_usd' at a filer converted from CNY / GBP with no currency
   "USD" on the judgment override refuses; a USD declaration (PUK / CX), a
   converted or declared-USD record, an unapplied override and a pre-5.5
   record pass the check.
Round-1 verification rulings (FIX_DECISIONS_R1 M1-M5, M7), each failing on the
code before it:
11. M1: the net-debt ratio on the ADS basis is printed and recorded
   (net_debt_to_normalized_oe_ads_basis) for every pre-5.5 ADS record,
   whatever state its cap is in — a 5.4.0 record whose cap main already divided
   (TX: 1.04x → 10.44x, HIGH_NET_DEBT; LTM: 0.00x → 3.33x) and a pre-5.4
   uncorrected one (JD: BIG_NET_CASH); never for a 5.5 record. M2: ratio 1 is
   no correction (basis diluted_latest, no ADS line, no ADS-basis ratio).
12. M3: a stale payable-earnings record spawns nothing and writes a consistent
   score + registry + key_numbers (the registry event carries the prior
   measurement on this base, else null fields with the note); an
   override_impact on a payable pin says base_used payable_5y; on a current
   release the payable replay runs before any write.
13. HTHT gate: a kind "estimate" override under the last-filed-unit basis is
   refused too (it cannot declare a currency); a filing override is gated
   whatever fx_conversion says.
14. M5: malformed share_class_mismatch values ("false", "no", "true", numbers,
   lists, {value: "false"}, {value: null}, {reason} only) refuse with the
   accepted shapes; dcf_engine.load_share_class_mismatch classifies every shape
   the same way and records a malformed value without a gap (offline engine
   run on the CCJ fixture, in a subprocess).
15. M7: key_numbers.md prints unconfirmed post-FY split facts and the
   in-history split facts.
16. Verifier round 2: a prior override_impact that is itself "not measured"
   is never carried (unit + make_score run twice over one stale record).
17. Re-score audit: a pin-rescued tier (share_scale.rescued_by_pin) closes
   both alert gates and the registry base_override event records kind and
   the pin's impact; an unchanged registry declaration keeps the date it
   was first recorded (a second run changes nothing).
Unit cases: release_tuple / predates_55 / scope_decision /
rewrite_judgment_scope / carried_override_impact / alert_reasons.
"""
import copy
import csv
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
PROBS = [0.1, 0.25, 0.3, 0.25, 0.1]
CUR = E.ENGINE_RELEASE  # the tests never hard-code the release string
# engine output from another (older) release: absent (a pre-5.4 run), an old 5.3.x, and 5.4.0 once 5.5 is current
STALE = [None, "5.3.1"] + (["5.4.0"] if CUR != "5.4.0" else [])
PREDATES = f"engine output predates release {CUR}"
T = "TST"

FAIL_LOUD = r'''import os, sys
# Fail-loud stand-in (test_make_score_55): make_score.py must not spawn this script in the case under test.
here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, "SPAWNED_" + os.path.basename(__file__) + ".txt"), "a", encoding="utf-8") as f:
    f.write(" ".join(sys.argv) + "\n")
sys.stderr.write("fail-loud stand-in: " + os.path.basename(__file__) + " was spawned\n")
sys.exit(97)
'''


def _numbers(release=CUR, **kw):
    """A synthetic engine record (B tier unless overridden); release None drops the key (a pre-5.4 run)."""
    n = {"ticker": T, "engine_version": 5, "engine_release": release, "data_gap": [], "as_of": "2026-10-18",
         "tier_by_numbers": "B", "moat_score": 6, "price": 20.0, "price_source": "nasdaq",
         "shares_diluted_latest": 1e9, "market_cap_est": 20e9, "net_debt_latest": 1e9, "cik": 1,
         "latest_period_end": "2025-12-31", "filer_annual_form": "10-K",
         "base_oe_per_share": 3.0, "base_source": "median_of_last_3_fy_oe_per_share",
         "inputs": {"moat": 6, "probs": PROBS, "offsets": [-0.12, -0.05, 0.0, 0.05, 0.12],
                    "mults": [0.75, 0.9, 1.0, 1.1, 1.25], "g_terminal": 0.025, "base_oe_ps_arg": None},
         "scenarios": {lbl: {"prob": p, "iv_at_15": 25.0, "iv_at_12": 30.0, "irr": 0.17, "g_start": 0.08,
                             "oe_mult": 1.0} for lbl, p in zip(LABELS, PROBS)},
         "weighted": {"iv_at_15": 25.0, "iv_at_12": 30.0, "iv_at_10": 35.0},
         "implied_irr_weighted": 0.17, "implied_irr_base": 0.17, "iv_at_15": 25.0, "iv_at_12": 30.0,
         "upside_at_15": 0.25, "fragility_flags": [],
         "diagnostics": {"oe_yield": 0.15, "net_debt_to_normalized_oe": 0.33, "months_since_fy_end": 9.5}}
    n.update(kw)
    if release is None:
        n.pop("engine_release")
    return n


def _ads(ratio, price, shares=1e9, release=None, **kw):
    """A pre-5.5 ADS record: the engine's cap is the uncorrected price × ordinary shares."""
    a = {"ratio": ratio, "source": "Form 20-F cover page", "reason": "the price is per ADS"}
    fields = dict(filer_annual_form="20-F", price=price, shares_diluted_latest=shares, market_cap_est=price * shares,
                  ads_ratio=a)
    fields.update(kw)
    return _numbers(release=release, **fields)


def _judgment(n=None, **kw):
    j = {"name": "Test Co", "sector": "Industrials", "moat_score": 6, "moat_justification": "test",
         "probs_used": PROBS, "one_liner": "Résumé — test", "confidence": "medium",
         "tier_override": None, "tier_override_reason": None, "in_scope_under_40b": True}
    if n is not None and n.get("ads_ratio"):
        j["ads_ratio"] = dict(n["ads_ratio"])
    j.update(kw)
    return j


def _stamp(n):
    n = {k: v for k, v in n.items() if k != "content_hash"}
    canon = json.dumps(n, sort_keys=True, separators=(",", ":"), default=str)
    return dict(n, content_hash=hashlib.sha256(canon.encode()).hexdigest())


class Run:
    """One synthetic folder in a temp STOCKS_BASE; make_score.py runs as a subprocess."""

    def __init__(self, n, j=None, judgment_text=None, prior_score=None, csv_rows=None):
        self.base = tempfile.mkdtemp(prefix="make_score_55_")
        self.folder = os.path.join(self.base, T)
        self.sysdir = os.path.join(self.base, "_system")
        os.makedirs(self.folder)
        os.makedirs(self.sysdir)
        for name in ("dcf_engine.py", "ttm.py"):
            with open(os.path.join(self.sysdir, name), "w", encoding="utf-8") as f:
                f.write(FAIL_LOUD)
        self.registry = os.path.join(self.sysdir, "overrides_registry.json")
        with open(os.path.join(self.folder, "dcf_numbers.json"), "w", encoding="utf-8") as f:
            json.dump(_stamp(n), f, indent=1, ensure_ascii=False)
        if judgment_text is None:
            judgment_text = json.dumps(j if j is not None else _judgment(n), indent=1, ensure_ascii=False) + "\n"
        with open(self.jpath, "w", encoding="utf-8", newline="") as f:
            f.write(judgment_text)
        self.had_prior = prior_score is not None
        if prior_score is not None:
            with open(os.path.join(self.folder, "score.json"), "w", encoding="utf-8") as f:
                json.dump(prior_score, f, indent=1)
        if csv_rows:
            with open(os.path.join(self.folder, "financials_history.csv"), "w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
                w.writeheader()
                w.writerows(csv_rows)

    @property
    def jpath(self):
        return os.path.join(self.folder, "judgment.json")

    def run(self):
        env = dict(os.environ, STOCKS_BASE=self.base, PYTHONIOENCODING="utf-8", MAKE_SCORE_REGISTRY=self.registry)
        r = subprocess.run([sys.executable, MAKE_SCORE, T], capture_output=True, text=True, encoding="utf-8",
                           env=env, timeout=120)
        self.rc, self.out, self.err = r.returncode, r.stdout, r.stderr
        return self

    def ok(self):
        assert self.rc == 0, f"make_score refused: {self.err}"
        return self

    def refused(self, *needles):
        assert self.rc == 1, f"expected a refusal, got rc {self.rc}: {self.out} {self.err}"
        assert "REFUSED" in self.err, self.err
        for s in needles:
            assert s in self.err, f"{s!r} not in: {self.err}"
        st = getattr(self, "result", None) or self.state()
        assert not st["key_exists"], "a refusal wrote key_numbers.md"
        assert st["score_exists"] == self.had_prior, "a refusal wrote score.json"
        return self

    def state(self):
        return {"key_exists": os.path.exists(os.path.join(self.folder, "key_numbers.md")),
                "score_exists": os.path.exists(os.path.join(self.folder, "score.json"))}

    def score(self):
        with open(os.path.join(self.folder, "score.json"), encoding="utf-8") as f:
            return json.load(f)

    def key(self):
        with open(os.path.join(self.folder, "key_numbers.md"), encoding="utf-8") as f:
            return f.read()

    def judgment_text(self):
        with open(self.jpath, encoding="utf-8", newline="") as f:
            return f.read()

    def entries(self, event=None):
        try:
            with open(self.registry, encoding="utf-8") as f:
                reg = json.load(f)
        except OSError:
            return []
        return [e for e in reg.get("entries", []) if event is None or e.get("event") == event]

    def spawned(self):
        return sorted(x for x in os.listdir(self.sysdir) if x.startswith("SPAWNED_"))

    def close(self):
        shutil.rmtree(self.base, ignore_errors=True)


def _with(n, j=None, **kw):
    """Run make_score once on a fresh folder; returns the closed Run with its outputs read."""
    r = Run(n, j, **kw).run()
    try:
        r.result = dict(r.state(), score=r.score() if r.rc == 0 else None, key=r.key() if r.rc == 0 else None,
                        judgment=r.judgment_text(), entries=r.entries(), spawned=r.spawned())
    finally:
        r.close()
    return r


# ---------------------------------------------------------------- unit
def test_release_helpers():
    assert M.release_tuple("5.4.0") == (5, 4, 0) and M.release_tuple("5.5") == (5, 5, 0)
    assert M.release_tuple("5.10.2") == (5, 10, 2) and M.release_tuple(None) is None and M.release_tuple("x") is None
    assert M.predates_55({}) and M.predates_55({"engine_release": "5.4.0"}) and M.predates_55({"engine_release": "5.4"})
    assert not M.predates_55({"engine_release": "5.5.0"}) and not M.predates_55({"engine_release": "5.10.0"})
    # a record carrying the engine's market_cap_basis is 5.5 output whatever its stamp: never corrected twice
    assert not M.predates_55({"engine_release": "5.4.0", "market_cap_basis": {"shares_source": "diluted_latest"}})
    assert M.release_mismatch_reason(None) == PREDATES and M.release_mismatch_reason("5.3.1") == PREDATES
    assert M.release_mismatch_reason("9.0.0") == f"engine output is from release 9.0.0, not the current release {CUR}"
    # the one formula: make_score's market cap is the engine's helper (an alias, never a local copy)
    import dcf_engine as _E
    assert M.market_cap_estimate is _E.market_cap_est
    assert M.market_cap_estimate(20.0, 1e9, 2.0) == (20.0 * 1e9) / 2.0 and M.market_cap_estimate(20.0, 1e9, None) == 20e9
    assert M.market_cap_estimate(None, 1e9, 2.0) is None and M.market_cap_estimate(20.0, 0, 2.0) is None
    assert M.ads_cap_correction(_ads(2.0, 20.0)) == {"cap": 10e9, "old_cap": 20e9, "ratio": 2.0}
    assert M.ads_cap_correction(_ads(2.0, 20.0, release="5.4.0")) == {"cap": 10e9, "old_cap": 20e9, "ratio": 2.0}
    assert M.ads_cap_correction(_numbers(release=None)) is None  # no ratio
    assert M.ads_cap_correction(_ads(2.0, 20.0, release="5.5.0")) is None  # 5.5 already divides
    assert M.ads_cap_correction(dict(_ads(2.0, 20.0), price=None)) is None  # the engine's universe fallback cap


def test_scope_decision():
    corr = {"cap": 25e9, "old_cap": 50e9, "ratio": 2.0}
    assert M.scope_decision(False, 25e9, corr) == (True, True, True)    # judgment followed the old cap → rewrite
    assert M.scope_decision(True, 25e9, corr) == (True, None, True)     # already corrected (a re-run) → idempotent
    assert M.scope_decision(True, 30e9, None) == (True, None, False)    # no correction: plain scope
    assert M.scope_decision(True, 60e9, {"cap": 60e9, "old_cap": 30e9, "ratio": 0.5}) == (False, False, True)
    # no flip: nothing to rewrite, and a contradiction is left to main() to refuse
    assert M.scope_decision(True, 50e9, {"cap": 50e9, "old_cap": 100e9, "ratio": 2.0}) == (False, None, False)
    assert M.scope_decision(True, None, corr) == (None, None, False)


def test_rewrite_judgment_scope_keeps_the_file_format():
    tmp = tempfile.mkdtemp(prefix="scope_rw_")
    try:
        p = os.path.join(tmp, "judgment.json")
        cases = [
            '{"ads_ratio":{"ratio":2.0},"one_liner":"Résumé → margins","in_scope_under_40b":false,"x":1}',     # compact, raw UTF-8
            '{\n "one_liner": "R\\u00e9sum\\u00e9",\n "in_scope_under_40b": false,\n "x": 1\n}\n',               # indented, escaped
            '{\r\n "in_scope_under_40b" : false\r\n}\r\n',                                                      # CRLF
        ]
        for text in cases:
            with open(p, "w", encoding="utf-8", newline="") as f:
                f.write(text)
            M.rewrite_judgment_scope(p, True)
            with open(p, encoding="utf-8", newline="") as f:
                got = f.read()
            assert got == text.replace("false", "true"), (text, got)
        # the token also appears inside a string: re-dumped in the file's style, still only that field changed
        text = '{\n "note": "was \\"in_scope_under_40b\\": false before",\n "in_scope_under_40b": false,\n "s": {"in_scope_under_40b": false}\n}\n'
        with open(p, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        M.rewrite_judgment_scope(p, True)
        with open(p, encoding="utf-8", newline="") as f:
            got = json.loads(f.read())
        assert got == dict(json.loads(text), in_scope_under_40b=True), got
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_alert_reasons_stale_release():
    R = M.alert_reasons
    entry, exit_ = R("A", "A", None, "medium", "modeled", False, False, stale_release=PREDATES)
    assert entry == [f"{PREDATES} — re-run the engine before an entry alert"] and exit_ == []
    entry, exit_ = R("B", "B", None, "medium", "modeled", False, False, stale_release=PREDATES)
    assert entry == [] and exit_ == [f"{PREDATES} — re-run the engine before an exit alert"]
    # appended to (never replacing) the 5.4 reasons; None keeps 5.4 exactly
    entry, _ = R("A", "B", "A", "medium", "misfit", True, True, stale_release=PREDATES)
    assert entry[0].startswith(PREDATES) and len(entry) == 5
    assert R("A", "A", None, "low", "modeled", False, False, stale_release=None) == ([], [])


def test_carried_override_impact_unit():
    n = _numbers(release="5.4.0", data_gap=["sbc"], data_gap_uncovered=[])
    prior = {"override_impact": {"base_used": "median_3y", "base_oe_without_override": 2.9, "base_oe_with_override": 3.0,
                                 "base_oe_impact_pct": 3.448, "weighted_irr_without_override": 0.165,
                                 "weighted_irr_with_override": 0.17, "weighted_irr_impact_pp": 0.5, "unblocks_tier": False}}
    got = M.carried_override_impact(n, prior)
    assert got == dict(prior["override_impact"], unblocks_tier=True, impact_carried_from_prior_score=True,
                       counterfactual_engine_release="5.4.0"), got
    # measured on another run's base (with-override base differs): not carried
    other = copy.deepcopy(prior)
    other["override_impact"]["base_oe_with_override"] = 2.5
    for p in (other, None, {}, {"override_impact": None}):
        got = M.carried_override_impact(n, p)
        assert got["base_oe_without_override"] is None and got["base_oe_impact_pct"] is None
        assert got["weighted_irr_without_override"] is None and got["weighted_irr_impact_pp"] is None
        assert got["base_oe_with_override"] == 3.0 and got["weighted_irr_with_override"] == 0.17
        assert got["unblocks_tier"] is True and got["base_used"] == "median_3y"
        assert got["note"] == f"not measured: engine output predates release {CUR}; re-run the engine to measure", got
        assert "impact_carried_from_prior_score" not in got


# ---------------------------------------------------------------- 1. pre-5.5 ADS market cap
def test_pre55_ads_market_cap_corrected():
    # (ratio, price, old cap printed, corrected cap printed, market_cap_b, engine nd ratio, corrected nd line tail)
    cases = [(100, 20.0, "$20.000B", "$200.0M", 0.2, -0.03, "BIG_NET_CASH (< -2x) would fire on the ADS basis"),
             (2.0, 20.0, "$20.000B", "$10.000B", 10.0, 1.6, "HIGH_NET_DEBT (> 3x) would fire on the ADS basis"),
             (0.5, 15.0, "$15.000B", "$30.000B", 30.0, 7.0, None)]
    for release in STALE:
        for ratio, price, old_s, new_s, cap_b, nd, nd_tail in cases:
            n = _ads(ratio, price, release=release,
                     diagnostics={"oe_yield": 0.15, "net_debt_to_normalized_oe": nd, "months_since_fy_end": 9.5})
            r = _with(n)
            assert r.rc == 0, (release, ratio, r.err)
            s, key = r.result["score"], r.result["key"]
            assert s["market_cap_b"] == cap_b, (ratio, s["market_cap_b"])
            assert s["market_cap_basis"] == "ads_corrected_by_make_score" and s["in_scope_under_40b"] is True
            assert "in_scope_corrected_by_make_score" not in s
            assert not [e for e in r.result["entries"] if e.get("event") == "scope_correction"]
            assert (f"- Market cap (est): {new_s} (ADS-corrected by make_score: price × shares ÷ ratio; "
                    f"the pre-5.5 engine printed {old_s}) · net debt (latest): $1.000B") in key, key
            ndc = nd * ratio
            assert (f"- Net debt / normalized OE: {ndc:.2f}x on the ADS basis (make_score: the pre-5.5 engine's ratio × "
                    f"ads_ratio {ratio:g} — it divided net debt by per-ADS OE × ORDINARY shares; the engine printed {nd:.2f}x") in key, key
            assert (nd_tail in key) if nd_tail else ("would fire" not in key and "would no longer fire" not in key), key
            assert s["net_debt_to_normalized_oe_ads_basis"] == round(ndc, 4), s  # M1: recorded in score.json too
            assert "- Scope: in scope (market cap under $40B)" in key
            assert r.result["spawned"] == []
    # ratio 0.5 the other way: HIGH_NET_DEBT fired on the engine's ratio and would no longer on the ADS basis
    n = _ads(0.5, 15.0, diagnostics={"net_debt_to_normalized_oe": 5.0})
    assert "HIGH_NET_DEBT (> 3x) would no longer fire on the ADS basis" in _with(n).result["key"]
    # pre-5.5 without an ADS ratio: unchanged cap, basis named
    r = _with(_numbers(release="5.3.1"))
    assert r.rc == 0, r.err
    s, key = r.result["score"], r.result["key"]
    assert s["market_cap_b"] == 20.0 and s["market_cap_basis"] == "diluted_latest"
    assert "- Market cap (est): $20.000B (basis: diluted_latest) · net debt (latest): $1.000B" in key
    assert "- Net debt / normalized OE: 0.33x\n" in key and "net_debt_to_normalized_oe_ads_basis" not in s
    # pre-5.5 cap from the universe fallback (no price × shares): named, never "corrected"
    r = _with(_ads(2.0, 20.0, shares_diluted_latest=None, market_cap_est=7e9))
    assert r.rc == 0, r.err
    assert r.result["score"]["market_cap_b"] == 7.0 and r.result["score"]["market_cap_basis"] == "universe_market_cap"


# ---------------------------------------------------------------- 2. scope rewrite
def test_scope_rewrite_when_the_old_cap_explains_judgment():
    n = _ads(2.0, 50.0)  # old cap $50B (out of scope), corrected $25B (in scope)
    j = _judgment(n, in_scope_under_40b=False)
    compact = json.dumps(j, separators=(",", ":"), ensure_ascii=False)  # JD-style file: compact, raw UTF-8, no newline
    r = Run(n, judgment_text=compact).run()
    try:
        r.ok()
        assert r.judgment_text() == compact.replace('"in_scope_under_40b":false', '"in_scope_under_40b":true')
        s = r.score()
        assert s["in_scope_under_40b"] is True and s["in_scope_corrected_by_make_score"] is True
        assert s["market_cap_b"] == 25.0 and s["market_cap_basis"] == "ads_corrected_by_make_score"
        ev = r.entries("scope_correction")
        assert len(ev) == 1 and ev[0]["ticker"] == T and ev[0]["old_cap"] == 50e9 and ev[0]["new_cap"] == 25e9
        assert ev[0]["in_scope"] is True and ev[0]["date"]
        assert "judgment.json in_scope_under_40b False -> True" in r.out and "$25.000B" in r.out and "$50.000B" in r.out
        assert "- Scope: in scope (market cap under $40B) — corrected by make_score from the ADS-corrected market cap" in r.key()
        # a re-run of the same engine output: nothing rewritten, the record and the event stay
        before = r.judgment_text()
        r.run().ok()
        assert r.judgment_text() == before and "->" not in r.out
        assert r.score()["in_scope_corrected_by_make_score"] is True and len(r.entries("scope_correction")) == 1
    finally:
        r.close()
    # an indented, \u-escaped judgment.json keeps its format too (one token changes)
    text = json.dumps(j, indent=1) + "\n"
    r = Run(n, judgment_text=text).run()
    try:
        r.ok()
        assert r.judgment_text() == text.replace('"in_scope_under_40b": false', '"in_scope_under_40b": true')
    finally:
        r.close()
    # the reverse (ratio 0.5): old $30B in scope, corrected $60B out → rewritten false
    n = _ads(0.5, 30.0)
    r = _with(n, _judgment(n, in_scope_under_40b=True))
    assert r.rc == 0, r.err
    assert json.loads(r.result["judgment"])["in_scope_under_40b"] is False
    assert r.result["score"]["in_scope_under_40b"] is False and r.result["score"]["in_scope_corrected_by_make_score"] is True
    assert [e["in_scope"] for e in r.result["entries"] if e.get("event") == "scope_correction"] == [False]


def test_scope_disagreement_the_old_cap_does_not_explain_still_refuses():
    for ratio, price in ((0.5, 50.0), (2.0, 100.0)):  # $50B → $100B and $100B → $50B: out of scope either way
        n = _ads(ratio, price)
        j = _judgment(n, in_scope_under_40b=True)
        text = json.dumps(j, indent=1) + "\n"
        r = _with(n, judgment_text=text)
        r.refused("contradicts the ADS-corrected market cap", "does not explain it either")
        assert r.result["judgment"] == text and r.result["entries"] == []
    # a 5.5 run: the engine's cap is already right, so make_score never rewrites
    n = _numbers(engine_release=CUR, filer_annual_form="20-F", price=50.0, shares_diluted_latest=1e9,
                 market_cap_est=25e9, ads_ratio={"ratio": 2.0, "source": "s", "reason": "r"},
                 market_cap_basis={"shares_used": 1e9, "shares_source": "diluted_latest", "ads_ratio": 2.0,
                                   "formula": "price × shares ÷ ads_ratio"})
    r = _with(n, _judgment(n, in_scope_under_40b=False))
    r.refused("contradicts the engine's market cap ($25.000B)")
    assert json.loads(r.result["judgment"])["in_scope_under_40b"] is False


# ---------------------------------------------------------------- 3. release mismatch: impact carried, nothing spawned
def _override_run(release, prior=None, base=3.0):
    n = _numbers(release=release, base_oe_per_share=base, data_gap=["sbc"], data_gap_uncovered=[],
                 overrides_applied=[{"field": "sbc", "value": 1e6, "kind": "filing", "source": "Form 10-K FY2025 cash-flow statement",
                                     "reason": "untagged", "periods_filled": ["2025-12-31"]}])
    j = _judgment(n, sbc_override={"value": 1e6, "kind": "filing", "source": "Form 10-K FY2025 cash-flow statement",
                                   "reason": "SBC printed on the cash-flow statement, untagged in companyfacts"})
    return _with(n, j, prior_score=prior)


PRIOR_IMPACT = {"base_used": "median_3y", "base_oe_without_override": 2.95, "base_oe_with_override": 3.0,
                "base_oe_impact_pct": 1.695, "weighted_irr_without_override": 0.168, "weighted_irr_with_override": 0.17,
                "weighted_irr_impact_pp": 0.2, "unblocks_tier": True}


def test_release_mismatch_carries_the_prior_impact_without_a_counterfactual():
    for release in STALE:
        r = _override_run(release, prior={"ticker": T, "override_impact": dict(PRIOR_IMPACT)})
        assert r.rc == 0, (release, r.err)
        assert r.result["spawned"] == [], f"a counterfactual was spawned: {r.result['spawned']}"
        imp = r.result["score"]["override_impact"]
        assert imp == dict(PRIOR_IMPACT, impact_carried_from_prior_score=True, counterfactual_engine_release=release), imp
        e = [x for x in r.result["entries"] if x.get("field") == "sbc"]
        assert len(e) == 1 and e[0]["base_oe_without_override"] == 2.95 and e[0]["unblocks_tier"] is True
        assert "carried from the prior score.json, not re-measured" in r.result["key"]
        # the override fills a gap (unblocks) and the release is stale: the exit gate names both
        assert "re-run the engine before an exit alert" in r.result["score"]["exit_alert_suppressed_reason"]


def test_release_mismatch_without_a_prior_measurement_records_nulls():
    other = dict(PRIOR_IMPACT, base_oe_with_override=2.5)  # measured on another run's base: not carried
    for prior in (None, {"ticker": T}, {"ticker": T, "override_impact": other}):
        r = _override_run(STALE[-1], prior=prior)
        assert r.rc == 0, r.err
        assert r.result["spawned"] == []
        imp = r.result["score"]["override_impact"]
        assert imp == {"base_used": "median_3y", "base_oe_without_override": None, "base_oe_with_override": 3.0,
                       "base_oe_impact_pct": None, "weighted_irr_without_override": None,
                       "weighted_irr_with_override": 0.17, "weighted_irr_impact_pp": None, "unblocks_tier": True,
                       "counterfactual_engine_release": STALE[-1],
                       "note": f"not measured: engine output predates release {CUR}; re-run the engine to measure"}, imp
        assert f"- Impact not measured: engine output predates release {CUR}; re-run the engine to measure" in r.result["key"]


def test_current_release_still_measures_the_counterfactual():
    """Control: on current-release output make_score spawns the engine's --measure
    run as before — here the fail-loud stand-in, so it refuses and leaves its marker."""
    r = _override_run(CUR, prior={"ticker": T, "override_impact": dict(PRIOR_IMPACT)})
    r.refused("counterfactual engine --measure run failed")
    assert r.result["spawned"] == ["SPAWNED_dcf_engine.py.txt"], r.result["spawned"]


# ---------------------------------------------------------------- 4. stale-release alert suppression
def test_stale_release_closes_both_alert_gates():
    for release in STALE:
        s = _with(_numbers(release=release, tier_by_numbers="A", implied_irr_weighted=0.22)).result["score"]
        assert s["tier_final"] == "A" and s["alert_eligible"] is False and s["exit_alert_eligible"] is False, s
        assert s["alert_suppressed_reason"] == f"{PREDATES} — re-run the engine before an entry alert", s
        assert "exit_alert_suppressed_reason" not in s
        s = _with(_numbers(release=release)).result["score"]  # Tier B: an exit would alert on a current run
        assert s["exit_alert_eligible"] is False and s["alert_eligible"] is False
        assert s["exit_alert_suppressed_reason"] == f"{PREDATES} — re-run the engine before an exit alert", s
    # a release newer than this make_score's: also closed, with its own wording
    s = _with(_numbers(release="9.0.0", tier_by_numbers="A", implied_irr_weighted=0.22)).result["score"]
    assert s["alert_eligible"] is False
    assert s["alert_suppressed_reason"].startswith(f"engine output is from release 9.0.0, not the current release {CUR}")
    # the current release keeps today's gates
    s = _with(_numbers(release=CUR, tier_by_numbers="A", implied_irr_weighted=0.22)).result["score"]
    assert s["alert_eligible"] is True and s["exit_alert_eligible"] is False
    assert "alert_suppressed_reason" not in s and "exit_alert_suppressed_reason" not in s
    s = _with(_numbers(release=CUR)).result["score"]
    assert s["exit_alert_eligible"] is True and "exit_alert_suppressed_reason" not in s


# ---------------------------------------------------------------- 5. override currency
def _sbc(**kw):
    o = {"value": 2e6, "kind": "filing", "source": "Form 20-F FY2025 cash-flow statement", "reason": "stated in USD"}
    o.update(kw)
    return o


def test_override_currency_validation():
    n = _numbers()  # the override is declared but nothing needed it: no gap, not applied, no counterfactual
    for cur in ("USD", "usd", " USD "):
        r = _with(n, _judgment(n, sbc_override=_sbc(currency=cur)))
        assert r.rc == 0, (cur, r.err)
    assert _with(n, _judgment(n, sbc_override=_sbc(currency=None))).rc == 0  # null = absent
    _with(n, _judgment(n, sbc_override=_sbc(kind="estimate", currency="USD"))).refused(
        'sbc_override.currency "USD" requires kind "filing"')
    for bad in ("EUR", "US$", 840, True):
        _with(n, _judgment(n, sbc_override=_sbc(currency=bad))).refused("sbc_override.currency", "is not allowed")
    _with(n, _judgment(n, capex_override=_sbc(currency="CNY"))).refused("capex_override.currency 'CNY' is not allowed")


def test_usd_declaration_the_run_converted_refuses():
    applied = [{"field": "sbc", "value": 2e6, "kind": "filing", "source": "s", "reason": "r", "periods_filled": ["2025-12-31"]}]
    fx = {"from_currency": "EUR", "rates": {"2025-12-31": 1.1}}
    # pre-5.5 engine: it converted every override at a converted filer
    n = _numbers(release=STALE[-1], data_gap=["sbc"], data_gap_uncovered=[], overrides_applied=applied, fx_conversion=fx)
    _with(n, _judgment(n, sbc_override=_sbc(currency="USD"))).refused("declares currency \"USD\" but the engine run FX-converted it")
    # 5.5 engine recording currency_basis "converted" for it: out of sync, refused before any counterfactual
    n = _numbers(release=CUR, data_gap=["sbc"], data_gap_uncovered=[], overrides_applied=applied, fx_conversion=fx,
                 override_checks={"sbc": {"currency_basis": "converted", "out_of_band": False}})
    r = _with(n, _judgment(n, sbc_override=_sbc(currency="USD")))
    r.refused("FX-converted")
    assert r.result["spawned"] == []
    # the same pre-5.5 run without the declaration is not this check's business (carried impact, scored)
    n = _numbers(release=STALE[-1], data_gap=["sbc"], data_gap_uncovered=[], overrides_applied=applied, fx_conversion=fx)
    assert _with(n, _judgment(n, sbc_override=_sbc())).rc == 0


# ---------------------------------------------------------------- 6. share_class_mismatch
def test_share_class_mismatch_refuses_every_declaration():
    n = _numbers()
    full = {"value": True, "source": "Form 20-F 2025 Item 9: the ADS represents Class B shares", "reason": "EPS is per Class A"}
    for decl, extra in ((True, "no source given"), (full, "Form 20-F 2025 Item 9"), ({"value": True}, "no source given"),
                        ({"value": True, "reason": "r"}, "lacks a source"), ({"source": "s"}, "lacks a source and/or reason")):
        r = _with(n, _judgment(n, share_class_mismatch=decl))
        r.refused("DATA_GAP:shares — SHARE_CLASS_MISMATCH", "NEEDS_MAIN_AGENT", extra)  # nothing written
    # the engine's rule: false, null, an object whose value is false, or an empty object declare nothing
    for falsy in (False, None, {}, {"value": False, "source": "s", "reason": "checked: same class"}):
        assert _with(n, _judgment(n, share_class_mismatch=falsy)).rc == 0, falsy
    # a 5.5 run that turned the declaration into its share_class gap: the refusal names the declaration
    n = _numbers(data_gap=["share_class"], data_gap_uncovered=["share_class"], tier_by_numbers=None)
    _with(n, _judgment(n, share_class_mismatch=True)).refused("SHARE_CLASS_MISMATCH")


# ---------------------------------------------------------------- 7. 5.5 market_cap_basis passes through
def test_55_record_market_cap_basis_passes_through():
    for release in ("5.5.0", CUR):
        mb = {"shares_used": 2e9, "shares_source": "diluted_latest_split_adjusted", "ads_ratio": 2.0,
              "formula": "price × shares ÷ ads_ratio"}
        n = _numbers(release=release, filer_annual_form="20-F", price=20.0, shares_diluted_latest=2e9,
                     market_cap_est=20e9, ads_ratio={"ratio": 2.0, "source": "s", "reason": "r"}, market_cap_basis=mb)
        r = _with(n)
        assert r.rc == 0, r.err
        s, key = r.result["score"], r.result["key"]
        assert s["market_cap_b"] == 20.0 and s["market_cap_basis"] == "diluted_latest_split_adjusted", s  # not ÷ 2 again
        assert "in_scope_corrected_by_make_score" not in s
        assert "- Market cap (est): $20.000B (basis: diluted_latest_split_adjusted; price × shares ÷ ads_ratio)" in key, key
        assert "ADS-corrected by make_score" not in key
    # the engine's universe.csv fallback cap (no price or shares) is named as such, whatever shares_source says
    n = _numbers(release=CUR, shares_diluted_latest=None, market_cap_est=7e9,
                 market_cap_basis={"shares_used": None, "shares_source": "diluted_latest", "ads_ratio": None,
                                   "formula": "universe.csv market_cap (no price or no share count)"})
    s = _with(n).result["score"]
    assert s["market_cap_b"] == 7.0 and s["market_cap_basis"] == "universe_market_cap", s
    # ... and the record shape engine 5.5 actually writes there (no share count used)
    n = _numbers(release=CUR, shares_diluted_latest=None, market_cap_est=7e9,
                 market_cap_basis={"shares_used": None, "shares_source": "universe_market_cap", "ads_ratio": None,
                                   "formula": "universe.csv market_cap (no price or no share count)"})
    s = _with(n).result["score"]
    assert s["market_cap_b"] == 7.0 and s["market_cap_basis"] == "universe_market_cap", s
    # a 5.5 stamp without the record: nothing corrected, basis unknown
    n = _ads(2.0, 20.0, release="5.5.0")
    s = _with(n).result["score"]
    assert s["market_cap_b"] == 20.0 and s["market_cap_basis"] is None


# ---------------------------------------------------------------- 8. key_numbers provenance lines
def _csv_row(pe, capex, src, tag, ppe, intang):
    return {"period_end": pe, "fy_label": pe[:4], "ocf": 5e8, "capex": capex, "capex_tag": tag, "sbc": 1e7,
            "shares_diluted": 1e9, "capex_ppe": ppe, "capex_intangibles": intang, "capex_source": src, "shares_split_factor": ""}


def test_key_numbers_capex_share_and_sbc_lines():
    prov = {pe: {"ppe_source": "rollup", "ppe": {"PaymentsToAcquirePropertyPlantAndEquipment": 9e7}, "ppe_unit": "USD",
                 "intangibles": {"PaymentsToAcquireIntangibleAssets": 1e7}, "intangibles_unit": "USD", "dropped": [],
                 "filed": {}} for pe in ("2022-12-31", "2023-12-31", "2024-12-31", "2025-12-31")}
    prov["2025-12-31"] = {"ppe_source": "components_mixed_filings",
                          "ppe": {"PaymentsToExploreAndDevelopOilAndGasProperties": 9.0e8, "PaymentsToAcquireOilAndGasProperty": 4.4e7},
                          "ppe_unit": "USD", "intangibles": {}, "intangibles_unit": None, "dropped": [], "filed": {}}
    sbc = {"2024-12-31": {"share": [3.4e6, "USD"], "allocated": [7.49e7, "USD"], "used": "AllocatedShareBasedCompensationExpense",
                          "reconciled": True, "note": None},
           "2025-12-31": {"share": [6.77e7, "USD"], "allocated": [6.77e7, "USD"], "used": "ShareBasedCompensation",
                          "reconciled": False, "note": None}}
    n = _numbers(capex_provenance=prov, sbc_provenance=sbc,
                 share_basis={"split": {"event_date": "2026-06-30", "ratio_filed": 0.333, "ratio_used": 1 / 3,
                                        "dei_count": 135042975}, "divergence": None, "unconfirmed_split_facts": []},
                 share_scale={"defect": True, "tests": {"a": True, "b": False}, "reasons": ["base OE/share 61x the price"],
                              "dei_count": None, "scale_factor": 1000, "factor_basis": "pin", "rescued_by_pin": True})
    rows = [_csv_row("2022-12-31", 1e8, "rollup", "PaymentsToAcquirePropertyPlantAndEquipment+PaymentsToAcquireIntangibleAssets", 9e7, 1e7),
            _csv_row("2023-12-31", 1e8, "rollup", "PaymentsToAcquirePropertyPlantAndEquipment+PaymentsToAcquireIntangibleAssets", 9e7, 1e7),
            _csv_row("2024-12-31", 4e7, "override", "OVERRIDE", 4e7, 0),
            _csv_row("2025-12-31", 9.44e8, "components_mixed_filings",
                     "PaymentsToExploreAndDevelopOilAndGasProperties+PaymentsToAcquireOilAndGasProperty", 9.44e8, 0)]
    key = _with(n, csv_rows=rows).result["key"]
    assert ("- Capex basis FY2023 (2023-12-31): $100.0M — rollup: PaymentsToAcquirePropertyPlantAndEquipment+"
            "PaymentsToAcquireIntangibleAssets (PP&E $90.0M + intangibles $10.0M)") in key, key
    assert "- Capex basis FY2024 (2024-12-31): $40.0M — override: OVERRIDE (PP&E $40.0M + intangibles $0.00)" in key
    assert ("- Capex basis FY2025 (2025-12-31): $944.0M — components_mixed_filings: PaymentsToExploreAndDevelopOilAndGasProperties+"
            "PaymentsToAcquireOilAndGasProperty (PP&E $944.0M + intangibles $0.00)") in key
    assert "FY2022" not in key.split("## Growth")[0].split("Capex basis", 1)[1], "last 3 FY only"
    assert "- Share basis: split adjustment applied — event_date=2026-06-30, ratio_filed=0.333, ratio_used=0.333333, dei_count=135,042,975" in key, key
    assert "- Share basis: share-scale defect — reasons=base OE/share 61x the price, scale_factor=1,000, factor_basis=pin, rescued_by_pin=True" in key, key
    assert "cover-page divergence" not in key
    assert ("- SBC reconciled FY2024 (2024-12-31): AllocatedShareBasedCompensationExpense $74.9M used over "
            "ShareBasedCompensation $3.4M (+2102.9%)") in key, key
    assert "SBC reconciled FY2025" not in key
    # no CSV columns (or no CSV): the lines come from capex_provenance itself
    key = _with(n).result["key"]
    assert ("- Capex basis FY2025 (2025-12-31): components_mixed_filings: PaymentsToExploreAndDevelopOilAndGasProperties $900.0M"
            " + PaymentsToAcquireOilAndGasProperty $44.0M") in key, key
    assert "- Capex basis FY2023 (2023-12-31): rollup: PaymentsToAcquirePropertyPlantAndEquipment $90.0M + PaymentsToAcquireIntangibleAssets $10.0M" in key
    # a divergence record prints; a run without any 5.5 record prints none of these lines
    n2 = _numbers(share_basis={"split": None, "divergence": {"dei_count": 135e6, "dei_date": "2026-07-31", "ratio": 0.32},
                               "unconfirmed_split_facts": []})
    assert "- Share basis: cover-page divergence — dei_count=135,000,000, dei_date=2026-07-31, ratio=0.32" in _with(n2).result["key"]
    key = _with(_numbers(), csv_rows=rows).result["key"]
    assert "Capex basis" not in key and "Share basis" not in key and "SBC reconciled" not in key


# ---------------------------------------------------------------- 9. [ADDITION — WY] superseded capex override
WY_CAPEX_OV = {"value": 447000000, "kind": "filing",
               "source": "Form 10-K FY2025, Consolidated Statements of Cash Flows: capital expenditures $423M + timberlands "
                         "reforestation $51M (FY2025), combined totals $474M / $416M / $447M",
               "reason": "DATA_GAP:capex — the total is tagged PropertyPlantAndEquipmentAdditions, which no engine list reads"}
WY_SUPERSEDED = [{"period": f"{y}-12-31", "override": 447000000.0, "filed_ppe": v, "filed_unit": "USD",
                  "filed_tags": "PaymentsForCapitalImprovements"}
                 for y, v in ((2023, 57000000), (2024, 52000000), (2025, 51000000))]
WY_FLAGS = ["OVERRIDE_SUPERSEDED_BY_FILED_TAG:capex — judgment.json capex_override 447,000,000 is outside 0.5x-2x of the PP&E "
            "capex now FILED for FY2023 (57,000,000 USD, PaymentsForCapitalImprovements), FY2024 (52,000,000 USD, "
            "PaymentsForCapitalImprovements), FY2025 (51,000,000 USD, PaymentsForCapitalImprovements); the filed value is used "
            "there (an override never replaces a filed value), so the override fills nothing — reconcile it against the "
            "cash-flow statement and remove it or justify it in analysis.md",
            "CAPEX_COVERAGE_LOW: capex is below 50% of D&A in each of the last 3 fiscal years (FY2023 11%, FY2024 10%, "
            "FY2025 10%) at a filer with positive PP&E — reconcile total capex against the cash-flow statement's investing "
            "section (construction in progress, capitalised software, land-use rights, spectrum, intangible purchases) before "
            "trusting the owner's-earnings base"]
WY_NEEDLES = ("OVERRIDE_SUPERSEDED_BY_FILED_TAG:capex", "still declares capex_override 447,000,000",
              "FY2023 57,000,000 USD (PaymentsForCapitalImprovements)", "FY2025 51,000,000 USD (PaymentsForCapitalImprovements)",
              "remove capex_override from judgment.json", "NEEDS_MAIN_AGENT: capex")


def _wy(applied=True, flags=True, superseded=True, coverage=True):
    """A 5.5 WY-shaped record: capital improvements now filed beneath the $447M total-capex override in FY2023-25
    (the override still fills FY2019-22 when `applied`)."""
    kw = {"fragility_flags": [f for f in WY_FLAGS if (flags or not f.startswith("OVERRIDE_SUPERSEDED"))
                              and (coverage or not f.startswith("CAPEX_COVERAGE_LOW"))],
          "override_checks": {"capex": dict({"value": 447000000.0, "last_filed_value": 368000000, "last_filed_unit": "USD",
                                             "out_of_band": False, "ack_reason_present": False, "currency_basis": "no_fx"},
                                            **({"superseded_periods": WY_SUPERSEDED} if superseded else {}))}}
    if applied:
        kw["overrides_applied"] = [dict(WY_CAPEX_OV, field="capex",
                                        periods_filled=["2019-12-31", "2020-12-31", "2021-12-31", "2022-12-31"])]
    return _numbers(tier_by_numbers="D", implied_irr_weighted=0.06, **kw)


def test_superseded_capex_override_refuses_while_declared():
    """[ADDITION — WY] OVERRIDE_SUPERSEDED_BY_FILED_TAG:capex beside a capex_override still in judgment.json refuses
    — whether the override still fills history years (applied) or fills nothing at all — naming the filed periods
    and both resolutions (remove the override / block NEEDS_MAIN_AGENT: capex), before any counterfactual replay."""
    for applied in (True, False):
        n = _wy(applied=applied)
        r = _with(n, _judgment(n, capex_override=dict(WY_CAPEX_OV))).refused(*WY_NEEDLES)
        assert "CAPEX_COVERAGE_LOW also fires on this run" in r.err, r.err
        assert r.result["spawned"] == [], f"refusal came after a counterfactual: {r.result['spawned']}"
    # the record of superseded periods alone (no flag text) is the same signal
    n = _wy(applied=False, flags=False)
    _with(n, _judgment(n, capex_override=dict(WY_CAPEX_OV))).refused(*WY_NEEDLES)
    # the flag alone (no period record): still refused, the coverage note only when that flag fires
    n = _wy(applied=False, superseded=False, coverage=False)
    r = _with(n, _judgment(n, capex_override=dict(WY_CAPEX_OV))).refused(
        "OVERRIDE_SUPERSEDED_BY_FILED_TAG:capex", "the flag names them", "NEEDS_MAIN_AGENT: capex")
    assert "CAPEX_COVERAGE_LOW also fires" not in r.err


def test_superseded_flag_without_a_declared_override_scores():
    """[ADDITION — WY] controls: the override removed from judgment.json (resolution (i), nothing applied) scores —
    the flag is left for analysis.md; a capex_override with no superseded period is untouched by the check."""
    n = _wy(applied=False)
    r = _with(n, _judgment(n))
    assert r.rc == 0, r.err
    n = _numbers()  # declared, not needed (no gap, not applied), nothing superseded
    assert _with(n, _judgment(n, capex_override=dict(WY_CAPEX_OV))).rc == 0


# ---------------------------------------------------------------- 10. [ADDITION — HTHT] last-filed-unit USD fallback
HTHT_CAPEX_OV = {"value": 828000000, "kind": "filing",
                 "source": "Form 20-F FY2025, Consolidated Statements of Cash Flows, 'Purchases of property and equipment': "
                           "RMB828M (US$119M in the convenience-translation column)",
                 "reason": "DATA_GAP:capex — the cash-flow line is not carried under any engine-read tag"}
PUK_SBC_OV = {"value": 85000000, "kind": "filing",
              "source": "Prudential plc Annual Report 2024 (Form 20-F), note B2.2(d): $85 million; reports in US dollars",
              "reason": "DATA_GAP:sbc — no ifrs-full SBC tag filed for FY2020-25"}


def _verbatim_run(field, o, ccy, basis="last_filed_unit_usd", release=CUR, applied=True):
    """A run whose `field` override the engine recorded under currency_basis `basis` at a filer converted from `ccy`."""
    kw = {"data_gap": [field] if applied else [], "data_gap_uncovered": [],
          "fx_conversion": {"from_currency": ccy, "to_currency": "USD", "rates": {"2025-12-31": 0.14},
                            "converted_fields": ["revenue", "ocf"],
                            "overrides_usd_verbatim": {field: basis} if basis in ("declared_usd", "last_filed_unit_usd") else {}}}
    if basis is not None:
        kw["override_checks"] = {field: {"value": float(o["value"]), "last_filed_value": 160198000, "last_filed_unit": "USD",
                                         "out_of_band": False, "ack_reason_present": False, "currency_basis": basis}}
    if applied:
        kw["overrides_applied"] = [dict(o, field=field, value=float(o["value"]),
                                        periods_filled=["2023-12-31", "2024-12-31", "2025-12-31"])]
    n = _numbers(release=release, **kw)
    return n, _judgment(n, **{f"{field}_override": dict(o)})


def test_last_filed_unit_usd_override_without_a_currency_refuses():
    """[ADDITION — HTHT] an applied override used verbatim as USD by decision 7's last-filed-unit fallback at a
    CNY / GBP filer, with no currency on the judgment.json override, refuses with the text the worker acts on —
    declare USD, or restate / block NEEDS_MAIN_AGENT — before any counterfactual replay."""
    n, j = _verbatim_run("capex", HTHT_CAPEX_OV, "CNY")
    r = _with(n, j).refused("capex_override 828,000,000", "verbatim as US dollars because the last filed unit for capex is USD",
                            "historically filed in CNY", 'declare currency: "USD"',
                            "if it is in CNY, it cannot be used as is", "NEEDS_MAIN_AGENT: capex")
    assert r.result["spawned"] == [], r.result["spawned"]
    n, j = _verbatim_run("sbc", PUK_SBC_OV, "GBP")
    _with(n, j).refused("sbc_override 85,000,000", "historically filed in GBP", "NEEDS_MAIN_AGENT: sbc")


def test_last_filed_unit_usd_override_controls():
    """[ADDITION — HTHT] controls: PUK / CX declaring currency "USD" pass the check (the run goes on to its
    counterfactual — here the fail-loud stand-in); a converted override (FER) and a declared-USD record are not this
    check's business; an override declared but not applied scores; a pre-5.5 record (no currency_basis: that engine
    converted every override — HTHT's 5.4.0 record today) keeps scoring with its carried impact."""
    for field, o, ccy, basis in (("sbc", dict(PUK_SBC_OV, currency="USD"), "GBP", "last_filed_unit_usd"),
                                 ("sbc", dict(PUK_SBC_OV, currency="USD"), "MXN", "declared_usd"),
                                 ("sbc", dict(PUK_SBC_OV, value=50000000), "EUR", "converted")):
        n, j = _verbatim_run(field, o, ccy, basis=basis)
        r = _with(n, j)
        assert r.rc == 1 and "counterfactual engine --measure run failed" in r.err, (basis, r.rc, r.err)
        assert r.result["spawned"] == ["SPAWNED_dcf_engine.py.txt"], (basis, r.result["spawned"])
    n, j = _verbatim_run("capex", HTHT_CAPEX_OV, "CNY", applied=False)
    assert _with(n, j).rc == 0
    n, j = _verbatim_run("capex", HTHT_CAPEX_OV, "CNY", basis=None, release=STALE[-1])
    r = _with(n, j)
    assert r.rc == 0 and r.result["spawned"] == [], r.err


# ---------------------------------------------------------------- 11. M1 / M2: net debt on the ADS basis; ratio 1
def _nd_line(engine, ads, ratio, tail=None):
    return (f"- Net debt / normalized OE: {ads:.2f}x on the ADS basis (make_score: the pre-5.5 engine's ratio × ads_ratio "
            f"{ratio:g} — it divided net debt by per-ADS OE × ORDINARY shares; the engine printed {engine:.2f}x"
            + (f" — {tail}; the engine's flag list predates the fix" if tail else "") + ")")


def test_m1_net_debt_on_the_ads_basis_when_main_already_divided_the_cap():
    """[ADDITION — M1] TX / LTM shape: 5.4.0 records from main's 2026-10-18 fix — market_cap_est already
    price × shares ÷ ratio (so no cap correction fires), but net_debt_to_normalized_oe still on per-ADS OE × ORDINARY
    shares. key_numbers prints the ADS-basis ratio beside the engine's and names HIGH_NET_DEBT; score.json records
    net_debt_to_normalized_oe_ads_basis. (Before M1 the line read 1.04x / 0.00x with no note and no record.)"""
    for (ratio, price, shares, nd, ads_s, eng_s) in ((10.0, 57.1, 1963076776.0, 1.0438856618771017, 10.44, 1.04),      # TX
                                                    (2000.0, 47.47, 589306002483.0, 0.0016672842507906276, 3.33, 0.00)):  # LTM
        n = _ads(ratio, price, shares=shares, release="5.4.0", market_cap_est=price * shares / ratio,
                 net_debt_latest=887.8e6, diagnostics={"oe_yield": 0.1, "net_debt_to_normalized_oe": nd, "months_since_fy_end": 9.5})
        assert M.ads_cap_correction(n) is None  # the cap is already divided: never divided a second time
        r = _with(n)
        assert r.rc == 0, r.err
        s, key = r.result["score"], r.result["key"]
        assert s["market_cap_b"] == round(price * shares / ratio / 1e9, 2) and s["market_cap_basis"] == "diluted_latest", s
        assert "ADS-corrected by make_score" not in key, key
        assert s["net_debt_to_normalized_oe_ads_basis"] == round(nd * ratio, 4), s
        assert f"{nd * ratio:.2f}" == f"{ads_s:.2f}" and f"{nd:.2f}" == f"{eng_s:.2f}"
        assert _nd_line(nd, nd * ratio, ratio, "HIGH_NET_DEBT (> 3x) would fire on the ADS basis") in key, key
    # FMS shape (ratio 0.5, 7.10x -> 3.55x): HIGH_NET_DEBT fires on both bases, so no crossing is named
    n = _ads(0.5, 22.17, shares=291190575.0, release="5.4.0", market_cap_est=22.17 * 291190575.0 / 0.5,
             diagnostics={"net_debt_to_normalized_oe": 7.100761700972019})
    r = _with(n)
    assert _nd_line(7.100761700972019, 7.100761700972019 * 0.5, 0.5) in r.result["key"], r.result["key"]
    assert r.result["score"]["net_debt_to_normalized_oe_ads_basis"] == round(7.100761700972019 * 0.5, 4)


def test_m1_net_debt_on_the_ads_basis_beside_the_cap_correction_and_never_on_55():
    """[ADDITION — M1] JD shape (pre-5.4, cap still price × ordinary shares): both corrections, independently; a 5.5
    record (market_cap_basis present) prints the engine's own ratio and records nothing; no recorded ratio -> '—'."""
    nd = -1.0041550880498962
    n = _ads(2.0, 26.6, shares=2978037127, release=None, net_debt_latest=-13.25e9,
             diagnostics={"net_debt_to_normalized_oe": nd})
    r = _with(n, _judgment(n, in_scope_under_40b=False))  # old cap $79.2B out of scope -> corrected $39.6B in scope
    assert r.rc == 0, r.err
    s, key = r.result["score"], r.result["key"]
    assert s["market_cap_basis"] == "ads_corrected_by_make_score" and s["market_cap_b"] == 39.61, s
    assert s["net_debt_to_normalized_oe_ads_basis"] == round(nd * 2, 4)
    assert _nd_line(nd, nd * 2, 2.0, "BIG_NET_CASH (< -2x) would fire on the ADS basis") in key, key
    mb = {"shares_used": 2e9, "shares_source": "diluted_latest", "ads_ratio": 2.0, "formula": "price × shares ÷ ads_ratio"}
    n55 = _numbers(release=CUR, filer_annual_form="20-F", price=20.0, shares_diluted_latest=2e9, market_cap_est=20e9,
                   ads_ratio={"ratio": 2.0, "source": "s", "reason": "r"}, market_cap_basis=mb,
                   diagnostics={"net_debt_to_normalized_oe": 1.6})
    assert M.ads_net_debt_basis(n55) is None
    r = _with(n55)
    assert "- Net debt / normalized OE: 1.60x\n" in r.result["key"] and "net_debt_to_normalized_oe_ads_basis" not in r.result["score"]
    r = _with(_ads(2.0, 20.0, diagnostics={"oe_yield": 0.1}))
    assert "- Net debt / normalized OE: —" in r.result["key"] and "net_debt_to_normalized_oe_ads_basis" not in r.result["score"]


def test_m2_ratio_one_is_no_correction():
    """[ADDITION — M2] AEG / BCE shape: a pre-5.5 record with ads_ratio 1 — price × shares ÷ 1 is the engine's own
    cap, so nothing is 'corrected': basis diluted_latest, no ADS label on the cap or the net-debt line, no ADS-basis
    ratio. (Before M2: basis ads_corrected_by_make_score and two '× 1' lines beside identical figures.)"""
    for release in STALE:
        n = _ads(1.0, 20.0, release=release, diagnostics={"net_debt_to_normalized_oe": -1.3})
        assert M.ads_cap_correction(n) is None and M.ads_net_debt_basis(n) is None
        r = _with(n)
        assert r.rc == 0, r.err
        s, key = r.result["score"], r.result["key"]
        assert s["market_cap_b"] == 20.0 and s["market_cap_basis"] == "diluted_latest", s
        assert "- Market cap (est): $20.000B (basis: diluted_latest)" in key and "ADS" not in key, key
        assert "- Net debt / normalized OE: -1.30x\n" in key and "net_debt_to_normalized_oe_ads_basis" not in s


# ---------------------------------------------------------------- 12. M3: payable base under a release mismatch
PAY_FIGS = [81_599_000.0, 322_791_000.0, 1_824_910_000.0, 2_234_426_000.0, 1_859_691_000.0]  # RNR, test_payable_base
PAY_SHARES = 46_483_000.0
PAY_BASE = sum(PAY_FIGS) / 5 / PAY_SHARES
PAY_BO = {"value": PAY_BASE, "kind": "filing", "basis": "payable_earnings_5y", "figures": list(PAY_FIGS),
          "shares": PAY_SHARES, "source": "Q4 earnings releases FY2021/FY2023/FY2025 (test)", "reason": "insurer payable-earnings rule"}


def _payable(release, **kw):
    """An RNR-shaped run pinned through --base-judgment to the payable-earnings base (SIC 6331)."""
    inputs = {"moat": 6, "probs": PROBS, "offsets": [-0.12, -0.05, 0.0, 0.05, 0.12], "mults": [0.75, 0.9, 1.0, 1.1, 1.25],
              "g_terminal": 0.025, "base_oe_ps_arg": PAY_BASE, "base_pin_source": "judgment_base_override"}
    n = _numbers(release=release, tier_by_numbers="C", implied_irr_weighted=0.12, base_oe_per_share=PAY_BASE,
                 base_source="judgment_base_override", inputs=inputs,
                 payable_base={"basis": "payable_earnings_5y", "figures": list(PAY_FIGS), "average": sum(PAY_FIGS) / 5,
                               "shares": PAY_SHARES, "per_ordinary_share": PAY_BASE, "ads_ratio": 1.0,
                               "pinned_per_share": PAY_BASE, "sic": "6331",
                               "sic_description": "FIRE, MARINE & CASUALTY INSURANCE"}, **kw)
    return n, _judgment(n, base_override=dict(PAY_BO))


PAY_MEASURED = {"base_used": "payable_5y", "base_oe_without_override": 77.78, "base_oe_with_override": round(PAY_BASE, 4),
                "base_oe_impact_pct": -65.019, "weighted_irr_without_override": 0.2731, "weighted_irr_with_override": 0.12,
                "weighted_irr_impact_pp": -15.31, "tier_by_numbers_without_override": "S", "tier_by_numbers_with_override": "C"}


def _run_with_registry(n, j, entries):
    r = Run(n, j)
    with open(r.registry, "w", encoding="utf-8") as f:
        json.dump({"entries": entries}, f, indent=1)
    r.run()
    try:
        r.result = dict(r.state(), score=r.score() if r.rc == 0 else None, key=r.key() if r.rc == 0 else None,
                        entries=r.entries(), spawned=r.spawned())
    finally:
        r.close()
    return r


def test_m3_stale_payable_record_spawns_nothing_and_writes_a_consistent_record():
    """[ADDITION — M3] A pre-5.5 payable-pinned record: payable_pin_impact (the current engine's native-base replay)
    is never run — the fail-loud stand-in is not reached — and score.json, the registry and key_numbers.md are all
    written. With no prior measurement the base_override event's impact fields are null with the note. (Before M3 the
    replay ran after score.json was written: rc 1, a score with no registry entry and no key_numbers.md.)"""
    for release in STALE:
        n, j = _payable(release)
        r = _with(n, j)
        assert r.rc == 0, (release, r.err)
        assert r.result["spawned"] == [], r.result["spawned"]
        assert r.result["score"]["tier_final"] == "C" and "## Payable-earnings base" in r.result["key"]
        ev = [e for e in r.result["entries"] if e.get("event") == "base_override"]
        assert len(ev) == 1 and ev[0]["basis"] == "payable_earnings_5y" and ev[0]["figures"] == PAY_FIGS, ev
        assert {k: ev[0][k] for k in M.PAYABLE_IMPACT_KEYS} == {
            "base_used": "payable_5y", "base_oe_without_override": None, "base_oe_with_override": round(PAY_BASE, 4),
            "base_oe_impact_pct": None, "weighted_irr_without_override": None, "weighted_irr_with_override": 0.12,
            "weighted_irr_impact_pp": None, "tier_by_numbers_without_override": None, "tier_by_numbers_with_override": "C"}, ev
        assert ev[0]["counterfactual_engine_release"] == release
        assert ev[0]["note"] == f"not measured: engine output predates release {CUR}; re-run the engine to measure", ev
        assert "impact_carried_from_prior_score" not in ev[0]


def test_m3_stale_payable_record_carries_the_prior_registry_measurement():
    """[ADDITION — M3] The prior run's base_override registry event measured on THIS pinned base and weighted IRR is
    carried (impact_carried_from_prior_score, counterfactual_engine_release); one measured on another base, or one
    that was itself 'not measured', is not."""
    n, j = _payable(STALE[-1])
    prior = dict(PAY_MEASURED, ticker=T, event="base_override", date="2026-10-18", value=PAY_BASE)
    other_ticker = dict(prior, ticker="OTHER")
    r = _run_with_registry(n, j, [other_ticker, prior])
    assert r.rc == 0 and r.result["spawned"] == [], r.err
    ev = [e for e in r.result["entries"] if e.get("event") == "base_override" and e["ticker"] == T]
    assert len(ev) == 1, ev
    assert {k: ev[0][k] for k in M.PAYABLE_IMPACT_KEYS} == PAY_MEASURED, ev
    assert ev[0]["impact_carried_from_prior_score"] is True and ev[0]["counterfactual_engine_release"] == STALE[-1]
    assert [e for e in r.result["entries"] if e["ticker"] == "OTHER"] == [other_ticker]  # other tickers untouched
    for bad in (dict(prior, base_oe_with_override=30.0), dict(prior, weighted_irr_with_override=0.2),
                dict(prior, base_oe_without_override=None, note="not measured: …")):
        r = _run_with_registry(n, j, [bad])
        ev = [e for e in r.result["entries"] if e.get("event") == "base_override"]
        assert r.rc == 0 and ev[0]["base_oe_without_override"] is None and ev[0]["note"].startswith("not measured"), ev
        assert "impact_carried_from_prior_score" not in ev[0]


def test_m3_override_impact_on_a_payable_pin_is_labelled_payable_5y():
    """[ADDITION — M3] _impact_from_run labels a payable-pinned run 'payable_5y' (it said 'ttm'), so a stale record's
    carried / not-measured override_impact block names the base the score actually used."""
    applied = [{"field": "sbc", "value": 1e6, "kind": "filing", "source": "Form 10-K FY2025 cash-flow statement",
                "reason": "untagged", "periods_filled": ["2025-12-31"]}]
    n, j = _payable(STALE[-1], data_gap=["sbc"], data_gap_uncovered=[], overrides_applied=applied)
    j["sbc_override"] = {"value": 1e6, "kind": "filing", "source": "Form 10-K FY2025 cash-flow statement",
                         "reason": "SBC printed on the cash-flow statement, untagged in companyfacts"}
    r = _with(n, j)
    assert r.rc == 0 and r.result["spawned"] == [], r.err
    imp = r.result["score"]["override_impact"]
    assert imp["base_used"] == "payable_5y" and imp["note"].startswith("not measured"), imp
    assert M._impact_from_run(n)[2] == "payable_5y"
    assert M._impact_from_run(dict(n, payable_base=None))[2] == "payable_5y"  # pin source alone names it
    assert M._impact_from_run(_numbers(inputs={"base_oe_ps_arg": 2.0}))[2] == "ttm"
    assert M._impact_from_run(_numbers())[2] == "median_3y"


def test_m3_current_release_payable_replay_runs_before_any_write():
    """[ADDITION — M3] On current-release output the payable replay still runs (main's feature), but before the first
    write: a failed replay refuses with no score.json and no key_numbers.md. (Before M3 it ran inside update_registry,
    after score.json was written.)"""
    n, j = _payable(CUR)
    r = _with(n, j)
    r.refused("native-base replay failed")
    assert r.result["spawned"] == ["SPAWNED_dcf_engine.py.txt"], r.result["spawned"]
    assert not [e for e in r.result["entries"] if e.get("ticker") == T]


# ---------------------------------------------------------------- 13. M4: estimate overrides exempt from the HTHT gate
def test_estimate_override_under_the_last_filed_unit_basis_refuses():
    """[ADDITION — HTHT gate; closes verifier round 2's follow-up (10)] An applied kind "estimate" override recorded
    currency_basis 'last_filed_unit_usd' is refused before any counterfactual is spawned: it cannot declare a currency
    (ruling 7 reserves that for kind filing) and the 0.1x-10x band admits HTHT's RMB 828M relabelled 'estimate'. The
    same figure as kind "filing" still refuses, also on a record without fx_conversion (the gate keys on the recorded
    basis alone). (Before this change the estimate passed the gate and reached its counterfactual.)"""
    est = dict(HTHT_CAPEX_OV, kind="estimate", value=828000000,
               source="estimate (test): HTHT's RMB figure relabelled", reason="DATA_GAP:capex (test)")
    n, j = _verbatim_run("capex", est, "CNY")
    r = _with(n, j)
    r.refused("kind estimate", "verbatim as US dollars", "NEEDS_MAIN_AGENT: capex")
    assert r.result["spawned"] == [], r.result
    n, j = _verbatim_run("capex", dict(est, kind="filing"), "CNY")
    _with(n, j).refused("verbatim as US dollars", "NEEDS_MAIN_AGENT: capex")
    n, j = _verbatim_run("capex", dict(est, kind="filing"), "CNY")
    n.pop("fx_conversion")
    _with(n, j).refused("verbatim as US dollars", "historically filed in a non-USD currency")


# ---------------------------------------------------------------- 14. M5: share_class_mismatch shapes
SC_SRC = "Form 20-F 2025 Item 9: the ADS represents Class B shares"
# (value, make_score status, engine record): "declared" -> {"declared": True, ...}; None -> no record; "malformed"
SC_SHAPES = [
    (True, "declared"), ({"value": True, "source": SC_SRC, "reason": "EPS is per Class A"}, "declared"),
    ({"value": True}, "declared"), ({"source": SC_SRC}, "declared"), ({"source": SC_SRC, "reason": "r"}, "declared"),
    (None, "none"), (False, "none"), ({}, "none"), ({"value": False, "source": "s", "reason": "checked: same class"}, "none"),
    ("false", "malformed"), ("no", "malformed"), ("true", "malformed"), ("yes", "malformed"), ("", "malformed"),
    (1, "malformed"), (0, "malformed"), (1.0, "malformed"), (["x"], "malformed"), ([], "malformed"),
    ({"value": "false", "source": SC_SRC, "reason": "checked: same class"}, "malformed"), ({"value": "true"}, "malformed"),
    ({"value": 1, "source": SC_SRC}, "malformed"), ({"value": None, "source": SC_SRC}, "malformed"),
    ({"reason": "the ADS is Class B"}, "malformed"), ({"source": "  "}, "malformed"),
]


def test_m5_malformed_share_class_mismatch_refuses_with_the_accepted_shapes():
    """[ADDITION — M5] make_score: every malformed value refuses with "share_class_mismatch must be true or
    {value: true, source, reason}" (nothing written) — also on pre-5.5 output whose engine turned the typo into a
    share_class gap, where the refusal must name the malformed value, not a declaration. (Before M5 "false" / "no" /
    {value: "false"} read as declarations: DATA_GAP:shares — SHARE_CLASS_MISMATCH.)"""
    shape = "share_class_mismatch must be true or {value: true, source, reason}"
    n = _numbers()
    for v, status in SC_SHAPES:
        if status != "malformed":
            continue
        r = _with(n, _judgment(n, share_class_mismatch=v))
        r.refused(shape, repr(v))
        assert "SHARE_CLASS_MISMATCH" not in r.err, r.err
    old = _numbers(release=STALE[-1], data_gap=["share_class"], data_gap_uncovered=["share_class"], tier_by_numbers=None)
    r = _with(old, _judgment(old, share_class_mismatch="false"))
    r.refused(shape, "'false'")
    assert M.SHARE_CLASS_SHAPE == shape
    for v, status in SC_SHAPES:
        assert M.share_class_status({"share_class_mismatch": v})[0] == status, (v, status)
    assert M.share_class_status({})[0] == "none" and M.share_class_status(None)[0] == "none"


def test_m5_engine_loader_classifies_every_shape_like_make_score():
    """[ADDITION — M5] dcf_engine.load_share_class_mismatch (unit, signature unchanged): a declaration returns
    {declared: True, source, reason}; no declaration returns None; a malformed value returns {"malformed":
    repr(value)} with no "declared" key (the engine raises the share_class gap only for a declared record)."""
    tmp = tempfile.mkdtemp(prefix="share_class_")
    saved = E.BASE
    try:
        E.BASE = tmp
        os.makedirs(os.path.join(tmp, T))
        assert E.load_share_class_mismatch(T) is None  # no judgment.json
        for v, status in SC_SHAPES:
            with open(os.path.join(tmp, T, "judgment.json"), "w", encoding="utf-8") as f:
                json.dump({"share_class_mismatch": v} if v is not None else {}, f)
            rec = E.load_share_class_mismatch(T)
            if status == "declared":
                st, src, why = M.share_class_status({"share_class_mismatch": v})
                assert rec == {"declared": True, "source": src, "reason": why} and rec, (v, rec)
            elif status == "none":
                assert rec is None, (v, rec)
            else:
                assert rec == {"malformed": repr(v)}, (v, rec)  # recorded; no "declared" key, so no gap
    finally:
        E.BASE = saved
        shutil.rmtree(tmp, ignore_errors=True)


ENGINE_SC_SCRIPT = r'''
import json, sys
sys.path.insert(0, sys.argv[1])
import engine55_harness as H
fx = H.load_fixture("CCJ")
args = H.recorded_args(H.recorded("CCJ"))
out = []
for decl in json.loads(sys.argv[2]):
    j = {"ads_ratio": {"ratio": 1.0, "source": "test fixture (40-F cover)", "reason": "test fixture"},
         "share_class_mismatch": decl}
    r = H.run_engine("CCJ", args, base=H.make_base(fx, j, None, copy_repo_files=False), fixture=fx)
    n = r["numbers"] or {}
    out.append({"exit": r["exit"], "gap": n.get("data_gap"), "rec": n.get("share_class_mismatch"),
                "flags": [f for f in n.get("fragility_flags") or [] if "SHARE_CLASS" in f]})
print("RESULT " + json.dumps(out))
'''


def test_m5_engine_run_records_a_malformed_value_without_a_gap():
    """[ADDITION — M5] The offline engine on the CCJ fixture (in a subprocess, so this module's dcf_engine is never
    reloaded): "false" and {value: "false", source, reason} are recorded as malformed with no share_class gap and a
    tier (before M5: exit 4, data_gap ['share_class']); a declaration still blocks; false is no record."""
    decls = ["false", {"value": "false", "source": SC_SRC, "reason": "checked: same class"}, True, False]
    p = subprocess.run([sys.executable, "-c", ENGINE_SC_SCRIPT, HERE, json.dumps(decls)], capture_output=True,
                       text=True, encoding="utf-8", timeout=600, env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    line = [x for x in p.stdout.splitlines() if x.startswith("RESULT ")]
    assert p.returncode == 0 and line, (p.returncode, p.stdout[-2000:], p.stderr[-2000:])
    res = json.loads(line[-1][len("RESULT "):])
    for d, o in zip(decls[:2], res[:2]):
        assert o["exit"] == 0 and "share_class" not in (o["gap"] or []) and not o["flags"], (d, o)
        assert o["rec"] == {"malformed": repr(d)}, (d, o)
    assert res[2]["exit"] == 4 and "share_class" in res[2]["gap"] and res[2]["rec"]["declared"] is True, res[2]
    assert res[3]["exit"] == 0 and res[3]["rec"] is None and "share_class" not in (res[3]["gap"] or []), res[3]


# ---------------------------------------------------------------- 15. M7: split facts in key_numbers.md
def test_m7_unconfirmed_and_in_history_split_facts_are_printed():
    """[ADDITION — M7] share_basis.unconfirmed_split_facts -> one 'unconfirmed split fact' line each (the worker must
    check the latest 10-Q: history and price may sit on different bases, and no flag fires); in_history_split_facts ->
    one compact, de-duplicated line. Empty lists print nothing. (Before M7 neither record reached key_numbers.md.)"""
    sb = {"split": None, "divergence": None,
          "unconfirmed_split_facts": [{"date": "2026-06-30", "ratio_filed": 2.0}, {"date": "2026-08-15", "ratio_filed": 0.05}],
          "in_history_split_facts": [{"date": "2024-03-27", "ratio_filed": 3.0}, {"date": "2024-03-27", "ratio_filed": 3.0},
                                     ["2021-05-01", 0.1]]}
    key = _with(_numbers(share_basis=sb)).result["key"]
    assert ("- Share basis: unconfirmed split fact 2026-06-30 ratio 2 (no post-event cover-page count confirms it) "
            "— check the latest 10-Q") in key, key
    assert "- Share basis: unconfirmed split fact 2026-08-15 ratio 0.05 (no post-event cover-page count confirms it)" in key
    assert ("- Share basis: in-history split facts (dated on or before the latest FY end; never applied by the engine "
            "— informational): 2021-05-01 ratio 0.1; 2024-03-27 ratio 3") in key, key
    key = _with(_numbers(share_basis=dict(sb, unconfirmed_split_facts=[], in_history_split_facts=[]))).result["key"]
    assert "Share basis" not in key, key


# ---------------------------------------------------------------- 16. verifier round 2: a "not measured" impact is never carried
def test_r2_not_measured_override_impact_is_never_carried():
    """[ADDITION — verifier round 2] carried_override_impact carried ANY prior block whose with-override base and IRR
    matched — including a block that was itself "not measured". Unit: such a prior yields a fresh not-measured block
    without impact_carried_from_prior_score (carried_payable_impact's rule). End to end: make_score twice over the
    same stale record with no measured prior — run 2 used to write impact_carried_from_prior_score: true beside the
    note and the null measured fields; now both runs write the same not-measured block."""
    n = _numbers(release=STALE[-1], data_gap=["sbc"], data_gap_uncovered=[])
    not_measured = M.carried_override_impact(n, None)
    assert not_measured["note"] and "impact_carried_from_prior_score" not in not_measured, not_measured
    again = M.carried_override_impact(n, {"override_impact": not_measured})
    assert again == not_measured, again                                     # round 2 before the fix: carried
    n = _numbers(release=STALE[-1], data_gap=["sbc"], data_gap_uncovered=[],
                 overrides_applied=[{"field": "sbc", "value": 1e6, "kind": "filing", "source": "Form 10-K FY2025 cash-flow statement",
                                     "reason": "untagged", "periods_filled": ["2025-12-31"]}])
    j = _judgment(n, sbc_override={"value": 1e6, "kind": "filing", "source": "Form 10-K FY2025 cash-flow statement",
                                   "reason": "SBC printed on the cash-flow statement, untagged in companyfacts"})
    r = Run(n, j)
    try:
        r.run().ok()
        first = r.score()["override_impact"]
        assert first["note"].startswith("not measured") and "impact_carried_from_prior_score" not in first, first
        r.run().ok()
        second = r.score()["override_impact"]
        assert "impact_carried_from_prior_score" not in second, second      # before the fix: True beside the note
        assert second == first, (first, second)
        assert r.spawned() == [], r.spawned()
        assert "- Impact not measured:" in r.key()
    finally:
        r.close()



# ---------------------------------------------------------------- declared base_override pin (VIV shape)
GATE_FIRED_ENGINE = r'''import json, os, sys
here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, "SPAWNED_" + os.path.basename(__file__) + ".txt"), "a", encoding="utf-8") as f:
    f.write(" ".join(sys.argv) + "\n")
# the counterfactual replay with overrides off: the shares gap fires, so no IRR
print(json.dumps({"base_oe_per_share": 1.28, "implied_irr_weighted": None, "data_gap": ["shares"],
                  "data_gap_uncovered": ["shares"], "tier_by_numbers": None}))
'''


def _declared_pin_record():
    pin = 1.2803686126106435
    n = _numbers(release=CUR, base_oe_per_share=pin, base_source="agent_supplied_ttm_override",
                 data_gap=["shares"], data_gap_uncovered=[],
                 overrides_applied=[{"field": "shares", "value": 3223658000, "kind": "filing",
                                     "source": "Form 20-F FY2025 Note 24.h EPS", "reason": "basic-only count filed",
                                     "periods_filled": ["2025-12-31"]}])
    n["inputs"] = dict(n["inputs"], base_oe_ps_arg=pin, base_pin_source="base_oe_ps_arg")
    j = _judgment(n, base_override={"value": pin, "source": "this run's dcf_numbers.json latest FY OE/share x 2",
                                    "reason": "share-scale artefact in the median"},
                  shares_override={"value": 3223658000, "kind": "filing", "source": "Form 20-F FY2025 Note 24.h EPS",
                                   "reason": "diluted equals basic (no dilutive instruments)"})
    return n, j


def test_declared_pin_override_impact_holds_the_pin_and_never_runs_ttm():
    """[v5.5] A --base-oe-ps pin that equals a declared base_override (no basis) and is not ttm.json's figure is
    measured with the pin held constant: only the engine is replayed (overrides off), never ttm.py. Before 5.5 it
    fell into the TTM branch and re-ran ttm.py, which an IFRS filer cannot run (VIV refused: 'cannot compute the
    no-override TTM base'). With the fail-loud engine the refusal names the declared pinned base and ttm.py is not
    spawned; with an engine whose replay fires the shares gate, the score is written with a null impact and
    unblocks_tier true."""
    n, j = _declared_pin_record()
    r = _with(n, j)
    r.refused("declared pinned base")
    assert r.result["spawned"] == ["SPAWNED_dcf_engine.py.txt"], r.result["spawned"]
    n, j = _declared_pin_record()
    run = Run(n, j)
    try:
        with open(os.path.join(run.sysdir, "dcf_engine.py"), "w", encoding="utf-8") as f:
            f.write(GATE_FIRED_ENGINE)
        run.run()
        assert run.rc == 0, run.err
        s = run.score()
        oi = s["override_impact"]
        assert oi["base_used"] == "declared_pin" and oi["unblocks_tier"] is True, oi
        assert oi["base_oe_without_override"] is None and oi["weighted_irr_without_override"] is None, oi
        assert "declared base_override pin" in run.key(), run.key()[:400]
        assert run.spawned() == ["SPAWNED_dcf_engine.py.txt"], run.spawned()
    finally:
        run.close()


# ------------------------------------------------- re-score audit (2026-10-19)
NTNX_SCALE_REASON = "latest diluted count 292,183 is 0.00107988x the cover-page count 270,570,179 (outside 1/100-100x)"


def _pin_rescue_record(tier="A", irr=0.22, rescued=True):
    """A 5.5 record whose tier exists only because a declared base_override pin rescued a share-scale defect
    (NTNX shape: the engine's median 1,355.34 on a count filed in thousands, the pin 1.3553)."""
    pin = 1.3553
    n = _numbers(release=CUR, base_oe_per_share=pin, base_oe_normalized_per_share=1355.34,
                 base_source="agent_supplied_ttm_override", tier_by_numbers=tier, implied_irr_weighted=irr,
                 implied_irr_base=irr,
                 share_scale={"defect": rescued, "tests": {"a": False, "b": rescued},
                              "reasons": [NTNX_SCALE_REASON] if rescued else [], "rescued_by_pin": rescued})
    n["inputs"] = dict(n["inputs"], base_oe_ps_arg=pin, base_pin_source="base_oe_ps_arg")
    n["scenarios"] = {lbl: dict(s, irr=irr) for lbl, s in n["scenarios"].items()}
    j = _judgment(n, base_override={"value": pin, "kind": "estimate",
                                    "source": "this run's dcf_numbers.json latest FY OE/share / 1000",
                                    "reason": "share counts filed in thousands"})
    return n, j


def test_pin_rescued_tier_closes_both_alert_gates_and_records_the_pin_impact():
    """[v5.5 — re-score audit, TEM / NTNX] A tier that exists only because a declared base_override pin rescued a
    share-scale defect (share_scale.rescued_by_pin) closes the entry gate (Tier A) and the exit gate (Tier D) with
    "tier exists only because of a judgment override", exactly as a field override with unblocks_tier does; and the
    registry base_override event carries kind and the pin's impact (engine median on the defective basis -> pin,
    no IRR without it, unblocks_tier true). Before the fix the gates read only field overrides: TEM and NTNX
    published exit_alert_eligible true, and the event had no kind and no impact. A record whose pin rescues
    nothing keeps both gates and records no impact (control)."""
    n, j = _pin_rescue_record("A", 0.22)
    r = _with(n, j)
    assert r.rc == 0, r.err
    s = r.result["score"]
    assert s["alert_eligible"] is False, s
    assert "tier exists only because of a judgment override" in (s.get("alert_suppressed_reason") or ""), s
    ev = [e for e in r.result["entries"] if e.get("event") == "base_override"]
    assert len(ev) == 1, r.result["entries"]
    ev = ev[0]
    assert ev["kind"] == "estimate" and ev["base_used"] == "declared_pin" and ev["unblocks_tier"] is True, ev
    assert ev["base_oe_without_override"] == 1355.34 and ev["base_oe_with_override"] == 1.3553, ev
    assert ev["weighted_irr_without_override"] is None and ev["weighted_irr_with_override"] == 0.22, ev
    assert "SHARE_SCALE" in ev["impact_note"] and NTNX_SCALE_REASON in ev["impact_note"], ev
    assert r.result["spawned"] == [], r.result["spawned"]
    n, j = _pin_rescue_record("D", 0.05)
    r = _with(n, j)
    assert r.rc == 0, r.err
    s = r.result["score"]
    assert s["exit_alert_eligible"] is False, s
    assert "tier exists only because of a judgment override" in (s.get("exit_alert_suppressed_reason") or ""), s
    n, j = _pin_rescue_record("D", 0.05, rescued=False)
    r = _with(n, j)
    assert r.rc == 0, r.err
    assert r.result["score"]["exit_alert_eligible"] is True, r.result["score"]
    ev = [e for e in r.result["entries"] if e.get("event") == "base_override"][0]
    assert ev["kind"] == "estimate" and "base_used" not in ev and "unblocks_tier" not in ev, ev


def test_registry_keeps_the_first_date_of_an_unchanged_declaration():
    """[v5.5 — re-score audit, NTNX / WF] The wholesale per-ticker replace stamped today on every entry, so a
    re-score rewrote when each declaration was first taken (NTNX's 2026-10-15 base_override and WF's 2026-10-16
    ads_ratio read 2026-10-19). An entry whose declaration is unchanged keeps its earliest recorded date — also a
    base_override that only gains the missing `kind` —; a changed declaration (a new tier_override reason) takes
    today; other tickers' entries are untouched; a second run changes nothing."""
    n, j = _pin_rescue_record("D", 0.05)
    n["inputs"] = dict(n["inputs"], g_terminal=0.03)
    j.update(tier_override="F", tier_override_reason="new reason: the pin is the only base")
    run = Run(n, j)
    try:
        bo = j["base_override"]
        prior = {"entries": [
            {"ticker": T, "event": "base_override", "date": "2026-10-15", "value": bo["value"],
             "source": bo["source"], "reason": bo["reason"]},
            {"ticker": T, "event": "gterm", "date": "2026-10-01", "value": 0.03},
            {"ticker": T, "event": "gterm", "date": "2026-10-03", "value": 0.03},
            {"ticker": T, "event": "tier_override", "date": "2026-10-02", "tier_by_numbers": "D", "tier_final": "F",
             "reason": "old reason"},
            {"ticker": "OTHER", "event": "gterm", "date": "2026-09-30", "value": 0.02}]}
        with open(run.registry, "w", encoding="utf-8") as f:
            json.dump(prior, f, indent=1)
        run.run()
        assert run.rc == 0, run.err
        mine = {e.get("event"): e for e in run.entries() if e.get("ticker") == T}
        assert mine["base_override"]["date"] == "2026-10-15", mine["base_override"]
        assert mine["base_override"]["kind"] == "estimate", mine["base_override"]
        assert mine["gterm"]["date"] == "2026-10-01", mine["gterm"]
        assert mine["tier_override"]["date"] not in ("2026-10-02",) and mine["tier_override"]["date"] > "2026-10-15", \
            mine["tier_override"]
        other = [e for e in run.entries() if e.get("ticker") == "OTHER"]
        assert other == [prior["entries"][-1]], other
        first = run.entries()
        run.run()
        assert run.rc == 0, run.err
        assert run.entries() == first, "a second run over the same record changed the registry"
    finally:
        run.close()


# ------------------------------------------------- Codex review of PR #31
TTM_LEG_STANDIN = r'''import json, os, sys
# Stand-in ttm.py / dcf_engine.py (test_make_score_55, Codex PR #31): reads standin.json beside it.
here = os.path.dirname(os.path.abspath(__file__))
name = os.path.basename(__file__)
cfg = json.load(open(os.path.join(here, "standin.json"), encoding="utf-8"))
no_ov = os.environ.get("DCF_NO_OVERRIDES") == "1"
with open(os.path.join(here, "SPAWNED_" + name + ".txt"), "a", encoding="utf-8") as f:
    f.write(" ".join(sys.argv[1:]) + (" [no overrides]" if no_ov else "") + "\n")
if name == "ttm.py":
    if no_ov and not cfg.get("ttm_builds_without"):
        sys.stderr.write("ttm.py: sbc: no YTD SBC leg filed (stand-in)\n")
        sys.exit(cfg.get("no_override_exit", 3))
    print(json.dumps(cfg["ttm"]))
else:
    a = sys.argv
    base = float(a[a.index("--base-oe-ps") + 1]) if "--base-oe-ps" in a else None
    print(json.dumps({"base_oe_per_share": base, "implied_irr_weighted": cfg["irr"], "data_gap": []}))
'''

APA_PIN = 5.669491525423729
APA_SHARES = 354000000.0
APA_LEG = 53060273.97260274


def _ttm_leg_record():
    """APA shape: a --ttm run pinned to ttm.json, whose YTD SBC legs only the $107M estimate fills; the annual
    engine applied no override (overrides_applied empty, override_checks records the in-band estimate)."""
    n = _numbers(release=CUR, base_oe_per_share=APA_PIN, base_source="ttm_json", tier_by_numbers="C",
                 implied_irr_weighted=0.1245, implied_irr_base=0.1245, overrides_applied=[],
                 override_checks={"sbc": {"value": 107000000.0, "last_filed_value": 107000000, "last_filed_unit": "USD",
                                          "out_of_band": False, "ack_reason_present": False, "currency_basis": "no_fx"}})
    n["inputs"] = dict(n["inputs"], base_oe_ps_arg=APA_PIN, base_pin_source="ttm_json")
    n["scenarios"] = {lbl: dict(s, irr=0.1245) for lbl, s in n["scenarios"].items()}
    src = "Last filed SBC: FY2025 AllocatedShareBasedCompensationExpense $107,000,000 (Form 10-K FY2025)"
    j = _judgment(n, sbc_override={"value": 107000000.0, "kind": "estimate", "source": src,
                                   "reason": "the 10-Qs print no SBC line; fills ttm.py's YTD SBC legs"})
    ttm = {"ttm_oe_per_share": APA_PIN, "ttm_oe_total": APA_PIN * APA_SHARES, "ttm_shares_diluted": APA_SHARES,
           "overrides_used": [{"field": "sbc", "value": 107000000.0, "kind": "estimate", "source": src,
                               "legs_filled": {"ytd_prior": {"period": ["2025-01-01", "2025-06-30"], "amount": APA_LEG},
                                               "ytd_current": {"period": ["2026-01-01", "2026-06-30"], "amount": APA_LEG}}}]}
    return n, j, ttm


def _ttm_leg_run(n, j, ttm, builds_without=False, no_override_exit=3):
    run = Run(n, j)
    for name in ("dcf_engine.py", "ttm.py"):
        with open(os.path.join(run.sysdir, name), "w", encoding="utf-8") as f:
            f.write(TTM_LEG_STANDIN)
    with open(os.path.join(run.sysdir, "standin.json"), "w", encoding="utf-8") as f:
        json.dump({"ttm": ttm, "irr": 0.1245, "ttm_builds_without": builds_without, "no_override_exit": no_override_exit}, f)
    with open(os.path.join(run.folder, "ttm.json"), "w", encoding="utf-8") as f:
        json.dump(ttm, f)
    return run


def test_ttm_leg_override_is_reported_measured_and_closes_the_gates():
    """[Codex, PR #31 — APA] An override that only ttm.py used (it fills the YTD SBC legs of the TTM base the score
    is pinned to; the annual engine applied none) is reported in score.json overrides (scope ttm_legs) and
    override_impact (base_used ttm, measured by zero-filling its legs — the prior- and current-YTD legs cancel, so
    the base and IRR do not move), recorded in the registry with scope ttm_legs, printed in key_numbers.md, and —
    because ttm.py cannot build the TTM base without it — sets unblocks_tier and closes the exit gate ("tier exists
    only because of a judgment override"). Before the fix the score said nothing about the override and published
    exit_alert_eligible true."""
    n, j, ttm = _ttm_leg_record()
    run = _ttm_leg_run(n, j, ttm)
    try:
        run.run()
        assert run.rc == 0, run.err
        s = run.score()
        assert s.get("overrides") == [{"field": "sbc", "value": 107000000.0, "kind": "estimate",
                                       "source": j["sbc_override"]["source"], "scope": "ttm_legs"}], s.get("overrides")
        oi = s["override_impact"]
        assert oi["base_used"] == "ttm" and oi["unblocks_tier"] is True, oi
        assert oi["base_oe_without_override"] == round(APA_PIN, 4) and oi["base_oe_impact_pct"] == 0.0, oi
        assert oi["weighted_irr_without_override"] == 0.1245 and oi["weighted_irr_impact_pp"] == 0.0, oi
        assert s["exit_alert_eligible"] is False, s
        assert "tier exists only because of a judgment override" in s["exit_alert_suppressed_reason"], s
        ent = [e for e in run.entries() if e.get("field") == "sbc"]
        assert len(ent) == 1 and ent[0]["scope"] == "ttm_legs" and ent[0]["unblocks_tier"] is True, ent
        assert ent[0]["kind"] == "estimate" and ent[0]["reason"] == j["sbc_override"]["reason"], ent
        k = run.key()
        assert "TTM legs only (ttm.json)" in k and "ytd_prior: 2025-01-01..2025-06-30" in k, k[-1200:]
        assert "ttm.py cannot build the TTM base without this override" in k and "blocks scoring entirely" not in k, k[-900:]
        assert run.spawned() == ["SPAWNED_dcf_engine.py.txt", "SPAWNED_ttm.py.txt"], run.spawned()
    finally:
        run.close()


def test_ttm_leg_override_controls_and_refusal():
    """[Codex, PR #31] Controls: when ttm.py CAN build the TTM base without the override, the override is still
    reported and measured but unblocks_tier stays false and the exit gate stays open; a TTM-pinned record whose
    ttm.json used no override reports none. Refusal: ttm.json used an sbc override that judgment.json no longer
    declares (or declares with another value) — the TTM pin and the judgment are out of sync."""
    n, j, ttm = _ttm_leg_record()
    run = _ttm_leg_run(n, j, ttm, builds_without=True)
    try:
        run.run()
        assert run.rc == 0, run.err
        s = run.score()
        assert s["overrides"][0]["scope"] == "ttm_legs" and s["override_impact"]["unblocks_tier"] is False, s
        assert s["exit_alert_eligible"] is True, s
    finally:
        run.close()
    n, j, ttm = _ttm_leg_record()
    ttm = dict(ttm, overrides_used=[])
    j.pop("sbc_override")
    run = _ttm_leg_run(n, j, ttm)
    try:
        run.run()
        assert run.rc == 0, run.err
        s = run.score()
        assert "overrides" not in s and "override_impact" not in s and s["exit_alert_eligible"] is True, s
        assert run.spawned() == [], run.spawned()
    finally:
        run.close()
    n, j, ttm = _ttm_leg_record()
    j.pop("sbc_override")
    run = _ttm_leg_run(n, j, ttm)
    try:
        run.run()
        run.refused("ttm.json used a sbc_override to fill TTM legs but judgment.json no longer declares one")
    finally:
        run.close()
    n, j, ttm = _ttm_leg_record()
    j["sbc_override"]["value"] = 95000000.0
    run = _ttm_leg_run(n, j, ttm)
    try:
        run.run()
        run.refused("disagrees with the override ttm.json used")
    finally:
        run.close()


def test_registry_declaration_identity_covers_currency_scope_and_payable_fields():
    """[Codex, PR #31] keep_first_dates keeps a first-recorded date only for a truly unchanged declaration:
    gaining or dropping currency "USD" (verbatim dollars vs FX conversion), a different scope (ttm_legs), a
    different payable basis / figures / shares, or a changed kind each take the new date. The one legacy
    allowance: a base_override event recorded before 5.5 carries no `kind` key, so it matches on the other fields."""
    old, new = "2026-10-01", "2026-10-19"

    def kept(prior, cur):
        p = dict(prior, ticker=T, date=old)
        c = dict(cur, ticker=T, date=new)
        M.keep_first_dates([c], [p])
        return c["date"] == old

    f = {"field": "sbc", "value": 85000000, "kind": "filing", "source": "20-F FY2025 note B2.2", "reason": "r"}
    assert kept(f, f)
    assert not kept(f, dict(f, currency="USD")), "gaining currency USD must re-date"
    assert not kept(dict(f, currency="USD"), f), "dropping currency USD must re-date"
    assert kept(dict(f, currency="USD"), dict(f, currency="USD"))
    assert not kept(f, dict(f, scope="ttm_legs")), "a TTM-leg override is a different declaration"
    pb = {"event": "base_override", "value": 27.21, "source": "s", "reason": "r", "kind": "filing",
          "basis": "payable_earnings_5y", "figures": [1, 2, 3, 4, 5], "shares": 46483000}
    assert kept(pb, pb)
    assert not kept(pb, dict(pb, figures=[1, 2, 3, 4, 6])), "different payable figures must re-date"
    assert not kept(pb, dict(pb, shares=46483001)), "different payable shares must re-date"
    assert not kept(pb, dict(pb, basis=None)), "a different basis must re-date"
    assert not kept(pb, dict(pb, kind="estimate")), "a recorded kind that changes must re-date"
    legacy = {k: v for k, v in pb.items() if k != "kind"}
    assert kept(legacy, pb), "a pre-5.5 event without kind matches on the other fields"
    assert not kept(legacy, dict(pb, figures=[9, 9, 9, 9, 9])), "the legacy allowance covers kind only"


def test_registry_persists_override_currency_and_scope():
    """[Codex, PR #31] update_registry writes a field override's declared currency and its scope into the entry
    (so the identity check can see them on the next run); an override without them writes neither key."""
    import tempfile as _tf
    d = _tf.mkdtemp(prefix="ms55_reg_")
    saved = M.REGISTRY
    try:
        M.REGISTRY = os.path.join(d, "overrides_registry.json")
        impact = {"base_used": "median_3y", "base_oe_without_override": 1.0, "base_oe_with_override": 1.1,
                  "base_oe_impact_pct": 10.0, "weighted_irr_without_override": 0.1, "weighted_irr_with_override": 0.11,
                  "weighted_irr_impact_pp": 1.0, "unblocks_tier": True}
        applied = {"sbc": {"value": 85e6, "kind": "filing", "source": "s"},
                   "capex": {"value": 9e6, "kind": "estimate", "source": "s", "scope": "ttm_legs"}}
        j_over = {"sbc": {"value": 85e6, "kind": "filing", "source": "s", "reason": "r", "currency": "USD"},
                  "capex": {"value": 9e6, "kind": "estimate", "source": "s", "reason": "r"}}
        M.update_registry(T, applied, j_over, impact, {}, {"inputs": {}, "fragility_flags": []})
        ents = {e["field"]: e for e in json.load(open(M.REGISTRY, encoding="utf-8"))["entries"]}
        assert ents["sbc"].get("currency") == "USD" and "scope" not in ents["sbc"], ents["sbc"]
        assert ents["capex"].get("scope") == "ttm_legs" and "currency" not in ents["capex"], ents["capex"]
    finally:
        M.REGISTRY = saved
        shutil.rmtree(d, ignore_errors=True)


def test_ttm_leg_unblocks_holds_on_stale_release_output():
    """[PR #31 verifier] On engine output from another release the TTM-leg rule still sets unblocks_tier: from the
    carried prior measurement when it said so (no subprocess), else from ttm.py's no-override run (exit 3). Before,
    carried_override_impact recomputed unblocks_tier from the annual data_gap only and wrote false."""
    n, j, ttm = _ttm_leg_record()
    n = dict(n, engine_release=STALE[-1]) if STALE[-1] is not None else n
    prior = {"override_impact": {"base_used": "ttm", "base_oe_without_override": round(APA_PIN, 4),
                                 "base_oe_with_override": round(APA_PIN, 4), "base_oe_impact_pct": 0.0,
                                 "weighted_irr_without_override": 0.1245, "weighted_irr_with_override": 0.1245,
                                 "weighted_irr_impact_pp": 0.0, "unblocks_tier": True}}
    run = _ttm_leg_run(n, j, ttm)
    try:
        with open(os.path.join(run.folder, "score.json"), "w", encoding="utf-8") as f:
            json.dump(prior, f)
        run.had_prior = True
        run.run()
        assert run.rc == 0, run.err
        oi = run.score()["override_impact"]
        assert oi.get("impact_carried_from_prior_score") is True and oi["unblocks_tier"] is True, oi
        assert "tier exists only because of a judgment override" in run.score()["exit_alert_suppressed_reason"]
        assert run.spawned() == [], run.spawned()
    finally:
        run.close()
    n, j, ttm = _ttm_leg_record()
    n = dict(n, engine_release=STALE[-1]) if STALE[-1] is not None else n
    run = _ttm_leg_run(n, j, ttm)
    try:
        run.run()
        assert run.rc == 0, run.err
        oi = run.score()["override_impact"]
        assert oi.get("note", "").startswith("not measured") and oi["unblocks_tier"] is True, oi
        assert run.spawned() == ["SPAWNED_ttm.py.txt"], run.spawned()
    finally:
        run.close()


def test_ttm_no_override_failure_refuses_instead_of_closing_a_gate():
    """[PR #31 verifier] Only ttm.py's own "cannot compute TTM" exit (3) means no TTM base exists without the
    override. A crash or fetch failure (exit 1) refuses; before, any failure read as "the tier rests on the
    override" and closed the exit gate."""
    n, j, ttm = _ttm_leg_record()
    run = _ttm_leg_run(n, j, ttm, no_override_exit=1)
    try:
        run.run()
        run.refused("ttm.py with overrides disabled did not complete (exit 1)")
    finally:
        run.close()


def test_ttm_json_override_check_covers_engine_applied_fields_and_malformed_legs():
    """[PR #31 verifier] Every override ttm.json used must match judgment.json's value and kind, an override the
    annual engine also applied included (a capex_override edited after ttm.py ran left the pin on the old value
    with nothing refusing); a malformed legs_filled refuses cleanly instead of a traceback; a TTM-only shares leg
    with no period prints as the TTM denominator."""
    n, j, ttm = _ttm_leg_record()
    src = "Form 10-K FY2025 cash-flow statement"
    n["overrides_applied"] = [{"field": "capex", "value": 1186000000.0, "kind": "filing", "source": src,
                               "periods_filled": ["2025-12-31"]}]
    n["data_gap"] = ["capex"]
    n["data_gap_uncovered"] = []
    j["capex_override"] = {"value": 1186000000.0, "kind": "filing", "source": src, "reason": "extension-tagged capex"}
    ttm["overrides_used"] = ttm["overrides_used"] + [{"field": "capex", "value": 600000000.0, "kind": "estimate",
                                                      "source": "old", "legs_filled": {}}]
    run = _ttm_leg_run(n, j, ttm)
    try:
        run.run()
        run.refused("judgment.json capex_override", "disagrees with the override ttm.json used")
    finally:
        run.close()
    for bad in ("junk", ["x"], {"ytd_current": {"period": ["2026-01-01"]}}):
        n, j, ttm = _ttm_leg_record()
        ttm["overrides_used"][0]["legs_filled"] = bad
        run = _ttm_leg_run(n, j, ttm)
        try:
            run.run()
            run.refused("legs_filled is malformed")
        finally:
            run.close()
    n, j, ttm = _ttm_leg_record()
    j["shares_override"] = {"value": 359000000.0, "kind": "filing", "source": "10-Q EPS note", "reason": "no YTD count"}
    ttm["overrides_used"] = ttm["overrides_used"] + [{"field": "shares", "value": 359000000.0, "kind": "filing",
                                                      "source": "10-Q EPS note",
                                                      "legs_filled": {"ytd_current": {"amount": 359000000.0, "prorated": False}}}]
    run = _ttm_leg_run(n, j, ttm)
    try:
        run.run()
        assert run.rc == 0, run.err
        assert "ytd_current: share count (TTM denominator)" in run.key(), run.key()[-900:]
        assert run.score()["override_impact"]["unblocks_tier"] is True
    finally:
        run.close()


def test_ttm_leg_override_at_an_fx_filer_must_declare_usd():
    """[Codex review 2, PR #31] Defence in depth for a stale ttm.json: an override that fills TTM legs at a filer the
    engine converted from another currency (fx_conversion recorded) refuses unless judgment.json declares currency
    "USD" on it; declared (kind filing) it scores."""
    n, j, ttm = _ttm_leg_record()
    n["fx_conversion"] = {"from_currency": "CNY", "to_currency": "USD", "rates": {}, "rates_by_currency": {}}
    run = _ttm_leg_run(n, j, ttm)
    try:
        run.run()
        run.refused('does not declare currency "USD"')
    finally:
        run.close()
    n, j, ttm = _ttm_leg_record()
    n["fx_conversion"] = {"from_currency": "CNY", "to_currency": "USD", "rates": {}, "rates_by_currency": {}}
    j["sbc_override"] = dict(j["sbc_override"], kind="filing", currency="USD")
    ttm["overrides_used"][0]["kind"] = "filing"
    n["override_checks"]["sbc"]["currency_basis"] = "declared_usd"
    run = _ttm_leg_run(n, j, ttm)
    try:
        run.run()
        assert run.rc == 0, run.err
        assert run.score()["overrides"][0]["scope"] == "ttm_legs"
    finally:
        run.close()


def test_ttm_leg_fx_guard_covers_applied_fields_and_normalizes_the_currency():
    """[PR #31 verifier] The TTM-leg currency guard also covers an override the annual engine applied (a stale
    ttm.json can carry a converted override's raw value in its USD legs), and a declaration written "usd" passes like
    "USD" (make_score's validator, the engine and ttm.py all normalize it)."""
    n, j, ttm = _ttm_leg_record()
    n["fx_conversion"] = {"from_currency": "CNY", "to_currency": "USD", "rates": {}, "rates_by_currency": {}}
    src = "Form 20-F FY2025 cash-flow statement"
    n["overrides_applied"] = [{"field": "capex", "value": 828e6, "kind": "filing", "source": src, "periods_filled": ["2025-12-31"]}]
    n["data_gap"], n["data_gap_uncovered"] = ["capex"], []
    j["capex_override"] = {"value": 828e6, "kind": "filing", "source": src, "reason": "RMB capex line"}
    j["sbc_override"] = dict(j["sbc_override"], kind="filing", currency="usd")
    ttm["overrides_used"][0]["kind"] = "filing"
    ttm["overrides_used"] = ttm["overrides_used"] + [{"field": "capex", "value": 828e6, "kind": "filing", "source": src,
        "legs_filled": {"ytd_current": {"period": ["2026-01-01", "2026-06-30"], "amount": 410e6}}}]
    n["override_checks"]["sbc"]["currency_basis"] = "declared_usd"
    run = _ttm_leg_run(n, j, ttm)
    try:
        run.run()
        run.refused('capex_override in its USD legs', 'does not declare currency "USD"')
    finally:
        run.close()


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
