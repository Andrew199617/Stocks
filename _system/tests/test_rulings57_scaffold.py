#!/usr/bin/env python3
"""Engine 5.7 scaffold (lane L0 of the 2026-10-19 rulings PR, Andrew's rulings R1-R9; integration plan 07 §3.1).
Run: python _system/tests/test_rulings57_scaffold.py (or python -m pytest _system/tests). No network; nothing outside
temp dirs is written.

L0 bumps ENGINE_RELEASE to 5.7.0 and places what every lane builds on, with behaviour unchanged apart from the
release string. Each test fails on the code before L0 (ba2bfc0):
1. The release is 5.7.0 and "a 5.7 run" has one predicate (facts.is_rulings_run = make_score.is_57_run, fixed at
   5.7.0); older output is a release mismatch ("engine output predates release 5.7.0").
2. The registry whitelist declares every event type the 5.7 lanes write: a registry holding them loads (load_registry
   refused it before), an unknown name is still refused, none uses an iprd_deferred_payment field name, and the new
   identity keys (absent on every recorded entry) re-date nothing; a make_score run beside another ticker's 5.7 events
   keeps them byte-for-byte, and an event a lane appends in update_registry's tail keeps its first date.
3. The engine's shared helpers: edgar_submissions (one fetch per CIK, memoised on success, raising on failure; the
   two readers keep their failure results), the misfit SIC ranges / notch / folder SIC, the identity stubs
   (load_annual_instance, fetch_instance, TTM_INPUT_OPTIONAL_FIELDS: every committed ttm.json hashes as before), the
   hoisted ttm.json read at the share-class marker, and the harness's submissions / instance patches.
4. facts.py and quote_tokens.py skeletons: the schema constants, period helpers, readers, run_hash_ok and the
   snippet rule (SNIPPET_MAX_WORDS 24, presentation scale).
5. make_score's scaffold: quoted(), the lane placeholders are inert and pure, key_numbers.md is exactly
   build_key_numbers' text, iprd_override_required is check_iprd_share_count_unverified's condition, and every
   main() placeholder runs before the first write (a refusal there leaves the registry, score.json and
   key_numbers.md untouched).
6. tests/rulings57.py: the G16 obligation helpers are the identity in L0 and never modify their inputs.
"""
import builtins
import contextlib
import copy
import glob
import hashlib
import inspect
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
ROOT = os.path.dirname(SYS)
for _p in (HERE, SYS):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import make_score as M  # noqa: E402
import dcf_engine as E  # noqa: E402
import facts as F  # noqa: E402
import quote_tokens as Q  # noqa: E402
import engine55_harness as H  # noqa: E402
import rulings57  # noqa: E402
from test_make_score_55 import Run, _numbers, _judgment, _stamp, MAKE_SCORE, T  # noqa: E402


@contextlib.contextmanager
def no_writes():
    """Every file write, replace, removal or directory creation inside the block raises: the code under test is pure
    (it may read)."""
    real_open, real = builtins.open, {k: getattr(os, k) for k in ("replace", "remove", "makedirs", "mkdir", "rename")}

    def guarded_open(file, mode="r", *a, **k):
        if any(c in mode for c in "wax+"):
            raise AssertionError(f"a pure function opened {file!r} for writing ({mode})")
        return real_open(file, mode, *a, **k)

    def refuse(name):
        def f(*a, **k):
            raise AssertionError(f"a pure function called os.{name}{a}")
        return f
    builtins.open = guarded_open
    for k in real:
        setattr(os, k, refuse(k))
    try:
        yield
    finally:
        builtins.open = real_open
        for k, v in real.items():
            setattr(os, k, v)


def _refused(fn, *a, **k):
    """The refusal text when fn(*a) calls make_score.fail (SystemExit), else None."""
    try:
        with contextlib.redirect_stderr(_Buf()) as buf:
            fn(*a, **k)
    except SystemExit:
        return buf.text
    return None


class _Buf:
    def __init__(self):
        self.text = ""

    def write(self, s):
        self.text += s

    def flush(self):
        pass


# ===========================================================================
# 1. The release
# ===========================================================================
def test_release_is_5_7_0():
    """ENGINE_RELEASE 5.7.0 (engine_version stays 5); RULINGS_RELEASE is fixed at (5, 7, 0) and make_score's
    RELEASE_57 / is_57_run are facts.py's; output from 5.6.0 (HALO) or earlier is a release mismatch."""
    assert E.ENGINE_RELEASE == "5.7.0", E.ENGINE_RELEASE
    assert F.RULINGS_RELEASE == (5, 7, 0) and M.RELEASE_57 is F.RULINGS_RELEASE and M.is_57_run is F.is_rulings_run
    for rel, want in (("5.7.0", True), ("5.7", True), ("5.7.1", True), ("5.10.0", True), ("6.0.0", True),
                      ("5.6.0", False), ("5.5.0", False), ("5.4.0", False), (None, False), ("", False), ("x", False)):
        n = {"engine_release": rel} if rel is not None else {}
        assert M.is_57_run(n) is want and F.release_at_least(rel) is want, (rel, want)
    assert F.release_at_least("5.6.0", "5.6.0") and not F.release_at_least("5.6.0", (5, 7, 0))
    assert not M.is_57_run(None) and not M.is_57_run(["5.7.0"])
    assert F.release_tuple("5.7.0") == M.release_tuple("5.7.0") == (5, 7, 0)
    assert M.release_mismatch_reason("5.6.0") == "engine output predates release 5.7.0"
    assert M.release_mismatch_reason(None) == "engine output predates release 5.7.0"


