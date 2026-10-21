#!/usr/bin/env python3
"""Engine 5.7 worker obligations for the PRE-EXISTING tests (07 §2 G16) — imported by tests, never run on its own.

Since engine release 5.7.0 every test that stamps a record with the current release (E.ENGINE_RELEASE) builds a "5.7
run", which inherits each new 5.7 obligation (a misfit's misfit_notch_reason, facts.json and cited reasons, the moat
scorecard, a 20-F STALE_FY run's interim declaration, an Up-C reason, a STALE_FY TTM rejection reason, a 5.7-stamped
ttm.json, the R7 base replays). One function per obligation, so every pre-existing test keeps its assertions
unchanged: the lane that adds an obligation fills its own function here (the scaffold, L0, left each a no-op) and the
call sites already apply it — test_make_score_55.Run (also test_make_score_iprd, which builds through Run),
test_payable_base._score_files, test_queue_alert_gates._folder and test_engine_55._ms_run, all through apply().
add_ttm_engine_release and answer_base_replays are wired by their lanes (L9, R7) where a test writes a ttm.json or
installs an engine stand-in.

Files: an obligation that needs a folder file writes it itself into `folder` (the test's temp folder) — facts go
through merge_facts, so the lanes that cite facts (L2 reasons, L3 scorecard, L8 / R7 reasons) never overwrite each
other's. (The other half of the L0 decision for L2 / L3: test_make_score_55.Run(files=...) writes any extra file a
lane's OWN new tests need — facts.json, fundamentals.json, _system/industry_returns.json.)
"""
import copy
import hashlib
import json
import os


# ---------------------------------------------------------------------------
# One function per 5.7 obligation (each lane fills its own; no-ops in L0)
# ---------------------------------------------------------------------------
def add_notch_reason(n, j):
    """L1 (R1): a current-release sector misfit (S-C, not on the payable base) gets a misfit_notch_reason carrying a
    number. No-op in L0."""
    return None


def cite_facts_for_reasons(j, n, folder=None):
    """L2 (R3): facts.json facts (merge_facts) and [F#] citations for the reasons a 5.7 run traces
    (tier_override_reason, base_override, ...), so every number in them traces. No-op in L0."""
    return None


def add_minimal_scorecard(j, n=None, folder=None):
    """L3 (R4): the minimal moat_scorecard (and its facts, merge_facts) a 5.7 run needs. No-op in L0."""
    return None


def add_interim_declined(n, j):
    """L4 (R2a): interim_bridge_declined with a numeric reason on a 5.7 STALE_FY 20-F / 40-F record. No-op in L0."""
    return None


def add_up_c_reason(j, n):
    """L8 (R6): up_c_suspect_reason (carrying a number) on a 5.7 record flagged UP_C_SUSPECT. No-op in L0."""
    return None


def add_ttm_rejection(j, n, ttm=None):
    """R7: a qualifying ttm_rejection_reason (a cash-flow line and a traced figure) on a 5.7 STALE_FY record whose
    published base is not ttm.json's TTM. No-op in L0."""
    return None


def _dcf_engine():
    """The shared dcf_engine module (imported once with a neutral argv: the engine reads --measure from sys.argv)."""
    import importlib
    import sys
    if "dcf_engine" in sys.modules:
        return sys.modules["dcf_engine"]
    sysdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if sysdir not in sys.path:
        sys.path.insert(0, sysdir)
    saved = sys.argv
    sys.argv = ["dcf_engine.py"]
    try:
        return importlib.import_module("dcf_engine")
    finally:
        sys.argv = saved


def add_ttm_engine_release(tt, n=None):
    """L9 (R8 / R9 TTM provenance; 09 rebase A8): a 5.7 run whose basis read ttm.json needs a ttm.json stamped by a
    5.7 ttm.py (make_score refuse_pre57_ttm_json), so a test that hand-writes a ttm.json for a current-release record
    stamps it here: tt["engine_release"] = dcf_engine.ENGINE_RELEASE (what ttm.py writes) and, given the record n
    whose ttm_inputs is a dict (the run read ttm.json), n["ttm_inputs"] = dcf_engine.ttm_inputs_record(tt) — the
    engine's own record of the stamped file — and n's content_hash re-stamped when it carries one. A record with
    ttm_inputs null (a median run) or absent (an older record) is left as it is. Modifies tt (and n) in place;
    returns tt."""
    if not isinstance(tt, dict):
        return tt
    E = _dcf_engine()
    tt["engine_release"] = E.ENGINE_RELEASE
    if isinstance(n, dict) and isinstance(n.get("ttm_inputs"), dict):
        n["ttm_inputs"] = E.ttm_inputs_record(tt)
        if "content_hash" in n:
            n["content_hash"] = content_hash(n)
    return tt


def answer_base_replays(sysdir, n, ttm_doc=None, replies=None):
    """R7: answer the DCF_REPLAY_PURPOSE=base_alternatives engine spawns beside the test's own stand-in in sysdir.
    No-op in L0."""
    return None


# ---------------------------------------------------------------------------
# The entry points the call sites use
# ---------------------------------------------------------------------------
def _canon(n):
    return json.dumps({k: v for k, v in n.items() if k != "content_hash"}, sort_keys=True, separators=(",", ":"),
                      default=str)


def content_hash(n):
    """The engine's content hash of record n (dcf_engine._content_hash's canonicalization)."""
    return hashlib.sha256(_canon(n).encode()).hexdigest()


def apply(n, j, folder=None, ttm=None):
    """Every judgment-side obligation above, in lane merge order, on COPIES of engine record n and judgment j (either
    may be None); returns (n, j). The inputs are never modified. A record that carried a content_hash is re-stamped
    when an obligation changed it. The identity in L0."""
    n2 = copy.deepcopy(n) if n is not None else None
    j2 = copy.deepcopy(j) if j is not None else None
    before = _canon(n2) if isinstance(n2, dict) else None
    add_notch_reason(n2, j2)                              # L1
    cite_facts_for_reasons(j2, n2, folder=folder)         # L2
    add_minimal_scorecard(j2, n=n2, folder=folder)        # L3
    add_interim_declined(n2, j2)                          # L4
    add_up_c_reason(j2, n2)                               # L8
    add_ttm_rejection(j2, n2, ttm=ttm)                    # R7
    if isinstance(n2, dict) and "content_hash" in n2 and _canon(n2) != before:
        n2["content_hash"] = content_hash(n2)
    return n2, j2


def make_current(base, ticker):
    """The obligations for a folder already written under base (lane L5's pr_worktree / rebuild_scores fixtures):
    applies apply() to <base>/<ticker>/dcf_numbers.json and judgment.json (ttm.json read when present) and rewrites a
    file only when it changed. Returns the folder path. The identity in L0."""
    folder = os.path.join(base, ticker)

    def rd(name):
        p = os.path.join(folder, name)
        if not os.path.exists(p):
            return None
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    n, j, tt = rd("dcf_numbers.json"), rd("judgment.json"), rd("ttm.json")
    n2, j2 = apply(n, j, folder=folder, ttm=tt)
    for name, old, new in (("dcf_numbers.json", n, n2), ("judgment.json", j, j2)):
        if new is not None and new != old:
            with open(os.path.join(folder, name), "w", encoding="utf-8") as f:
                json.dump(new, f, indent=1, ensure_ascii=False)
    return folder


def merge_facts(folder, facts, ticker=None):
    """Add (or replace, by id) fact objects in <folder>/facts.json, creating it as {schema: 1, ticker, facts: []}
    when absent — so two lanes' obligations never overwrite each other's facts. Returns the written document."""
    path = os.path.join(folder, "facts.json")
    doc = None
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
    if not isinstance(doc, dict):
        doc = {"schema": 1, "ticker": (ticker or os.path.basename(os.path.normpath(folder))).upper(), "facts": []}
    have = {f.get("id"): i for i, f in enumerate(doc.get("facts") or []) if isinstance(f, dict)}
    doc.setdefault("facts", [])
    for fact in facts:
        if fact.get("id") in have:
            doc["facts"][have[fact["id"]]] = fact
        else:
            have[fact.get("id")] = len(doc["facts"])
            doc["facts"].append(fact)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
    return doc