# ===========================================================================
# 2. The registry whitelist
# ===========================================================================
NEW_EVENTS = {   # event -> (identity keys, the fields its lane's design writes)
    "misfit_notch": (("tier_by_numbers", "tier_final", "reason"),
                     {"tier_by_numbers": "B", "tier_final": "C", "weighted_irr": 0.1234,
                      "reason": "numbers tier B at 12.34% weighted IRR", "reason_source": "auto", "basis": "engine_flag"}),
    "declared_facts": (("facts_sha256",), {"facts_sha256": "a" * 64, "count": 2, "by_kind": {"filing": 2},
                                           "influencing": ["F1"]}),
    "moat_divergence": (("moat_score", "reason"), {"moat_score": 6.0, "evidence_score": 3.5, "core_evidence_score": 3.0,
                                                  "supporting_adjustment": 0.5, "divergence": 2.5,
                                                  "reason": "retention 97% [F1]"}),
    "moat_low_roic": (("moat_score", "reason"), {"moat_score": 7.0, "measure": "roic", "median": 0.08,
                                                "median_note": None, "reason": "ROIC 8% [F2]"}),
    "moat_high_return_low_moat": (("moat_score", "reason"), {"moat_score": 3.0, "measure": "roic", "median": 0.31,
                                                            "median_note": None, "min": 0.25, "reason": "31% [F3]"}),
    "moat_erosion_rebuttal": (("moat_score", "reason"), {"moat_score": 6.0, "governing_change_pp": -4.1,
                                                        "gross_margin_change_pp": -3.2, "hold_years": 2,
                                                        "hold_without": 0, "irr_weighted": 0.12,
                                                        "irr_weighted_without": 0.11, "reason": "mix 3.2pp [F4]"}),
    "moat_widening_declined": (("moat_score", "reason"), {"moat_score": 6.0, "governing_change_pp": 3.1,
                                                         "gross_margin_change_pp": 2.0, "hold_years": 2,
                                                         "hold_without": 3, "irr_weighted": 0.12,
                                                         "irr_weighted_without": 0.125, "reason": "cyclical"}),
    "interim_bridge": (("declaration_hash",), {"declaration_hash": "b" * 64, "currency": "EUR",
                                              "fy_period": "2025-12-31", "prior_interim_period": "2025-06-30",
                                              "current_interim_period": "2026-06-30",
                                              "report_accession": "0000000000-26-000001", "estimate_legs": [],
                                              "perimeter_changes": []}),
    "interim_bridge_declined": (("reason",), {"reason": "no comparative half-year: 2 of 4 legs", "report_accession": None}),
    "share_classes": (("basis", "declaration_sha256"), {"basis": "up_c_exchangeable_units",
                                                       "declaration_sha256": "c" * 64, "traded_class": "Class A",
                                                       "classes": [{"name": "Class B", "holder": "Parent",
                                                                    "exchange_ratio": 1.0}],
                                                       "units_by_period": {"2025-12-31": 164811000},
                                                       "reason": "164,811,000 units"}),
    "up_c_suspect": (("reason",), {"reason": "NCI share 42.2% is the minority partner's", "s": 0.422}),
    "capex_unlisted_ack": (("tag", "reason"), {"tag": "PaymentsToAcquireProductiveAssets", "reason": "a 0.1% line",
                                              "value": 1.0e6}),
    "base_alternatives": (("chosen", "reason", "ttm_kind", "ttm_fy_end", "ttm_ytd_end"),
                          {"chosen": "annual_median", "stale_fy": True,
                           "reason": "median +$16.14/sh vs TTM -$3.48/sh on a working-capital trough",
                           "ttm_kind": "ttm", "ttm_fy_end": "2025-12-31", "ttm_ytd_end": "2026-06-30",
                           "bases": [{"kind": "annual_median", "role": "published", "computed": True,
                                      "base_oe_per_share": 16.1404, "weighted_irr": 0.1033, "tier_by_numbers": "C",
                                      "note": None}],
                           "measured": True, "note": None, "impact_carried_from_prior_score": False,
                           "counterfactual_engine_release": None}),
}


def _events(ticker="OTHR", date="2026-10-20"):
    out = [dict({"ticker": ticker, "event": ev, "date": date}, **fields) for ev, (_, fields) in NEW_EVENTS.items()]
    out += [{"ticker": ticker, "event": "tier_override", "date": date, "tier_by_numbers": "B", "tier_final": "C",
             "reason": "test 9.25%", "facts": [{"id": "F1", "kind": "filing", "value": 9.25, "unit": "pct",
                                                 "period": "FY2025", "source": {"form": "10-K"}}]},
            {"ticker": ticker, "event": "base_override", "date": date, "value": 4.1434, "kind": "filing",
             "source": "s", "reason": "r", "share_basis": "total_units", "share_period": "2026-06-30",
             "facts": [{"id": "F2", "kind": "filing", "value": 1.0, "unit": "count", "period": "2026-06-30",
                        "source": {"form": "10-Q"}}]},
            {"ticker": ticker, "field": "capex", "value": 1.0e8, "kind": "filing", "source": "s", "reason": "r",
             "date": date, "software_included": True}]
    return out


@contextlib.contextmanager
def _registry_file(entries):
    d = tempfile.mkdtemp(prefix="r57_reg_")
    path = os.path.join(d, "overrides_registry.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"entries": entries}, f)
    old = M.REGISTRY
    M.REGISTRY = path
    try:
        yield path
    finally:
        M.REGISTRY = old
        shutil.rmtree(d, ignore_errors=True)


def test_every_57_event_is_declared_and_loads():
    """07 §1.11 + every lane rebase: each 5.7 event type is an _EVENT_DECLARATION key with its lane's identity
    tuple, BEFORE any run writes it — load_registry refuses the whole registry on an unknown event, so a lane writing
    an undeclared one would stop every ticker's make_score. A registry holding one of each (and the new identity keys
    on tier_override / base_override / a field override) loads; a misspelt name is still refused."""
    for ev, (keys, fields) in NEW_EVENTS.items():
        assert M._EVENT_DECLARATION.get(ev) == keys, (ev, M._EVENT_DECLARATION.get(ev), keys)
        assert not set(keys) & set(M.IPRD_DEFERRED_EVENT_KEYS), ev
        assert not set(fields) & set(M.IPRD_DEFERRED_EVENT_KEYS), (ev, "a deferred-payment field name")
        assert set(keys) <= set(fields), (ev, "the identity keys are fields the event writes")
    assert M._EVENT_DECLARATION["tier_override"] == ("tier_by_numbers", "tier_final", "reason", "facts")
    assert M._EVENT_DECLARATION["base_override"][-4:] == ("basis_window", "share_basis", "share_period", "facts")
    assert M._FIELD_DECLARATION[-1] == "software_included"
    assert M._EVENT_DECLARATION["iprd_deferred_payment"] == M.IPRD_DEFERRED_EVENT_KEYS   # #47's, unchanged
    entries = _events()
    for e in entries:
        assert M.registry_entry_problem(e) is None, (e.get("event"), M.registry_entry_problem(e))
    with _registry_file(entries):
        reg = M.load_registry()
        assert reg is not None and reg["entries"] == entries
    with _registry_file(entries + [{"ticker": "OTHR", "event": "share_class", "date": "2026-10-20", "basis": "x"}]):
        why = _refused(M.load_registry)
        assert why and "malformed" in why and "share_class" in why, why
    # a stray `periods` key still routes an entry to the deferred-payment validator (L8's units_by_period rename)
    bad = dict(next(e for e in entries if e.get("event") == "share_classes"), periods={"2025-12-31": 1})
    assert M.registry_entry_problem(bad)[0] == "event", M.registry_entry_problem(bad)


def test_new_identity_keys_redate_nothing():
    """The keys appended to existing identities (tier_override / base_override `facts`, base_override `share_basis` /
    `share_period`, a field override's `software_included`) are carried by no recorded entry, so a legacy entry and
    its unchanged re-derivation compare equal (null == null) and keep the first date; a new 5.7 event keeps its first
    date the same way, and a changed reason re-dates."""
    legacy = [{"ticker": "TST", "event": "tier_override", "date": "2026-10-14", "tier_by_numbers": "B",
               "tier_final": "C", "reason": "one notch"},
              {"ticker": "TST", "event": "base_override", "date": "2026-10-15", "value": 3.0, "source": "s",
               "reason": "r"},
              {"ticker": "TST", "field": "capex", "value": 5.0, "kind": "filing", "source": "s", "reason": "r",
               "date": "2026-10-16"},
              {"ticker": "TST", "event": "misfit_notch", "date": "2026-10-17", "tier_by_numbers": "B",
               "tier_final": "C", "reason": "r 1.5%", "reason_source": "auto"}]
    new = [dict(e, date="2026-10-21") for e in legacy]
    new[1]["kind"] = "filing"          # a pre-5.5 base_override event gaining its kind keeps its date (#31's rule)
    M.keep_first_dates(new, copy.deepcopy(legacy))
    assert [e["date"] for e in new] == ["2026-10-14", "2026-10-15", "2026-10-16", "2026-10-17"], new
    changed = [dict(legacy[3], date="2026-10-21", reason="r 1.6%")]
    M.keep_first_dates(changed, copy.deepcopy(legacy))
    assert changed[0]["date"] == "2026-10-21", changed
    cited = [dict(legacy[0], date="2026-10-21", facts=[{"id": "F1"}])]   # a reason that now cites facts re-dates
    M.keep_first_dates(cited, copy.deepcopy(legacy))
    assert cited[0]["date"] == "2026-10-21", cited


def _run_patched(r, program_patch, timeout=120):
    """make_score.main() on Run r's folder in a subprocess after `program_patch` (Python source with M in scope)."""
    prog = ("import sys\nsys.path.insert(0, sys.argv[1])\nimport make_score as M\n" + program_patch +
            "\nsys.argv = [M.__file__, sys.argv[2]]\nM.main()\n")
    env = dict(os.environ, STOCKS_BASE=r.base, PYTHONIOENCODING="utf-8", MAKE_SCORE_REGISTRY=r.registry)
    p = subprocess.run([sys.executable, "-c", prog, os.path.dirname(MAKE_SCORE), T], capture_output=True, text=True,
                       encoding="utf-8", env=env, timeout=timeout)
    r.rc, r.out, r.err = p.returncode, p.stdout, p.stderr
    return r


def test_a_registry_with_57_events_survives_a_make_score_run():
    """End to end (07 §1.11; L1 T-17's registry half): make_score on TST beside another ticker's 5.7 events (one of
    each) exits 0 and keeps them byte-for-byte — before L0 load_registry refused the registry (an unknown event) and
    nothing scored. An event a lane appends in update_registry's tail (here _notch_events, patched) is recorded, and
    an unchanged second run keeps its first date (keep_first_dates)."""
    others = _events()
    r = Run(_numbers())
    try:
        with open(r.registry, "w", encoding="utf-8") as f:
            json.dump({"entries": others}, f, indent=1)
        r.run()
        assert r.rc == 0, r.err[-800:]
        with open(r.registry, encoding="utf-8") as f:
            reg = json.load(f)
        assert [e for e in reg["entries"] if e.get("ticker") == "OTHR"] == others
        ev = ('M._notch_events = lambda ticker, today, notch, n: [{"ticker": ticker, "event": "misfit_notch", '
              '"date": today, "tier_by_numbers": "B", "tier_final": "C", "weighted_irr": 0.17, '
              '"reason": "numbers tier B at 17.00%", "reason_source": "auto", "basis": "engine_flag"}]')
        _run_patched(r, ev)
        assert r.rc == 0, r.err[-800:]
        mine = [e for e in r.entries() if e.get("ticker") == T and e.get("event") == "misfit_notch"]
        assert len(mine) == 1, r.entries()
        # back-date it, rerun: the unchanged declaration keeps the earlier date
        with open(r.registry, encoding="utf-8") as f:
            reg = json.load(f)
        for e in reg["entries"]:
            if e.get("ticker") == T and e.get("event") == "misfit_notch":
                e["date"] = "2026-10-01"
        with open(r.registry, "w", encoding="utf-8") as f:
            json.dump(reg, f, indent=1)
        _run_patched(r, ev)
        assert r.rc == 0, r.err[-800:]
        mine = [e for e in r.entries() if e.get("ticker") == T and e.get("event") == "misfit_notch"]
        assert [e["date"] for e in mine] == ["2026-10-01"], mine
        assert [e for e in r.entries() if e.get("ticker") == "OTHR"] == others
    finally:
        r.close()


# ===========================================================================
# 3. The engine's shared helpers
# ===========================================================================
def test_misfit_helpers():
    """01 §2.1-§2.2 with 07 §1.5: the SIC ranges (inclusive; 6726 BDCs are credit; 4950-4959 waste services, 6200
    exchanges, 6282 asset managers, 6411 brokers and 6531 agents are not misfits by SIC), the notch (D / F
    unchanged) and the folder's own SIC (fundamentals.json first, then profile.json; none -> all None) — pure."""
    cases = {"4911": "utility", 4941: "utility", "4949": "utility", "4950": None, "4953": None, "4959": None,
             "4960": "utility", "4991": "utility", "4999": "utility", "6019": None, "6020": "bank", "6022": "bank",
             "6099": "bank", "6111": "credit", "6141": "credit", "6199": "credit", "6200": None, "6211": "broker_dealer",
             "6282": None, "6311": "insurance_carrier", "6324": "insurance_carrier", "6331": "insurance_carrier",
             "6399": "insurance_carrier", "6411": None, "6510": "real_estate_lessor", "6519": "real_estate_lessor",
             "6531": None, "6726": "credit", "6798": "reit", " 6798 ": "reit", "7370": None, "": None, None: None,
             "abc": None, 6.5: None}
    with no_writes():
        for sic, want in cases.items():
            assert E.sic_misfit_class(sic) == want, (sic, E.sic_misfit_class(sic), want)
        assert [E.notch_tier(t) for t in ("S", "A", "B", "C", "D", "F", None)] == ["A", "B", "C", "D", "D", "F", None]
    assert E.MISFIT_SECTORS == ("Finance", "Real Estate", "Utilities")
    assert set(E.MISFIT_SIC_LABEL) == {c for _, _, c in E.MISFIT_SIC_RANGES}
    assert all(lo <= hi for lo, hi, _ in E.MISFIT_SIC_RANGES)
    d = tempfile.mkdtemp(prefix="r57_sic_")

    def put(t, name, text):
        os.makedirs(os.path.join(d, t), exist_ok=True)
        with open(os.path.join(d, t, name), "w", encoding="utf-8") as f:
            f.write(text if isinstance(text, str) else json.dumps(text))
    try:
        put("AAA", "fundamentals.json", {"profile": {"sic": "6324", "sic_description": "Hospital & Medical Service Plans"}})
        put("AAA", "profile.json", {"about": {"sic": "7370"}})
        put("BBB", "fundamentals.json", {"profile": {"sic": ""}})
        put("BBB", "profile.json", {"about": {"sic": 6798, "sic_description": "REIT"}})
        put("CCC", "fundamentals.json", "{not json")
        with no_writes():
            assert E.folder_sic(d, "AAA") == ("6324", "Hospital & Medical Service Plans", "fundamentals.json")
            assert E.folder_sic(d, "BBB") == ("6798", "REIT", "profile.json")
            assert E.folder_sic(d, "CCC") == (None, None, None)
            assert E.folder_sic(d, "ZZZ") == (None, None, None)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    assert E.folder_sic(ROOT, "APP")[0] == "7370"   # a committed folder: fundamentals.json profile.sic


def test_edgar_submissions_one_fetch_and_the_readers_degrade_as_before():
    """07 §1.2: filer_annual_form and filer_sic read ONE submissions document per CIK (memoised on success); a failed
    fetch raises from edgar_submissions, is not memoised (the next reader retries), and the readers return None /
    (None, None) as when each fetched it itself."""
    X = H._engine()
    calls = []
    doc = {"sic": "6324", "sicDescription": "Hospital & Medical Service Plans",
           "filings": {"recent": {"form": ["8-K", "10-Q", "20-F/A", "20-F", "10-K"]}}}

    def ok(url, headers=None, timeout=90):
        calls.append(url)
        return doc
    X.get_json = ok
    assert X.filer_annual_form(320193) == "20-F" and X.filer_sic(320193) == ("6324", "Hospital & Medical Service Plans")
    assert X.edgar_submissions(320193) is doc
    assert calls == ["https://data.sec.gov/submissions/CIK0000320193.json"], calls
    calls.clear()

    def boom(url, headers=None, timeout=90):
        calls.append(url)
        raise RuntimeError("offline")
    X.get_json = boom
    assert X.filer_annual_form(1) is None and X.filer_sic(1) == (None, None)
    assert len(calls) == 2, calls   # not memoised: each reader tried
    try:
        X.edgar_submissions(1)
        raise AssertionError("edgar_submissions swallowed a failed fetch")
    except RuntimeError:
        pass
    X.get_json = lambda url, headers=None, timeout=90: {"filings": {"recent": {"form": ["S-1"]}}}
    assert X.filer_annual_form(2) is None and X.filer_sic(2) == (None, None)   # no annual form, no SIC filed


def test_engine_stubs_are_the_identity():
    """The L4 / L8 stubs change nothing: load_annual_instance returns the same companyfacts object and no record,
    fetch_instance (None, None); TTM_INPUT_OPTIONAL_FIELDS is empty and ttm_input_legs / ttm_inputs_record equal the
    5.6 definition on every committed ttm.json (so every recorded ttm_input_hash still matches)."""
    facts = {"facts": {"us-gaap": {}}}
    assert E.load_annual_instance("TST", 1, facts) == (facts, None) and E.load_annual_instance("TST", 1, facts)[0] is facts
    assert E.fetch_instance(1, {"accession": "x"}) == (None, None)
    assert E.TTM_INPUT_OPTIONAL_FIELDS == ()

    def legs_56(tt):   # dcf_engine.ttm_input_legs at ba2bfc0, verbatim
        if not isinstance(tt, dict):
            return None
        out = {k: E._iprd_canon(tt.get(k)) for k in E.TTM_INPUT_TOP_FIELDS}
        out["overrides_used"] = E._iprd_entries(tt.get("overrides_used"), E.TTM_INPUT_OVERRIDE_FIELDS)
        return out
    paths = sorted(glob.glob(os.path.join(ROOT, "*", "ttm.json")))
    assert len(paths) > 300, len(paths)
    for p in paths:
        with open(p, encoding="utf-8") as f:
            tt = json.load(f)
        assert E.ttm_input_legs(tt) == legs_56(tt), p
        canon = json.dumps(legs_56(tt), sort_keys=True, separators=(",", ":"), default=str)
        assert E.ttm_inputs_record(tt)["ttm_input_hash"] == hashlib.sha256(canon.encode()).hexdigest(), p
    assert E.ttm_input_legs(None) is None and E.ttm_input_legs([1]) is None


def test_ttm_read_is_hoisted_to_the_share_class_marker():
    """L8 rebase §4 item 11: main() reads ttm.json once (ttm_doc, the isinstance guard kept) right before the
    latest-FY row, with the lane's marker between; the IPR&D block no longer re-reads it."""
    src = open(os.path.join(SYS, "dcf_engine.py"), encoding="utf-8").read()
    assert src.count('ttm_doc = json.load(_f)') == 1, "ttm.json must be read into ttm_doc exactly once"
    i_read = src.index('ttm_doc = json.load(_f)')
    i_marker = src.index("    # v5.7 share classes (L8)\n\n    latest = hist[-1] if hist else {}")
    i_iprd = src.index("    # ---- v5.6 acquired IPR&D one-time value adjustment (Andrew, 2026-10-19) ----")
    assert i_read < i_marker < i_iprd, (i_read, i_marker, i_iprd)
    assert "if not isinstance(ttm_doc, dict):" in src[i_read:i_marker]


def test_harness_patches_the_submissions_and_instance_fetches():
    """engine55_harness.run_engine patches edgar_submissions (07 §1.2) and fetch_instance (L4, moved into L0's
    harness edit): a fixture without `sic` / `submissions` / `instance_bytes` reads as no SIC, no filings and no
    instance — never the network."""
    seen = {}

    def peek(X):
        seen["sic"] = X.filer_sic(1)
        seen["sub"] = X.edgar_submissions(1)
        seen["inst"] = X.fetch_instance(1, {"accession": "a"})
        X.main = lambda: None   # stop before the run: the patches are what this test checks
    fx = dict(H.load_fixture("AR"))
    H.run_engine("AR", fixture=fx, patch=peek)
    assert seen["sic"] == (None, None) and seen["sub"]["filings"] == {"recent": {}} and seen["inst"] == (None, None), seen
    fx.update(sic="6324", sic_description="Hospital & Medical Service Plans",
              submissions={"filings": {"recent": {"form": ["10-K"]}}}, instance_bytes=b"<xbrl/>", instance_url="u")
    H.run_engine("AR", fixture=fx, patch=peek)
    assert seen["sic"] == ("6324", "Hospital & Medical Service Plans"), seen
    assert seen["sub"]["filings"] == {"recent": {"form": ["10-K"]}} and seen["inst"] == (b"<xbrl/>", "u"), seen


# ===========================================================================
# 4. facts.py and quote_tokens.py skeletons
# ===========================================================================
def test_facts_schema_constants():
    """07 §1.6 and the lane rebases: kinds, types (incl. `event`), the unit / period / id / metric patterns, every
    lane's used_for tag (incl. low_roic, high_return_low_moat, erosion_rebuttal, share_classes, ttm_rejection) and
    `moat:<name>` for the 11 core pillars, 4 supporting factors and `sources` — the retired M1b names refused with
    their pointer; INFLUENCE_TAGS maps every lane's reason field to a used_for tag."""
    assert F.KINDS == ("folder", "filing", "release", "third_party")
    assert F.TYPES == ("actual", "guidance", "estimate", "metric", "event")
    for u in ("USD", "EUR", "USD/share", "EUR/ADS", "pct", "pp", "bps", "x", "count"):
        assert F.UNIT_RE.match(u), u
    for u in ("usd", "percent", "USD/unit", "US$", ""):
        assert not F.UNIT_RE.match(u), u
    for p in ("FY2025", "CY2026", "Q2 FY2026", "H1 FY2026", "9M FY2026", "TTM 2026-06-30", "2026-06-30"):
        assert F.PERIOD_RE.match(p), p
    for p in ("FY25", "Q5 FY2026", "2026", "TTM", "fy2025"):
        assert not F.PERIOD_RE.match(p), p
    assert F.ID_RE.match("F1") and F.ID_RE.match("F90") and not F.ID_RE.match("F0") and not F.ID_RE.match("f1")
    for tag in ("context", "tier_override", "misfit_notch", "base_override", "moat_divergence", "low_roic",
                "high_return_low_moat", "erosion_rebuttal", "interim_bridge", "share_classes", "ttm_rejection",
                "moat:retention", "moat:erosion_risks", "moat:management", "moat:sources"):
        assert F.used_for_problem(tag) is None, (tag, F.used_for_problem(tag))
    assert len(F.MOAT_CORE_PILLARS) == 11 and len(F.MOAT_SUPPORTING_FACTORS) == 4
    for name, where in F.RETIRED_MOAT_TAGS.items():
        why = F.used_for_problem("moat:" + name)
        assert why and where in why, (name, why)
    for tag in ("moat:moat", "moat:", "nonsense", "", None, 3):
        assert F.used_for_problem(tag), tag
    assert set(F.INFLUENCE_TAGS.values()) <= set(F.USED_FOR), F.INFLUENCE_TAGS
    for field in ("tier_override_reason", "misfit_notch_reason", "base_override", "moat_scorecard.moat_divergence_reason",
                  "moat_scorecard.low_roic_reason", "up_c_suspect_reason", "ttm_rejection_reason"):
        assert field in F.INFLUENCE_TAGS, field
    assert set(F.THIRD_PARTY_NOT_SOLE_SUPPORT) <= set(F.USED_FOR)


def test_facts_readers_are_pure():
    """period_end (07 §1.6: the calendar, else the FY end month-day of latest_period_end; Q / H / 9M offset from the
    FY start; TTM / instant / CY parsed), fiscal_calendar (the CSV's bare fy_label read as FY<yyyy>, statements.json
    labels), series (by period, unplaced last), by_id, parse_refs and run_hash_ok — reading only."""
    with no_writes():
        assert F.period_end("2026-06-30") == "2026-06-30" and F.period_end("TTM 2026-06-30") == "2026-06-30"
        assert F.period_end("CY2026") == "2026-12-31" and F.period_end({"period": "CY2025"}) == "2025-12-31"
        assert F.period_end("FY2025") is None and F.period_end("bad") is None and F.period_end(None) is None
        assert F.period_end("FY2025", {"FY2025": "2025-09-27"}) == "2025-09-27"
        dec, jun = "2025-12-31", "2025-06-30"
        assert [F.period_end(p, None, dec) for p in ("FY2024", "Q1 FY2026", "Q2 FY2026", "H1 FY2026", "9M FY2026",
                                                      "Q4 FY2026", "H2 FY2026")] == \
            ["2024-12-31", "2026-03-31", "2026-06-30", "2026-06-30", "2026-09-30", "2026-12-31", "2026-12-31"]
        assert [F.period_end(p, None, jun) for p in ("FY2026", "Q1 FY2026", "H1 FY2026", "9M FY2026", "Q4 FY2026")] == \
            ["2026-06-30", "2025-09-30", "2025-12-31", "2026-03-31", "2026-06-30"]
        assert F.period_end("FY2025", None, "2024-02-29") == "2025-02-28"
        cal = F.fiscal_calendar(os.path.join(ROOT, "APP"))
        assert cal["FY2025"] == "2025-12-31" and cal["Q2 FY2026"] == "2026-06-30", cal
        assert F.fiscal_calendar(os.path.join(ROOT, "NO_SUCH_FOLDER")) == {}
        doc = {"facts": [{"id": "F3", "metric": "nrr", "period": "FY2025"}, {"id": "F1", "metric": "nrr", "period": "FY2023"},
                         {"id": "F2", "metric": "nrr", "period": "nonsense"}, {"id": "F4", "metric": "other", "period": "FY2024"},
                         {"id": "F1", "metric": "dup"}, "not a fact"]}
        assert [f["id"] for f in F.series(doc, "nrr", latest_period_end=dec)] == ["F1", "F3", "F2"]
        assert [f["id"] for f in F.series(doc, "nrr")] == ["F3", "F1", "F2"]   # nothing placeable: declaration order
        assert list(F.by_id(doc)) == ["F3", "F1", "F2", "F4"] and F.by_id(doc)["F1"]["metric"] == "nrr"
        assert F.by_id(None) == {} and F.series(None, "x") == []
        assert F.parse_refs("x [F1, F3] y [F3] [F12] [f4] [F0] F5") == ["F1", "F3", "F12"] and F.parse_refs(None) == []
        with open(os.path.join(ROOT, "APP", "dcf_numbers.json"), encoding="utf-8") as f:
            n = json.load(f)
        assert F.run_hash_ok(n) and not F.run_hash_ok(dict(n, price=n["price"] + 1)) and not F.run_hash_ok({})


def test_snippet_rule():
    """07 §1.7 (04 test 17): SNIPPET_MAX_WORDS 24; a token at its own precision; presentation_scale lets a bare token
    match value / 10^3, 10^6, 10^9 (539 / 276 / "(182)" / "1,234.5" positives; 538M negative); a percent token for a
    pct / pp fraction, bps for bps; accounting-standard references and form names are not numbers."""
    assert Q.SNIPPET_MAX_WORDS == 24 and Q.snippet_words("a b  c\n d") == 4
    s = "Net cash flow from operating activities 539 276"
    with no_writes():
        assert Q.snippet_shows_value(s, 539e6, presentation_scale=True)
        assert Q.snippet_shows_value(s, 276_000_000, presentation_scale=True)
        assert not Q.snippet_shows_value(s, 538e6, presentation_scale=True)
        assert not Q.snippet_shows_value(s, 539e6)                       # no presentation scale: 539 is 539
        assert Q.snippet_shows_value("Purchase of PP&E (182)", -182e6, presentation_scale=True)
        assert Q.snippet_shows_value("Revenue 1,234.5", 1_234_500_000, presentation_scale=True)
        assert Q.snippet_shows_value("Revenue 1,923.7", 1_923_686_000, presentation_scale=True)
        assert Q.snippet_shows_value("Revenue of $1.92 billion, up 53% year over year", 1_923_686_000)
        assert Q.snippet_shows_value("Revenue of $1.92 billion, up 53% year over year", 0.53, unit="pct")
        assert not Q.snippet_shows_value("Revenue of $1.92 billion", 0.0192, unit="pct")
        assert Q.snippet_shows_value("net revenue retention rate was 126%", 1.26, unit="pct")
        assert Q.snippet_shows_value("spread widened 42 bps", 0.0042, unit="bps")
        assert Q.snippet_shows_value("164,810,547 Class B units", 164_810_547)
        assert Q.snippet_shows_value("Class B units (in thousands) 164,811", 164_810_547, presentation_scale=True)
        assert not Q.snippet_shows_value("charged under ASC 805-50", 805)
        assert not Q.snippet_shows_value("per the Form 10-K", 10) and not Q.snippet_shows_value("FY2026 Q2", 2)
        assert Q.snippet_shows_value("nil 0", 0) and not Q.snippet_shows_value("nil 0", 5)
        assert not Q.snippet_shows_value("x", None) and not Q.snippet_shows_value("1", True)


# ===========================================================================
# 5. make_score's scaffold
# ===========================================================================
def test_quoted_echo_convention():
    """07 §1.10 / 02 §7.1: worker text in curly quotes, its own curly quotes straightened."""
    assert M.quoted("x 1.5%") == "“x 1.5%”" and M.quoted("a “b” c") == '“a "b" c”' and M.quoted(None) == "“”"


def test_placeholders_are_inert_and_pure():
    """Every lane placeholder returns its empty value and touches no file; the keywords the lanes fill exist where
    their rebases put them (update_registry after lock_held, alert_reasons' share_classes_raise, build_key_numbers,
    check_influence's 10 §(l) signature), and the R7 / L5 constants are placed."""
    n, j = {"engine_release": "5.7.0", "ticker": "TST"}, {"tier_override": None}
    with no_writes():
        # (L2 fills check_influence: a 5.7 tier_override_reason with no number now refuses — R3 — so the purity
        # probe uses a plain pin's reason, which needs none; test_facts.py covers the refusals)
        for fn, a in ((M.check_influence, ("base_override", "x", [], None, "/nowhere", n)),
                      (M.load_declared_facts, ("/nowhere", n, j)), (M.load_method_runs, ("/nowhere", n)),
                      (M.previous_score_summary, (None, n)), (M.validate_share_classes, (j,)),
                      (M.check_share_classes_sync, (n, None, "/nowhere")), (M.check_up_c_obligation, (n, j)),
                      (M.check_ttm_on_declaration, (n, None, None)), (M.share_classes_impact, ("TST", n, None)),
                      (M.share_classes_raise_reason, (None,)), (M.score_share_classes_fields, ({}, n, None, None)),
                      (M.annual_instance_check, ("/nowhere", n)), (M.interim_pin_state, ("/nowhere", n, j, None)),
                      (M.check_interim_obligation, (n, j, None)),
                      (M.interim_bridge_measurement, ("TST", n, None, False)),
                      (M.score_interim_fields, ({}, n, j, None, None)),
                      (M.ttm_rejection_state, ("/nowhere", n, j)),
                      (M.build_base_alternatives, ("TST", "/nowhere", n, j, None)),
                      (M.refuse_capex_override_software, (n, {})), (M.refuse_unlisted_capex_component, (n, j)),
                      (M.refuse_pre57_ttm_json, (n, None)), (M._attach_fact_citations, ([], None))):
            assert fn(*a) is None, fn.__name__
        assert M._alt_ttm_ok({}, None) is True
        for fn, a in ((M._notch_events, ("TST", "2026-10-21", None, n)), (M._moat_events, ("TST", "2026-10-21", None)),
                      (M._interim_events, ("TST", None, None, "2026-10-21")), (M._facts_events, ("TST", "2026-10-21", None)),
                      (M._share_classes_events, ("TST", None, None, n, j)),
                      (M._base_alternatives_events, ("TST", None, "2026-10-21")),
                      (M._capex_events, ("TST", "2026-10-21", None, n)),
                      (M._kn_price_vs_iv, (n,)), (M._kn_base_extras, (n,)), (M._kn_share_classes, (n, {})),
                      (M._kn_base_interim, (n, {}, None, None)), (M._kn_base_alternatives, ({},)),
                      (M._kn_growth_extras, ("/nowhere", n)), (M._kn_filed_history, ("/nowhere", n)),
                      (M._kn_scenario_extras, (n,)), (M._kn_method_runs, (None, None)), (M._kn_moat, ({},)),
                      (M._kn_interim, ({}, None)), (M._kn_declared_facts, (None,))):
            assert fn(*a) == [], fn.__name__
        assert M._kn_shares_suffix(n) == ""
    params = list(inspect.signature(M.update_registry).parameters)
    assert params[params.index("lock_held") + 1:] == ["notch", "override_in_force", "facts_check", "moat_ev", "interim",
                                                       "declined", "share_classes", "up_c", "unlisted_acks", "base_alts"]
    assert list(inspect.signature(M.check_influence).parameters) == [
        "field", "text", "fact_ids", "fc", "folder", "n", "extra", "trace_only", "require_anchor"]
    assert list(inspect.signature(M.build_key_numbers).parameters) == [
        "folder", "n", "j", "score", "applied", "impact", "ads_corr", "facts_check", "method_runs", "previous",
        "interim", "instance"]
    assert "share_classes_raise" in inspect.signature(M.alert_reasons).parameters
    for args in (("A", "A", None, "medium", "misfit", True, True), ("B", "B", None, "low", "misfit", True, False),
                 ("A", "B", "A", "high", "modeled", False, False)):
        assert M.alert_reasons(*args) == M.alert_reasons(*args, share_classes_raise=None)
    assert M.TTM_REJECTION_KEY == "ttm_rejection_reason" and M.REPLAY_PURPOSE_ENV == "DCF_REPLAY_PURPOSE"
    assert M.BASE_KINDS == ("annual_median", "ttm", "declared_interim", "payable_5y", "declared_pin")
    assert M.BASE_ROLES == ("published", "rejected", "alternative")
    assert {"tier_final", "tier_by_numbers", "dcf_content_hash", "iprd_adjustment", "fragility_flags"} <= set(
        M.SCORE_DECISION_KEYS)


def test_iprd_override_required_is_the_share_count_check_condition():
    """L1 rebase §4 item 11: the predicate factored out of check_iprd_share_count_unverified, behaviour unchanged —
    True exactly when that check demands a quantified main-agent tier_override."""
    q = "main agent: $40,000,000 / 100M shares = $0.40/share; adjusted weighted IRR 9.6%"
    for blk in (None, {}, {"treatment": "one_time_value_deduction", "total": 4e7},
                {"treatment": "not_applied_share_count_unverified", "total": 0},
                {"treatment": "not_applied_share_count_unverified", "total": -1.0},
                {"treatment": "not_applied_share_count_unverified", "total": "40000000"},
                {"treatment": "not_applied_share_count_unverified", "total": 4e7}):
        n = {"iprd_adjustment": blk}
        need = M.iprd_override_required(n)
        assert (_refused(M.check_iprd_share_count_unverified, n, {}) is not None) == need, blk
        assert _refused(M.check_iprd_share_count_unverified, n, {"tier_override": "B", "tier_override_reason": q}) is None
    assert M.iprd_override_required({"iprd_adjustment": {"treatment": "not_applied_share_count_unverified", "total": 1.0}})


def test_key_numbers_is_exactly_the_built_text():
    """07 §1.9: key_numbers.md is build_key_numbers' text (built before the write phase, written last by
    write_key_numbers_text) — the pure builder reproduces the file make_score wrote, line for line."""
    n = _numbers(fragility_flags=["THIN_HISTORY: only 3 fiscal years of data"])
    r = Run(n).run()
    try:
        assert r.rc == 0, r.err[-800:]
        with open(os.path.join(r.folder, "key_numbers.md"), encoding="utf-8") as f:
            on_disk = f.read()
        # [Integrate L3] the run's facts.json holds the minimal moat scorecard's facts (rulings57), so the builder is
        # handed the facts check make_score made from it (main step 2, load_declared_facts: reads only)
        with open(r.jpath, encoding="utf-8") as f:
            j_disk = json.load(f)
        with no_writes():
            fc = M.load_declared_facts(r.folder, _stamp(n), j_disk)
            built = M.build_key_numbers(r.folder, _stamp(n), _judgment(n), r.score(), {}, facts_check=fc)
        assert built == on_disk, (built, on_disk)
        # (lane L3: the "## Moat scorecard" section — _kn_moat, the tail's L3 hook — now follows the engine sections;
        # [Integrate L3] then L2's "## Declared facts (not engine output)", last — 07 §1.9)
        tail = M._kn_moat(r.score()) + M._kn_declared_facts(fc)
        assert built.startswith(f"# {T} — key numbers\n") and built.endswith(
            "- THIN_HISTORY: only 3 fiscal years of data\n" + ("\n".join(tail) + "\n" if tail else ""))
    finally:
        r.close()


PLACEHOLDERS_BEFORE_THE_WRITE = ("annual_instance_check", "refuse_capex_override_software",
                                 "refuse_unlisted_capex_component", "validate_share_classes", "check_share_classes_sync",
                                 "check_up_c_obligation", "load_declared_facts", "load_method_runs",
                                 "refuse_pre57_ttm_json", "check_ttm_on_declaration", "interim_pin_state",
                                 "ttm_rejection_state", "check_interim_obligation", "interim_bridge_measurement",
                                 "share_classes_impact", "build_base_alternatives", "share_classes_raise_reason",
                                 "score_interim_fields", "score_share_classes_fields", "previous_score_summary",
                                 "build_key_numbers")


def test_every_main_placeholder_runs_before_the_first_write():
    """07 §1.12 re-based on #47 (registry first, inside registry_transaction): each lane's main() step is called on
    every run, and a refusal from any of them (patched to fail) leaves the registry, score.json and key_numbers.md
    unwritten — so a lane filling its placeholder can refuse there without breaking the write-phase order."""
    for name in PLACEHOLDERS_BEFORE_THE_WRITE:
        r = Run(_numbers())
        try:
            _run_patched(r, f"def _x(*a, **k):\n    M.fail('simulated refusal: {name}')\nM.{name} = _x")
            assert r.rc == 1 and f"simulated refusal: {name}" in r.err, (name, r.rc, r.err[-600:])
            st = r.state()
            assert not os.path.exists(r.registry) and not st["score_exists"] and not st["key_exists"], (name, st)
        finally:
            r.close()


# ===========================================================================
# 6. tests/rulings57.py
# ===========================================================================
def test_rulings57_helpers_are_the_identity_and_never_modify_inputs():
    """07 G16: one helper per lane obligation, the identity in L0 — apply() returns equal COPIES (the inputs are never
    modified; a record is re-stamped only when an obligation changed it), make_current rewrites nothing, and
    merge_facts adds / replaces facts by id without dropping another lane's."""
    n, j = _stamp(_numbers()), _judgment(None)
    n0, j0 = copy.deepcopy(n), copy.deepcopy(j)
    n2, j2 = rulings57.apply(n, j)
    assert (n2, j2) == (n0, j0) and n2 is not n and j2 is not j and (n, j) == (n0, j0)
    assert rulings57.apply(None, None) == (None, None)
    assert rulings57.content_hash(n) == n["content_hash"]
    tt = {"ttm_oe_per_share": 1.0}
    assert rulings57.add_ttm_engine_release(tt) is tt and tt == {"ttm_oe_per_share": 1.0}
    assert rulings57.answer_base_replays("/nowhere", n) is None
    d = tempfile.mkdtemp(prefix="r57_g16_")
    try:
        os.makedirs(os.path.join(d, T))
        for name, obj in (("dcf_numbers.json", n), ("judgment.json", j)):
            with open(os.path.join(d, T, name), "w", encoding="utf-8") as f:
                json.dump(obj, f, indent=1)
        # (lane L3 filled add_minimal_scorecard: a 5.7 record gains the minimal moat scorecard and its facts.json the
        # first time; make_current is idempotent — a second call rewrites nothing)
        rulings57.make_current(d, T)
        jm = json.load(open(os.path.join(d, T, "judgment.json"), encoding="utf-8"))
        assert {k: v for k, v in jm.items() if k != "moat_scorecard"} == j
        assert jm.get("moat_scorecard") == (rulings57.minimal_scorecard() if M.is_57_run(n) else None)
        before = {x: open(os.path.join(d, T, x), "rb").read() for x in os.listdir(os.path.join(d, T))}
        rulings57.make_current(d, T)
        after = {x: open(os.path.join(d, T, x), "rb").read() for x in os.listdir(os.path.join(d, T))}
        assert before == after
        os.remove(os.path.join(d, T, "facts.json")) if os.path.exists(os.path.join(d, T, "facts.json")) else None
        folder = os.path.join(d, T)
        rulings57.merge_facts(folder, [{"id": "F90", "value": 7.25}])
        doc = rulings57.merge_facts(folder, [{"id": "F91", "value": 1.0}, {"id": "F90", "value": 7.5}])
        assert doc == {"schema": 1, "ticker": T, "facts": [{"id": "F90", "value": 7.5}, {"id": "F91", "value": 1.0}]}
        with open(os.path.join(folder, "facts.json"), encoding="utf-8") as f:
            assert json.load(f) == doc
    finally:
        shutil.rmtree(d, ignore_errors=True)
    # Run(files=...) writes a lane test's extra files into the temp base (the other half of the L0 decision)
    r = Run(_numbers(), files={"TST/facts.json": {"schema": 1, "ticker": T, "facts": []},
                               "_system/industry_returns.json": "{}\n"})
    try:
        assert json.load(open(os.path.join(r.folder, "facts.json"), encoding="utf-8"))["ticker"] == T
        assert open(os.path.join(r.sysdir, "industry_returns.json"), encoding="utf-8").read() == "{}\n"
    finally:
        r.close()


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
